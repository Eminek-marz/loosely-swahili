"""
src/polyglot_discovery.py - Dynamic Polyglot Environment & Runtime Capability Discovery
Inspects local OS binaries, Docker daemon status, and auto-detects workspace software stacks.
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from .workspace_config import get_workspace_dir

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = get_workspace_dir()


class PolyglotEnvironmentDiscovery:
    """
    Discovers local environment runtimes and workspace stacks to inform LLM & execution engines.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or WORKSPACE_DIR
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self._cached_manifest: Optional[Dict[str, Any]] = None

        self.target_binaries = {
            "python": ["python --version", "py -3 --version"],
            "node": ["node --version"],
            "npm": ["npm --version"],
            "rust": ["rustc --version"],
            "cargo": ["cargo --version"],
            "go": ["go version"],
            "java": ["java -version"],
            "dotnet": ["dotnet --version"],
            "docker": ["docker --version"],
            "podman": ["podman --version"],
            "git": ["git --version"],
            "gcc": ["gcc --version"],
            "g++": ["g++ --version"],
            "clang": ["clang --version"]
        }

    def inspect_local_capabilities(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Scans the system for compiler and runtime binaries (cached to avoid repeat probing)."""
        if self._cached_manifest and not force_refresh:
            return self._cached_manifest

        manifest = {}

        for tool_name, check_commands in self.target_binaries.items():
            binary_path = shutil.which(tool_name)
            if binary_path:
                version_str = self._get_version_output(check_commands[0])
                manifest[tool_name] = {
                    "installed": True,
                    "binary_path": binary_path,
                    "version": version_str
                }
            else:
                manifest[tool_name] = {
                    "installed": False,
                    "binary_path": None,
                    "version": None
                }

        # Check Docker daemon liveness
        docker_active = False
        if manifest.get("docker", {}).get("installed"):
            docker_active = self._check_docker_daemon()
        manifest["docker_daemon_active"] = docker_active

        self._cached_manifest = manifest
        return manifest

    def _check_docker_daemon(self) -> bool:
        """Verifies if the Docker engine/daemon is currently responsive with zero terminal popups."""
        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            res = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=3,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            return res.returncode == 0
        except Exception:
            return False

    def _get_version_output(self, command: str) -> str:
        """Runs a version check command and captures the first line with zero terminal popups."""
        try:
            import shlex
            cmd_args = shlex.split(command) if isinstance(command, str) else command
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            res = subprocess.run(
                cmd_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=3,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            output = (res.stdout + res.stderr).strip()
            if output:
                return output.splitlines()[0].strip()
            return "Installed (version unknown)"
        except Exception:
            return "Installed (version probe timed out)"

    def detect_workspace_stack(self) -> Dict[str, Any]:
        """
        Analyzes the files within the user workspace to determine the primary stack,
        framework, language, and recommended build/run tools.
        """
        if not self.workspace_path.exists():
            return {
                "primary_language": "unknown",
                "framework": "none",
                "stack_name": "Empty Workspace",
                "icon": "📁",
                "build_tools": []
            }

        file_counts: Dict[str, int] = {}
        manifests_found: List[str] = []

        manifest_map = {
            "Cargo.toml": ("rust", "Cargo / Rust Ecosystem", "🦀"),
            "go.mod": ("go", "Go Modules", "🐹"),
            "package.json": ("javascript", "Node.js / NPM Ecosystem", "🟨"),
            "pyproject.toml": ("python", "Python Modern (PEP 517/621)", "🐍"),
            "requirements.txt": ("python", "Python Pip Ecosystem", "🐍"),
            "Pipfile": ("python", "Pipenv", "🐍"),
            "setup.py": ("python", "Setuptools", "🐍"),
            "pom.xml": ("java", "Maven Java Project", "☕"),
            "build.gradle": ("java", "Gradle Project", "☕"),
            "Makefile": ("c/c++", "Make Build System", "⚙️"),
            "CMakeLists.txt": ("c/c++", "CMake Project", "⚙️"),
            "Dockerfile": ("docker", "Containerized Architecture", "🐳")
        }

        ext_map = {
            ".py": ("python", "Python", "🐍"),
            ".rs": ("rust", "Rust", "🦀"),
            ".go": ("go", "Go", "🐹"),
            ".js": ("javascript", "JavaScript", "🟨"),
            ".jsx": ("react", "React JSX", "⚛️"),
            ".ts": ("typescript", "TypeScript", "🟦"),
            ".tsx": ("react-ts", "React TypeScript", "⚛️"),
            ".html": ("html", "Web HTML", "🌐"),
            ".css": ("css", "Web CSS", "🎨"),
            ".java": ("java", "Java", "☕"),
            ".cpp": ("cpp", "C++", "⚙️"),
            ".c": ("c", "C", "⚙️"),
            ".sh": ("shell", "Shell / Bash", "🐚"),
            ".ps1": ("powershell", "PowerShell", "💻"),
            ".json": ("json", "JSON Config", "📄"),
            ".sql": ("sql", "SQL Database", "🗄️")
        }

        detected_primary = "python"
        stack_name = "Python Workspace"
        stack_icon = "🐍"
        framework = "standard"

        # Walk workspace
        for root, dirs, files in os.walk(str(self.workspace_path)):
            # skip hidden / virtual envs
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv", "node_modules", "target", "dist"}]
            for f in files:
                # Check manifest files
                if f in manifest_map:
                    lang, desc, icon = manifest_map[f]
                    manifests_found.append(f)
                    detected_primary = lang
                    stack_name = desc
                    stack_icon = icon

                # Count extensions
                _, ext = os.path.splitext(f)
                ext = ext.lower()
                if ext in ext_map:
                    file_counts[ext] = file_counts.get(ext, 0) + 1

        # If no manifest, pick by highest file extension frequency
        if not manifests_found and file_counts:
            sorted_exts = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
            top_ext = sorted_exts[0][0]
            if top_ext in ext_map:
                lang, desc, icon = ext_map[top_ext]
                detected_primary = lang
                stack_name = f"{desc} Project"
                stack_icon = icon

        # Framework heuristics
        if detected_primary == "python":
            # Check for django, fastapi, flask, pytorch
            for root, _, files in os.walk(str(self.workspace_path)):
                if "manage.py" in files:
                    framework = "django"
                    stack_name = "Django Web Framework"
                    break
                for f in files:
                    if f.endswith(".py"):
                        p = Path(root) / f
                        try:
                            sample = p.read_text(encoding="utf-8", errors="ignore")[:2000]
                            if "from fastapi" in sample or "import fastapi" in sample:
                                framework = "fastapi"
                                stack_name = "FastAPI Asynchronous Engine"
                                break
                            elif "from flask" in sample or "import flask" in sample:
                                framework = "flask"
                                stack_name = "Flask Micro-Framework"
                                break
                        except Exception:
                            pass
        elif detected_primary in ["javascript", "typescript", "react", "react-ts"]:
            pkg_path = self.workspace_path / "package.json"
            if pkg_path.exists():
                try:
                    pkg_data = json.loads(pkg_path.read_text(encoding="utf-8", errors="ignore"))
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    if "next" in deps:
                        framework = "nextjs"
                        stack_name = "Next.js Full-Stack App"
                        stack_icon = "▲"
                    elif "react" in deps:
                        framework = "react"
                        stack_name = "React Frontend Application"
                        stack_icon = "⚛️"
                    elif "express" in deps:
                        framework = "express"
                        stack_name = "Express.js REST API"
                        stack_icon = "🚂"
                except Exception:
                    pass

        return {
            "primary_language": detected_primary,
            "framework": framework,
            "stack_name": stack_name,
            "icon": stack_icon,
            "manifests": manifests_found,
            "file_counts": file_counts
        }

    def format_system_env_prompt(self) -> str:
        """
        Creates the live injected [SYSTEM_ENV] context block for the model.
        """
        capabilities = self.inspect_local_capabilities()
        stack = self.detect_workspace_stack()

        installed = []
        missing = []
        for tool, meta in capabilities.items():
            if tool == "docker_daemon_active":
                continue
            if meta.get("installed"):
                v = meta.get("version") or "Ready"
                installed.append(f"{tool} ({v})")
            else:
                missing.append(tool)

        docker_status = "Active & Available" if capabilities.get("docker_daemon_active") else "CLI Available, Daemon Offline (Subprocess Fallback)" if capabilities.get("docker", {}).get("installed") else "Not Installed"

        lines = [
            "[SYSTEM_ENV_CAPABILITIES]",
            f"Active Workspace Stack: {stack['icon']} {stack['stack_name']} (Framework: {stack['framework']})",
            f"Installed Host Runtimes: {', '.join(installed) if installed else 'None detected'}",
            f"Missing Host Tools: {', '.join(missing[:6])}",
            f"Docker Isolation Sandbox: {docker_status}",
            "[END_SYSTEM_ENV]"
        ]
        return "\n".join(lines)


_discovery_instance = None

def get_polyglot_discovery(workspace_path: Optional[Path] = None) -> PolyglotEnvironmentDiscovery:
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = PolyglotEnvironmentDiscovery(workspace_path=workspace_path)
    return _discovery_instance
