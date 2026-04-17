import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- AYARLAR ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except: return None
    return None

df = verileri_yukle()

# --- BAŞLIK ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# --- JAVASCRIPT KÖPRÜSÜ (GİZLİ İLETİŞİM) ---
# Bu parça, kameranın okuduğu veriyi Python'a "fırlatır"
if 'barkod_depo' not in st.session_state:
    st.session_state.barkod_depo = ""

def barkod_ayarla():
    if st.session_state.barkod_girdisi:
        st.session_state.barkod_depo = st.session_state.barkod_girdisi

# Görünen arama kutusu
arama = st.text_input("🔍 Barkod:", value=st.session_state.barkod_depo, key="barkod_girdisi", on_change=barkod_ayarla)

# --- OTOMATİK KAMERA SİSTEMİ ---
if not arama:
    st.info("📸 Barkodu kameraya gösterin...")
    
    # Html5-Qrcode kullanarak doğrudan giriş kutusunu tetikliyoruz
    kamera_js = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 20, qrbox: { width: 250, height: 150 } };
        
        const success = (text) => {
            // 1. Bip sesi
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // 2. Streamlit'in input kutusunu bul ve değeri içine yaz
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            for (let input of inputs) {
                // Streamlit'in React yapısını tetiklemek için değeri set et ve event fırlat
                let lastValue = input.value;
                input.value = text.trim();
                let event = new Event('input', { bubbles: true });
                event.simulated = true;
                let tracker = input._valueTracker;
                if (tracker) { tracker.setValue(lastValue); }
                input.dispatchEvent(event);
                
                // Enter tuşuna basma simülasyonu
                let enterEvent = new KeyboardEvent('keydown', {
                    bubbles: true, cancelable: true, keyCode: 13
                });
                input.dispatchEvent(enterEvent);
            }
            
            html5QrCode.stop();
        };

        html5QrCode.start({ facingMode: "environment" }, config, success);
    </script>
    """
    components.html(kamera_js, height=350)

# --- ÜRÜN GÖSTERİMİ ---
if df is not None and arama:
    if st.button("🔄 Yeni Ürün Tara"):
        st.session_state.barkod_depo = ""
        st.rerun()

    hedef = str(arama).strip()
    sonuc = df[df['BARKOD'] == hedef]
    
    if sonuc.empty:
        sonuc = df[df['BARKOD'].str.contains(hedef, na=False)]

    if not sonuc.empty:
        st.divider()
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2 = st.columns(2)
            c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            st.info(f"💰 Toplam Değer: {row['STOK'] * row['FİYAT']:,.2f} TL")
    else:
        st.error(f"❌ '{arama}' barkodlu ürün bulunamadı.")
