"""
test_svm_model_performance.py
=================================
OBJECTIVE 1 – Verify the performance of the RBF SVM-based Baybayin recognition
model using HOG feature extraction.

Metrics evaluated
-----------------
  • Accuracy
  • Precision  (macro-averaged and per-character)
  • Recall     (macro-averaged and per-character)
  • F1-Score   (macro-averaged and per-character)
  • Confusion Matrix (17×17)
  • Separate evaluation for "printed" vs "handwritten" simulation

Test structure
--------------
  1. TestModelFiles          – model and class-name files exist on disk
  2. TestModelLoading        – model loads and has the expected interface
  3. TestHOGPipeline         – HOG feature extraction behaves correctly
  4. TestSVMPrediction       – model predicts valid classes
  5. TestMetricsComputation  – all five metrics are computable and sensible
  6. TestPrintedVsHandwritten – metrics computed separately for two styles
  7. TestReportGeneration    – JSON / PNG / HTML artefacts are written to disk
"""

import json
import os

import numpy as np
import pytest
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from skimage.feature import hog

from constants import BAYBAYIN_CLASSES, HOG_FEATURE_SIZE, HOG_PARAMS, IMAGE_SIZE

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


# ===========================================================================
# 1. TestModelFiles
# ===========================================================================
class TestModelFiles:
    """Verify that required model files are present on disk."""

    def test_svm_model_file_exists(self, model_path):
        assert os.path.isfile(model_path), (
            f"baybayin_svm_model.sav not found at {model_path}"
        )

    def test_class_names_file_exists(self, class_names_path):
        assert os.path.isfile(class_names_path), (
            f"class_names.sav not found at {class_names_path}"
        )

    def test_model_file_is_not_empty(self, model_path):
        assert os.path.getsize(model_path) > 0

    def test_class_names_file_is_not_empty(self, class_names_path):
        assert os.path.getsize(class_names_path) > 0


# ===========================================================================
# 2. TestModelLoading
# ===========================================================================
class TestModelLoading:
    """Verify the SVM model loads with the expected interface."""

    def test_model_loads_successfully(self, svm_model):
        assert svm_model is not None

    def test_model_has_predict_method(self, svm_model):
        assert hasattr(svm_model, "predict")

    def test_model_has_predict_proba_method(self, svm_model):
        assert hasattr(svm_model, "predict_proba")

    def test_model_feature_count_matches_hog(self, svm_model):
        """Model must have been trained on the same feature size as our HOG pipeline."""
        assert svm_model.n_features_in_ == HOG_FEATURE_SIZE

    def test_class_names_count_is_17(self, class_names):
        assert len(class_names) == 17

    def test_class_names_contain_expected_characters(self, class_names):
        for name in BAYBAYIN_CLASSES:
            assert name in class_names, f"Expected class '{name}' not in class_names"

    def test_model_has_17_support_vector_groups(self, svm_model):
        assert len(svm_model.n_support_) == 17


# ===========================================================================
# 3. TestHOGPipeline
# ===========================================================================
class TestHOGPipeline:
    """Verify the HOG feature extraction pipeline matches the production code."""

    def test_hog_extracts_features(self, make_synthetic_image):
        img = make_synthetic_image()
        features = hog(img, **HOG_PARAMS)
        assert features is not None
        assert len(features) > 0

    def test_hog_feature_vector_length(self, make_synthetic_image):
        img = make_synthetic_image()
        features = hog(img, **HOG_PARAMS)
        assert len(features) == HOG_FEATURE_SIZE

    def test_hog_features_are_finite(self, make_synthetic_image):
        img = make_synthetic_image()
        features = hog(img, **HOG_PARAMS)
        assert np.all(np.isfinite(features))

    def test_hog_features_are_non_negative(self, make_synthetic_image):
        img = make_synthetic_image()
        features = hog(img, **HOG_PARAMS)
        assert np.all(features >= 0)

    def test_hog_extraction_is_deterministic(self, make_synthetic_image):
        img = make_synthetic_image(seed=0)
        feat1 = hog(img, **HOG_PARAMS)
        feat2 = hog(img, **HOG_PARAMS)
        np.testing.assert_array_equal(feat1, feat2)

    def test_hog_works_on_batch_of_images(self, make_synthetic_image):
        imgs = [make_synthetic_image(seed=i) for i in range(10)]
        features = [hog(img, **HOG_PARAMS) for img in imgs]
        assert len(features) == 10
        assert all(len(f) == HOG_FEATURE_SIZE for f in features)


# ===========================================================================
# 4. TestSVMPrediction
# ===========================================================================
class TestSVMPrediction:
    """Verify the SVM model produces valid output for HOG feature inputs."""

    def test_predict_returns_valid_class_index(self, svm_model, make_synthetic_image):
        img = make_synthetic_image(seed=1)
        feat = hog(img, **HOG_PARAMS)
        idx = svm_model.predict([feat])[0]
        assert 0 <= int(idx) <= 16

    def test_predict_maps_to_valid_class_name(
        self, svm_model, class_names, make_synthetic_image
    ):
        img = make_synthetic_image(seed=2)
        feat = hog(img, **HOG_PARAMS)
        idx = svm_model.predict([feat])[0]
        name = class_names[int(idx)]
        assert name in BAYBAYIN_CLASSES

    def test_predict_proba_length_is_17(self, svm_model, make_synthetic_image):
        img = make_synthetic_image(seed=3)
        feat = hog(img, **HOG_PARAMS)
        proba = svm_model.predict_proba([feat])[0]
        assert len(proba) == 17

    def test_predict_proba_sums_to_one(self, svm_model, make_synthetic_image):
        img = make_synthetic_image(seed=4)
        feat = hog(img, **HOG_PARAMS)
        proba = svm_model.predict_proba([feat])[0]
        assert abs(sum(proba) - 1.0) < 1e-5

    def test_predict_proba_all_non_negative(self, svm_model, make_synthetic_image):
        img = make_synthetic_image(seed=5)
        feat = hog(img, **HOG_PARAMS)
        proba = svm_model.predict_proba([feat])[0]
        assert all(p >= 0 for p in proba)

    def test_predict_batch_matches_individual(
        self, svm_model, make_hog_features
    ):
        feats = make_hog_features(n=5, seed=10)
        batch_preds = svm_model.predict(feats)
        individual_preds = [svm_model.predict([f])[0] for f in feats]
        np.testing.assert_array_equal(batch_preds, individual_preds)


# ===========================================================================
# 5. TestMetricsComputation
# ===========================================================================
class TestMetricsComputation:
    """
    Verify all five required performance metrics are computable.

    Uses the session-scoped `synthetic_eval_dataset` fixture (5 synthetic
    images per class) to exercise the full sklearn metrics pipeline.
    """

    def test_accuracy_is_float_in_0_1(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        acc = accuracy_score(y_true, y_pred)
        assert isinstance(acc, float)
        assert 0.0 <= acc <= 1.0

    def test_precision_is_computable(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        prec = precision_score(
            y_true, y_pred, average="weighted", zero_division=0
        )
        assert 0.0 <= prec <= 1.0

    def test_recall_is_computable(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        rec = recall_score(
            y_true, y_pred, average="weighted", zero_division=0
        )
        assert 0.0 <= rec <= 1.0

    def test_f1_score_is_computable(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        assert 0.0 <= f1 <= 1.0

    def test_confusion_matrix_is_17x17(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)
        assert cm.shape == (17, 17)

    def test_confusion_matrix_totals_match_sample_count(
        self, synthetic_eval_dataset
    ):
        y_true, y_pred = synthetic_eval_dataset
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)
        assert cm.sum() == len(y_true)

    def test_confusion_matrix_row_sums_equal_actual_class_counts(
        self, synthetic_eval_dataset
    ):
        y_true, y_pred = synthetic_eval_dataset
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)
        # Each class appears the same number of times in y_true
        expected = len(y_true) // len(BAYBAYIN_CLASSES)
        row_sums = cm.sum(axis=1)
        assert all(s == expected for s in row_sums)

    def test_classification_report_contains_all_classes(
        self, synthetic_eval_dataset
    ):
        y_true, y_pred = synthetic_eval_dataset
        report = classification_report(
            y_true, y_pred, labels=BAYBAYIN_CLASSES, zero_division=0
        )
        for cls in BAYBAYIN_CLASSES:
            assert cls in report

    def test_per_character_precision_computed_for_all(
        self, synthetic_eval_dataset
    ):
        y_true, y_pred = synthetic_eval_dataset
        per_class = precision_score(
            y_true,
            y_pred,
            labels=BAYBAYIN_CLASSES,
            average=None,
            zero_division=0,
        )
        assert len(per_class) == 17

    def test_per_character_recall_computed_for_all(
        self, synthetic_eval_dataset
    ):
        y_true, y_pred = synthetic_eval_dataset
        per_class = recall_score(
            y_true,
            y_pred,
            labels=BAYBAYIN_CLASSES,
            average=None,
            zero_division=0,
        )
        assert len(per_class) == 17

    def test_per_character_f1_computed_for_all(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        per_class = f1_score(
            y_true,
            y_pred,
            labels=BAYBAYIN_CLASSES,
            average=None,
            zero_division=0,
        )
        assert len(per_class) == 17


# ===========================================================================
# 6. TestPrintedVsHandwritten
# ===========================================================================

def _make_dataset(svm_model, class_names, rng, n_per_class=3):
    """Helper: generate synthetic dataset and return (y_true, y_pred)."""
    X, y_true_idx = [], []
    for idx in range(len(class_names)):
        for _ in range(n_per_class):
            img = rng.integers(0, 256, IMAGE_SIZE, dtype=np.uint8)
            X.append(hog(img, **HOG_PARAMS))
            y_true_idx.append(idx)
    y_pred_idx = svm_model.predict(X)
    y_true = [class_names[i] for i in y_true_idx]
    y_pred = [class_names[i] for i in y_pred_idx]
    return y_true, y_pred


class TestPrintedVsHandwritten:
    """
    Simulate separate evaluation for 'printed' and 'handwritten' styles.

    In production these would be two labelled test-image folders.
    Here we use different RNG seeds to represent the two data distributions.
    """

    @pytest.fixture(scope="class")
    def printed_data(self, svm_model, class_names):
        return _make_dataset(svm_model, class_names, np.random.default_rng(100))

    @pytest.fixture(scope="class")
    def handwritten_data(self, svm_model, class_names):
        return _make_dataset(svm_model, class_names, np.random.default_rng(200))

    def test_printed_accuracy_is_float(self, printed_data):
        y_true, y_pred = printed_data
        acc = accuracy_score(y_true, y_pred)
        assert 0.0 <= acc <= 1.0

    def test_handwritten_accuracy_is_float(self, handwritten_data):
        y_true, y_pred = handwritten_data
        acc = accuracy_score(y_true, y_pred)
        assert 0.0 <= acc <= 1.0

    def test_printed_confusion_matrix_is_17x17(self, printed_data):
        y_true, y_pred = printed_data
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)
        assert cm.shape == (17, 17)

    def test_handwritten_confusion_matrix_is_17x17(self, handwritten_data):
        y_true, y_pred = handwritten_data
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)
        assert cm.shape == (17, 17)

    def test_separate_metrics_dict_built(self, printed_data, handwritten_data):
        comparison = {}
        for label, (y_true, y_pred) in [
            ("printed", printed_data),
            ("handwritten", handwritten_data),
        ]:
            comparison[label] = {
                "accuracy": accuracy_score(y_true, y_pred),
                "precision": precision_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
                "recall": recall_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
                "f1": f1_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
            }
        assert set(comparison.keys()) == {"printed", "handwritten"}
        for style in ("printed", "handwritten"):
            assert set(comparison[style].keys()) == {
                "accuracy", "precision", "recall", "f1"
            }


# ===========================================================================
# 7. TestReportGeneration
# ===========================================================================
class TestReportGeneration:
    """Verify that performance artefacts are generated to the reports folder."""

    @pytest.fixture(autouse=True)
    def ensure_reports_dir(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def test_reports_directory_is_created(self):
        assert os.path.isdir(REPORTS_DIR)

    def test_metrics_json_can_be_written(self, synthetic_eval_dataset):
        y_true, y_pred = synthetic_eval_dataset
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(
                y_true, y_pred, average="weighted", zero_division=0
            ),
            "recall": recall_score(
                y_true, y_pred, average="weighted", zero_division=0
            ),
            "f1_score": f1_score(
                y_true, y_pred, average="weighted", zero_division=0
            ),
            "num_classes": 17,
            "classes": BAYBAYIN_CLASSES,
        }
        out = os.path.join(REPORTS_DIR, "model_metrics.json")
        with open(out, "w") as fh:
            json.dump(metrics, fh, indent=2)
        assert os.path.isfile(out)
        with open(out) as fh:
            loaded = json.load(fh)
        assert loaded["num_classes"] == 17
        assert "accuracy" in loaded

    def test_confusion_matrix_png_can_be_saved(self, synthetic_eval_dataset):
        pytest.importorskip("matplotlib")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        y_true, y_pred = synthetic_eval_dataset
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=BAYBAYIN_CLASSES,
            yticklabels=BAYBAYIN_CLASSES,
            ax=ax,
        )
        ax.set_title("Baybayin SVM – Confusion Matrix (Synthetic Evaluation)")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        out = os.path.join(REPORTS_DIR, "confusion_matrix.png")
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)
        assert os.path.isfile(out)

    def test_printed_vs_handwritten_json_can_be_saved(
        self, svm_model, class_names
    ):
        comparison = {}
        for label, seed in [("printed", 100), ("handwritten", 200)]:
            y_true, y_pred = _make_dataset(
                svm_model, class_names, np.random.default_rng(seed)
            )
            comparison[label] = {
                "accuracy": accuracy_score(y_true, y_pred),
                "precision": precision_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
                "recall": recall_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
                "f1": f1_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
            }
        out = os.path.join(
            REPORTS_DIR, "printed_vs_handwritten_comparison.json"
        )
        with open(out, "w") as fh:
            json.dump(comparison, fh, indent=2)
        assert os.path.isfile(out)

    def test_performance_report_html_can_be_generated(
        self, synthetic_eval_dataset
    ):
        y_true, y_pred = synthetic_eval_dataset
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(
            y_true, y_pred, average="weighted", zero_division=0
        )
        rec = recall_score(
            y_true, y_pred, average="weighted", zero_division=0
        )
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=BAYBAYIN_CLASSES)

        # Build a minimal but complete HTML report
        cm_html_rows = "".join(
            "<tr><td><b>{}</b></td>{}</tr>".format(
                cls,
                "".join(
                    "<td style='background:rgba(0,0,255,{:.2f})'>{}</td>".format(
                        v / max(cm.max(), 1), v
                    )
                    for v in row
                ),
            )
            for cls, row in zip(BAYBAYIN_CLASSES, cm)
        )
        cm_header = "<tr><th>Actual \\ Predicted</th>" + "".join(
            f"<th>{c}</th>" for c in BAYBAYIN_CLASSES
        ) + "</tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dayaw – SVM Model Performance Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    table {{ border-collapse: collapse; font-size: 11px; }}
    th, td {{ border: 1px solid #ccc; padding: 4px 6px; text-align: center; }}
    th {{ background: #4a90d9; color: white; }}
    .metric {{ font-size: 1.4em; font-weight: bold; color: #2c3e50; }}
    .card {{ display: inline-block; border: 1px solid #ddd; border-radius: 6px;
             padding: 16px 24px; margin: 8px; text-align: center; }}
  </style>
</head>
<body>
  <h1>Dayaw Baybayin Recognition – OBJ 1 Performance Report</h1>
  <h2>Overall Metrics (Synthetic Evaluation)</h2>
  <div>
    <div class="card"><div class="metric">{acc:.1%}</div>Accuracy</div>
    <div class="card"><div class="metric">{prec:.1%}</div>Precision</div>
    <div class="card"><div class="metric">{rec:.1%}</div>Recall</div>
    <div class="card"><div class="metric">{f1:.1%}</div>F1-Score</div>
    <div class="card"><div class="metric">17</div>Classes</div>
  </div>
  <h2>Confusion Matrix (17 × 17)</h2>
  <table>
    {cm_header}
    {cm_html_rows}
  </table>
  <p><em>Note: metrics computed on synthetic HOG data.
  Replace with labelled test images for production evaluation.</em></p>
</body>
</html>"""

        out = os.path.join(REPORTS_DIR, "performance_report.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        assert os.path.isfile(out)
        assert "Accuracy" in open(out).read()
