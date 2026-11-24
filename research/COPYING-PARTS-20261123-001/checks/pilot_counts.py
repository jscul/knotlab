"""The thread's side check, made after the freeze: the number of two-knot parts by round in the pilot's program
(a private workspace file with no distinctions in it), for the three starts under FLOOR0 with each treatment, and the
three frozen recurrences.  Run from the repository root with .venv/bin/python -B."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs/prompts/2026-11-23_balance_pilot/balance"))
import roster as R

STARTS = {"two-knot start": [[0, 1, 2], [0, 3, 4]],
          "three-knot start": [[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 6, 7]],
          "Ring(5, 3)": [[(i - 1) % 5, i, 5 + 3 * i, 6 + 3 * i, 7 + 3 * i] for i in range(5)]}
TREAT = {"retiring": "CANCEL-END", "offshoots": "CANCEL-BUD", "waiting": "CANCEL-WAIT"}   # the pilot's names

def two_knot_parts(state):
    n = 0
    for part in R.parts(state):
        part = set(part)
        if len(part) == 2 and all(state.h[u] == 2 for u in part) and any(part <= set(s) for s in state.wsets):
            n += 1
    return n

def recurrence(seq, name):
    first = next((i for i, v in enumerate(seq) if v), None)
    if first is None: return "no two-knot part"
    if name == "retiring": bad = [t for t in range(first, len(seq) - 2) if seq[t + 2] != 2 * seq[t]]
    if name == "offshoots": bad = [t for t in range(first + 1, len(seq) - 2) if seq[t + 2] != 2 * seq[t] + seq[t - 1]]
    if name == "waiting": bad = [t for t in range(first + 2, len(seq) - 2) if seq[t + 2] != 2 * seq[t] + seq[t - 2]]
    return "recurrence holds" if not bad else f"recurrence FAILS at t = {bad[:4]}"

for sname, stars in STARTS.items():
    for tname, shortage in TREAT.items():
        st = R.from_stars(stars); law = R.Law("FLOOR0", shortage, True); seq = [two_knot_parts(st)]; knots = len(stars)
        for r in range(1, 25):
            t = R.step(st, law)
            if t.status != "extend": seq.append(t.status); break
            knots += len(t.births); st = t.state
            if knots > 20000: break
            seq.append(two_knot_parts(st))
        nums = [v for v in seq if isinstance(v, int)]
        print(f"{sname:16s} {tname:9s} N(0..{len(nums) - 1}) = {nums}  | {recurrence(nums, tname)}")
