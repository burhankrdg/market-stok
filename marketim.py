import streamlit as st
import pandas as pd
import os
from PIL import Image

# Barkod okuma motorunu kontrol et
try:
    from pyzbar.pyzbar import decode
    import numpy as np
    BARKOD_SISTEMI = True
except:
    BARKOD_SISTEMI = False

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Stok", layout="centered")

# --- LOGO VE BAŞLIK ---
# GitHub'a yüklediğin image_1.png dosyasını kullanır
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>Canlı Barkod Okuma Sistemi</h3>", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
        # Sütunları senin dosyandaki gerçek isimlerle eşle
        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
        
        # Sayısal temizlik ve Hesaplamalar
        df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
        df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
        return df
    return None

df = verileri_yukle()

# --- KAMERA VE OKUMA SİSTEMİ ---
okunan_barkod = ""

# iPhone'da HTTPS olduğu için artık bu kısım hata vermeden kamerayı açar
with st.container():
    kamera_karesi = st.camera_input("Barkodu kameraya gösterin ve çekin")

    if kamera_karesi and BARKOD_SISTEMI:
        img = Image.open(kamera_karesi)
        sonuclar = decode(img)
        if sonuclar:
            okunan_barkod = sonuclar[0].data.decode("utf-8")
            st.success(f"✅ Barkod Algılandı: {okunan_barkod}")
            st.balloons()
        else:
            st.warning("⚠️ Barkod net değil veya bulunamadı. Lütfen tekrar deneyin.")

# --- ARAMA VE TABLO ---
st.write("---")
arama = st.text_input("🔍 Ürün Adı veya Barkod:", value=okunan_barkod)

if df is not None:
    # Arama motoru
    filtre = arama if arama else okunan_barkod
    if filtre:
        sonuc_df = df[df['ÜRÜN ADI'].str.contains(filtre, case=False, na=False) | (df['BARKOD'] == filtre)]
        
        if not sonuc_df.empty:
            for _, row in sonuc_df.iterrows():
                st.markdown(f"### {row['ÜRÜN ADI']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("FİYAT", f"{row['FİYAT']} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                c3.metric("KALEM DEĞERİ", f"{row['KALEM DEĞERİ']:,.2f} TL")
                st.write(f"**Barkod:** {row['BARKOD']}")
                st.divider()
        else:
            st.error("❌ Aranan ürün stokta bulunamadı.")
    else:
        st.info("Kameradan barkod çekin veya yukarıya ürün adı yazın.")
else:
    st.error("Dosya bulunamadı! Lütfen envanter.csv dosyasını GitHub'a yüklediğinizden emin olun.")
