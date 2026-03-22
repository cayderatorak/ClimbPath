from datetime import date, datetime
from database import supabase
from milestones import check_and_unlock_milestones


def _serialize_created_at(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time()).isoformat()
    return value


def add_flight(
    user_id,
    instructor_id,
    aircraft_id,
    rate_id,
    duration,
    flight_type,
    is_xc,
    is_night,
    feedback,
    flight_date=None,
):
    created_at = _serialize_created_at(flight_date or datetime.utcnow())

    result = supabase.table("flights").insert({
        "student_id": user_id,
        "instructor_id": instructor_id,
        "aircraft_id": aircraft_id,
        "rate_id": rate_id,
        "total_time": duration,
        "solo": flight_type == "Solo",
        "cross_country": is_xc,
        "night": is_night,
        "created_at": created_at,
    }).execute()

    flight_id = result.data[0]["id"] if result.data else None

    supabase.table("training_events").insert({
        "student_id": user_id,
        "instructor_id": instructor_id,
        "related_flight_id": flight_id,
        "event_type": flight_type.lower(),
        "event_value": duration,
        "notes": feedback,
    }).execute()

    # Fixed: use correct column names matching activity_feed schema
    supabase.table("activity_feed").insert({
        "user_id": user_id,
        "activity_type": "flight",
        "title": f"Logged a {flight_type.lower()} flight",
        "description": f"{duration} hrs",
        "related_flight_id": flight_id,
        "is_public": True,
    }).execute()

    check_and_unlock_milestones(user_id)