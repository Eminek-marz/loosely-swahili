"""
One-Command Hugging Face Hub Dataset Publisher
Uploads the harvested Kenyan Code-Switching dataset (train.jsonl, test.jsonl, README.md, dataset_info.json)
directly to the Hugging Face Hub using the official huggingface_hub client.
"""

import sys
import os
import argparse
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_ROOT / "data" / "huggingface_dataset"

def upload_dataset(repo_id: str, token: str = None, private: bool = False):
    print("=" * 75)
    print(f"🚀 UPLOADING KENYAN NLP DATASET TO HUGGING FACE HUB: {repo_id}")
    print("=" * 75)

    if not DATASET_DIR.exists():
        print(f"[ERROR] Directory {DATASET_DIR} does not exist. Run export_huggingface_dataset.py first.")
        return

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[!] huggingface_hub package is not installed. Installing it now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        from huggingface_hub import HfApi, create_repo

    api = HfApi(token=token)

    print(f"[*] Ensuring repository '{repo_id}' exists on Hugging Face...")
    try:
        create_repo(repo_id=repo_id, repo_type="dataset", private=private, token=token, exist_ok=True)
        print("    -> Repository verified.")
    except Exception as e:
        print(f"    -> Repo note: {e}")

    print(f"[*] Uploading dataset files from {DATASET_DIR}...")
    try:
        api.upload_folder(
            folder_path=str(DATASET_DIR),
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Add initial Kenyan Sheng and Code-Switching Parallel Corpus (1,100+ triples)"
        )
        print("\n" + "=" * 75)
        print("🎉 SUCCESS! DATASET IS NOW LIVE ON HUGGING FACE:")
        print(f"👉 https://huggingface.co/datasets/{repo_id}")
        print("=" * 75)
    except Exception as e:
        print(f"\n[ERROR] Upload failed: {e}")
        print("Ensure your HF token has 'write' permissions at https://huggingface.co/settings/tokens")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Kenyan Code-Switching Corpus to Hugging Face")
    parser.add_argument("--repo-id", "-r", type=str, help="Hugging Face repo id, e.g. username/kenyan-sheng-corpus")
    parser.add_argument("--token", "-t", type=str, help="Hugging Face User Access Token (write permission)")
    parser.add_argument("--private", action="store_true", help="Set repository to private")
    args = parser.parse_args()

    repo = args.repo_id
    if not repo:
        print("\n[Hugging Face Upload Setup]")
        repo = input("Enter your Hugging Face repo ID (e.g. your-username/kenyan-sheng-corpus): ").strip()
    
    if not repo:
        print("No repository specified. Exiting.")
        sys.exit(1)

    tok = args.token or os.environ.get("HF_TOKEN")
    if not tok:
        tok = input("Enter your Hugging Face write token (or press Enter if logged in via `huggingface-cli login`): ").strip()
        tok = tok if tok else None

    upload_dataset(repo_id=repo, token=tok, private=args.private)
