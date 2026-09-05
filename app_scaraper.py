import streamlit as st
from openai import OpenAI
import json
import urllib.parse
import re

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CUSTOM CSS FUTURISTIK SUPER KONTRAS
# ---------------------------------------------------------
st.set_page_config(
    page_title="SaaS AI Toko Online - CyberSuite",
    page_icon="⚡",
    layout="wide"
)

# Injeksi CSS Futuristik dengan Kontras Tinggi (Prioritas !important)
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
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

    /* FIX TOMBOL KONTRAS TINGGI - HURUF SANGAT TEBAL DAN KETARA */
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
# 2. DAFTAR MODEL OPENROUTER (DENGAN SLUG PERBAIKAN REVISI)
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
    selected_model_name
