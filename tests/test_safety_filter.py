import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.safety_filter import get_safety_filter
import time

filter = get_safety_filter()

test_cases = [
    ("The CGMM genomics algorithm accelerates alignment of homologous sequences.", True),
    ("Studies in sexual reproduction in angiosperms show high genetic diversity.", True),
    ("The patient was admitted to the trauma center with cardiac arrest.", True),
    ("Huyu msee anauza ngono na porn videos kwa telegram.", False),
    ("Tunafaa kwenda kuwachinja hao watu na kumwaga damu mtaani.", False),
    ("Nataka kujiua na kujinyonga maisha haina maana tena.", False),
    ("All Kikuyus are thieves and madoadoa lazima waondoke.", False),
    ("Manze jana tulicheki movie poa sana na mabuda mtaani.", True),
    ("Tuna-compute gradient loss tukitumia AdamW optimizer.", True)
]

print("=== TESTING ANJIRU SAFETY & DETOXIFICATION FILTER ===")
all_pass = True
for text, expected in test_cases:
    is_safe, reason = filter.is_safe(text)
    status = "PASS" if is_safe == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"[{status}] Safe: {str(is_safe):<5} ({reason:<27}) | \"{text[:50]}...\"")

# Speed benchmark on 50,000 iterations
t0 = time.time()
sample = "Tuna-compute gradient loss tukitumia AdamW optimizer na Bantu concord."
for _ in range(50000):
    filter.is_safe(sample)
elapsed = time.time() - t0
rate = 50000 / max(0.001, elapsed)
print(f"\n✓ SPEED BENCHMARK: {rate:,.0f} sentences / second on CPU!")
print(f"Audit Summary: {filter.get_audit_report()}")
assert all_pass, "Some safety filter test cases failed!"
print("\n>>> ALL SAFETY TESTS PASSED 100% OK! <<<")
