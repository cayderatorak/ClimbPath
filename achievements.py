from database import supabase

# Calculate unlocked achievements based on totals
def calculate_achievements(totals):
    badges = []
    if totals["Solo"] >= 1:
        badges.append("First Solo")
    if totals["XC"] >= 5:
        badges.append("Cross-Country Master")
    if totals["Night"] >= 3:
        badges.append("Night Owl")
    if totals["Total"] >= 50:
        badges.append("50 Hours Logged")
    return badges

# Unlock achievement in DB
def unlock_achievement(student_id, achievement_name):
    achievement = supabase.table("achievements").select("*").eq("name", achievement_name).single().execute().data
    if not achievement:
        return False
    # Check if already unlocked
    exists = supabase.table("user_achievements")\
        .select("*")\
        .eq("user_id", student_id)\
        .eq("achievement_id", achievement["id"]).single().execute().data
    if exists:
        return False
    # Insert
    supabase.table("user_achievements").insert({
        "user_id": student_id,
        "achievement_id": achievement["id"]
    }).execute()
    return True