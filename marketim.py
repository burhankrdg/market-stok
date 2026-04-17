import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            # Barkodları baştan string olarak oku ki 0'lar kaybolmasın
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            df['BARKOD'] = df['BARKOD'].astype(str).str.split('.').str[0].str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except: return None
    return None

df = verileri_yukle()
okunan_barkod = st.query_params.get("barcode", "")

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>🛒 Otomatik Barkod Terminali</h3>", unsafe_allow_html=True)

# --- OTOMATİK TARAYICI (EN GÜÇLÜ SÜRÜM) ---
if not okunan_barkod:
    # Bu HTML bileşeni, barkodu gördüğü an URL'ye fırlatır
    terminal_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; overflow: hidden; border: 4px solid #2a7e2a;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Barkod okunduğunda BİP sesi
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // Okunan barkodu Streamlit URL'sine gönder ve sayfayı yenile
            const url = new URL(window.parent.location.href);
            url.searchParams.set('barcode', decodedText.trim());
            window.parent.location.href = url.href;
        }

        const html5QrCode = new Html5Qrcode("reader");
        const config = { 
            fps: 25,          // Daha hızlı tarama
            qrbox: { width: 280, height: 180 }, // Barkod odak alanı
            aspectRatio: 1.0
        };

        // iPhone ve Android için arka kamerayı zorla ve başlat
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
        .catch(err => { console.error("Kamera başlatılamadı:", err); });
    </script>
    """
    components.html(terminal_html, height=350)
    
    # Kamera altındaki yedek arama kutusu
    manuel = st.text_input("🔍 Barkod Okunmazsa Buraya Yazın:")
    if manuel:
        okunan_barkod = manuel
else:
    if st.button("🔄 Yeni Ürün Okut"):
        st.query_params.clear()
        st.rerun()

# --- SONUÇ GÖSTERİMİ ---
if df is not None and okunan_barkod:
    # Temiz barkod eşleştirme
    hedef = str(okunan_barkod).strip()
    sonuc = df[df['BARKOD'] == hedef]
    
    if sonuc.empty: # Eğer tam bulamazsa içinde ara (0 hataları için)
        sonuc = df[df['BARKOD'].str.contains(hedef, na=False)]

    if not sonuc.empty:
        st.divider()
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2 = st.columns(2)
            c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            st.info(f"💰 Kalem Değeri: {row['FİYAT'] * row['STOK']:.2f} TL")
    else:
        st.error(f"❌ Ürün bulunamadı: {hedef}")
