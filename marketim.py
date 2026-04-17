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

# URL'den barkodu oku (Sihirli nokta burası)
url_params = st.query_params
okunan = url_params.get("barcode", "")

# --- BAŞLIK ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# --- EĞER BARKOD OKUNMAMIŞSA KAMERAYI GÖSTER ---
if not okunan:
    st.info("📸 Barkodu gösterin, ses geldiğinde ürün açılacaktır.")
    
    kamera_js = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        
        function onScanSuccess(decodedText) {
            // 1. SES ÇIKARMA (Tarayıcı izinleri için)
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.type = "sine";
            oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // Bip sesi frekansı
            gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.2);

            // 2. SAYFAYI ZORLA YENİLE (Zorla yönlendirme)
            setTimeout(() => {
                const url = new URL(window.parent.location.href);
                url.searchParams.set('barcode', decodedText.trim());
                window.parent.location.href = url.href;
            }, 100);
        }

        const config = { fps: 20, qrbox: { width: 250, height: 150 } };
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess);
    </script>
    """
    components.html(kamera_js, height=360)
    
    st.write("---")
    manuel = st.text_input("🔍 Veya Elle Yazın:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

# --- EĞER BARKOD OKUNMUŞSA SONUCU GÖSTER ---
else:
    if st.button("⬅️ YENİ ÜRÜN İÇİN TIKLA"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef = str(okunan).strip()
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
                st.info(f"💰 Kalem Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
        else:
            st.error(f"❌ '{okunan}' barkodu bulunamadı.")
