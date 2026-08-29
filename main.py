import json
from pathlib import Path
from tqdm import tqdm
from src.preprocess import preprocess_image
from src.ocr_engine import OCREngine
from src.extractor import extract_receipt_fields
from src.summary import generate_expense_summary

# Directories
input_dir = Path("Data/receipts")
json_out_dir = Path("outputs/json")
raw_ocr_out_file = "outputs/raw_ocr_results.json"
summary_out_file = "outputs/expense_summary.json"

json_out_dir.mkdir(parents=True, exist_ok=True)
Path("outputs").mkdir(parents=True, exist_ok=True)

# Gather images
image_extensions = ("*.png", "*.jpg")
image_paths = []
for ext in image_extensions:
    image_paths.extend(input_dir.glob(ext))

print(f"Total receipt images found: {len(image_paths)}")

# Initialize OCR engine
ocr_engine = OCREngine()
all_parsed_data = []
all_raw_ocr_data = {}

# Process all images
for img_path in tqdm(image_paths, desc="Processing receipts"):
    # Preprocess
    preprocessed_img = preprocess_image(str(img_path))
    target = preprocessed_img if preprocessed_img is not None else str(img_path)

    # OCR Extraction
    ocr_lines = ocr_engine.extract(target)
    all_raw_ocr_data[img_path.name] = ocr_lines

    # Field Parsing & Confidence Scoring
    parsed = extract_receipt_fields(ocr_lines)
    all_parsed_data.append(parsed)

    # Save Individual Receipt JSON
    out_file = json_out_dir / f"{img_path.stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)

# Save the raw OCR data cache
with open(raw_ocr_out_file, "w", encoding="utf-8") as f:
    json.dump(all_raw_ocr_data, f, indent=2, ensure_ascii=False)
print(f"Raw OCR results saved to: {raw_ocr_out_file}")

# Generate Overall Financial Summary
summary = generate_expense_summary(all_parsed_data, summary_out_file)
print("\nProcessing Complete!")
print(f"Expense Summary saved to: {summary_out_file}")
print(json.dumps(summary, indent=2))
