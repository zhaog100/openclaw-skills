# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""Pytest configuration to prevent src/ classes from being collected as tests."""
import sys
from pathlib import Path

# Ensure src is in path but exclude it from collection
sys.path.insert(0, str(Path(__file__).parent / "src"))


def pytest_ignore_collect(collection_path, config):
    """Ignore src directory for test collection."""
    if "src" in str(collection_path) and collection_path.name.endswith(".py"):
        # Only ignore if it looks like a module, not a test file
        if not collection_path.name.startswith("test_"):
            return True
    return False
