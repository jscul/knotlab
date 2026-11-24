"""The thread's side check of run 5, after the runs: with the pilot's program (no distinctions in it), in how many census
starts of up to five knots does a two-knot part appear by round 8 under FLOOR1 with each treatment?  By the settled
statement a two-knot part past its start copies itself within two rounds, so this count should be close to the engine's
count of starts with a part that copies itself (3,126 retiring, 3,229 offshoots, 2,851 waiting, of 3,344).
Starts the pilot's program refuses or that fail its own lawfulness test are counted separately.
Run from the repository root with .venv/bin/python -B."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs/prompts/2026-11-23_balance_pilot/balance"))
sys.path.insert(0, str(ROOT / "experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies"))
import roster as R
import cpcensus as C

def two_knot_parts(state):
    return sum(1 for part in map(set, R.parts(state))
               if len(part) == 2 and all(state.h[u] == 2 for u in part) and any(part <= set(s) for s in state.wsets))

TREAT = {"retiring": "CANCEL-END", "offshoots": "CANCEL-BUD", "waiting": "CANCEL-WAIT"}
tot = 0; seen = {k: 0 for k in TREAT}; refused = 0
for n in (3, 4, 5):
    for gi, loose in C.starts(n):
        stars = C.stars(gi, loose)
        try:
            st0 = R.from_stars(stars)
        except Exception:
            refused += 1; continue
        tot += 1
        for name, shortage in TREAT.items():
            st = st0.copy(); law = R.Law("FLOOR1", shortage, True); hit = two_knot_parts(st) > 0; knots = len(stars)
            for r in range(8):
                if hit: break
                t = R.step(st, law)
                if t.status != "extend": break
                st = t.state; knots += len(t.births); hit = two_knot_parts(st) > 0
                if knots > 1500: break
            seen[name] += hit
print(f"{tot} starts run ({refused} refused by the pilot's program); a two-knot part appears by round 8 in: {seen}")
