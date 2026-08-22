import json
import os
import re
import streamlit as st
import google.generativeai as genai

# Safe key retrieval
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]

if API_KEY:
    genai.configure(api_key=API_KEY)
def parse_voice_command(user_text):
    prompt = f"""
    You are an AI parsing voice commands for a grocery app: "{user_text}"

    Instructions:
    - action: "ADD", "REMOVE", "SEARCH", or "UNKNOWN"
    - item_name: Clean item name in lowercase singular/plural form (e.g., "pineapple", "bananas", "milk"). Remove action verbs ("add", "buy") and numbers.
    - quantity: Convert spoken numbers or digits to an INTEGER (e.g. "3", "three" -> 3). Default to 1 if no quantity is specified.
    - category: "Produce", "Dairy", "Bakery", "Hygiene", or "General".
    - max_price: Numerical float limit if specified (e.g. 5.0). Otherwise null.
    """

    # Define schema directly
    schema = {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "enum": ["ADD", "REMOVE", "SEARCH", "UNKNOWN"]},
            "item_name": {"type": "STRING"},
            "quantity": {"type": "INTEGER"},
            "category": {"type": "STRING"},
            "max_price": {"type": "NUMBER", "nullable": True}
        },
        "required": ["action", "item_name", "quantity", "category"]
    }

    try:
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema
            }
        )
        response = model.generate_content(prompt)
        return json.loads(response.text)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        text_lower = user_text.lower().strip()

        # Regex fallback for quantities
        qty_match = re.search(r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b', text_lower)
        num_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        
        qty = 1
        if qty_match:
            val = qty_match.group(1)
            qty = int(val) if val.isdigit() else num_map.get(val, 1)

        # Strip standard stopwords
        clean_item = text_lower
        for word in ["add", "buy", "remove", "delete", "find", "search", str(qty), "one", "two", "three", "four", "five"]:
            clean_item = re.sub(rf'\b{word}\b', '', clean_item)
        
        clean_item = clean_item.strip()

        action = "ADD" if any(k in text_lower for k in ["add", "buy"]) else ("REMOVE" if any(k in text_lower for k in ["remove", "delete"]) else "UNKNOWN")

        return {
            "action": action,
            "item_name": clean_item if clean_item else "item",
            "quantity": qty,
            "category": "General",
            "max_price": None
        }