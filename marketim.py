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

# --- 2. URL'DEN VERİ ÇEKME ---
# Burası kameradan gelen barkodu yakalayan tek yer
query_params = st.query_params
okunan = query_params.get("barcode", "")

st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# --- 3. ANA MANTIK ---
if not okunan:
    st.warning("📸 Barkodu kameraya gösterin...")
    
    # BU KOD BARKODU GÖRDÜĞÜ AN STREAMLIT'I UYANDIRIR
    kamera_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        
        function onScanSuccess(decodedText) {
            // 1. Bip Sesi
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // 2. Streamlit'e veriyi fırlat ve sayfayı sars (yenile)
            const u = new URL(window.parent.location.href);
            u.searchParams.set('barcode', decodedText.trim());
            window.parent.location.href = u.href;
            
            html5QrCode.stop();
        }

        const config = { 
            fps: 25, 
            qrbox: { width: 250, height: 150 },
            aspectRatio: 1.0
        };

        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess);
    </script>
    """
    components.html(kamera_html, height=360)
    
    # Manuel Giriş
    manuel = st.text_input("🔍 Barkod veya Ürün Adı Girin:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

else:
    # --- 4. SONUÇ EKRANI ---
    if st.button("⬅️ Yeni Ürün Okut"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        target = str(okunan).strip()
        sonuc = df[(df['BARKOD'] == target) | (df['ÜRÜN ADI'].str.contains(target, case=False, na=False))]
        
        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Toplam Değer: {row['STOK'] * row['FİYAT']:,.2f} TL")
        else:
            st.error(f"❌ Barkod Bulunamadı: {target}")
