# Test Execution Report – Dayaw Baybayin Recognition & Translation System

## Report Metadata

| Field | Value |
|---|---|
| Project | Dayaw – Baybayin Recognition & Translation |
| Report Version | 1.0 |
| Prepared By | _(tester name)_ |
| Date of Execution | _(YYYY-MM-DD)_ |
| Environment | Ubuntu 22.04 / Python 3.11 (CI) or Windows 10 / Miniconda (local) |
| Tool | pytest 9.0+ with pytest-cov |

---

## Execution Command

```bash
# From repo root
cd backend
pytest tests/ -v \
  --tb=short \
  --cov=. \
  --cov-config=.coveragerc \
  --cov-report=term-missing \
  --cov-report=xml:tests/reports/coverage.xml \
  --cov-report=html:tests/reports/htmlcov \
  --cov-fail-under=85

# Generate performance/translation reports
python tests/model_evaluation_report.py
```

---

## Objective 1 – SVM Model Performance (HOG Features)

### Test Results

| Test ID | Test Name | Result | Notes |
|---|---|---|---|
| OBJ1-01 | `test_svm_model_file_exists` | PASS | |
| OBJ1-02 | `test_class_names_file_exists` | PASS | |
| OBJ1-03 | `test_model_file_is_not_empty` | PASS | |
| OBJ1-04 | `test_class_names_file_is_not_empty` | PASS | |
| OBJ1-05 | `test_model_loads_successfully` | PASS | |
| OBJ1-06 | `test_model_has_predict_method` | PASS | |
| OBJ1-07 | `test_model_has_predict_proba_method` | PASS | |
| OBJ1-08 | `test_model_feature_count_matches_hog` | PASS | |
| OBJ1-09 | `test_class_names_count_is_17` | PASS | |
| OBJ1-10 | `test_class_names_contain_expected_characters` | PASS | |
| OBJ1-11 | `test_model_has_17_support_vector_groups` | PASS | |
| OBJ1-12 | `test_hog_extracts_features` | PASS | |
| OBJ1-13 | `test_hog_feature_vector_length` | PASS | |
| OBJ1-14 | `test_hog_features_are_finite` | PASS | |
| OBJ1-15 | `test_hog_features_are_non_negative` | PASS | |
| OBJ1-16 | `test_hog_extraction_is_deterministic` | PASS | |
| OBJ1-17 | `test_hog_works_on_batch_of_images` | PASS | |
| OBJ1-18 | `test_predict_returns_valid_class_index` | PASS | |
| OBJ1-19 | `test_predict_maps_to_valid_class_name` | PASS | |
| OBJ1-20 | `test_predict_proba_length_is_17` | PASS | |
| OBJ1-21 | `test_predict_proba_sums_to_one` | PASS | |
| OBJ1-22 | `test_predict_proba_all_non_negative` | PASS | |
| OBJ1-23 | `test_predict_batch_matches_individual` | PASS | |
| OBJ1-24 | `test_accuracy_is_float_in_0_1` | PASS | |
| OBJ1-25 | `test_precision_is_computable` | PASS | |
| OBJ1-26 | `test_recall_is_computable` | PASS | |
| OBJ1-27 | `test_f1_score_is_computable` | PASS | |
| OBJ1-28 | `test_confusion_matrix_is_17x17` | PASS | |
| OBJ1-29 | `test_confusion_matrix_totals_match_sample_count` | PASS | |
| OBJ1-30 | `test_confusion_matrix_row_sums_equal_actual_class_counts` | PASS | |
| OBJ1-31 | `test_classification_report_contains_all_classes` | PASS | |
| OBJ1-32 | `test_per_character_precision_computed_for_all` | PASS | |
| OBJ1-33 | `test_per_character_recall_computed_for_all` | PASS | |
| OBJ1-34 | `test_per_character_f1_computed_for_all` | PASS | |
| OBJ1-35 | `test_printed_accuracy_is_float` | PASS | |
| OBJ1-36 | `test_handwritten_accuracy_is_float` | PASS | |
| OBJ1-37 | `test_printed_confusion_matrix_is_17x17` | PASS | |
| OBJ1-38 | `test_handwritten_confusion_matrix_is_17x17` | PASS | |
| OBJ1-39 | `test_separate_metrics_dict_built` | PASS | |
| OBJ1-40 | `test_reports_directory_is_created` | PASS | |
| OBJ1-41 | `test_metrics_json_can_be_written` | PASS | |
| OBJ1-42 | `test_confusion_matrix_png_can_be_saved` | PASS | |
| OBJ1-43 | `test_printed_vs_handwritten_json_can_be_saved` | PASS | |
| OBJ1-44 | `test_performance_report_html_can_be_generated` | PASS | |

**Objective 1 Pass Rate**: 44 / 44 = **100%**

### Metrics Summary (from `tests/reports/model_metrics.json`)

| Metric | Value | Threshold | Met? |
|---|---|---|---|
| Accuracy | _(from JSON)_ | ≥ 80% | _(✅ / ❌)_ |
| Precision (weighted) | _(from JSON)_ | ≥ 78% | _(✅ / ❌)_ |
| Recall (weighted) | _(from JSON)_ | ≥ 78% | _(✅ / ❌)_ |
| F1-Score (weighted) | _(from JSON)_ | ≥ 78% | _(✅ / ❌)_ |
| Confusion Matrix | 17×17 | 17×17 generated | ✅ |

> ⚠️ The values above are computed on synthetic HOG data (random images).
> Replace with labelled printed/handwritten test images for production evaluation.

---

## Objective 2 – Translation System (TTB & BTT)

### Test Results

| Test ID | Test Name | Result | Notes |
|---|---|---|---|
| OBJ2-01 | `test_empty_string_returns_empty` | PASS | |
| OBJ2-02 | `test_single_space_preserved` | PASS | |
| OBJ2-03 | `test_multiple_spaces_preserved` | PASS | |
| OBJ2-04 | `test_uppercase_input_normalised` | PASS | |
| OBJ2-05 | `test_mixed_case_normalised` | PASS | |
| OBJ2-06 | `test_leading_trailing_spaces_stripped` | PASS | |
| OBJ2-07 | `test_single_consonant_virama` | PASS | |
| OBJ2-08 | `test_single_vowel_a` | PASS | |
| OBJ2-09 to OBJ2-13 | `test_standalone_vowel[a/e/i/o/u]` (5 parametrised) | PASS | |
| OBJ2-14 | `test_ei_share_same_glyph` | PASS | |
| OBJ2-15 | `test_ou_share_same_glyph` | PASS | |
| OBJ2-16 | `test_vowel_sequence` | PASS | |
| OBJ2-17 to OBJ2-32 | `test_base_syllable[*]` (16 parametrised) | PASS | |
| OBJ2-33 | `test_ba_glyph_is_ba` | PASS | |
| OBJ2-34 | `test_nga_glyph_is_nga` | PASS | |
| OBJ2-35 | `test_da_and_ra_share_glyph` | PASS | |
| OBJ2-36 | `test_all_17_base_syllables_produce_output` | PASS | |
| OBJ2-37 to OBJ2-43 | Upper kudlit tests (7 parametrised) | PASS | |
| OBJ2-44 | `test_i_and_e_same_kudlit` | PASS | |
| OBJ2-45 | `test_ngiti` | PASS | |
| OBJ2-46 to OBJ2-51 | Lower kudlit tests (6 parametrised) | PASS | |
| OBJ2-52 | `test_o_and_u_same_kudlit` | PASS | |
| OBJ2-53 | `test_opo` | PASS | |
| OBJ2-54 to OBJ2-58 | Virama tests (5 parametrised) | PASS | |
| OBJ2-59 | `test_virama_character_used` | PASS | |
| OBJ2-60 | `test_standalone_ng_produces_virama` | PASS | |
| OBJ2-61 | `test_mga_exception` | PASS | |
| OBJ2-62 | `test_mga_uppercase_exception` | PASS | |
| OBJ2-63 | `test_ng_digraph_in_word` | PASS | |
| OBJ2-64 | `test_word_with_space` | PASS | |
| OBJ2-65 | `test_ilog` | PASS | |
| OBJ2-66 | `test_baya` | PASS | |
| OBJ2-67 | `test_translation_is_deterministic` | PASS | |
| OBJ2-68 | `test_all_base_syllables_non_empty` | PASS | |
| OBJ2-69 | `test_virama_only_on_final_consonants` | PASS | |
| OBJ2-70 | `test_pure_cv_pair_no_virama` | PASS | |
| OBJ2-71 | `test_kudlit_ei_only_for_ei_vowels` | PASS | |
| OBJ2-72 | `test_kudlit_ou_only_for_ou_vowels` | PASS | |
| OBJ2-73 | `test_da_equals_ra_for_all_vowels` | PASS | |
| OBJ2-74 | `test_e_equals_i_kudlit` | PASS | |
| OBJ2-75 | `test_o_equals_u_kudlit` | PASS | |
| OBJ2-76 | `test_space_in_output_when_space_in_input` | PASS | |
| OBJ2-77 to OBJ2-82 | `TestBTTWithMockPredictions` (6 tests) | PASS | |
| OBJ2-83 | `test_all_test_cases_pass` | PASS | |
| OBJ2-84 | `test_translation_accuracy_is_100_percent` | PASS | |
| OBJ2-85 | `test_translation_metrics_json_written` | PASS | |
| OBJ2-86 | `test_translation_confusion_matrix_png_written` | PASS | |
| OBJ2-87 | `test_coverage_summary_written` | PASS | |

**Objective 2 Pass Rate**: 87 / 87 = **100%**

### Coverage Summary (from `pytest --cov`)

| Module | Statements | Missed | Coverage |
|---|---|---|---|
| `tagalog_to_baybayin.py` | 39 | 0 | **100%** |
| `tests/conftest.py` | 57 | 0 | **100%** |
| `tests/constants.py` | 4 | 0 | **100%** |
| `tests/test_svm_model_performance.py` | 241 | 0 | **100%** |
| `tests/test_translation_system.py` | 226 | 0 | **100%** |
| **TOTAL** | **567** | **0** | **100%** ✅ |

---

## Overall Test Execution Summary

| Objective | Tests Run | Tests Passed | Tests Failed | Pass Rate |
|---|---|---|---|---|
| OBJ 1 – SVM Model | 44 | 44 | 0 | 100% |
| OBJ 2 – Translation | 87 | 87 | 0 | 100% |
| **TOTAL** | **131** | **131** | **0** | **100%** |

| Metric | Value |
|---|---|
| Total Execution Time | 6.70 seconds (CI) |
| Statement Coverage | 100% (567/567) |
| Coverage Threshold (85%) | ✅ Passed |
| Warnings | 1 (sklearn version mismatch – non-critical) |

---

## Generated Artefacts

After running `python tests/model_evaluation_report.py`, the following files are produced in
`backend/tests/reports/`:

| File | Description |
|---|---|
| `model_metrics.json` | SVM accuracy, precision, recall, F1 |
| `confusion_matrix.png` | 17×17 heatmap (synthetic data) |
| `printed_vs_handwritten_comparison.json` | Metrics split by style |
| `performance_report.html` | Interactive OBJ 1 dashboard |
| `translation_metrics.json` | TTB accuracy = 100%, target_met = true |
| `translation_confusion_matrix.png` | TTB confusion matrix heatmap |
| `coverage_summary.txt` | Code path summary |
| `htmlcov/index.html` | Full HTML coverage report |
| `coverage.xml` | Coverage XML (for CI badge) |

---

## Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| Tester | | | |
| Developer | | | |
| Supervisor / Adviser | | | |

---

## Defect Log

| Defect ID | Description | Severity | Status | Resolved In |
|---|---|---|---|---|
| _(no defects found in automated test run)_ | | | | |
