# database.py
from supabase import create_client
import os
import streamlit as st

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Helper functions for common queries ---

@st.cache_data(ttl=60)
def get_student_flights(user_id):
    return supabase.table("flights").select("*").eq("student_id", user_id).execute()

def get_flight_rate(flight_id):
    try:
        flight = supabase.table("flights").select("rate_id").eq("id", flight_id).single().execute()
    except APIError:
        return None

            rate_id = flight.data.get("rate_id")
        if not rate_id:
            return None

        try:
            return supabase.table("rates").select("*").eq("id", rate_id).single().execute().data
        except APIError:
            return None
    return None

def get_student_achievements(student_id):
    return supabase.table("user_achievements").select("*").eq("user_id", student_id).execute()
