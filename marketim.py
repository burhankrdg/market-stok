import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- LOGO VE BAŞLIK ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Otomatik Barkod Terminali</h3>", unsafe_allow_html=True)

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

# --- CANLI BARKOD SİSTEMİ (JS KÖPRÜSÜ) ---
# Bu bölüm kamerayı açar ve barkodu bulduğu an kutuya yazar.
st.write("📸 Barkodu kameraya yaklaştırın...")

# Kullanıcıya bir giriş alanı sunuyoruz (JS burayı dolduracak)
okunan_barkod = st.text_input("Barkod Kodu:", key="barkod_alani", placeholder="Otomatik okunuyor...")

# HTML/JS Kodları: Kamerayı yönetir ve barkodu yakalar
barcode_js = """
<div id="interactive" class="viewport" style="width: 100%; height: 300px; border: 2px solid #2a7e2a; border-radius: 10px;"></div>
<script src="https://cdn.jsdelivr.net/npm/@ericblade/quagga2/dist/quagga.min.js"></script>
<script>
    Quagga.init({
        inputStream : {
            name : "Live",
            type : "LiveStream",
            target: document.querySelector('#interactive'),
            constraints: { facingMode: "environment" } // Arka kamerayı zorla
        },
        decoder : {
            readers : ["ean_reader", "ean_8_reader", "code_128_reader", "upc_reader"]
        },
        locate: true
    }, function(err) {
        if (err) { console.log(err); return; }
        Quagga.start();
    });

    Quagga.onDetected(function(result) {
        var code = result.codeResult.code;
        // Streamlit içindeki input alanını bul ve değeri yaz
        const inputs = window.parent.document.querySelectorAll('input');
        for (let i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === "Otomatik okunuyor...") {
                inputs[i].value = code;
                inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                break;
            }
        }
    });
</script>
<style>
    canvas.drawingBuffer, video.drawingBuffer { display: none; }
    #interactive video { width: 100%; height: 100%; object-fit: cover; border-radius: 8px; }
</style>
"""
components.html(barcode_js, height=320)

# --- SONUÇLARI GÖSTER ---
if df is not None and okunan_barkod:
    sonuc = df[df['ÜRÜN ADI'].str.contains(okunan_barkod, case=False, na=False) | (df['BARKOD'] == okunan_barkod)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.divider()
    else:
        st.warning(f"Ürün bulunamadı: {okunan_barkod}")
