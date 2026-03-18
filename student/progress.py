from database import supabase
import pandas as pd

SCHOOL_AVG = {
    "Dual": 8,
    "Solo": 4,
    "XC": 6,
    "Night": 2
}

def school_averages(track):
    return SCHOOL_AVG

def student_rankings(student_id, track):
    leaderboard = supabase.table("flights").select("student_id,total_time").execute().data
    if not leaderboard:
        return 0,0
    df = pd.DataFrame(leaderboard)
    total_times = df.groupby("student_id").total_time.sum().sort_values(ascending=False)
    rank_list = list(total_times.index)
    rank = rank_list.index(student_id)+1 if student_id in rank_list else len(rank_list)
    percentile = int((1 - (rank-1)/len(rank_list))*100)
    return rank, percentile