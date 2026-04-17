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

# URL'den barkodu oku
params = st.query_params
okunan = params.get("barcode", "")

# --- ARAYÜZ ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

if not okunan:
    st.info("📸 Barkodu kameraya gösterin, otomatik bulacaktır.")
    
    # JAVASCRIPT: Streamlit ile doğrudan konuşan gelişmiş okuyucu
    kamera_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 5px solid #2a7e2a;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 30, qrbox: { width: 250, height: 150 } };
        
        const success = (text) => {
            // Bip sesi çal
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // KRİTİK NOKTA: Streamlit URL'sini doğrudan manipüle et ve sayfayı "hard reload" yap
            const currentUrl = new URL(window.parent.location.href);
            currentUrl.searchParams.set('barcode', text.trim());
            
            // Kamerayı durdur ve yönlendir
            html5QrCode.stop().then(() => {
                window.parent.location.href = currentUrl.href;
            });
        };

        html5QrCode.start({ facingMode: "environment" }, config, success)
            .catch(err => console.error("Kamera hatası:", err));
    </script>
    """
    components.html(kamera_html, height=380)
    
    # Yedek manuel giriş (Eğer kamera izin vermezse)
    st.write("---")
    manuel = st.text_input("🔍 Barkod Okunmazsa Buraya Yazın:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

else:
    # --- ÜRÜN GÖSTERME ---
    if st.button("⬅️ YENİ ÜRÜN OKUT"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef_barkod = str(okunan).strip()
        sonuc = df[df['BARKOD'] == hedef_barkod]
        
        # Eğer tam barkodla bulamazsa 'içinde geçiyor mu' diye bak
        if sonuc.empty:
            sonuc = df[df['BARKOD'].str.contains(hedef_barkod, na=False)]

        if not sonuc.empty:
            st.write("---")
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Toplam Mal Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
        else:
            st.error(f"❌ '{okunan}' barkodu listede bulunamadı!")
            st.write("CSV dosyanızdaki barkod ile okunan barkodun aynı olduğundan emin olun.")
