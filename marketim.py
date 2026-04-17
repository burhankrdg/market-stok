import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- VERİ YÜKLEME (GELİŞTİRİLMİŞ) ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    # Envanter dosyasını bul (envanter.csv veya benzeri)
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or 'stok' in d.lower() or '2.xls' in d.lower()), None)
    
    if hedef:
        try:
            # Dosyayı oku
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
            # Sütun isimlerini standartlaştır
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            
            # KRİTİK DÜZELTME: Barkodları temiz metne çevir (0'ların kaybolmaması için)
            df['BARKOD'] = df['BARKOD'].astype(str).str.split('.').str[0].str.strip()
            
            # Sayısal alanları temizle
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")
            return None
    return None

df = verileri_yukle()

# --- URL PARAMETRE YÖNETİMİ ---
url_params = st.query_params
# Kameradan gelen barkodu al ve temizle
okunan_barkod = str(url_params.get("barcode", "")).strip()

st.markdown("<h3 style='text-align: center;'>⚡ Market Barkod Terminali</h3>", unsafe_allow_html=True)

# --- KAMERA BÖLÜMÜ ---
if not okunan_barkod or okunan_barkod == "None":
    st.info("📸 Barkodu okutun...")
    terminal_html = """
    <div id="reader" style="width: 100%; border-radius: 10px; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const onScanSuccess = (decodedText) => {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('barcode', decodedText.trim());
            window.parent.location.href = url.href;
        };
        html5QrCode.start({ facingMode: "environment" }, { fps: 20, qrbox: 250 }, onScanSuccess);
    </script>
    """
    components.html(terminal_html, height=350)
else:
    # --- ÜRÜN BULMA VE GÖSTERME ---
    st.success(f"🔎 Aranan Barkod: {okunan_barkod}")
    
    if st.button("🔄 Yeni Ürün Okut"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        # ARAMA MANTIĞI: Hem tam eşleşme hem de içerme kontrolü
        sonuc = df[df['BARKOD'] == okunan_barkod]
        
        # Eğer tam eşleşme yoksa, barkodun içinde geçiyor mu diye bak (bazı cihazlar baştaki 0'ı okumaz)
        if sonuc.empty:
            sonuc = df[df['BARKOD'].str.contains(okunan_barkod, na=False)]

        if not sonuc.empty:
            for _, row in sonuc.iterrows():
                st.balloons()
                st.markdown(f"## {row['ÜRÜN ADI']}")
                col1, col2 = st.columns(2)
                col1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                col2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.divider()
        else:
            st.error(f"❌ '{okunan_barkod}' barkodlu ürün listede bulunamadı.")
            st.warning("İpucu: Excel/CSV dosyanızdaki barkod numarasının cihazın okuduğuyla aynı olduğundan emin olun.")
