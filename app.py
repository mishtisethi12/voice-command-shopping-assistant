import streamlit as st
import pandas as pd
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
from utils.command_parser import parse_voice_command
from utils.database import get_shopping_list, add_item, remove_item
from utils.recommendation import get_smart_suggestions

# Page configuration
st.set_page_config(page_title="Voice Cart | Smart Assistant", page_icon="🛒", layout="wide")

# Load catalog and shopping history safely
def load_data():
    try:
        catalog_df = pd.read_csv("data/products.csv")
        catalog_df.columns = catalog_df.columns.str.strip().str.lower()
    except Exception:
        catalog_df = pd.DataFrame(columns=["product_name", "category", "price"])
        
    try:
        history_df = pd.read_csv("data/shopping_history.csv")
        history_df.columns = history_df.columns.str.strip().str.lower()
        past_items = history_df["item_name"].tolist() if "item_name" in history_df.columns else []
    except Exception:
        past_items = []
        
    return catalog_df, past_items

catalog_df, past_items = load_data()

# App Header
st.title("🛒 Voice Command Shopping Assistant")
st.caption("Powered by Gemini & Supabase | Supports English, Hindi, Hinglish & Recipe Parsing")

# Fetch current shopping cart
cart_items = get_shopping_list()

# Layout Columns
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    st.subheader("🎙️ Speak or Type Command")
    
    st.write("Click microphone to record voice:")
    audio_bytes = audio_recorder(
        text="", 
        recording_color="#e8b62c", 
        neutral_color="#6aa36f", 
        icon_size="2x",
        key="voice_recorder"
    )
    
    spoken_text = ""
    if audio_bytes:
        recognizer = sr.Recognizer()
        try:
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_bytes)
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = recognizer.record(source)
                spoken_text = recognizer.recognize_google(audio_data, language="hi-IN")
                st.info(f"🗣️ Recognized Voice: **{spoken_text}**")
        except Exception:
            st.warning("Could not clearly translate audio. Type command below.")

    user_input = st.text_input("Or enter command manually:", value=spoken_text, key="user_command_input")
    
    if st.button("Process Command", type="primary", key="process_cmd_btn") and user_input:
        with st.spinner("Processing command with Gemini..."):
            parsed = parse_voice_command(user_input)
            
            action = parsed.get("action")
            items = parsed.get("items", [])
            
            if action == "ADD" and items:
                added_names = []
                for item in items:
                    name = item.get("item_name")
                    qty = item.get("quantity", 1)
                    cat = item.get("category", "General")
                    if name:
                        add_item(name, qty, cat)
                        added_names.append(f"{qty}x {name}")
                
                st.success(f"✅ Added to cart: {', '.join(added_names)}")
                st.rerun()
                
            elif action == "REMOVE" and items:
                removed_names = []
                for item in items:
                    name = item.get("item_name")
                    if name:
                        remove_item(name)
                        removed_names.append(name)
                
                st.success(f"🗑️ Removed from cart: {', '.join(removed_names)}")
                st.rerun()
                
            elif action == "SEARCH" and items:
                st.subheader("🔍 Search Results")
                search_item = items[0].get("item_name", "")
                max_price = items[0].get("max_price")
                brand = items[0].get("brand")
                
                filtered_df = catalog_df.copy()
                
                if search_item and "product_name" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['product_name'].str.lower().str.contains(search_item.lower(), na=False)]
                if max_price is not None and "price" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['price'] <= float(max_price)]
                if brand and "product_name" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['product_name'].str.lower().str.contains(brand.lower(), na=False)]
                    
                if not filtered_df.empty:
                    st.dataframe(filtered_df[['product_name', 'category', 'price']], use_container_width=True)
                else:
                    st.warning("No matching products found.")
            else:
                st.error("Could not determine intent. Try: 'Chai banane ka samaan add karo' or 'Add Tea, Milk, Sugar'")

    st.markdown("---")
    st.subheader("📋 Current Shopping Cart")
    
    cart_items = get_shopping_list()
    
    if cart_items:
        grouped_items = {}
        for item in cart_items:
            cat = item.get("category", "General") or "General"
            if cat not in grouped_items:
                grouped_items[cat] = []
            grouped_items[cat].append(item)
            
        total_price = 0.0
        global_idx = 1

        for category, items in grouped_items.items():
            with st.expander(f"📦 **{category}** ({len(items)} items)", expanded=True):
                col_num, col_name, col_qty, col_price, col_action = st.columns([0.5, 2.5, 1, 1.2, 0.8])
                with col_num:
                    st.markdown("**#**")
                with col_name:
                    st.markdown("**Item Name**")
                with col_qty:
                    st.markdown("**Quantity**")
                with col_price:
                    st.markdown("**Est. Price**")
                with col_action:
                    st.markdown("**Action**")
                
                st.divider()

                for item in items:
                    item_name = str(item.get("item_name", "")).strip()
                    qty = int(item.get("quantity", 1))
                    
                    # Fuzzy / Partial Price Lookup
                    unit_price = 0.0
                    if not catalog_df.empty and "product_name" in catalog_df.columns and "price" in catalog_df.columns:
                        clean_item = item_name.lower()
                        
                        match = catalog_df[catalog_df['product_name'].astype(str).str.strip().str.lower() == clean_item]
                        
                        if match.empty:
                            match = catalog_df[catalog_df['product_name'].astype(str).str.strip().str.lower().apply(
                                lambda x: x in clean_item or clean_item in x if x else False
                            )]
                            
                        if not match.empty:
                            try:
                                unit_price = float(match.iloc[0]['price'])
                            except (ValueError, TypeError):
                                unit_price = 0.0
                    
                    item_total = unit_price * qty
                    total_price += item_total

                    c1, c2, c3, c4, c5 = st.columns([0.5, 2.5, 1, 1.2, 0.8])
                    with c1:
                        st.write(f"**{global_idx}**")
                    with c2:
                        st.write(item_name)
                    with c3:
                        st.write(qty)
                    with c4:
                        if item_total > 0:
                            st.write(f"₹{item_total:.2f}")
                        else:
                            st.caption("N/A")
                    with c5:
                        item_id = item.get("id", f"item_{global_idx}")
                        if st.button("🗑️", key=f"del_btn_{item_id}_{global_idx}"):
                            remove_item(item_name)
                            st.toast(f"Removed '{item_name}'", icon="🗑️")
                            st.rerun()
                    
                    global_idx += 1

        st.divider()
        
        m1, m2 = st.columns([3, 1])
        with m2:
            st.metric(label="💰 Total Estimated Cost", value=f"₹{total_price:.2f}")

    else:
        st.info("Your shopping list is empty.")

with col_sidebar:
    st.subheader("💡 Smart AI Suggestions")
    if st.button("Generate Suggestions", key="gen_suggestions_btn"):
        with st.spinner("Analyzing cart context..."):
            current_names = [item['item_name'] for item in cart_items] if cart_items else []
            catalog_names = catalog_df['product_name'].tolist() if not catalog_df.empty and 'product_name' in catalog_df.columns else []
            suggestions = get_smart_suggestions(
                current_list=current_names, 
                products_catalog=catalog_names, 
                past_history=past_items
            )
            st.markdown(suggestions)