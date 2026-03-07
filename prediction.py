from database import supabase
from calculations import estimate_remaining_cost

def create_prediction(student_id, predicted_hours_remaining, predicted_completion_date):
    cost_estimate = estimate_remaining_cost(student_id, predicted_hours_remaining)
    supabase.table("predictions").insert({
        "student_id": student_id,
        "predicted_hours": predicted_hours_remaining,
        "predicted_cost": cost_estimate,
        "predicted_completion_date": predicted_completion_date
    }).execute()