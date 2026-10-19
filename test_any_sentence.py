"""
Interactive CLI Tester: Test any Kenyan Sheng or Code-Switched sentence live.
"""

import sys
from pathlib import Path

# Ensure UTF-8 terminal output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.normalizer import ShengNormalizerPipeline
from src.tokenizer import ShengCodeSwitchTokenizer
from src.loosely_swahili_engine import LooselySwahiliValidator

def analyze(sentence: str):
    pipeline = ShengNormalizerPipeline()
    res = pipeline.process(sentence)
    validator = LooselySwahiliValidator()
    report = validator.audit_sentence(sentence)

    print("\n" + "=" * 70)
    print("🇰🇪 SHENG & CODE-SWITCHING LIVE MODEL TEST")
    print("=" * 70)
    print(f"INPUT SENTENCE:       \"{res.original_text}\"")
    print("-" * 70)
    print(f"FORMAL SWAHILI:       {res.normalized_swahili}")
    print(f"ENGLISH TRANSLATION:  {res.english_translation}")
    print("-" * 70)
    print(f"CODE-SWITCH MIX:      {res.code_switch_metrics['sheng_ratio']}% Sheng | {res.code_switch_metrics['swahili_ratio']}% Swahili | {res.code_switch_metrics['english_ratio']}% English")
    print("-" * 70)
    
    eff = res.token_efficiency
    print(f"STANDARD BPE TOKENS:  ({eff['standard_bpe_count']} tokens - SHATTERED)")
    print(f"                      {eff['standard_bpe_tokens']}")
    print(f"OUR SHENG TOKENS:     ({eff['sheng_aware_count']} tokens - CLEAN)")
    print(f"                      {eff['sheng_aware_tokens']}")
    print(f"TOKEN COMPUTE SAVED:  {eff['token_reduction_savings_pct']}% SAVINGS 🚀")
    print("-" * 70)

    # 7-Pillars & Emergent Rules Compliance Audit
    status_icon = "✅ COMPLIANT" if report.is_fully_compliant else "⚠️ RULE ISSUES DETECTED"
    print(f"BLUEPRINT GRAMMAR:    {status_icon}")
    if report.pillars_triggered:
        print(f"PILLARS DETECTED:     {', '.join(report.pillars_triggered)}")

    # Metathesis Structural Insulation Layer Showcase
    if "Pillar X: Metathesis Inversion" in report.pillars_triggered:
        syn = report.syntactic_breakdown
        mode = syn.get("metathesis_slider_mode", "STANDARD_INSULATED")
        print("-" * 70)
        print(f"METATHESIS ENGINE:    [SLIDER MODE: {mode}]")
        print(f"  • Visual Glancing:   \"{syn.get('visual_glancing', '')}\"")
        print(f"  • Silent Normal:     \"{syn.get('silent_normalization', '')}\"")
        for m in syn.get("metathesis", []):
            shift_info = f" [SEMANTIC SHIFT: {m['safe_universal_equivalent']}]" if m.get("is_semantic_shift") else ""
            print(f"    - '{m['surface_form']}' -> Rewritten to '{m['internal_rewrite']}' ({m['primary_risk_factor']}){shift_info}")

    # Soft-Target Infix Modifier (-ka-) Showcase
    if "Pillar I: Soft-Target Modifier (-ka-)" in report.pillars_triggered:
        print("-" * 70)
        print("AFFECTIVE MODIFIER:   [SOFT-TARGET INFIX -ka- DETECTED 🎯]")
        for v in report.syntactic_breakdown.get("verbs", []):
            if v.get("is_soft_target"):
                print(f"  • Verb Complex:     {v['surface_form']}")
                print(f"  • Morph Breakdown:  [{v['subject_prefix']}-] + [{v['tense_marker']}-] + [-ka-] + [{v['bare_verb_root']}]")
                print(f"  • Affect Matrix:    {v['emotional_affect']}")
                print(f"  • Nuanced Meaning:  {v['english_translation']}")

    # Disgust / Sarcasm Inanimate Shift (Forced Ki-) Showcase
    if "Pillar I: Disgust / Contempt Modifier (Forced Ki-)" in report.pillars_triggered:
        print("-" * 70)
        print("SARCASM & DISGUST:    [FORCED Ki- INANIMATE COLLAPSE DETECTED ⚡]")
        for v in report.syntactic_breakdown.get("verbs", []):
            if v.get("is_disgust_depersonalized"):
                print(f"  • Verb Complex:     {v['surface_form']}")
                print(f"  • Morph Breakdown:  [{v['subject_prefix']}- (Forced Inanimate It)] + [{v['tense_marker']}-] + [{v['bare_verb_root']}]")
                print(f"  • Sarcasm Matrix:   {v['emotional_affect']}")
                print(f"  • Nuanced Meaning:  {v['english_translation']}")

    if report.issues:
        for issue in report.issues:
            print(f"  • [{issue.pillar} - {issue.rule_name}] ({issue.severity}): {issue.faulty_segment}")
            print(f"    Reason: {issue.explanation}")
            print(f"    Fix:    {issue.suggestion}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_input = " ".join(sys.argv[1:])
    else:
        test_input = "Niko mtaani na mayouth tukipiga luku safi."
    analyze(test_input)

