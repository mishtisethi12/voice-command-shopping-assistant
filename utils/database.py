import os
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client safely
@st.cache_resource
def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL") or (st.secrets["SUPABASE_URL"] if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets else None)
    key = os.getenv("SUPABASE_KEY") or (st.secrets["SUPABASE_KEY"] if hasattr(st, "secrets") and "SUPABASE_KEY" in st.secrets else None)
    
    if not url or not key:
        st.error("Supabase credentials missing. Check your secrets.toml or environment variables.")
        return None
        
    return create_client(url, key)

supabase = init_supabase()

def get_shopping_list():
    if not supabase:
        return []
    try:
        # desc=False se naye items list me niche add honge
        response = supabase.table("shopping_list").select("*").order("created_at", desc=False).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching shopping list: {e}")
        return []

def add_item(item_name: str, quantity: int = 1, category: str = "General"):
    if not supabase:
        return None
    try:
        data = {
            "item_name": item_name,
            "quantity": quantity,
            "category": category
        }
        response = supabase.table("shopping_list").insert(data).execute()
        return response.data
    except Exception as e:
        st.error(f"Error adding item: {e}")
        return None

def remove_item(item_name: str):
    if not supabase or not item_name:
        return None
    try:
        clean_name = item_name.strip()
        # Case-insensitive delete query
        response = supabase.table("shopping_list").delete().ilike("item_name", f"%{clean_name}%").execute()
        return response.data
    except Exception as e:
        st.error(f"Error removing item: {e}")
        return None