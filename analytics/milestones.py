from database import supabase

MILESTONES = [
    {"name":"First Solo","hours":5},
    {"name":"XC Ready","hours":15},
    {"name":"Checkride","hours":25}
]

def next_milestone(totals):
    total_hours = totals.get("Total",0)
    for milestone in MILESTONES:
        if total_hours < milestone["hours"]:
            return milestone["name"]
    return "Completed"

def check_and_unlock_milestones(user_id):
    totals = supabase.table("flights").select("*").eq("student_id", user_id).execute().data
    hours = sum([f["total_time"] for f in totals]) if totals else 0
    unlocked = []
    for m in MILESTONES:
        if hours >= m["hours"]:
            # record in DB if not already unlocked
            exists = supabase.table("milestones").select("*").eq("student_id", user_id).eq("name", m["name"]).execute().data
            if not exists:
                supabase.table("milestones").insert({"student_id": user_id,"name":m["name"]}).execute()
                unlocked.append(m["name"])
    return unlocked