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
okunan = st.query_params.get("barcode", "")

st.markdown("<h2 style='text-align: center;'>🛒 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# --- ANA MANTIK ---
if not okunan:
    # KAMERAYI AÇAN BÖLÜM (En basit ve çalışan hali)
    kamera_js = """
    <div id="reader" style="width: 100%; border-radius: 10px; border: 3px solid #2a7e2a;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        html5QrCode.start(
            { facingMode: "environment" }, 
            { fps: 15, qrbox: 250 },
            (text) => {
                // Sadece URL'yi değiştir ve sayfayı yenile (En güvenli yol)
                const u = new URL(window.parent.location.href);
                u.searchParams.set('barcode', text.trim());
                window.parent.location.href = u.href;
            }
        ).catch(err => console.error(err));
    </script>
    """
    components.html(kamera_js, height=350)
    
    st.write("---")
    manuel = st.text_input("🔍 Veya Elle Barkod Girin:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()
else:
    # SONUÇLARI GÖSTEREN BÖLÜM
    if st.button("⬅️ Yeni Ürün Okut"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef = str(okunan).strip()
        sonuc = df[df['BARKOD'] == hedef]
        
        if sonuc.empty:
            sonuc = df[df['BARKOD'].str.contains(hedef, na=False)]

        if not sonuc.empty:
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Toplam Değer: {row['STOK'] * row['FİYAT']:,.2f} TL")
        else:
            st.error(f"❌ '{okunan}' barkodu bulunamadı.")
