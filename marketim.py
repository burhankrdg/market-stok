import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- AYARLAR ---
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

# --- BAŞLIK ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# --- JAVASCRIPT KÖPRÜSÜ (GİZLİ İLETİŞİM) ---
# Okunan barkodu bu gizli bileşen aracılığıyla Python'a alacağız
okunan_barkod = components.declare_component("barcode_scanner", path=".") 

# JavaScript kodunu doğrudan sayfaya gömüyoruz
kamera_html = """
<div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a;"></div>
<script src="https://unpkg.com/html5-qrcode"></script>
<script>
    const html5QrCode = new Html5Qrcode("reader");
    const config = { fps: 25, qrbox: { width: 250, height: 150 } };
    
    const success = (text) => {
        // 1. Bip sesi
        var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
        audio.play();
        
        // 2. Streamlit'e veriyi URL üzerinden DEĞİL, doğrudan state üzerinden gönder
        // Pencereyi kapatmadan veya yenilemeden doğrudan Python değişkenini tetikler
        window.parent.postMessage({
            type: 'streamlit:set_query_params',
            query_params: {barcode: text.trim()}
        }, '*');

        // Hafif bir bekleme ile sayfayı zorla dürt
        setTimeout(() => { window.parent.location.reload(); }, 150);
    };

    html5QrCode.start({ facingMode: "environment" }, config, success);
</script>
"""

# URL parametresini kontrol et
barkod_param = st.query_params.get("barcode", "")

if not barkod_param:
    components.html(kamera_html, height=350)
    st.info("📸 Barkodu kameraya gösterin...")
    
    # Yedek arama kutusu
    manuel = st.text_input("🔍 Veya Elle Yazın:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()
else:
    # Ürün Detay Ekranı
    if st.button("⬅️ Yeni Ürün Tara"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef = str(barkod_param).strip()
        sonuc = df[df['BARKOD'] == hedef]
        
        if sonuc.empty:
            sonuc = df[df['BARKOD'].str.contains(hedef, na=False)]

        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Toplam Mal Değeri: {row['STOK'] * row['FİYAT']:,.2f} TL")
        else:
            st.error(f"❌ Barkod bulunamadı: {hedef}")
