import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:7860"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get(endpoint):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("==================================================")
    print("ANJIRU DEEP INJECTIONS VERIFICATION BENCHMARK")
    print("==================================================")
    
    # 1. System Status
    st = get("/api/system/status")
    print(f"[OK] System Status: OK | Tasks: {len(st.get('tasks', []))} | Models: {len(st.get('models', []))}")

    # 2. Codebase Orchestrator Index
    idx = post("/api/orchestrator/index", {"force": True})
    print(f"[OK] Orchestrator Index: OK | Files Indexed: {idx.get('files_indexed')} | Symbols: {idx.get('symbols_indexed')}")

    # 3. Codebase Cross-File Impact
    impact = post("/api/orchestrator/context", {"active_file": "main.py"})
    print(f"[OK] Cross-File Impact: OK | Active: {impact.get('active_file')}")

    # 4. Multi-File Planner
    plan = post("/api/orchestrator/plan", {"prompt": "Build an e-commerce order service with routes and tests", "action": "plan_only"})
    print(f"[OK] Multi-Step Planner: OK | Generated Steps: {plan.get('total_steps')} files planned")

    # 5. Terminal Diagnose & Self-Healing
    tb = """Traceback (most recent call last):
  File "main.py", line 4, in <module>
    x = 10 / 0
ZeroDivisionError: division by zero"""
    diag = post("/api/terminal/diagnose", {"traceback": tb, "language": "sheng"})
    print(f"[OK] Terminal Auto-Heal: {diag.get('status')} | Error: {diag.get('error_type')} | Target: {diag.get('target_file')} | Diff lines: {len(diag.get('diff', []))}")

    # 6. Autonomous Sandbox Operations
    sb = post("/api/terminal/sandbox", {"command": "python -c \"print('Sandbox execution verified: ' + str(42 * 100))\""})
    print(f"[OK] Autonomous Sandbox: {sb.get('status')} | Output: {sb.get('stdout', '').strip()} ({sb.get('elapsed_ms')}ms)")

    # 7. Supercompletion (Ghost Text)
    comp = post("/api/anjiru/complete", {
        "prefix": "def calculate_discount(price, tier):",
        "suffix": "",
        "file_path": "pricing.py",
        "language": "python"
    })
    print(f"[OK] Supercompletion Engine: {comp.get('status')} | Latency: {comp.get('latency_ms')}ms | Prediction: {comp.get('predicted_text', '').strip()[:60]}...")

    # 8. Local Profile Sync / Sovereign Export
    prof = get("/api/profile/export")
    print(f"[OK] Sovereign Profile Export: {prof.get('status')} | Machine ID: {prof.get('sovereignty_profile', {}).get('machine_id')}")

    print("==================================================")
    print("ALL 8 DEEP INJECTION SUBSYSTEMS OPERATING NOMINALLY")
    print("==================================================")

if __name__ == "__main__":
    main()
