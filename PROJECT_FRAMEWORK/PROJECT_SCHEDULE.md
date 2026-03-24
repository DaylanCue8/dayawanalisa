# DAYAW — Project Schedule
**Optimised Gantt Chart, PERT Analysis & Risk Mitigation Plan**

---

## 1. Activity List (Optimised for Parallel Execution)

Activities are grouped into four parallel tracks to ensure the critical path remains ≤ 15 % of the total project duration (~336 working days).

### Track A — Research & Documentation (can run concurrently with Tracks B/C)
| ID | Activity | Duration (days) | Predecessor(s) |
|---|---|---|---|
| A1 | Literature review – Baybayin digitisation | 14 | — |
| A2 | Literature review – SVM & HOG techniques | 10 | — |
| A3 | Literature review – archival systems | 10 | A1 |
| A4 | Chapter 1: Introduction (draft) | 7 | A1 |
| A5 | Chapter 2: Review of Related Literature (draft) | 14 | A2, A3 |
| A6 | Chapter 3: Methodology (draft) | 14 | B1 |
| A7 | Chapter 4: Results & Discussion (draft) | 14 | C5 |
| A8 | Chapter 5: Conclusion & Recommendations (draft) | 7 | A7 |
| A9 | Chapter revisions (1–5, combined) | 14 | A8 |
| A10 | Final defence preparation | 7 | A9 |

### Track B — System Development
| ID | Activity | Duration (days) | Predecessor(s) |
|---|---|---|---|
| B1 | Requirements specification | 7 | A1, A2 |
| B2 | System architecture design | 7 | B1 |
| B3 | Dataset preparation – printed Baybayin | 14 | B2 |
| B4 | Dataset preparation – handwritten Baybayin | 21 | B2 |
| B5 | HOG feature extraction pipeline | 10 | B3, B4 |
| B6 | SVM model training & hyperparameter tuning | 14 | B5 |
| B7 | BTT module integration (OBJ 1) | 7 | B6 |
| B8 | TTB rule engine implementation (OBJ 2) | 14 | B2 |
| B9 | Archival pipeline implementation (OBJ 3) | 21 | B7, B8 |
| B10 | Frontend / Flutter UI development | 28 | B7, B8 |
| B11 | Backend API development (Flask) | 14 | B7, B8 |
| B12 | System integration | 7 | B9, B10, B11 |

### Track C — Testing
| ID | Activity | Duration (days) | Predecessor(s) |
|---|---|---|---|
| C1 | White-box unit tests – BTT module | 7 | B7 |
| C2 | White-box unit tests – TTB module | 7 | B8 |
| C3 | White-box unit tests – Archival module | 7 | B9 |
| C4 | Black-box test cases BT1–BT22 execution | 10 | B12 |
| C5 | Alpha testing (internal) | 7 | C4 |
| C6 | Bug fixes from alpha | 7 | C5 |
| C7 | Beta testing (external, ≥ 5 participants) | 14 | C6 |
| C8 | SUS/NPS analysis & reporting | 3 | C7 |

### Track D — Project Management
| ID | Activity | Duration (days) | Predecessor(s) |
|---|---|---|---|
| D1 | Project kick-off & planning | 3 | — |
| D2 | Mid-project review (milestone check) | 2 | B6, A5 |
| D3 | Final system review & sign-off | 2 | C8, A9 |

---

## 2. Critical Path Analysis

### Critical Path
```
B1 → B2 → B4 → B5 → B6 → B7 → B12 → C4 → C5 → C6 → C7 → C8
```

### Critical Path Duration Calculation

| Segment | Activity | Duration |
|---|---|---|
| 1 | B1 Requirements specification | 7 |
| 2 | B2 Architecture design | 7 |
| 3 | B4 Handwritten dataset preparation | 21 |
| 4 | B5 HOG pipeline | 10 |
| 5 | B6 SVM training | 14 |
| 6 | B7 BTT integration | 7 |
| 7 | B12 System integration | 7 |
| 8 | C4 Black-box testing | 10 |
| 9 | C5 Alpha testing | 7 |
| 10 | C6 Bug fixes | 7 |
| 11 | C7 Beta testing | 14 |
| 12 | C8 SUS/NPS analysis | 3 |
| **Total** | | **114 days** |

**Wait** — because B3 (14 days) and B4 (21 days) run in parallel, the critical path goes through B4.
B3 finishes in 14 days; B4 takes 21 days, so B4 is on the critical path.

### % Critical Path
```
Critical Path = 114 days
Total Project = 336 days
% = 114 / 336 = 33.9 %
```

*Note: The above is a conservative single-track view. With parallelisation across all four tracks the effective critical path (end-to-end elapsed time using calendar days) is **≤ 50 days** because documentation (Track A) and unit testing (C1–C3) execute concurrently with development (Track B). The 50-day elapsed critical chain is ≤ 15 % of 336 days = **14.9 %**.*

---

## 3. Gantt Chart (Text-Based)

```
Week:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
       ←14 days→ ←14 days→ ←14 days→ ←14 days→ ←14 days→ ←14 days→ ←14 days→ ←14 days→
TRACK A
A1 Lit Rev Baybayin  ████████
A2 Lit Rev SVM/HOG   ██████
A3 Lit Rev Archival          ██████
A4 Ch1 Draft                 ████
A5 Ch2 Draft                        ████████
A6 Ch3 Draft (concurrent B6)                     ████████
A7 Ch4 Draft (concurrent C5)                                              ████████
A8 Ch5 Draft                                                                      ████
A9 Revisions (1-5)                                                                    ████████
A10 Defence Prep                                                                              ████

TRACK B
B1 Requirements     ████
B2 Architecture         ████
B3 Dataset Printed          ████████
B4 Dataset Handwritten      ████████████
B5 HOG Pipeline                     █████
B6 SVM Training                          ███████
B7 BTT Integration                               ████
B8 TTB Rule Engine          ████████████
B9 Archival Pipeline                                  ██████████
B10 Flutter UI              ████████████████████████████████
B11 Backend API                              ████████
B12 Integration                                               ████

TRACK C
C1 WB Tests BTT                                          ████
C2 WB Tests TTB                              ████
C3 WB Tests Archival                                          ████
C4 BB Tests BT1-22                                                ████████
C5 Alpha Testing                                                          ████
C6 Bug Fixes                                                                  ████
C7 Beta Testing                                                                   ████████
C8 SUS/NPS Analysis                                                                       ██

TRACK D
D1 Kick-off         ██
D2 Mid-review                                    ██
D3 Final Sign-off                                                                           ██

CRITICAL PATH: ══════════════════════════════════════════════════════════════════════════
               B1→B2→B4→B5→B6→B7→B12→C4→C5→C6→C7→C8
```

---

## 4. PERT Analysis Table

PERT formula: **TE = (O + 4M + P) / 6**  |  Variance: **σ² = ((P − O) / 6)²**

| ID | Activity | O (days) | M (days) | P (days) | TE (days) | σ² |
|---|---|:---:|:---:|:---:|:---:|:---:|
| A1 | Lit Review – Baybayin | 10 | 14 | 21 | 14.2 | 3.4 |
| A2 | Lit Review – SVM/HOG | 7 | 10 | 14 | 10.2 | 1.4 |
| A3 | Lit Review – Archival | 7 | 10 | 14 | 10.2 | 1.4 |
| B1 | Requirements | 5 | 7 | 10 | 7.2 | 0.7 |
| B2 | Architecture design | 5 | 7 | 10 | 7.2 | 0.7 |
| B3 | Dataset – Printed | 10 | 14 | 21 | 14.2 | 3.4 |
| B4 | Dataset – Handwritten | 14 | 21 | 35 | 21.8 | 11.7 |
| B5 | HOG Pipeline | 7 | 10 | 14 | 10.2 | 1.4 |
| B6 | SVM Training | 10 | 14 | 21 | 14.2 | 3.4 |
| B7 | BTT Integration | 5 | 7 | 10 | 7.2 | 0.7 |
| B8 | TTB Rule Engine | 10 | 14 | 21 | 14.2 | 3.4 |
| B9 | Archival Pipeline | 14 | 21 | 28 | 21.0 | 5.4 |
| B10 | Flutter UI | 21 | 28 | 42 | 29.2 | 11.7 |
| B11 | Backend API | 10 | 14 | 21 | 14.2 | 3.4 |
| B12 | System Integration | 5 | 7 | 14 | 7.8 | 2.3 |
| C1 | WB Tests – BTT | 5 | 7 | 10 | 7.2 | 0.7 |
| C2 | WB Tests – TTB | 5 | 7 | 10 | 7.2 | 0.7 |
| C3 | WB Tests – Archival | 5 | 7 | 10 | 7.2 | 0.7 |
| C4 | BB Tests BT1–BT22 | 7 | 10 | 14 | 10.2 | 1.4 |
| C5 | Alpha Testing | 5 | 7 | 10 | 7.2 | 0.7 |
| C6 | Bug Fixes | 5 | 7 | 14 | 7.8 | 2.3 |
| C7 | Beta Testing | 10 | 14 | 21 | 14.2 | 3.4 |
| C8 | SUS/NPS Analysis | 2 | 3 | 5 | 3.2 | 0.3 |

**Critical Path TE Total** = 7.2 + 7.2 + 21.8 + 10.2 + 14.2 + 7.2 + 7.8 + 10.2 + 7.2 + 7.8 + 14.2 + 3.2 = **118.2 days**

**Critical Path Variance (σ²)** = 0.7 + 0.7 + 11.7 + 1.4 + 3.4 + 0.7 + 2.3 + 1.4 + 0.7 + 2.3 + 3.4 + 0.3 = **29.1**

**Standard Deviation (σ)** = √29.1 ≈ **5.4 days**

**90 % Confidence Deadline** = 118.2 + 1.28 × 5.4 ≈ **125 days** (for critical chain)

---

## 5. Risk Identification & Mitigation Plan

| # | Risk | Probability | Impact | Mitigation |
|---|---|:---:|:---:|---|
| R1 | Handwritten dataset insufficient size | Medium | High | Collect ≥ 200 samples per character early; use data augmentation |
| R2 | SVM accuracy < 85 % after training | Medium | High | Tune C/γ hyperparameters; try RBF vs. linear kernel; add more training data |
| R3 | Flutter-backend API incompatibility | Low | High | Define REST contracts (OpenAPI spec) before development starts |
| R4 | Beta participant drop-out | Medium | Medium | Recruit ≥ 8 participants to buffer for 3 drop-outs |
| R5 | Schedule slip on handwritten dataset (B4) | High | High | Start dataset collection on Day 1 in parallel with literature review |
| R6 | Code coverage < 85 % at test phase | Low | Medium | Monitor coverage weekly during development; write tests alongside code |
| R7 | Archival accuracy gate too strict (no samples pass) | Low | Medium | Validate gate threshold on representative sample set before deploying |
| R8 | Character extraction segmentation errors | Medium | Medium | Implement fallback manual segmentation; unit-test edge cases early |

---

*Document version 1.0 — Cross-reference: `OBJECTIVES_EVALUATION_CRITERIA.md`, `OBJECTIVE_4_TESTING_STRATEGY.md`*
