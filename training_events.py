from database import supabase

def log_training_event(student_id, instructor_id, flight_id, event_type, value=None, notes=None):
    supabase.table("training_events").insert({
        "student_id": student_id,
        "instructor_id": instructor_id,
        "related_flight_id": flight_id,
        "event_type": event_type,
        "event_value": value,
        "notes": notes
    }).execute()