# calculations.py
def calculate_totals(df):
    totals = {
        "Dual": df[df["solo"]==False]["total_time"].sum() if not df.empty else 0,
        "Solo": df[df["solo"]==True]["total_time"].sum() if not df.empty else 0,
        "XC": df[df.get("cross_country", False)]["total_time"].sum() if not df.empty else 0,
        "Night": df[df.get("night", False)]["total_time"].sum() if not df.empty else 0,
    }
    totals["Total"] = sum([totals[k] for k in ["Dual","Solo","XC","Night"]])
    return totals, df

def calculate_flight_cost(duration, aircraft_rate, instructor_rate):
    return duration * (aircraft_rate + instructor_rate)