"""
Shared constants and parameters for the Dayaw test suite.
Import this module in test files (not conftest.py directly).
"""

BAYBAYIN_CLASSES = [
    "A", "BA", "DARA", "EI", "GA", "HA",
    "KA", "LA", "MA", "NA", "NGA", "OU",
    "PA", "SA", "TA", "WA", "YA",
]

# HOG parameters – must match app.py
HOG_PARAMS = dict(
    orientations=9,
    pixels_per_cell=(8, 8),
    cells_per_block=(2, 2),
    visualize=False,
)

IMAGE_SIZE = (42, 42)        # matches cv2.resize(padded, (42, 42)) in app.py
HOG_FEATURE_SIZE = 576       # derived from IMAGE_SIZE + HOG_PARAMS
