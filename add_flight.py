from datetime import date, datetime
from database import supabase
from milestones import check_and_unlock_milestones


def _serialize_date(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
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
    flight_date_str = _serialize_date(flight_date or datetime.utcnow())

    is_solo = flight_type == "Solo"
    is_dual = flight_type == "Dual"

    result = supabase.table("flights").insert({
        "student_id":   user_id,
        "instructor_id": instructor_id if not is_solo else None,
        "aircraft_id":  aircraft_id,
        "rate_id":      rate_id,
        "date":         flight_date_str,
        "total_time":   duration,
        "dual_time":    duration if is_dual else 0,
        "solo_time":    duration if is_solo else 0,
        "cross_country": duration if is_xc else 0,
        "night":        duration if is_night else 0,
        "solo":         is_solo,
        "remarks":      feedback,
    }).execute()

    flight_id = result.data[0]["id"] if result.data else None

    supabase.table("training_events").insert({
        "student_id":        user_id,
        "instructor_id":     instructor_id,
        "related_flight_id": flight_id,
        "event_type":        flight_type.lower(),
        "event_value":       duration,
        "notes":             feedback,
    }).execute()

    supabase.table("activity_feed").insert({
        "user_id":           user_id,
        "activity_type":     "flight",
        "title":             f"Logged a {flight_type.lower()} flight",
        "description":       f"{duration} hrs",
        "related_flight_id": flight_id,
        "is_public":         True,
    }).execute()

    check_and_unlock_milestones(user_id)