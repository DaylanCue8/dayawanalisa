import cv2
import numpy as np
import joblib
import mysql.connector
import os
import uuid
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.feature import hog
from tagalog_to_baybayin import TagalogToBaybayin

app = Flask(__name__)
CORS(app)

ttb_translator = TagalogToBaybayin()

# --- 1. AI & ARCHIVE PATH CONFIG ---
ARCHIVE_ROOT = 'open_archival_dataset'
TEMP_ROOT = 'temp_crops'

for folder in [ARCHIVE_ROOT, TEMP_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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

def get_db_connection():
    return mysql.connector.connect(**db_config)

def start_processing_session(ip_address):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO processing_sessions (status, ip_address) VALUES ('Processing', %s)"
        cursor.execute(query, (ip_address,))
        new_id = cursor.lastrowid 
        conn.commit()
        return new_id
    except Exception as e:
        print(f"❌ DB Session Error: {e}")
        return 0
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def log_detections(session_id, detections_list):
    if not detections_list or session_id == 0: return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        formatted_logs = [(session_id, d['char'], d['confidence']) for d in detections_list]
        query = "INSERT INTO detection_logs (session_id, detected_char, confidence_score) VALUES (%s, %s, %s)"
        cursor.executemany(query, formatted_logs)
        conn.commit()
    except Exception as e:
        print(f"❌ Log Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def update_session_status(session_id, status):
    if session_id == 0: return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE processing_sessions SET status = %s, end_time = CURRENT_TIMESTAMP WHERE session_id = %s"
        cursor.execute(query, (status, session_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Update Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# --- 4. IMAGE PROCESSING & AUTO-CROP ENGINE ---

def preprocess_and_predict(image_bytes, session_id):
    import uuid
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return "Error", 0.0, []

    # 1. PREPROCESSING
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bg_img = cv2.medianBlur(gray, 51)
    normalized = cv2.divide(gray, bg_img, scale=255)
    binary = cv2.adaptiveThreshold(normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 10)

    # 2. STROKE CLEANUP
    kernel = np.ones((3,3), np.uint8) 
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.dilate(binary, np.ones((2,2), np.uint8), iterations=2)
    binary = cv2.medianBlur(binary, 3)

    # 3. SMART PIECE MERGING
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    all_pieces = [list(cv2.boundingRect(c)) for c in contours if cv2.boundingRect(c)[2] > 35 and cv2.boundingRect(c)[3] > 35]

    def get_iou_horizontal(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        return max(0, xB - xA)

    def group_and_merge(boxes):
        if not boxes: return []
        boxes.sort(key=lambda b: b[1])
        merged = []
        while len(boxes) > 0:
            curr = boxes.pop(0)
            found_neighbor = False
            for i in range(len(merged)):
                m = merged[i]
                h_overlap = get_iou_horizontal(curr, m)
                v_dist = max(0, m[1] - (curr[1] + curr[3]), curr[1] - (m[1] + m[3]))
                h_dist = max(0, m[0] - (curr[0] + curr[2]), curr[0] - (m[0] + m[2]))
                if (h_overlap > 0 and v_dist < 25) or (h_dist < 15 and v_dist < 30):
                    x_n = min(curr[0], m[0]); y_n = min(curr[1], m[1])
                    w_n = max(curr[0] + curr[2], m[0] + m[2]) - x_n
                    h_n = max(curr[1] + curr[3], m[1] + m[3]) - y_n
                    merged[i] = [x_n, y_n, w_n, h_n]
                    found_neighbor = True
                    break
            if not found_neighbor:
                merged.append(curr)
        return merged

    final_boxes = group_and_merge(group_and_merge(all_pieces))

    # 4. SORT BOXES INTO LINES
    if not final_boxes:
        return "No characters detected", 0.0, []

    final_boxes.sort(key=lambda b: b[1] + b[3]/2)
    lines = []
    curr_line = [final_boxes[0]]
    for i in range(1, len(final_boxes)):
        if abs((final_boxes[i][1] + final_boxes[i][3]/2) - (curr_line[-1][1] + curr_line[-1][3]/2)) < 100:
            curr_line.append(final_boxes[i])
        else:
            lines.append(sorted(curr_line, key=lambda b: b[0]))
            curr_line = [final_boxes[i]]
    lines.append(sorted(curr_line, key=lambda b: b[0]))

    # 5. PREDICTION PIPELINE
    full_sentence_text = []
    confidences = []
    detections = []
    target_size = 64
    margin_ratio = 0.10

    # Create temp folder per session
    session_temp_dir = os.path.join(TEMP_ROOT, f"session_{session_id}")
    os.makedirs(session_temp_dir, exist_ok=True)

    crop_index = 0

    for line in lines:
        line_chars = []
        for box in line:
            x, y, w, h = box
            roi = binary[y:y+h, x:x+w]

            coords = cv2.findNonZero(roi)
            if coords is None:
                continue

            tx, ty, tw, th = cv2.boundingRect(coords)
            roi_tight = roi[ty:ty+th, tx:tx+tw]

            side = max(tw, th)
            pad = int(side * margin_ratio)
            roi_padded = cv2.copyMakeBorder(roi_tight, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)

            img_final = cv2.resize(roi_padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

            fd = hog(img_final, orientations=9, pixels_per_cell=(8, 8),
                     cells_per_block=(2, 2), visualize=False)
            scaled_fd = scaler.transform(fd.reshape(1, -1))
            probs = model.predict_proba(scaled_fd)[0]
            best_idx = np.argmax(probs)

            char = class_names[best_idx]
            conf = float(probs[best_idx])
            is_eligible = conf >= 0.90

            # SAVE ONLY TO TEMP, NOT TO ARCHIVE
            temp_filename = f"{crop_index}_{uuid.uuid4().hex[:8]}.jpg"
            temp_path = os.path.join(session_temp_dir, temp_filename)
            cv2.imwrite(temp_path, img_final)

            line_chars.append(char)
            confidences.append(conf)
            detections.append({
                "char": char,
                "confidence": round(conf * 100, 2),
                "is_eligible": is_eligible,
                "temp_path": temp_path
            })

            crop_index += 1

        full_sentence_text.append("".join(line_chars))

    return " | ".join(full_sentence_text), round(np.mean(confidences)*100, 2) if confidences else 0, detections
# --- 5. API ROUTES ---

@app.route('/api/translate', methods=['POST'])
def translate():
    session_id = start_processing_session(request.remote_addr)
    mode = request.form.get('mode') if 'mode' in request.form else request.json.get('mode')

    try:
        if mode == 'Baybayin to Tagalog':
            if 'file' not in request.files:
                update_session_status(session_id, 'No_File')
                return jsonify({"error": "No image uploaded"}), 400
            
            image_bytes = request.files['file'].read()
            # Pass session_id to enable auto-cropping
            text, conf, results = preprocess_and_predict(image_bytes, session_id)
            
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

        elif mode == 'Tagalog to Baybayin':
            input_text = request.form.get('text') if 'text' in request.form else request.json.get('text')
            if not input_text:
                update_session_status(session_id, 'No_Text')
                return jsonify({"error": "No text provided"}), 400
            
            translated_result, confidence = ttb_translator.translate(input_text)
            update_session_status(session_id, "Success")
            
            return jsonify({
                "translated_text": translated_result,
                "confidence": confidence,
                "session_id": session_id
            })

    except Exception as e:
        update_session_status(session_id, 'Error')
        return jsonify({"error": str(e)}), 500

@app.route('/api/archive_bulk', methods=['POST'])
def archive_bulk():
    data = request.json
    session_id = data.get('session_id')
    detections = data.get('detections', [])

    print("\n===== ARCHIVE BULK DEBUG =====")
    print("Session ID:", session_id)
    print("Detections Received:", detections)

    if not detections:
        print("❌ No detections received")
        return jsonify({"status": "Ignored", "message": "No detections to archive"}), 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        saved_count = 0
        archive_data = []

        for i, d in enumerate(detections):
            print(f"\n--- Detection {i+1} ---")
            print("Raw Detection:", d)

            char = d.get('char')
            confidence = d.get('confidence')
            temp_path = d.get('temp_path')
            is_eligible = d.get('is_eligible', False)

            print("Char:", char)
            print("Confidence:", confidence)
            print("Temp Path:", temp_path)
            print("Eligible:", is_eligible)

            if not char:
                print("❌ Skipped: Missing char")
                continue

            if not temp_path:
                print("❌ Skipped: Missing temp_path")
                continue

            if not os.path.exists(temp_path):
                print(f"❌ Skipped: Temp file does not exist -> {temp_path}")
                continue

            if not is_eligible:
                print("❌ Skipped: is_eligible is False")
                continue

            char_dir = os.path.join(ARCHIVE_ROOT, char)
            os.makedirs(char_dir, exist_ok=True)

            final_filename = f"sess{session_id}_{uuid.uuid4().hex[:8]}.jpg"
            final_path = os.path.join(char_dir, final_filename)

            print("➡ Moving file:")
            print("FROM:", temp_path)
            print("TO  :", final_path)

            try:
                os.rename(temp_path, final_path)
                print("✅ File moved successfully")
            except Exception as move_error:
                print("❌ Move Error:", move_error)
                continue

            archive_data.append((session_id, char, confidence, True))
            saved_count += 1

        if archive_data:
            query = """
                INSERT INTO open_archival 
                (session_id, char_label, confidence_score, verified_by_user) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.executemany(query, archive_data)
            conn.commit()
            print("✅ Database insert complete")
        else:
            print("❌ No archive_data to insert")

        # Cleanup leftover temp files
        session_temp_dir = os.path.join(TEMP_ROOT, f"session_{session_id}")
        if os.path.exists(session_temp_dir):
            for file in os.listdir(session_temp_dir):
                try:
                    os.remove(os.path.join(session_temp_dir, file))
                except Exception as cleanup_error:
                    print("Cleanup file error:", cleanup_error)
            try:
                os.rmdir(session_temp_dir)
            except Exception as cleanup_error:
                print("Cleanup folder error:", cleanup_error)

        print("===== END ARCHIVE DEBUG =====\n")

        return jsonify({
            "status": "Success",
            "message": f"Archived {saved_count} approved entries"
        }), 200

    except Exception as e:
        print(f"❌ Bulk Archive Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)