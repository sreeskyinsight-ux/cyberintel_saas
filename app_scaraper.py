import streamlit as st
from openai import OpenAI
import json
import urllib.parse

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="SaaS AI Toko Online",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ SaaS AI Toko Online (Lightweight)")
st.caption("Generator deskripsi produk, hashtag, dan integrasi checkout WhatsApp otomatis.")

# ---------------------------------------------------------
# 2. PENANGANAN API KEY (LOKAL & STREAMLIT CLOUD SAFE)
# ---------------------------------------------------------
api_key = None

# Cek apakah ada API key dari st.secrets (Streamlit Cloud / secrets.toml)
try:
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

# Jika tidak ada di secrets, sediakan input manual di Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan Toko")
    store_name = st.text_input("Nama Toko", value="Sri Store")
    wa_number = st.text_input("Nomor WhatsApp Toko", value="6281234567890", help="Gunakan kode negara (contoh: 628...)")
    
    st.divider()
    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password", help="Masukkan API Key OpenAI Anda")

if not api_key:
    st.warning("⚠️ Silakan masukkan OpenAI API Key di sidebar atau atur melalui secrets.toml untuk menggunakan fitur AI.")
    st.stop()

# Inisialisasi Klien OpenAI
client = OpenAI(api_key=api_key)

# ---------------------------------------------------------
# 3. FORM INPUT PRODUK
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    prod_name = st.text_input("Nama Produk", placeholder="Contoh: Gamis Rayon Premium")
    prod_price = st.number_input("Harga Produk (Rp)", min_value=0, value=150000, step=5000)

with col2:
    prod_category = st.selectbox("Kategori", ["Fashion", "Kecantikan", "Elektronik", "Makanan/Minuman", "Lainnya"])
    prod_features = st.text_area("Fitur / Keunggulan Utama", placeholder="Contoh: Bahan adem, tidak menerawang, ada resleting depan")

st.divider()

# ---------------------------------------------------------
# 4. PROSES GENERASI KONTEN AI
# ---------------------------------------------------------
if st.button("✨ Hasilkan Konten Toko via AI", type="primary"):
    if not prod_name:
        st.error("Nama produk wajib diisi!")
    else:
        with st.spinner("AI sedang merancang deskripsi dan materi promosi..."):
            prompt = f"""
            Kamu adalah ahli pemasaran e-commerce profesional.
            Buatkan materi penjualan untuk produk berikut:
            - Nama Produk: {prod_name}
            - Kategori: {prod_category}
            - Keunggulan: {prod_features}

            Kembalikan jawaban DALAM FORMAT JSON VALID dengan struktur kunci berikut:
            {{
                "deskripsi": "Deskripsi persuasif 2 paragraf yang siap pakai di toko online",
                "keunggulan": ["poin keunggulan 1", "poin keunggulan 2", "poin keunggulan 3"],
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
            }}
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "Kamu adalah asisten e-commerce yang merespon hanya dalam format JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )

                # Simpan hasil generasi ke session state agar tidak hilang saat di-click/refresh
                result = json.loads(response.choices[0].message.content)
                st.session_state["ai_result"] = result
                st.success("Konten berhasil dibuat!")

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memanggil OpenAI API: {e}")

# ---------------------------------------------------------
# 5. MENAMPILKAN HASIL & TAUTAN CHECKOUT WHATSAPP
# ---------------------------------------------------------
if "ai_result" in st.session_state:
    res = st.session_state["ai_result"]
    
    st.subheader("📝 Deskripsi Penjualan")
    st.write(res.get("deskripsi", ""))

    st.subheader("💡 Keunggulan Utama")
    for point in res.get("keunggulan", []):
        st.write(f"• {point}")

    st.subheader("🏷️ Rekomendasi Hashtag")
    st.write(" ".join(res.get("hashtags", [])))

    st.divider()

    # Generator Link Checkout WhatsApp
    wa_message = f"Halo {store_name}, saya mau pesan produk berikut:\n\n*Nama Produk:* {prod_name}\n*Harga:* Rp {prod_price:,}\n\nApakah stok masih tersedia?"
    wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_message)}"

    st.subheader("📲 Tes Transaksi")
    st.markdown(
        f'<a href="{wa_url}" target="_blank">'
        f'<button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; font-weight:bold;">'
        f'Pesan via WhatsApp'
        f'</button></a>',
        unsafe_allow_html=True
    )
