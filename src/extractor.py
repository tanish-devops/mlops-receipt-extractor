import re
from src.confidence import compute_field_confidence

DATE_REGEX = r"(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}\b)"
PRICE_REGEX = r"(\$?\d+\.\d{2})"
TOTAL_KEYWORDS = [
    "total",
    "grand total",
    "amount due",
    "balance due",
    "net amount",
    "total usd",
    "total:",
]
SUBTOTAL_KEYWORDS = ["subtotal", "sub total", "net sales"]
DISALLOWED_STORE_KEYWORDS = [
    "survey",
    "feedback",
    "chance to win",
    "win $",
    "welcome",
    "tax invoice",
    "simplified",
    "customer copy",
    "thank you",
    "id#",
    "mgr:",
    "manager",
    "store#",
    "www.",
    ".com",
]


def clean_name(name: str) -> str:
    if not name:
        return "Unknown"
    cleaned = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", name)
    return re.sub(r"\s+", " ", cleaned).strip()


def extract_receipt_fields(ocr_lines: list) -> dict:
    if not ocr_lines:
        return {
            "store_name": {
                "value": "Unknown",
                "confidence": 0.0,
                "is_low_confidence": True,
            },
            "date": {"value": None, "confidence": 0.0, "is_low_confidence": True},
            "items": [],
            "total_amount": {
                "value": None,
                "confidence": 0.0,
                "is_low_confidence": True,
            },
        }

    # 1. STORE NAME
    store_name = "Unknown Store"
    raw_store_conf = 0.5
    for line in ocr_lines[:8]:
        txt = line["text"].strip()
        txt_lower = txt.lower()
        if len(txt) < 3 or txt.isdigit():
            continue
        if any(kw in txt_lower for kw in DISALLOWED_STORE_KEYWORDS):
            continue
        store_name = clean_name(txt)
        raw_store_conf = line["confidence"]
        break

    store_eval = compute_field_confidence(
        raw_store_conf, pattern_matched=True, keyword_present=True
    )

    # 2. DATE
    date_val, date_conf = None, 0.0
    for line in ocr_lines:
        match = re.search(DATE_REGEX, line["text"])
        if match:
            date_val = match.group(0)
            date_conf = line["confidence"]
            break
    date_eval = compute_field_confidence(
        date_conf, pattern_matched=(date_val is not None), keyword_present=True
    )

    # 3. LINE ITEMS & PRICES
    items = []
    price_lines, text_lines = [], []

    for line in ocr_lines:
        box = line["box"]
        y_center = (box[0][1] + box[2][1]) / 2.0
        x_min = min(pt[0] for pt in box)

        match = re.search(PRICE_REGEX, line["text"])
        if match and x_min > 200:
            clean_p = re.sub(r"[^\d.]", "", match.group(0))
            try:
                price_lines.append({"price": float(clean_p), "y": y_center})
            except ValueError:
                pass
        else:
            txt_lower = line["text"].lower()
            if not any(
                kw in txt_lower
                for kw in TOTAL_KEYWORDS
                + SUBTOTAL_KEYWORDS
                + ["tax", "cash", "change", "approved"]
            ):
                text_lines.append({"name": line["text"], "y": y_center})

    for pl in price_lines:
        closest_text = None
        min_dist = 25.0
        for tl in text_lines:
            dist = abs(tl["y"] - pl["y"])
            if dist < min_dist:
                min_dist = dist
                closest_text = tl["name"]
        if closest_text and len(closest_text) > 2:
            items.append({"name": clean_name(closest_text), "price": str(pl["price"])})

    # 4. TOTAL AMOUNT (with Conflict Resolution for Subtotal vs Total)
    total_val, total_conf, keyword_matched = None, 0.0, False

    # Priority: Grand Total > Total > Subtotal
    for kw_list in [TOTAL_KEYWORDS, SUBTOTAL_KEYWORDS]:
        for i, line in enumerate(ocr_lines):
            txt_lower = line["text"].lower()
            if any(kw in txt_lower for kw in kw_list):
                match = re.search(PRICE_REGEX, line["text"])
                if match:
                    total_val = float(re.sub(r"[^\d.]", "", match.group(0)))
                    total_conf = line["confidence"]
                    keyword_matched = True
                    break
                elif i + 1 < len(ocr_lines):
                    next_match = re.search(PRICE_REGEX, ocr_lines[i + 1]["text"])
                    if next_match:
                        total_val = float(re.sub(r"[^\d.]", "", next_match.group(0)))
                        total_conf = ocr_lines[i + 1]["confidence"]
                        keyword_matched = True
                        break
        if total_val is not None:
            break

    # Fallback to max price
    if total_val is None:
        all_prices = []
        for line in ocr_lines:
            match = re.search(PRICE_REGEX, line["text"])
            if match:
                try:
                    p = float(re.sub(r"[^\d.]", "", match.group(0)))
                    all_prices.append((p, line["confidence"]))
                except ValueError:
                    pass
        if all_prices:
            total_val, total_conf = max(all_prices, key=lambda x: x[0])

    # 5. ARITHMETIC CROSS-VALIDATION
    sum_items = sum(float(it["price"]) for it in items) if items else 0.0
    arithmetic_valid = None
    if total_val is not None and sum_items > 0:
        # Check if items sum is roughly equal to total (allowing for taxes)
        arithmetic_valid = bool(
            abs(total_val - sum_items) < 2.0 or sum_items <= total_val
        )

    total_eval = compute_field_confidence(
        total_conf,
        pattern_matched=(total_val is not None),
        keyword_present=keyword_matched,
        arithmetic_valid=arithmetic_valid,
    )

    return {
        "store_name": {
            "value": store_name,
            "confidence": store_eval["confidence"],
            "is_low_confidence": store_eval["is_low_confidence"],
        },
        "date": {
            "value": date_val,
            "confidence": date_eval["confidence"],
            "is_low_confidence": date_eval["is_low_confidence"],
        },
        "items": items,
        "total_amount": {
            "value": total_val,
            "confidence": total_eval["confidence"],
            "is_low_confidence": total_eval["is_low_confidence"],
        },
    }
