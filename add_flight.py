from database import supabase
from datetime import datetime
from milestones import check_and_unlock_milestones

def add_flight(user_id, instructor_id, aircraft_id, rate_id, duration, flight_type, is_xc, is_night, feedback):
    result = supabase.table("flights").insert({
        "student_id": user_id,
        "instructor_id": instructor_id,
        "aircraft_id": aircraft_id,
        "rate_id": rate_id,
        "total_time": duration,
        "solo": flight_type=="Solo",
        "cross_country": is_xc,
        "night": is_night,
        "created_at": datetime.utcnow()
    }).execute()

    flight_id = result.data[0]["id"] if result.data else None

    supabase.table("training_events").insert({
        "student_id": user_id,
        "instructor_id": instructor_id,
        "related_flight_id": flight_id,
        "event_type": flight_type.lower(),
        "event_value": duration,
        "notes": feedback
    }).execute()

    supabase.table("activity_feed").insert({
        "student_id": user_id,
        "event_type": "flight",
        "event_value": duration,
        "related_id": flight_id
    }).execute()

    check_and_unlock_milestones(user_id)