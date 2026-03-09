import pandas as pd
from database import supabase

def load_student_flights(student_id):
    flights = supabase.table("flights").select("*").eq("student_id", student_id).execute()
    df = pd.DataFrame(flights.data) if flights.data else pd.DataFrame(columns=[
        "id","student_id","instructor_id","aircraft_id","rate_id",
        "total_time","solo","cross_country","night","created_at"
    ])
    return df