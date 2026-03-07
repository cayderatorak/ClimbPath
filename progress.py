from database import supabase

# Example: get school average for each category
def school_averages(track):
    flights = supabase.table("flights").select("*").execute().data
    if not flights:
        return {}
    df = pd.DataFrame(flights)
    averages = {
        "Dual": df[df["solo"]==False]["total_time"].mean(),
        "Solo": df[df["solo"]==True]["total_time"].mean(),
        "XC": df[df["cross_country"]==True]["total_time"].mean(),
        "Night": df[df["night"]==True]["total_time"].mean()
    }
    return averages

# Rank students in the school for a specific track
def student_rankings(student_id, track):
    flights = supabase.table("flights").select("*").execute().data
    if not flights:
        return 0,0
    df = pd.DataFrame(flights)
    totals = df.groupby("student_id")["total_time"].sum().sort_values(ascending=False)
    rank = list(totals.index).index(student_id) + 1 if student_id in totals.index else len(totals)+1
    percentile = int((1 - (rank-1)/len(totals))*100)
    return rank, percentile