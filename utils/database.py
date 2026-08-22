import os
import streamlit as st
from supabase import create_client, Client

# Retrieve credentials safely without hardcoding
SUPABASE_URL = os.getenv("SUPABASE_URL") or (st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else None)
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or (st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else None)

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing Supabase credentials. Please configure secrets.toml or environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=2)  # Caches reads for 2 seconds for smooth UI performance
def get_shopping_list():
    try:
        response = supabase.table("shopping_list").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Database fetch error: {e}")
        return []

def add_to_list(item_name, quantity=1, category="General"):
    try:
        # Check if item already exists in table
        existing = supabase.table("shopping_list").select("*").ilike("item_name", item_name).execute()
        
        if existing.data:
            # Update quantity for existing item
            current_qty = existing.data[0].get("quantity", 1)
            new_qty = current_qty + quantity
            supabase.table("shopping_list").update({"quantity": new_qty}).eq("id", existing.data[0]["id"]).execute()
        else:
            # Insert new item
            supabase.table("shopping_list").insert({
                "item_name": item_name.lower().strip(),
                "quantity": quantity,
                "category": category
            }).execute()
    except Exception as e:
        print(f"Database error in add_to_list: {e}")

def remove_from_list(item_name):
    return supabase.table("shopping_list").delete().ilike("item_name", f"%{item_name}%").execute()

def search_products(query="", max_price=None):
    q = supabase.table("products").select("*")
    if query:
        q = q.ilike("name", f"%{query}%")
    if max_price:
        q = q.lte("price", max_price)
    return q.execute().data