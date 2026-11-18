"""Referee R1 for MEET-TWIST-20261118-001 (own code; the study's job.py, its Lemma 2 table and melib.py are not imported).

  ../../../.venv/bin/python -B referee_twist.py law <n0> <depth>      Theorem 2, one mark move, every bracketing -> referee_twist_law_<n0>_<depth>.json
  ../../../.venv/bin/python -B referee_twist.py beyond                  the first added state from the line of five, and the law there

The engine is the referee's MEET-ORDERS-R1 KF3 (`referee_meet.run`, labelled (S, G), exact fractions).  The test does not use
Lemma 2's table: it compares, after every new distinction, the exact joint law of (the odd sets of the new distinctions, in order,
and the co-knotted pairs) between a bracketing with the ends' pair {m, 0} and the same knots with the ends' pair moved to {0, 1}
(their line 1, 2, ..., m, 0, renamed to 0..m for the run and renamed back for the comparison).  Theorem 2 says the two laws are equal
until a state is added.  Also: whether a state was added anywhere, and whether the two laws of the number of orders differ.

`beyond` asks the coordinator's question: from the line of five, where does KF3 first add a state, and is the law of the pairs still
carried by the mark move after that?
"""
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402


def moved(T, n0):
    """The same knots with the ends' pair moved from {m, 0} to {0, 1}: line order 1, 2, ..., m, 0, renamed by v -> v - 1 mod n0."""
    rho = lambda v: (v - 1) % n0
    K = []
    for k in T:
        a, b, c = sorted(rho(v) for v in k)
        K.append((a, b, c))
    back = lambda x: (x + 1) % n0
    return tuple(K), back


def laws(n0, T, depth, back=None):
    lv = RM.run(n0, T, depth, keep_levels=True)
    f = (lambda v: back(v) if v < n0 else v) if back else (lambda v: v)
    out = []
    for L in lv:
        joint = defaultdict(Fraction)
        two = Fraction(0)
        added = Fraction(0)
        for (S, G), q in L["dist"].items():
            o = RM.odd_sets(S, L["n"], n0)
            if o is None:
                added += q
                key = ("a state was added", frozenset((min(f(a), f(b)), max(f(a), f(b))) for a, b in G))
            else:
                key = (tuple(tuple(sorted(f(v) for v in O)) for O in o),
                       frozenset((min(f(a), f(b)), max(f(a), f(b))) for a, b in G))
            joint[key] += q
            m = RM.RC.measure(S, L["n"])
            two += q if (m["k"] == 2 and m["lam"] == 2) else 0
        out.append({"n": L["n"], "joint": dict(joint), "two": two, "added": added, "labelled": L["labelled"]})
    return out


def part_law(n0, depth):
    Ts = RM.bracketings(0, n0 - 1)
    res = Counter()
    states_added = 0
    first_bad = []
    orders_differ = 0
    for T in Ts:
        A = laws(n0, T, depth)
        T2, back = moved(T, n0)
        assert RM.line_states(n0) == RM.RC.base(n0, list(T2)), "the moved knots do not present the line"
        B = laws(n0, T2, depth, back)
        for La, Lb in zip(A, B):
            same = La["joint"] == Lb["joint"]
            res["levels carried" if same else "levels NOT carried"] += 1
            res["labelled counts equal" if La["labelled"] == Lb["labelled"] else "labelled counts differ"] += 1
            states_added += (La["added"] > 0) + (Lb["added"] > 0)
            if not same and len(first_bad) < 5:
                first_bad.append({"knots": T, "n": La["n"]})
        orders_differ += any(La["two"] != Lb["two"] for La, Lb in zip(A, B))
    out = {"n0": n0, "depth": depth, "bracketings": len(Ts), "tally": dict(res), "levels_with_an_added_state": states_added,
           "bracketings_whose_two_order_chances_differ_under_the_move": orders_differ, "first_failures": first_bad}
    (HERE / f"referee_twist_law_{n0}_{depth}.json").write_text(json.dumps(out, indent=1, default=str))
    return out


def part_beyond(nmax=None):
    """From each bracketing of five: KF3 run until some branch adds a state (exact), then the law of the co-knotted pairs alone
    (in original labels) against the moved mark's, at that level and the next."""
    out = {}
    for T in RM.bracketings(0, 4):
        T = tuple(T)
        first = None
        for d in range(1, 9):
            lv = RM.run(5, T, d, keep_levels=True)
            L = lv[-1]
            if any(RM.odd_sets(S, L["n"], 5) is None for (S, G) in L["dist"]):
                first = L["n"]
                break
            if L["labelled"] > 60000:
                break
        out[str(T)] = {"first_level_with_an_added_state": first, "last_level_run": L["n"], "labelled_there": L["labelled"]}
        print("beyond", T, json.dumps(out[str(T)]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "law":
        print(json.dumps(part_law(int(sys.argv[2]), int(sys.argv[3])), indent=1, default=str))
    else:
        r = part_beyond()
        (HERE / "referee_twist_beyond.json").write_text(json.dumps(r, indent=1))
        print(json.dumps(r, indent=1))
