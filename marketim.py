import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- LOGO VE BAŞLIK ---
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
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")
    return None

df = verileri_yukle()

# --- URL PARAMETRESİNDEN BARKODU AL ---
# Sayfa yenilendiğinde barkodu buradan yakalıyoruz
url_params = st.query_params
okunan_barkod = url_params.get("barcode", "")

# --- CANLI BARKOD TARAYICI (JS) ---
st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Canlı Barkod Terminali</h3>", unsafe_allow_html=True)

# Eğer bir barkod okunmuşsa kamerayı geçici olarak gizle (Ürünü görmek için alan kalsın)
if not okunan_barkod:
    st.write("📸 Barkodu kameraya gösterin...")
    barcode_js = """
    <div id="interactive" class="viewport" style="width: 100%; height: 250px; border: 3px solid #2a7e2a; border-radius: 15px; overflow: hidden;"></div>
    <script src="https://cdn.jsdelivr.net/npm/@ericblade/quagga2/dist/quagga.min.js"></script>
    <script>
        Quagga.init({
            inputStream : { name : "Live", type : "LiveStream", target: document.querySelector('#interactive'), constraints: { facingMode: "environment" } },
            decoder : { readers : ["ean_reader", "ean_8_reader", "code_128_reader", "upc_reader"] },
            locate: true
        }, function(err) { if (err) { return; } Quagga.start(); });

        let lastCode = "";
        Quagga.onDetected(function(result) {
            let code = result.codeResult.code;
            if (code !== lastCode) {
                lastCode = code;
                const url = new URL(window.parent.location.href);
                url.searchParams.set('barcode', code);
                window.parent.location.href = url.href;
            }
        });
    </script>
    <style>
        canvas.drawingBuffer, video.drawingBuffer { display: none; }
        #interactive video { width: 100%; height: 100%; object-fit: cover; }
    </style>
    """
    components.html(barcode_js, height=270)
else:
    if st.button("🔄 Yeni Ürün Okut (Kamerayı Aç)"):
        st.query_params.clear()
        st.rerun()

# --- SONUÇLARI GÖSTER ---
if df is not None and okunan_barkod:
    sonuc = df[df['BARKOD'] == okunan_barkod]
    
    if not sonuc.empty:
        st.write("---")
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("KALEM DEĞERİ", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.info(f"Barkod No: {row['BARKOD']}")
    else:
        st.warning(f"Ürün bulunamadı: {okunan_barkod}")
        if st.button("Ana Menüye Dön"):
            st.query_params.clear()
            st.rerun()
elif df is None:
    st.error("Veri dosyası (envanter.csv) bulunamadı!")
