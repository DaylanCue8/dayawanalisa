# Project Schedule – Dayaw Baybayin Recognition & Translation System

## Gantt Chart

```
ID   Activity                          Duration  Start  End    Critical?
──────────────────────────────────────────────────────────────────────
1a   Project Initiation                2 days    D1     D2     ⭐ YES
1b   Data Collection & Organisation    3 days    D3     D5
─────────────────── Phase 2: Development ─────────────────────────────
2a   Backend API Implementation        8 days    D6     D13    ⭐ YES
2b   Frontend UI/UX Development        10 days   D6     D15    ⭐ YES
2c   SVM Model Training Code           5 days    D6     D10
2d   Translation System Implementation 7 days    D6     D12
─────────────────── Phase 3: Testing ─────────────────────────────────
3a   Unit Test Development             5 days    D46    D50
3b   SVM Model Training & Validation   10 days   D46    D55    ⭐ YES
3c   Integration Testing               5 days    D56    D60    ⭐ YES
3d   White Box Testing                 5 days    D61    D65
3e   Black Box Testing                 5 days    D61    D65    ⭐ YES
3f   Bug Fixes & Refinement            4 days    D66    D69
─────────────────── Phase 4: Documentation ───────────────────────────
4a   Final Report Writing              3 days    D76    D78
4b   Presentation Preparation          2 days    D79    D80
──────────────────────────────────────────────────────────────────────
     TOTAL PROJECT                     80 days   D1     D80
```

---

## Timeline Diagram (8-week view)

```
Week:    1         2         3         4         5         6         7
Day:  1234 5  6789 0  1234 5  6789 0  1234 5  6789 0  1234 5
                  1          1          2          2          3
Phase 1 ████  
Phase 2      ██████████████████████████
Phase 3                                          ██████████████████
Phase 4                                                           █████
```

---

## Critical Path Analysis

The **Critical Path** is the longest chain of dependent tasks that determines the minimum
project duration.

### Critical Path Sequence

```
Project Initiation (D1–D2)
    ↓
Backend API (D6–D13) ──┐
                        ├──► Frontend UI/UX (D6–D15, longest parallel leg)
                        │         ↓
                        └──► SVM Model Training & Validation (D46–D55)
                                  ↓
                         Integration Testing (D56–D60)
                                  ↓
                         Black Box Testing (D61–D65)
                                  ↓
                          Documentation (D76–D80)
```

### Critical Path Duration

The critical path is the longest sequence of dependent tasks with no slack:

| Segment | Days |
|---|---|
| Project Initiation (1a) | 2 |
| Frontend UI/UX Development (2b, longest parallel leg) | 10 |
| SVM Model Training & Validation (3b) | 10 |
| Integration Testing (3c) | 5 |
| Black Box Testing (3e) | 5 |
| **Critical Path Total** | **30 days** |

**Total Project Duration**: 80 days
(Phases 1–4 including parallel development tasks, testing phases, buffer, and documentation)

**Critical Path Percentage**: 30 / 80 = **37.5%** ✅ (exceeds the 15% minimum requirement)

---

## Phase Summaries

### Phase 1 – Setup & Planning (Days 1–5)
- **1a. Project Initiation** (D1–D2, 2 days) ⭐ Critical
  - Define scope, assign roles, set up repository
- **1b. Data Collection & Organisation** (D3–D5, 3 days)
  - Collect Baybayin character image dataset
  - Organise into printed / handwritten categories

### Phase 2 – Development (Days 6–45)
- **2a. Backend API Implementation** (D6–D13, 8 days) ⭐ Critical
  - Flask REST endpoints (`/api/translate`)
  - Image upload handling, SVM inference pipeline
- **2b. Frontend UI/UX Development** (D6–D15, 10 days) ⭐ Critical
  - Flutter mobile app screens
  - Image capture, translation display
- **2c. SVM Model Training Code** (D6–D10, 5 days)
  - HOG feature extraction pipeline
  - scikit-learn SVM (RBF kernel) training scripts
- **2d. Translation System Implementation** (D6–D12, 7 days)
  - `tagalog_to_baybayin.py` rule engine
  - All 17 Baybayin syllable mappings, kudlit / virama rules

### Phase 3 – Testing (Days 46–75) ⭐ Critical Phase
- **3a. Unit Test Development** (5 days)
  - pytest framework, ≥ 30 test cases
- **3b. SVM Model Training & Validation** (10 days) ⭐ Critical
  - Train on full dataset, compute Accuracy / Precision / Recall / F1
  - Generate 17×17 confusion matrix
- **3c. Integration Testing** (5 days)
  - End-to-end API tests
- **3d. White Box Testing** (5 days)
  - Code path coverage, boundary value testing
- **3e. Black Box Testing** (5 days)
  - ≥ 20 functional test cases
- **3f. Bug Fixes & Refinement** (4 days)

### Phase 4 – Documentation & Presentation (Days 76–80)
- **4a. Final Report Writing** (3 days)
- **4b. Presentation Preparation** (2 days)

---

## Milestone Table

| Milestone | Target Day | Deliverable |
|---|---|---|
| M1 – Project Kick-off | D1 | Repository set up, team aligned |
| M2 – Data Ready | D5 | Labelled dataset organised |
| M3 – Backend Alpha | D13 | Flask API accepting image uploads |
| M4 – Frontend Alpha | D15 | Flutter app connected to backend |
| M5 – Test Suite Green | D55 | SVM validated, 131 tests PASSED, 85%+ coverage |
| M6 – Validation Complete | D65 | All White Box / Black Box test cases pass |
| M7 – Final Report | D78 | Documentation submitted |
| M8 – Presentation | D80 | Defence / demo complete |
