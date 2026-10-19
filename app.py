"""
app.py - Deployment Entrypoint for Hugging Face Spaces, Render, and Cloud Containers.
Launches the Loosely Swahili Interactive Web Studio & REST API.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from web.server import run_server

if __name__ == "__main__":
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_f = open(logs_dir / "daemon.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = log_f
    sys.stderr = log_f

    import datetime
    import traceback
    try:
        # Hugging Face Spaces defaults to port 7860; Render/Railway provide $PORT (or 8080)
        port = int(os.environ.get("PORT", 7860))
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Anjiru.AI on port {port}...")
        run_server(port)
    except Exception as e:
        traceback.print_exc(file=log_f)
        log_f.flush()
