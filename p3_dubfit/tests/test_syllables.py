"""Checks the syllable counter against lines counted by hand. Run: python tests/test_syllables.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dubfit import syllables

HAND = [("मकान मालिक ने पैसे नहीं दिए।", 11), ("तुम्हारी हिम्मत कैसे हुई?", 9), ("क्या आप मुझसे शादी करेंगी?", 9),
        ("ମୋ ଦରମା ତିନି ମାସ ହେଲା ମିଳିନି", 13), ("আমি তোমাকে ভালোবাসি", 9),
        ("Please accept my hand, my lady.", 8), ("Mujhe mera paisa wapas chahiye!", 10)]
res = [{"text": t, "hand": h, "counted": syllables(t), "off_by": syllables(t) - h} for t, h in HAND]
Path("outputs").mkdir(exist_ok=True)
Path("outputs/syllable_test.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
for r in res:
    print(f"{r['counted']:>3} vs {r['hand']:>3}  {r['text']}")
print(f"exact on {sum(r['off_by'] == 0 for r in res)}/{len(res)}")
