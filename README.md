# 🛒 Voice Command Shopping Assistant

An intelligent, voice-activated grocery list manager built with Streamlit, Supabase (PostgreSQL), and Google Gemini 3.6-flash. The application enables multi-lingual voice/text input, natural language intent parsing, recipe-to-cart multi-item expansion, real-time price estimation, and contextual AI recommendations.

🔗 Live Application: [https://voice-command-shopping-assistant-ez4uos2dyrfuwayxjx3ivh.streamlit.app/](https://your-app-name.streamlit.app)

📂 GitHub Repository: [https://github.com/mishtisethi12/voice-command-shopping-assistant](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/your-username/voice-command-shopping-assistant)

---

## ✨ Features

* 🎙️ Multi-Lingual Voice & Text Input: Supports natural language commands in English, Hindi, and Hinglish using Google Speech Recognition.
* 🍳 Recipe-to-Cart Engine: Automatically decomposes complex recipes (e.g., "Chai banane ka samaan", "Paneer Tikka ingredients") into individual categorized grocery items.
* 📦 Categorized Cart Management: Groups items automatically by category (Dairy, Produce, Beverages, etc.) with real-time persistent storage in Supabase.
* 💰 Live Price Lookup & Total Estimation: Performs fuzzy string matching against a local product catalog (data/products.csv) to project total cart cost.
* 💡 Smart AI Suggestions: Context-aware recommendations for routine replenishment, seasonal/budget picks, and healthy dietary substitutes (e.g., Almond Milk for Milk).
* 🔍 Voice-Activated Catalog Search: Filter catalog items by keyword, brand, or price constraints (e.g., "Find toothpaste under ₹100").

---

## 🛠️ Tech Stack

* Frontend / UI: Streamlit
* Backend / Database: Supabase (PostgreSQL)
* AI / NLP Engine: Google Gemini API (gemini-3.6-flash)
* Speech Processing: SpeechRecognition, audio-recorder-streamlit
* Data Handling: Pandas

---

## 📁 Project Structure

```text
voice-command-shopping-assistant/
├── data/
│   ├── products.csv            # Product catalog for price lookup
│   └── shopping_history.csv    # User purchase history for smart suggestions
├── utils/
│   ├── command_parser.py       # Gemini-powered natural language intent parser
│   ├── database.py             # Supabase database helper functions
│   └── recommendation.py       # Gemini-powered recommendation engine
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites

* Python 3.10+ installed
* Supabase project set up with a shopping_list table (id, item_name, quantity, category)
* Google Gemini API Key

### 2. Clone the Repository

git clone [https://github.com/your-username/voice-command-shopping-assistant.git](https://www.google.com/search?q=https://github.com/mishtisethi12/voice-command-shopping-assistant.git)
cd voice-command-shopping-assistant

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Configure Secrets

Create a .streamlit/secrets.toml file in the root directory:

GEMINI_API_KEY = "your_gemini_api_key"
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_key"

### 5. Run the Application

streamlit run app.py

---

## 📝 Approach & Architecture 
-Approach & Architecture Overview I built this Voice-Activated Shopping Assistant to make grocery management fast, intuitive, and hands-free. The app uses Streamlit for a clean, responsive UI, Supabase (PostgreSQL) for reliable real-time cart persistence, and Google’s Gemini 3.6-flash API to handle all natural language understanding. 

-To make voice input flexible, I integrated Google Speech Recognition supporting English, Hindi, and Hinglish. Instead of relying on basic keyword matching, Gemini parses voice commands into structured JSON objects. It intelligently translates item names into English and expands broad recipe requests (like "Chai banane ka samaan") into complete, categorized ingredient lists (tea, milk, sugar) with standard quantities. 

-The assistant also features a smart recommendation engine that analyzes current cart items against user purchase history to suggest routine refills, seasonal options, and healthy substitutes like almond milk. Items are cross-referenced with a catalog dataset using flexible string matching to give instant estimated cart totals, while real-time spinners and toast alerts keep the user experience smooth and interactive. 


---

## 📄 License

This project is open source under the MIT License.
