"""Shared test setup: find tools installed in the same virtualenv as the interpreter."""

import os
import sys
from pathlib import Path

os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
