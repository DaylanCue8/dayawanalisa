import cv2
import numpy as np
import joblib
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.feature import hog
from tagalog_to_baybayin import TagalogToBaybayin

# Initialize Translator
ttb_translator = TagalogToBaybayin()

app = Flask(__name__)
CORS(app)

# --- DATABASE CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'dayaw' 
}

# --- LOAD SVM MODEL ---
try:
    model = joblib.load('baybayin_svm_model.sav')
    class_names = ['A', 'BA', 'DARA', 'EI', 'GA', 'HA', 'KA', 'LA', 'MA', 'NA', 'NGA', 'OU', 'PA', 'SA', 'TA', 'WA', 'YA']
    print("✅ Model and Class Names loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# --- DATABASE HELPERS ---

def start_processing_session(ip_address, device_info="Mobile/Emulator"):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO processing_sessions (status, device_info, ip_address) VALUES ('Processing', %s, %s)"
        cursor.execute(query, (device_info, ip_address))
        conn.commit()
        new_id = cursor.lastrowid 
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"❌ DB Session Error: {e}")
        return 0

def log_detections(detections_list):
    if not detections_list: return
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO detection_logs (session_id, detected_char, confidence_score) VALUES (%s, %s, %s)"
        cursor.executemany(query, detections_list)
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

# --- IMAGE PROCESSING ---

def preprocess_and_predict(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None: return "Invalid Image", 0.0, []

    # Preprocessing (Upscale, Threshold, Denoise)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Healing
    kernel = np.ones((5,5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.dilate(binary, np.ones((3,3), np.uint8), iterations=1)

    # Filtering & Segmentation
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    clean_binary = np.zeros_like(binary)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > 800:
            clean_binary[labels == i] = 255

    contours, _ = cv2.findContours(clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_boxes = sorted([cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[2] > 50], key=lambda b: b[0])
    
    if not valid_boxes: return "No Detections", 0.0, []

    full_word = []
    total_confidence = 0
    detections = []
    
    for (x, y, w, h) in valid_boxes:
        roi = clean_binary[y:y+h, x:x+w]
        padded = cv2.copyMakeBorder(roi, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=0)
        resized = cv2.resize(padded, (42, 42))

        fd = hog(resized, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=False)
        
        # Use predict_proba for the confidence score
        probs = model.predict_proba([fd])[0]
        pred_idx = np.argmax(probs)
        conf = round(float(probs[pred_idx] * 100), 2)
        
        char = class_names[pred_idx]
        full_word.append(char)
        total_confidence += conf
        detections.append((char, conf))

    avg_conf = round(total_confidence / len(valid_boxes), 2)
    return "".join(full_word), avg_conf, detections

# --- API ROUTES ---

@app.route('/api/translate', methods=['POST'])
def translate():
    session_id = start_processing_session(request.remote_addr)
    mode = request.form.get('mode') or (request.json.get('mode') if request.is_json else 'Baybayin to Tagalog')
    
    try:
        # Initialize an empty list for Flutter
        flutter_detections = [] 

        if mode == 'Baybayin to Tagalog':
            if 'file' not in request.files:
                return jsonify({"error": "No image"}), 400
            
            image_bytes = request.files['file'].read()
            raw_text, confidence, individual_detections = preprocess_and_predict(image_bytes)
            
            # 1. Format for MySQL (Tuples)
            formatted_logs = [(session_id, d[0], d[1]) for d in individual_detections]
            log_detections(formatted_logs)

            # 2. Format for Flutter JSON (List of Dicts)
            # This is what fills your "Detected Characters" and Table
            flutter_detections = [{"char": d[0], "confidence": d[1]} for d in individual_detections]

            if confidence < 20:
                final_text = f"{confidence}% confidence\nRetake photo"
                final_status = 'Low_Confidence'
            else:
                final_text = raw_text
                final_status = 'Success'
            
        elif mode == 'Tagalog to Baybayin':
            tagalog_text = request.form.get('text') or (request.json.get('text') if request.is_json else '')
            final_text = ttb_translator.translate(tagalog_text)
            confidence = 100.0
            final_status = 'Success'
            flutter_detections = [] # No detections for text mode
        
        update_session_status(session_id, final_status)

        # THE KEY CHANGE: Send flutter_detections back to the app
        return jsonify({
            "translated_text": final_text,
            "confidence": confidence,
            "session_id": session_id,
            "status": final_status,
            "individual_detections": flutter_detections # Flutter is looking for this!
        })

    except Exception as e:
        update_session_status(session_id, 'Failed')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)