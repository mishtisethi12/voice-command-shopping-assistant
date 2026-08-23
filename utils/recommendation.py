import google.generativeai as genai
import streamlit as st

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_smart_suggestions(current_list, products_catalog, past_history):
    """
    Generates smart, seasonal, and substitute recommendations based on cart state.
    """
    if not api_key:
        return "⚠️ Please set GEMINI_API_KEY in secrets.toml"

    model = genai.GenerativeModel("gemini-3.6-flash")

    prompt = f"""
    You are an intelligent grocery shopping assistant.
    Current Shopping Cart: {current_list}
    Product Catalog: {products_catalog}
    User Past Purchase History: {past_history}

    Provide concise recommendations formatted nicely in Markdown:
    1. 🔄 **Running Low / Routine Items**: Suggest 2 items based on history or missing complementary items (e.g., if coffee is in cart, suggest sugar).
    2. 🌿 **Seasonal / On Sale**: Suggest 2 seasonal or trending budget items.
    3. 🔁 **Smart Substitutes**: If an item in the cart is dairy or generic, suggest 1 healthier or alternative option (e.g., Almond Milk for Milk).

    Keep the total response under 100 words and use clear bullet points.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating suggestions: {e}"