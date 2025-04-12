import cv2
import numpy as np
import os
from pdf2image import convert_from_path

def pdf_to_image(pdf_path):
    """Convert the first page of a PDF to an image."""
    try:
        page = convert_from_path(pdf_path, dpi=300)[0]
        temp_path = "temp_document_image.png"
        page.save(temp_path, "PNG")
        return temp_path
    except Exception as e:
        raise ValueError(f"Failed to convert PDF {pdf_path}: {str(e)}")

def preprocess_signature(img, margin=10, min_area=50):
    """Preprocess a signature image."""
    if img is None or img.size == 0:
        return None

    img_eq = cv2.equalizeHist(img)
    blurred = cv2.GaussianBlur(img_eq, (3, 3), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 35, 6)

    thresh = cv2.dilate(thresh, np.ones((2,2), np.uint8), iterations=1)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > min_area]

    if not contours:
        print("Warning: No significant contours found in preprocess. Returning blurred image.")
        return blurred

    x, y, w, h = cv2.boundingRect(np.concatenate(contours))
    x, y = max(0, x - margin), max(0, y - margin)
    cropped = img[y:y+h+margin, x:x+w+margin]

    if cropped.size == 0:
        print("Warning: Empty crop in preprocess. Returning blurred image.")
        return blurred

    return cropped

def crop(img):
    """Crop tightly to black writing, minimizing white space."""
    if img is None or img.size == 0:
        print("Warning: Empty image in crop. Returning None.")
        return None

    blurred = cv2.GaussianBlur(img, (3, 3), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 5)

    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    coords = np.column_stack(np.where(cleaned > 0))

    if coords.size == 0:
        print("Warning: No black pixels found in crop. Returning blurred image.")
        return blurred

    x, y, w, h = cv2.boundingRect(coords)
    margin = 30
    x, y = max(0, x - margin), max(0, y - margin)
    w, h = w + 2 * margin, h + 2 * margin

    h_img, w_img = img.shape
    x_end = min(x + w, w_img)
    y_end = min(y + h, h_img)
    x = min(x, w_img - 1)
    y = min(y, h_img - 1)

    if x >= x_end or y >= y_end:
        print("Warning: Invalid crop bounds. Returning blurred image.")
        return blurred

    cropped = img[y:y_end, x:x_end]

    if cropped.size == 0:
        print("Warning: Empty crop after bounds check. Returning blurred image.")
        return blurred

    return cropped


def normalize_size(sig, target_size=(120, 40)):
    """Resize image to target size with padding."""
    if sig is None or sig.size == 0:
        return None

    h, w = sig.shape
    target_w, target_h = target_size
    scale = min(target_w / w, target_h / h)

    new_w, new_h = int(w * scale), int(h * scale)
    if new_w <= 0 or new_h <= 0:
        return None

    resized = cv2.resize(sig, (new_w, new_h), interpolation=cv2.INTER_AREA)

    pad_top = (target_h - new_h) // 2
    pad_bottom = target_h - new_h - pad_top
    pad_left = (target_w - new_w) // 2
    pad_right = target_w - new_w - pad_left

    padded = cv2.copyMakeBorder(resized, pad_top, pad_bottom, pad_left, pad_right,
                                cv2.BORDER_CONSTANT, value=255)
    return padded

def compare_signatures(sig1, sig2, ratio_threshold=0.75):
    """Compare two signatures using SIFT with normalized score."""
    if sig1 is None or sig2 is None:
        print("One or both images are invalid.")
        return 0.0, 0

    s1 = normalize_size(sig1, target_size=(120, 40))
    s2 = normalize_size(sig2, target_size=(120, 40))

    cv2.imwrite("s1.png", s2)
    quit()

    if s1 is None or s2 is None:
        print("Normalization failed for one or both signatures.")
        return 0.0, 0

    output_dir = "data_files/signatures"
    os.makedirs(output_dir, exist_ok=True)
    global save_base_name
    cv2.imwrite(os.path.join(output_dir, f"{save_base_name}_passport_sig.png"), s1)
    cv2.imwrite(os.path.join(output_dir, f"{save_base_name}_document_sig.png"), s2)
    print(f"Saved signatures to {output_dir}/{save_base_name}_*.png")

    sift = cv2.SIFT_create(contrastThreshold=0.06)
    kp1, des1 = sift.detectAndCompute(s1, None)
    kp2, des2 = sift.detectAndCompute(s2, None)

    if des1 is None or des2 is None or des1.shape[0] == 0 or des2.shape[0] == 0:
        print("No valid descriptors found in one or both signatures.")
        return 0.0, 0

    print(f"Descriptors for passport: {des1.shape[0]}")
    print(f"Descriptors for document: {des2.shape[0]}")

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    try:
        matches = bf.knnMatch(des1, des2, k=2)
        good_matches = [m for m, n in matches if m.distance < ratio_threshold * n.distance]
        raw_score = len(good_matches)
        norm_score = (raw_score / min(len(kp1), len(kp2))) * 100 if min(len(kp1), len(kp2)) > 0 else 0.0
        print(f"Raw matches: {raw_score}, Normalized score: {norm_score:.2f}%")
        return norm_score, raw_score
    except cv2.error as e:
        print(f"SIFT matching failed: {str(e)}")
        return 0.0, 0

def extract_signature(image_path, crop_coords):
    """Extract a signature with validated cropping."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")

    h_img, w_img = img.shape
    x, y, w, h = crop_coords

    if x + w > w_img or y + h > h_img:
        print(f"Warning: Crop {crop_coords} exceeds image size ({w_img}, {h_img}). Adjusting...")
        x = min(x, w_img - 1)
        y = min(y, h_img - 1)
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        if w <= 0 or h <= 0:
            print("Warning: Invalid crop adjusted. Using full image.")
            return preprocess_signature(img)

    x_end = x + w
    y_end = y + h

    if x >= x_end or y >= y_end:
        print("Warning: Invalid crop coordinates. Using full image.")
        return preprocess_signature(img)

    signature = img[y:y_end, x:x_end]
    processed = preprocess_signature(signature)
    return processed

def main(passport_path, document_pdf_path):
    """Process and compare signatures from a PNG and PDF."""
    global save_base_name
    save_base_name = os.path.basename(passport_path).split(".")[0]

    try:
        document_img_path = pdf_to_image(document_pdf_path)
        sig_passport = extract_signature(passport_path, (260, 210, 120, 40))
        sig_document = extract_signature(document_img_path, (300, 2430, 730, 160))

        sig_passport_aligned = crop(sig_passport)
        sig_document_aligned = crop(sig_document)

        norm_score, raw_score = compare_signatures(sig_passport_aligned, sig_document_aligned)
        print(f"Combined Score: {norm_score:.2f}% ({raw_score} matches)")
        return norm_score > 20.0
    except Exception as e:
        print(f"Verification failed: {str(e)}")
        return False
    finally:
        if 'document_img_path' in locals() and os.path.exists(document_img_path):
            os.remove(document_img_path)

if __name__ == "__main__":
    data_dir = "data_files"
    files = {fname.split(".")[0] for fname in os.listdir(data_dir) if fname.endswith((".png", ".pdf"))}

    for file in files:
        passport_path = os.path.join(data_dir, f"{file}.png")
        document_path = os.path.join(data_dir, f"{file}.pdf")

        if not (os.path.exists(passport_path) and os.path.exists(document_path)):
            print(f"Skipping {file}: Missing PNG or PDF")
            continue

        print(f"Processing {file}")
        result = main(passport_path, document_path)
        print(f"{file}: {'MATCH' if result else 'NO MATCH'}")
        print("="*40)
