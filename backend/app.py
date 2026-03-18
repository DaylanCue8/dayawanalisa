import cv2
import numpy as np
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.feature import hog

app = Flask(__name__)
CORS(app)

# 1. LOAD MODEL & CONFIGURATION (Matches your Colab)
try:
    model = joblib.load('baybayin_svm_model.sav')
    # This list must be in the EXACT same order as your training folders
    class_names = ['A', 'BA', 'DARA', 'EI', 'GA', 'HA', 'KA', 'LA', 'MA', 'NA', 'NGA', 'OU', 'PA', 'SA', 'TA', 'WA', 'YA']
    print("✅ Model and Class Names loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")

def preprocess_and_predict(image_bytes):
    # Convert bytes to OpenCV image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return "Invalid Image"

    # --- STEP 1: UPSCALE (From your Colab: helps with thin ballpen lines) ---
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- STEP 2: DENOISING ---
    blurred = cv2.medianBlur(gray, 5)

    # --- STEP 3: ADAPTIVE THRESHOLDING ---
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # --- STEP 4: MORPHOLOGICAL HEALING (Fixes fragmented lines) ---
    kernel = np.ones((5,5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.dilate(binary, np.ones((3,3), np.uint8), iterations=1)

    # --- STEP 5: AREA FILTERING (Removes "dot" noise) ---
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    clean_binary = np.zeros_like(binary)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 800: # Matches your Colab filter
            clean_binary[labels == i] = 255

    # --- STEP 6: SEGMENTATION ---
    contours, _ = cv2.findContours(clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 50 and h > 50: 
            valid_boxes.append((x, y, w, h))

    # Sort Left-to-Right
    valid_boxes = sorted(valid_boxes, key=lambda b: b[0])
    
    full_word = []
    
    for (x, y, w, h) in valid_boxes:
        roi = clean_binary[y:y+h, x:x+w]

        # --- STEP 7: STANDARDIZE FOR SVM (Add padding then resize) ---
        padded = cv2.copyMakeBorder(roi, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=0)
        resized = cv2.resize(padded, (42, 42))

        # HOG Feature Extraction
        fd = hog(resized, orientations=9, pixels_per_cell=(8, 8), 
                 cells_per_block=(2, 2), visualize=False)
        
        # Prediction
        pred_idx = model.predict([fd])[0]
        
        # Map index to class name
        char = class_names[pred_idx]
        full_word.append(char)
        
        print(f"Detected: {char} (Index: {pred_idx})")

    return "".join(full_word)

@app.route('/api/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'Default')
    
    try:
        image_bytes = file.read()
        translated_text = preprocess_and_predict(image_bytes)
        
        return jsonify({
            "translated_text": translated_text if translated_text else "No text detected",
            "status": "success"
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)