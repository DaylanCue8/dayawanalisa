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

# Load Translator module
try:
    from tagalog_to_baybayin import TagalogToBaybayin
    ttb_translator = TagalogToBaybayin()
except ImportError:
    ttb_translator = None

# --- 1. DATABASE CONFIG ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'dayaw' 
}

# --- 2. LOAD MODEL ---
try:
    model = joblib.load('baybayin_svm_model.sav')
    class_names = joblib.load('class_names.sav') 
    print(f"✅ Model loaded. Classes: {class_names}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    class_names = []

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

    # --- STEP 0: UPSCALE ---
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- STEP 1: NOISE REDUCTION ---
    blurred = cv2.medianBlur(gray, 5)

    # --- STEP 2: ADAPTIVE THRESHOLD ---
    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2   # <-- from Colab (important)
    )

    # --- STEP 3: MORPHOLOGICAL HEALING ---
    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.dilate(binary, np.ones((3, 3), np.uint8), iterations=1)

    # --- STEP 4: AREA FILTERING ---
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    clean_binary = np.zeros_like(binary)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 400:  # <-- from Colab
            clean_binary[labels == i] = 255

    # --- STEP 5: SEGMENTATION ---
    contours, _ = cv2.findContours(clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 25 and h > 25:  # <-- from Colab
            valid_boxes.append((x, y, w, h))

    valid_boxes = sorted(valid_boxes, key=lambda b: b[0])

    full_word = []
    confidences = []
    detections = []

    # --- STEP 6: PREDICTION ---
    for (x, y, w, h) in valid_boxes:
        roi = clean_binary[y:y+h, x:x+w]

        padded = cv2.copyMakeBorder(
            roi, 15, 15, 15, 15,
            cv2.BORDER_CONSTANT, value=0
        )

        resized = cv2.resize(padded, (42, 42))

        fd = hog(
            resized,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            visualize=False
        )

        probabilities = model.predict_proba([fd])[0]
        best_index = np.argmax(probabilities)
        confidence = float(probabilities[best_index])  # 0–1

        char = class_names[best_index]

        full_word.append(char)
        confidences.append(confidence)

        detections.append({
            "char": char,
            "confidence": round(confidence * 100, 2)
        })

    word_text = "".join(full_word)
    avg_conf = (np.mean(confidences) * 100) if confidences else 0

    return word_text, round(avg_conf, 2), detections

# --- 5. API ROUTES ---

@app.route('/api/translate', methods=['POST'])
def translate():
    session_id = start_processing_session(request.remote_addr)
    mode = request.form.get('mode') or (request.json.get('mode') if request.is_json else None)
    
    try:
        if mode == 'Baybayin to Tagalog':
            if 'file' not in request.files:
                update_session_status(session_id, 'No_File')
                return jsonify({"error": "No image uploaded"}), 400
            
            image_bytes = request.files['file'].read()
            text, conf, results = preprocess_and_predict(image_bytes)
            
            log_detections(session_id, results)
            status = "Success" if conf > 30 else "Low_Confidence"
            update_session_status(session_id, status)

            return jsonify({
                "translated_text": text,
                "confidence": conf,
                "status": status,
                "individual_detections": results,
                "session_id": session_id
            })

        elif mode == 'Tagalog to Baybayin':
            data = request.json if request.is_json else request.form
            input_text = data.get('text', '')
            baybayin_text = ttb_translator.translate(input_text) if ttb_translator else "Error"
            update_session_status(session_id, "Success")
            
            return jsonify({
                "translated_text": baybayin_text,
                "confidence": 100.0,
                "status": "Success",
                "individual_detections": [],
                "session_id": session_id
            })

    except Exception as e:
        update_session_status(session_id, 'Error')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)