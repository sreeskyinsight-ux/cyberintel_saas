import streamlit as st
from openai import OpenAI
import json
import urllib.parse
import re

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CUSTOM CSS SUPER KONTRAS
# ---------------------------------------------------------
st.set_page_config(
    page_title="SaaS AI Toko Online - CyberSuite",
    page_icon="⚡",
    layout="wide"
)

# Force CSS Styling dengan tingkat prioritas tinggi
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0b0f19 100%) !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Header Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #94a3b8 !important;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }

    /* FIX TOTAL PERBAIKAN TOMBOL KONTRAST TINGGI */
    div.stButton > button {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        padding: 10px 20px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease-in-out !important;
    }

    /* Efek Hover untuk Tombol Standar */
    div.stButton > button:hover {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.8) !important;
        transform: translateY(-2px) !important;
    }

    /* TOMBOL UTAMA (PRIMARY) BERCAHAYA UNGU-BIRU TEKS PUTIH */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5, #9333ea) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(147, 51, 234, 0.6) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(168, 85, 247, 1) !important;
        transform: translateY(-2px) !important;
    }

    /* Teks Dalam Tombol Dijamin Putih / Terbaca */
    div.stButton > button p, div.stButton > button span {
        color: inherit !important;
        font-weight: 800 !important;
    }

    /* Tab Styling */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
    
    button[aria-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38bdf8 !important;
        border-bottom: 3px solid #38bdf8 !important;
    }

    /* Sidebar Fix */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown('<h1 class="main-title">⚡ CyberCommerce AI Engine</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Generasi Ekosistem Pemasaran Toko Online Berbasis Multi-Agent AI</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DAFTAR MODEL OPENROUTER
# ---------------------------------------------------------
MODEL_OPTIONS = {
    "Hermes 3 (Llama 3.1 405B)": "nousresearch/hermes-3-llama-3.1-405b",
    "Hermes 3 (Llama 3.1 70B)": "nousresearch/hermes-3-llama-3.1-70b",
    "DeepSeek V3": "deepseek/deepseek-chat",
    "DeepSeek R1 (Reasoning)": "deepseek/deepseek-r1",
    "DeepSeek R1 Distill (Llama 70B)": "deepseek/deepseek-r1-distill-llama-70b",
    "Llama 3.3 (70B)": "meta-llama/llama-3.3-70b-instruct",
    "Qwen 2.5 (72B)": "qwen/qwen-2.5-72b-instruct",
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
    st.header("⚙️ Control Panel")
    store_name = st.text_input("Nama Toko", value="Sri Store")
    wa_number = st.text_input("Nomor WhatsApp Toko", value="6281234567890")
    
    st.divider()
    selected_model_name = st.selectbox("🤖 Brain Model AI", list(MODEL_OPTIONS.keys()))
    selected_model_id = MODEL_OPTIONS[selected_model_name]
    
    st.divider()
    if not api_key:
        api_key = st.text_input("OpenRouter API Key", type="password", help="Masukkan sk-or-v1-...")

if not api_key:
    st.warning("⚠️ Masukkan OpenRouter API Key di sidebar atau atur via secrets.toml.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# ---------------------------------------------------------
# 4. HELPER FUNCTION UNTUK REQUEST AI
# ---------------------------------------------------------
def call_openrouter(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model=selected_model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            timeout=30
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        clean_json = match.group(0) if match else raw
        return json.loads(clean_json)
    except Exception as e:
        raise Exception(f"Koneksi gagal ke {selected_model_name}. Coba ganti model lain di sidebar. Detail: {e}")

# ---------------------------------------------------------
# 5. FORM INPUT UTAMA PRODUK
# ---------------------------------------------------------
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        prod_name = st.text_input("📦 Nama Produk", placeholder="Contoh: Gamis Rayon Premium")
        prod_price = st.number_input("💎 Harga Produk (Rp)", min_value=0, value=150000, step=5000)

    with col2:
        prod_category = st.selectbox("🏷️ Kategori", ["Fashion", "Kecantikan", "Elektronik", "Makanan/Minuman", "Lainnya"])
        prod_features = st.text_area("✨ Fitur / Keunggulan Utama", placeholder="Contoh: Bahan adem, resleting depan, tidak menerawang")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. INTEGRASI AGEN AI BERBASIS TAB
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Copywriting & WA", 
    "🚀 Marketing Strategy", 
    "🔍 SEO Marketplace", 
    "📊 Riset & Rekomendasi",
    "💬 CS & FAQ", 
    "🎨 Visual Prompt"
])

# --- TAB 1: COPYWRITING & CHECKOUT WA ---
with tab1:
    if st.button("✨ Execute Copywriting Agent", key="btn_tab1", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent memproses deskripsi & checkout link..."):
                try:
                    sys_p = "Kamu adalah ahli pemasaran e-commerce. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Fitur: {prod_features}.
