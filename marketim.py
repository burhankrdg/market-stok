import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            # Barkod temizliği (Baştaki ve sondaki görünmez boşlukları, .0 uzantılarını temizle)
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except: return None
    return None

df = verileri_yukle()

# --- URL PARAMETRE YÖNETİMİ ---
# Barkod okunduğunda burası dolacak
url_params = st.query_params
okunan_barkod = url_params.get("barcode", "")

# --- BAŞLIK ---
st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Otomatik Barkod Terminali</h3>", unsafe_allow_html=True)

# --- ANA MANTIK ---
if not okunan_barkod:
    st.info("📸 Barkodu kameraya gösterin...")
    
    # BU KOD BARKODU GÖRDÜĞÜ AN ADRES ÇUBUĞUNA YAZAR VE SAYFAYI YENİLER
    barcode_js = """
    <div id="reader" style="width: 100%; border-radius: 15px; overflow: hidden; border: 4px solid #2a7e2a;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText) {
            // Barkod okundu! Bip sesi çal.
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // Streamlit'e veriyi URL üzerinden zorla gönder
            const url = new URL(window.parent.location.href);
            url.searchParams.set('barcode', decodedText.trim());
            window.parent.location.href = url.href;
        }

        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 20, qrbox: {width: 280, height: 180} };
        
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
            .catch(err => { console.error(err); });
    </script>
    """
    components.html(barcode_js, height=350)
    
    # Manuel giriş kutusu her zaman yedek olarak dursun
    manuel = st.text_input("🔍 Barkod Okunmazsa Buraya Yazın:", key="manuel_input")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()
else:
    # --- ÜRÜN GÖSTERİMİ ---
    if st.button("⬅️ Yeni Ürün Okut (Kamerayı Aç)"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        # Barkodu hem tam eşleşme hem de 'içerir' şeklinde ara (0 hataları için)
        hedef = str(okunan_barkod).strip()
        sonuc = df[df['BARKOD'] == hedef]
        
        if sonuc.empty:
             sonuc = df[df['BARKOD'].str.contains(hedef, na=False)]

        if not sonuc.empty:
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.divider()
        else:
            st.error(f"❌ '{okunan_barkod}' barkodlu ürün listede yok.")
