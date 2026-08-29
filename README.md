Receipt OCR and Expense Extraction Pipeline

Project Overview:
This project is built to process scanned and mobile-captured receipt images containing noise, lighting issues, and varied layouts.
The pipeline performs:
```bash

1.Image Preprocessing: Straightens tilted images (deskewing), removes image noise, and enhances contrast.
1.Text Extraction (OCR): Uses PaddleOCR to read text, polygon bounding boxes, and detection confidence scores.
2.Key Field Extraction: Extracts merchant name, transaction date, line items with prices, and grand total.
3.Confidence & Reliability Scoring: Combines OCR scores with regex pattern validation, keyword heuristics,
and math cross-validation to assign a score ($0.0$ to $1.0$) and flag low-confidence values ($< 0.70$).
4.Financial Summary: Aggregates total spend, counts transactions, and merges similar store names using fuzzy matching
```

```bash
receipt-ocr-pipeline/
├── data/
│   └── receipts/               # Raw receipt images (.png, .jpg)
├── outputs/
│   ├── json/                   # Extracted JSON for each individual receipt
│   ├── raw_ocr_results.json    # Cached OCR bounding boxes and text
│   └── expense_summary.json    # Final spending summary across all receipts
├── src/
│   ├── __init__.py             # Module initialization
│   ├── preprocess.py           # Deskewing, CLAHE, and noise filtering
│   ├── ocr_engine.py           # PaddleOCR runner
│   ├── confidence.py           # Composite confidence scoring and flag logic
│   ├── extractor.py            # Field parsing (Store, Date, Items, Total)
│   └── summary.py              # Spend aggregation and fuzzy store deduplication
├── main.py                     # Full pipeline runner (Images -> OCR -> JSONs -> Summary)
├── fast_parse.py               # Fast parser (Uses cached OCR results -> Instant JSONs)
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```


Tech Stack & ToolsProgramming Language:
```bash
Python
Computer Vision: OpenCV (cv2), NumPy
OCR Framework: PaddleOCR
Data Processing & Utilities: re (Regular Expressions), difflib, tqdm, json
```

Setup & Installation-


```bash
#Clone the repository
git clone https://github.com/tanish-devops/mlops-receipt-extractor.git
cd mlops-receipt-extractor

#Create a virtual environment
python -m venv myenv
# Activate on Windows:
myenv\Scripts\activate
# Activate on Linux/macOS:
source myenv/bin/activate

#Install dependencies
pip install -r requirements.txt

```

to Run this

```bash
#Fast Run(for testing)
python fast_parse.py

#for Full Pipeline Run
python main.py

```

# Financial Summary
```bash

{
  "total_spend": $23734.97,
  "number_of_transactions": 371,
  "low_confidence_transactions_count": 25,
  "top3_stores_spending": {
    "SYARIKAT PERNIAGAAN GIN KEE": 1748.04,
    "KEDAI PAPAN YEW CHUAN": 1131.0,
    "PERNIAGAAN ZHENG HUI": 857.45,
  }
}
```
# Future Improvements
Adding GPU batching for faster large-scale OCR processing.

Adding multi-currency detection and automatic currency conversion.

Integrating deep-learning document understanding models (like LayoutLM) for irregular receipt tables.


>>💡 **Open for suggestions!** If you have ideas to improve this setup, feel free to open an issue or a pull request.
