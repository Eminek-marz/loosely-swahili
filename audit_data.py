import os
import json
from pathlib import Path

def inspect_file(p):
    p = Path(p)
    if not p.exists() or p.is_dir():
        return None
    size_mb = p.stat().st_size / (1024 * 1024)
    lines = 0
    words = 0
    try:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                lines += 1
                words += len(line.split())
    except Exception:
        pass
    return {'size_mb': round(size_mb, 2), 'lines': lines, 'words': words}

print('=== DRIVE D: ANJIRU CORPUS (D:/ANJIRU_AI_MASSIVE_CORPUS) ===')
d_base = Path('D:/ANJIRU_AI_MASSIVE_CORPUS')
d_total_lines = 0
d_total_words = 0
d_total_mb = 0.0

if d_base.exists():
    for f in sorted(d_base.rglob('*.*')):
        if f.suffix in ['.jsonl', '.json', '.txt', '.csv']:
            res = inspect_file(f)
            if res:
                rel = str(f.relative_to(d_base))
                d_total_lines += res['lines']
                d_total_words += res['words']
                d_total_mb += res['size_mb']
                lines_str = f"{res['lines']:,}"
                words_str = f"{res['words']:,}"
                size_str = f"{res['size_mb']:.2f} MB"
                print(f"{rel:<52} | {lines_str:>10} lines | {words_str:>12} words | {size_str:>10}")

print('-' * 95)
print(f"TOTAL ON DRIVE D: {d_total_lines:,} lines | {d_total_words:,} words | {d_total_mb:.2f} MB")

print('\n=== LOCAL WORKSPACE (data/) ===')
w_base = Path('data')
w_total_lines = 0
w_total_words = 0
w_total_mb = 0.0

if w_base.exists():
    for f in sorted(w_base.rglob('*.*')):
        if f.suffix in ['.jsonl', '.json', '.txt', '.csv']:
            res = inspect_file(f)
            if res:
                rel = str(f.relative_to(w_base))
                w_total_lines += res['lines']
                w_total_words += res['words']
                w_total_mb += res['size_mb']
                lines_str = f"{res['lines']:,}"
                words_str = f"{res['words']:,}"
                size_str = f"{res['size_mb']:.2f} MB"
                print(f"{rel:<52} | {lines_str:>10} lines | {words_str:>12} words | {size_str:>10}")

print('-' * 95)
print(f"TOTAL LOCAL WORKSPACE: {w_total_lines:,} lines | {w_total_words:,} words | {w_total_mb:.2f} MB")
print('=' * 95)
grand_lines = d_total_lines + w_total_lines
grand_words = d_total_words + w_total_words
grand_mb = d_total_mb + w_total_mb
print(f"GRAND TOTAL DATA: {grand_lines:,} lines/records | {grand_words:,} words | {grand_mb:.2f} MB")
