import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- LOGO ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
            df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
            return df
        except: return None
    return None

df = verileri_yukle()

# --- URL'DEN GELEN BARKODU YAKALA ---
url_params = st.query_params
okunan_barkod = url_params.get("barcode", "")

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Profesyonel Barkod Terminali</h3>", unsafe_allow_html=True)

# --- 1. ADIM: EĞER BARKOD YOKSA KAMERAYI GÖSTER ---
if not okunan_barkod:
    st.info("📸 Barkodu kare içine getirin, otomatik okunacaktır.")
    
    # En profesyonel JS tarayıcı (Html5-QRCode)
    terminal_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 20, qrbox: { width: 280, height: 150 } };

        const onScanSuccess = (decodedText, decodedResult) => {
            // 1. Sesli uyarı
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // 2. Taramayı durdur (donmasın diye)
            html5QrCode.stop().then(() => {
                // 3. Adres çubuğunu güncelle ve sayfayı zorla yenile
                const url = new URL(window.parent.location.href);
                url.searchParams.set('barcode', decodedText);
                window.parent.location.href = url.href;
            });
        };

        // Arka kamerayı (environment) başlat
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess);
    </script>
    """
    components.html(terminal_html, height=350)

# --- 2. ADIM: SONUÇLARI VE MANUEL ARAMAYI GÖSTER ---
st.divider()
arama = st.text_input("🔍 Barkod veya Ürün Adı Girin:", value=okunan_barkod)

if okunan_barkod:
    if st.button("🔄 Yeni Ürün Okut (Kamerayı Aç)"):
        st.query_params.clear()
        st.rerun()

if df is not None and arama:
    sonuc = df[(df['BARKOD'] == arama) | (df['ÜRÜN ADI'].str.contains(arama, case=False, na=False))]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("TOPLAM DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.caption(f"Kayıtlı Barkod: {row['BARKOD']}")
            st.divider()
    else:
        st.error(f"❌ Ürün bulunamadı: {arama}")
