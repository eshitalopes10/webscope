import os
import pandas as pd
import streamlit as st
from exa_py import Exa
from urllib.parse import urlparse

# ========================
# Page Config
# ========================
st.set_page_config(page_title="WebScope — AI Search Engine", layout="wide")

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
# CSS + JS Styling
# ========================
st.markdown("""
<style>
body {background-color:#0E0E0E; color:#FFF; font-family:'Segoe UI', sans-serif; scroll-behavior: smooth;}

/* Hero Section */
.hero {
    height: 80vh; display:flex; flex-direction:column; justify-content:center; align-items:center;
    text-align:center; background: linear-gradient(180deg, #2C1C54 0%, #0E0E0E 100%);
    margin-bottom:50px; border-radius:12px;
}
.hero h1 {font-size:90px; color:#FF6EC7; margin:0; font-weight:bold;}
.hero p {font-size:26px; color:#F0F0F0; margin-top:20px; max-width:700px;}
.hero button {
    margin-top:30px; padding:18px 45px; font-size:22px; border:none; border-radius:12px;
    background-color:#FF6EC7; color:#FFF; cursor:pointer; transition: all 0.3s ease-in-out;
}
.hero button:hover {background-color:#D94FB3; transform:translateY(-3px);}

/* Search Section */
#search-section {background: linear-gradient(180deg, #3C1C70 0%, #1C0E2E 100%); padding:40px; border-radius:12px;}

/* Search Cards */
.result-card {
    padding:20px; margin-bottom:20px; border-radius:15px; background-color:#4B1C7F;
    box-shadow:0px 4px 12px rgba(0,0,0,0.5); display:flex; gap:15px; opacity:0; transform: translateY(20px);
    animation: fadeInUp 0.6s forwards;
}
.result-card:hover {transform: translateY(-5px); box-shadow:0px 8px 20px rgba(255,110,199,0.6);}
.result-card img {width:50px; height:50px; border-radius:8px;}
.result-content {flex:1;}
.result-content h4 {margin:0; color:#FF6EC7; font-size:20px;}
.result-content a {color:#FFA3E0; font-size:14px; text-decoration:none;}
.result-content a:hover {text-decoration:underline;}
.result-content p {color:#F0F0F0; font-size:15px; margin-top:5px; margin-bottom:5px;}
.result-content small {color:#DDD; font-size:12px;}

/* Fade-in animation */
@keyframes fadeInUp { to {opacity:1; transform:translateY(0);} }

/* Sidebar / Most Searched */
.most-searched h3 {color:#FF6EC7; margin-bottom:10px;}
.search-tag {
    display:inline-block; background-color:#D94FB3; color:#FFF; padding:8px 15px; margin:5px;
    border-radius:10px; cursor:pointer; transition: all 0.3s ease-in-out;
}
.search-tag:hover {background-color:#FF6EC7; transform:translateY(-2px);}
.css-1d391kg {background-color:#2C1C3F !important;}

/* CSV button */
.stDownloadButton button {background-color:#FF6EC7; color:white; font-weight:bold; border-radius:8px;}
.stDownloadButton button:hover {background-color:#D94FB3;}
</style>

<script>
// Scroll to search section
function scrollToSearch() {
    const el = document.getElementById('search-section');
    if(el) el.scrollIntoView({behavior:'smooth'});
}

// Animate search cards
function animateCards() {
    const cards = document.querySelectorAll('.result-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = (index * 0.1) + 's';
    });
}
window.onload = animateCards;
</script>
""", unsafe_allow_html=True)

# ========================
# Front Page Hero
# ========================
st.markdown("""
<div class="hero">
    <h1>WebScope</h1>
    <p>🔍 Explore the Web Instantly • Beautiful Dark UI • Fast Results • CSV Export</p>
    <a href="#search-section"><button>Start Searching ⬇️</button></a>
</div>
""", unsafe_allow_html=True)

# ========================
# Search Section Anchor
# ========================
st.markdown('<div id="search-section"></div>', unsafe_allow_html=True)

# ========================
# Sidebar: Most Searched
# ========================
st.sidebar.markdown('<div class="most-searched"><h3>🔥 Most Searched</h3></div>', unsafe_allow_html=True)
most_searched = ["garlic naan recipe", "React file upload", "AI regulation India 2025", "frontend tutorial", "chocolate chip cookies"]

for query_tag in most_searched:
    st.sidebar.markdown(f'<div class="search-tag" onclick="window.location.hash=\'search-section\';">{query_tag}</div>', unsafe_allow_html=True)

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
    st.info("Click a 'Most Searched' tag to scroll and search!")

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
# Helper: Extract domain name
# ========================
def get_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.","") if parsed.netloc else "unknown"
    except:
        return "unknown"

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
                "snippet": getattr(r, "snippet", ""),
                "domain": get_domain(getattr(r, "url", ""))
            })

        if not results:
            st.info("ℹ️ No results found.")
        else:
            df = pd.DataFrame(results)
            st.subheader("✨ Search Results")

            for i, row in df.iterrows():
                favicon_url = f"https://www.google.com/s2/favicons?domain={row['domain']}" if row['domain'] != "unknown" else ""
                st.markdown(f"""
                <div class="result-card">
                    <img src="{favicon_url}" alt="favicon">
                    <div class="result-content">
                        <h4>{i+1}. {row['title']}</h4>
                        <a href="{row['url']}" target="_blank">Open Link</a>
                        <p>{row['snippet']}</p>
                        <small>Source: {row['domain']}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download results as CSV",
                csv_bytes,
                file_name="exa_results.csv",
                mime="text/csv"
            )
