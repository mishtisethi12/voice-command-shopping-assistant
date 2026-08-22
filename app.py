import streamlit as st
from streamlit_mic_recorder import speech_to_text
from utils.database import get_shopping_list, add_to_list, remove_from_list, search_products
from utils.command_parser import parse_voice_command
from utils.recommendation import get_smart_suggestions

# Page Config
st.set_page_config(page_title="Voice Cart | Smart Assistant", page_icon="🛒", layout="wide")

# Modern Styling Injection
st.markdown("""
    <style>
    /* Main container background & typography */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    /* Item Cards */
    .item-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .item-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    
    /* Category Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-produce { background-color: #064e3b; color: #34d399; }
    .badge-dairy { background-color: #1e3a8a; color: #93c5fd; }
    .badge-bakery { background-color: #78350f; color: #fde047; }
    .badge-hygiene { background-color: #581c87; color: #c084fc; }
    .badge-general { background-color: #334155; color: #cbd5e1; }
    
    /* Hide default Streamlit fluff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Helper for category styling
def get_badge_html(category):
    cat_clean = str(category).lower()
    badge_class = f"badge-{cat_clean}" if cat_clean in ["produce", "dairy", "bakery", "hygiene"] else "badge-general"
    return f'<span class="badge {badge_class}">{category}</span>'

# --- Header Section ---
st.markdown("""
    <div class="header-card">
        <h1 style='margin:0; font-size: 2.2rem; font-weight: 700; color: #f8fafc;'>🛒 Voice Cart AI</h1>
        <p style='margin-top:6px; color: #94a3b8; font-size: 1rem;'>Your intelligent, voice-powered grocery companion</p>
    </div>
""", unsafe_allow_html=True)

# --- Voice Command Interface ---
with st.container():
    col_v1, col_v2 = st.columns([1, 2])
    
    with col_v1:
        st.markdown("#### 🎙️ Voice Input")
        st.caption("Click to record: *'Add 3 apples'*, *'Remove milk'*, or *'Find bread under $4'*")
        spoken_text = speech_to_text(
            language='en', 
            start_prompt="Start Speaking 🎙️", 
            stop_prompt="Processing... 🔴", 
            key='speech'
        )

    with col_v2:
        if spoken_text:
            st.markdown(f"**Recognized Command:** `{spoken_text}`")
            with st.spinner("Analyzing intent..."):
                parsed = parse_voice_command(spoken_text)
                action = parsed.get("action")
                
                if action == "ADD":
                    item_name = parsed.get("item_name")
                    qty = parsed.get("quantity", 1)
                    cat = parsed.get("category", "General")
                    
                    # Update database in background
                    add_to_list(item_name, qty, cat)
                    st.success(f"Added **{qty}x {item_name}** to your cart!")
                    
                elif action == "REMOVE":
                    item_name = parsed.get("item_name")
                    remove_from_list(item_name)
                    st.warning(f"Removed **{item_name}** from your cart!")
                elif action == "SEARCH":
                    st.session_state['search_query'] = parsed.get("item_name")
                    st.session_state['search_price'] = parsed.get("max_price")
                else:
                    st.error("Could not understand the command. Try again.")

# Display Search Results if triggered
if 'search_query' in st.session_state and st.session_state['search_query']:
    query = st.session_state['search_query']
    price = st.session_state.get('search_price')
    results = search_products(query, price)
    
    st.markdown("---")
    st.subheader(f"🔍 Catalog Results for '{query}'" + (f" (Under ${price})" if price else ""))
    
    if results:
        st.dataframe(results, use_container_width=True)
    else:
        st.info("No matching products found in catalog.")
        
    if st.button("Clear Search Results"):
        del st.session_state['search_query']
        st.rerun()

st.markdown("---")

# --- Main Dashboard ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📋 Current Shopping List")
    items = get_shopping_list()
    
    if items:
        # Quick stats metrics
        m1, m2 = st.columns(2)
        m1.metric("Total Unique Items", len(items))
        m2.metric("Total Items Count", sum(i.get('quantity', 1) for i in items))
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Render stylized rows
        for idx, item in enumerate(items):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1])
            with c1:
                st.markdown(f"**{item['item_name'].title()}**")
            with c2:
                st.markdown(f"Qty: **`{item['quantity']}`**")
            with c3:
                st.markdown(get_badge_html(item['category']), unsafe_allow_html=True)
            with c4:
                if st.button("🗑️", key=f"del_{idx}"):
                    remove_from_list(item['item_name'])
                    st.rerun()
    else:
        st.info("Your shopping list is completely empty.")

with col_right:
    st.subheader("💡 Smart AI Assistant")
    catalog = search_products()
    
    if st.button("Generate AI Recommendations", use_container_width=True, type="primary"):
        with st.spinner("Analyzing active list..."):
            suggestions = get_smart_suggestions(items, catalog)
            st.markdown("""
                <div style='background-color: #1e293b; padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-top: 12px;'>
            """, unsafe_allow_html=True)
            st.markdown(suggestions)
            st.markdown("</div>", unsafe_allow_html=True)