import streamlit as st
from openai import OpenAI
import json
import urllib.parse
import re

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
    base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",
    api_key=api_key
)

# ---------------------------------------------------------
# 4. HELPER FUNCTION UNTUK REQUEST AI & CLEANING JSON
# ---------------------------------------------------------
def call_openrouter(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=selected_model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    raw = response.choices[0].message.content.strip()
    
    # Ekstraksi string JSON menggunakan Regex (Mencegah Syntax Error dari Markdown ```)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        clean_json = match.group(0)
    else:
        clean_json = raw

    return json.loads(clean_json)

# ---------------------------------------------------------
# 5. FORM INPUT UTAMA PRODUK
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
# 6. INTEGRASI AGEN AI BERBASIS TAB
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Copywriting & WA", 
    "🚀 Strategi Promosi", 
    "🔍 SEO Marketplace", 
    "❓ CS & FAQ", 
    "🎨 Visual Prompt"
])

# --- TAB 1: COPYWRITING & CHECKOUT WA ---
with tab1:
    if st.button("✨ Generasi Copywriting Toko", key="btn_tab1", type="primary"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner(f"Agent Copywriting bekerja menggunakan {selected_model_name}..."):
                try:
                    sys_p = "Kamu adalah ahli pemasaran e-commerce. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Fitur: {prod_features}.
                    Format JSON yang wajib digunakan:
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
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; font-weight:bold;">Pesan via WhatsApp</button></a>', unsafe_allow_html=True)

# --- TAB 2: STRATEGI PROMOSI ---
with tab2:
    if st.button("🚀 Buat Strategi Promosi Video & Broadcast", key="btn_tab2"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent Marketing merancang skrip & promo..."):
                try:
                    sys_p = "Kamu adalah pakar TikTok Marketing & WA Broadcast. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON yang wajib digunakan:
                    {{
                        "script_tiktok": "Skrip video 15 detik (Hook, Body, CTA)",
                        "broadcast_wa": "Pesan broadcast promo WA yang persuasif disertai emojinya"
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
    if st.button("🎯 Optimasi SEO Marketplace", key="btn_tab3"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent SEO mengoptimasi kata kunci..."):
                try:
                    sys_p = "Kamu adalah spesialis SEO Shopee dan Tokopedia. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON yang wajib digunakan:
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
        st.subheader("🔑 Kata Kunci Pencarian Utama")
        st.write(", ".join(res.get("keywords", [])))

# --- TAB 4: CS & FAQ GENERATOR ---
with tab4:
    if st.button("❓ Hasilkan FAQ Pertanyaan Pelanggan", key="btn_tab4"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent Customer Service menyusun FAQ..."):
                try:
                    sys_p = "Kamu adalah manajer CS e-commerce profesional. Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON yang wajib digunakan:
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
        st.subheader("💬 Jawaban Pertanyaan Sering Diajukan (FAQ)")
        for item in res.get("faq", []):
            with st.expander(f"Q: {item.get('tanya')}"):
                st.write(item.get("jawab"))

# --- TAB 5: VISUAL PROMPT GENERATOR ---
with tab5:
    if st.button("🎨 Hasilkan Prompt Gambar AI", key="btn_tab5"):
        if not prod_name:
            st.error("Nama produk wajib diisi!")
        else:
            with st.spinner("Agent Visual Designer membuat prompt foto produk..."):
                try:
                    sys_p = "Kamu adalah instruktur prompt AI Gambar (Midjourney / FLUX / DALL-E). Merespon HANYA dalam format JSON valid."
                    usr_p = f"""
                    Produk: {prod_name}, Kategori: {prod_category}, Keunggulan: {prod_features}.
                    Format JSON yang wajib digunakan:
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
        st.subheader("🖼️ English Prompt (Midjourney / FLUX / DALL-E)")
        st.code(res.get("prompt_en", ""), language="text")
        st.caption(res.get("instruksi", ""))
