import pandas as pd
from database import supabase


def load_student_flights(student_id):
    flights = supabase.table("flights").select("*").eq("student_id", student_id).execute()
    df = pd.DataFrame(flights.data) if flights.data else pd.DataFrame(columns=[
        "id", "student_id", "instructor_id", "aircraft_id", "rate_id",
        "total_time", "solo", "cross_country", "night", "created_at"
    ])
    return df


def load_student_feedback_notes(student_id):
    events = (
        supabase.table("training_events")
        .select("notes,created_at,event_type")
        .eq("student_id", student_id)
        .execute()
    )

    df = pd.DataFrame(events.data) if events.data else pd.DataFrame(columns=["notes", "created_at", "event_type"])
    if df.empty:
        return df

    df["notes"] = df["notes"].fillna("").astype(str)
    return df[df["notes"].str.strip() != ""]