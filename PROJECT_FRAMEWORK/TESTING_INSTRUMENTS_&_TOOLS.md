# DAYAW — Testing Instruments & Tools
**Tools, Metrics, Templates, and Evidence Collection**

---

## 1. Tool Summary by Test Type

| Test Type | Tool | Purpose |
|---|---|---|
| White Box – Coverage | `pytest` + `pytest-cov` | Statement & branch coverage |
| White Box – Unit | `pytest` | Unit test execution |
| White Box – Mocking | `unittest.mock` / `pytest-mock` | Mock SVM model & file I/O |
| Black Box – API | `Postman` | HTTP endpoint testing |
| Black Box – Functional | `pytest` parametrised | Functional test cases BT1–BT22 |
| Performance | `pytest` + `time.perf_counter()` | Latency measurement |
| Load Testing | `locust` | Concurrent session simulation (BT22) |
| Mutation Testing | `mutmut` | Verify test effectiveness |
| Alpha – Bug Tracking | GitHub Issues | Defect logging & tracking |
| Beta – SUS Survey | Google Forms / Typeform | SUS questionnaire (10 items) |
| Beta – NPS Survey | Google Forms / Typeform | NPS single-question survey |
| Reporting | `pytest-html` | HTML test report generation |
| Coverage HTML Report | `coverage.py` | Visual coverage dashboard |

---

## 2. Pytest Configuration

### `pytest.ini` (existing, reproduced for reference)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### `.coveragerc` (existing, with branch coverage enabled)

```ini
[run]
branch = True
source = .
omit =
    tests/*
    */__pycache__/*
    */conftest.py

[report]
fail_under = 85
show_missing = True

[html]
directory = htmlcov
```

### Running All Tests with Coverage

```bash
# From backend/ directory
pytest tests/ -v \
  --cov=. \
  --cov-report=html \
  --cov-report=term-missing \
  --html=tests/reports/pytest_report.html \
  --self-contained-html
```

### Running a Specific Test Module

```bash
# BTT module only
pytest tests/test_svm_model_performance.py -v --cov=app --cov-report=term-missing

# TTB module only
pytest tests/test_translation_system.py -v --cov=tagalog_to_baybayin --cov-report=term-missing
```

### Running Black-Box Test Cases

```bash
# Run tests marked as black-box
pytest tests/ -m "blackbox" -v --html=tests/reports/blackbox_report.html
```

Add `@pytest.mark.blackbox` decorator to BT1–BT22 test functions.

---

## 3. Postman Collection Template

### Collection: `DAYAW API Black-Box Tests`

**Environment Variables:**
```json
{
  "base_url": "http://localhost:5000",
  "test_image_path": "./tests/fixtures/ba_sample.png"
}
```

### Request Templates

#### POST /predict — BTT Character Recognition

```json
{
  "name": "BT1 - Predict 'ba' character",
  "request": {
    "method": "POST",
    "url": "{{base_url}}/predict",
    "body": {
      "mode": "formdata",
      "formdata": [
        { "key": "image", "type": "file", "src": "{{test_image_path}}" }
      ]
    }
  },
  "tests": [
    "pm.test('Status 200', () => pm.response.to.have.status(200));",
    "pm.test('Label is ba', () => pm.expect(pm.response.json().label).to.eql('ba'));",
    "pm.test('Response < 500ms', () => pm.expect(pm.response.responseTime).to.be.below(500));"
  ]
}
```

#### POST /translate — TTB Translation

```json
{
  "name": "BT8 - Translate 'baybayin'",
  "request": {
    "method": "POST",
    "url": "{{base_url}}/translate",
    "header": [{ "key": "Content-Type", "value": "application/json" }],
    "body": {
      "mode": "raw",
      "raw": "{ \"text\": \"baybayin\" }"
    }
  },
  "tests": [
    "pm.test('Status 200', () => pm.response.to.have.status(200));",
    "pm.test('Translation correct', () => pm.expect(pm.response.json().baybayin).to.be.a('string'));"
  ]
}
```

#### POST /archive — Submit for Archival

```json
{
  "name": "BT13 - Archive approved submission",
  "request": {
    "method": "POST",
    "url": "{{base_url}}/archive",
    "body": {
      "mode": "formdata",
      "formdata": [
        { "key": "image", "type": "file", "src": "{{test_image_path}}" },
        { "key": "word", "value": "ba" },
        { "key": "contributor_id", "value": "test-user-001" }
      ]
    }
  },
  "tests": [
    "pm.test('Status 200 or 201', () => pm.expect(pm.response.code).to.be.oneOf([200, 201]));",
    "pm.test('Status archived', () => pm.expect(pm.response.json().status).to.eql('archived'));"
  ]
}
```

### Running the Collection via CLI

```bash
newman run DAYAW_BlackBox_Tests.json \
  --environment DAYAW_Local.json \
  --reporters html,cli \
  --reporter-html-export tests/reports/postman_report.html
```

---

## 4. Test Execution Spreadsheet Template

Copy the table below into a spreadsheet (Excel / Google Sheets) and fill in results during test execution.

| Test ID | Test Name | Module | Type | Tester | Date | Input | Expected Output | Actual Output | Pass/Fail | Defect ID | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BT1 | Single char recognition | BTT | Functional | | | ba image | label=ba | | | | |
| BT2 | All 17 chars recognised | BTT | Functional | | | 17 images | accuracy ≥85% | | | | |
| BT3 | Printed vs Handwritten | BTT | Functional | | | paired images | gap <5% | | | | |
| BT4 | Low-quality image | BTT | Robustness | | | blurred image | no crash | | | | |
| BT5 | Invalid image format | BTT | Negative | | | .txt file | 400 error | | | | |
| BT6 | Virama recognition | BTT | Functional | | | virama image | label=virama | | | | |
| BT7 | Single vowel TTB | TTB | Functional | | | "a" | ᜀ | | | | |
| BT8 | Full word TTB | TTB | Functional | | | "baybayin" | Baybayin string | | | | |
| BT9 | Kudlit upper (e/i) | TTB | Functional | | | "si" | ᜐᜒ | | | | |
| BT10 | Kudlit lower (o/u) | TTB | Functional | | | "su" | ᜐᜓ | | | | |
| BT11 | mga exception | TTB | Functional | | | "mga" | special mapping | | | | |
| BT12 | Empty string | TTB | Negative | | | "" | "" | | | | |
| BT13 | Archive approved | Archival | Functional | | | acc=0.93 | archived | | | | |
| BT14 | Reject below threshold | Archival | Functional | | | acc=0.87 | rejected | | | | |
| BT15 | Metadata completeness | Archival | Functional | | | session JSON | 9 fields | | | | |
| BT16 | Char extraction | Archival | Functional | | | "halimbawa na" | [ha,li,m,ba,wa,na] | | | | |
| BT17 | Duplicate rejected | Archival | Negative | | | same image | rejected | | | | |
| BT18 | Folder auto-created | Archival | Functional | | | empty archive | 3 folders | | | | |
| BT19 | Module navigation | UX | Usability | | | tap nav | ≤500ms | | | | |
| BT20 | Error message clarity | UX | Usability | | | blank input | readable error | | | | |
| BT21 | BTT latency | Performance | Performance | | | 42×42 image | ≤500ms | | | | |
| BT22 | Concurrent sessions | Performance | Load | | | 10 sessions | no corruption | | | | |

---

## 5. SUS (System Usability Scale) Questionnaire Template

**Instructions to participants:** For each statement, select a number from 1 (Strongly Disagree) to 5 (Strongly Agree).

| # | Statement | 1 | 2 | 3 | 4 | 5 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | I think that I would like to use this system frequently. | ○ | ○ | ○ | ○ | ○ |
| 2 | I found the system unnecessarily complex. | ○ | ○ | ○ | ○ | ○ |
| 3 | I thought the system was easy to use. | ○ | ○ | ○ | ○ | ○ |
| 4 | I think that I would need the support of a technical person to use this system. | ○ | ○ | ○ | ○ | ○ |
| 5 | I found the various functions in this system were well integrated. | ○ | ○ | ○ | ○ | ○ |
| 6 | I thought there was too much inconsistency in this system. | ○ | ○ | ○ | ○ | ○ |
| 7 | I would imagine that most people would learn to use this system very quickly. | ○ | ○ | ○ | ○ | ○ |
| 8 | I found the system very cumbersome to use. | ○ | ○ | ○ | ○ | ○ |
| 9 | I felt very confident using the system. | ○ | ○ | ○ | ○ | ○ |
| 10 | I needed to learn a lot of things before I could get going with this system. | ○ | ○ | ○ | ○ | ○ |

**Scoring:**
- Odd items: `score - 1`
- Even items: `5 - score`
- Sum all 10 contributions and multiply by 2.5
- Score range: 0–100

---

## 6. Measurement Metrics & Evidence Collection

### White Box Evidence

| Metric | Tool | Output File | Threshold |
|---|---|---|---|
| Statement coverage | `pytest-cov` | `htmlcov/index.html` | ≥ 85 % |
| Branch coverage | `pytest-cov` (branch=True) | `htmlcov/index.html` | ≥ 80 % |
| Test count | `pytest -v` | Terminal log | ≥ 131 |
| Test pass rate | `pytest` | Terminal log | 100 % |

### Black Box Evidence

| Metric | Tool | Output File | Threshold |
|---|---|---|---|
| Test cases executed | Spreadsheet | `TEST_EXECUTION_REPORT.xlsx` | 22 / 22 |
| Pass rate | Spreadsheet | `TEST_EXECUTION_REPORT.xlsx` | ≥ 90 % |
| API response time (BT21) | Postman | `postman_report.html` | ≤ 500 ms |
| Defects logged | GitHub Issues | Issue list | 0 open P1 |

### Alpha Testing Evidence

| Metric | Tool | Output | Threshold |
|---|---|---|---|
| Defects found | GitHub Issues | Issue count | Logged |
| P1 defects resolved | GitHub Issues | Closed issues | 100 % |
| Re-test pass rate | `pytest` | Test log | 100 % |

### Beta Testing Evidence

| Metric | Tool | Output File | Threshold |
|---|---|---|---|
| SUS score | Survey | `beta_sus_scores.csv` | ≥ 68 |
| NPS score | Survey | `beta_nps_scores.csv` | ≥ 0 |
| Participant count | Survey | Response count | ≥ 5 |
| Session completion rate | Observation log | Log file | ≥ 80 % |

---

*Document version 1.0 — Cross-reference: `OBJECTIVE_4_TESTING_STRATEGY.md`, `TEST_EXECUTION_REPORT_TEMPLATE.md`*
