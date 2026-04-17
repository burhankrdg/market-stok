import streamlit as st
import pandas as pd
import os
from PIL import Image

# Barkod motoru (pyzbar)
try:
    from pyzbar.pyzbar import decode
    import numpy as np
    BARKOD_OKUYUCU = True
except:
    BARKOD_OKUYUCU = False

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Stok", layout="centered")

# --- LOGO VE BAŞLIK ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>🛒 Stok Sorgulama Terminali</h3>", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
        df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
        df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
        return df
    return None

df = verileri_yukle()

# --- ANA SİSTEM ---
okunan_barkod = ""

# 1. ADIM: Kamerayı Aç
st.write("📸 **Barkodu okutmak için 'Fotoğraf Çek' düğmesine basın:**")
kamera_verisi = st.camera_input("Barkod Tara", label_visibility="collapsed")

# 2. ADIM: Görseli İşle
if kamera_verisi:
    img = Image.open(kamera_verisi)
    # Barkodu bulmaya çalış
    sonuclar = decode(img)
    
    if sonuclar:
        okunan_barkod = sonuclar[0].data.decode("utf-8")
        st.success(f"✅ Barkod Bulundu: {okunan_barkod}")
        # Bip sesi simülasyonu
        st.toast("Barkod başarıyla okundu!", icon="🔔")
    else:
        st.error("❌ Barkod net değil. Lütfen daha dik ve ışıklı bir açıyla tekrar deneyin.")

# 3. ADIM: Arama ve Gösterim
st.divider()
arama = st.text_input("🔍 Manuel Barkod veya Ürün Adı:", value=okunan_barkod)

if df is not None and arama:
    sonuc = df[df['ÜRÜN ADI'].str.contains(arama, case=False, na=False) | (df['BARKOD'] == arama)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            with st.container():
                st.markdown(f"### {row['ÜRÜN ADI']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("FİYAT", f"{row['FİYAT']} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                c3.metric("KALEM DEĞERİ", f"{row['KALEM DEĞERİ']:,.2f} TL")
                st.write(f"🏷️ **Barkod:** {row['BARKOD']}")
                st.divider()
    else:
        st.warning("Ürün bulunamadı.")
