def compute_field_confidence(
    ocr_conf: float,
    pattern_matched: bool,
    keyword_present: bool = True,
    arithmetic_valid: bool = None,
    threshold: float = 0.70,
) -> dict:
    """
    Computes a composite reliability score (0.0 to 1.0) and flags low confidence (<0.70).
    """
    w_ocr = 0.40
    w_pattern = 0.30
    w_keyword = 0.30

    score = (
        (ocr_conf * w_ocr)
        + (1.0 * w_pattern if pattern_matched else 0.2 * w_pattern)
        + (1.0 * w_keyword if keyword_present else 0.3 * w_keyword)
    )

    # Bonus/Penalty based on math consistency
    if arithmetic_valid is True:
        score = min(score + 0.15, 1.0)
    elif arithmetic_valid is False:
        score = max(score - 0.25, 0.20)

    final_score = round(min(max(score, 0.0), 1.0), 2)

    return {
        "confidence": final_score,
        "is_low_confidence": bool(final_score < threshold),
    }
