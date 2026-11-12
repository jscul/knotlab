import sys, json
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from collections import Counter
rows = {}
for l in open("reach.jsonl"):
    r = json.loads(l); rows.setdefault((r["q"], r["base"]), []).extend(r["rows"])
for (q, b), rr in sorted(rows.items()):
    rr.sort()
    rc = Counter(x[1] for x in rr); bc = Counter(x[2] for x in rr)
    print(q, b, "u covered", len(rr), "reach values (count>=3):", sorted(v for v, c in rc.items() if c >= 3), " back-reach values:", sorted(v for v, c in bc.items() if c >= 3))
    if q == 0.0:
        k = regen(q, b); kn = {max(t): t for t in k}
        words = [c for c in range(5, 795) if (c - 1) in kn[c] and kn.get(c + 1) == (c - 1, c, c + 1) and kn.get(c + 2) == (c - 1, c, c + 2) and kn.get(c + 3) == (c + 1, c + 2, c + 3)]
        print("   twin-pair words at b =", words)
