import streamlit as st
import json
from groq import Groq
from googleapiclient.discovery import build

st.set_page_config(page_title="AI Deal Finder", layout="centered")
st.title("⚡ FAST AI DEAL FINDER")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
CX_ID = "1757119c94ec04ab2"

prod_input = st.text_input("Product Name:")

if st.button("Get Quick Deal"):
    with st.spinner("Fetching..."):
        try:
            # 1. Google Search
            service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
            res = service.cse().list(q=f"{prod_input} price india", cx=CX_ID, num=3).execute()
            context = "\n".join([item['snippet'] for item in res.get('items', [])])
            
            # 2. Fast AI Analysis (Using 8B Instant)
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Compare {prod_input} on Amazon and Flipkart. Give Price, Offers, and Winner. Context: {context}"}],
                model="llama-3.3-8b-instant" 
            )
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Error: {e}")
