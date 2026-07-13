import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq
import json
import re

# ==========================================
# 1. PAGE SETUP & EYE-CATCHING CSS
# ==========================================
st.set_page_config(page_title="Fast AI Deal Finder", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .main-title { font-size: 45px; font-weight: 800; background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 30px; }
    .deal-card { background-color: #1e1e24; border: 1px solid #333; border-radius: 15px; padding: 20px; margin-bottom: 20px; transition: all 0.3s ease-in-out; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .deal-card:hover { transform: translateY(-8px); box-shadow: 0 12px 24px rgba(255, 75, 43, 0.4); border-color: #FF4B2B; }
    .emi-tag { background-color: #2b9348; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; display: inline-block; margin: 10px 0; }
    .buy-link { color: #00d2ff; text-decoration: none; font-weight: bold; transition: color 0.2s; }
    .buy-link:hover { color: #FF4B2B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA FUNCTIONS
# ==========================================
def fetch_live_deals(product_name):
    query = f"{product_name} price india reviews"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            text_data = "\n\n".join([f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nLink: {r.get('href')}" for r in results])
            images = list(ddgs.images(product_name, max_results=1))
            image_url = images[0].get('image') if images else "https://via.placeholder.com/300"
            return text_data, image_url
    except: return None, None

def analyze_with_ai(product_name, search_data):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    prompt = f"""
    Analyze these search results for '{product_name}'. Return a JSON list of 3 best deals.
    Fields: "title", "price", "emi" (estimated 6-mo), "reviews", "link", "highlight".
    Return ONLY valid JSON array.
    Results: {search_data}
    """
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="mixtral-8x7b-32768", temperature=0.2)
    raw = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    return json.loads(re.search(r'\[.*\]', raw, re.DOTALL).group())

# ==========================================
# 3. UI RENDERING
# ==========================================
st.markdown('<div class="main-title">⚡ FAST AI DEAL FINDER</div>', unsafe_allow_html=True)
product_query = st.text_input("🔍 What do you want to buy?")

if st.button("🚀 Get Live Quick Deal"):
    with st.spinner("Fetching live market data..."):
        text, img = fetch_live_deals(product_query)
        if text:
            st.image(img, use_column_width=True)
            deals = analyze_with_ai(product_query, text)
            for deal in deals:
                st.markdown(f"""
                <div class="deal-card">
                    <h3>🛒 {deal.get('title')}</h3>
                    <b style='color:#FF4B2B; font-size:22px;'>{deal.get('price')}</b>
                    <div class="emi-tag">💳 EMI: {deal.get('emi')}</div>
                    <p><b>⭐ Reviews:</b> {deal.get('reviews')}</p>
                    <p><b>✨ Highlight:</b> {deal.get('highlight')}</p>
                    <a class="buy-link" href="{deal.get('link')}" target="_blank">🔗 Click here to buy ➔</a>
                </div>
                """, unsafe_allow_html=True)
        else: st.error("Error fetching data.")