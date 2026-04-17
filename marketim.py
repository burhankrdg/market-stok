import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. SAYFA VE VERİ AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or 'stok' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            # Barkodların bozulmaması için hepsini metin (string) olarak okuyoruz
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            
            # Temizlik: Barkodlardaki boşlukları ve olası ".0" eklerini temizle
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
            return df
        except: return None
    return None

df = verileri_yukle()

# --- 2. BARKOD YAKALAMA MANTIĞI ---
# URL'den gelen barkodu al (Kameranın fırlattığı veri)
url_params = st.query_params
okunan = url_params.get("barcode", "")

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Profesyonel Barkod Terminali</h3>", unsafe_allow_html=True)

# --- 3. KAMERA / SONUÇ EKRANI AYIRIMI ---
if not okunan:
    st.info("📸 Barkodu kameraya gösterin...")
    # HTML5-QRCode Kütüphanesi (En Kararlısı)
    terminal_js = """
    <div id="reader" style="width: 100%; border-radius: 15px; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 20, qrbox: { width: 250, height: 150 } };
        
        const onScanSuccess = (decodedText) => {
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // Okunan barkodu URL'ye fırlat ve sayfayı zorla yenile
            setTimeout(() => {
                const url = new URL(window.parent.location.href);
                url.searchParams.set('barcode', decodedText.trim());
                window.parent.location.href = url.href;
            }, 200);
        };
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess);
    </script>
    """
    components.html(terminal_js, height=350)
    
    # Kamera altında manuel arama kutusu her zaman dursun
    manuel = st.text_input("🔍 Veya Elle Barkod/Ürün Girin:")
    if manuel:
        okunan = manuel
else:
    # Ürün bulunduysa ekranı temizle ve sonucu göster
    if st.button("⬅️ Kamerayı Tekrar Aç"):
        st.query_params.clear()
        st.rerun()

# --- 4. OTOMATİK ÜRÜN BULUCU ---
if df is not None and okunan:
    # Barkodu temizle (önemli)
    hedef_barkod = str(okunan).strip()
    
    # Arama: Hem tam eşleşme hem içerme (0'lar kaybolmasın diye)
    sonuc = df[df['BARKOD'] == hedef_barkod]
    if sonuc.empty:
        # Baştaki sıfır hatası için alternatif arama
        sonuc = df[df['BARKOD'].str.contains(hedef_barkod, na=False)]

    if not sonuc.empty:
        st.write("---")
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.info(f"Barkod: {row['BARKOD']}")
    else:
        st.error(f"❌ Ürün bulunamadı: {hedef_barkod}")
