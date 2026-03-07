from database import supabase
from achievements import unlock_achievement

# Example milestones
MILESTONES = [
    {"name":"First Solo","required_hours":1},
    {"name":"10 Hours Total","required_hours":10},
    {"name":"50 Hours Total","required_hours":50},
    {"name":"Checkride Ready","required_hours":60}
]

# Next milestone based on totals
def next_milestone(totals):
    for m in MILESTONES:
        if totals["Total"] < m["required_hours"]:
            return m["name"]
    return "All Milestones Completed"

# Check and unlock milestones automatically
def check_and_unlock_milestones(student_id):
    flights = supabase.table("flights").select("*").eq("student_id", student_id).execute().data
    total_hours = sum(f["total_time"] for f in flights) if flights else 0
    for m in MILESTONES:
        if total_hours >= m["required_hours"]:
            unlock_achievement(student_id, m["name"])