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

# --- 4. IMAGE PROCESSING & AUTO-CROP ENGINE (SYNCED WITH COLAB) ---

def preprocess_and_predict(image_bytes, session_id):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return "Error", 0.0, []

    # =========================================================
    # STEP 1: BINARIZATION — now matches doc1's tested approach
    # Otsu threshold on a Gaussian-blurred background estimate,
    # instead of adaptiveThreshold. This is the version that was
    # actually tuned for isolating baybayin strokes cleanly.
    # =========================================================
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_h, img_w = gray.shape

    bg = cv2.GaussianBlur(gray, (101, 101), 0)
    normalized = cv2.divide(gray, bg, scale=255)
    _, binary = cv2.threshold(
        normalized, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    # `binary` = clean, undilated stroke mask. This is what actual
    # character crops come from — never thickened as a whole image.

    # =========================================================
    # STEP 2: ADAPTIVE COMPONENT SEPARATION (for box-finding only)
    # Builds a separate, more heavily dilated `mask` purely to find
    # character boundaries and bridge kudlit/virama marks to their
    # base character. `binary` (undilated) is untouched and is what
    # gets cropped later — matches doc1's design.
    # =========================================================
    base_kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(binary, base_kernel, iterations=1)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    heights = [
        stats[i, cv2.CC_STAT_HEIGHT]
        for i in range(1, num_labels)
        if stats[i, cv2.CC_STAT_HEIGHT] > 15
    ]
    if heights:
        avg_letter_height = int(np.mean(heights))
        adaptive_v_size = max(20, int(avg_letter_height * 0.40))
    else:
        adaptive_v_size = 45

    safe_v_kernel = np.ones((adaptive_v_size, 1), np.uint8)
    mask = cv2.dilate(mask, safe_v_kernel, iterations=1)

    safe_h_kernel = np.ones((1, 8), np.uint8)
    mask = cv2.dilate(mask, safe_h_kernel, iterations=1)

    # =========================================================
    # STEP 3: FIND CANDIDATE BOXES FROM THE DILATED MASK
    # =========================================================
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    all_pieces = [
        list(cv2.boundingRect(c))
        for c in contours
        if cv2.boundingRect(c)[2] > 20 and cv2.boundingRect(c)[3] > 20
    ]

    # =========================================================
    # STEP 4: SMART PIECE MERGING (kept — needed for multi-word
    # lines, which doc1 never has to handle since each sheet is
    # a single label. Acts as a safety net on top of the adaptive
    # vertical bridging above.)
    # =========================================================
    def group_and_merge(boxes):
        if not boxes:
            return []
        boxes.sort(key=lambda b: b[0])
        merged = []
        while len(boxes) > 0:
            curr = boxes.pop(0)
            found_neighbor = False
            for i in range(len(merged)):
                m = merged[i]

                h_overlap = max(0, min(curr[0] + curr[2], m[0] + m[2]) - max(curr[0], m[0]))
                v_dist = max(0, m[1] - (curr[1] + curr[3]), curr[1] - (m[1] + m[3]))
                h_dist = max(0, m[0] - (curr[0] + curr[2]), curr[0] - (m[0] + m[2]))

                is_vertical_stack = (h_overlap > 2 and v_dist < 85)
                is_too_close_horizontal = (h_dist < 5 and v_dist < 10)

                if is_vertical_stack or is_too_close_horizontal:
                    x_n = min(curr[0], m[0])
                    y_n = min(curr[1], m[1])
                    w_n = max(curr[0] + curr[2], m[0] + m[2]) - x_n
                    h_n = max(curr[1] + curr[3], m[1] + m[3]) - y_n
                    merged[i] = [x_n, y_n, w_n, h_n]
                    found_neighbor = True
                    break
            if not found_neighbor:
                merged.append(curr)
        return merged

    final_boxes = group_and_merge(group_and_merge(all_pieces))

    # =========================================================
    # STEP 5: SORT BOXES INTO LINES
    # =========================================================
    if not final_boxes:
        return "No characters detected", 0.0, []

    final_boxes.sort(key=lambda b: b[1] + b[3] / 2)
    lines = []
    curr_line = [final_boxes[0]]
    for i in range(1, len(final_boxes)):
        curr_center = final_boxes[i][1] + final_boxes[i][3] / 2
        prev_center = curr_line[-1][1] + curr_line[-1][3] / 2
        if abs(curr_center - prev_center) < 120:
            curr_line.append(final_boxes[i])
        else:
            lines.append(sorted(curr_line, key=lambda b: b[0]))
            curr_line = [final_boxes[i]]
    lines.append(sorted(curr_line, key=lambda b: b[0]))

    # =========================================================
    # STEP 6: PREDICTION PIPELINE
    # =========================================================
    CONF_LIMIT = 0.23
    WORD_GAP_THRESHOLD = 30
    target_size = 64
    FIXED_PAD = 5  # must match training's FIXED_PAD — do not change

    # Same light local thickening doc1 applies to each character
    # AFTER cropping — not to the whole image beforehand.
    THICK_KERNEL = np.ones((2, 2), np.uint8)
    THICK_ITER = 1

    full_sentence_text = []
    confidences = []
    detections = []

    session_temp_dir = os.path.join(TEMP_ROOT, f"session_{session_id}")
    os.makedirs(session_temp_dir, exist_ok=True)

    crop_index = 0
    for line in lines:
        line_chars = []
        for i, box in enumerate(line):
            x, y, w, h = box

            # Crop from the UNDILATED binary — matches doc1, which
            # never crops from the box-finding mask.
            roi_bin = binary[
                max(0, y):min(img_h, y + h),
                max(0, x):min(img_w, x + w)
            ]
            if roi_bin.size == 0:
                continue

            # Tight crop pass — remove any slack around the ink
            pts = cv2.findNonZero(roi_bin)
            if pts is None:
                continue
            tx, ty, tw, th = cv2.boundingRect(pts)
            tight_bin = roi_bin[ty:ty+th, tx:tx+tw]

            # Local thickening (matches doc1's post-crop thickening)
            tight_bin = cv2.dilate(tight_bin, THICK_KERNEL, iterations=THICK_ITER)

            # Re-crop tight after thickening (dilation expands bounds)
            pts2 = cv2.findNonZero(tight_bin)
            if pts2 is None:
                continue
            tx2, ty2, tw2, th2 = cv2.boundingRect(pts2)
            tight_bin = tight_bin[ty2:ty2+th2, tx2:tx2+tw2]

            ch, cw = tight_bin.shape[:2]
            if ch == 0 or cw == 0:
                continue

            # --- CANVAS LOGIC — fixed 5px pad, matches training ---
            side = max(cw, ch)
            total_side = side + (FIXED_PAD * 2)
            canvas = np.zeros((total_side, total_side), dtype=np.uint8)

            off_x = (total_side - cw) // 2
            off_y = (total_side - ch) // 2
            canvas[off_y:off_y + ch, off_x:off_x + cw] = tight_bin

            # Resize to 64x64 (matches training input)
            img_final = cv2.resize(canvas, (target_size, target_size), interpolation=cv2.INTER_AREA)

            # Force clean binary — resize introduces grey anti-aliasing pixels
            _, img_final = cv2.threshold(img_final, 127, 255, cv2.THRESH_BINARY)

            # HOG Feature Extraction
            fd = hog(img_final, orientations=9, pixels_per_cell=(8, 8),
                     cells_per_block=(2, 2), visualize=False)
            scaled_fd = scaler.transform(fd.reshape(1, -1))

            # Prediction
            probs = model.predict_proba(scaled_fd)[0]
            best_idx = np.argmax(probs)
            char = class_names[best_idx]
            conf = float(probs[best_idx])

            # Save cropped image for session temp storage
            temp_filename = f"{crop_index}_{uuid.uuid4().hex[:8]}.jpg"
            temp_path = os.path.join(session_temp_dir, temp_filename)
            cv2.imwrite(temp_path, img_final)

            detections.append({
                "char": char,
                "confidence": round(conf * 100, 2),
                "is_eligible": conf >= CONF_LIMIT,
                "temp_path": temp_path
            })
            confidences.append(conf)
            crop_index += 1

            if conf >= CONF_LIMIT:
                prefix = ""
                if i > 0:
                    prev_x, _, prev_w, _ = line[i - 1]
                    if (x - (prev_x + prev_w)) > WORD_GAP_THRESHOLD:
                        prefix = " "
                line_chars.append(prefix + char)

        full_sentence_text.append("".join(line_chars).strip())

    final_text = " | ".join(line for line in full_sentence_text if line)
    avg_conf = round(np.mean(confidences) * 100, 2) if confidences else 0.0

    return final_text, avg_conf, detections

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

    if not detections:
        return jsonify({"status": "Ignored", "message": "No detections to archive"}), 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        saved_count = 0
        archive_data = []

        for d in detections:
            char = d.get('char')
            confidence = d.get('confidence')
            temp_path = d.get('temp_path')
            is_eligible = d.get('is_eligible', False)

            if not char or not temp_path or not os.path.exists(temp_path) or not is_eligible:
                continue

            char_dir = os.path.join(ARCHIVE_ROOT, char)
            os.makedirs(char_dir, exist_ok=True)

            final_filename = f"sess{session_id}_{uuid.uuid4().hex[:8]}.jpg"
            final_path = os.path.join(char_dir, final_filename)

            os.rename(temp_path, final_path)
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

        # Cleanup
        session_temp_dir = os.path.join(TEMP_ROOT, f"session_{session_id}")
        if os.path.exists(session_temp_dir):
            for file in os.listdir(session_temp_dir):
                os.remove(os.path.join(session_temp_dir, file))
            os.rmdir(session_temp_dir)

        return jsonify({"status": "Success", "message": f"Archived {saved_count} entries"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)