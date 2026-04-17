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

# --- OTOMATİK BARKOD YAKALAMA (JS SİHRİ) ---
# Quagga barkodu okur ve Streamlit'in dahili mekanizmasını tetikler
st.write("📸 Barkodu kameraya gösterin...")

# HTML ve Gelişmiş JavaScript Köprüsü
barcode_html = """
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
        decoder : {
            readers : ["ean_reader", "ean_8_reader", "code_128_reader", "upc_reader"]
        },
        locate: true
    }, function(err) {
        if (err) { console.error(err); return; }
        Quagga.start();
    });

    let lastCode = "";
    Quagga.onDetected(function(result) {
        let code = result.codeResult.code;
        
        // Aynı barkodu üst üste okuyup sayfayı yormasın diye kontrol
        if (code !== lastCode) {
            lastCode = code;
            
            // 1. Sesli uyarı (Bip)
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();

            // 2. Streamlit Input alanını bul, değeri yaz ve ENTER tetikle
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            for (let i = 0; i < inputs.length; i++) {
                // Bizim placeholder'ı hedef alıyoruz
                if (inputs[i].placeholder === "Otomatik aranıyor...") {
                    let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(inputs[i], code);
                    
                    // Streamlit'in değişikliği algılaması için gerekli event'ler
                    inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                    inputs[i].dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Otomatik arama için küçük bir gecikmeyle odak kaydırma (blur)
                    setTimeout(() => { inputs[i].blur(); }, 100);
                    break;
                }
            }
        }
    });
</script>
<style>
    canvas.drawingBuffer, video.drawingBuffer { display: none; }
    #interactive video { width: 100%; height: 100%; object-fit: cover; }
</style>
"""
components.html(barcode_html, height=270)

# Bu kutu JavaScript tarafından otomatik doldurulacak
arama_kutusu = st.text_input("Barkod:", placeholder="Otomatik aranıyor...", key="barkod_input")

# --- SONUÇLARI ANINDA GÖSTER ---
if df is not None and arama_kutusu:
    # Hem Barkod hem Ürün Adı kontrolü
    sonuc = df[(df['BARKOD'] == arama_kutusu) | (df['ÜRÜN ADI'].str.contains(arama_kutusu, case=False, na=False))]
    
    if not sonuc.empty:
        st.write("---")
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("KALEM DEĞERİ", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.info(f"Barkod: {row['BARKOD']}")
    else:
        st.warning(f"'{arama_kutusu}' barkodlu ürün bulunamadı.")
