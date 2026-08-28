import json
import re
import difflib
from collections import defaultdict
from pathlib import Path


def canonicalize_store_name(
    name: str, existing_names: list, threshold: float = 0.82
) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", name).strip().upper()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("SDN BHD", "SDN BHD").replace("SDNBHD", "SDN BHD")

    for existing in existing_names:
        if difflib.SequenceMatcher(None, cleaned, existing).ratio() >= threshold:
            return existing
    return cleaned


def generate_expense_summary(parsed_receipts: list, output_file: str):
    total_spend = 0.0
    valid_transactions = 0
    low_confidence_transactions = 0
    spend_per_store = defaultdict(float)
    known_stores = []

    for receipt in parsed_receipts:
        total_obj = receipt.get("total_amount", {})
        amt = total_obj.get("value")
        raw_store = receipt.get("store_name", {}).get("value") or "UNKNOWN"

        if total_obj.get("is_low_confidence", False):
            low_confidence_transactions += 1

        if amt is not None:
            try:
                numeric_amt = float(amt)
                total_spend += numeric_amt
                valid_transactions += 1

                canon_store = canonicalize_store_name(raw_store, known_stores)
                if canon_store not in known_stores and canon_store != "UNKNOWN":
                    known_stores.append(canon_store)

                spend_per_store[canon_store] += numeric_amt
            except ValueError:
                continue

    summary = {
        "total_spend": round(total_spend, 2),
        "number_of_transactions": valid_transactions,
        "low_confidence_transactions_count": low_confidence_transactions,
        "spend_per_store": {
            k: round(v, 2)
            for k, v in sorted(
                spend_per_store.items(), key=lambda x: x[1], reverse=True
            )
        },
    }

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
