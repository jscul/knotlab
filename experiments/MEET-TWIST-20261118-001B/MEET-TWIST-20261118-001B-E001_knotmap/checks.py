"""Gate checks for MEET-TWIST-20261118-001B (run before the freeze; all must pass).

  ../../../.venv/bin/python -B checks.py
"""
import hashlib
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job
import melib as M

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" -- " + str(detail) if detail else ""), flush=True)
    if not ok:
        FAILS.append(name)


src = HERE.parents[2] / "experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/melib.py"
h = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
check("G1 melib.py is MEET-ORDERS's engine unchanged", h(HERE / "melib.py") == h(src))

# G2. The twist maps the line's states one to one onto the moved presentation's (which are again the line's states).
ok = True
for n0 in range(4, 9):
    T = M.bracketings(0, n0 - 1)[0]
    S = M.base(n0, T)
    T2, rho = job.moved(T, n0)
    img = job.state_image(S, n0, n0, rho, [])
    ok &= img == M.base(n0, T2) == S and len(set(img)) == len(S)
check("G2 the twist maps the line's states onto themselves one to one (n0 = 4..8)", ok)

# G3. Every moved bracketing is a bracketing (a presentation of the line).
ok = all(sorted(job.moved(T, n0)[0]) in [sorted(x) for x in M.bracketings(0, n0 - 1)]
         for n0 in range(4, 9) for T in M.bracketings(0, n0 - 1))
check("G3 moving the ends' pair gives a bracketing (n0 = 4..8)", ok)

# G4. Mutant: Lemma 2 without the role change (every knot kept as it is) must disagree somewhere.
orig = job.lemma2
job.lemma2 = lambda nk, Or, O, w=0: nk
bad = 0
for T in M.bracketings(0, 4):
    r = job.run("x", {"n0": 5, "depth": 2, "knots": T})
    bad += sum(L["option_states_bad"] for L in r["levels"])
job.lemma2 = orig
check("G4 the mutant without role changes fails on some state", bad > 0, f"{bad} states")

# G5. The real map passes on the line of five to depth 2.
ok = all(all(L["law_carried"] and L["option_states_bad"] == 0 for L in job.run("x", {"n0": 5, "depth": 2, "knots": T})["levels"])
         for T in M.bracketings(0, 4))
check("G5 the map passes on every bracketing of five to depth 2", ok)

print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
