import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- AYAR ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

# --- VERİ OKUMA ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]

    if not dosyalar:
        return None

    hedef = dosyalar[0]

    try:
        df = pd.read_csv(
            hedef,
            encoding='utf-8-sig',
            sep=None,
            engine='python',
            dtype=str
        )

        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])

        df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        df['FİYAT'] = pd.to_numeric(
            df['FİYAT'].astype(str).str.replace(',', '.'),
            errors='coerce'
        ).fillna(0)

        df['STOK'] = pd.to_numeric(
            df['STOK'].astype(str).str.replace(',', '.'),
            errors='coerce'
        ).fillna(0)

        return df

    except Exception as e:
        st.error(f"CSV Hatası: {e}")
        return None

df = verileri_yukle()

# --- URL PARAM ---
query_params = st.query_params
url_barkod = query_params.get("barcode", "")

# --- BAŞLIK ---
st.markdown(
    "<h2 style='text-align: center; color: #2a7e2a;'>🛒 Çamlık Market Barkod Sistemi</h2>",
    unsafe_allow_html=True
)

# --- KAMERA ---
if not url_barkod:

    st.info("📸 Barkodu kameraya gösterin")

    kamera_html = """
    <div id="reader" style="width:100%; border-radius:15px; border:3px solid #2a7e2a;"></div>

    <script src="https://unpkg.com/html5-qrcode"></script>

    <script>
        function baslat() {
            const qr = new Html5Qrcode("reader");

            qr.start(
                { facingMode: "environment" },
                { fps: 15, qrbox: 250 },
                (text) => {
                    var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
                    audio.play();

                    const url = new URL(window.parent.location.href);
                    url.searchParams.set("barcode", text.trim());

                    window.parent.location.href = url.href;

                    qr.stop();
                }
            );
        }

        setTimeout(baslat, 500);
    </script>
    """

    components.html(kamera_html, height=400)

    manuel = st.text_input("🔍 Barkodu manuel gir")

    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

# --- SONUÇ ---
else:

    if st.button("🔄 Yeni Ürün Okut"):
        st.query_params.clear()
        st.rerun()

    if df is not None:

        hedef = str(url_barkod).strip()

        sonuc = df[df['BARKOD'] == hedef]

        if sonuc.empty:
            sonuc = df[df['ÜRÜN ADI'].str.contains(hedef, case=False, na=False)]

        if not sonuc.empty:

            st.divider()

            for _, row in sonuc.iterrows():

                st.markdown(
                    f"<h1 style='color:#2a7e2a;text-align:center'>{row['FİYAT']:.2f} ₺</h1>",
                    unsafe_allow_html=True
                )

                st.subheader(f"📦 {row['ÜRÜN ADI']}")

                c1, c2 = st.columns(2)

                c1.metric("Stok", f"{int(row['STOK'])} {row['BİRİM']}")
                c2.metric("Toplam Değer", f"{row['STOK'] * row['FİYAT']:.2f} ₺")

                st.caption(f"Barkod: {row['BARKOD']}")

        else:
            st.error(f"❌ '{hedef}' bulunamadı")

    else:
        st.error("CSV dosyası bulunamadı")
