"""
src/polyglot_error_extractor.py - Universal Polyglot Error Extractor & Self-Healing Diagnostics
Parses compiler and runtime failure traces across Python, Rust, Go, Node.js, C/C++, and Java
into normalized contextual frames for the self-healing execution loop.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .workspace_config import get_workspace_dir

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = get_workspace_dir()


class PolyglotErrorExtractor:
    """
    Parses arbitrary terminal crash footprints into normalized contextual frames.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or WORKSPACE_DIR

        # Ordered regex signatures
        self.error_signatures = [
            # Rust Cargo compiler
            {
                "lang": "rust",
                "regex": re.compile(r'error(?:\[(?P<code>E\d+)\])?: (?P<message>.*?)\n\s+-->\s+(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+)', re.MULTILINE),
            },
            # Python Tracebacks
            {
                "lang": "python",
                "regex": re.compile(r'File "(?P<file>[^"]+)", line (?P<line>\d+)(?:, in (?P<func>.*))?\n(?P<context>.*?\n)?(?P<type>[a-zA-Z0-9_.]+(?:Error|Exception)): (?P<message>.*)', re.MULTILINE),
            },
            # Node / JS / TS stack traces
            {
                "lang": "javascript",
                "regex": re.compile(r'(?P<type>[a-zA-Z0-9_]+Error): (?P<message>.*?)\n\s+at (?:(?P<func>[^\s]+) \()?(?P<file>[^:()]+):(?P<line>\d+):(?P<col>\d+)\)?', re.MULTILINE),
            },
            # Go compiler failures
            {
                "lang": "go",
                "regex": re.compile(r'(?P<file>[^:\s]+\.go):(?P<line>\d+):(?P<col>\d+): (?P<message>.*)', re.MULTILINE),
            },
            # GCC / Clang C / C++ compiler
            {
                "lang": "c/c++",
                "regex": re.compile(r'(?P<file>[^:\s]+\.(?:c|cpp|cc|h|hpp)):(?P<line>\d+):(?P<col>\d+): (?:fatal )?error: (?P<message>.*)', re.MULTILINE),
            },
            # Java compiler
            {
                "lang": "java",
                "regex": re.compile(r'(?P<file>[^:\s]+\.java):(?P<line>\d+): error: (?P<message>.*)', re.MULTILINE),
            }
        ]

    def parse_traceback(self, raw_stderr: str) -> Dict[str, Any]:
        """
        Scans raw stderr and extracts normalized error fields.
        """
        text = (raw_stderr or "").strip()
        if not text:
            return {
                "detected": False,
                "target_file": "unknown",
                "line_number": 0,
                "column": 0,
                "language": "unknown",
                "error_type": "None",
                "diagnostic_message": "No error output found.",
                "raw_context": ""
            }

        for sig in self.error_signatures:
            matches = list(sig["regex"].finditer(text))
            if matches:
                # Use the last frame (most specific)
                match = matches[-1]
                data = match.groupdict()
                file_p = data.get("file", "").strip()

                # Clean up file path relative to workspace
                if os.path.isabs(file_p):
                    try:
                        file_p = str(Path(file_p).relative_to(self.workspace_path)).replace("\\", "/")
                    except ValueError:
                        file_p = os.path.basename(file_p)
                else:
                    file_p = file_p.replace("\\", "/")

                err_type = data.get("type", "CompileError" if sig["lang"] in ["rust", "go", "c/c++"] else "RuntimeError")
                err_msg = data.get("message", "").strip()

                return {
                    "detected": True,
                    "target_file": file_p,
                    "line_number": int(data.get("line", 1)),
                    "column": int(data.get("col", 0) or 0),
                    "language": sig["lang"],
                    "error_type": err_type,
                    "diagnostic_message": err_msg or "Unspecified compiler error",
                    "raw_context": text[-1000:]
                }

        # Fallback for unrecognized error traces
        first_line = text.splitlines()[0] if text else "Unknown Error"
        return {
            "detected": False,
            "target_file": "unknown",
            "line_number": 0,
            "column": 0,
            "language": "unknown",
            "error_type": "UnclassifiedError",
            "diagnostic_message": first_line[:200],
            "raw_context": text[-800:]
        }

    def generate_healing_blueprint(
        self,
        trace_data: Dict[str, Any],
        language_pref: str = "sheng"
    ) -> Dict[str, Any]:
        """
        Translates parsed error into localized diagnosis and automated resolution actions.
        """
        lang = trace_data.get("language", "python")
        err_type = trace_data.get("error_type", "")
        err_msg = trace_data.get("diagnostic_message", "")
        target_file = trace_data.get("target_file", "")
        line_no = trace_data.get("line_number", 0)

        # Localized descriptions
        sheng_desc = f"Hitilafu ya **{err_type}** kwenye faili `{target_file}` mstari {line_no}: {err_msg}."
        swahili_desc = f"Hitilafu ya **{err_type}** imetambuliwa katika faili `{target_file}` mstari wa {line_no}: {err_msg}."
        english_desc = f"Identified **{err_type}** in `{target_file}` at line {line_no}: {err_msg}."

        recommended_action = "Review target line and patch syntax or dependencies."

        # Rust specific
        if lang == "rust":
            if "mismatched types" in err_msg.lower():
                sheng_desc += " Aina za data hazilingani (type mismatch). Badilisha type au tumia `.into()` / `.to_string()`."
                swahili_desc += " Aina za data haziendani. Rekebisha aina ya kigezo kwa kubadilisha unyumbufu."
                recommended_action = "Apply explicit type cast or adjust function signature."
            elif "cannot find value" in err_msg.lower() or "not found in this scope" in err_msg.lower():
                sheng_desc += " Thamani au crate haijapatikana. Ongeza `use` statement au crate kwa `Cargo.toml`."
                swahili_desc += " Thamani haijatambuliwa. Ongeza taarifa ya `use` au tegemezi katika `Cargo.toml`."
                recommended_action = "Import missing crate or module."

        # Go specific
        elif lang == "go":
            if "undefined" in err_msg.lower():
                sheng_desc += " Variable au function haija-declareiwa au package haija-importiwa."
                swahili_desc += " Kigezo hakijatambuliwa au kifurushi hakijaagizwa."
                recommended_action = "Add missing package import to Go source."

        # Python specific
        elif lang == "python":
            if "ModuleNotFoundError" in err_type or "No module named" in err_msg:
                missing_mod = re.findall(r"No module named ['\"]([^'\"]+)['\"]", err_msg)
                mod_name = missing_mod[0] if missing_mod else "package"
                sheng_desc += f" Moduli `{mod_name}` haipo. Inahitaji ku-installiwa kupitia `pip install {mod_name}`."
                swahili_desc += f" Moduli `{mod_name}` haijapatikana. Sakinisha kupitia `pip`."
                recommended_action = f"Run: pip install {mod_name}"

        chosen_explanation = english_desc
        if language_pref.lower() == "sheng":
            chosen_explanation = sheng_desc
        elif language_pref.lower() == "swahili":
            chosen_explanation = swahili_desc

        return {
            "status": "ready",
            "detected": trace_data.get("detected", False),
            "language": lang,
            "target_file": target_file,
            "line_number": line_no,
            "explanation": chosen_explanation,
            "recommended_action": recommended_action,
            "action_type": "PATCH_FILE" if target_file != "unknown" else "RUN_COMMAND"
        }


_error_extractor_instance = None

def get_error_extractor(workspace_path: Optional[Path] = None) -> PolyglotErrorExtractor:
    global _error_extractor_instance
    if _error_extractor_instance is None:
        _error_extractor_instance = PolyglotErrorExtractor(workspace_path=workspace_path)
    return _error_extractor_instance
