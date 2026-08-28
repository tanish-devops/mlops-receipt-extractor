import cv2
import numpy as np


def deskew_image(image: np.ndarray) -> np.ndarray:
    """Detects text orientation angle and straightens the receipt."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    elif angle > 45:
        angle = 90 - angle
    else:
        angle = -angle

    # Rotate only if skew is noticeable
    if abs(angle) > 0.5 and abs(angle) < 45.0:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    return image


def preprocess_image(image_path: str) -> np.ndarray:
    """Enhances contrast, normalizes lighting, and deskews the receipt image."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    # Deskew
    straightened = deskew_image(image)

    # Grayscale
    gray = cv2.cvtColor(straightened, cv2.COLOR_BGR2GRAY)

    # CLAHE for uneven lighting
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Denoising
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)

    return denoised
