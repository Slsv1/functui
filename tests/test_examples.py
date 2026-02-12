import pytest
import subprocess
import sys
import time
import signal
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

INTERACTIVE_EXAMPLES = [
    "curses_elm_template.py",
    "multiple_interactibles.py",
]

# @pytest.mark.parametrize("example", INTERACTIVE_EXAMPLES)
# def test_einteractive_examples(example):
#     example_path = EXAMPLES_DIR / example
#
#     proc = subprocess.Popen(
#         [sys.executable, example_path],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#     )
#
#     time.sleep(1)
#     proc.send_signal(signal.SIGINT)
#
#     # stdout, stderr = proc.communicate(timeout=5)
#
#     assert proc.returncode in (0, -signal.SIGINT)
