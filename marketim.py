import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. AYARLAR VE VERİ YÜKLEME ---
st.set_page_config(page_title="Çamlık Market", layout="centered")

@st.cache_data
def verileri_yukle():
    # Klasördeki tüm dosyaları tara
    dosyalar = [f for f in os.listdir('.') if f.endswith('.csv')]
    # Envanter veya 2.xls içeren dosyayı bul
    hedef = next((d for d in dosyalar if 'envanter' in d.lower() or '2.xls' in d.lower()), None)
    
    if hedef:
        try:
            # Barkodları metin olarak oku (0'ların kaybolmaması için en garanti yol)
            df = pd.read_csv(hedef, encoding='utf-8-sig', sep=None, engine='python', dtype={'BARKOD': str})
            # Sütun isimlerini zorla eşitle
            df.columns = ['BARKOD', 'ÜRÜN ADI', 'STOK', 'BİRİM', 'FİYAT'] + list(df.columns[5:])
            # Veri temizliği
            df['BARKOD'] = df['BARKOD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['FİYAT'] = pd.to_numeric(df['FİYAT'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['STOK'] = pd.to_numeric(df['STOK'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except:
            return None
    return None

df = verileri_yukle()

# URL'den gelen barkodu yakala (Kameranın fırlatacağı veri)
params = st.query_params
okunan_barkod = params.get("barcode", "")

# --- 2. TASARIM VE ARAYÜZ ---
st.markdown("<h2 style='text-align: center; color: #2a7e2a;'>🚀 Çamlık Market Terminal</h2>", unsafe_allow_html=True)

# Eğer barkod okunmadıysa kamerayı göster
if not okunan_barkod:
    st.warning("📸 Barkodu kameraya gösterin, otomatik bulacaktır.")
    
    # KESİN ÇALIŞAN JAVASCRIPT: Barkodu okuduğu an ana sayfayı (parent) yeniler
    kamera_html_kodu = """
    <div id="reader" style="width: 100%; border-radius: 15px; border: 4px solid #2a7e2a; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        
        function onScanSuccess(decodedText) {
            // 1. Onay sesi
            var audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();
            
            // 2. Streamlit'e veriyi URL üzerinden zorla gönder (En sağlam iletişim yolu)
            const currentUrl = new URL(window.parent.location.href);
            currentUrl.searchParams.set('barcode', decodedText.trim());
            
            // 3. Sayfayı yeni parametreyle tamamen yenile
            window.parent.location.href = currentUrl.href;
            
            html5QrCode.stop();
        }

        const config = { 
            fps: 25, 
            qrbox: { width: 280, height: 160 },
            aspectRatio: 1.0
        };

        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
            .catch(err => console.error("Kamera başlatılamadı:", err));
    </script>
    """
    components.html(kamera_html_kodu, height=380)
    
    # Manuel yedek arama kutusu
    manuel = st.text_input("🔍 Barkod veya Ürün Adı Girin:", key="manuel_search")
    if manuel:
        st.query_params["barcode"] = manuel
        st.rerun()

# Eğer barkod okunduysa sonucu göster
else:
    if st.button("⬅️ Yeni Ürün Okut (Kamerayı Aç)"):
        st.query_params.clear()
        st.rerun()

    if df is not None:
        hedef = str(okunan_barkod).strip()
        # Barkodu tam eşleşme veya ürün adı içerisinde arama
        sonuc = df[(df['BARKOD'] == hedef) | (df['ÜRÜN ADI'].str.contains(hedef, case=False, na=False))]
        
        if not sonuc.empty:
            st.divider()
            for _, row in sonuc.iterrows():
                st.success(f"### {row['ÜRÜN ADI']}")
                c1, c2 = st.columns(2)
                c1.metric("FİYAT", f"{row['FİYAT']:.2f} TL")
                c2.metric("STOK", f"{int(row['STOK'])} {row['BİRİM']}")
                st.info(f"💰 Toplam Değer: {row['STOK'] * row['FİYAT']:,.2f} TL")
                st.caption(f"Barkod: {row['BARKOD']}")
        else:
            st.error(f"❌ '{hedef}' barkodlu ürün listede bulunamadı!")
            st.info("İpucu: Envanter dosyanızdaki barkodun cihaz tarafından doğru okunduğundan emin olun.")
