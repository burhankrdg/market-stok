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
            df['BARKOD'] = df['BARKOD'].astype(str).str.split('.').str[0].str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
            return df
        except: return None
    return None

df = verileri_yukle()

# --- URL'DEN BARKODU YAKALA ---
okunan_barkod = st.query_params.get("barcode", "")

# --- BAŞLIK ---
st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Otomatik Barkod Okuyucu</h3>", unsafe_allow_html=True)

# --- OTOMATİK TARAYICI (JAVASCRIPT) ---
if not okunan_barkod:
    st.info("📸 Barkodu kameraya gösterin, otomatik okunacaktır.")
    
    # Bu kod parçası tarayıcıyı doğrudan yönetir ve barkodu yakalar
    barcode_js = """
    <div id="interactive" class="viewport" style="width: 100%; height: 250px; border: 3px solid #2a7e2a; border-radius: 15px; overflow: hidden;"></div>
    <script src="https://cdn.jsdelivr.net/npm/@ericblade/quagga2/dist/quagga.min.js"></script>
    <script>
        Quagga.init({
            inputStream : { 
                name : "Live", 
                type : "LiveStream", 
                target: document.querySelector('#interactive'),
                constraints: { facingMode: "environment" } 
            },
            decoder : { readers : ["ean_reader", "ean_8_reader", "code_128_reader"] },
            locate: true
        }, function(err) { if (err) { console.log(err); return; } Quagga.start(); });

        let lastCode = "";
        Quagga.onDetected(function(result) {
            let code = result.codeResult.code;
            if (code !== lastCode) {
                lastCode = code;
                // Bip sesi çal
                var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
                audio.play();
                
                // Sayfayı yeni barkodla yenile
                setTimeout(() => {
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('barcode', code);
                    window.parent.location.href = url.href;
                }, 300);
            }
        });
    </script>
    <style>
        canvas.drawingBuffer, video.drawingBuffer { display: none; }
        #interactive video { width: 100%; height: 100%; object-fit: cover; }
    </style>
    """
    components.html(barcode_js, height=280)
else:
    if st.button("🔄 Yeni Ürün Tara"):
        st.query_params.clear()
        st.rerun()

# --- SONUÇLARI GÖSTER ---
# URL'de barkod varsa veya elle yazılırsa sonucu getir
arama = st.text_input("🔍 Barkod:", value=okunan_barkod)

if df is not None and arama:
    sonuc = df[df['BARKOD'] == arama]
    if sonuc.empty:
        sonuc = df[df['ÜRÜN ADI'].str.contains(arama, case=False, na=False)]

    if not sonuc.empty:
        st.divider()
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
    else:
        st.error(f"❌ '{arama}' ürünü bulunamadı.")
