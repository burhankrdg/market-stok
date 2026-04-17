import streamlit as st
import pandas as pd
import os
from PIL import Image

# Barkod okuma için en basit kütüphane
try:
    from pyzbar.pyzbar import decode
    import numpy as np
    BARCODE_READY = True
except:
    BARCODE_READY = False

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

# --- VERİ YÜKLEME ---
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

st.title("🛒 Çamlık Market Stok")

# --- KAMERA SİSTEMİ ---
# Streamlit'in kendi resmi bileşeni. Hata verme şansı yok.
img_file = st.camera_input("Barkodu okutmak için fotoğraf çekin")

okunan_barkod = ""

if img_file:
    if BARCODE_READY:
        img = Image.open(img_file)
        # Barkodu görüntüden çöz
        detected = decode(img)
        if detected:
            okunan_barkod = detected[0].data.decode("utf-8").strip()
            st.success(f"Barkod Yakalandı: {okunan_barkod}")
        else:
            st.warning("Barkod okunamadı, lütfen daha net çekin.")
    else:
        st.error("Barkod okuma kütüphanesi (pyzbar) eksik. Lütfen manuel girin.")

# --- ARAMA KUTUSU ---
arama = st.text_input("🔍 Barkod veya Ürün Adı:", value=okunan_barkod)

# --- SONUÇLAR ---
if df is not None and arama:
    sonuc = df[(df['BARKOD'] == arama) | (df['ÜRÜN ADI'].str.contains(arama, case=False, na=False))]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            st.divider()
            st.subheader(row['ÜRÜN ADI'])
            c1, c2 = st.columns(2)
            c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            st.info(f"💰 Kalem Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
