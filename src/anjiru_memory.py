"""
src/anjiru_memory.py - Persistent Memory Point Management Engine for Anjiru.AI
Provides concrete, filesystem-backed memory points that can be:
- CREATED: Provisioned as an actual directory on disk with metadata & manifest
- READ: Inspected for objectives, checkpoints, files, and contextual knowledge
- UPDATED: Dynamically augmented with new notes, code artifacts, or status transitions
- DELETED: Cleanly decommissioned and purged from workspace storage
Modeled after Antigravity's autonomous agent session memory & artifact architecture.
"""

import os
import json
import time
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .workspace_config import get_workspace_dir

MANIFEST_FILENAME = "memory_manifest.json"

class AnjiruMemoryManager:
    """
    Manages physical memory points on disk within the Anjiru workspace.
    Each memory point is an actual directory containing:
    1. memory_manifest.json - Structured metadata, objectives, milestones, notes
    2. Real code, configuration, or documentation files
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or get_workspace_dir()
        self.memory_root = (self.workspace_path / "memory_points").resolve()
        self.memory_root.mkdir(parents=True, exist_ok=True)

    def _sanitize_name(self, raw_name: str) -> str:
        """Sanitizes memory point name for safe directory naming."""
        clean = raw_name.strip().replace(" ", "_").lower()
        clean = re.sub(r'[^a-zA-Z0-9_\-]', '', clean)
        clean = re.sub(r'_+', '_', clean).strip('_')
        return clean or f"memory_{int(time.time())}"

    def create_memory_point(
        self,
        name: str,
        objective: str = "",
        tags: Optional[List[str]] = None,
        initial_notes: Optional[str] = None,
        initial_files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Creates an actual folder on disk representing a persistent memory point.
        """
        slug = self._sanitize_name(name)
        point_dir = self.memory_root / slug
        point_dir.mkdir(parents=True, exist_ok=True)

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        manifest_file = point_dir / MANIFEST_FILENAME

        # Check if already exists
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                return {
                    "status": "exists",
                    "id": slug,
                    "name": existing.get("name", name),
                    "path": str(point_dir),
                    "rel_path": f"memory_points/{slug}",
                    "manifest": existing,
                    "message": f"Memory point '{slug}' already exists."
                }
            except Exception:
                pass

        files_written = []
        # Write any initial files
        if initial_files:
            for fname, fcontent in initial_files.items():
                clean_f = Path(fname.strip().replace("../", "").lstrip("/\\"))
                f_path = point_dir / clean_f
                f_path.parent.mkdir(parents=True, exist_ok=True)
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(fcontent)
                files_written.append(str(clean_f).replace("\\", "/"))

        # Default README if no initial files
        if not files_written:
            readme_path = point_dir / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# Memory Point: {name}\n\n**Objective:** {objective or 'Persistent knowledge & workspace context'}\n\n**Created:** {now_str}\n")
            files_written.append("README.md")

        manifest = {
            "version": "1.0.0",
            "id": slug,
            "name": name,
            "objective": objective or "Autonomous task and architecture memory checkpoint",
            "tags": tags or ["agentic", "memory_point"],
            "status": "active",
            "created_at": now_str,
            "updated_at": now_str,
            "notes": [
                {
                    "timestamp": now_str,
                    "text": initial_notes or f"Memory point initialized with objective: {objective or 'N/A'}"
                }
            ],
            "tracked_files": files_written,
            "checkpoints": [
                {"title": "Initialization", "status": "completed", "timestamp": now_str}
            ]
        }

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "id": slug,
            "name": name,
            "path": str(point_dir),
            "rel_path": f"memory_points/{slug}",
            "manifest": manifest,
            "message": f"Successfully created memory point '{slug}' at {point_dir}"
        }

    def read_memory_point(self, name_or_id: str) -> Dict[str, Any]:
        """
        Reads an actual memory point folder and its manifest and files from disk.
        """
        slug = self._sanitize_name(name_or_id)
        point_dir = self.memory_root / slug

        if not point_dir.exists() or not point_dir.is_dir():
            # Check if name is given directly
            candidates = [p for p in self.memory_root.iterdir() if p.is_dir() and (p.name.lower() == name_or_id.lower() or slug in p.name.lower())]
            if candidates:
                point_dir = candidates[0]
                slug = point_dir.name
            else:
                return {
                    "status": "error",
                    "message": f"Memory point '{name_or_id}' not found in {self.memory_root}."
                }

        manifest_file = point_dir / MANIFEST_FILENAME
        manifest = {}
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception as e:
                manifest = {"error": f"Failed to parse manifest: {e}"}

        # Scan actual files on disk
        files_info = []
        for p in point_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(point_dir)).replace("\\", "/")
                files_info.append({
                    "name": p.name,
                    "rel_path": rel,
                    "size_bytes": p.stat().st_size,
                    "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))
                })

        return {
            "status": "success",
            "id": slug,
            "name": manifest.get("name", slug),
            "path": str(point_dir),
            "rel_path": f"memory_points/{slug}",
            "manifest": manifest,
            "files": files_info,
            "total_files": len(files_info)
        }

    def update_memory_point(
        self,
        name_or_id: str,
        note: Optional[str] = None,
        objective: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        files_to_add: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Updates an existing memory point by adding notes, updating metadata, or writing files.
        """
        read_res = self.read_memory_point(name_or_id)
        if read_res.get("status") != "success":
            return read_res

        slug = read_res["id"]
        point_dir = Path(read_res["path"])
        manifest = read_res["manifest"]
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        if objective:
            manifest["objective"] = objective
        if status:
            manifest["status"] = status
        if tags:
            existing_tags = set(manifest.get("tags", []))
            existing_tags.update(tags)
            manifest["tags"] = sorted(list(existing_tags))
        if note:
            manifest.setdefault("notes", []).append({
                "timestamp": now_str,
                "text": note
            })

        # Write or update files
        if files_to_add:
            for fname, fcontent in files_to_add.items():
                clean_f = Path(fname.strip().replace("../", "").lstrip("/\\"))
                f_path = point_dir / clean_f
                f_path.parent.mkdir(parents=True, exist_ok=True)
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(fcontent)
                rel_f = str(clean_f).replace("\\", "/")
                if rel_f not in manifest.setdefault("tracked_files", []):
                    manifest["tracked_files"].append(rel_f)

        manifest["updated_at"] = now_str
        manifest_file = point_dir / MANIFEST_FILENAME
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "id": slug,
            "name": manifest.get("name", slug),
            "rel_path": f"memory_points/{slug}",
            "manifest": manifest,
            "message": f"Updated memory point '{slug}' successfully."
        }

    def delete_memory_point(self, name_or_id: str) -> Dict[str, Any]:
        """
        Deletes the physical memory point directory from disk.
        """
        slug = self._sanitize_name(name_or_id)
        point_dir = self.memory_root / slug

        if not point_dir.exists() or not point_dir.is_dir():
            candidates = [p for p in self.memory_root.iterdir() if p.is_dir() and (p.name.lower() == name_or_id.lower() or slug in p.name.lower())]
            if candidates:
                point_dir = candidates[0]
                slug = point_dir.name
            else:
                return {
                    "status": "error",
                    "message": f"Memory point '{name_or_id}' not found."
                }

        try:
            shutil.rmtree(point_dir)
            return {
                "status": "success",
                "id": slug,
                "message": f"Successfully deleted memory point '{slug}' from disk."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete memory point '{slug}': {str(e)}"
            }

    def list_memory_points(self) -> List[Dict[str, Any]]:
        """
        Lists all persistent memory points present on disk with summary metadata.
        """
        results = []
        if not self.memory_root.exists():
            return results

        for p in self.memory_root.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                manifest_file = p / MANIFEST_FILENAME
                manifest = {}
                if manifest_file.exists():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                    except Exception:
                        pass

                file_count = sum(1 for _ in p.rglob("*") if _.is_file())
                results.append({
                    "id": p.name,
                    "name": manifest.get("name", p.name),
                    "objective": manifest.get("objective", ""),
                    "status": manifest.get("status", "active"),
                    "tags": manifest.get("tags", []),
                    "created_at": manifest.get("created_at", ""),
                    "updated_at": manifest.get("updated_at", ""),
                    "file_count": file_count,
                    "rel_path": f"memory_points/{p.name}"
                })

        return sorted(results, key=lambda x: x.get("updated_at", ""), reverse=True)


_global_memory_mgr: Optional[AnjiruMemoryManager] = None

def get_memory_manager(workspace_path: Optional[Path] = None) -> AnjiruMemoryManager:
    """Returns the singleton AnjiruMemoryManager instance."""
    global _global_memory_mgr
    if _global_memory_mgr is None or workspace_path is not None:
        _global_memory_mgr = AnjiruMemoryManager(workspace_path)
    return _global_memory_mgr
