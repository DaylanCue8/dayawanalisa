# DAYAW — Objective 3: Archival Preservation System
**Complete Specification, Workflow, and Test Cases**

---

## 1. System Overview

The Baybayin Archival Preservation System (BAPS) is a session-based pipeline that:
1. Accepts handwritten Baybayin input from a user.
2. Evaluates per-character recognition confidence against a ≥ 90 % threshold.
3. Segments the input into individual syllabic characters.
4. Stores approved samples in a structured three-tier folder hierarchy.
5. Records provenance metadata for every archived artefact.

---

## 2. Archive Folder Structure

```
archive/
├── Captured/
│   └── {session_id}/
│       └── {timestamp}_{contributor_id}.png     ← full handwritten image
├── Characters/
│   └── {character_label}/
│       ├── {session_id}_{index}.png              ← extracted syllabic character
│       └── ...
└── Metadata/
    └── {session_id}/
        └── session_meta.json                     ← provenance record
```

### Captured/ Folder
Stores the **full, un-cropped** handwritten image submitted by the contributor.

| Field | Description |
|---|---|
| `session_id` | UUID generated per submission |
| `timestamp` | ISO 8601 datetime (UTC) |
| `contributor_id` | Anonymised user identifier |

### Characters/ Folder
Stores **individually extracted** syllabic character images, one sub-folder per character label.

Valid character labels (17 base + virama):
`ba, ka, da, ga, ha, la, ma, na, nga, pa, ra, sa, ta, wa, ya, a, ei, virama`

### Metadata/ Folder
Stores JSON provenance records.

**Mandatory fields in `session_meta.json`:**
```json
{
  "session_id": "uuid-v4",
  "contributor_id": "anon-hash",
  "timestamp": "2025-01-01T00:00:00Z",
  "word": "halimbawa",
  "characters": ["ha", "li", "m", "ba", "wa"],
  "accuracy_scores": { "ha": 0.97, "li": 0.92, "m": 0.91, "ba": 0.95, "wa": 0.93 },
  "overall_accuracy": 0.936,
  "status": "archived",
  "source_file": "Captured/uuid-v4/ts_anon.png"
}
```

---

## 3. Character Extraction Algorithm

### 3.1 Syllabic Segmentation Rules

Baybayin is an **abugida**: each base character represents a consonant + inherent /a/ vowel. The segmentation algorithm follows these rules:

```
Input word:  "halimbawa na"
Segmented:   [ha] [li] [m] [ba] [wa] [ ] [na]
             (space treated as separator; virama appended to standalone consonant)
```

**Step-by-step algorithm:**

```python
def segment_baybayin_word(word: str) -> list[str]:
    """
    Segment a Tagalog word into Baybayin syllabic units.
    Returns a list of syllable strings to look up in the character map.
    """
    syllables = []
    i = 0
    word = word.lower().strip()
    vowels = set('aeiou')
    digraphs = {'ng', 'ngg'}

    while i < len(word):
        # Skip spaces
        if word[i] == ' ':
            i += 1
            continue

        # Check for 'ng' digraph
        if i + 1 < len(word) and word[i:i+2] == 'ng':
            if i + 2 < len(word) and word[i+2] not in vowels:
                # 'ng' + consonant → virama applied later
                syllables.append('ng')
                i += 2
                continue
            elif i + 2 < len(word) and word[i+2] in vowels:
                # 'ng' + vowel → nga/nge/ngi/ngo/ngu
                syllables.append('ng' + word[i+2])
                i += 3
                continue

        # Consonant + vowel → standard syllable
        if word[i] not in vowels and i + 1 < len(word) and word[i+1] in vowels:
            syllables.append(word[i] + word[i+1])
            i += 2
            continue

        # Standalone vowel
        if word[i] in vowels:
            syllables.append(word[i])
            i += 1
            continue

        # Standalone consonant (final) → virama marker
        syllables.append(word[i])
        i += 1

    return syllables
```

### 3.2 Accuracy Scoring Algorithm

```python
def compute_session_accuracy(confidence_scores: dict[str, float]) -> float:
    """
    Compute overall session accuracy as the arithmetic mean of per-character
    SVM confidence scores (probability estimates from predict_proba).

    Args:
        confidence_scores: {'ha': 0.97, 'li': 0.92, ...}

    Returns:
        float between 0.0 and 1.0
    """
    if not confidence_scores:
        return 0.0
    return sum(confidence_scores.values()) / len(confidence_scores)


ARCHIVAL_THRESHOLD = 0.90  # 90 % required for archival contribution

def should_archive(overall_accuracy: float) -> bool:
    return overall_accuracy >= ARCHIVAL_THRESHOLD
```

### 3.3 Image Bounding-Box Extraction

Individual character images are extracted using contour detection:

```python
import cv2
import numpy as np

def extract_character_images(full_image_path: str) -> list[np.ndarray]:
    """
    Detect bounding boxes for each Baybayin character stroke
    and return list of cropped 42×42 character images.
    """
    img = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    char_images = []
    for cnt in sorted(contours, key=lambda c: cv2.boundingRect(c)[0]):
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 10 and h > 10:  # filter noise
            char_crop = img[y:y+h, x:x+w]
            char_resized = cv2.resize(char_crop, (42, 42))
            char_images.append(char_resized)

    return char_images
```

---

## 4. Archival Workflow Diagram

```
 User submits handwritten Baybayin
            │
            ▼
 ┌──────────────────────────┐
 │   Session Initialisation  │
 │   Generate session_id     │
 │   Record contributor_id   │
 └──────────┬───────────────┘
            │
            ▼
 ┌──────────────────────────┐
 │  Character Extraction     │
 │  OpenCV contour detect    │
 │  Segment → list of crops  │
 └──────────┬───────────────┘
            │
            ▼
 ┌──────────────────────────┐
 │  SVM Inference            │
 │  HOG features (42×42 img) │
 │  predict_proba() per char │
 └──────────┬───────────────┘
            │
            ▼
 ┌──────────────────────────┐
 │  Accuracy Gate            │
 │  overall_accuracy ≥ 90 %? │
 └──────────┬───────────────┘
         ┌──┴──┐
        YES    NO
         │      │
         ▼      ▼
  Archive   Return feedback:
  session   "Accuracy below threshold.
             Please retrace characters."
         │
         ▼
 ┌──────────────────────────┐
 │  Storage                  │
 │  Save full image →        │
 │    Captured/{session_id}/ │
 │  Save char crops →        │
 │    Characters/{label}/    │
 │  Write session_meta.json  │
 │    → Metadata/{session_id}│
 └──────────────────────────┘
```

---

## 5. Database Schema for Metadata Storage

### Table: `archive_sessions`

```sql
CREATE TABLE archive_sessions (
    session_id       VARCHAR(36)   PRIMARY KEY,  -- UUID v4
    contributor_id   VARCHAR(64)   NOT NULL,
    timestamp        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    word             VARCHAR(255)  NOT NULL,
    overall_accuracy DECIMAL(5,4)  NOT NULL,
    status           ENUM('archived','rejected','pending') NOT NULL,
    source_file      VARCHAR(512)  NOT NULL
);
```

### Table: `archive_characters`

```sql
CREATE TABLE archive_characters (
    id               INT           AUTO_INCREMENT PRIMARY KEY,
    session_id       VARCHAR(36)   NOT NULL,
    character_label  VARCHAR(10)   NOT NULL,
    confidence_score DECIMAL(5,4)  NOT NULL,
    file_path        VARCHAR(512)  NOT NULL,
    FOREIGN KEY (session_id) REFERENCES archive_sessions(session_id)
);
```

### Table: `archive_metadata_fields`

```sql
CREATE TABLE archive_metadata_fields (
    id          INT          AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(36)  NOT NULL,
    field_key   VARCHAR(64)  NOT NULL,
    field_value TEXT         NOT NULL,
    FOREIGN KEY (session_id) REFERENCES archive_sessions(session_id)
);
```

---

## 6. Test Cases — Archival System (A1–A6)

### A1 — Accuracy Gate: Approved Submission

| Field | Value |
|---|---|
| **Test ID** | A1 |
| **Test Name** | Archive session with ≥ 90 % accuracy |
| **Precondition** | SVM model loaded; archive directory writable |
| **Input** | Handwritten "ba" image with known confidence = 0.95 |
| **Expected Result** | Session written to `Captured/`, `Characters/ba/`, `Metadata/`; status = "archived" |
| **Pass Criteria** | All three folders contain new files; `session_meta.json` status = "archived" |

---

### A2 — Accuracy Gate: Rejected Submission

| Field | Value |
|---|---|
| **Test ID** | A2 |
| **Test Name** | Reject session with < 90 % accuracy |
| **Precondition** | SVM model loaded |
| **Input** | Low-quality image with computed confidence = 0.75 |
| **Expected Result** | No files written to archive; feedback message returned |
| **Pass Criteria** | Archive directories unchanged; return value contains "below threshold" |

---

### A3 — Character Extraction: Multi-character Word

| Field | Value |
|---|---|
| **Test ID** | A3 |
| **Test Name** | Segment "halimbawa" into 5 characters |
| **Precondition** | `segment_baybayin_word` function available |
| **Input** | `"halimbawa"` |
| **Expected Result** | `["ha", "li", "m", "ba", "wa"]` |
| **Pass Criteria** | Returned list equals expected list exactly |

---

### A4 — Character Extraction: Virama Detection

| Field | Value |
|---|---|
| **Test ID** | A4 |
| **Test Name** | Segment "salamat" — detects final virama |
| **Precondition** | `segment_baybayin_word` function available |
| **Input** | `"salamat"` |
| **Expected Result** | `["sa", "la", "ma", "t"]` where `"t"` maps to virama character |
| **Pass Criteria** | Final element is standalone consonant |

---

### A5 — Metadata Completeness

| Field | Value |
|---|---|
| **Test ID** | A5 |
| **Test Name** | Validate all mandatory metadata fields present |
| **Precondition** | A session has been archived (A1 passed) |
| **Input** | Read `session_meta.json` from `Metadata/{session_id}/` |
| **Expected Result** | JSON contains `session_id`, `contributor_id`, `timestamp`, `word`, `characters`, `accuracy_scores`, `overall_accuracy`, `status`, `source_file` |
| **Pass Criteria** | All 9 fields present and non-null |

---

### A6 — Duplicate Prevention

| Field | Value |
|---|---|
| **Test ID** | A6 |
| **Test Name** | Prevent duplicate archival of identical image |
| **Precondition** | A session with image hash H has already been archived |
| **Input** | Same image submitted again (same MD5/SHA256 hash) |
| **Expected Result** | System rejects duplicate; no new files written; message "duplicate detected" returned |
| **Pass Criteria** | Archive directory unchanged after second submission |

---

*Document version 1.0 — Cross-reference: `OBJECTIVES_EVALUATION_CRITERIA.md`, `SYSTEM_INTEGRATION_PROCESS.md`*
