"""
conftest.py – Shared fixtures for the Dayaw test suite.

Provides re-usable pytest fixtures for:
  - The TagalogToBaybayin translator
  - The trained SVM model and class-name list
  - Synthetic image / HOG-feature generators used when no real test images
    are available (keeps CI green without external data)
"""

import os
import sys

import joblib
import numpy as np
import pytest
from skimage.feature import hog

# Make the backend package importable from any working directory
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _d in (BACKEND_DIR, TESTS_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

from constants import BAYBAYIN_CLASSES, HOG_FEATURE_SIZE, HOG_PARAMS, IMAGE_SIZE


# ---------------------------------------------------------------------------
# Translator fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def ttb():
    """Return a ready-to-use TagalogToBaybayin translator."""
    from tagalog_to_baybayin import TagalogToBaybayin
    return TagalogToBaybayin()


# ---------------------------------------------------------------------------
# Model fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def model_path():
    return os.path.join(BACKEND_DIR, "baybayin_svm_model.sav")


@pytest.fixture(scope="session")
def class_names_path():
    return os.path.join(BACKEND_DIR, "class_names.sav")


@pytest.fixture(scope="session")
def svm_model(model_path):
    """Load and return the trained SVM model."""
    return joblib.load(model_path)


@pytest.fixture(scope="session")
def class_names(class_names_path):
    """Load and return the list of Baybayin class names."""
    return joblib.load(class_names_path)


# ---------------------------------------------------------------------------
# Synthetic data generators
# ---------------------------------------------------------------------------

@pytest.fixture
def make_synthetic_image():
    """Factory: returns a callable that creates random grayscale images."""
    def _make(size=IMAGE_SIZE, seed=None):
        rng = np.random.default_rng(seed)
        return rng.integers(0, 256, size, dtype=np.uint8)
    return _make


@pytest.fixture
def make_hog_features(make_synthetic_image):
    """Factory: returns a callable that creates HOG feature vectors."""
    def _make(n=1, seed=None):
        feats = []
        for i in range(n):
            img = make_synthetic_image(seed=None if seed is None else seed + i)
            feats.append(hog(img, **HOG_PARAMS))
        return np.array(feats)
    return _make


@pytest.fixture(scope="session")
def synthetic_eval_dataset(svm_model, class_names):
    """
    Session-scoped synthetic dataset for metrics tests.

    Generates N_PER_CLASS synthetic images per class, extracts HOG features,
    predicts with the SVM model, and returns (y_true_names, y_pred_names).
    """
    N_PER_CLASS = 5
    rng = np.random.default_rng(42)
    X, y_true_idx = [], []
    for idx in range(len(class_names)):
        for _ in range(N_PER_CLASS):
            img = rng.integers(0, 256, IMAGE_SIZE, dtype=np.uint8)
            X.append(hog(img, **HOG_PARAMS))
            y_true_idx.append(idx)

    y_pred_idx = svm_model.predict(X)

    y_true = [class_names[i] for i in y_true_idx]
    y_pred = [class_names[i] for i in y_pred_idx]
    return y_true, y_pred
