"""
src/universal_patch_engine.py - Universal Block Diffing & Structural Syntax Engine
Inspired by Aider's search/replace block editing and Tree-sitter AST structural mapping.
"""

import os
import re
import ast
import difflib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from .workspace_config import get_workspace_dir

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = get_workspace_dir()


class UniversalFileModifier:
    """
    Executes precise, language-agnostic code injections and block diffs.
    Avoids rewrites of entire files, preserving tokens and formatting idioms.
    """

    @staticmethod
    def normalize_newlines(text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    @classmethod
    def apply_block_patch(cls, file_content: str, patch_action: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Replaces search_block with replace_block.
        Tolerates arbitrary indentation, whitespace variations, and line-ending differences.
        Returns (new_content, metadata).
        """
        normalized_content = cls.normalize_newlines(file_content)
        raw_search = cls.normalize_newlines(patch_action.get("search_block", ""))
        replace_block = cls.normalize_newlines(patch_action.get("replace_block", ""))

        if not raw_search.strip():
            # Fallback append behavior
            new_content = normalized_content
            if new_content and not new_content.endswith("\n"):
                new_content += "\n"
            new_content += replace_block
            return new_content, {"match_strategy": "append", "replacements": 1}

        # Strategy 1: Exact substring match (preserves precise indentation)
        if raw_search in normalized_content:
            new_content = normalized_content.replace(raw_search, replace_block, 1)
            return new_content, {"match_strategy": "exact", "replacements": 1}

        search_block = raw_search.strip()

        # Strategy 2: Whitespace-flexible regex match
        escaped_search = re.escape(search_block)
        flexible_search = re.sub(r'\\\s+', r'\\s+', escaped_search)
        pattern = re.compile(flexible_search, re.MULTILINE)

        match = pattern.search(normalized_content)
        if match:
            new_content = pattern.sub(lambda _: replace_block, normalized_content, count=1)
            return new_content, {"match_strategy": "regex_flexible", "replacements": 1}

        # Strategy 3: Line-by-line fuzzy trim matching (handles indentation drift)
        search_lines = [l.strip() for l in search_block.splitlines() if l.strip()]
        content_lines = normalized_content.splitlines()

        if search_lines:
            match_start = -1
            match_len = len(search_lines)
            for i in range(len(content_lines) - match_len + 1):
                slice_stripped = [content_lines[i + j].strip() for j in range(match_len)]
                if slice_stripped == search_lines:
                    match_start = i
                    break

            if match_start != -1:
                # Replace the slice
                before = content_lines[:match_start]
                after = content_lines[match_start + match_len:]
                new_content = "\n".join(before + [replace_block] + after)
                return new_content, {"match_strategy": "line_trimmed_match", "replacements": 1}

        # If all strategies fail: produce a unified diff error diagnostic
        close_matches = difflib.get_close_matches(search_block, normalized_content.splitlines(), n=3, cutoff=0.6)
        error_msg = (
            f"Target patch pattern mismatch: search block not located in file.\n"
            f"Searched block preview:\n{search_block[:200]}..."
        )
        if close_matches:
            error_msg += f"\nPossible closest lines in file:\n" + "\n".join(close_matches)

        raise LookupError(error_msg)

    @classmethod
    def generate_unified_diff(cls, original_text: str, modified_text: str, filename: str = "file") -> str:
        """Returns standard unified diff format for auditing and UI review."""
        orig_lines = cls.normalize_newlines(original_text).splitlines(keepends=True)
        mod_lines = cls.normalize_newlines(modified_text).splitlines(keepends=True)
        diff = difflib.unified_diff(orig_lines, mod_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}")
        return "".join(diff)


class PolyglotRepoMap:
    """
    Aider-inspired Repository Map generator.
    Parses multi-language definitions (Python AST, JS/TS functions, Rust structs/impls, Go funcs)
    and produces an ultra-compact structural schema of the workspace.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or WORKSPACE_DIR

    def extract_symbols_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        ext = file_path.suffix.lower()
        symbols = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        # 1. Python AST parsing
        if ext == ".py":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                        args = [a.arg for a in node.args.args]
                        symbols.append({
                            "kind": "def",
                            "name": node.name,
                            "line": node.lineno,
                            "sig": f"def {node.name}({', '.join(args)})"
                        })
                    elif isinstance(node, ast.ClassDef):
                        symbols.append({
                            "kind": "class",
                            "name": node.name,
                            "line": node.lineno,
                            "sig": f"class {node.name}"
                        })
                return symbols
            except Exception:
                pass

        # 2. Rust parsing (regex structural extraction)
        if ext == ".rs":
            # fn name(...)
            for m in re.finditer(r'(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*\((.*?)\)', content):
                symbols.append({
                    "kind": "fn",
                    "name": m.group(1),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"fn {m.group(1)}({m.group(2)[:30]})"
                })
            # struct / enum
            for m in re.finditer(r'(?:pub\s+)?(struct|enum|trait)\s+([a-zA-Z0-9_]+)', content):
                symbols.append({
                    "kind": m.group(1),
                    "name": m.group(2),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"{m.group(1)} {m.group(2)}"
                })
            return symbols

        # 3. Go parsing
        if ext == ".go":
            for m in re.finditer(r'func\s+(?:\([^)]+\)\s+)?([a-zA-Z0-9_]+)\s*\((.*?)\)', content):
                symbols.append({
                    "kind": "func",
                    "name": m.group(1),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"func {m.group(1)}(...)"
                })
            for m in re.finditer(r'type\s+([a-zA-Z0-9_]+)\s+(struct|interface)', content):
                symbols.append({
                    "kind": m.group(2),
                    "name": m.group(1),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"type {m.group(1)} {m.group(2)}"
                })
            return symbols

        # 4. JavaScript / TypeScript
        if ext in [".js", ".jsx", ".ts", ".tsx"]:
            for m in re.finditer(r'(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_]+)\s*\((.*?)\)', content):
                symbols.append({
                    "kind": "function",
                    "name": m.group(1),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"function {m.group(1)}()"
                })
            for m in re.finditer(r'(?:export\s+)?class\s+([a-zA-Z0-9_]+)', content):
                symbols.append({
                    "kind": "class",
                    "name": m.group(1),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"class {m.group(1)}"
                })
            # const myFunc = () =>
            for m in re.finditer(r'(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', content):
                symbols.append({
                    "kind": "arrow_fn",
                    "name": m.group(1),
                    "line": content[:m.start()].count('\n') + 1,
                    "sig": f"const {m.group(1)} = () =>"
                })
            return symbols

        return symbols

    def generate_repo_map(self, max_tokens: int = 1500) -> str:
        """
        Produces an ultra-condensed repo map outline of workspace symbols.
        Example:
        students/models.py:
          class Student
          class Course
        students/views.py:
          def get_students()
        """
        lines = ["[REPO_MAP_OUTLINE]"]
        total_symbols = 0

        valid_exts = {".py", ".rs", ".go", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp"}

        for root, dirs, files in os.walk(str(self.workspace_path)):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv", "node_modules", "target", "dist"}]
            for f in sorted(files):
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_exts:
                    full_p = Path(root) / f
                    rel_p = str(full_p.relative_to(self.workspace_path)).replace("\\", "/")
                    syms = self.extract_symbols_from_file(full_p)
                    if syms:
                        lines.append(f"{rel_p}:")
                        for s in syms[:8]: # cap per file
                            lines.append(f"  {s['sig']}")
                            total_symbols += 1
                        if len(syms) > 8:
                            lines.append(f"  ... (+{len(syms) - 8} more symbols)")
                    else:
                        lines.append(f"{rel_p} (source file)")

        lines.append(f"[END_REPO_MAP: {total_symbols} symbols mapped]")
        return "\n".join(lines)


_repo_map_instance = None

def get_repo_map(workspace_path: Optional[Path] = None) -> PolyglotRepoMap:
    global _repo_map_instance
    if _repo_map_instance is None:
        _repo_map_instance = PolyglotRepoMap(workspace_path=workspace_path)
    return _repo_map_instance
