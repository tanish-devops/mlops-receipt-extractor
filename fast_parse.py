import json
from pathlib import Path
from src.extractor import extract_receipt_fields
from src.summary import generate_expense_summary

json_out_dir = Path("outputs/json")
json_out_dir.mkdir(parents=True, exist_ok=True)

raw_ocr_file = Path("outputs/raw_ocr_results.json")

if not raw_ocr_file.exists():
    print(f"Error: {raw_ocr_file} not found!")
    print("Please run main.py first to generate the raw OCR results.")
    exit(1)

with open(raw_ocr_file, "r", encoding="utf-8") as f:
    raw_ocr_data = json.load(f)

all_parsed = []
for img_name, ocr_lines in raw_ocr_data.items():
    parsed = extract_receipt_fields(ocr_lines)
    all_parsed.append(parsed)

    out_file = json_out_dir / f"{Path(img_name).stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)

summary = generate_expense_summary(all_parsed, "outputs/expense_summary.json")
print(
    "Successfully generated all outputs with confidence flags, item arrays, and expense summary"
)
print(f"Total Transactions: {summary['number_of_transactions']}")
print(f"Total Spend: ${summary['total_spend']}")
