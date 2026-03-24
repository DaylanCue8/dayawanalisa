# DAYAW — Objectives & Evaluation Criteria
**ISO/IEC 25010 Software Quality Standards**

---

## Overview

DAYAW (Digitally Archiving Your Ancient Writing) is a system that enables Baybayin handwriting recognition (BTT), Tagalog-to-Baybayin translation (TTB), and archival preservation of digitized Baybayin characters. The four project objectives below map directly to the ISO/IEC 25010 product-quality characteristics.

---

## OBJECTIVE 1 — SVM-Based Baybayin Handwriting Recognition (BTT Module)

### Statement
Develop and validate a Support Vector Machine (SVM) classifier that recognises all 17 Baybayin base characters from handwritten input images.

### Measurable Success Criteria

| Metric | Threshold | Evaluation Method |
|---|---|---|
| Overall Accuracy | ≥ 85 % | Confusion-matrix on held-out test set |
| Per-class Precision | ≥ 80 % for every character | `sklearn.metrics.classification_report` |
| Per-class Recall | ≥ 80 % for every character | `sklearn.metrics.classification_report` |
| Macro F1-Score | ≥ 0.82 | `sklearn.metrics.f1_score(average='macro')` |
| Model Load Time | ≤ 2 s | Timed using `time.perf_counter()` |
| Single-image Inference Time | ≤ 500 ms | Timed using `time.perf_counter()` |

### Failure Criteria
- Overall accuracy < 85 %
- Any single character class with F1-score < 0.70
- Model file fails to deserialise via `pickle`/`joblib`

### ISO/IEC 25010 Characteristics
- **Functional Suitability** — Functional correctness of character mapping
- **Performance Efficiency** — Time behaviour (inference latency ≤ 500 ms)
- **Reliability** — Fault tolerance under low-quality input images

### Evidence Requirements
- `tests/reports/model_metrics.json` — per-class precision/recall/F1
- `tests/reports/confusion_matrix.png` — 17 × 17 confusion matrix
- `tests/reports/performance_report.html` — interactive dashboard
- Pytest run log showing ≥ 26 PASSED for `test_svm_model_performance.py`

---

## OBJECTIVE 2 — Rule-Based Tagalog-to-Baybayin Translation (TTB Module)

### Statement
Implement and verify a deterministic, rule-based engine that converts Tagalog text to the corresponding Unicode Baybayin script, covering all phonological rules (kudlit, virama, digraph handling).

### Measurable Success Criteria

| Metric | Threshold | Evaluation Method |
|---|---|---|
| Translation Accuracy | 100 % on defined rule set | Unit tests covering all 17 syllables + special rules |
| Statement Code Coverage | ≥ 85 % | `pytest --cov=. --cov-report=term-missing` |
| Branch Code Coverage | ≥ 80 % | `.coveragerc` with `branch = True` |
| Kudlit Rule Correctness | 100 % | Dedicated parametrised tests |
| Virama Rule Correctness | 100 % | Dedicated parametrised tests |
| Round-trip Consistency | 0 regressions | `test_rule_based_consistency` suite |

### Failure Criteria
- Any defined Tagalog→Baybayin mapping produces wrong output
- Statement coverage drops below 85 %
- Any kudlit or virama rule produces incorrect Unicode code point

### ISO/IEC 25010 Characteristics
- **Functional Suitability** — Functional correctness & completeness of translation rules
- **Maintainability** — Analysability supported by ≥ 85 % code coverage
- **Compatibility** — Unicode (U+1700–U+171F range) interoperability

### Evidence Requirements
- `tests/reports/translation_metrics.json` — accuracy: 100.0 %
- `tests/reports/translation_confusion_matrix.png`
- Coverage terminal report showing ≥ 85 % for `tagalog_to_baybayin.py`
- Pytest log: ≥ 30 PASSED for `test_translation_system.py`

---

## OBJECTIVE 3 — Baybayin Archival Preservation System

### Statement
Build a session-based archival pipeline that (a) evaluates handwriting accuracy against a reference dataset, (b) extracts individual syllabic characters, and (c) stores approved samples in a structured archive.

### Measurable Success Criteria

| Metric | Threshold | Evaluation Method |
|---|---|---|
| Archival Accuracy Gate | ≥ 90 % confidence before storage | SVM confidence score per character |
| Character Extraction Rate | ≥ 95 % of characters correctly segmented | Manual review of 50-sample test set |
| Archive Write Latency | ≤ 3 s per session | End-to-end timing test |
| Metadata Completeness | 100 % required fields populated | Schema validation script |
| Duplicate Detection | 0 false positives / 0 false negatives on test set | Hash-based deduplication test |
| Folder Structure Integrity | `Captured/`, `Characters/`, `Metadata/` always created | File-system assertion in tests |

### Failure Criteria
- Samples with confidence < 90 % are persisted to archive
- Character segmentation fails on standard Baybayin syllabic boundaries
- Metadata folder missing mandatory `source`, `timestamp`, or `contributor_id` fields

### ISO/IEC 25010 Characteristics
- **Functional Suitability** — Functional completeness of archival workflow
- **Security** — Integrity of archived data (no corruption, no unauthorised modification)
- **Maintainability** — Modifiability of archive schema

### Evidence Requirements
- Test cases A1–A6 (see `OBJECTIVE_3_ARCHIVAL_SYSTEM.md`) all PASSED
- Sample archive directory tree showing `Captured/`, `Characters/`, `Metadata/`
- Accuracy gate log demonstrating rejection of < 90 % confidence samples

---

## OBJECTIVE 4 — Software Testing & Quality Assurance

### Statement
Execute a multi-level testing strategy (white box, black box, alpha, beta) demonstrating system quality against ISO/IEC 25010 characteristics, resulting in ≥ 85 % code coverage and ≥ 22 documented test cases.

### Measurable Success Criteria

| Metric | Threshold | Evaluation Method |
|---|---|---|
| Statement Code Coverage | ≥ 85 % | `pytest --cov` HTML report |
| Branch Code Coverage | ≥ 80 % | `.coveragerc branch=True` |
| Black-Box Test Cases Executed | 22 (BT1–BT22) | Test log / Postman collection |
| Black-Box Pass Rate | ≥ 90 % on first execution | Test execution spreadsheet |
| Alpha Testing Issues Resolved | 100 % of P1 (critical) defects | Bug tracker / GitHub Issues |
| Beta SUS Score | ≥ 68 (industry average) | System Usability Scale survey |
| Beta NPS Score | ≥ 0 (net promoter) | Post-session NPS questionnaire |
| Integration Test Pass Rate | 100 % of IT1–IT7 | Integration test log |

### Failure Criteria
- Statement coverage < 85 % after final test run
- Any BT test case remains unexecuted
- SUS score < 68 (below industry average)
- Any P1 defect open at delivery

### ISO/IEC 25010 Characteristics
- **Functional Suitability** — Completeness validated by black-box test suite
- **Usability** — Acceptability & satisfaction validated by SUS/NPS
- **Reliability** — Fault tolerance validated by boundary & negative tests
- **Performance Efficiency** — Response-time thresholds in BT20–BT22

### Evidence Requirements
- `htmlcov/index.html` showing ≥ 85 % statement coverage
- Completed `TEST_EXECUTION_REPORT_TEMPLATE.md` with all BT rows filled
- SUS survey data (raw scores from ≥ 5 beta participants)
- NPS tallies from beta session

---

## Cross-Objective Traceability Matrix

| Requirement | OBJ 1 | OBJ 2 | OBJ 3 | OBJ 4 |
|---|:---:|:---:|:---:|:---:|
| Baybayin character recognition | ✅ | | ✅ | ✅ |
| Tagalog translation rules | | ✅ | | ✅ |
| Archival storage workflow | | | ✅ | ✅ |
| Code coverage ≥ 85 % | | ✅ | | ✅ |
| User acceptability (SUS/NPS) | | | | ✅ |
| ISO/IEC 25010 compliance | ✅ | ✅ | ✅ | ✅ |

---

*Document version 1.0 — Cross-reference: `PROJECT_SCHEDULE.md`, `OBJECTIVE_3_ARCHIVAL_SYSTEM.md`, `OBJECTIVE_4_TESTING_STRATEGY.md`*
