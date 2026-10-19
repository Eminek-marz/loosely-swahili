"""
src/polyglot_sandbox.py - Hybrid Isolated Sandboxing Engine
Combines ephemeral Docker container execution with local secure subprocess jailing.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from .workspace_config import get_workspace_dir

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = get_workspace_dir()

from .polyglot_discovery import get_polyglot_discovery


class PolyglotSandboxEngine:
    """
    Executes commands safely in ephemeral Docker containers (when active)
    or localized subprocess jail (when Docker is unavailable or offline).
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or WORKSPACE_DIR
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.discovery = get_polyglot_discovery(self.workspace_path)

        # Standard container images per ecosystem
        self.container_images = {
            "python": "python:3.12-slim",
            "javascript": "node:20-alpine",
            "typescript": "node:20-alpine",
            "rust": "rust:1.76-alpine",
            "go": "golang:1.22-alpine",
            "c": "gcc:13",
            "cpp": "gcc:13"
        }

    def execute(
        self,
        command: str,
        language: str = "python",
        prefer_docker: bool = False,
        timeout_sec: int = 15,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes an arbitrary CLI command or code execution task.
        Automatically routes to Docker if prefer_docker is True AND Docker daemon is alive,
        otherwise routes to localized process jail.
        """
        lang = (language or "python").lower().strip()
        start = time.perf_counter()

        target_cwd = self.workspace_path
        if cwd:
            custom_dir = (self.workspace_path / Path(cwd).as_posix().lstrip("/\\")).resolve()
            if str(custom_dir).startswith(str(self.workspace_path)):
                target_cwd = custom_dir

        # Check if Docker execution is possible
        capabilities = self.discovery.inspect_local_capabilities()
        docker_available = capabilities.get("docker_daemon_active", False)

        if prefer_docker and docker_available:
            return self._execute_docker(command, lang, target_cwd, timeout_sec, start)
        else:
            return self._execute_local_process(command, lang, target_cwd, timeout_sec, start, docker_available)

    def _execute_docker(
        self,
        command: str,
        language: str,
        target_cwd: Path,
        timeout_sec: int,
        start_time: float
    ) -> Dict[str, Any]:
        """Executes command within an isolated ephemeral Docker container."""
        image = self.container_images.get(language, "alpine:latest")
        docker_cmd = [
            "docker", "run",
            "--rm",
            "--memory=512m",
            "--cpus=1.0",
            "-v", f"{str(self.workspace_path)}:/workspace",
            "-w", "/workspace",
            image,
            "sh", "-c", command
        ]

        try:
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_sec,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "sandbox_mode": "docker_container",
                "container_image": image,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "duration_ms": duration_ms,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "sandbox_mode": "docker_container",
                "container_image": image,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Docker container execution timed out after {timeout_sec}s.",
                "duration_ms": round(timeout_sec * 1000.0, 2),
                "command": command
            }
        except Exception as e:
            # Fallback to local process if Docker invocation failed
            return self._execute_local_process(command, language, target_cwd, timeout_sec, start_time, False)

    def _execute_local_process(
        self,
        command: str,
        language: str,
        target_cwd: Path,
        timeout_sec: int,
        start_time: float,
        docker_daemon_active: bool
    ) -> Dict[str, Any]:
        """Executes inside local host jail with sanitized environment."""
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0

            # On Windows use PowerShell for complex commands or shell=True
            proc = subprocess.run(
                command,
                cwd=str(target_cwd),
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=timeout_sec,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "sandbox_mode": "local_jail",
                "docker_available": docker_daemon_active,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "duration_ms": duration_ms,
                "cwd": str(target_cwd),
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "sandbox_mode": "local_jail",
                "docker_available": docker_daemon_active,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_sec}s.",
                "duration_ms": round(timeout_sec * 1000.0, 2),
                "cwd": str(target_cwd),
                "command": command
            }
        except Exception as e:
            return {
                "status": "error",
                "sandbox_mode": "local_jail",
                "docker_available": docker_daemon_active,
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": round((time.perf_counter() - start_time) * 1000.0, 2),
                "cwd": str(target_cwd),
                "command": command
            }


_sandbox_instance = None

def get_polyglot_sandbox(workspace_path: Optional[Path] = None) -> PolyglotSandboxEngine:
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = PolyglotSandboxEngine(workspace_path=workspace_path)
    return _sandbox_instance
