"""
archival_manager.py
====================
OBJECTIVE 3 — Baybayin Archival Preservation System

Core archival module that:
  1. Evaluates handwriting accuracy via SVM confidence scoring
  2. Applies a 90% accuracy gate before contributing to the archive
  3. Extracts and stores individual syllabic characters
  4. Saves provenance metadata for every archived artefact
  5. Prevents duplicate submissions via MD5-based deduplication

Usage
-----
    from archival_manager import ArchivalSystem
    archiver = ArchivalSystem()
    result = archiver.process_submission(
        image_bytes=...,
        word="halimbawa",
        contributor_id="user-abc123",
    )
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import cv2
import numpy as np
from skimage.feature import hog

# ---------------------------------------------------------------------------
# Valid Baybayin character labels (17 base + virama)
# ---------------------------------------------------------------------------
VALID_CHARACTERS: list[str] = [
    "a", "ba", "ka", "da", "ga", "ha", "la", "ma", "na",
    "nga", "pa", "ra", "sa", "ta", "wa", "ya", "ei", "virama",
]

# Tagalog syllable-segmentation helpers
# Consonants that form CV syllables with a following vowel
_CONSONANTS = list("bkdghlmnprstwyr")
_VOWELS = set("aeiou")
_DIGRAPH = "ng"


# ---------------------------------------------------------------------------
# ArchivalSystem
# ---------------------------------------------------------------------------

class ArchivalSystem:
    """
    Session-based archival pipeline for handwritten Baybayin samples.

    Parameters
    ----------
    archive_root : str
        Absolute (or relative) path to the root archive directory.
        Sub-folders ``Captured/``, ``Characters/``, and ``Metadata/``
        are created automatically under this root.
    accuracy_threshold : float
        Minimum overall accuracy (0–1) required for a sample to be eligible
        for archival.  Defaults to 0.90.
    """

    def __init__(
        self,
        archive_root: str | None = None,
        accuracy_threshold: float = 0.90,
    ) -> None:
        if archive_root is None:
            archive_root = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "archives"
            )
        self.archive_root = archive_root
        self.accuracy_threshold = accuracy_threshold
        self._ensure_folder_structure()

        # In-memory set of MD5 hashes already archived (persistence via scan)
        self._archived_hashes: set[str] = self._load_existing_hashes()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_submission(
        self,
        image_bytes: bytes,
        word: str,
        contributor_id: str,
        predictions: list[dict[str, Any]] | None = None,
        handwritten_hog: np.ndarray | None = None,
        reference_hog: np.ndarray | None = None,
    ) -> dict[str, Any]:
        """
        Full archival pipeline for one handwritten submission.

        Parameters
        ----------
        image_bytes : bytes
            Raw bytes of the handwritten image (PNG/JPEG).
        word : str
            Romanised word that was written (e.g. "halimbawa").
        contributor_id : str
            Anonymised identifier for the contributor.
        predictions : list[dict]
            Per-character prediction dicts with keys ``"char"`` and
            ``"confidence"`` (0–100 range).
        handwritten_hog : np.ndarray, optional
            HOG feature vector of the handwritten image for similarity scoring.
        reference_hog : np.ndarray, optional
            HOG feature vector of the reference (standard) character form.

        Returns
        -------
        dict
            Result dictionary with keys: ``session_id``, ``status``,
            ``overall_accuracy``, ``message``, and (if archived)
            ``archive_path``.
        """
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now(timezone.utc).isoformat()

        # --- Deduplication check ------------------------------------------
        image_hash = self._md5(image_bytes)
        if image_hash in self._archived_hashes:
            return {
                "session_id": session_id,
                "status": "duplicate",
                "message": "duplicate detected",
                "overall_accuracy": None,
                "archive_path": None,
            }

        # --- Confidence / accuracy scoring --------------------------------
        if predictions is None:
            predictions = []
        overall_accuracy = self.compute_confidence_score(predictions)

        # --- Similarity scoring (optional) --------------------------------
        similarity = None
        if handwritten_hog is not None and reference_hog is not None:
            similarity = self.compute_similarity_score(
                handwritten_hog, reference_hog
            )

        # --- Accuracy gate ------------------------------------------------
        eligible = self.should_archive(overall_accuracy)
        if not eligible:
            return {
                "session_id": session_id,
                "status": "rejected",
                "message": (
                    f"Overall accuracy {overall_accuracy:.1%} is below "
                    f"the {self.accuracy_threshold:.0%} threshold. "
                    "Improve character formation and try again."
                ),
                "overall_accuracy": overall_accuracy,
                "archive_path": None,
            }

        # --- Character segmentation ---------------------------------------
        characters = self.segment_baybayin_word(word)

        # --- Extract character images -------------------------------------
        char_images = self.extract_character_images(image_bytes)

        # --- Per-character accuracy map -----------------------------------
        accuracy_scores: dict[str, float] = {}
        for i, char in enumerate(characters):
            if i < len(predictions):
                accuracy_scores[char] = round(
                    predictions[i].get("confidence", 0) / 100, 4
                )
            else:
                accuracy_scores[char] = round(overall_accuracy, 4)

        # --- Build metadata -----------------------------------------------
        source_file = (
            f"Captured/{session_id}/"
            f"{timestamp.replace(':', '-')}_{contributor_id}.png"
        )
        metadata: dict[str, Any] = {
            "session_id": session_id,
            "contributor_id": contributor_id,
            "timestamp": timestamp,
            "word": word,
            "characters": characters,
            "accuracy_scores": accuracy_scores,
            "overall_accuracy": round(overall_accuracy, 4),
            "status": "archived",
            "source_file": source_file,
        }
        if similarity is not None:
            metadata["similarity_score"] = round(float(similarity), 4)

        # --- Persist to archive -------------------------------------------
        archive_path = self.store_to_archive(
            session_data={
                "session_id": session_id,
                "contributor_id": contributor_id,
                "timestamp": timestamp,
                "image_bytes": image_bytes,
                "characters": characters,
                "char_images": char_images,
                "metadata": metadata,
            }
        )

        self._archived_hashes.add(image_hash)

        return {
            "session_id": session_id,
            "status": "archived",
            "message": (
                "Thank you! Your handwriting has been contributed to the "
                "Dayaw Archives for open-source Baybayin preservation."
            ),
            "overall_accuracy": overall_accuracy,
            "archive_path": archive_path,
            "metadata": metadata,
        }

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    def compute_confidence_score(
        self, predictions: list[dict[str, Any]]
    ) -> float:
        """
        Compute the overall accuracy as the mean SVM confidence across all
        per-character predictions.

        Parameters
        ----------
        predictions : list[dict]
            Each dict must have a ``"confidence"`` key with a value in the
            range 0–100 (as returned by the BTT pipeline in ``app.py``).

        Returns
        -------
        float
            Mean confidence in the range 0–1.  Returns 0.0 for empty input.
        """
        if not predictions:
            return 0.0
        total = sum(p.get("confidence", 0) for p in predictions)
        return total / len(predictions) / 100.0

    # ------------------------------------------------------------------
    # Similarity scoring
    # ------------------------------------------------------------------

    def compute_similarity_score(
        self,
        handwritten_hog: np.ndarray,
        reference_hog: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between the HOG feature vectors of the
        handwritten character and the standard reference form.

        Returns a value in [0, 1], where 1 = perfect similarity.
        """
        a = np.asarray(handwritten_hog, dtype=float).flatten()
        b = np.asarray(reference_hog, dtype=float).flatten()
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        similarity = float(np.dot(a, b) / (norm_a * norm_b))
        # Clamp to [0, 1] (cosine can be negative for very dissimilar vectors)
        return max(0.0, min(1.0, similarity))

    # ------------------------------------------------------------------
    # Accuracy gate
    # ------------------------------------------------------------------

    def should_archive(self, overall_accuracy: float) -> bool:
        """Return True if *overall_accuracy* meets the archival threshold."""
        return overall_accuracy >= self.accuracy_threshold

    # ------------------------------------------------------------------
    # Character segmentation (Tagalog romanisation → syllable list)
    # ------------------------------------------------------------------

    def segment_baybayin_word(self, word: str) -> list[str]:
        """
        Segment a Tagalog romanised word into Baybayin syllabic units.

        Algorithm
        ---------
        Walk through the characters left-to-right:
          1. Check for the 'ng' digraph followed by a vowel → "nga/ngi/…"
          2. Check for a consonant followed by a vowel → CV syllable
          3. A consonant with no following vowel (word-final or before another
             consonant) → standalone consonant (maps to virama in Baybayin)
          4. A standalone vowel → kept as-is

        Parameters
        ----------
        word : str
            Lowercase Tagalog romanised word (e.g. ``"halimbawa"``).

        Returns
        -------
        list[str]
            Syllabic units, e.g. ``["ha", "li", "m", "ba", "wa"]``.
        """
        word = word.lower().strip()
        syllables: list[str] = []
        i = 0
        n = len(word)

        while i < n:
            ch = word[i]

            # Digraph 'ng'
            if (
                ch == "n"
                and i + 1 < n
                and word[i + 1] == "g"
            ):
                if i + 2 < n and word[i + 2] in _VOWELS:
                    syllables.append("ng" + word[i + 2])
                    i += 3
                else:
                    # Standalone 'ng' → virama
                    syllables.append("ng")
                    i += 2
                continue

            if ch in _VOWELS:
                syllables.append(ch)
                i += 1
                continue

            if ch in _CONSONANTS:
                if i + 1 < n and word[i + 1] in _VOWELS:
                    syllables.append(ch + word[i + 1])
                    i += 2
                else:
                    # Final consonant → virama
                    syllables.append(ch)
                    i += 1
                continue

            # Unknown character (e.g. space, punctuation) — skip
            i += 1

        return syllables

    # ------------------------------------------------------------------
    # Character image extraction (OpenCV-based)
    # ------------------------------------------------------------------

    def extract_character_images(
        self, image_bytes: bytes
    ) -> list[np.ndarray]:
        """
        Extract individual character images from a handwritten Baybayin
        image using OpenCV connected-component analysis.

        Returns
        -------
        list[np.ndarray]
            List of cropped grayscale character images, sorted left-to-right.
            Returns an empty list if the image cannot be decoded.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return []

        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.medianBlur(gray, 5)
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11, 2,
        )
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.dilate(binary, np.ones((3, 3), np.uint8), iterations=1)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )
        clean_binary = np.zeros_like(binary)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] > 400:
                clean_binary[labels == i] = 255

        contours, _ = cv2.findContours(
            clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = sorted(
            [cv2.boundingRect(c) for c in contours if
             cv2.boundingRect(c)[2] > 25 and cv2.boundingRect(c)[3] > 25],
            key=lambda b: b[0],
        )

        crops: list[np.ndarray] = []
        for (x, y, w, h) in boxes:
            roi = clean_binary[y: y + h, x: x + w]
            crops.append(roi)

        return crops

    # ------------------------------------------------------------------
    # Archive storage
    # ------------------------------------------------------------------

    def store_to_archive(self, session_data: dict[str, Any]) -> str:
        """
        Persist a session's full image, individual character images, and
        metadata to the three-tier archive structure.

        Returns
        -------
        str
            Absolute path to the session's ``Captured/`` directory.
        """
        sid = session_data["session_id"]
        timestamp = session_data["timestamp"].replace(":", "-")
        contributor = session_data["contributor_id"]
        image_bytes: bytes = session_data["image_bytes"]
        characters: list[str] = session_data["characters"]
        char_images: list[np.ndarray] = session_data.get("char_images", [])
        metadata: dict[str, Any] = session_data["metadata"]

        # --- Captured/ ---------------------------------------------------
        captured_dir = os.path.join(self.archive_root, "Captured", sid)
        os.makedirs(captured_dir, exist_ok=True)
        captured_file = os.path.join(
            captured_dir, f"{timestamp}_{contributor}.png"
        )
        with open(captured_file, "wb") as fh:
            fh.write(image_bytes)

        # --- Characters/ -------------------------------------------------
        for idx, char_label in enumerate(characters):
            char_dir = os.path.join(self.archive_root, "Characters", char_label)
            os.makedirs(char_dir, exist_ok=True)
            char_filename = os.path.join(char_dir, f"{sid}_{idx + 1}.png")
            if idx < len(char_images) and char_images[idx] is not None:
                cv2.imwrite(char_filename, char_images[idx])
            else:
                # Write a placeholder 42×42 blank image
                placeholder = np.zeros((42, 42), dtype=np.uint8)
                cv2.imwrite(char_filename, placeholder)

        # --- Metadata/ ---------------------------------------------------
        self.save_metadata(sid, metadata)

        return captured_dir

    # ------------------------------------------------------------------
    # Metadata management
    # ------------------------------------------------------------------

    def save_metadata(
        self, session_id: str, metadata_dict: dict[str, Any]
    ) -> str:
        """
        Save provenance metadata for *session_id* as a JSON file.

        Returns
        -------
        str
            Absolute path to the saved ``session_meta.json`` file.
        """
        meta_dir = os.path.join(self.archive_root, "Metadata", session_id)
        os.makedirs(meta_dir, exist_ok=True)
        meta_file = os.path.join(meta_dir, "session_meta.json")
        with open(meta_file, "w", encoding="utf-8") as fh:
            json.dump(metadata_dict, fh, indent=2, ensure_ascii=False)
        return meta_file

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_folder_structure(self) -> None:
        """Create the three-tier archive directory structure if absent."""
        for sub in ("Captured", "Characters", "Metadata"):
            os.makedirs(os.path.join(self.archive_root, sub), exist_ok=True)

    def _load_existing_hashes(self) -> set[str]:
        """
        Scan existing Captured/ files and load their MD5 hashes into memory
        so duplicate detection is persistent across restarts.
        """
        hashes: set[str] = set()
        captured_root = os.path.join(self.archive_root, "Captured")
        if not os.path.isdir(captured_root):
            return hashes
        for session_dir in os.listdir(captured_root):
            session_path = os.path.join(captured_root, session_dir)
            if not os.path.isdir(session_path):
                continue
            for fname in os.listdir(session_path):
                fpath = os.path.join(session_path, fname)
                if os.path.isfile(fpath):
                    try:
                        with open(fpath, "rb") as fh:
                            hashes.add(hashlib.md5(fh.read()).hexdigest())
                    except OSError:
                        pass
        return hashes

    @staticmethod
    def _md5(data: bytes) -> str:
        return hashlib.md5(data).hexdigest()
