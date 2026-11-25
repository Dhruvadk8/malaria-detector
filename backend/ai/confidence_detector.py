from typing import Dict, Any, Tuple, Literal

def detect_uncertainty(match_score: float, is_ambiguous: bool, is_human_requested: bool) -> Tuple[float, Literal["HIGH", "MEDIUM", "LOW"]]:
    """
    Evaluates confidence percentage (0-100%) and confidence level (HIGH, MEDIUM, LOW).
    """
    if is_human_requested:
        return 0.10, "LOW"

    if is_ambiguous:
        return 0.45, "LOW"

    # Scale match_score (0.30 - 0.95) to percentage (40% - 98%)
    if match_score >= 0.75:
        confidence = min(0.98, 0.80 + (match_score - 0.75) * 0.9)
        level = "HIGH"
    elif match_score >= 0.45:
        confidence = 0.50 + (match_score - 0.45) * 0.95
        level = "MEDIUM"
    else:
        confidence = max(0.15, match_score * 0.9)
        level = "LOW"

    return round(confidence, 2), level
