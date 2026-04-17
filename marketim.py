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
            # Barkod temizleme (Hayati öneme sahip)
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except: return None
    return None

df = verileri_yukle()

# URL'den veya sistem hafızasından barkodu çek
if 'barcode' not in st.session_state:
    st.session_state.barcode = st.query_params.get("barcode", "")

# --- 2. ARAYÜZ ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# Eğer elimizde barkod yoksa kamerayı aç
if not st.session_state.barcode:
    st.info("📸 Barkodu kameraya gösterin...")
    
    kamera_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        function onScanSuccess(decodedText) {
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            const barcode = decodedText.trim();
            // URL'yi güncelle ve sayfayı sert yenile
            const u = new URL(window.parent.location.href);
            u.searchParams.set('barcode', barcode);
            window.parent.location.href = u.href;
            
            html5QrCode.stop();
        }
        html5QrCode.start({ facingMode: "environment" }, { fps: 25, qrbox: 250 }, onScanSuccess);
    </script>
    """
    components.html(kamera_html, height=360)
    
    manuel = st.text_input("🔍 Barkod veya Ürün Adı Girin:")
    if manuel:
        st.session_state.barcode = manuel
        st.rerun()

# Eğer barkod okunduysa (sayfa yenilendiğinde burası çalışacak)
else:
    if st.button("⬅️ YENİ ÜRÜN TARA"):
        st.query_params.clear()
        st.session_state.barcode = ""
        st.rerun()

    if df is not None:
        hedef = str(st.session_state.barcode).strip()
        # Barkod eşleşmesi (Tam veya kısmi)
        sonuc = df[(df['BARKOD'] == hedef) | (df['ÜRÜN ADI'].str.contains(hedef, case=False, na=False))]
        
        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Kalem Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
                st.caption(f"Kayıtlı Barkod: {row['BARKOD']}")
        else:
            st.error(f"❌ Ürün bulunamadı: {hedef}")
            st.info("Eğer barkod doğruysa, CSV dosyasındaki barkod numarasını kontrol edin.")
