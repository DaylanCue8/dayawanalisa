# DAYAW — Objective 4: Software Testing Strategy
**White Box, Black Box, Alpha, Beta Testing — ISO/IEC 25010 Compliance**

---

## 1. Testing Overview

The testing strategy for DAYAW follows a multi-level approach aligned with the **ISO/IEC 25010** software product-quality model. Testing progresses from internal code-level validation through to external user acceptance.

```
Level 1 — White Box Testing (developer-internal)
    ├── Statement Coverage ≥ 85 %
    ├── Branch Coverage ≥ 80 %
    └── Boundary / Equivalence Testing

Level 2 — Black Box Testing (functional, system)
    └── 22 test cases (BT1–BT22)
        ├── BTT Module (BT1–BT6)
        ├── TTB Module (BT7–BT12)
        ├── Archival System (BT13–BT18)
        ├── Usability / UX (BT19–BT20)
        └── Performance (BT21–BT22)

Level 3 — Alpha Testing (internal, controlled)
Level 4 — Beta Testing (external users, SUS/NPS)
```

---

## 2. White Box Testing

### 2.1 Statement Coverage

**Target:** ≥ 85 % for all source modules.

| Module | File | Target |
|---|---|---|
| BTT Recognition | `app.py` | ≥ 85 % |
| TTB Translation | `tagalog_to_baybayin.py` | ≥ 85 % |
| Archival Pipeline | `archival.py` (planned) | ≥ 85 % |

**Tool:** `pytest --cov=. --cov-report=html --cov-report=term-missing`

**Evidence:** `htmlcov/index.html` screenshot showing per-module percentages.

### 2.2 Branch Coverage

**Target:** ≥ 80 % (all `if/elif/else` paths exercised).

Configure in `.coveragerc`:
```ini
[run]
branch = True
source = .
omit = tests/*

[report]
fail_under = 80
```

**Key branches to test:**

| Branch | Module | Test |
|---|---|---|
| Kudlit present / absent | `tagalog_to_baybayin.py` | `test_kudlit_ei`, `test_kudlit_ou` |
| Virama appended / not appended | `tagalog_to_baybayin.py` | `test_virama_salamat` |
| `mga` exception | `tagalog_to_baybayin.py` | `test_mga_exception` |
| `ng` digraph / regular `n` | `tagalog_to_baybayin.py` | `test_ng_digraph` |
| Confidence ≥ 90 % / < 90 % | `archival.py` | `test_accuracy_gate` |
| Duplicate detected / not detected | `archival.py` | `test_duplicate_prevention` |

### 2.3 Boundary Testing

Boundary and equivalence partitions for each module:

**BTT Module (SVM Input Image):**

| Partition | Input Value | Expected Outcome |
|---|---|---|
| Valid – minimum size | 42 × 42 px | Prediction returned |
| Valid – large image | 1000 × 1000 px | Resized to 42 × 42; prediction returned |
| Invalid – empty array | `np.zeros((0,0))` | `ValueError` raised |
| Invalid – wrong channels | RGB 3-channel | Converted to grayscale; prediction returned |
| Boundary – exactly 42 × 42 | `np.ones((42,42))` | No resize needed; prediction returned |

**TTB Module (String Input):**

| Partition | Input Value | Expected Outcome |
|---|---|---|
| Valid – single vowel | `"a"` | `ᜀ` |
| Valid – full word | `"baybayin"` | Correct Baybayin string |
| Valid – with space | `"mga bata"` | Handles 'mga' exception + space |
| Invalid – empty string | `""` | Empty string returned |
| Invalid – non-Tagalog chars | `"z"` | Graceful fallback / pass-through |
| Boundary – 255 chars | string × 255 | Processed without truncation |

**Archival Accuracy Gate:**

| Partition | Confidence Value | Expected Outcome |
|---|---|---|
| Below threshold | 0.89 | Rejected |
| At boundary (exact) | 0.90 | Archived (inclusive boundary) |
| Above threshold | 0.95 | Archived |

---

## 3. Black Box Testing — 22 Test Cases (BT1–BT22)

### BTT Module — Handwriting Recognition (BT1–BT6)

#### BT1 — Single Character Recognition: "ba"

| Field | Value |
|---|---|
| **Test ID** | BT1 |
| **Module** | BTT |
| **Type** | Functional |
| **Input** | Handwritten image of Baybayin "ba" character |
| **Expected Output** | Predicted label: `"ba"` |
| **Pass Criteria** | `predicted_label == "ba"` |
| **ISO 25010** | Functional Correctness |

#### BT2 — All 17 Base Characters Recognised

| Field | Value |
|---|---|
| **Test ID** | BT2 |
| **Module** | BTT |
| **Type** | Functional |
| **Input** | 17 reference images (one per character) |
| **Expected Output** | Each image predicted with correct label |
| **Pass Criteria** | Accuracy ≥ 85 % across all 17 |
| **ISO 25010** | Functional Completeness |

#### BT3 — Printed vs. Handwritten Comparison

| Field | Value |
|---|---|
| **Test ID** | BT3 |
| **Module** | BTT |
| **Type** | Functional |
| **Input** | Paired printed and handwritten images for each character |
| **Expected Output** | Both predicted correctly |
| **Pass Criteria** | No significant accuracy gap (< 5 %) between printed and handwritten |
| **ISO 25010** | Functional Correctness |

#### BT4 — Low-Quality Image Input

| Field | Value |
|---|---|
| **Test ID** | BT4 |
| **Module** | BTT |
| **Type** | Robustness |
| **Input** | Blurred / noisy handwritten image (Gaussian blur σ=2) |
| **Expected Output** | Prediction returned without crash |
| **Pass Criteria** | No exception raised; label returned (may be incorrect) |
| **ISO 25010** | Reliability – Fault Tolerance |

#### BT5 — Invalid Image Format

| Field | Value |
|---|---|
| **Test ID** | BT5 |
| **Module** | BTT |
| **Type** | Negative |
| **Input** | Non-image file (`.txt` file) |
| **Expected Output** | `ValueError` or HTTP 400 Bad Request |
| **Pass Criteria** | System does not crash; error returned gracefully |
| **ISO 25010** | Reliability – Fault Tolerance |

#### BT6 — Virama Character Recognition

| Field | Value |
|---|---|
| **Test ID** | BT6 |
| **Module** | BTT |
| **Type** | Functional |
| **Input** | Handwritten virama (᜔) character image |
| **Expected Output** | Predicted label: `"virama"` |
| **Pass Criteria** | `predicted_label == "virama"` |
| **ISO 25010** | Functional Correctness |

---

### TTB Module — Translation (BT7–BT12)

#### BT7 — Single Vowel Translation

| Field | Value |
|---|---|
| **Test ID** | BT7 |
| **Input** | `"a"` |
| **Expected Output** | `"ᜀ"` (U+1700) |
| **Pass Criteria** | Output == `"ᜀ"` |
| **ISO 25010** | Functional Correctness |

#### BT8 — Full Word Translation: "baybayin"

| Field | Value |
|---|---|
| **Test ID** | BT8 |
| **Input** | `"baybayin"` |
| **Expected Output** | `"ᜊᜌ᜔ᜊᜌᜒᜈ᜔"` (correct Unicode) |
| **Pass Criteria** | Output matches expected Unicode string |
| **ISO 25010** | Functional Correctness |

#### BT9 — Kudlit Upper (e/i) Application

| Field | Value |
|---|---|
| **Test ID** | BT9 |
| **Input** | `"si"` |
| **Expected Output** | `"ᜐᜒ"` (sa + upper kudlit) |
| **Pass Criteria** | Output == `"ᜐᜒ"` |
| **ISO 25010** | Functional Correctness |

#### BT10 — Kudlit Lower (o/u) Application

| Field | Value |
|---|---|
| **Test ID** | BT10 |
| **Input** | `"su"` |
| **Expected Output** | `"ᜐᜓ"` (sa + lower kudlit) |
| **Pass Criteria** | Output == `"ᜐᜓ"` |
| **ISO 25010** | Functional Correctness |

#### BT11 — 'mga' Exception Handling

| Field | Value |
|---|---|
| **Test ID** | BT11 |
| **Input** | `"mga"` |
| **Expected Output** | Special 'mga' Baybayin rendering (not m+g+a individually) |
| **Pass Criteria** | Output matches predefined 'mga' mapping |
| **ISO 25010** | Functional Suitability |

#### BT12 — Empty String Input

| Field | Value |
|---|---|
| **Test ID** | BT12 |
| **Input** | `""` |
| **Expected Output** | `""` (empty string) |
| **Pass Criteria** | No exception; output is empty |
| **ISO 25010** | Reliability – Fault Tolerance |

---

### Archival System (BT13–BT18)

#### BT13 — Archive Approved Submission (≥ 90 %)

| Field | Value |
|---|---|
| **Test ID** | BT13 |
| **Input** | Session with overall_accuracy = 0.93 |
| **Expected Output** | Files written to `Captured/`, `Characters/`, `Metadata/` |
| **Pass Criteria** | All three folders updated; status = "archived" |
| **ISO 25010** | Functional Completeness |

#### BT14 — Reject Below-Threshold Submission

| Field | Value |
|---|---|
| **Test ID** | BT14 |
| **Input** | Session with overall_accuracy = 0.87 |
| **Expected Output** | No files written; feedback message |
| **Pass Criteria** | Archive unchanged; message contains "threshold" |
| **ISO 25010** | Functional Correctness |

#### BT15 — Metadata JSON Completeness

| Field | Value |
|---|---|
| **Test ID** | BT15 |
| **Input** | Archived session |
| **Expected Output** | `session_meta.json` contains all 9 mandatory fields |
| **Pass Criteria** | All fields present and non-null |
| **ISO 25010** | Data Integrity (Security) |

#### BT16 — Character Extraction: "halimbawa na"

| Field | Value |
|---|---|
| **Test ID** | BT16 |
| **Input** | Text `"halimbawa na"` |
| **Expected Output** | `["ha", "li", "m", "ba", "wa", "na"]` |
| **Pass Criteria** | List equals expected exactly |
| **ISO 25010** | Functional Correctness |

#### BT17 — Duplicate Submission Rejected

| Field | Value |
|---|---|
| **Test ID** | BT17 |
| **Input** | Previously archived image submitted again |
| **Expected Output** | Rejection with "duplicate detected" |
| **Pass Criteria** | No new files written to archive |
| **ISO 25010** | Data Integrity |

#### BT18 — Folder Structure Auto-created

| Field | Value |
|---|---|
| **Test ID** | BT18 |
| **Input** | First-ever submission to empty archive directory |
| **Expected Output** | `Captured/`, `Characters/`, `Metadata/` created automatically |
| **Pass Criteria** | All three directories exist after submission |
| **ISO 25010** | Functional Suitability |

---

### Usability & UX Testing (BT19–BT20)

#### BT19 — Navigation: BTT to TTB Module Switch

| Field | Value |
|---|---|
| **Test ID** | BT19 |
| **Type** | Usability |
| **Scenario** | User switches from BTT to TTB module via navigation menu |
| **Expected Outcome** | Screen transitions within 500 ms; no loading errors |
| **Pass Criteria** | Transition time ≤ 500 ms; correct module loaded |
| **ISO 25010** | Usability – Operability |

#### BT20 — Error Message Clarity

| Field | Value |
|---|---|
| **Test ID** | BT20 |
| **Type** | Usability |
| **Scenario** | User submits blank input to BTT |
| **Expected Outcome** | Clear, human-readable error message displayed |
| **Pass Criteria** | Error message present; does not expose stack trace |
| **ISO 25010** | Usability – User Error Protection |

---

### Performance Testing (BT21–BT22)

#### BT21 — BTT Inference Latency

| Field | Value |
|---|---|
| **Test ID** | BT21 |
| **Type** | Performance |
| **Input** | Single 42 × 42 character image |
| **Expected Output** | Prediction returned |
| **Pass Criteria** | Response time ≤ 500 ms (measured by Postman / pytest timing) |
| **ISO 25010** | Performance Efficiency – Time Behaviour |

#### BT22 — Concurrent Session Handling

| Field | Value |
|---|---|
| **Test ID** | BT22 |
| **Type** | Performance / Load |
| **Input** | 10 simultaneous archive submissions |
| **Expected Output** | All 10 processed; no data corruption |
| **Pass Criteria** | 0 data integrity errors; all sessions independently stored |
| **ISO 25010** | Performance Efficiency – Capacity |

---

## 4. Integration Testing (BT–IT Bridge)

See `SYSTEM_INTEGRATION_PROCESS.md` for IT1–IT7 integration test cases.

---

## 5. Alpha Testing Plan

### Definition
Alpha testing is **internal developer testing** conducted in a controlled environment before release to external users.

### Participants
- Project developers (2–3 members)
- Academic supervisor (1 member)

### Scope
- Full system walkthrough: BTT → TTB → Archival
- Edge case scenarios identified during white-box testing
- Performance benchmarking on development hardware

### Process
1. Execute all BT1–BT22 black-box test cases formally.
2. Log all defects in GitHub Issues with labels `P1-critical`, `P2-major`, `P3-minor`.
3. All P1 defects must be resolved before beta testing begins.
4. Retest all P1/P2 fixes before beta release.

### Exit Criteria
- All BT1–BT22 executed.
- 0 open P1 defects.
- ≤ 3 open P2 defects (all with accepted workarounds).

---

## 6. Beta Testing Plan

### Definition
Beta testing is **external user testing** with real end users in an uncontrolled environment.

### Participants
- ≥ 5 external users (target: students / researchers interested in Baybayin)
- Recruited via academic network or university mailing list

### Instruments
1. **System Usability Scale (SUS)** — 10-item Likert questionnaire
2. **Net Promoter Score (NPS)** — Single question: "How likely are you to recommend DAYAW?"

### SUS Scoring
```
SUS Score = Σ contributions × 2.5

For odd items (1,3,5,7,9): contribution = (response - 1)
For even items (2,4,6,8,10): contribution = (5 - response)
Score range: 0–100; Industry average ≥ 68 = "Good"
```

### NPS Scoring
```
Promoters (score 9–10): %P
Detractors (score 0–6): %D
NPS = %P - %D
Target: NPS ≥ 0 (net positive)
```

### Beta Test Sessions
| Session | Activity | Duration |
|---|---|---|
| Onboarding | Introduction to DAYAW; consent form | 10 min |
| Task 1 | Use BTT to recognise 5 handwritten characters | 15 min |
| Task 2 | Use TTB to translate "salamat" and "baybayin" | 10 min |
| Task 3 | Submit handwriting to archive | 10 min |
| Survey | SUS questionnaire + NPS | 10 min |

### Exit Criteria
- ≥ 5 participants completed full session.
- SUS ≥ 68.
- NPS ≥ 0.
- All P1 defects discovered in beta resolved within 7 days.

---

## 7. ISO/IEC 25010 Compliance Matrix

| Quality Characteristic | Sub-characteristic | Testing Coverage |
|---|---|---|
| Functional Suitability | Functional completeness | BT2, BT8, BT13 |
| Functional Suitability | Functional correctness | BT1, BT7–BT11, BT14–BT16 |
| Performance Efficiency | Time behaviour | BT21 |
| Performance Efficiency | Capacity | BT22 |
| Reliability | Fault tolerance | BT4, BT5, BT12, BT17 |
| Usability | Operability | BT19, Beta SUS |
| Usability | User error protection | BT20 |
| Usability | User satisfaction | Beta SUS ≥ 68, NPS ≥ 0 |
| Security | Data integrity | BT15, BT17 |
| Maintainability | Analysability | White-box coverage ≥ 85 % |

---

*Document version 1.0 — Cross-reference: `OBJECTIVES_EVALUATION_CRITERIA.md`, `TESTING_INSTRUMENTS_&_TOOLS.md`, `SYSTEM_INTEGRATION_PROCESS.md`*
