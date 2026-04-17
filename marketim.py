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

# --- 1. SAYFA VE TEMA AYARLARI ---
# Sayfayı logoya uygun aydınlık ve geniş yapıyoruz
st.set_page_config(page_title="Çamlık Market Stok", layout="wide", page_icon="image_1.png")

# --- 2. GÖRSEL TASARIM (CSS) ---
# Logonun yeşil ve beyaz tonlarını temel alan modern bir tema
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #f7fff7; }
    
    /* Başlık ve Slogan */
    .market-title {
        color: #2a7e2a; 
        font-size: 36px; 
        font-weight: bold; 
        text-align: center;
        margin-bottom: 0px;
    }
    .market-slogan {
        color: #6da26d;
        font-size: 18px;
        font-style: italic;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    
    /* Input Alanları ve Tablo */
    .stTextInput>div>div>input {
        background-color: #ffffff;
        border: 2px solid #a3d9a3;
        border-radius: 8px;
        color: #2a7e2a;
    }
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #a3d9a3;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. VERİ YÜKLEME ---
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    # Senin 2.xls - envanter.csv dosyanı veya envanter içeren dosyayı bulur
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            # Sütun isimlerini senin dosyandaki başlıklarla (Stok Kodu, Stok Adı vb.) eşliyoruz
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python')
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
            return df, hedef
        except:
            return None, "Dosya okuma hatası."
    return None, None

df, dosya_adi = verileri_yukle()

# --- 4. ARARYÜZ BAŞLANGIÇ (Logo ve Slogan) ---
# Masaüstünde ve mobilde logoyu ve sloganı en üstte gösterir
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.image("image_1.png", use_container_width=True) # Logonun adı 'image_1.png' olmalı
    st.markdown('<p class="market-slogan">"Mahallemizin Gülen Yüzü"</p>', unsafe_allow_html=True)

# --- 5. KAMERA BÖLÜMÜ (IPHONE & TABLET UYUMLU) ---
# file_uploader kullanarak iPhone/tabletlerdeki kamera izni sorununu aşıyoruz.
# Bu düğme iPhone'da direkt "Fotoğraf Çek" seçeneğini açar.
foto_yukleyici = st.file_uploader("📸 Barkodu kameraya gösterin ve fotoğraf çekin", type=['jpg', 'jpeg', 'png'], help="Düğmeye dokunun, telefon kameranız açılacaktır.")

okunan_barkod = ""

if foto_yukleyici and BARKOD_SISTEMI:
    try:
        img = Image.open(foto_yukleyici)
        # Barkodu tarama
        detaylar = decode(img)
        if detaylar:
            okunan_barkod = detaylar[0].data.decode("utf-8")
            st.success(f"Başarılı! Okunan Barkod: {okunan_barkod}")
            st.balloons() # Güzel bir efekt ekliyoruz
        else:
            st.error("Barkod okunamadı! Lütfen daha net ve yakın bir fotoğraf çekin.")
    except Exception as e:
        st.error(f"Fotoğraf işlenemedi: {e}")

# --- 6. HIZLI ARAMA VE SONUÇ ---
st.write("---")
# Barkod okutulduğunda burası otomatik dolar
arama_kutusu = st.text_input("🔍 Barkod veya Ürün Adı:", value=okunan_barkod, placeholder="Ürün adı veya barkod girin...")

if df is not None:
    # Arama motoru: Hem isimde hem barkodda arar
    sonuc = df[df['ÜRÜN ADI'].str.contains(arama_kutusu, case=False, na=False) | (df['BARKOD'] == arama_kutusu)]
    
    if arama_kutusu:
        if not sonuc.empty:
            st.write(f"### Bulunan Ürün Detayları ({len(sonuc)} Adet)")
            # Sadece önemli sütunları daha temiz göster
            st.dataframe(sonuc[['BARKOD', 'ÜRÜN ADI', 'STOK', 'FİYAT']], use_container_width=True, height=400)
        else:
            st.warning("Bu kriterde bir ürün bulunamadı.")
    else:
        # Arama kutusu boşsa tüm listeyi göster
        st.write("### Tüm Envanter Listesi")
        st.dataframe(df[['BARKOD', 'ÜRÜN ADI', 'STOK', 'FİYAT']], use_container_width=True, height=500)
    
    # Alt Bilgi
    st.info(f"Şu an çalışan liste: {dosya_adi}")

else:
    st.error("CSV dosyası bulunamadı! Lütfen '2.xls - envanter.csv' dosyasını klasöre kopyalayın.")