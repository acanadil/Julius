import cv2
import numpy as np
import os
from pdf2image import convert_from_path
import time

def pdf_to_image(pdf_path):
    """Convert the first page of a PDF to an image."""
    try:
        page = convert_from_path(pdf_path, dpi=300)[0]
        temp_path = "temp_document_image.png"
        page.save(temp_path, "PNG")
        return temp_path
    except Exception as e:
        raise ValueError(f"Failed to convert PDF {pdf_path}: {str(e)}")

def preprocess_signature(img, margin=2):
    # Check for valid input
    if img is None or img.size == 0:
        raise ValueError("Input image is empty")

    # Optional: Upscale small images for better processing
    min_dim = min(img.shape[:2])
    if min_dim < 100:
        xx = 1
        #img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # Enhance contrast and reduce noise
    img_eq = cv2.equalizeHist(img)
    blurred = cv2.GaussianBlur(img_eq, (5, 5), 0)

    # Create binary image with adaptive thresholding
    thresh = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Compute projections (count white pixels)
    col_sums = np.sum(thresh == 255, axis=0)  # Sum along columns
    row_sums = np.sum(thresh == 255, axis=1)  # Sum along rows

    # Find maximum sums for adaptive thresholding
    max_col_sum = np.max(col_sums)
    max_row_sum = np.max(row_sums)

    # Set threshold as 10% of max sum, with a minimum of 1 pixel
    col_threshold = max(1, 0.1 * max_col_sum)
    row_threshold = max(1, 0.1 * max_row_sum)

    # Find signature boundaries
    cols_above = np.where(col_sums > col_threshold)[0]
    rows_above = np.where(row_sums > row_threshold)[0]

    # Check if signature was detected
    if len(cols_above) == 0 or len(rows_above) == 0:
        raise ValueError("No significant signature area found")

    left = cols_above[0]
    right = cols_above[-1]
    top = rows_above[0]
    bottom = rows_above[-1]

    # Apply margin, ensuring we stay within image bounds
    x = max(0, left - margin)
    y = max(0, top - margin)
    w = min(right - left + 1 + 2 * margin, img.shape[1] - x)
    h = min(bottom - top + 1 + 2 * margin, img.shape[0] - y)

    # Crop the original image
    cropped = img[y:y+h, x:x+w]
    cropped = cv2.resize(cropped, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    if cropped.size == 0:
        raise ValueError("Resulting crop is empty")

    return cropped


def extract_signature(image_path, crop_coords, passport=False):
    """Extract a signature from an image using given coordinates."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    x, y, w, h = crop_coords
    x_end = min(x + w, img.shape[1])
    y_end = min(y + h, img.shape[0])
    
    if x >= x_end or y >= y_end:
        raise ValueError("Crop coordinates out of bounds")
    
    signature = img[y:y_end, x:x_end]
    processed = preprocess_signature(signature)
    return processed

def resize_images_to_same_size(img1, img2):
    """Resize the smaller image to match the size of the larger image."""
    h1, w1 = img1.shape
    h2, w2 = img2.shape

    if (h1, w1) != (h2, w2):
        # Resize the smaller image to match the larger one
        if h1 * w1 > h2 * w2:
            img2 = cv2.resize(img2, (w1, h1))  # Resize img2 to match img1
        else:
            img1 = cv2.resize(img1, (w2, h2))  # Resize img1 to match img2
    
    return img1, img2

def compare_signatures_sift(sig1, sig2, ratio_threshold=0.75):
    """Compare two signatures using SIFT and return a normalized score."""
    # Ensure grayscale
    if len(sig1.shape) > 2:
        sig1 = cv2.cvtColor(sig1, cv2.COLOR_BGR2GRAY)
    if len(sig2.shape) > 2:
        sig2 = cv2.cvtColor(sig2, cv2.COLOR_BGR2GRAY)
        
    sig1, sig2 = resize_images_to_same_size(sig1, sig2)
    cv2.imwrite("s1.png", sig1)
    quit()
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    
    # Detect keypoints and compute descriptors
    kp1, des1 = sift.detectAndCompute(sig1, None)
    kp2, des2 = sift.detectAndCompute(sig2, None)
    
    # Check for valid descriptors
    if des1 is None or des2 is None or des1.shape[0] == 0 or des2.shape[0] == 0:
        print("No valid descriptors found in one or both signatures.")
        return 0.0, 0
    
    # Initialize brute-force matcher
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    
    try:
        # Find k-nearest matches
        matches = bf.knnMatch(des1, des2, k=2)
        
        # Apply ratio test
        good_matches = [m for m, n in matches if m.distance < ratio_threshold * n.distance]
        
        # Compute scores
        raw_score = len(good_matches)
        norm_score = (raw_score / min(len(kp1), len(kp2))) * 100 if min(len(kp1), len(kp2)) > 0 else 0.0
        
        return norm_score, raw_score
    
    except cv2.error as e:
        print(f"SIFT matching failed: {str(e)}")
        return 0.0, 0

def main():
    data_dir = "data_files"
    # Find pairs of PNG and PDF files with the same base name
    files = {fname.split(".")[0] for fname in os.listdir(data_dir) if fname.endswith((".png", ".pdf"))}
    
    for base_name in files:
        png_path = os.path.join(data_dir, f"{base_name}.png")
        pdf_path = os.path.join(data_dir, f"{base_name}.pdf")
        
        # Check if both files exist
        if not (os.path.exists(png_path) and os.path.exists(pdf_path)):
            print(f"Skipping {base_name}: Missing PNG or PDF")
            continue
        
        try:
            # Convert PDF to image
            document_img_path = pdf_to_image(pdf_path)
            
            # Extract signatures with predefined crop coordinates
            # Using your original coordinates
            sig_passport = extract_signature(png_path, (260, 210, 120, 40), True)
            sig_document = extract_signature(document_img_path, (300, 2430, 730, 160))
            
            # Compare signatures using SIFT
            norm_score, raw_score = compare_signatures_sift(sig_passport, sig_document)
            
            # Output results
            print(f"{base_name}: Normalized Score: {norm_score:.2f}% ({raw_score} matches)")
            print("="*40)
            
            # Clean up temporary image
            if os.path.exists(document_img_path):
                os.remove(document_img_path)
                
        except Exception as e:
            print(f"Error processing {base_name}: {str(e)}")
            print("="*40)

if __name__ == "__main__":
    main()