import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. AYARLAR ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except: return None
    return None

df = verileri_yukle()

# URL'den gelen barkodu yakala
url_barkod = st.query_params.get("barcode", "")

# --- 2. TASARIM ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# EĞER URL'DE BARKOD YOKSA KAMERAYI GÖSTER
if not url_barkod:
    st.info("📸 Barkodu kameraya gösterin...")
    
    kamera_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        function onScanSuccess(decodedText) {
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // Sayfayı yeni barkodla zorla yenile
            const u = new URL(window.parent.location.href);
            u.searchParams.set('barcode', decodedText.trim());
            window.parent.location.href = u.href;
            
            html5QrCode.stop();
        }
        html5QrCode.start({ facingMode: "environment" }, { fps: 20, qrbox: 250 }, onScanSuccess);
    </script>
    """
    components.html(kamera_html, height=380)
    
    manuel = st.text_input("🔍 Veya Barkodu Elinizle Yazın:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

# EĞER BARKOD VARSA (SAYFA YENİLENDİĞİNDE BURASI ÇALIŞACAK)
else:
    if st.button("🔄 YENİ ÜRÜN OKUT"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef = str(url_barkod).strip()
        sonuc = df[df['BARKOD'] == hedef]
        
        # Eğer tam eşleşme yoksa ürün adı içinde ara
        if sonuc.empty:
            sonuc = df[df['ÜRÜN ADI'].str.contains(hedef, case=False, na=False)]

        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.markdown(f"<h1 style='color: #2a7e2a; text-align: center;'>{row['FİYAT']:.2f} TL</h1>", unsafe_allow_html=True)
                st.subheader(f"📦 {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                c2.metric("TOPLAM", f"{row['STOK'] * row['FİYAT']:,.2f} TL")
                st.caption(f"Barkod: {row['BARKOD']}")
        else:
            st.error(f"❌ '{hedef}' ürünü listede bulunamadı.")
