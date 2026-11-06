"""Enumerate (K)-only edges modulo gamma_4 of free class 4 on <= 3 generators at d = 5 (up to scaling characters by units)."""
import itertools, sys, json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edge_conditions_mod4 import conds
d, p = 5, 11
seen, out = set(), []
for n in (2, 3):
    for chars in itertools.combinations_with_replacement(range(d), n):
        if not any(c % d for c in chars): continue
        canon = min(tuple(sorted((u * c) % d for c in chars)) for u in range(1, d))
        if canon in seen: continue
        seen.add(canon)
        for a in range(1, d):
            for b in range(1, d):
                if (a + b) % d == 0 or a not in chars or b not in chars: continue
                try:
                    r = conds(list(chars), d, p, (a, b))
                except Exception as ex:
                    print("ERR", chars, (a, b), ex, flush=True); continue
                if r["pair bracket nonzero"] and r["failing"] == ["K"]:
                    out.append({"chars": list(chars), "edge": [a, b], **{k: r[k] for k in ("roots", "gamma_4 chars", "slot-2 layer-1 data")}})
                    print(json.dumps(out[-1]), flush=True)
