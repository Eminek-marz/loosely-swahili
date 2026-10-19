"""
src/workspace_config.py - Independent Workspace Configuration
Manages the independent storage location for user projects created by Anjiru AI.
Decouples created codebases from the Anjiru AI repository and tool runtime.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROJECTS_DIR = (PROJECT_ROOT / "workspace").resolve()

def get_workspace_dir() -> Path:
    """
    Returns the root directory for Anjiru projects.
    Completely isolated within the Anjiru environment, decoupled from user's external Projects folder.
    Can be overridden via ANJIRU_PROJECTS_DIR or ANJIRU_WORKSPACE_DIR env variables.
    """
    override = os.environ.get("ANJIRU_PROJECTS_DIR") or os.environ.get("ANJIRU_WORKSPACE_DIR")
    if override:
        p = Path(override).resolve()
    else:
        p = DEFAULT_PROJECTS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p
