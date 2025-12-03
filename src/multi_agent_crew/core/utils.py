"""Common utility functions."""

import os
import json
from typing import Any, Dict, Union
from pathlib import Path


def ensure_directory(path: Union[str, Path]) -> None:
    """Ensure a directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(path: Union[str, Path]) -> Any:
    """Load JSON from a file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, path: Union[str, Path], indent: int = 2) -> None:
    """Save data to a JSON file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, default=str)


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assuming this file is in src/multi_agent_crew/core/utils.py
    return Path(__file__).parent.parent.parent.parent
