import streamlit as st
import pandas as pd
import os
from streamlit_quagga2 import streamlit_quagga2

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- LOGO VE BAŞLIK ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>Canlı Barkod Terminali</h3>", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
        # Sütunları senin dosyandaki gerçek isimlerle eşle
        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
        
        # Sayısal Temizlik ve Hesaplama
        df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
        df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
        return df
    return None

df = verileri_yukle()

# --- CANLI BARKOD TARAYICI ---
# Bu bileşen kamerayı otomatik açar ve 'Take Photo' tuşuna basmanı gerektirmez.
st.write("📸 Barkodu kameraya gösterin...")
barkod_verisi = streamlit_quagga2(key='scanner')

# --- SONUÇLARI GÖSTER ---
# Barkod okunduğunda veya elle girildiğinde çalışır
arama_metni = ""

if barkod_verisi:
    arama_metni = barkod_verisi
    st.success(f"Okunan Barkod: {arama_metni}")
else:
    arama_metni = st.text_input("Veya Ürün Adı Girin:", "")

if df is not None and arama_metni:
    sonuc = df[df['ÜRÜN ADI'].str.contains(arama_metni, case=False, na=False) | (df['BARKOD'] == arama_metni)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            with st.container():
                st.markdown(f"### {row['ÜRÜN ADI']}")
                col1, col2 = st.columns(2)
                col1.metric("FİYAT", f"{row['FİYAT']} TL")
                col2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"Bu kalemdeki toplam mal değeri: **{row['KALEM DEĞERİ']:,.2f} TL**")
                st.divider()
    else:
        st.warning("Ürün bulunamadı.")
