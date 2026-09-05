import streamlit as st
from openai import OpenAI
import json
import urllib.parse

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="SaaS AI Toko Online - Super Agent Ecosystem",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ SaaS AI Toko Online (Multi-Agent Multi-Model)")
st.caption("Solusi e-commerce lengkap: Copywriting, SEO Marketplace, Strategi Promosi, FAQ, dan Visual Prompt via OpenRouter.")

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
# 3. PENANGANAN API KEY & MODEL SELECTOR
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

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# ---------------------------------------------------------
# 4. FORM INPUT UTAMA PRODUK
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    prod_name = st.text_input("Nama Produk", placeholder="Contoh: Gamis Rayon Premium")
    prod_price = st.number_input("Harga Produk (Rp)", min_value=0, value=150000, step=5000)

with col2:
    prod_category = st.selectbox("Kategori", ["Fashion", "Kecantikan", "Elektronik", "Makanan/Minuman", "Lainnya"])
    prod_features = st.text_area("Fitur / Keunggulan Utama", placeholder="Contoh: Bahan adem, tidak menerawang, resleting depan")

st.divider()

# ---------------------------------------------------------
# 5. INTEGRASI AGEN AI BERBASIS TAB
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Copywriting & WA", 
    "📈 Strategi Promosi", 
    "🔍 SEO Marketplace", 
    "❓ CS & FAQ", 
    "🎨 Visual Prompt"
])

# Helper function untuk request AI
def call_openrouter(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=selected_model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```json"):
        raw = raw.replace("```json", "", 1).rstrip("```").strip()
    elif raw.startswith("```"):
        raw = raw.replace("
