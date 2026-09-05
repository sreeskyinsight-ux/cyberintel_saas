import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"
# Mencegah error Pydantic v1 fallback di Python baru
import pydantic.v1

import streamlit as st
from openai import OpenAI
import datetime
import urllib.parse
import time

# --- IMPORT CREWAI ---
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Konfigurasi Halaman (Tema Gelap Premium)
st.set_page_config(
    page_title="CyberIntel Enterprise - Multi-Agent Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# Kustomisasi CSS Tingkat Lanjut (Ultimate SaaS Dark Theme v2.0)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .stApp {
        background: #030712 !important;
        color: #f3f4f6 !important;
    }

    [data-testid="stSidebar"] {
        background: #0b0f19 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.1) !important;
        padding-top: 1.5rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(56, 189, 248, 0.15) !important;
    }

    h1, h2, h3 {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
    }
    
    h1 {
        font-size: 2.4rem !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem !important;
    }

    .stForm {
        background: rgba(15, 23, 42, 0.75) !important;
        padding: 32px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 30px rgba(56, 189, 248, 0.05) !important;
        backdrop-filter: blur(16px) !important;
    }

    .stTextInput label, .stSelectbox label {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin-bottom: 6px !important;
    }

    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #030712 !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25) !important;
    }

    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
        box-shadow: 0 10px 25px rgba(56, 189, 248, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    .report-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 32px;
        border-radius: 16px;
        margin-top: 2rem;
        box-shadow: 0 15px 30px -10px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# --- 0. FUNGSI & KONFIGURASI UTAMA ---
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None

if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin@cyberintel.id": {"password": "adminpassword123", "role": "Administrator"},
        "agent@cyberintel.id": {"password": "password123", "role": "Agent"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_role = ""

if "history" not in st.session_state:
    st.session_state.history = []

def get_llm(model_name="nousresearch/hermes-3-llama-3.1-70b"):
    if not api_key:
        st.error("OpenRouter API Key belum diset di secrets.")
        st.stop()
    return ChatOpenAI(
        model_name=model_name,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
    )

# --- A. FUNGSI PEMBUAT GAMBAR MANDIRI ---
def run_visual_generator(prompt_text):
    encoded_prompt = urllib.parse.quote(prompt_text)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=123"
    return image_url

# --- B. FUNGSI SISTEM MULTI-AGENT CREWAI ---
def run_agentic_research(topic):
    llm_fast = get_llm("nousresearch/hermes-3-llama-3.1-70b")
    llm_writer = get_llm("anthropic/claude-3.5-sonnet")

    agent_researcher = Agent(
        role='Senior Data Analyst & Researcher',
        goal='Mengumpulkan data mendalam, tren terkini, dan fakta kunci terkait topik: {topic}',
        backstory="Analis data jenius dengan kemampuan riset mendalam.",
        verbose=True,
        allow_delegation=False,
        llm=llm_fast
    )

    agent_reporter = Agent(
        role='Senior Intelligence Reporter',
        goal='Menyusun data dari Researcher menjadi laporan intelijen formal dan terstruktur rapi berformat Markdown.',
        backstory="Mantan jurnalis investigasi spesialis penyusun laporan strategis.",
        verbose=True,
        allow_delegation=False,
        llm=llm_writer
    )

    agent_artist = Agent(
        role='Creative Visual Strategist',
        goal='Membuat prompt deskriptif bahasa Inggris yang detail untuk merender gambar ilustrasi konseptual.',
        backstory="Direktur seni visioner penerjemah data ke konsep visual.",
        verbose=True,
        allow_delegation=False,
        llm=llm_fast
    )

    task_gather = Task(
        description=f'Lakukan riset mendalam tentang "{topic}". Kumpulkan poin-poin data utama.',
        expected_output='Ringkasan poin-poin data terstruktur.',
        agent=agent_researcher
    )

    task_report = Task(
        description=f'Susun laporan intelijen formal minimal 300 kata tentang "{topic}".',
        expected_output='Laporan intelijen lengkap dalam format Markdown.',
        agent=agent_reporter,
        context=[task_gather]
    )

    task_visual = Task(
        description=f'Buat prompt teks deskriptif untuk ilustrasi visual berdasarkan laporan tentang "{topic}".',
        expected_output='Satu kalimat prompt deskriptif.',
        agent=agent_artist,
        context=[task_report]
    )

    crew = Crew(
        agents=[agent_researcher, agent_reporter, agent_artist],
        tasks=[task_gather, task_report, task_visual],
        process=Process.sequential,
        verbose=True,
        manager_llm=llm_fast
    )

    with st.spinner(f"🤖 Tim Multi-Agent CrewAI sedang bekerja secara otonom pada topik: {topic}..."):
        try:
            crew.kickoff()
            final_report = task_report.output.raw
            visual_prompt = task_visual.output.raw
            return final_report, visual_prompt
        except Exception as e:
            st.error(f"Terjadi kesalahan CrewAI: {e}")
            return None, None

# --- HALAMAN LOGIN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🛡️</div>
                <h1 style='font-size: 2.2rem !important;'>CyberIntel Enterprise</h1>
                <p style='color: #94a3b8; font-size: 0.95rem;'>Agentic AI Command & Visual Center</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.info("⚡ **Akses Cepat Demo (Instan):**")
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            if st.button("🔑 Login Admin"):
                st.session_state.logged_in = True
                st.session_state.current_user = "admin@cyberintel.id"
                st.session_state.current_role = "Administrator"
                st.rerun()
        with dcol2:
            if st.button("🔑 Login Agent"):
                st.session_state.logged_in = True
                st.session_state.current_user = "agent@cyberintel.id"
                st.session_state.current_role = "Agent"
                st.rerun()
                
        st.markdown("<p style='text-align:center; color:#64748b; font-size:0.85rem; margin: 20px 0 10px 0;'>Atau gunakan email pribadi:</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username_input = st.text_input("Alamat Email", placeholder="contoh: sree@cyberintel.id")
            password_input = st.text_input("Password", type="password", placeholder="Masukkan password")
            login_btn = st.form_submit_button("Masuk Sistem")
            
            if login_btn:
                if username_input.strip() != "":
                    if username_input not in st.session_state.users_db:
                        st.session_state.users_db[username_input] = {"password": "123", "role": "Agent"}
                    st.session_state.logged_in = True
                    st.session_state.current_user = username_input
                    st.session_state.current_role = st.session_state.users_db[username_input]["role"]
                    st.rerun()
                else:
                    st.error("Email tidak boleh kosong!")
        st.stop()

# --- HALAMAN UTAMA DASHBOARD SAAS ---
with st.sidebar:
    st.markdown("### 🛡️ CyberIntel Agency")
    st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.6); padding: 14px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2); margin: 15px 0;'>
            <p style='margin: 0; font-size: 0.7rem; color: #94a3b8; font-weight: 700;'>AGEN TEROTORISASI:</p>
            <p style='margin: 6px 0 0 0; font-size: 0.85rem; font-weight: 600; color: #38bdf8; word-break: break-all;'>{st.session_state.current_user}</p>
            <div style='margin-top: 8px;'>
                <span style='background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.65rem; font-weight: 700;'>{st.session_state.current_role}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Keluar Sistem"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()
    st.markdown("### 📂 Arsip Investigasi")
    if len(st.session_state.history) == 0:
        st.caption("Belum ada arsip tersimpan.")
    else:
        for i, item in enumerate(st.session_state.history):
            item_type = item.get('type', 'text')
            icon = "🤖" if item_type == "agentic" else ("🎨" if item_type == "image" else "📁")
            if st.button(f"{icon} {item['target'][:18]}...", key=f"hist_{i}"):
                st.session_state.active_result = item['result']
                st.session_state.active_target = item['target']
                st.session_state.active_type = item_type
                if item_type == "agentic":
                    st.session_state.active_image = item.get('image', None)

st.markdown("<h1>🕵️‍♂️ CyberIntel SaaS: Multi-Agent Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 30px;'>Platform Enterprise Intelligence otonom berbasis kolaborasi multi-agen AI (CrewAI & Hermes).</p>", unsafe_allow_html=True)

with st.form("scraper_form"):
    target_query = st.text_input(
        "Target Investigasi / Topik Utama:",
        placeholder="Contoh: Analisis Tren Keamanan Siber Global 2026"
    )
    
    task_type = st.selectbox(
        "Protokol Operasi:",
        [
            "🤖 CrewAI Multi-Agent Autonomous Mission (Riset + Laporan + Visual)",
            "🎨 Pembuat Gambar AI Mandiri (Visual Generator)",
            "📁 Rangkuman Intelijen Standar (Single LLM)"
        ]
    )
    
    submitted = st.form_submit_button("🚀 Jalankan Operasi")

if submitted:
    if not api_key:
        st.warning("⚠️ Kesalahan Sistem: OpenRouter API Key belum dikonfigurasi.")
    elif not target_query:
        st.warning("⚠️ Mohon masukkan target investigasi terlebih dahulu.")
    else:
        if "CrewAI Multi-Agent" in task_type:
            report, v_prompt = run_agentic_research(target_query)
            if report:
                img_url = run_visual_generator(v_prompt)
                
                st.session_state.history.insert(0, {
                    "target": target_query,
                    "result": report,
                    "image": img_url,
                    "type": "agentic",
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                st.session_state.active_result = report
                st.session_state.active_target = target_query
                st.session_state.active_type = "agentic"
                st.session_state.active_image = img_url
                
        elif "Pembuat Gambar AI" in task_type:
            img_url = run_visual_generator(target_query)
            if img_url:
                st.session_state.history.insert(0, {
                    "target": target_query,
                    "result": img_url,
                    "type": "image",
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.session_state.active_result = img_url
                st.session_state.active_target = target_query
                st.session_state.active_type = "image"
        else:
            with st.spinner("🛡️ Menjalankan intelijen standar..."):
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                response = client.chat.completions.create(
                    model="nousresearch/hermes-3-llama-3.1-70b",
                    messages=[
                        {"role": "system", "content": "Kamu adalah agen intelijen data profesional."},
                        {"role": "user", "content": f"Buatkan laporan intelijen mendalam tentang: {target_query}"}
                    ]
                )
                hasil_ai = response.choices[0].message.content
                st.session_state.history.insert(0, {
                    "target": target_query,
                    "result": hasil_ai,
                    "type": "text",
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.session_state.active_result = hasil_ai
                st.session_state.active_target = target_query
                st.session_state.active_type = "text"

if "active_result" in st.session_state:
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    curr_type = st.session_state.get("active_type", "text")
    
    if curr_type == "agentic":
        st.markdown(f"### 🤖 Berkas Misi Multi-Agent: *{st.session_state.get('active_target', '')}*")
        st.divider()
        if st.session_state.get("active_image"):
            st.image(st.session_state.active_image, caption="Ilustrasi Visual Konseptual oleh Agen Artistik", use_container_width=True)
            st.divider()
        st.markdown(st.session_state.active_result)
        
    elif curr_type == "image":
        st.markdown(f"### 🎨 Hasil Render Visual: *{st.session_state.get('active_target', '')}*")
        st.divider()
        st.image(st.session_state.active_result, caption=st.session_state.get('active_target', ''), use_container_width=True)
        
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### 🗂️ Berkas Laporan: *{st.session_state.get('active_target', '')}*")
        with col2:
            st.download_button(
                label="📥 Unduh Laporan (.md)",
                data=st.session_state.active_result,
                file_name=f"laporan_cyberintel_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        st.divider()
        st.markdown(st.session_state.active_result)
        
    st.markdown('</div>', unsafe_allow_html=True)
