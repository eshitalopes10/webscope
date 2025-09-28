import os
import pandas as pd
import streamlit as st
from exa_py import Exa

# ========================
# Page Config
# ========================
st.set_page_config(page_title="WebScope — Exa Search Demo", layout="wide")

# ========================
# API Key Setup
# ========================
try:
    EXA_API_KEY = st.secrets["EXA_API_KEY"]
except Exception:
    EXA_API_KEY = os.environ.get("EXA_API_KEY", "7b067e89-9bfe-406a-96e4-946e32036224")

if not EXA_API_KEY:
    st.error("Missing Exa API key. Please set it in Streamlit Secrets or as an environment variable.")
    st.stop()

exa = Exa(EXA_API_KEY)

# ========================
# CSS Styling
# ========================
st.markdown("""
    <style>
    /* General Page */
    body {
        background-color: #0E0E0E;
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Hero Section */
    .hero {
        height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: linear-gradient(180deg, #1B1B1B 0%, #0E0E0E 100%);
        margin-bottom: 50px;
    }
    .hero h1 {
        font-size: 80px;
        color: #6C63FF;
        margin: 0;
    }
    .hero p {
        font-size: 24px;
        color: #CCCCCC;
        margin-top: 20px;
    }
    .hero button {
        margin-top: 30px;
        padding: 15px 40px;
        font-size: 20px;
        border: none;
        border-radius: 10px;
        background-color: #6C63FF;
        color: #FFF;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
    }
    .hero button:hover {
        background-color: #4E49C5;
        transform: translateY(-3px);
    }

    /* Search Cards */
    .result-card {
        padding:20px;
        margin-bottom:20px;
        border-radius:15px;
        background-color:#1C1C2E;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
        transition: all 0.3s ease-in-out;
    }
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 20px rgba(108,99,255,0.6);
    }

    /* Links */
    a {
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }

    /* Sidebar */
    .css-1d391kg {background-color:#1C1C2E !important;} /* Override sidebar color */
    </style>

    <!-- Smooth Scroll Script -->
    <script>
    function scrollToSearch() {
        document.getElementById('search-section').scrollIntoView({behavior: 'smooth'});
    }
    </script>
""", unsafe_allow_html=True)

# ========================
# Hero Front Page
# ========================
st.markdown("""
<div class="hero">
    <h1>WebScope</h1>
    <p>🔍 Explore the Web Instantly • Beautiful Dark UI • Fast Results • CSV Export</p>
    <button onclick="scrollToSearch()">Start Searching ⬇️</button>
</div>
""", unsafe_allow_html=True)

# ========================
# Sidebar (Quick Examples)
# ========================
st.sidebar.title("⚡ Quick Examples")
st.sidebar.markdown("- 🍲 `garlic naan recipe`")
st.sidebar.markdown("- 💻 `react file upload component`")
st.sidebar.markdown("- 📰 `AI regulation India 2025`")
st.sidebar.markdown("- 🎥 `frontend tutorial`")

# ========================
# Search Section Anchor
# ========================
st.markdown('<div id="search-section"></div>', unsafe_allow_html=True)

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

            # Stylish Results in Card Layout with Hover Effect
            st.subheader("✨ Search Results")
            for i, row in df.iterrows():
                st.markdown(f"""
                <div class="result-card">
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
