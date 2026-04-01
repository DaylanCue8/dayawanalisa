import cv2
import numpy as np
import joblib
import mysql.connector
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.feature import hog
from tagalog_to_baybayin import TagalogToBaybayin

app = Flask(__name__)
CORS(app)

ttb_translator = TagalogToBaybayin()

# --- 1. LOAD AI ASSETS ---
# Ensure these .pkl files are in the same folder as this script!
try:
    model = joblib.load('baybayin_svm_model.pkl')
    scaler = joblib.load('baybayin_scaler.pkl')
    class_names = joblib.load('baybayin_classes.pkl')
    print(f"✅ AI System Online. Loaded {len(class_names)} classes.")
except Exception as e:
    print(f"❌ Critical Error: Could not load AI files. {e}")
    model, scaler, class_names = None, None, []

# --- 2. DATABASE CONFIG ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'dayaw' 
}

# --- 3. DATABASE HELPERS ---

def start_processing_session(ip_address):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO processing_sessions (status, ip_address) VALUES ('Processing', %s)"
        cursor.execute(query, (ip_address,))
        new_id = cursor.lastrowid 
        conn.commit()
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"❌ DB Session Error: {e}")
        return 0

def log_detections(session_id, detections_list):
    if not detections_list or session_id == 0: return
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        formatted_logs = [(session_id, d['char'], d['confidence']) for d in detections_list]
        query = "INSERT INTO detection_logs (session_id, detected_char, confidence_score) VALUES (%s, %s, %s)"
        cursor.executemany(query, formatted_logs)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Log Error: {e}")

def update_session_status(session_id, status):
    if session_id == 0: return
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "UPDATE processing_sessions SET status = %s, end_time = CURRENT_TIMESTAMP WHERE session_id = %s"
        cursor.execute(query, (status, session_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Update Error: {e}")

# --- 4. IMAGE PROCESSING ENGINE ---

def preprocess_and_predict(image_bytes):
    # Convert bytes to OpenCV image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return "Error", 0.0, []

    # --- STEP A: PRE-PROCESSING (1.2x Zoom) ---
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- STEP B: SHADOW FIXER & BINARIZATION (21, 15) ---
    bg_img = cv2.medianBlur(gray, 51)
    normalized = cv2.divide(gray, bg_img, scale=255)
    binary = cv2.adaptiveThreshold(normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 21, 15)

    # --- STEP C: CLEANING (The "NA" & Gap Fix) ---
    # Synced with Colab: 7x7 Morphological Closing to glue strokes together
    kernel = np.ones((7,7), np.uint8) 
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.dilate(binary, kernel, iterations=1) 
    binary = cv2.medianBlur(binary, 5)

    # --- STEP D: SEGMENTATION ---
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    raw_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # Filter noise fragments (Synced with Colab 40x40 threshold)
        if w > 40 and h > 40:
            raw_boxes.append([x, y, w, h])

    if not raw_boxes:
        return "No characters detected", 0.0, []

    # --- STEP E: MULTI-LINE & LEFT-TO-RIGHT SORTING (Centroid Math) ---
    # Sort by Vertical Center: y + (h/2)
    raw_boxes.sort(key=lambda b: b[1] + b[3]/2)

    lines = []
    curr_line = [raw_boxes[0]]
    line_threshold = 80 # Adjust based on how close your lines are written

    for i in range(1, len(raw_boxes)):
        prev_y_center = curr_line[-1][1] + curr_line[-1][3]/2
        curr_y_center = raw_boxes[i][1] + raw_boxes[i][3]/2
        
        if abs(curr_y_center - prev_y_center) < line_threshold:
            curr_line.append(raw_boxes[i])
        else:
            curr_line.sort(key=lambda b: b[0]) # Sort finished line Left-to-Right
            lines.append(curr_line)
            curr_line = [raw_boxes[i]]
            
    curr_line.sort(key=lambda b: b[0])
    lines.append(curr_line)

    # --- STEP F: PREDICTION LOOP ---
    full_sentence_text = []
    confidences = []
    detections = []

    for line in lines:
        line_chars = []
        for box in line:
            x, y, w, h = box
            roi = binary[y:y+h, x:x+w]
            resized = cv2.resize(roi, (42, 42), interpolation=cv2.INTER_AREA)

            # Feature Extraction
            fd = hog(resized, orientations=9, pixels_per_cell=(8, 8),
                     cells_per_block=(2, 2), visualize=False)

            # SVM Prediction
            scaled_fd = scaler.transform(fd.reshape(1, -1))
            probs = model.predict_proba(scaled_fd)[0]
            best_idx = np.argmax(probs)
            
            char = class_names[best_idx]
            conf = float(probs[best_idx])

            # Store results
            line_chars.append(char)
            confidences.append(conf)
            detections.append({"char": char, "confidence": round(conf * 100, 2)})
        
        full_sentence_text.append("-".join(line_chars))

    # Join lines with a space or newline for final output
    word_text = " | ".join(full_sentence_text) 
    avg_conf = (np.mean(confidences) * 100) if confidences else 0
    
    return word_text, round(avg_conf, 2), detections

# --- NEW: LINGUISTIC SCORER FOR TTB ---
def calculate_linguistic_confidence(text):
    """
    Calculates a 'Learning Score' based on traditional Baybayin rules.
    - Foreign letters (C, F, J, Q, V, X, Z) are penalized.
    - Modern 'R' is penalized (traditionally used 'D').
    """
    original_text = text.lower()
    score = 100.0
    
    # 1. Identify Foreign Characters that don't exist in Baybayin
    # Each foreign character reduces confidence by 15%
    foreign_matches = re.findall(r'[cfjqzvx]', original_text)
    score -= (len(foreign_matches) * 15)
    
    # 2. Check for 'R'
    # Traditional Baybayin didn't have 'R'; it used the 'D' character (Ra/Da)
    if 'r' in original_text:
        score -= 5
        
    # Ensure score doesn't go below 0
    return max(0.0, float(score))

# --- 6. API ROUTES ---

@app.route('/api/translate', methods=['POST'])
def translate():
    session_id = start_processing_session(request.remote_addr)
    
    # Handle both Form Data (Mobile) and JSON (Web/Postman)
    if request.is_json:
        data = request.json
        mode = data.get('mode')
        input_text = data.get('text')
    else:
        mode = request.form.get('mode')
        input_text = request.form.get('text')

    try:
        # --- MODE 1: BAYBAYIN TO TAGALOG (OCR) ---
        if mode == 'Baybayin to Tagalog':
            if 'file' not in request.files:
                update_session_status(session_id, 'No_File')
                return jsonify({"error": "No image uploaded"}), 400
            
            image_bytes = request.files['file'].read()
            text, conf, results = preprocess_and_predict(image_bytes)
            
            log_detections(session_id, results)
            status = "Success" if conf > 60 else "Low_Confidence"
            update_session_status(session_id, status)

            return jsonify({
                "translated_text": text,
                "confidence": conf,
                "status": status,
                "individual_detections": results,
                "session_id": session_id
            })

        # --- MODE 2: TAGALOG TO BAYBAYIN (TTB Focus) ---
        elif mode == 'Tagalog to Baybayin':
            if not input_text:
                update_session_status(session_id, 'No_Text')
                return jsonify({"error": "No text provided"}), 400
            
            # 1. Perform Transliteration 
            # (Now correctly unpacking the tuple returned by the class)
            translated_result, confidence = ttb_translator.translate(input_text)
            
            # 2. Determine status based on the confidence score calculated in the class
            status = "Success" if confidence >= 80 else "Incompatible_Chars"
            
            update_session_status(session_id, status)
            
            return jsonify({
                "translated_text": translated_result,
                "confidence": confidence,
                "status": status,
                "session_id": session_id,
                "is_native": confidence == 100.0
            })

    except Exception as e:
        update_session_status(session_id, 'Error')
        print(f"❌ Route Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use port 5000 as defined in your VS Code setup
    app.run(host='0.0.0.0', port=5000, debug=True)