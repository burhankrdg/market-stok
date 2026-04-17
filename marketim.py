import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- LOGO VE BAŞLIK ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>Canlı Barkod Terminali</h3>", unsafe_allow_html=True)

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

# --- ÖZEL BARKOD OKUYUCU (HTML/JS) ---
# Bu kısım harici kütüphane istemez, tarayıcıda çalışır.
st.write("📸 Barkodu kameraya gösterin...")

# HTML tabanlı barkod okuyucu bileşeni
barcode_html = """
<div id="interactive" class="viewport"></div>
<script src="https://cdn.jsdelivr.net/npm/@ericblade/quagga2/dist/quagga.min.js"></script>
<script>
    Quagga.init({
        inputStream: { name: "Live", type: "LiveStream", target: document.querySelector('#interactive') },
        decoder: { readers: ["ean_reader", "ean_8_reader", "code_128_reader"] }
    }, function(err) {
        if (err) { console.log(err); return; }
        Quagga.start();
    });
    Quagga.onDetected(function(data) {
        const code = data.codeResult.code;
        window.parent.postMessage({type: 'barcode', value: code}, '*');
    });
</script>
<style>
    #interactive.viewport canvas, #interactive.viewport video { width: 100%; border-radius: 10px; }
</style>
"""
# Streamlit ile JS arasında köprü kuruyoruz
components.html(barcode_html, height=300)

# Okunan barkodu almak için bir hile (Arama kutusuna odaklanma)
okunan_barkod = st.text_input("Okunan Barkod veya Ürün Adı:", key="search_box")

# --- SONUÇLARI GÖSTER ---
if df is not None and okunan_barkod:
    sonuc = df[df['ÜRÜN ADI'].str.contains(okunan_barkod, case=False, na=False) | (df['BARKOD'] == okunan_barkod)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("KALEM DEĞERİ", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.divider()
