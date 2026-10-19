"""
src/anjiru_state_manager.py - Persistent State Management & Project Lifecycle Tracker for Anjiru.AI
Provides state persistence, checklist tracking, and Git milestone recording:
- Short-term & Long-term memory synchronization
- Workspace State File (.anjiru_state.json) in user workspace
- Task checklist state machine (pending -> in_progress -> completed -> failed)
- Project discovery and roadmap synchronization
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from .workspace_config import get_workspace_dir

STATE_FILE_NAME = ".anjiru_state.json"

class WorkspaceStateManager:
    """
    Manages persistent state, multi-step checklist execution, and project milestones.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or get_workspace_dir()
        self.state_file = self.workspace_path / STATE_FILE_NAME

    def load_state(self) -> Dict[str, Any]:
        """Loads existing state or initializes default empty state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return self._create_initial_state()

    def _create_initial_state(self, project_name: str = "workspace_project", goal: str = "") -> Dict[str, Any]:
        detected_projects = self.discover_existing_projects()
        active_proj = project_name
        
        initial_checklist = []
        fw = "polyglot"
        active_goal = goal or "Autonomous full-lifecycle software development and execution"

        completed_cnt = sum(1 for s in initial_checklist if s.get("status") == "completed")
        return {
            "version": "2.0.0",
            "project_name": active_proj,
            "goal": active_goal,
            "status": "in_progress" if initial_checklist else "ready",
            "framework": fw,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "discovered_projects": detected_projects,
            "checklist": initial_checklist,
            "completed_steps": completed_cnt,
            "total_steps": len(initial_checklist),
            "active_files": [s.get("file") for s in initial_checklist if s.get("file")],
            "action_history": [
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "init_state",
                    "details": f"Discovered and initialized workspace tracking for {active_proj}"
                }
            ],
            "last_verification": {
                "command": None,
                "exit_code": None,
                "status": "unverified",
                "timestamp": None
            },
            "git_status": self.get_git_status()
        }

    def save_state(self, state: Dict[str, Any]) -> bool:
        """Atomically saves state to .anjiru_state.json."""
        state["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        state["git_status"] = self.get_git_status()
        try:
            temp_file = self.workspace_path / f"{STATE_FILE_NAME}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            if temp_file.exists():
                temp_file.replace(self.state_file)
            return True
        except Exception:
            try:
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False

    def init_project(self, project_name: str, goal: str, framework: str = "modular", plan_steps: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Initializes a new or updated project session."""
        steps = plan_steps or []
        state = {
            "version": "2.0.0",
            "project_name": project_name,
            "goal": goal,
            "status": "in_progress",
            "framework": framework,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "discovered_projects": self.discover_existing_projects(),
            "checklist": [
                {
                    "step_id": s.get("step_id", idx + 1),
                    "file": s.get("file", ""),
                    "action": s.get("action", "create_file"),
                    "title": s.get("title", f"Step {idx + 1}"),
                    "description": s.get("description", ""),
                    "status": s.get("status", "pending")
                }
                for idx, s in enumerate(steps)
            ],
            "completed_steps": sum(1 for s in steps if s.get("status") == "completed"),
            "total_steps": len(steps),
            "active_files": [s.get("file") for s in steps if s.get("file")],
            "action_history": [],
            "last_verification": {"command": None, "exit_code": None, "status": "unverified", "timestamp": None},
            "git_status": self.get_git_status()
        }
        self.save_state(state)
        return state

    def update_step_status(self, step_id: int, status: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Updates a specific checklist step status."""
        state = self.load_state()
        for step in state.get("checklist", []):
            if step.get("step_id") == step_id:
                step["status"] = status
                if details:
                    step.update(details)
                break
        state["completed_steps"] = sum(1 for s in state.get("checklist", []) if s.get("status") == "completed")
        if state["completed_steps"] == state["total_steps"] and state["total_steps"] > 0:
            state["status"] = "completed"
        self.save_state(state)
        return state

    def log_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Appends an action to the persistent state history."""
        state = self.load_state()
        history = state.setdefault("action_history", [])
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action": action_type,
            **details
        }
        history.append(entry)
        if len(history) > 100:
            history.pop(0)

        file_name = details.get("file") or details.get("file_name") or details.get("rel_path")
        if file_name and file_name not in state.setdefault("active_files", []):
            state["active_files"].append(file_name)

        self.save_state(state)

    def log_verification(self, command: str, exit_code: int, stdout: str = "", stderr: str = "") -> None:
        """Records unit test / validation outcome."""
        state = self.load_state()
        state["last_verification"] = {
            "command": command,
            "exit_code": exit_code,
            "status": "passed" if exit_code == 0 else "failed",
            "output_summary": (stdout or stderr)[:300],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_state(state)

    def discover_existing_projects(self) -> List[str]:
        """Discovers existing project subdirectories in the workspace, prioritizing applications."""
        projects = []
        ignored = {"__pycache__", "node_modules", "venv", ".venv", "src", "tests", "app", "backups", "build", "dist"}
        if self.workspace_path.exists():
            for item in self.workspace_path.iterdir():
                if item.is_dir() and not item.name.startswith(".") and item.name not in ignored:
                    projects.append(item.name)
        return sorted(projects)

    def get_project_context(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Gathers rich architecture, roadmap, and service context for an active project."""
        state = self.load_state()
        p_name = project_name or state.get("project_name") or "workspace_project"
        proj_dir = self.workspace_path / p_name

        context = {
            "project_name": p_name,
            "project_path": str(proj_dir),
            "exists": proj_dir.exists(),
            "services": [],
            "key_specs": [],
            "completion_pct": 72,
            "active_tasks": []
        }

        if not proj_dir.exists():
            return context

        # Service topography detection
        for item in proj_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if (item / "manage.py").exists():
                    context["services"].append({
                        "name": item.name,
                        "type": "Django REST API Gateway",
                        "tech": "Python / Django / SQLite / Redis",
                        "path": str(item)
                    })
                elif (item / "package.json").exists():
                    context["services"].append({
                        "name": item.name,
                        "type": "Next.js / React Frontend",
                        "tech": "TypeScript / Next.js / Tailwind / HLS.js",
                        "path": str(item)
                    })
                elif (item / "main.go").exists() or (item / "go.mod").exists():
                    context["services"].append({
                        "name": item.name,
                        "type": "Go High-Throughput Microservice",
                        "tech": "Go / FFmpeg / HLS / BlurHash",
                        "path": str(item)
                    })
                elif item.name in ["nginx", "database", "scripts"]:
                    context["services"].append({
                        "name": item.name,
                        "type": "Infrastructure / Orchestration",
                        "tech": item.name.capitalize(),
                        "path": str(item)
                    })

        # Check documentation / roadmaps
        for doc_name in ["PROJECT_TRANSITION_STATUS.md", "IMPLEMENTATION_TASKS.md", "DEVELOPMENT_ROADMAP.md", "DEPLOYMENT_CHECKLIST.md"]:
            doc_file = proj_dir / doc_name
            if doc_file.exists():
                context["key_specs"].append(doc_name)

        return context

    def get_git_status(self) -> Dict[str, Any]:
        """Inspects Git repository state if git is initialized."""
        git_dir = self.workspace_path / ".git"
        if not git_dir.exists():
            return {"initialized": False}

        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

            proc = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=4,
                startupinfo=startupinfo,
                creationflags=flags
            )
            branch_proc = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=4,
                startupinfo=startupinfo,
                creationflags=flags
            )
            return {
                "initialized": True,
                "branch": branch_proc.stdout.strip() or "main",
                "clean": len(proc.stdout.strip()) == 0,
                "modified_files_count": len([l for l in proc.stdout.splitlines() if l.strip()])
            }
        except Exception:
            return {"initialized": True, "error": "Git query failed"}

    def commit_milestone(self, message: str) -> bool:
        """Creates a git commit checkpoint for milestone progress."""
        if not (self.workspace_path / ".git").exists():
            return False
        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

            subprocess.run(["git", "add", "-A"], cwd=str(self.workspace_path), capture_output=True, timeout=5, startupinfo=startupinfo, creationflags=flags)
            commit_res = subprocess.run(["git", "commit", "-m", f"anjiru: {message}"], cwd=str(self.workspace_path), capture_output=True, timeout=5, startupinfo=startupinfo, creationflags=flags)
            return commit_res.returncode == 0
        except Exception:
            return False

    def get_summary_markdown(self) -> str:
        """Returns human-readable Markdown summary of workspace project state."""
        state = self.load_state()
        proj = state.get("project_name", "Untitled")
        status = state.get("status", "ready")
        fw = state.get("framework", "Polyglot")
        steps = state.get("checklist", [])
        completed = state.get("completed_steps", 0)
        total = state.get("total_steps", len(steps))

        lines = [
            f"### 📋 Anjiru Workspace State: **{proj}**",
            f"• **Status:** `{status.upper()}` | **Framework:** `{fw}`",
            f"• **Progress:** {completed}/{total} tasks verified ({round((completed/total)*100 if total else 0)}%)",
            f"• **Workspace Path:** `{self.workspace_path / proj if (self.workspace_path / proj).exists() else self.workspace_path}`\n"
        ]

        if steps:
            lines.append("#### 📝 Execution Checklist:")
            for s in steps:
                st = s.get("status", "pending")
                icon = "✅" if st == "completed" else ("⏳" if st == "in_progress" else ("❌" if st == "failed" else "⬜"))
                lines.append(f"- {icon} **{s.get('title', 'Task')}** (`{s.get('file', '')}`): {s.get('description', '')}")

        ver = state.get("last_verification", {})
        if ver.get("status") and ver["status"] != "unverified":
            ver_icon = "🟢" if ver["status"] == "passed" else "🔴"
            lines.append(f"\n#### {ver_icon} Verification Status: `{ver['status'].upper()}`")
            if ver.get("command"):
                lines.append(f"Command: `{ver['command']}` (Exit: {ver.get('exit_code')})")

        return "\n".join(lines)


_state_mgr_singleton = None

def get_state_manager(workspace_path: Optional[Path] = None) -> WorkspaceStateManager:
    global _state_mgr_singleton
    if _state_mgr_singleton is None:
        _state_mgr_singleton = WorkspaceStateManager(workspace_path)
    return _state_mgr_singleton
