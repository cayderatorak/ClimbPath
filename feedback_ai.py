from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

KEYWORDS = {
    "Landings": ["landing", "flare", "touchdown", "roundout"],
    "Radio Communication": ["radio", "comms", "communication", "phraseology", "atc"],
    "Crosswind Control": ["crosswind", "wind correction", "drift"],
    "Pattern Work": ["pattern", "traffic pattern", "downwind", "base", "final"],
    "Takeoffs": ["takeoff", "rotation", "centerline"],
    "Stalls": ["stall", "stall recovery", "angle of attack"],
    "Navigation": ["navigation", "nav", "heading", "course", "pilotage", "dead reckoning"],
    "Checklist Discipline": ["checklist", "flows", "before takeoff", "before landing"],
    "ADM / Risk": ["decision", "adm", "risk", "weather", "go/no-go", "minimums"],
}

POSITIVE_WORDS = {
    "good", "great", "improved", "solid", "excellent", "confident", "smooth", "stable", "better"
}
NEGATIVE_WORDS = {
    "weak", "late", "poor", "unsafe", "unstable", "missed", "forgot", "needs", "inconsistent", "fix"
}

ACTION_LIBRARY = {
    "Landings": "Do 6 pattern reps focused on stabilized approach and sight picture consistency.",
    "Radio Communication": "Practice 10 radio calls using script cards before your next flight.",
    "Crosswind Control": "Add 20 minutes of crosswind correction drills in pattern work.",
    "Pattern Work": "Fly a pattern-focused lesson with target altitude/speed gates on each leg.",
    "Takeoffs": "Review takeoff briefing flow and centerline tracking cues before engine start.",
    "Stalls": "Run a stall recognition/recovery session and brief ACS standards before flight.",
    "Navigation": "Plan and brief one short XC route, then verbalize checkpoints in flight.",
    "Checklist Discipline": "Use challenge-response checklist callouts for critical phases.",
    "ADM / Risk": "Write personal weather minimums and brief go/no-go criteria preflight.",
}

def _clean_notes(df: pd.DataFrame) -> list[str]:
    if df.empty or "notes" not in df.columns:
        return []
    notes = df["notes"].dropna().astype(str)
    return [n.strip() for n in notes if n.strip()]


def _score_sentiment(text: str) -> int:
    words = text.lower().split()
    pos = sum(1 for w in words if w.strip(".,!?;:") in POSITIVE_WORDS)
    neg = sum(1 for w in words if w.strip(".,!?;:") in NEGATIVE_WORDS)
    return pos - neg


def _extract_categories(notes: list[str]) -> dict[str, dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    for note in notes:
        low = note.lower()
        for category, words in KEYWORDS.items():
            hits = sum(low.count(word) for word in words)
            if hits > 0:
                if category not in categories:
                    categories[category] = {"mentions": 0, "sample_notes": []}
                categories[category]["mentions"] += hits
                if len(categories[category]["sample_notes"]) < 2:
                    categories[category]["sample_notes"].append(note)
    return categories


def _trend_label(older_avg: float, recent_avg: float) -> str:
    if recent_avg - older_avg > 0.4:
        return "improving"
    if older_avg - recent_avg > 0.4:
        return "declining"
    return "steady"


def analyze_feedback(df: pd.DataFrame) -> dict[str, Any]:
    """
    Returns a richer feedback payload while keeping backward compatibility for
    UI consumers by including `categories` and `legacy_counts`.
    """
    notes = _clean_notes(df)
    if not notes:
        return {
            "summary": "No instructor feedback available yet.",
            "categories": {},
            "legacy_counts": {},
            "actions": [],
            "sentiment": {"recent": 0.0, "older": 0.0, "trend": "steady"},
        }


    category_data = _extract_categories(notes)
    legacy_counts = {k: v["mentions"] for k, v in category_data.items()}

    # Split older vs recent by note order (last third = recent).
    split_idx = max(int(len(notes) * (2 / 3)), 1)
    older_notes = notes[:split_idx]
    recent_notes = notes[split_idx:] if split_idx < len(notes) else notes[-1:]

    older_avg = sum(_score_sentiment(n) for n in older_notes) / max(len(older_notes), 1)
    recent_avg = sum(_score_sentiment(n) for n in recent_notes) / max(len(recent_notes), 1)
    trend = _trend_label(older_avg, recent_avg)

    # Highest-mention categories become action priorities.
    top_categories = sorted(category_data.items(), key=lambda item: item[1]["mentions"], reverse=True)[:3]
    actions = [ACTION_LIBRARY.get(cat, f"Practice focused drills for {cat}.") for cat, _ in top_categories]

    if top_categories:
        focus_text = ", ".join(cat for cat, _ in top_categories)
        summary = f"Top focus areas: {focus_text}. Sentiment trend: {trend}."
    else:
        summary = f"General feedback trend: {trend}."

    return {
        "summary": summary,
        "categories": category_data,
        "legacy_counts": legacy_counts,
        "actions": actions,
        "sentiment": {"recent": recent_avg, "older": older_avg, "trend": trend},
    }