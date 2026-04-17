import streamlit as st
import pandas as pd
import os
from streamlit_zxing import zxing_barcode_scanner

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
        # Sütun isimlerini sabitle
        df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
        
        # Sayısal Temizlik
        df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df['KALEM DEĞERİ'] = df['STOK'] * df['FİYAT']
        df['BARKOD'] = df['BARKOD'].astype(str).str.strip()
        return df
    return None

df = verileri_yukle()

# --- CANLI BARKOD TARAYICI (ZXING) ---
st.write("📸 Barkodu kameraya gösterin (Otomatik okur)")
# Bu bileşen hiçbir düğme gerektirmeden barkodu canlı yakalar
barkod_sonucu = zxing_barcode_scanner(key='terminal_scanner')

# --- SONUÇLARI GÖSTER ---
arama_metni = ""

if barkod_sonucu:
    # Barkod verisi gelince içindeki metni alıyoruz
    arama_metni = barkod_sonucu['barcodeText']
    st.success(f"✅ Okundu: {arama_metni}")
else:
    arama_metni = st.text_input("Veya Ürün Adı Girin:", "")

if df is not None and arama_metni:
    # Barkod veya isimle eşleşenleri bul
    sonuc = df[df['ÜRÜN ADI'].str.contains(arama_metni, case=False, na=False) | (df['BARKOD'] == arama_metni)]
    
    if not sonuc.empty:
        for _, row in sonuc.iterrows():
            with st.container():
                st.markdown(f"#### {row['ÜRÜN ADI']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("FİYAT", f"{row['FİYAT']} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                c3.metric("KALEM DEĞERİ", f"{row['KALEM DEĞERİ']:,.2f} TL")
                st.divider()
    elif arama_metni:
        st.warning("Ürün bulunamadı.")
