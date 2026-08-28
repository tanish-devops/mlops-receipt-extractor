from paddleocr import PaddleOCR
import numpy as np


class OCREngine:
    def __init__(self):
        self.ocr = PaddleOCR(
            use_angle_cls=False,
            lang="en",
            use_gpu=False,
            enable_mkldnn=True,
            show_log=False,
        )

    def extract(self, img_input):
        # Accepts file path string or numpy array
        results = self.ocr.ocr(img_input, cls=False)
        extracted = []
        if results and results[0]:
            for line in results[0]:
                extracted.append(
                    {
                        "box": line[0],
                        "text": line[1][0],
                        "confidence": float(line[1][1]),
                    }
                )
        return extracted
