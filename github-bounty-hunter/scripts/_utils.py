# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
GitHub Bounty Hunter - Cross-Platform Utilities
版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import os
import sys
import tempfile
from pathlib import Path


def get_temp_dir(suffix: str = "") -> Path:
    """Get cross-platform temp directory.
    
    Args:
        suffix: Optional suffix for the directory name
    
    Returns:
        Path object in system temp directory
    """
    base = Path(tempfile.gettempdir())
    if suffix:
        return base / f"github-bounty-{suffix}"
    return base


def get_workspace_dir() -> Path:
    """Get the skill workspace directory."""
    return Path(__file__).parent.parent.resolve()


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_dir() -> Path:
    """Get data directory for scan results and known issues."""
    data_dir = get_workspace_dir() / "data"
    ensure_dir(data_dir)
    return data_dir


def check_dependency(cmd: str) -> bool:
    """Check if a command-line tool is available.
    
    Args:
        cmd: Command name to check
    
    Returns:
        True if command is available
    """
    import shutil
    return shutil.which(cmd) is not None


def check_dependencies(required: list) -> tuple[bool, list]:
    """Check multiple dependencies.
    
    Args:
        required: List of command names
    
    Returns:
        (all_available, missing_list)
    """
    missing = [cmd for cmd in required if not check_dependency(cmd)]
    return len(missing) == 0, missing


def print_dependency_warning(missing: list) -> None:
    """Print warning about missing dependencies."""
    print("⚠️  Missing dependencies:", file=sys.stderr)
    for cmd in missing:
        print(f"  - {cmd}", file=sys.stderr)
    print(file=sys.stderr)
    print("Please install missing tools to use all features.", file=sys.stderr)


# Exit codes for scripts
class ExitCode:
    SUCCESS = 0
    ERROR = 1
    SKIP = 2
    RETRY = 3


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    """Safe division with default value."""
    return a / b if b != 0 else default


if __name__ == "__main__":
    # Self-test
    print("✅ _utils.py loaded successfully")
    print(f"   Temp dir: {get_temp_dir()}")
    print(f"   Workspace: {get_workspace_dir()}")
    print(f"   Data dir: {get_data_dir()}")