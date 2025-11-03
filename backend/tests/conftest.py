import os
import sys

# Ensure the backend package is importable in tests
TESTS_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.dirname(TESTS_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

