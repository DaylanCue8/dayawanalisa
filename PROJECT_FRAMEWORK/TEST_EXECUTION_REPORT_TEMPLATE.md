# DAYAW — Test Execution Report Template
**Fillable Template for Recording Test Results, Evidence, and Issues**

---

## Document Information

| Field | Value |
|---|---|
| **Project** | DAYAW — Digitally Archiving Your Ancient Writing |
| **Report Version** | [Fill in: e.g., v1.0] |
| **Testing Phase** | [Fill in: Alpha / Beta / White Box / Black Box] |
| **Tester(s)** | [Fill in names] |
| **Start Date** | [Fill in: YYYY-MM-DD] |
| **End Date** | [Fill in: YYYY-MM-DD] |
| **Environment** | [Fill in: OS, Python version, pytest version] |
| **Build / Commit SHA** | [Fill in: git commit hash] |

---

## 1. White Box Testing Results

### 1.1 Coverage Summary

| Module | Statements | Covered | Missed | Coverage % | Pass (≥85%) |
|---|---|---|---|---|---|
| `app.py` | | | | | ☐ |
| `tagalog_to_baybayin.py` | | | | | ☐ |
| `archival.py` | | | | | ☐ |
| **TOTAL** | | | | | ☐ |

**Branch Coverage:**

| Module | Branches | Covered | Coverage % | Pass (≥80%) |
|---|---|---|---|---|
| `app.py` | | | | ☐ |
| `tagalog_to_baybayin.py` | | | | ☐ |
| `archival.py` | | | | ☐ |
| **TOTAL** | | | | ☐ |

**Evidence:** Attach `htmlcov/index.html` screenshot or paste terminal output below.

```
[Paste pytest --cov terminal output here]
```

### 1.2 Unit Test Run Summary

| Suite | Total Tests | Passed | Failed | Skipped | Duration |
|---|---|---|---|---|---|
| `test_svm_model_performance.py` | | | | | |
| `test_translation_system.py` | | | | | |
| `test_archival.py` | | | | | |
| **TOTAL** | | | | | |

**Pass Criteria:** 0 failures, 0 errors.

---

## 2. Black Box Test Execution Log (BT1–BT22)

For each test, fill in: Actual Output, Pass/Fail, and Defect ID if failed.

### BTT Module (BT1–BT6)

| Test ID | Test Name | Date | Tester | Input | Expected Output | Actual Output | P/F | Defect ID |
|---|---|---|---|---|---|---|---|---|
| BT1 | Single char recognition "ba" | | | ba image | label=ba | | ☐ | |
| BT2 | All 17 chars recognised | | | 17 images | accuracy ≥85% | | ☐ | |
| BT3 | Printed vs. Handwritten | | | paired images | gap <5% | | ☐ | |
| BT4 | Low-quality image | | | blurred image | no crash | | ☐ | |
| BT5 | Invalid image format | | | .txt file | HTTP 400 | | ☐ | |
| BT6 | Virama character recognition | | | virama image | label=virama | | ☐ | |

### TTB Module (BT7–BT12)

| Test ID | Test Name | Date | Tester | Input | Expected Output | Actual Output | P/F | Defect ID |
|---|---|---|---|---|---|---|---|---|
| BT7 | Single vowel "a" | | | "a" | ᜀ | | ☐ | |
| BT8 | Full word "baybayin" | | | "baybayin" | Baybayin string | | ☐ | |
| BT9 | Kudlit upper "si" | | | "si" | ᜐᜒ | | ☐ | |
| BT10 | Kudlit lower "su" | | | "su" | ᜐᜓ | | ☐ | |
| BT11 | mga exception | | | "mga" | special mapping | | ☐ | |
| BT12 | Empty string | | | "" | "" | | ☐ | |

### Archival System (BT13–BT18)

| Test ID | Test Name | Date | Tester | Input | Expected Output | Actual Output | P/F | Defect ID |
|---|---|---|---|---|---|---|---|---|
| BT13 | Archive approved (acc=0.93) | | | acc=0.93 | status=archived | | ☐ | |
| BT14 | Reject below threshold | | | acc=0.87 | status=rejected | | ☐ | |
| BT15 | Metadata completeness | | | session JSON | 9 fields present | | ☐ | |
| BT16 | Char extraction "halimbawa na" | | | "halimbawa na" | [ha,li,m,ba,wa,na] | | ☐ | |
| BT17 | Duplicate rejected | | | same image x2 | rejected | | ☐ | |
| BT18 | Folder auto-created | | | empty archive | 3 folders exist | | ☐ | |

### Usability & UX (BT19–BT20)

| Test ID | Test Name | Date | Tester | Input | Expected Output | Actual Output | P/F | Defect ID |
|---|---|---|---|---|---|---|---|---|
| BT19 | Module navigation ≤500ms | | | tap nav menu | ≤500ms transition | | ☐ | |
| BT20 | Error message clarity | | | blank submission | readable error | | ☐ | |

### Performance (BT21–BT22)

| Test ID | Test Name | Date | Tester | Input | Expected Output | Actual Output | P/F | Defect ID |
|---|---|---|---|---|---|---|---|---|
| BT21 | BTT inference ≤500ms | | | 42×42 image | response ≤500ms | | ☐ | |
| BT22 | Concurrent 10 sessions | | | 10 simultaneous | no corruption | | ☐ | |

---

## 3. Integration Test Execution Log (IT1–IT7)

| Test ID | Phase | Scenario | Date | Tester | Pass? | Notes |
|---|---|---|---|---|---|---|
| IT1 | Phase 3 | BTT API end-to-end | | | ☐ | |
| IT2 | Phase 3 | TTB API end-to-end | | | ☐ | |
| IT3 | Phase 3 | Archive API (approved) | | | ☐ | |
| IT4 | Phase 3 | Archive API (rejected) | | | ☐ | |
| IT5 | Phase 4 | DB write on archive | | | ☐ | |
| IT6 | Phase 4 | Flutter→Backend BTT | | | ☐ | |
| IT7 | Phase 5 | Full user workflow | | | ☐ | |

---

## 4. Archival System Test Cases (A1–A6)

| Test ID | Test Name | Date | Tester | Pass? | Notes |
|---|---|---|---|---|---|
| A1 | Archive approved (acc≥90%) | | | ☐ | |
| A2 | Reject below threshold | | | ☐ | |
| A3 | Segment "halimbawa" → 5 chars | | | ☐ | |
| A4 | Segment "salamat" → virama | | | ☐ | |
| A5 | Metadata JSON completeness | | | ☐ | |
| A6 | Duplicate prevention | | | ☐ | |

---

## 5. Defect Log

| Defect ID | Test Case | Severity | Description | Steps to Reproduce | Status | Resolution |
|---|---|---|---|---|---|---|
| DEF-001 | | P1/P2/P3 | | | Open/Resolved | |
| DEF-002 | | | | | | |
| DEF-003 | | | | | | |

**Severity Definitions:**
- **P1 (Critical):** System crash; data loss; security vulnerability. Must be resolved before release.
- **P2 (Major):** Feature not working correctly; significant usability issue. Must be resolved before beta.
- **P3 (Minor):** Cosmetic issue; minor inaccuracy. Can be deferred.

---

## 6. Alpha Testing Summary

| Criterion | Target | Actual | Pass? |
|---|---|---|---|
| All BT1–BT22 executed | 22 / 22 | | ☐ |
| P1 defects resolved | 0 open | | ☐ |
| P2 defects open with workaround | ≤ 3 | | ☐ |
| Code coverage ≥ 85 % | ≥ 85 % | [Fill in: ___%] | ☐ |

**Alpha Sign-off:** _________________ Date: _____________

---

## 7. Beta Testing Summary

### SUS Scores

| Participant | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | SUS Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| P1 | | | | | | | | | | | |
| P2 | | | | | | | | | | | |
| P3 | | | | | | | | | | | |
| P4 | | | | | | | | | | | |
| P5 | | | | | | | | | | | |
| **Average** | | | | | | | | | | | **≥ 68?** |

### NPS Scores

| Participant | NPS Rating (0–10) | Category |
|---|---|---|
| P1 | | Promoter / Passive / Detractor |
| P2 | | |
| P3 | | |
| P4 | | |
| P5 | | |

```
Promoters (9–10): _____ / 5 = ____%
Detractors (0–6): _____ / 5 = ____%
NPS = ____% - ____% = ____  (Target: ≥ 0)
```

### Beta Exit Criteria Checklist

| Criterion | Target | Actual | Pass? |
|---|---|---|---|
| Participants completed | ≥ 5 | | ☐ |
| SUS average | ≥ 68 | | ☐ |
| NPS | ≥ 0 | | ☐ |
| P1 defects from beta resolved | 0 open | | ☐ |

**Beta Sign-off:** _________________ Date: _____________

---

## 8. Overall Test Summary

| Category | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| Unit Tests | | | | % |
| Black Box (BT1–BT22) | 22 | | | % |
| Integration (IT1–IT7) | 7 | | | % |
| Archival (A1–A6) | 6 | | | % |
| **GRAND TOTAL** | | | | % |

**Statement Coverage:** _____ % (Target: ≥ 85 %)
**Branch Coverage:** _____ % (Target: ≥ 80 %)
**SUS Score:** _____ (Target: ≥ 68)
**NPS Score:** _____ (Target: ≥ 0)

---

## 9. Evidence Checklist

| Evidence Artefact | Location | Collected? |
|---|---|---|
| `htmlcov/index.html` — coverage report | `backend/htmlcov/` | ☐ |
| `tests/reports/pytest_report.html` | `backend/tests/reports/` | ☐ |
| `tests/reports/model_metrics.json` | `backend/tests/reports/` | ☐ |
| `tests/reports/confusion_matrix.png` | `backend/tests/reports/` | ☐ |
| `tests/reports/performance_report.html` | `backend/tests/reports/` | ☐ |
| `tests/reports/translation_metrics.json` | `backend/tests/reports/` | ☐ |
| Postman collection HTML report | `tests/reports/postman_report.html` | ☐ |
| BT1–BT22 spreadsheet (filled) | `PROJECT_FRAMEWORK/` | ☐ |
| SUS raw data CSV | `PROJECT_FRAMEWORK/` | ☐ |
| NPS raw data CSV | `PROJECT_FRAMEWORK/` | ☐ |
| GitHub Issues — defect log | GitHub repository | ☐ |

---

*Document version 1.0 — Cross-reference: `OBJECTIVE_4_TESTING_STRATEGY.md`, `TESTING_INSTRUMENTS_&_TOOLS.md`, `SYSTEM_INTEGRATION_PROCESS.md`*
