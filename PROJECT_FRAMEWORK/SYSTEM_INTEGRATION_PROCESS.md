# DAYAW — System Integration Process
**Integration Testing Phases, API Endpoints, Database Schema, Data Flow, and Test Cases**

---

## 1. Integration Testing Approach

Integration testing for DAYAW follows a **bottom-up** strategy:

```
Phase 1 — Unit Testing (modules individually)
        ↓
Phase 2 — Component Integration (module pairs)
        ↓
Phase 3 — Subsystem Integration (BTT + TTB + Archival)
        ↓
Phase 4 — System Integration (Backend + Frontend + Database)
        ↓
Phase 5 — End-to-End (full user workflow)
```

### Phase 1 — Unit Testing
- **Scope:** Individual functions and classes in isolation.
- **Tools:** `pytest`, `unittest.mock`
- **Evidence:** 131 unit tests PASSED; coverage ≥ 85 %

### Phase 2 — Component Integration
- **Scope:** Two or more modules working together.
- **Pairs tested:**
  - BTT module ↔ SVM model file
  - TTB module ↔ Unicode output layer
  - Archival module ↔ File system
- **Tools:** `pytest`, integration fixtures

### Phase 3 — Subsystem Integration
- **Scope:** Full backend subsystem (BTT + TTB + Archival) without frontend.
- **Tools:** `pytest`, `requests` (HTTP), `Postman`

### Phase 4 — System Integration
- **Scope:** Backend API ↔ Flutter frontend ↔ MySQL database
- **Tools:** `Postman`, Flutter integration tests, MySQL Workbench

### Phase 5 — End-to-End Testing
- **Scope:** Complete user workflow from app launch to archive confirmation.
- **Tools:** Flutter widget tests, manual walkthrough

---

## 2. API Endpoint Specifications

Base URL (local): `http://localhost:5000`

### 2.1 POST /predict — BTT: Baybayin Character Recognition

```
POST /predict
Content-Type: multipart/form-data

Form fields:
  image   (file)    — Handwritten character image (PNG/JPEG, max 5 MB)

Response 200 OK:
{
  "label":      "ba",
  "confidence": 0.97,
  "processing_time_ms": 124
}

Response 400 Bad Request:
{
  "error": "Invalid image format or missing image field"
}

Response 500 Internal Server Error:
{
  "error": "Model inference failed"
}
```

### 2.2 POST /translate — TTB: Tagalog-to-Baybayin Translation

```
POST /translate
Content-Type: application/json

Request body:
{
  "text": "baybayin"
}

Response 200 OK:
{
  "input":   "baybayin",
  "baybayin": "ᜊᜌ᜔ᜊᜌᜒᜈ᜔",
  "syllables": ["ba", "y", "ba", "yi", "n"]
}

Response 400 Bad Request:
{
  "error": "Missing 'text' field in request body"
}
```

### 2.3 POST /archive — Submit Handwriting for Archival

```
POST /archive
Content-Type: multipart/form-data

Form fields:
  image          (file)    — Full handwritten image
  word           (string)  — Tagalog word written
  contributor_id (string)  — Anonymised user identifier

Response 201 Created:
{
  "session_id":       "uuid-v4",
  "status":           "archived",
  "overall_accuracy": 0.93,
  "message":          "Session archived successfully"
}

Response 200 OK (rejected):
{
  "session_id":       "uuid-v4",
  "status":           "rejected",
  "overall_accuracy": 0.87,
  "message":          "Accuracy below threshold (0.90). Please retrace characters."
}

Response 400 Bad Request:
{
  "error": "Missing required fields: image, word, contributor_id"
}
```

### 2.4 GET /archive/{session_id} — Retrieve Archive Session Metadata

```
GET /archive/{session_id}

Response 200 OK:
{
  "session_id":       "uuid-v4",
  "contributor_id":   "anon-hash",
  "timestamp":        "2025-01-01T00:00:00Z",
  "word":             "halimbawa",
  "characters":       ["ha", "li", "m", "ba", "wa"],
  "accuracy_scores":  {"ha": 0.97, "li": 0.92, "m": 0.91, "ba": 0.95, "wa": 0.93},
  "overall_accuracy": 0.936,
  "status":           "archived",
  "source_file":      "Captured/uuid-v4/ts_anon.png"
}

Response 404 Not Found:
{
  "error": "Session not found"
}
```

### 2.5 GET /health — System Health Check

```
GET /health

Response 200 OK:
{
  "status":       "ok",
  "model_loaded": true,
  "db_connected": true,
  "timestamp":    "2025-01-01T00:00:00Z"
}
```

---

## 3. Database Schema

See also `OBJECTIVE_3_ARCHIVAL_SYSTEM.md` §5 for full DDL.

### Entity-Relationship Overview

```
archive_sessions (1) ──────< (M) archive_characters
archive_sessions (1) ──────< (M) archive_metadata_fields
```

### archive_sessions

| Column | Type | Constraint |
|---|---|---|
| `session_id` | VARCHAR(36) | PRIMARY KEY |
| `contributor_id` | VARCHAR(64) | NOT NULL |
| `timestamp` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| `word` | VARCHAR(255) | NOT NULL |
| `overall_accuracy` | DECIMAL(5,4) | NOT NULL |
| `status` | ENUM('archived','rejected','pending') | NOT NULL |
| `source_file` | VARCHAR(512) | NOT NULL |

### archive_characters

| Column | Type | Constraint |
|---|---|---|
| `id` | INT | AUTO_INCREMENT PRIMARY KEY |
| `session_id` | VARCHAR(36) | FK → archive_sessions |
| `character_label` | VARCHAR(10) | NOT NULL |
| `confidence_score` | DECIMAL(5,4) | NOT NULL |
| `file_path` | VARCHAR(512) | NOT NULL |

### archive_metadata_fields

| Column | Type | Constraint |
|---|---|---|
| `id` | INT | AUTO_INCREMENT PRIMARY KEY |
| `session_id` | VARCHAR(36) | FK → archive_sessions |
| `field_key` | VARCHAR(64) | NOT NULL |
| `field_value` | TEXT | NOT NULL |

---

## 4. Data Flow Diagrams

### 4.1 BTT Data Flow

```
Flutter App                Flask Backend              SVM Model
    │                           │                          │
    │── POST /predict ──────────►                          │
    │   (image bytes)           │── load image ───────────►│
    │                           │   HOG features (42×42)   │
    │                           │◄─ predicted label ───────│
    │◄─ JSON response ──────────│   + confidence           │
    │   {label, confidence}     │                          │
```

### 4.2 TTB Data Flow

```
Flutter App                Flask Backend              Translation Engine
    │                           │                          │
    │── POST /translate ─────────►                         │
    │   {"text": "baybayin"}    │── transliterate() ──────►│
    │                           │                          │── apply rules ──►
    │                           │◄─ Baybayin string ───────│   (kudlit, virama)
    │◄─ JSON response ──────────│                          │
    │   {input, baybayin}       │                          │
```

### 4.3 Archival Data Flow

```
Flutter App          Flask Backend         File System       MySQL DB
    │                     │                     │                │
    │─ POST /archive ─────►                     │                │
    │  (image, word,       │── extract chars ───►               │
    │   contributor_id)    │   HOG + SVM infer   │               │
    │                      │── accuracy ≥ 90%? ──┤               │
    │                      │   YES               │               │
    │                      │── write Captured/ ──►               │
    │                      │── write Characters/─►               │
    │                      │── write Metadata/ ──►               │
    │                      │── INSERT session ───────────────────►
    │◄─ {status:archived} ─│                     │                │
```

---

## 5. Integration Test Cases (IT1–IT7)

### IT1 — BTT API End-to-End

| Field | Value |
|---|---|
| **Test ID** | IT1 |
| **Phase** | Phase 3 – Subsystem Integration |
| **Components** | Flask `/predict` ↔ SVM model |
| **Input** | HTTP POST to `/predict` with valid PNG image |
| **Expected Output** | JSON with `label` and `confidence` fields; status 200 |
| **Pass Criteria** | Status 200; `label` is one of 17 valid characters; `confidence` ∈ [0,1] |

---

### IT2 — TTB API End-to-End

| Field | Value |
|---|---|
| **Test ID** | IT2 |
| **Phase** | Phase 3 – Subsystem Integration |
| **Components** | Flask `/translate` ↔ TTB rule engine |
| **Input** | HTTP POST `{"text": "salamat"}` |
| **Expected Output** | JSON with `baybayin` = correct Unicode; status 200 |
| **Pass Criteria** | Status 200; `baybayin` contains only U+1700–U+171F range + spaces |

---

### IT3 — Archival API End-to-End (Approved)

| Field | Value |
|---|---|
| **Test ID** | IT3 |
| **Phase** | Phase 3 – Subsystem Integration |
| **Components** | Flask `/archive` ↔ Archival module ↔ File system |
| **Input** | HTTP POST with high-quality image (confidence = 0.95) |
| **Expected Output** | Status 201; `status` = "archived"; files on disk |
| **Pass Criteria** | Status 201; `Captured/`, `Characters/`, `Metadata/` updated |

---

### IT4 — Archival API End-to-End (Rejected)

| Field | Value |
|---|---|
| **Test ID** | IT4 |
| **Phase** | Phase 3 – Subsystem Integration |
| **Components** | Flask `/archive` ↔ Archival module |
| **Input** | HTTP POST with low-quality image (confidence = 0.82) |
| **Expected Output** | Status 200; `status` = "rejected"; no files on disk |
| **Pass Criteria** | Status 200; archive directories unchanged |

---

### IT5 — Database Write on Archive

| Field | Value |
|---|---|
| **Test ID** | IT5 |
| **Phase** | Phase 4 – System Integration |
| **Components** | Archival module ↔ MySQL database |
| **Input** | Approved session (accuracy = 0.93) |
| **Expected Output** | Row inserted into `archive_sessions`; rows in `archive_characters` |
| **Pass Criteria** | `SELECT COUNT(*) FROM archive_sessions WHERE session_id = ?` returns 1 |

---

### IT6 — Frontend-to-Backend BTT Flow

| Field | Value |
|---|---|
| **Test ID** | IT6 |
| **Phase** | Phase 4 – System Integration |
| **Components** | Flutter app ↔ Flask API |
| **Input** | User draws character on Flutter canvas; taps "Recognise" |
| **Expected Output** | Predicted label displayed on screen within 500 ms |
| **Pass Criteria** | UI shows correct label; no HTTP error displayed |

---

### IT7 — Full User Workflow (End-to-End)

| Field | Value |
|---|---|
| **Test ID** | IT7 |
| **Phase** | Phase 5 – End-to-End |
| **Components** | Flutter app ↔ Flask API ↔ SVM + TTB ↔ Archival ↔ MySQL |
| **Scenario** | User writes "ba", recognises it (BTT), translates to Baybayin (TTB), submits to archive |
| **Expected Output** | All three operations succeed; archive session stored; UI confirms |
| **Pass Criteria** | Status = "archived"; all three API calls return expected responses; UI shows confirmation |

---

## 6. Integration Test Matrix

| Test | Phase | BTT | TTB | Archival | File System | Database | Frontend | Pass |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| IT1 | 3 | ✅ | | | | | | |
| IT2 | 3 | | ✅ | | | | | |
| IT3 | 3 | ✅ | | ✅ | ✅ | | | |
| IT4 | 3 | ✅ | | ✅ | | | | |
| IT5 | 4 | ✅ | | ✅ | ✅ | ✅ | | |
| IT6 | 4 | ✅ | | | | | ✅ | |
| IT7 | 5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |

---

*Document version 1.0 — Cross-reference: `OBJECTIVE_3_ARCHIVAL_SYSTEM.md`, `OBJECTIVE_4_TESTING_STRATEGY.md`, `TEST_EXECUTION_REPORT_TEMPLATE.md`*
