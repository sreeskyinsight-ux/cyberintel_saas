import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"  # Mencegah error telemetry Streamlit

# --- PENGAMAN IMPORT PYDANTIC V1 ---
try:
    import pydantic.v1
except ImportError:
    import pydantic

import streamlit as st
from openai import OpenAI

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CyberIntel Enterprise SaaS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan Cyber/SaaS yang elegan
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #ff2121;
    }
    .sidebar .sidebar-content {
        background-color: #16192b;
    }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Session State untuk Riwayat & Autentikasi Simulasi
if "history" not in st.session_state:
    st.session_state.history = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Default login otomatis untuk kemudahan uji coba

# --- SIDEBAR: NAVIGASI & KONTROL ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/cyber-security.png", width=80)
    st.title("CyberIntel Ops")
    st.markdown("---")
    
    st.subheader("🔑 Konfigurasi API")
    openrouter_api_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
    
    st.markdown("---")
    st.subheader("📂 Arsip Investigasi")
    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history):
            if st.button(f"🔍 {item['topic'][:25]}...", key=f"hist_{idx}"):
                st.info(f"Menampilkan arsip: {item['topic']}")
    else:
        st.caption("Belum ada riwayat investigasi.")

# --- HALAMAN UTAMA: COMMAND CENTER ---
st.title("🛡️ CyberIntel Enterprise SaaS")
st.markdown("### Platform Intelijen Siber Multi-Agen Berbasis AI Otonom")
st.markdown("---")

# Form Input Utama
with st.form("intel_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        target_topic = st.text_input("Target Investigasi / Topik Siber:", placeholder="Contoh: Analisis kerentanan zero-day pada server enterprise atau kebocoran data.")
    with col2:
        agent_mode = st.selectbox("Mode Agen:", ["Multi-Agent (CrewAI)", "Quick LLM (Hermes/OpenAI)"])
    
    submit_btn = st.form_submit_button("🚀 Jalankan Operasi Intelijen")

# Logika Eksekusi saat tombol diklik
if submit_btn:
    if not target_topic:
        st.warning("⚠️ Mohon masukkan target atau topik investigasi terlebih dahulu!")
    elif not openrouter_api_key:
        st.warning("⚠️ Mohon masukkan OpenRouter API Key kamu di sidebar!")
    else:
        with st.spinner("🔄 Sedang mengerahkan tim agen intelijen siber... Mohon tunggu..."):
            try:
                # Inisialisasi Client OpenAI menggunakan OpenRouter Endpoint
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_api_key,
                )
                
                # Simulasi/Eksekusi Permintaan ke LLM (OpenRouter)
                response = client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet", # Bisa disesuaikan dengan model pilihan
                    messages=[
                        {"role": "system", "content": "Anda adalah analis intelijen siber senior. Buat laporan investigasi yang terstruktur, tajam, dan profesional dalam format Markdown."},
                        {"role": "user", "content": f"Lakukan analisis intelijen mendalam mengenai: {target_topic}"}
                    ]
                )
                
                result_text = response.choices[0].message.content
                
                # Simpan ke Riwayat Session State
                st.session_state.history.append({
                    "topic": target_topic,
                    "result": result_text
                })
                
                st.success("✅ Operasi Intelijen Berhasil Diselesaikan!")
                st.markdown("### 📋 Hasil Laporan Investigasi:")
                st.markdown(result_text)
                
                # Tombol Download Laporan
                st.download_button(
                    label="📥 Unduh Laporan (Markdown)",
                    data=result_text,
                    file_name=f"CyberIntel_Report_{target_topic[:15].strip()}.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat menghubungi API: {e}")
