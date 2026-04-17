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

# --- URL'DEN BARKODU YAKALA ---
url_params = st.query_params
okunan_barkod = url_params.get("barcode", "")

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Otomatik Barkod Okuyucu</h3>", unsafe_allow_html=True)

# --- OTOMATİK KAMERA SİSTEMİ (BİP SESLİ) ---
if not okunan_barkod:
    st.write("📸 Barkodu kameraya gösterin...")
    
    barcode_js = """
    <div id="interactive" class="viewport" style="width: 100%; height: 250px; border: 3px solid #2a7e2a; border-radius: 15px; overflow: hidden;"></div>
    <script src="https://cdn.jsdelivr.net/npm/@ericblade/quagga2/dist/quagga.min.js"></script>
    <script>
        // Bip sesi için audio objesi
        const beep = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');

        Quagga.init({
            inputStream : { 
                name : "Live", 
                type : "LiveStream", 
                target: document.querySelector('#interactive'),
                constraints: { facingMode: "environment" } // ARKA KAMERAYI ZORLA
            },
            decoder : { readers : ["ean_reader", "ean_8_reader", "code_128_reader"] },
            locate: true
        }, function(err) { if (err) { return; } Quagga.start(); });

        let detected = false;
        Quagga.onDetected(function(result) {
            if (!detected) {
                detected = true;
                let code = result.codeResult.code;
                
                // Bip sesini çal
                beep.play();

                // Sayfayı yeni barkodla güncelle
                setTimeout(() => {
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('barcode', code);
                    window.parent.location.href = url.href;
                }, 300); // Ses duyulsun diye hafif bekleme
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
    if st.button("🔄 Yeni Ürün Tara"):
        st.query_params.clear()
        st.rerun()

# --- SONUÇLARI GÖSTER ---
# Arama kutusunu her zaman gösterelim (Elle düzeltme gerekirse)
arama = st.text_input("🔍 Barkod veya Ürün Adı:", value=okunan_barkod)

if df is not None and arama:
    sonuc = df[(df['BARKOD'] == arama) | (df['ÜRÜN ADI'].str.contains(arama, case=False, na=False))]
    
    if not sonuc.empty:
        st.divider()
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("TOPLAM DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.caption(f"Barkod: {row['BARKOD']}")
    else:
        st.error("❌ Ürün bulunamadı.")
