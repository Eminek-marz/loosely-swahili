"""
tests/test_polyglot_endpoints.py - Validates that the web server handler properly routes polyglot requests.
"""

import sys
import os
import json
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from web.server import ShengNLPHandler

class DummyServer:
    pass

class DummySocket:
    def makefile(self, *args, **kwargs):
        return io.BytesIO(b"")

def test_routes():
    print("[*] Testing polyglot server handler integration...")
    # Verify handler has the polyglot routes loaded
    import web.server as srv
    assert hasattr(srv, "polyglot_discovery"), "polyglot_discovery not initialized in server"
    assert hasattr(srv, "polyglot_sandbox"), "polyglot_sandbox not initialized in server"
    assert hasattr(srv, "polyglot_extractor"), "polyglot_extractor not initialized in server"
    assert hasattr(srv, "repo_map_engine"), "repo_map_engine not initialized in server"

    # Test discovery method directly
    cap = srv.polyglot_discovery.inspect_local_capabilities()
    assert "python" in cap, "Python missing from discovery"

    # Test stack detection
    st = srv.polyglot_discovery.detect_workspace_stack()
    assert "stack_name" in st, "Stack name missing from stack detection"

    # Test repomap
    rm = srv.repo_map_engine.generate_repo_map()
    assert "[REPO_MAP_OUTLINE]" in rm, "Repo map outline missing"

    # Test error extractor
    trace = "error: cannot find value `foo` in this scope\n --> src/main.rs:10:5"
    diag = srv.polyglot_extractor.parse_traceback(trace)
    assert diag["detected"] is True, "Failed to detect rust trace"
    assert diag["language"] == "rust", "Language mismatch"

    print("[✓] All polyglot server routing components verified successfully.")

if __name__ == "__main__":
    test_routes()
