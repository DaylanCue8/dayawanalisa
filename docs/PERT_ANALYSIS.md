# PERT Analysis – Dayaw Baybayin Recognition & Translation System

## PERT Formula

For each task:

```
Expected Duration (TE) = (Optimistic + 4 × Most Likely + Pessimistic) / 6
Variance (σ²)          = ((Pessimistic − Optimistic) / 6)²
```

---

## Task Estimates

### Phase 1 – Project Setup

| Task ID | Activity | O | M | P | TE (days) | σ² |
|---|---|---|---|---|---|---|
| 1a | Project Initiation | 1 | 2 | 3 | **2.00** | 0.11 |
| 1b | Data Collection & Organisation | 2 | 3 | 5 | **3.17** | 0.25 |

### Phase 2 – Development

| Task ID | Activity | O | M | P | TE (days) | σ² |
|---|---|---|---|---|---|---|
| 2a | Backend API Implementation | 5 | 8 | 12 | **8.17** | 1.36 |
| 2b | Frontend UI/UX Development | 7 | 10 | 15 | **10.33** | 1.78 |
| 2c | SVM Model Training Code | 4 | 5 | 7 | **5.17** | 0.25 |
| 2d | Translation System Implementation | 5 | 7 | 10 | **7.17** | 0.69 |

### Phase 3 – Testing

| Task ID | Activity | O | M | P | TE (days) | σ² | Critical? |
|---|---|---|---|---|---|---|---|
| 3a | Unit Test Development | 3 | 5 | 8 | **5.17** | 0.69 | |
| 3b | SVM Model Training & Validation | 7 | 10 | 15 | **10.33** | 1.78 | ⭐ YES |
| 3c | Integration Testing | 3 | 5 | 7 | **5.00** | 0.44 | |
| 3d | White Box Testing | 3 | 5 | 8 | **5.17** | 0.69 | |
| 3e | Black Box Testing | 4 | 5 | 7 | **5.17** | 0.25 | |
| 3f | Bug Fixes & Refinement | 2 | 4 | 6 | **4.00** | 0.44 | |

### Phase 4 – Documentation

| Task ID | Activity | O | M | P | TE (days) | σ² |
|---|---|---|---|---|---|---|
| 4a | Final Report Writing | 2 | 3 | 4 | **3.00** | 0.11 |
| 4b | Presentation Preparation | 1 | 2 | 3 | **2.00** | 0.11 |

---

## Network Diagram (Activity-on-Node)

```
START
  │
  ▼
[1a] Initiation  ──────────────────────────────────────┐
  │                                                     │
  ▼                                                     │
[1b] Data Collection                                    │
  │                                                     │
  ├──▶ [2a] Backend ──┐                                 │
  ├──▶ [2b] Frontend ─┤                                 │
  ├──▶ [2c] SVM Code  ┤                                 │
  └──▶ [2d] Translate ┘                                 │
              │                                         │
              ▼                                         │
    ┌──▶ [3a] Unit Tests                                │
    ├──▶ [3b] SVM Train & Validate ⭐ ──┐               │
    ├──▶ [3c] Integration               │               │
    │                                   ▼               │
    ├──▶ [3d] White Box ────────▶ [3f] Bug Fixes ──────▶│
    └──▶ [3e] Black Box ─────────────────────────────────┘
                                        │
                                        ▼
                                  [4a] Report
                                        │
                                        ▼
                                  [4b] Presentation
                                        │
                                        ▼
                                       END
```

---

## Critical Path Duration (PERT)

The critical path runs through the tasks with the longest cumulative expected duration:

```
1a → 2b (Frontend) → 3b (SVM Train) → 3f (Bug Fixes) → 4a → 4b
```

| Task | TE |
|---|---|
| 1a Project Initiation | 2.00 |
| 2b Frontend UI/UX | 10.33 |
| 3b SVM Training & Validation | 10.33 |
| 3f Bug Fixes & Refinement | 4.00 |
| 4a Final Report | 3.00 |
| 4b Presentation | 2.00 |
| **Critical Path Total** | **31.66 days** |

---

## Project Duration Statistics

**Expected Project Duration (TE)**: ~79 days (including parallel paths and buffer)

**Critical Path Variance**:

```
σ²_critical = σ²(1a) + σ²(2b) + σ²(3b) + σ²(3f) + σ²(4a) + σ²(4b)
             = 0.11 + 1.78 + 1.78 + 0.44 + 0.11 + 0.11
             = 4.33 days²
σ_critical   = √4.33 ≈ 2.08 days
```

**Confidence Intervals**:

| Confidence Level | Duration Range |
|---|---|
| 68% (±1σ) | 29.6 – 33.7 days (critical path) |
| 95% (±2σ) | 27.5 – 35.8 days (critical path) |
| 99% (±3σ) | 25.4 – 37.9 days (critical path) |

**Buffer Recommendation**: Add **3–4 days** (≈ 1.5σ) buffer to the project schedule for risk
mitigation.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| SVM model convergence takes longer than expected | Medium | High | Allocate 15-day maximum; use pre-trained features |
| Frontend/Backend integration issues | Medium | Medium | Daily integration builds via CI/CD |
| Dataset quality insufficient for ≥ 80% accuracy | Low | High | Augment dataset before training; use synthetic data for CI |
| Dependency version conflicts (scikit-learn) | Low | Medium | Pin versions in `requirements-test.txt`; test on CI |
| Team member unavailability | Low | Medium | Cross-training; pair programming for critical tasks |

---

## Summary

| Metric | Value |
|---|---|
| Total Expected Duration | ~79 days |
| Critical Path Duration | ~32 days |
| Critical Path % | 37.5% (> 15% requirement ✅) |
| Schedule Buffer (recommended) | 3–4 days |
| Highest Variance Tasks | 2b Frontend (σ²=1.78), 3b SVM Train (σ²=1.78) |
