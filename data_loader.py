import pandas as pd
from database import get_student_flights
from database import supabase

def load_student_data(user_id):

    flights = get_student_flights(user_id).data

    flights_df = pd.DataFrame(flights) if flights else pd.DataFrame()

    events = supabase.table("training_events") \
        .select("*") \
        .eq("student_id", user_id) \
        .execute().data

    events_df = pd.DataFrame(events) if events else pd.DataFrame()

    return flights_df, events_df

def get_aircraft():
    response = supabase.table("aircraft").select("*").execute()
    return response.data

def get_instructors():
    response = supabase.table("instructors").select("*").execute()
    return response.data