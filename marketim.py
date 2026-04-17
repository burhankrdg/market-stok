import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. AYARLAR ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

# Veriyi bir kez yükleyip hafızada tutuyoruz
@st.cache_data
def verileri_yukle():
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    if hedef:
        try:
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            # Barkod temizliği
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except: return None
    return None

df = verileri_yukle()

# --- 2. BARKOD YAKALAMA MANTIĞI ---
# Sayfa yenilendiğinde ilk iş adres çubuğuna bakmak
query_barcode = st.query_params.get("barcode", "")

# --- 3. ARAYÜZ ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# EĞER BARKOD YOKSA: KAMERAYI AÇ
if not query_barcode:
    st.info("📸 Barkodu kameraya gösterin...")
    
    kamera_html = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        function onScanSuccess(decodedText) {
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            const barcode = decodedText.trim();
            // ADRESİ GÜNCELLE: Bu işlem sayfayı otomatik yeniler ve Python'u uyandırır
            const u = new URL(window.parent.location.href);
            u.searchParams.set('barcode', barcode);
            window.parent.location.href = u.href;
            
            html5QrCode.stop();
        }
        html5QrCode.start({ facingMode: "environment" }, { fps: 25, qrbox: 250 }, onScanSuccess);
    </script>
    """
    components.html(kamera_html, height=360)
    
    manuel = st.text_input("🔍 Barkod veya Ürün Adı Girin:")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

# EĞER BARKOD VARSA: ÜRÜNÜ GÖSTER
else:
    if st.button("⬅️ YENİ ÜRÜN OKUT"):
        st.query_params.clear() # URL'yi temizle
        st.rerun()

    if df is not None:
        target = str(query_barcode).strip()
        # Hem tam barkod hem de ürün adı içinde ara
        sonuc = df[(df['BARKOD'] == target) | (df['ÜRÜN ADI'].str.contains(target, case=False, na=False))]
        
        if not sonuc.empty:
            st.success(f"### Barkod Okundu: {target}")
            st.divider()
            for _, row in sonuc.iterrows():
                st.markdown(f"<h1 style='color: #2a7e2a;'>{row['FİYAT']:.2f} TL</h1>", unsafe_allow_html=True)
                st.subheader(row['ÜRÜN ADI'])
                c1, c2 = st.columns(2)
                c1.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                c2.metric("TOPLAM DEĞER", f"{row['STOK'] * row['FİYAT']:,.2f} TL")
                st.divider()
        else:
            st.error(f"❌ Ürün bulunamadı: {target}")
            st.info("İpucu: Eğer barkod doğruysa, CSV dosyanızda bu numaranın kayıtlı olduğundan emin olun.")
