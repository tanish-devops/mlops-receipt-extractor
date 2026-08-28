import json
from pathlib import Path
from tqdm import tqdm
from src.preprocess import preprocess_image
from src.ocr_engine import OCREngine
from src.extractor import extract_receipt_fields
from src.summary import generate_expense_summary

# 1. Directories
input_dir = Path("Data/receipts")
json_out_dir = Path("outputs/json")
summary_out_file = "outputs/expense_summary.json"

json_out_dir.mkdir(parents=True, exist_ok=True)

# 2. Gather images
image_extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp")
image_paths = []
for ext in image_extensions:
    image_paths.extend(input_dir.glob(ext))

print(f"Total receipt images found: {len(image_paths)}")

# 3. Initialize OCR engine
ocr_engine = OCREngine()
all_parsed_data = []

# 4. Process all images
for img_path in tqdm(image_paths, desc="Processing receipts"):
    # Step A: Preprocess
    preprocessed_img = preprocess_image(str(img_path))
    target = preprocessed_img if preprocessed_img is not None else str(img_path)

    # Step B: OCR Extraction
    ocr_lines = ocr_engine.extract(target)

    # Step C: Field Parsing & Confidence Scoring
    parsed = extract_receipt_fields(ocr_lines)
    all_parsed_data.append(parsed)

    # Step D: Save Individual Receipt JSON
    out_file = json_out_dir / f"{img_path.stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)

# 5. Generate Overall Financial Summary
summary = generate_expense_summary(all_parsed_data, summary_out_file)
print("\nProcessing Complete!")
print(f"Expense Summary saved to: {summary_out_file}")
print(json.dumps(summary, indent=2))
