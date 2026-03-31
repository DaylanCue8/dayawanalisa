import cv2
import numpy as np
import joblib
import mysql.connector
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.feature import hog

app = Flask(__name__)
CORS(app)

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
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return "Error", 0.0, []

    # A. Pre-processing
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    

    # B. Shadow Fixer & Binarization
    bg_img = cv2.medianBlur(gray, 51)
    normalized = cv2.divide(gray, bg_img, scale=255)
    binary = cv2.adaptiveThreshold(normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 21, 15)

    # C. Cleaning
    binary = cv2.medianBlur(binary, 3)

    # D. Line-Aware Segmentation
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    raw_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 15 and h > 15:
            raw_boxes.append([x, y, w, h])

    if not raw_boxes:
        return "No characters detected", 0.0, []

    raw_boxes.sort(key=lambda b: b[1])
    lines = []
    curr_line = [raw_boxes[0]]
    for box in raw_boxes[1:]:
        if box[1] < curr_line[-1][1] + curr_line[-1][3] + 60:
            curr_line.append(box)
        else:
            curr_line.sort(key=lambda b: b[0])
            lines.append(curr_line)
            curr_line = [box]
    curr_line.sort(key=lambda b: b[0])
    lines.append(curr_line)

    full_word = []
    confidences = []
    detections = []

    # E. Prediction Loop
    for line_idx, line_boxes in enumerate(lines):
        i = 0
        while i < len(line_boxes):
            curr = line_boxes[i]
            
            # --- FIX 1: Merge fragmented strokes (NGA is often split) ---
            # Using 18px ensures the 'tail' of the NGA connects to the body
            if i + 1 < len(line_boxes):
                next_b = line_boxes[i+1]
                if next_b[0] - (curr[0] + curr[2]) < 18: 
                    nx, ny = min(curr[0], next_b[0]), min(curr[1], next_b[1])
                    nw = max(curr[0] + curr[2], next_b[0] + next_b[2]) - nx
                    nh = max(curr[1] + curr[3], next_b[1] + next_b[3]) - ny
                    curr = [nx, ny, nw, nh]
                    i += 1 

            roi = binary[curr[1]:curr[1]+curr[3], curr[0]:curr[0]+curr[2]]
            resized = cv2.resize(roi, (42, 42), interpolation=cv2.INTER_AREA)

            fd = hog(resized, orientations=9, pixels_per_cell=(8, 8),
                     cells_per_block=(2, 2), visualize=False)

            scaled_fd = scaler.transform(fd.reshape(1, -1))
            probs = model.predict_proba(scaled_fd)[0]
            best_idx = np.argmax(probs)
            char = class_names[best_idx]
            conf = float(probs[best_idx])

            # --- FIX 2: TARGETED THRESHOLD OVERRIDE ---
            # We know your NGA is hitting ~27-29%. 
            # We create a 'Rescue Zone' for NGA specifically.
            
            is_valid = False
            if char == "NGA" and conf > 0.25: # Lowered gate for NGA
                is_valid = True
            elif conf > 0.32: # Keep original strict gate for everything else
                is_valid = True

            # --- FIX 3: THE "EI" SECOND CHANCE ---
            # If the AI chose 'EI' with low confidence, but 'NGA' was the 2nd choice
            if char == "EI" and conf < 0.35:
                # Check if NGA is the second highest probability
                sorted_indices = np.argsort(probs)
                second_best_idx = sorted_indices[-2]
                if class_names[second_best_idx] == "NGA":
                    char = "NGA"
                    conf = float(probs[second_best_idx])
                    is_valid = True if conf > 0.25 else False

            if is_valid:
                full_word.append(char)
                confidences.append(conf)
                detections.append({"char": char, "confidence": round(conf * 100, 2)})
            
            i += 1

    word_text = "-".join(full_word)
    avg_conf = (np.mean(confidences) * 100) if confidences else 0
    return word_text, round(avg_conf, 2), detections

# --- 5. API ROUTES ---

@app.route('/api/translate', methods=['POST'])
def translate():
    session_id = start_processing_session(request.remote_addr)
    
    # Get mode from Form Data (Flutter often uses this) or JSON
    mode = request.form.get('mode') or (request.json.get('mode') if request.is_json else None)
    
    try:
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

        # Placeholder for Tagalog to Baybayin logic
        elif mode == 'Tagalog to Baybayin':
            return jsonify({"translated_text": "Feature coming soon", "status": "Success"})

    except Exception as e:
        update_session_status(session_id, 'Error')
        print(f"❌ Translate Route Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use port 5000 as defined in your VS Code setup
    app.run(host='0.0.0.0', port=5000, debug=True)