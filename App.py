def fetch_live_deals(product_name):
    query = f"{product_name} price India"
    try:
        # 10 second ka timeout diya hai taaki server response ka wait kare
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            text_data = "\n\n".join([f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nLink: {r.get('href')}" for r in results])
            
            # Images ke liye bhi error handling
            try:
                images = list(ddgs.images(product_name, max_results=1))
                image_url = images[0].get('image') if images else "https://via.placeholder.com/300"
            except:
                image_url = "https://via.placeholder.com/300"
                
            return text_data, image_url
    except Exception as e:
        st.error(f"DDGS Error: {e}")
        return None, None
