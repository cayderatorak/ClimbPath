import pandas as pd
from postgrest.exceptions import APIError
from database import supabase


FLIGHT_COLUMNS = [
    "id", "student_id", "instructor_id", "aircraft_id", "rate_id",
    "total_time", "solo", "cross_country", "night", "created_at"
]
FEEDBACK_COLUMNS = ["notes", "created_at", "event_type"]


def _empty_frame(columns):
    return pd.DataFrame(columns=columns)

def load_student_flights(student_id):
    try:
        flights = supabase.table("flights").select("*").eq("student_id", student_id).execute()
    except APIError:
        return _empty_frame(FLIGHT_COLUMNS)

    return pd.DataFrame(flights.data) if flights.data else _empty_frame(FLIGHT_COLUMNS)

def load_student_feedback_notes(student_id):
    try:
        events = (
            supabase.table("training_events")
            .select("notes,created_at,event_type")
            .eq("student_id", student_id)
            .execute()
        )
    except APIError:
        return _empty_frame(FEEDBACK_COLUMNS)

    df = pd.DataFrame(events.data) if events.data else _empty_frame(FEEDBACK_COLUMNS)
    if df.empty:
        return df

    df["notes"] = df["notes"].fillna("").astype(str)
    return df[df["notes"].str.strip() != ""]