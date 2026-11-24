"""Two of ticket A's new findings checked with the pilot's programs (private workspace files), after the runs:
(1) a cap of four or five in the thread's own program: does a ring of five holding the cap each come back every two rounds?
(2) FLOOR0 with each cancelling treatment in the helper's pilot program: how many two-member parts are there each round?
Run from the repository root with .venv/bin/python -B."""
import collections, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
PILOT = ROOT / "docs/prompts/2026-11-23_balance_pilot"
src = (PILOT / "own_check.py").read_text().split("\nfor law in (")[0].replace('cap = 3 if law != "ORD" else None', 'cap = CAP if law != "ORD" else None')
for cap in (4, 5):
    own = {"CAP": cap}; exec(compile(src, "own_cap", "exec"), own)
    w = own["World"](); live = [w.knot(3) for _ in range(5)]
    for i in range(5): w.join(live[i], live[(i + 1) % 5])
    seen = []
    for r in range(1, 2 * cap + 4):
        live = own["step"](w, live, "CAP")
        if any(p[0] == 5 and p[1] == (cap,) * 5 for p in own["parts"](w, live)): seen.append(r)
        if w.next > 15000: break
    print(f"cap {cap}: a part of five members holding {cap} each is present after rounds {seen}")
sys.path.insert(0, str(PILOT / "balance")); import roster as R
stars = [[(i - 1) % 5, i, 5 + 3 * i, 6 + 3 * i, 7 + 3 * i] for i in range(5)]
for shortage in ("CANCEL-WAIT", "CANCEL-BUD", "CANCEL-END"):
    st = R.from_stars(stars); law = R.Law("FLOOR0", shortage, True); out = []
    for r in range(1, 11):
        t = R.step(st, law)
        if t.status != "extend": out.append(t.status); break
        st = t.state
        out.append(collections.Counter(len(p) for p in R.parts(st)).get(2, 0))
    print(f"FLOOR0 with {shortage} (the pilot's names): two-member parts after rounds 1 to 10: {out}")
