import streamlit as st
from openai import OpenAI
import json
import urllib.parse
import re

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CUSTOM CSS FUTURISTIK
# ---------------------------------------------------------
st.set_page_config(
    page_title="SaaS AI Toko Online - CyberSuite",
    page_icon="⚡",
    layout="wide"
)

# Injeksi CSS Futuristik (Dark Mode, Glassmorphism, Glow Effects)
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Card Glassmorphism Effect */
    div[data-testid="stExpander"], div.stButton > button {
        border-radius: 12px;
    }
    
    /* Custom Header Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }

    /* Glowing Primary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
        transition: all 0.3s ease-in-out;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.8);
        transform: translateY(-2px);
    }

    /* Tab Styling */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }
    
    button[aria-selected="true"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
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
# 6. INTEGRASI AGEN AI BERBASIS TAB (DENGAN TAB RISET DITAMBAHKAN)
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
                    Format JSON:
                    {{
                        "deskripsi": "Deskripsi persuasif 2 paragraf",
                        "keunggulan": ["poin 1", "poin 2", "poin 3"],
                        "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
                    }}
                    """
                    st.session_state["res_copy"] = call_openrouter(sys_p, usr_p)
                    st.success("Berhasil!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "res_copy" in st.session_state:
        res = st.session_state["res_copy"]
        st.subheader("📝 Deskripsi Penjualan")
        st.write(res.get("deskripsi", ""))
        st.subheader("💡 Keunggulan Utama")
        for p in res.get("keunggulan", []):
            st.write(f"• {p}")
        st.subheader("🏷️ Rekomendasi Hashtag")
        st.write(" ".join(res.get("hashtags", [])))
        st.divider()
        
        wa_message = f"Halo {store_name}, saya mau pesan:\n\n*Nama Produk:* {prod_name}\n*Harga:* Rp {prod_price:,}\n\nApakah stok masih tersedia?"
        wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_message)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background: linear-gradient(90deg, #10b981, #059669); color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);">🚀 Checkout via WhatsApp</button></a>', unsafe_allow_html=True)

# --- TAB 2: MARKETING STRATEGY ---
with tab2:
    if st.button("🚀 Execute Marketing Agent", key="btn_tab2", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent merancang video script & broadcast..."):
                try:
                    sys_p = "Kamu adalah pakar TikTok Marketing & WA Broadcast. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON:
                    {{
                        "script_tiktok": "Skrip video 15 detik (Hook, Body, CTA)",
                        "broadcast_wa": "Pesan broadcast promo WA persuasif beserta emoji"
                    }}
                    """
                    st.session_state["res_promo"] = call_openrouter(sys_p, usr_p)
                    st.success("Berhasil!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "res_promo" in st.session_state:
        res = st.session_state["res_promo"]
        st.subheader("🎬 Skrip Video Singkat (TikTok / Reels)")
        st.info(res.get("script_tiktok", ""))
        st.subheader("📲 Draf Broadcast WhatsApp Promo")
        st.code(res.get("broadcast_wa", ""), language="text")

# --- TAB 3: SEO MARKETPLACE ---
with tab3:
    if st.button("🎯 Execute SEO Agent", key="btn_tab3", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent melakukan keyword research..."):
                try:
                    sys_p = "Kamu adalah spesialis SEO Shopee dan Tokopedia. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON:
                    {{
                        "judul_seo": "Judul Produk Yang Ramah Algoritma Marketplace (Maks 100 Karakter)",
                        "keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"]
                    }}
                    """
                    st.session_state["res_seo"] = call_openrouter(sys_p, usr_p)
                    st.success("Berhasil!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "res_seo" in st.session_state:
        res = st.session_state["res_seo"]
        st.subheader("📌 Judul Optimal Shopee/Tokopedia")
        st.code(res.get("judul_seo", ""), language="text")
        st.subheader("🔑 Kata Kunci Utama")
        st.write(", ".join(res.get("keywords", [])))

# --- TAB 4: RISET & REKOMENDASI PRODUK (BARU) ---
with tab4:
    if st.button("📊 Execute Product Research Agent", key="btn_tab4", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent melakukan analisis riset pasar & potensi produk..."):
                try:
                    sys_p = "Kamu adalah Konsultan Riset Pasar & Product Strategist E-Commerce senior. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Harga: Rp {prod_price}, Keunggulan: {prod_features}.
                    Lakukan analisis mendalam dan berikan respon JSON dengan struktur:
                    {{
                        "target_audience": "Profil pembeli ideal (demografi, kebiasaan, pain points)",
                        "usp": "Unique Selling Proposition utama yang membedakan dari pesaing",
                        "market_potential": "Analisis potensi pasar dan posisi harga (apakah murah, mid-tier, atau premium)",
                        "competitor_analysis": "Tantangan persaingan pasar saat ini",
                        "product_recommendations": ["Rekomendasi ide varian/bundling 1", "Rekomendasi ide varian/bundling 2", "Rekomendasi ide varian/bundling 3"]
                    }}
                    """
                    st.session_state["res_research"] = call_openrouter(sys_p, usr_p)
                    st.success("Riset Berhasil!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "res_research" in st.session_state:
        res = st.session_state["res_research"]
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.subheader("🎯 Target Pembeli Ideal")
            st.info(res.get("target_audience", ""))
            
            st.subheader("💡 Unique Selling Proposition (USP)")
            st.success(res.get("usp", ""))

        with col_res2:
            st.subheader("📈 Analisis Potensi Pasar & Harga")
            st.write(res.get("market_potential", ""))
            
            st.subheader("⚔️ Analisis Persaingan Pasar")
            st.warning(res.get("competitor_analysis", ""))

        st.divider()
        st.subheader("🎁 Rekomendasi Pengembangan / Bundling Produk")
        for rec in res.get("product_recommendations", []):
            st.write(f"✨ {rec}")

# --- TAB 5: CS & FAQ ---
with tab5:
    if st.button("❓ Execute CS Agent", key="btn_tab5", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent menyusun FAQ..."):
                try:
                    sys_p = "Kamu adalah manajer CS e-commerce profesional. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON:
                    {{
                        "faq": [
                            {{"tanya": "Pertanyaan 1", "jawab": "Jawaban 1"}},
                            {{"tanya": "Pertanyaan 2", "jawab": "Jawaban 2"}},
                            {{"tanya": "Pertanyaan 3", "jawab": "Jawaban 3"}}
                        ]
                    }}
                    """
                    st.session_state["res_faq"] = call_openrouter(sys_p, usr_p)
                    st.success("Berhasil!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "res_faq" in st.session_state:
        res = st.session_state["res_faq"]
        st.subheader("💬 Auto FAQ Generator")
        for item in res.get("faq", []):
            with st.expander(f"Q: {item.get('tanya')}"):
                st.write(item.get("jawab"))

# --- TAB 6: VISUAL PROMPT ---
with tab6:
    if st.button("🎨 Execute Visual Agent", key="btn_tab6", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent merancang prompt foto studio..."):
                try:
                    sys_p = "Kamu adalah instruktur prompt AI Gambar (Midjourney / FLUX / DALL-E). Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON:
                    {{
                        "prompt_en": "Professional product studio photoshoot prompt in English, 8k resolution, photorealistic",
                        "instruksi": "Instruksi cara memakai prompt ini di AI Generator"
                    }}
                    """
                    st.session_state["res_visual"] = call_openrouter(sys_p, usr_p)
                    st.success("Berhasil!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "res_visual" in st.session_state:
        res = st.session_state["res_visual"]
        st.subheader("🖼️ English Studio Prompt")
        st.code(res.get("prompt_en", ""), language="text")
        st.caption(res.get("instruksi", ""))
