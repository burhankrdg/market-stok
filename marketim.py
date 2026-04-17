import streamlit as st
import pandas as pd
import os
from PIL import Image

# Barkod okuma kütüphanesi kontrolü
try:
    from pyzbar.pyzbar import decode
    import numpy as np
    BARKOD_DESTEGI = True
except:
    BARKOD_DESTEGI = False

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

# --- SİSTEM ---
okunan_barkod = ""

# 1. ADIM: KAMERA (Garantili Yöntem)
st.info("📸 Barkodu okutmak için aşağıdaki butona basın")
kamera_resmi = st.camera_input("Barkod Tara", label_visibility="collapsed")

if kamera_resmi and BARKOD_DESTEGI:
    img = Image.open(kamera_resmi)
    sonuclar = decode(img)
    if sonuclar:
        okunan_barkod = sonuclar[0].data.decode("utf-8")
        st.success(f"✅ Okunan Barkod: {okunan_barkod}")
    else:
        st.warning("⚠️ Barkod net değil, lütfen tekrar deneyin.")

# 2. ADIM: ARAMA ÇUBUĞU (Geri Geldi!)
st.write("---")
arama = st.text_input("🔍 Barkod veya Ürün Adı Girin:", value=okunan_barkod)

# 3. ADIM: SONUÇLARI GÖSTER
if df is not None and arama:
    # Hem barkod hem isimde ara
    sonuc_df = df[(df['BARKOD'] == arama) | (df['ÜRÜN ADI'].str.contains(arama, case=False, na=False))]
    
    if not sonuc_df.empty:
        for _, row in sonuc_df.iterrows():
            with st.container():
                st.markdown(f"### {row['ÜRÜN ADI']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("FİYAT", f"{row['FİYAT']} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                c3.metric("TOPLAM DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
                st.write(f"🏷️ **Barkod:** {row['BARKOD']}")
                st.divider()
    else:
        st.error("❌ Ürün bulunamadı.")
elif df is None:
    st.error("Veri dosyası (csv) bulunamadı. Lütfen GitHub'a yükleyin.")
