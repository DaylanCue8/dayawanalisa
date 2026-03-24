# Dayaw Archives

This directory is the root of the **Baybayin Archival Preservation System (BAPS)**.

## Folder Structure

```
archives/
├── Captured/
│   └── {session_id}/
│       └── {timestamp}_{contributor_id}.png   ← full handwritten image
├── Characters/
│   └── {character_label}/
│       ├── {session_id}_1.png                 ← extracted syllabic character
│       ├── {session_id}_2.png
│       └── ...
└── Metadata/
    └── {session_id}/
        └── session_meta.json                  ← provenance record (9 fields)
```

## Sub-folder Descriptions

### `Captured/`
Stores the **full, un-cropped** handwritten image submitted by the contributor,
organised by session UUID.

### `Characters/`
Stores **individually extracted** syllabic character images.
One sub-folder per character label:

| Label     | Baybayin Glyph | Notes                              |
|-----------|----------------|------------------------------------|
| `a`       | ᜀ              | Standalone vowel                   |
| `ba`      | ᜊ              | Base syllable                      |
| `ka`      | ᜃ              | Base syllable                      |
| `da`      | ᜇ              | Shared with `ra`                   |
| `ga`      | ᜄ              | Base syllable                      |
| `ha`      | ᜑ              | Base syllable                      |
| `la`      | ᜎ              | Base syllable                      |
| `ma`      | ᜋ              | Base syllable                      |
| `na`      | ᜈ              | Base syllable                      |
| `nga`     | ᜅ              | Digraph base syllable              |
| `pa`      | ᜉ              | Base syllable                      |
| `ra`      | ᜇ              | Shared glyph with `da`             |
| `sa`      | ᜐ              | Base syllable                      |
| `ta`      | ᜆ              | Base syllable                      |
| `wa`      | ᜏ              | Base syllable                      |
| `ya`      | ᜌ              | Base syllable                      |
| `ei`      | ᜁ              | Standalone e/i vowel               |
| `virama`  | ᜔              | Final consonant / pamudpod mark    |

### `Metadata/`
Stores JSON provenance records (one per session).  Each `session_meta.json`
contains all **9 mandatory fields**:

| Field              | Type   | Description                                  |
|--------------------|--------|----------------------------------------------|
| `session_id`       | string | UUID for the submission                      |
| `contributor_id`   | string | Anonymised contributor identifier            |
| `timestamp`        | string | ISO 8601 UTC datetime                        |
| `word`             | string | Romanised word that was written              |
| `characters`       | array  | Ordered syllabic units extracted             |
| `accuracy_scores`  | object | Per-character confidence scores (0–1)        |
| `overall_accuracy` | number | Mean confidence across all characters (0–1)  |
| `status`           | string | `"archived"` or `"rejected"`                 |
| `source_file`      | string | Relative path to the captured image          |

## Archival Eligibility

Only submissions where **overall accuracy ≥ 90%** are archived.
Lower-accuracy submissions receive feedback to improve their writing
and are **not** written to any of the folders above.

## Duplicate Prevention

Each submitted image is hashed with MD5.  If an identical image is submitted
again, the system returns `"duplicate detected"` and writes no new files.

## Open-Source Access

The Dayaw Archives are intended to be **freely accessible** to:
- Linguists studying the Baybayin writing system
- Researchers building Baybayin NLP datasets
- Developers training future character-recognition models

For data access requests, refer to the project documentation.
