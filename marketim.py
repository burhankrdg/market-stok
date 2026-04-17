import streamlit as st
import pandas as pd
import os
from streamlit_barcode_scanner import barcode_scanner # Bu kütüphane otomatik tarama yapar

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market Terminal", layout="centered")

# --- 1. GEREKLİ KÜTÜPHANE KONTROLÜ ---
# GitHub'daki requirements.txt dosyasına 'streamlit-barcode-scanner' eklemeyi unutma!

# --- 2. LOGO VE BAŞLIK ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>Canlı Barkod Terminali</h3>", unsafe_allow_html=True)
st.write("Barkodu kameraya gösterin, otomatik tanıyacaktır.")

# --- 3. VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
        
        # Sayısal Temizlik
        df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
        df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
        return df
    return None

df = verileri_yukle()

# --- 4. OTOMATİK BARKOD TARAYICI (TUŞSUZ) ---
# Bu bileşen kamerayı canlı açar ve barkodu görünce değeri döndürür.
okunan_barkod = barcode_scanner()

# --- 5. ARAMA VE SONUÇ ---
if okunan_barkod:
    st.audio("https://www.soundjay.com/buttons/beep-01a.mp3") # Barkod okununca 'Bip' sesi
    st.success(f"Okunan Barkod: {okunan_barkod}")
    arama_degeri = okunan_barkod
else:
    arama_degeri = st.text_input("Veya El ile Ürün/Barkod Girin:", "")

if df is not None and arama_degeri:
    sonuc = df[df['ÜRÜN ADI'].str.contains(arama_degeri, case=False, na=False) | (df['BARKOD'] == arama_degeri)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            with st.expander(f"📦 {row['ÜRÜN ADI']}", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"Bu kalemdeki toplam mal değeri: **{row['KALEM DEĞERİ']:,.2f} TL**")
    else:
        st.error("Ürün bulunamadı.")
