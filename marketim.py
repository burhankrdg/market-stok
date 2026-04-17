import streamlit as st
import pandas as pd
import os

# --- 1. AYARLAR ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

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

# --- 2. ARAYÜZ ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# Manuel giriş kutusu - Odak noktası burası
arama = st.text_input("🔍 Barkodu okutun veya yazın:", key="barkod_input", placeholder="Barkod bekleniyor...")

if arama:
    if df is not None:
        hedef = str(arama).strip()
        sonuc = df[(df['BARKOD'] == hedef) | (df['ÜRÜN ADI'].str.contains(hedef, case=False, na=False))]
        
        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.markdown(f"<h1 style='color: #2a7e2a; text-align: center;'>{row['FİYAT']:.2f} TL</h1>", unsafe_allow_html=True)
                st.subheader(f"📦 {row['ÜRÜN ADI']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                with c2:
                    st.metric("DEĞER", f"{row['STOK'] * row['FİYAT']:,.2f} TL")
                st.divider()
        else:
            st.error(f"❌ '{hedef}' bulunamadı.")
            
# Alt kısma kamera yerine manuel yükleme butonu (Eğer dosya değişirse)
if st.button("🔄 Verileri Yenile"):
    st.cache_data.clear()
    st.rerun()
