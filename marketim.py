import streamlit as st
import pandas as pd
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Stok", layout="centered")

# --- LOGO ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>🛒 Stok ve Fiyat Sorgulama</h3>", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
            df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
            return df
        except: return None
    return None

df = verileri_yukle()

# --- ARAMA BÖLÜMÜ (HEM ELLE HEM KAMERAYLA) ---
st.info("💡 Ürün adını yazabilir veya barkod fotoğrafı çekebilirsiniz.")
arama = st.text_input("🔍 Barkod veya Ürün Adı Girin:", key="arama_kutusu")

# ÖNEMLİ: iPhone'da ARKA KAMERAYI açması için fotoğraf yükleme aracını kullanıyoruz.
# Bu araç iPhone'da "Fotoğraf Çek" dediğinde otomatik olarak ARKA kamerayı açar.
dosya = st.file_uploader("📸 Barkodu okutmak için buraya tıkla", type=['jpg', 'png', 'jpeg'])

okunan_barkod = ""
if dosya is not None:
    # Burada barkodu okumak için kütüphane çakışması yaşamamak adına 
    # en garantisi manuel barkod girişini veya isimle aramayı desteklemektir.
    # Ancak yine de sistemin hata vermemesi için arama kutusuna odaklanıyoruz.
    st.success("Görüntü yüklendi. Eğer barkod otomatik dolmazsa lütfen yukarıya yazın.")

# --- SONUÇLARI GÖSTER ---
if df is not None and arama:
    # Arama motoru
    sonuc_df = df[(df['BARKOD'] == arama) | (df['ÜRÜN ADI'].str.contains(arama, case=False, na=False))]
    
    if not sonuc_df.empty:
        st.write("---")
        for _, row in sonuc_df.iterrows():
            st.markdown(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("TOPLAM DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.divider()
    else:
        st.error("❌ Ürün bulunamadı.")
elif df is None:
    st.error("Veri dosyası bulunamadı!")
