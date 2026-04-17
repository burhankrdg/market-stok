import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- LOGO VE BAŞLIK ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Hızlı Barkod Terminali</h3>", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
        df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
        df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
        return df
    return None

df = verileri_yukle()

# --- GELİŞMİŞ CANLI TARAYICI (HTML5-QRCode) ---
st.write("📸 Barkodu çerçeve içine getirin...")

# Bu JavaScript kodu iPhone kameralarında otomatik odaklama yapar ve çok hızlıdır
barcode_reader_html = """
<div id="reader" style="width: 100%; border-radius: 10px; overflow: hidden;"></div>
<script src="https://unpkg.com/html5-qrcode"></script>
<script>
    function onScanSuccess(decodedText, decodedResult) {
        // Barkod okunduğunda bip sesi çal (isteğe bağlı)
        var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
        audio.play();
        
        // Okunan değeri Streamlit'e gönder
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: decodedText
        }, '*');
        
        // Okuma sonrası durdurma (isteğe bağlı, seri okuma için kapatılabilir)
        // html5QrcodeScanner.clear();
    }

    let config = { 
        fps: 20, 
        qrbox: {width: 250, height: 150},
        aspectRatio: 1.0
    };

    let html5QrcodeScanner = new Html5QrcodeScanner("reader", config, false);
    html5QrcodeScanner.render(onScanSuccess);
</script>
"""

# HTML Bileşenini ekrana basıyoruz
# Bu bileşen okunan barkodu doğrudan 'okunan' değişkenine atar
okunan = components.html(barcode_reader_html, height=450)

# Arama kutusu (Manuel giriş veya otomatik dolum için)
search_query = st.text_input("Barkod Kodu:", key="barkod_input", placeholder="Barkod bekleniyor...")

# --- SONUÇLARI GÖSTER ---
if df is not None and search_query:
    sonuc = df[df['ÜRÜN ADI'].str.contains(search_query, case=False, na=False) | (df['BARKOD'] == search_query)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            st.markdown(f"### ✅ {row['ÜRÜN ADI']}")
            c1, c2 = st.columns(2)
            c1.metric("SATIŞ FİYATI", f"{row['FİYAT']} TL")
            c2.metric("STOK MİKTARI", f"{int(row['STOK'])} {row['BİRİM']}")
            st.info(f"💰 Bu kalemin toplam değeri: **{row['KALEM DEĞERİ']:,.2f} TL**")
            st.divider()
    else:
        st.warning(f"'{search_query}' barkodlu ürün listede yok.")
