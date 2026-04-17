import streamlit as st
import pandas as pd
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

# --- VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            # Barkodların bozulmaması için string (metin) olarak okuyoruz
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            # Temizlik
            df['BARKOD'] = df['BARKOD'].astype(str).str.split('.').str[0].str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
            return df
        except: return None
    return None

df = verileri_yukle()

# --- LOGO ---
if os.path.exists("image_1.png"):
    st.image("image_1.png", use_container_width=True)

st.markdown("<h3 style='text-align: center; color: #2a7e2a;'>🛒 Stok Sorgulama Terminali</h3>", unsafe_allow_html=True)

# --- ANA SİSTEM (EN GARANTİ YÖNTEM) ---
# iPhone'da arka kamerayı açmanın tek %100 yolu budur.
st.info("📸 Barkodun fotoğrafını çekin, fiyat otomatik gelecektir.")
kamera_verisi = st.camera_input("Barkod Tara", label_visibility="collapsed")

# Barkod okuma motoru (Dışarıdan kütüphane yerine tarayıcıyı kullanır)
if kamera_verisi:
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        import numpy as np
        
        img = Image.open(kamera_verisi)
        sonuclar = decode(img)
        
        if sonuclar:
            barkod = sonuclar[0].data.decode("utf-8").strip()
            st.success(f"✅ Barkod Okundu: {barkod}")
            # Otomatik arama için arama değişkenini güncelle
            st.session_state['arama'] = barkod
        else:
            st.warning("⚠️ Barkod net çıkmadı, lütfen biraz daha uzaktan ve ışıklı çekin.")
    except:
        st.error("Sistemde küçük bir teknik eksiklik var (pyzbar). Lütfen manuel arama kutusunu kullanın.")

# --- ARAMA KUTUSU (HER ZAMAN ÇALIŞIR) ---
st.divider()
arama_degeri = st.session_state.get('arama', "")
arama = st.text_input("🔍 Barkod No veya Ürün Adı Girin:", value=arama_degeri)

# --- SONUÇLARI GÖSTER ---
if df is not None and arama:
    # Hem barkodda hem isimde ara
    sonuc = df[(df['BARKOD'] == arama) | (df['ÜRÜN ADI'].str.contains(arama, case=False, na=False))]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            st.success(f"### {row['ÜRÜN ADI']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
            c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
            c3.metric("TOPLAM DEĞER", f"{row['KALEM DEĞERİ']:,.2f} TL")
            st.divider()
    else:
        st.error(f"❌ '{arama}' bulunamadı.")
