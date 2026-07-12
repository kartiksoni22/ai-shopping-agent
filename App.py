import streamlit as st
import json
import pandas as pd
from groq import Groq
from googleapiclient.discovery import build

# ==========================================
# ⚙️ CONFIGURATION & API KEYS (SECURE MODE)
# ==========================================
# Keys ab Streamlit ki tijori (secrets) se aayengi
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
CX_ID = "1757119c94ec04ab2" # Ye public ID hai, isko hide karne ki zaroorat nahi

# ==========================================
# 🎨 ADVANCED UI & 3D CSS ANIMATIONS
# ==========================================
st.set_page_config(page_title="AI Deal Finder", page_icon="🛍️", layout="wide")

# Injecting Custom CSS for 3D Hover, Gradients, and Animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(45deg, #FF9900, #FF5252, #2874F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3rem;
        animation: fadeInDown 1s ease-out;
    }
    
    /* 3D Hover Effect for Cards and Images */
    .stImage > img {
        transition: transform 0.5s ease, box-shadow 0.5s ease;
        border-radius: 15px;
    }
    .stImage > img:hover {
        transform: scale(1.05) perspective(1000px) rotateY(5deg) rotateX(5deg);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #2874F0 !important;
        font-weight: 800;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🛍️ THE ULTIMATE DEAL FINDER</div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #888;'>Universal AI Comparison Engine</h4>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 🧠 UNIVERSAL AI LOGIC
# ==========================================
def get_ecommerce_data(product):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    query = f"{product} specifications price details site:amazon.in OR site:flipkart.com"
    try:
        res = service.cse().list(q=query, cx=CX_ID, num=10).execute()
        context = ""
        image_url = None
        for item in res.get('items', []):
            context += f"Source: {item.get('title', '')} - Details: {item.get('snippet', '')}\n"
            if not image_url and 'pagemap' in item and 'cse_image' in item['pagemap']:
                image_url = item['pagemap']['cse_image'][0]['src']
        return context, image_url
    except Exception as e:
        return None, None

def analyze_ecommerce_battle(product, context):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = (
        "You are an Elite E-commerce Analyst. Analyze this query and context.\n"
        f"Query: {product}\nContext: {context}\n\n"
        "INSTRUCTIONS:\n"
        "1. UNIVERSAL CATEGORY: Dynamically adjust the metrics. If it's a laptop, compare RAM/CPU. If it's a gemstone/jewelry, compare Carat/Clarity/Metal. If it's home decor, compare Material/Dimensions.\n"
        "2. MULTI-ITEM FILTERING: If the user asks to compare many items, select the TOP 2 best options from the query to keep the UI clean, and compare them on Amazon vs Flipkart.\n"
        "OUTPUT ONLY VALID JSON:\n"
        "{\n"
        '  "verdict": "Clear winner explanation.",\n'
        '  "key_specs": ["Spec 1", "Spec 2"],\n'
        '  "amazon": {"price": "₹...", "offers": "...", "rating": ".../5", "pros": ["Pro1"], "cons": ["Con1"]},\n'
        '  "flipkart": {"price": "₹...", "offers": "...", "rating": ".../5", "pros": ["Pro1"], "cons": ["Con1"]}\n'
        "}"
    )
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.2
    )
    return json.loads(chat_completion.choices[0].message.content.replace("```json", "").replace("```", "").strip(), strict=False)

# ==========================================
# 🖥️ FRONTEND INTERACTION
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    prod_input = st.text_input("🔍 Search any product, category, or comparison (e.g., Dyson Airwrap, 2 Carat Diamond Ring, S24 vs iPhone):")
    analyze_btn = st.button("✨ Run Universal Analysis", use_container_width=True)

if analyze_btn and prod_input:
    with st.spinner("🕵️ AI is analyzing categories, specs, and converting data..."):
        live_context, prod_image_url = get_ecommerce_data(prod_input)
        if live_context:
            try:
                data = analyze_ecommerce_battle(prod_input, live_context)
                
                if prod_image_url:
                    img_col1, img_col2, img_col3 = st.columns([1.5, 1, 1.5])
                    with img_col2:
                        st.image(prod_image_url, use_container_width=True)
                
                st.success(f"🏆 **AI VERDICT:** {data.get('verdict', '')}")
                
                plat_col1, plat_col2 = st.columns(2)
                with plat_col1:
                    with st.container(border=True):
                        st.subheader("📦 Amazon India")
                        st.metric(label="Estimated Price", value=data['amazon'].get('price', 'N/A'))
                        st.write(f"💳 Offers: {data['amazon'].get('offers', 'N/A')}")
                        with st.expander("Pros & Cons"):
                            st.write("**Pros:**", ", ".join(data['amazon'].get('pros', [])))
                            st.write("**Cons:**", ", ".join(data['amazon'].get('cons', [])))
                
                with plat_col2:
                    with st.container(border=True):
                        st.subheader("🛍️ Flipkart")
                        st.metric(label="Estimated Price", value=data['flipkart'].get('price', 'N/A'))
                        st.write(f"💳 Offers: {data['flipkart'].get('offers', 'N/A')}")
                        with st.expander("Pros & Cons"):
                            st.write("**Pros:**", ", ".join(data['flipkart'].get('pros', [])))
                            st.write("**Cons:**", ", ".join(data['flipkart'].get('cons', [])))
                            
            except Exception as e:
                st.error("⚠️ Formatting Error. Try a slightly different search term.")