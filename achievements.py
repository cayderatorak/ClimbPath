def calculate_achievements(totals):
    achievements = []
    if totals.get("Solo",0) >= 5:
        achievements.append("Solo Achieved")
    if totals.get("XC",0) >= 10:
        achievements.append("Cross Country Achieved")
    if totals.get("Total",0) >= 25:
        achievements.append("Checkride Ready")
    return achievements