from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CheckrideQuestion:
    prompt: str
    good_answer_points: list[str]
    category: str


QUESTION_BANK = {
    "Private Pilot": [
        CheckrideQuestion(
            category="ADM / Weather",
            prompt="You're planning a VFR cross-country and ceilings are forecast near your personal minimums. Walk me through your go/no-go decision.",
            good_answer_points=[
                "References personal minimums and PAVE/5P risk framework",
                "Compares forecast with trend data and alternates",
                "Provides clear no-go trigger and mitigation plan",
            ],
        ),
        CheckrideQuestion(
            category="Systems",
            prompt="What would you do if the alternator fails in flight?",
            good_answer_points=[
                "Recognizes electrical failure indications",
                "Runs checklist and load-shedding steps",
                "Plans nearest suitable landing",
            ],
        ),
        CheckrideQuestion(
            category="Performance",
            prompt="How do you evaluate takeoff distance for a short runway on a hot day?",
            good_answer_points=[
                "Uses POH performance tables correctly",
                "Adjusts for pressure altitude, temperature, wind, runway condition",
                "Includes conservative safety margin",
            ],
        ),
    ],
    "Instrument": [
        CheckrideQuestion(
            category="IFR Decision Making",
            prompt="When would you file an alternate, and how would you choose one?",
            good_answer_points=["Uses 1-2-3 rule", "Evaluates approach minima and fuel", "Considers weather trends"],
        ),
    ],
    "Commercial": [
        CheckrideQuestion(
            category="Regulations",
            prompt="Explain common carriage vs private carriage and why it matters.",
            good_answer_points=["Defines holding out", "Distinguishes compensation rules", "Applies to realistic scenario"],
        ),
    ],
}


def _weak_categories(feedback_insights: dict[str, Any]) -> list[str]:
    categories = feedback_insights.get("categories", {}) if feedback_insights else {}
    ranked = sorted(categories.items(), key=lambda item: item[1].get("mentions", 0), reverse=True)
    return [name for name, _ in ranked[:2]]


def build_checkride_session(track_name: str, totals: dict[str, float], feedback_insights: dict[str, Any]) -> dict[str, Any]:
    questions = QUESTION_BANK.get(track_name, QUESTION_BANK["Private Pilot"])
    weak = _weak_categories(feedback_insights)

    # Create a simple readiness estimate from completed total hours.
    total_hours = float(totals.get("Total", 0) or 0)
    readiness = min(max((total_hours / 40) * 100, 0), 100)

    focus_hint = ""
    if weak:
        focus_hint = f"Focus extra practice on: {', '.join(weak)}."

    return {
        "track": track_name,
        "readiness_percent": round(readiness, 1),
        "focus_hint": focus_hint,
        "questions": questions,
    }
