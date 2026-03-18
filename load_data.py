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


def _safe_execute(columns, query_builder):
    try:
        response = query_builder.execute()
    except APIError:
        return _empty_frame(columns)
    except Exception:
        return _empty_frame(columns)

    return pd.DataFrame(response.data) if response.data else _empty_frame(columns)


def load_student_flights(student_id):
    if not student_id:
        return _empty_frame(FLIGHT_COLUMNS)

    return _safe_execute(
        FLIGHT_COLUMNS,
        supabase.table("flights").select("*").eq("student_id", student_id),
    )


def load_student_feedback_notes(student_id):
    if not student_id:
        return _empty_frame(FEEDBACK_COLUMNS)

    df = _safe_execute(
        FEEDBACK_COLUMNS,
        supabase.table("training_events")
        .select("notes,created_at,event_type")
        .eq("student_id", student_id),
    )
    if df.empty:
        return df

    df["notes"] = df["notes"].fillna("").astype(str)
    return df[df["notes"].str.strip() != ""]