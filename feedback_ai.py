import pandas as pd

KEYWORDS = {
    "Landings": ["landing", "flare", "touchdown"],
    "Radio Communication": ["radio", "comms", "communication"],
    "Crosswind Control": ["crosswind", "wind correction"],
    "Pattern Work": ["pattern", "traffic pattern"],
    "Takeoffs": ["takeoff", "rotation"],
    "Stalls": ["stall", "stall recovery"],
    "Navigation": ["navigation", "nav", "heading"],
}

def analyze_feedback(df):

    if df.empty or "notes" not in df.columns:
        return {}

    feedback = " ".join(df["notes"].dropna().astype(str)).lower()

    insights = {}

    for category, words in KEYWORDS.items():

        count = sum(feedback.count(word) for word in words)

        if count > 0:
            insights[category] = count

    return insights