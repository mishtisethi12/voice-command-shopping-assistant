import os
import streamlit as st
import google.generativeai as genai

# Fetch Gemini API Key safely
API_KEY = os.getenv("GEMINI_API_KEY") or (st.secrets["GEMINI_API_KEY"] if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets else None)

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_smart_suggestions(current_list, products_catalog):
    if not API_KEY:
        return "Gemini API Key is missing. Please check your setup."

    prompt = f"""
    You are a smart grocery shopping assistant.
    Current Shopping List: {current_list}
    Available Catalog: {products_catalog}

    Provide 3 concise, helpful recommendations:
    1. Product Recommendation (frequently bought together or missing staple)
    2. Seasonal Item Suggestion
    3. Smart/Healthier Substitute (e.g., suggest almond milk if dairy milk is present)

    Format as a plain text bulleted list (max 15 words per line).
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Unable to fetch suggestions right now. ({e})"