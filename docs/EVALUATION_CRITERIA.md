# Evaluation Criteria – Dayaw Baybayin Recognition & Translation System

## Overview

This document defines the measurable success criteria for each objective of the Dayaw project.
All thresholds must be verified via the automated test suite located in `backend/tests/`.

---

## Objective 1 – RBF SVM Baybayin Recognition Model Performance (HOG Features)

**Goal**: Determine the performance of the RBF SVM-based Baybayin recognition model using HOG
feature extraction.

| Metric | Threshold | Measurement Method | Evidence |
|---|---|---|---|
| Model Accuracy | ≥ 80% | Test set confusion matrix | `tests/reports/model_metrics.json` |
| Precision (per character) | ≥ 78% | scikit-learn `precision_score` | `TestMetricsComputation` in `test_svm_model_performance.py` |
| Recall (per character) | ≥ 78% | scikit-learn `recall_score` | `TestMetricsComputation` in `test_svm_model_performance.py` |
| F1-Score | ≥ 78% | scikit-learn `f1_score` | `TestMetricsComputation` in `test_svm_model_performance.py` |
| Confusion Matrix | 17×17 generated | `confusion_matrix(labels=BAYBAYIN_CLASSES)` | `tests/reports/confusion_matrix.png` |
| Printed vs Handwritten | ≥ 5% difference analysed | Separate seed-based dataset evaluation | `tests/reports/printed_vs_handwritten_comparison.json` |

**Success Criteria**: All 5 metrics must meet thresholds AND all report artefacts generated.

### Evidence Collection
- Run `pytest tests/ -v --cov=. --cov-report=term-missing`
- Run `python tests/model_evaluation_report.py`
- Inspect `tests/reports/model_metrics.json` for metric values
- Inspect `tests/reports/confusion_matrix.png` for 17×17 heatmap
- Inspect `tests/reports/printed_vs_handwritten_comparison.json` for comparison data

---

## Objective 2 – TTB & BTT Translation System Effectiveness

**Goal**: Evaluate the effectiveness of the Tagalog-to-Baybayin (TTB) and Baybayin-to-Tagalog
(BTT) translation system through unit testing and statistical validation.

| Metric | Threshold | Measurement Method | Evidence |
|---|---|---|---|
| Rule-Based Consistency | 100% of 17 syllables mapped correctly | Parametrised unit tests | `TestTTBBaseSyllables`, `TestRuleBasedConsistency` |
| Statement Coverage | ≥ 85% | `pytest --cov` with `.coveragerc` | `tests/reports/coverage.xml`, `htmlcov/` |
| Classification Accuracy | ≥ 95% | Translation accuracy over 33 test cases | `TestTranslationAccuracy::test_translation_accuracy_is_100_percent` |
| Confusion Matrix | Generated for all syllable translations | `sklearn.metrics.confusion_matrix` | `tests/reports/translation_confusion_matrix.png` |
| Automated Unit Tests | ≥ 25 tests, all PASSED | `pytest tests/test_translation_system.py -v` | Terminal output / CI artefacts |

**Success Criteria**: Statement coverage ≥ 85%, all tests PASS, classification accuracy ≥ 95%.

### Evidence Collection
- Run `pytest tests/test_translation_system.py -v` → verify ≥ 25 PASSED
- Check coverage output for `tagalog_to_baybayin.py` ≥ 85%
- Inspect `tests/reports/translation_metrics.json` for `"target_met": true`
- Inspect `tests/reports/translation_confusion_matrix.png`

---

## Objective 3 – Comprehensive Testing Framework for System Validation

**Goal**: Design and implement a comprehensive testing framework for system validation.

| Metric | Threshold | Measurement Method | Evidence |
|---|---|---|---|
| Test Case Count | ≥ 30 pytest test cases | `pytest --collect-only` | Terminal output |
| Code Coverage – Critical Modules | 100% for `tagalog_to_baybayin.py`, `tests/conftest.py`, `tests/constants.py` | `--cov-report=term-missing` | Coverage report |
| CI/CD Pipeline | Runs on every commit via GitHub Actions | `.github/workflows/test.yml` | GitHub Actions dashboard |
| Test Execution Time | < 30 seconds | pytest timing output | `pytest -v` duration line |
| HTML Reports | Generated for model performance and translation accuracy | `model_evaluation_report.py` | `tests/reports/performance_report.html`, `tests/reports/translation_confusion_matrix.png` |

**Success Criteria**: All tests automated and passing with < 30 s total execution time.

### Evidence Collection
- `pytest tests/ --collect-only | grep "test session starts"` → count collected items
- Check GitHub Actions run results in `.github/workflows/test.yml`
- Verify `tests/reports/performance_report.html` and `tests/reports/htmlcov/index.html` exist

---

## Objective 4 – White Box & Black Box Testing

**Goal**: Perform White Box and Black Box Testing on the Baybayin recognition and translation
system.

### White Box Testing

| Metric | Threshold | Measurement Method | Evidence |
|---|---|---|---|
| Statement Coverage (core modules) | ≥ 85% | `pytest --cov --cov-fail-under=85` | Coverage report |
| Branch Coverage | All if/else paths exercised | Manual path analysis + `--cov-branch` | Coverage HTML report |
| Boundary Value Tests | Min/max image sizes and character counts tested | `TestHOGPipeline`, `TestTTBEdgeCases` | Test results |
| Decision Point Tests | All if/else branches exercised | `TestRuleBasedConsistency`, virama/kudlit tests | Test results |

**White Box Success**: Coverage ≥ 85%, all code paths covered.

### Black Box Testing

| Metric | Threshold | Measurement Method | Evidence |
|---|---|---|---|
| Functional Test Cases | ≥ 20 test cases covering upload, translate, recognise | `TestBTTWithMockPredictions`, `TestTranslationAccuracy` | Test results |
| Error Handling | Invalid inputs handled (blank image, non-Baybayin, corrupted) | Edge-case tests in `TestTTBEdgeCases` | Test results |
| Performance | Response time < 2 seconds per operation | `model_evaluation_report.py` runtime | Execution timing |
| Usability | User completes workflow in < 3 steps | Manual UX walkthrough | UX documentation |
| Integration | End-to-end: image upload → recognition → translation | `TestBTTWithMockPredictions` pipeline | Test results |

**Black Box Success**: All 20+ test cases PASS, error handling robust.

### Evidence Collection
- See `docs/OBJECTIVE_4_TESTING_PLAN.md` for detailed test case listing
- Run `pytest tests/ -v` and count test IDs ≥ 20 functional cases
- Check `--cov-fail-under=85` passes in CI

---

## Global Pass/Fail Summary

| Objective | Key Threshold | Status Field |
|---|---|---|
| OBJ 1 – SVM Model | Accuracy ≥ 80%, F1 ≥ 78% | `tests/reports/model_metrics.json → "accuracy"` |
| OBJ 2 – Translation | Accuracy ≥ 95%, Coverage ≥ 85%, 25+ tests pass | `tests/reports/translation_metrics.json → "target_met"` |
| OBJ 3 – Framework | ≥ 30 tests, < 30 s, CI green | GitHub Actions badge |
| OBJ 4 – WB/BB Testing | WB ≥ 85% coverage, BB 20+ cases pass | Coverage XML + pytest output |
