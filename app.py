import os
import requests
import pandas as pd
import streamlit as st
from exa_py import Exa
from streamlit_lottie import st_lottie

# ========================
# Streamlit Page Config
# ========================
st.set_page_config(page_title="Exa Search — Demo", layout="wide")

# ========================
# Load Animation
# ========================
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_search = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_totrpclr.json")

# ========================
# API Key Setup
# ========================
try:
    EXA_API_KEY = st.secrets["7b067e89-9bfe-406a-96e4-946e32036224"]
except Exception:
    # fallback: environment variable or hardcoded for local testing
    EXA_API_KEY = os.environ.get("EXA_API_KEY", "7b067e89-9bfe-406a-96e4-946e32036224")

if not EXA_API_KEY:
    st.error("Missing Exa API key. Please set it in Streamlit Secrets or as an environment variable.")
    st.stop()

exa = Exa(EXA_API_KEY)

# ========================
# Sidebar (Quick Examples)
# ========================
st.sidebar.title("⚡ Quick Examples")
st.sidebar.markdown("- 🍲 `garlic naan recipe`")
st.sidebar.markdown("- 💻 `react file upload component`")
st.sidebar.markdown("- 📰 `AI regulation India 2025`")
st.sidebar.markdown("- 🎥 `frontend tutorial`")

# ========================
# Header with Styling
# ========================
st.markdown("""
    <h1 style='text-align: center; color: #6C63FF; font-size:48px;'>
        🔍 Exa Search
    </h1>
    <p style='text-align: center; color: #CCCCCC; font-size:18px;'>
        Pick a domain, type a query, and get instant results. <br>
        Beautiful UI • Fast Results • CSV Export
    </p>
""", unsafe_allow_html=True)

# ========================
# Animation
# ========================
if lottie_search:
    st_lottie(lottie_search, height=180, key="search")

# ========================
# UI Controls
# ========================
col_left, col_right = st.columns([3, 1])

with col_left:
    query = st.text_input(
        "Search query",
        value="",
        placeholder="e.g. chocolate chip cookie recipe or React star rating component"
    )
    num_results = st.slider("Number of results", 1, 20, 5)
    domain_choice = st.selectbox(
        "Search domain",
        ["🌍 Whole Web", "🎥 YouTube", "💻 GitHub", "📰 News", "🍲 Recipes"]
    )
    search_button = st.button("🔍 Search")

with col_right:
    st.info("Use the sidebar 👉 for quick example searches!")

# ========================
# Domain Mapping
# ========================
domain_map = {
    "🌍 Whole Web": None,
    "🎥 YouTube": ["https://www.youtube.com"],
    "💻 GitHub": ["https://github.com"],
    "📰 News": ["https://www.bbc.com", "https://www.ndtv.com", "https://www.cnn.com"],
    "🍲 Recipes": ["https://www.allrecipes.com", "https://www.foodnetwork.com"]
}

# ========================
# Search Logic
# ========================
if search_button:
    if not query.strip():
        st.warning("⚠️ Please enter a search query.")
    else:
        include_domains = domain_map.get(domain_choice)
        with st.spinner("🔎 Searching…"):
            try:
                response = exa.search(
                    query,
                    num_results=num_results,
                    type="keyword",
                    include_domains=include_domains
                )
            except Exception as e:
                st.error(f"❌ Search failed: {e}")
                st.stop()

        results = []
        for r in getattr(response, "results", []):
            results.append({
                "title": getattr(r, "title", "No title"),
                "url": getattr(r, "url", ""),
                "snippet": getattr(r, "snippet", "")
            })

        if not results:
            st.info("ℹ️ No results found.")
        else:
            df = pd.DataFrame(results)

            # Stylish Results in Card Layout
            st.subheader("✨ Search Results")
            for i, row in df.iterrows():
                st.markdown(f"""
                <div style="padding:15px; margin-bottom:15px; border-radius:12px;
                            background-color:#2C2C3E; box-shadow: 0px 4px 8px rgba(0,0,0,0.3);">
                    <h4 style="margin:0; color:#6C63FF;">{i+1}. {row['title']}</h4>
                    <a href="{row['url']}" target="_blank" style="color:#4DA6FF; font-size:14px;">
                        {row['url']}
                    </a>
                    <p style="color:#CCCCCC; font-size:15px;">{row['snippet']}</p>
                </div>
                """, unsafe_allow_html=True)

            # CSV Download
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download results as CSV",
                csv_bytes,
                file_name="exa_results.csv",
                mime="text/csv"
            )


