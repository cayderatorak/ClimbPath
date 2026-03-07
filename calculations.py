from database import supabase, get_flight_rate

# Calculate total hours and breakdown by flight type
def calculate_totals(df):
    totals = {
        "Total": df["total_time"].sum() if not df.empty else 0,
        "Dual": df[df["solo"]==False]["total_time"].sum() if not df.empty else 0,
        "Solo": df[df["solo"]==True]["total_time"].sum() if not df.empty else 0,
        "XC": df[df["cross_country"]==True]["total_time"].sum() if not df.empty else 0,
        "Night": df[df["night"]==True]["total_time"].sum() if not df.empty else 0
    }
    total_cost = df["flight_cost"].sum() if "flight_cost" in df.columns else 0
    return totals, total_cost

# Flight cost based on flight time and rate
def calculate_flight_cost(total_time, aircraft_rate, instructor_rate):
    return total_time * (aircraft_rate + instructor_rate)

# Checkride prediction (example: linear estimate)
def estimate_checkride(df, targets_hours):
    total_hours = df["total_time"].sum() if not df.empty else 0
    remaining = targets_hours - total_hours
    # Assume average 3 hrs/week
    weeks_remaining = remaining / 3
    return weeks_remaining