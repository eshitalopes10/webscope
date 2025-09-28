# app.py
import os
import streamlit as st
import pandas as pd
from exa_py import Exa

st.set_page_config(page_title="Exa Search — Demo", layout="wide")
st.title("🔎 Exa Search — Live Demo")
st.write("Pick a domain, type a query, and get clickable results. Download as CSV.")

# --- Get API key ---
EXA_API_KEY = None
# Prefer Streamlit Secrets (on Streamlit Cloud) but fall back to environment variable locally
try:
    EXA_API_KEY = st.secrets["7b067e89-9bfe-406a-96e4-946e32036224"]
except Exception:
    EXA_API_KEY = os.environ.get("7b067e89-9bfe-406a-96e4-946e32036224")

if not EXA_API_KEY:
    st.error("Missing Exa API key. Set EXA_API_KEY in Streamlit Secrets (cloud) or as an env var locally.")
    st.stop()

exa = Exa(EXA_API_KEY)

# --- UI controls ---
col_left, col_right = st.columns([3, 1])

with col_left:
    query = st.text_input("Search query", value="", placeholder="e.g. chocolate chip cookie recipe or React star rating component")
    num_results = st.slider("Number of results", 1, 20, 5)
    domain_choice = st.selectbox(
        "Search domain",
        ["🌍 Whole Web", "🎥 YouTube", "💻 GitHub", "📰 News", "🍲 Recipes"]
    )
    search_button = st.button("🔍 Search")

with col_right:
    st.markdown("**Quick examples**")
    st.markdown("- recipes: `garlic naan recipe`")
    st.markdown("- github: `react file upload component`")
    st.markdown("- news: `AI regulation India 2025`")

domain_map = {
    "🌍 Whole Web": None,
    "🎥 YouTube": ["https://www.youtube.com"],
    "💻 GitHub": ["https://github.com"],
    "📰 News": ["https://www.bbc.com", "https://www.ndtv.com", "https://www.cnn.com"],
    "🍲 Recipes": ["https://www.allrecipes.com", "https://www.foodnetwork.com"]
}

if search_button:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        include_domains = domain_map.get(domain_choice)
        with st.spinner("Searching…"):
            try:
                response = exa.search(
                    query,
                    num_results=num_results,
                    type="keyword",
                    include_domains=include_domains
                )
            except Exception as e:
                st.error(f"Search failed: {e}")
                st.stop()

        results = []
        for r in getattr(response, "results", []):
            # Some result objects may not have all fields; use getattr safely
            results.append({
                "title": getattr(r, "title", "No title"),
                "url": getattr(r, "url", ""),
                "snippet": getattr(r, "snippet", "")
            })

        if not results:
            st.info("No results found.")
        else:
            df = pd.DataFrame(results)
            # Display clickable list
            for i, row in df.iterrows():
                st.markdown(f"**{i+1}. {row['title']}**  \n[{row['url']}]({row['url']})  \n{row['snippet']}\n---")

            # Provide CSV download
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download results as CSV", csv_bytes, file_name="exa_results.csv", mime="text/csv")
