"""
test_archival_system.py
========================
OBJECTIVE 3 — Comprehensive Archival System Test Suite

Unit tests (A1–A6) and Integration tests (IT1–IT4) for the Baybayin
Archival Preservation System implemented in ``archival_manager.py``.

Test map
--------
  A1: Confidence Scoring with ≥90% Accuracy → archived
  A2: Rejection with <90% Accuracy → rejected, no files written
  A3: Character Extraction — multi-character word ("halimbawa")
  A4: Character Extraction — virama detection ("salamat")
  A5: Metadata Completeness — all 9 required fields present
  A6: Duplicate Prevention — MD5-based deduplication

  IT1: End-to-End Workflow (upload → process → archive)
  IT2: Character Extraction + Storage (folder structure verification)
  IT3: Feedback Pipeline (<90% → reject message, ≥90% → archive dialog)
  IT4: Archival Acceptance Rate (10 submissions at varying accuracies)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Ensure backend is importable
# ---------------------------------------------------------------------------
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from archival_manager import ArchivalSystem  # noqa: E402

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _blank_png(width: int = 100, height: int = 100) -> bytes:
    """Return a minimal valid PNG as raw bytes (white image)."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    success, buf = cv2.imencode(".png", img)
    assert success
    return buf.tobytes()


def _mock_predictions(confidence_pct: float, n: int = 3) -> list[dict]:
    """Return *n* mock predictions all with *confidence_pct* (0–100)."""
    return [{"char": "BA", "confidence": confidence_pct} for _ in range(n)]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_archiver(tmp_path):
    """Return an ArchivalSystem wired to an isolated temporary directory."""
    return ArchivalSystem(archive_root=str(tmp_path), accuracy_threshold=0.90)


# ===========================================================================
# A1: Confidence Scoring with ≥90% Accuracy
# ===========================================================================
class TestA1HighConfidenceArchived:
    """A1 — SVM confidence ≥ 90% → session archived."""

    def test_compute_confidence_score_above_threshold(self, tmp_archiver):
        predictions = _mock_predictions(95.0, n=5)
        score = tmp_archiver.compute_confidence_score(predictions)
        assert score >= 0.90, (
            f"Expected confidence ≥ 0.90, got {score:.4f}"
        )

    def test_should_archive_returns_true(self, tmp_archiver):
        assert tmp_archiver.should_archive(0.95) is True

    def test_should_archive_exactly_at_threshold(self, tmp_archiver):
        assert tmp_archiver.should_archive(0.90) is True

    def test_process_submission_status_archived(self, tmp_archiver):
        image_bytes = _blank_png()
        predictions = _mock_predictions(95.0, n=3)
        result = tmp_archiver.process_submission(
            image_bytes=image_bytes,
            word="ba",
            contributor_id="test-user",
            predictions=predictions,
        )
        assert result["status"] == "archived"

    def test_process_submission_returns_session_id(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="test-user",
            predictions=_mock_predictions(92.0),
        )
        assert result["session_id"] is not None
        assert len(result["session_id"]) > 0

    def test_process_submission_accuracy_in_result(self, tmp_archiver):
        predictions = _mock_predictions(94.0, n=4)
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="baba",
            contributor_id="test-user",
            predictions=predictions,
        )
        assert result["overall_accuracy"] == pytest.approx(0.94, abs=1e-4)


# ===========================================================================
# A2: Rejection with <90% Accuracy
# ===========================================================================
class TestA2LowConfidenceRejected:
    """A2 — SVM confidence < 90% → session rejected, no files written."""

    def test_compute_confidence_score_below_threshold(self, tmp_archiver):
        predictions = _mock_predictions(75.0, n=5)
        score = tmp_archiver.compute_confidence_score(predictions)
        assert score < 0.90

    def test_should_archive_returns_false(self, tmp_archiver):
        assert tmp_archiver.should_archive(0.75) is False

    def test_should_archive_just_below_threshold(self, tmp_archiver):
        assert tmp_archiver.should_archive(0.8999) is False

    def test_process_submission_status_rejected(self, tmp_archiver, tmp_path):
        image_bytes = _blank_png()
        result = tmp_archiver.process_submission(
            image_bytes=image_bytes,
            word="ba",
            contributor_id="test-user",
            predictions=_mock_predictions(75.0),
        )
        assert result["status"] == "rejected"

    def test_no_files_written_on_rejection(self, tmp_archiver, tmp_path):
        image_bytes = _blank_png()
        tmp_archiver.process_submission(
            image_bytes=image_bytes,
            word="ba",
            contributor_id="test-user",
            predictions=_mock_predictions(60.0),
        )
        captured_dir = os.path.join(str(tmp_path), "Captured")
        # No session sub-directories should have been created
        session_dirs = [
            d for d in os.listdir(captured_dir)
            if os.path.isdir(os.path.join(captured_dir, d))
        ]
        assert len(session_dirs) == 0, (
            f"Expected no files in Captured/, found: {session_dirs}"
        )

    def test_rejection_message_contains_threshold_info(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="test-user",
            predictions=_mock_predictions(80.0),
        )
        assert "90%" in result["message"] or "threshold" in result["message"].lower()


# ===========================================================================
# A3: Character Extraction — Multi-character Word
# ===========================================================================
class TestA3SegmentMultiCharWord:
    """A3 — 'halimbawa' segments into ['ha', 'li', 'm', 'ba', 'wa']."""

    def test_halimbawa_segmentation(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("halimbawa")
        assert result == ["ha", "li", "m", "ba", "wa"], (
            f"Expected ['ha', 'li', 'm', 'ba', 'wa'], got {result}"
        )

    def test_halimbawa_length(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("halimbawa")
        assert len(result) == 5

    def test_baya_segmentation(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("baya")
        assert result == ["ba", "ya"]

    def test_ngiti_segmentation(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("ngiti")
        assert result == ["ngi", "ti"]

    def test_opo_segmentation(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("opo")
        assert result == ["o", "po"]

    def test_empty_string_returns_empty_list(self, tmp_archiver):
        assert tmp_archiver.segment_baybayin_word("") == []

    def test_single_vowel(self, tmp_archiver):
        assert tmp_archiver.segment_baybayin_word("a") == ["a"]

    def test_uppercase_input_normalised(self, tmp_archiver):
        lower = tmp_archiver.segment_baybayin_word("halimbawa")
        upper = tmp_archiver.segment_baybayin_word("HALIMBAWA")
        assert lower == upper


# ===========================================================================
# A4: Character Extraction — Virama Detection
# ===========================================================================
class TestA4ViramaDetection:
    """A4 — 'salamat' → ['sa', 'la', 'ma', 't'] where 't' is a standalone
    consonant (maps to virama in Baybayin)."""

    def test_salamat_segmentation(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("salamat")
        assert result == ["sa", "la", "ma", "t"], (
            f"Expected ['sa', 'la', 'ma', 't'], got {result}"
        )

    def test_salamat_final_element_is_consonant(self, tmp_archiver):
        result = tmp_archiver.segment_baybayin_word("salamat")
        assert result[-1] == "t"

    def test_ang_segmentation(self, tmp_archiver):
        # 'ang' → a + ng (ng is standalone → virama)
        result = tmp_archiver.segment_baybayin_word("ang")
        assert result == ["a", "ng"]

    def test_final_consonant_is_single_char(self, tmp_archiver):
        for word, expected_last in [("salamat", "t"), ("ilog", "g"), ("alab", "b")]:
            result = tmp_archiver.segment_baybayin_word(word)
            assert result[-1] == expected_last, (
                f"Word '{word}': expected last unit '{expected_last}', "
                f"got '{result[-1]}'"
            )

    def test_word_without_virama(self, tmp_archiver):
        # 'baya' ends with a vowel so no virama
        result = tmp_archiver.segment_baybayin_word("baya")
        # None of the units should be a single consonant
        for unit in result:
            if len(unit) == 1:
                assert unit in "aeiou", (
                    f"Unexpected standalone consonant '{unit}' in 'baya'"
                )


# ===========================================================================
# A5: Metadata Completeness
# ===========================================================================
class TestA5MetadataCompleteness:
    """A5 — Archived session metadata must contain all 9 mandatory fields."""

    REQUIRED_FIELDS = {
        "session_id",
        "contributor_id",
        "timestamp",
        "word",
        "characters",
        "accuracy_scores",
        "overall_accuracy",
        "status",
        "source_file",
    }

    def test_metadata_contains_all_9_fields(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="halimbawa",
            contributor_id="user-abc123",
            predictions=_mock_predictions(96.0, n=5),
        )
        assert result["status"] == "archived"
        meta = result["metadata"]
        missing = self.REQUIRED_FIELDS - set(meta.keys())
        assert not missing, f"Missing metadata fields: {missing}"

    def test_all_metadata_fields_non_null(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="halimbawa",
            contributor_id="user-abc123",
            predictions=_mock_predictions(93.0, n=5),
        )
        meta = result["metadata"]
        for field in self.REQUIRED_FIELDS:
            assert meta[field] is not None, (
                f"Field '{field}' is None"
            )

    def test_metadata_json_valid_and_written_to_disk(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-test",
            predictions=_mock_predictions(91.0, n=1),
        )
        session_id = result["session_id"]
        meta_file = os.path.join(
            str(tmp_path), "Metadata", session_id, "session_meta.json"
        )
        assert os.path.isfile(meta_file), (
            f"Expected metadata file at {meta_file}"
        )
        with open(meta_file, encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert loaded["session_id"] == session_id

    def test_metadata_status_is_archived(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-test",
            predictions=_mock_predictions(95.0),
        )
        assert result["metadata"]["status"] == "archived"

    def test_metadata_word_matches_input(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ngiti",
            contributor_id="user-test",
            predictions=_mock_predictions(97.0, n=3),
        )
        assert result["metadata"]["word"] == "ngiti"

    def test_metadata_overall_accuracy_in_range(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-test",
            predictions=_mock_predictions(92.0),
        )
        acc = result["metadata"]["overall_accuracy"]
        assert 0.0 <= acc <= 1.0


# ===========================================================================
# A6: Duplicate Prevention
# ===========================================================================
class TestA6DuplicatePrevention:
    """A6 — Submitting an identical image twice is detected and blocked."""

    def test_duplicate_returns_duplicate_status(self, tmp_archiver):
        image_bytes = _blank_png()
        predictions = _mock_predictions(95.0)
        # First submission
        r1 = tmp_archiver.process_submission(
            image_bytes=image_bytes,
            word="ba",
            contributor_id="user-x",
            predictions=predictions,
        )
        assert r1["status"] == "archived"
        # Second identical submission
        r2 = tmp_archiver.process_submission(
            image_bytes=image_bytes,
            word="ba",
            contributor_id="user-x",
            predictions=predictions,
        )
        assert r2["status"] == "duplicate"

    def test_duplicate_message_contains_duplicate_text(self, tmp_archiver):
        image_bytes = _blank_png()
        predictions = _mock_predictions(92.0)
        tmp_archiver.process_submission(
            image_bytes=image_bytes, word="ba",
            contributor_id="u", predictions=predictions,
        )
        r2 = tmp_archiver.process_submission(
            image_bytes=image_bytes, word="ba",
            contributor_id="u", predictions=predictions,
        )
        assert "duplicate" in r2["message"].lower()

    def test_no_new_files_written_on_duplicate(self, tmp_archiver, tmp_path):
        image_bytes = _blank_png()
        predictions = _mock_predictions(93.0)
        tmp_archiver.process_submission(
            image_bytes=image_bytes, word="ba",
            contributor_id="u", predictions=predictions,
        )
        # Count files in Captured/ after first submission
        captured_dir = os.path.join(str(tmp_path), "Captured")
        count_before = sum(
            len(files) for _, _, files in os.walk(captured_dir)
        )
        # Duplicate submission
        tmp_archiver.process_submission(
            image_bytes=image_bytes, word="ba",
            contributor_id="u", predictions=predictions,
        )
        count_after = sum(
            len(files) for _, _, files in os.walk(captured_dir)
        )
        assert count_before == count_after, (
            "Duplicate submission should not write new files"
        )

    def test_different_images_not_flagged_as_duplicate(self, tmp_archiver):
        img1 = _blank_png(100, 100)
        img2 = _blank_png(200, 200)
        predictions = _mock_predictions(95.0)
        r1 = tmp_archiver.process_submission(
            image_bytes=img1, word="ba",
            contributor_id="u", predictions=predictions,
        )
        r2 = tmp_archiver.process_submission(
            image_bytes=img2, word="ba",
            contributor_id="u", predictions=predictions,
        )
        assert r1["status"] == "archived"
        assert r2["status"] == "archived"

    def test_md5_hash_uniqueness(self):
        img1 = _blank_png(100, 100)
        img2 = _blank_png(200, 200)
        h1 = hashlib.md5(img1).hexdigest()
        h2 = hashlib.md5(img2).hexdigest()
        assert h1 != h2


# ===========================================================================
# IT1: End-to-End Workflow
# ===========================================================================
class TestIT1EndToEndWorkflow:
    """IT1 — Full pipeline: upload → process → archive all three storage tiers."""

    def test_full_image_saved_to_captured(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="halimbawa",
            contributor_id="user-it1",
            predictions=_mock_predictions(96.0, n=5),
        )
        assert result["status"] == "archived"
        session_id = result["session_id"]
        captured_dir = os.path.join(str(tmp_path), "Captured", session_id)
        assert os.path.isdir(captured_dir)
        files = os.listdir(captured_dir)
        assert len(files) == 1
        assert files[0].endswith(".png")

    def test_characters_saved_to_characters_folder(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-it1",
            predictions=_mock_predictions(94.0, n=1),
        )
        assert result["status"] == "archived"
        characters_dir = os.path.join(str(tmp_path), "Characters")
        char_dirs = os.listdir(characters_dir)
        assert len(char_dirs) >= 1

    def test_metadata_saved_to_metadata_folder(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="baya",
            contributor_id="user-it1",
            predictions=_mock_predictions(95.0, n=2),
        )
        session_id = result["session_id"]
        meta_file = os.path.join(
            str(tmp_path), "Metadata", session_id, "session_meta.json"
        )
        assert os.path.isfile(meta_file)

    def test_archive_path_returned_in_result(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-it1",
            predictions=_mock_predictions(91.0),
        )
        assert result["archive_path"] is not None
        assert os.path.isdir(result["archive_path"])


# ===========================================================================
# IT2: Character Extraction + Storage
# ===========================================================================
class TestIT2CharacterExtractionStorage:
    """IT2 — Characters from 'halimbawa' land in correct sub-folders."""

    def test_character_sub_folders_created(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="halimbawa",
            contributor_id="user-it2",
            predictions=_mock_predictions(96.0, n=5),
        )
        assert result["status"] == "archived"
        # Expected characters from segment_baybayin_word("halimbawa")
        expected_labels = {"ha", "li", "m", "ba", "wa"}
        characters_dir = os.path.join(str(tmp_path), "Characters")
        created_labels = set(os.listdir(characters_dir))
        assert expected_labels.issubset(created_labels), (
            f"Missing character folders: {expected_labels - created_labels}"
        )

    def test_character_files_named_with_session_id(self, tmp_archiver, tmp_path):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-it2",
            predictions=_mock_predictions(92.0, n=1),
        )
        session_id = result["session_id"]
        char_dir = os.path.join(str(tmp_path), "Characters", "ba")
        assert os.path.isdir(char_dir)
        files = os.listdir(char_dir)
        assert any(session_id in f for f in files), (
            f"No file containing session_id '{session_id}' in {files}"
        )

    def test_segment_produces_correct_count(self, tmp_archiver):
        result_chars = tmp_archiver.segment_baybayin_word("halimbawa na")
        # halimbawa → 5 (ha,li,m,ba,wa), space skipped, na → 1 = 6
        assert len(result_chars) == 6


# ===========================================================================
# IT3: Feedback Pipeline
# ===========================================================================
class TestIT3FeedbackPipeline:
    """IT3 — Accuracy gate drives correct user feedback messages."""

    def test_below_threshold_returns_rejection_message(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-it3",
            predictions=_mock_predictions(70.0),
        )
        assert result["status"] == "rejected"
        assert len(result["message"]) > 0

    def test_above_threshold_returns_archive_invitation(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-it3",
            predictions=_mock_predictions(92.0),
        )
        assert result["status"] == "archived"
        msg = result["message"].lower()
        assert "archive" in msg or "contribut" in msg

    def test_feedback_message_is_non_empty(self, tmp_archiver):
        for conf in [60.0, 92.0]:
            result = tmp_archiver.process_submission(
                image_bytes=_blank_png(),
                word="ba",
                contributor_id="user-it3",
                predictions=_mock_predictions(conf),
            )
            assert result["message"] != ""

    def test_rejection_includes_accuracy_info(self, tmp_archiver):
        result = tmp_archiver.process_submission(
            image_bytes=_blank_png(),
            word="ba",
            contributor_id="user-it3",
            predictions=_mock_predictions(55.0),
        )
        # Message must mention accuracy or threshold
        msg = result["message"].lower()
        assert any(kw in msg for kw in ("accuracy", "threshold", "90", "%")), (
            f"Rejection message does not mention accuracy: '{result['message']}'"
        )


# ===========================================================================
# IT4: Archival Acceptance Rate
# ===========================================================================
class TestIT4ArchivalAcceptanceRate:
    """IT4 — Track archival acceptance rate across 10 varying submissions."""

    # 6 above threshold, 4 below — expected acceptance ≥ 60%
    SUBMISSION_CONFIDENCES = [
        95.0,  # archived
        40.0,  # rejected
        92.0,  # archived
        88.0,  # rejected
        97.0,  # archived
        75.0,  # rejected
        91.0,  # archived
        65.0,  # rejected
        93.0,  # archived
        90.0,  # archived
    ]
    EXPECTED_ARCHIVED = 6

    def test_10_submissions_correct_archived_count(self, tmp_path):
        archiver = ArchivalSystem(
            archive_root=str(tmp_path), accuracy_threshold=0.90
        )
        archived = 0
        for i, conf in enumerate(self.SUBMISSION_CONFIDENCES):
            # Use slightly different images to avoid duplicate detection
            img_bytes = _blank_png(100 + i, 100 + i)
            result = archiver.process_submission(
                image_bytes=img_bytes,
                word="ba",
                contributor_id=f"user-{i}",
                predictions=_mock_predictions(conf),
            )
            if result["status"] == "archived":
                archived += 1
        assert archived == self.EXPECTED_ARCHIVED, (
            f"Expected {self.EXPECTED_ARCHIVED} archived, got {archived}"
        )

    def test_acceptance_rate_meets_60_percent_target(self, tmp_path):
        archiver = ArchivalSystem(
            archive_root=str(tmp_path), accuracy_threshold=0.90
        )
        archived = 0
        for i, conf in enumerate(self.SUBMISSION_CONFIDENCES):
            img_bytes = _blank_png(100 + i, 100 + i)
            result = archiver.process_submission(
                image_bytes=img_bytes,
                word="ba",
                contributor_id=f"user-{i}",
                predictions=_mock_predictions(conf),
            )
            if result["status"] == "archived":
                archived += 1
        rate = archived / len(self.SUBMISSION_CONFIDENCES)
        assert rate >= 0.60, (
            f"Acceptance rate {rate:.0%} is below 60% target"
        )

    def test_acceptance_rate_metric_saved_to_reports(self, tmp_path):
        archiver = ArchivalSystem(
            archive_root=str(tmp_path), accuracy_threshold=0.90
        )
        archived = 0
        for i, conf in enumerate(self.SUBMISSION_CONFIDENCES):
            img_bytes = _blank_png(100 + i, 100 + i)
            result = archiver.process_submission(
                image_bytes=img_bytes,
                word="ba",
                contributor_id=f"user-{i}",
                predictions=_mock_predictions(conf),
            )
            if result["status"] == "archived":
                archived += 1

        rate = archived / len(self.SUBMISSION_CONFIDENCES)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        report = {
            "total_submissions": len(self.SUBMISSION_CONFIDENCES),
            "archived": archived,
            "rejected": len(self.SUBMISSION_CONFIDENCES) - archived,
            "acceptance_rate": rate,
            "target_rate": 0.60,
            "target_met": rate >= 0.60,
        }
        out = os.path.join(REPORTS_DIR, "archival_acceptance_rate.json")
        with open(out, "w") as fh:
            json.dump(report, fh, indent=2)
        assert os.path.isfile(out)
        with open(out) as fh:
            loaded = json.load(fh)
        assert loaded["target_met"] is True


# ===========================================================================
# Additional unit tests for ArchivalSystem helper methods
# ===========================================================================
class TestArchivalSystemHelpers:
    """Low-level unit tests for scoring and utility methods."""

    def test_compute_confidence_score_empty(self, tmp_archiver):
        assert tmp_archiver.compute_confidence_score([]) == 0.0

    def test_compute_confidence_score_single(self, tmp_archiver):
        score = tmp_archiver.compute_confidence_score(
            [{"char": "BA", "confidence": 80.0}]
        )
        assert score == pytest.approx(0.80)

    def test_compute_similarity_score_identical_vectors(self, tmp_archiver):
        v = np.ones(576)
        assert tmp_archiver.compute_similarity_score(v, v) == pytest.approx(1.0)

    def test_compute_similarity_score_orthogonal_vectors(self, tmp_archiver):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert tmp_archiver.compute_similarity_score(a, b) == pytest.approx(0.0)

    def test_compute_similarity_score_zero_vector(self, tmp_archiver):
        a = np.zeros(10)
        b = np.ones(10)
        assert tmp_archiver.compute_similarity_score(a, b) == 0.0

    def test_compute_similarity_score_in_range(self, tmp_archiver):
        rng = np.random.default_rng(42)
        a = rng.random(576)
        b = rng.random(576)
        score = tmp_archiver.compute_similarity_score(a, b)
        assert 0.0 <= score <= 1.0

    def test_extract_character_images_invalid_bytes(self, tmp_archiver):
        result = tmp_archiver.extract_character_images(b"not-an-image")
        assert result == []

    def test_extract_character_images_valid_image(self, tmp_archiver):
        result = tmp_archiver.extract_character_images(_blank_png())
        # White image has no contours → empty list is acceptable
        assert isinstance(result, list)

    def test_save_metadata_creates_json(self, tmp_archiver, tmp_path):
        meta = {
            "session_id": "test-sid",
            "contributor_id": "u",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "word": "ba",
            "characters": ["ba"],
            "accuracy_scores": {"ba": 0.95},
            "overall_accuracy": 0.95,
            "status": "archived",
            "source_file": "Captured/test-sid/file.png",
        }
        fpath = tmp_archiver.save_metadata("test-sid", meta)
        assert os.path.isfile(fpath)
        with open(fpath) as fh:
            loaded = json.load(fh)
        assert loaded["session_id"] == "test-sid"

    def test_folder_structure_created_on_init(self, tmp_path):
        archiver = ArchivalSystem(archive_root=str(tmp_path))
        for sub in ("Captured", "Characters", "Metadata"):
            assert os.path.isdir(os.path.join(str(tmp_path), sub))
