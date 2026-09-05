import streamlit as st
from openai import OpenAI
import json
import urllib.parse

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="SaaS AI Toko Online Multi-Model",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ SaaS AI Toko Online (Multi-Model AI)")
st.caption("Gunakan berbagai pilihan model AI (DeepSeek V3/R1, Llama 3, Claude, Gemini, Qwen, Hermes) via OpenRouter.")

# ---------------------------------------------------------
# 2. DAFTAR MODEL OPENROUTER
# ---------------------------------------------------------
MODEL_OPTIONS = {
    "DeepSeek V3": "deepseek/deepseek-chat",
    "DeepSeek R1 (Reasoning Original)": "deepseek/deepseek-r1",
    "DeepSeek R1 Distill (Llama 70B)": "deepseek/deepseek-r1-distill-llama-70b",
    "DeepSeek R1 Distill (Qwen 32B)": "deepseek/deepseek-r1-distill-qwen-32b",
    "Llama 3.3 (70B)": "meta-llama/llama-3.3-70b-instruct",
    "Qwen 2.5 (72B)": "qwen/qwen-2.5-72b-instruct",
    "Hermes 3 (Llama 3.1 405B)": "nousresearch/hermes-3-llama-3.1-405b",
    "Gemini Flash 1.5": "google/gemini-flash-1.5",
    "Claude 3.5 Haiku": "anthropic/claude-3.5-haiku"
}

# ---------------------------------------------------------
# 3. PENANGANAN API KEY & MODEL SELECTOR IN SIDEBAR
# ---------------------------------------------------------
api_key = None

try:
    if "OPENROUTER_API_KEY" in st.secrets:
        api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    pass

with st.sidebar:
    st.header("⚙️ Pengaturan Toko & AI")
    store_name = st.text_input("Nama Toko", value="Sri Store")
    wa_number = st.text_input("Nomor WhatsApp Toko", value="6281234567890")
    
    st.divider()
    selected_model_name = st.selectbox("🤖 Pilih Model AI", list(MODEL_OPTIONS.keys()))
    selected_model_id = MODEL_OPTIONS[selected_model_name]
    
    st.divider()
    if not api_key:
        api_key = st.text_input("OpenRouter API Key", type="password", help="Masukkan sk-or-v1-...")

if not api_key:
    st.warning("⚠️ Silakan masukkan OpenRouter API Key di sidebar atau atur via secrets.toml.")
    st.stop()

# Inisialisasi Client OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# ---------------------------------------------------------
# 4. FORM INPUT PRODUK
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    prod_name = st.text_input("Nama Produk", placeholder="Contoh: Gamis Rayon Premium")
    prod_price = st.number_input("Harga Produk (Rp)", min_value=0, value=150000, step=5000)

with col2:
    prod_category = st.selectbox("Kategori", ["Fashion", "Kecantikan", "Elektronik", "Makanan/Minuman", "Lainnya"])
    prod_features = st.text_area("Fitur / Keunggulan Utama", placeholder="Contoh: Bahan adem, resleting depan")

st.divider()

# ---------------------------------------------------------
# 5. PROSES GENERASI KONTEN AI
# ---------------------------------------------------------
if st.button(f"✨ Hasilkan Konten via {selected_model_name}", type="primary"):
    if not prod_name:
        st.error("Nama produk wajib diisi!")
    else:
        with st.spinner(f"Memproses data menggunakan {selected_model_name}..."):
            prompt = f"""
            Kamu adalah ahli pemasaran e-commerce.
            Buatkan materi penjualan untuk produk berikut:
            - Nama Produk: {prod_name}
            - Kategori: {prod_category}
            - Keunggulan: {prod_features}

            PENTING: Kembalikan jawaban HANYA DALAM FORMAT JSON VALID tanpa teks pembuat/markdown tambahan dengan struktur:
            {{
                "deskripsi": "Deskripsi persuasif 2 paragraf yang siap pakai",
                "keunggulan": ["poin 1", "poin 2", "poin 3"],
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
            }}
            """

            try:
                response = client.chat.completions.create(
                    model=selected_model_id,
                    messages=[
                        {"role": "system", "content": "Kamu adalah asisten e-commerce yang merespon hanya dalam format JSON valid."},
                        {"role": "user", "content": prompt}
                    ]
                )

                raw_content = response.choices[0].message.content.strip()
                
                # Pembersihan teks jika AI menyertakan penanda ```json
                if raw_content.startswith("```json"):
                    raw_content = raw_content.replace("```json", "", 1).rstrip("```").strip()
                elif raw_content.startswith("```"):
                    raw_content = raw_content.replace("```", "", 1).rstrip("```").strip()

                result = json.loads(raw_content)
                st.session_state["ai_result"] = result
                st.success(f"Konten berhasil dibuat oleh {selected_model_name}!")

            except Exception as e:
                st.error(f"Terjadi kesalahan pada {selected_model_name}: {e}")

# ---------------------------------------------------------
# 6. HASIL & CHECKOUT WHATSAPP
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

    wa_message = f"Halo {store_name}, saya mau pesan produk berikut:\n\n*Nama Produk:* {prod_name}\n*Harga:* Rp {prod_price:,}\n\nApakah stok masih tersedia?"
    wa_url = f"[https://wa.me/](https://wa.me/){wa_number}?text={urllib.parse.quote(wa_message)}"

    st.subheader("📲 Tes Transaksi")
    st.markdown(
        f'<a href="{wa_url}" target="_blank">'
        f'<button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; font-weight:bold;">'
        f'Pesan via WhatsApp'
        f'</button></a>',
        unsafe_allow_html=True
    )
