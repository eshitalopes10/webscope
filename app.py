import os
import pandas as pd
import streamlit as st
from exa_py import Exa

# ========================
# Streamlit Page Config
# ========================
st.set_page_config(page_title="Exa Search — Demo", layout="wide")

# ========================
# API Key Setup
# ========================
try:
    EXA_API_KEY = st.secrets["EXA_API_KEY"]
except Exception:
    EXA_API_KEY = os.environ.get("EXA_API_KEY", "7b067e89-9bfe-406a-96e4-946e32036224")

if not EXA_API_KEY:
    st.error("❌ Missing Exa API key. Please set it in Streamlit Secrets or as an environment variable.")
    st.stop()

exa = Exa(EXA_API_KEY)

# ========================
# CSS Styling (UI + Hover)
# ========================
st.markdown("""
    <style>
    /* App background + font */
    body { font-family: 'Segoe UI', sans-serif; background-color:#1E1E2F; }

    /* Result Cards */
    .result-card {
        padding:15px;
        margin-bottom:15px;
        border-radius:12px;
        background-color:#2C2C3E;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0px 6px 14px rgba(108,99,255,0.6);
    }

    /* History Cards */
    .history-card {
        padding:10px;
        margin-bottom:10px;
        border-radius:8px;
        background-color:#2E2E40;
        transition: all 0.3s ease-in-out;
        cursor: pointer;
    }
    .history-card:hover {
        transform: translateX(5px);
        background-color:#3A3A55;
    }
    </style>
""", unsafe_allow_html=True)

# ========================
# Sidebar (Quick Examples + History)
# ========================
st.sidebar.title("⚡ Quick Examples")
examples = [
    "🍲 garlic naan recipe",
    "💻 react file upload component",
    "📰 AI regulation India 2025",
    "🎥 frontend tutorial"
]
for e in examples:
    st.sidebar.markdown(f"- {e}")

st.sidebar.markdown("---")
st.sidebar.title("🕘 Search History")

if "history" not in st.session_state:
    st.session_state.history = []

# Show history in sidebar
if st.session_state.history:
    for h in st.session_state.history[::-1]:  # latest first
        st.sidebar.markdown(
            f"<div class='history-card'>{h}</div>", unsafe_allow_html=True
        )
else:
    st.sidebar.info("No history yet.")

# ========================
# Header
# ========================
st.markdown("""
    <h1 style='text-align: center; color: #6C63FF; font-size:48px;'>
        🔍 Exa Search
    </h1>
    <p style='text-align: center; color: #CCCCCC; font-size:18px;'>
        Search smarter. Explore domains. Export results.<br>
        Beautiful UI • Hover Effects • Search History
    </p>
""", unsafe_allow_html=True)

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
    st.info("👉 Use the sidebar for quick examples & history")

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

        # Save to history
        st.session_state.history.append(query)

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

