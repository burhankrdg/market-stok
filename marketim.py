import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. AYARLAR VE VERİ ---
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
        except:
            return None
    return None

df = verileri_yukle()
okunan = st.query_params.get("barcode", "")

# --- 2. ARAYÜZ ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

if not okunan:
    st.info("📸 Barkodu kameraya gösterin, otomatik bulacaktır.")
    
    # BU KOD BARKODU GÖRDÜĞÜ AN ANA SAYFAYI ZORLA YENİLER
    kamera_html_kodu = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        
        function onScanSuccess(decodedText) {
            // Onay sesi
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // Streamlit'in iframe korumasını aşmak için URL'yi dışarıdan değiştir
            const currentUrl = new URL(window.parent.location.href);
            currentUrl.searchParams.set('barcode', decodedText.trim());
            window.parent.location.href = currentUrl.href;
            
            html5QrCode.stop();
        }

        html5QrCode.start(
            { facingMode: "environment" }, 
            { fps: 20, qrbox: { width: 250, height: 150 } },
            onScanSuccess
        ).catch(err => console.error(err));
    </script>
    """
    components.html(kamera_html_kodu, height=380)
    
    # Yedek Manuel Giriş
    manuel = st.text_input("🔍 Barkod veya Ürün Adı Girin:", key="m_input")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

else:
    # --- 3. SONUÇ EKRANI ---
    if st.button("⬅️ Yeni Ürün İçin Kamerayı Aç"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef = str(okunan).strip()
        sonuc = df[(df['BARKOD'] == hedef) | (df['ÜRÜN ADI'].str.contains(hedef, case=False, na=False))]
        
        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Kalem Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
        else:
            st.error(f"❌ '{hedef}' ürünü listede yok.")
