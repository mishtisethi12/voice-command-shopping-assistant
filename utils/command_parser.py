import json
import google.generativeai as genai
import streamlit as st

# Configure Gemini API
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def parse_voice_command(user_text: str):
    """
    Parses natural language commands (English, Hindi, Hinglish) into structured JSON.
    Supports single-item commands and multi-item recipe expansions using Gemini API.
    """
    if not api_key:
        return {"action": "UNKNOWN", "items": []}

    model = genai.GenerativeModel("gemini-3.6-flash")

    prompt = f"""
    You are an AI grocery assistant parser. Analyze the user command in English, Hindi, or Hinglish:
    "{user_text}"

    Tasks:
    1. Identify intent:
       - ADD: Adding single items OR recipe/dish ingredients (e.g. "Chai banane ka samaan", "Paneer Tikka ingredients").
       - REMOVE: Deleting item(s) from cart.
       - SEARCH: Searching catalog or prices.
    2. Extract item details:
       - If it is a recipe (like "chai", "coffee", "pasta", "butter chicken"), automatically list all fundamental individual grocery items required for it.
       - Translate Hindi/Hinglish item names into clean, standard English product names (e.g., "Chai Patty" -> "Tea Powder", "Doodh" -> "Milk", "Chini" -> "Sugar").

    Return strictly a JSON object with this structure:
    {{
        "action": "ADD",
        "items": [
            {{
                "item_name": "Tea Powder",
                "quantity": 1,
                "category": "Beverages",
                "max_price": null,
                "brand": null
            }},
            {{
                "item_name": "Milk",
                "quantity": 1,
                "category": "Dairy",
                "max_price": null,
                "brand": null
            }},
            {{
                "item_name": "Sugar",
                "quantity": 1,
                "category": "General",
                "max_price": null,
                "brand": null
            }}
        ]
    }}
    """

    try:
        # Enforce strict JSON output mode
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        parsed_data = json.loads(response.text.strip())
        return parsed_data
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return {"action": "UNKNOWN", "items": []}