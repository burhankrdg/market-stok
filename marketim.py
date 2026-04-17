import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- SAYFA VE VERİ AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

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
            return df
        except: return None
    return None

df = verileri_yukle()
url_params = st.query_params
okunan_barkod = url_params.get("barcode", "")

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>⚡ Süper Hızlı Otomatik Terminal</h3>", unsafe_allow_html=True)

# --- OTOMATİK TARAYICI (ZXing Kütüphanesi ile) ---
if not okunan_barkod:
    st.info("📸 Barkodu kameraya tutun, otomatik okuyacaktır.")
    
    # Bu kütüphane iPhone'larda çok daha kararlıdır
    barcode_js = """
    <div style="position: relative; width: 100%; height: 300px; border: 4px solid #2a7e2a; border-radius: 15px; overflow: hidden;">
        <video id="video" style="width: 100%; height: 100%; object-fit: cover;"></video>
    </div>
    <script src="https://unpkg.com/@zxing/library@latest"></script>
    <script>
        const codeReader = new ZXing.BrowserMultiFormatReader();
        const videoElement = document.getElementById('video');

        codeReader.decodeFromVideoDevice(null, 'video', (result, err) => {
            if (result) {
                // Başarılı okuma
                var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
                audio.play();
                
                // URL'ye gönder ve yenile
                const url = new URL(window.parent.location.href);
                url.searchParams.set('barcode', result.text.trim());
                window.parent.location.href = url.href;
                
                codeReader.reset();
            }
        });
    </script>
    """
    components.html(barcode_js, height=320)
else:
    if st.button("🔄 Yeni Ürün İçin Kamerayı Aç"):
        st.query_params.clear()
        st.rerun()

# --- SONUÇLARI GÖSTER ---
arama = st.text_input("🔍 Aranan Barkod:", value=okunan_barkod)

if df is not None and arama:
    sonuc = df[df['BARKOD'] == arama]
    if sonuc.empty:
        # Eğer tam barkodla bulamazsa isimde ara
        sonuc = df[df['ÜRÜN ADI'].str.contains(arama, case=False, na=False)]

    if not sonuc.empty:
        st.divider()
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2 = st.columns(2)
            c1.metric("SATIŞ FİYATI", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK MİKTARI", f"{int(row['STOK'])} {row['BİRİM']}")
            st.info(f"💰 Toplam Mal Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
    else:
        st.error(f"❌ '{arama}' barkodlu ürün listede yok.")
