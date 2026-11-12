"""ROW-NEST-R1: the referee's own rebuild of ROW-NEST-20261112-001's triangles, and two checks of the rule class.

  ref_row.py census WORKER WORKERS   all 1,024 rules, depths 1..40, compared with the census rows -> result_census_<w>.jsonl
  ref_row.py parity                  window rules with one hidden parity (4-place even parity, complement-closed, NAE-definable
                                     only with fresh distinctions) -> result_parity.json
  ref_row.py boundary                affine rules read against a reference distinction (missing positions = the reference)
                                     -> result_boundary.json
  ref_row.py kboundary W N           the 1,024 rules with ends read against the reference -> result_kboundary_<w>.jsonl
  ref_row.py summary                 -> result_summary.json
"""
import glob
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parents[2] / "artifacts" / "ROW-NEST-20261112-001A" / "ROW-NEST-20261112-001A-E001_row_rules"
WINDOW = ["o-1", "o0", "o+1", "n-1", "n0"]
OFF = {"o-1": ("o", -1), "o0": ("o", 0), "o+1": ("o", 1), "n-1": ("n", -1), "n0": ("n", 0)}
TRIPLES = list(itertools.combinations(range(5), 3))
TMAX = 40


def cell(r, p, t):
    """Variable of row r, position p (rows of length 3 + r), numbered row by row; None when off the row."""
    if not 0 <= p < 3 + r:
        return None
    return sum(3 + q for q in range(r)) + p + 1


def build(rule_triples, t, parity=None, boundary=False):
    """Clauses of the depth-t triangle: rule knots between rows (window positions missing at a row end drop the knot), the
    closing knots on the bottom row's consecutive triples, and optionally an even parity on window positions. With boundary,
    the parity reads a missing position, and the name "r", as one reference distinction (so the parity stays closed under
    complement); without it, a parity touching a missing position is dropped like a knot."""
    cl = []
    ref = sum(3 + q for q in range(t + 1)) + 1
    for r in range(1, t + 1):
        for i in range(3 + r):
            def at(name):
                if name == "r":
                    return ref
                side, off = OFF[name]
                v = cell(r - 1 if side == "o" else r, i + off, t)
                return ref if v is None and boundary else v
            for tr in rule_triples:
                vs = [at(WINDOW[j]) for j in tr]
                if None not in vs and len(set(vs)) == 3:     # with boundary, a knot reaching two missing positions is dropped
                    cl += [vs, [-v for v in vs]]
            if parity:
                vs = [at(n) for n in parity]
                if boundary:                              # a reference read twice cancels out of the parity
                    vs = [v for v, c in Counter(vs).items() if c % 2 == 1]
                if None not in vs:                        # even parity: forbid every odd assignment
                    for bits in itertools.product((0, 1), repeat=len(vs)):
                        if sum(bits) % 2 == 1:
                            cl.append([-v if b else v for v, b in zip(vs, bits)])
    for p in range(3 + t - 2):
        vs = [cell(t, p + q, t) for q in range(3)]
        cl += [vs, [-v for v in vs]]
    return cl


def read(rule_triples, parity=None, boundary=False):
    alive, top = [], []
    for t in range(1, TMAX + 1):
        with Solver(name="glucose4", bootstrap_with=build(rule_triples, t, parity, boundary)) as s:
            a = s.solve()
            alive.append(a)
            cls = [b for b in ("000", "001", "010", "011")
                   if a and s.solve(assumptions=[cell(0, j, t) if b[j] == "1" else -cell(0, j, t) for j in range(3)])]
            top.append("|".join(cls))
    return alive, top


def last_change(seq):
    return max([t + 1 for t in range(1, len(seq)) if seq[t] != seq[t - 1]] + [0])


def census(worker, workers):
    rec = {}
    for name in glob.glob(str(CENSUS / "runs_*.jsonl")):
        for x in open(name):
            r = json.loads(x)
            rec[r["mask"]] = r
    with open(HERE / f"result_census_{worker}.jsonl", "w") as f:
        for mask in range(1024):
            if mask % workers != worker:
                continue
            rule = [TRIPLES[j] for j in range(10) if mask >> j & 1]
            alive, top = read(rule)
            c = rec[mask]
            mono = all(not alive[t] or alive[t - 1] for t in range(1, TMAX))
            f.write(json.dumps(dict(mask=mask, knots=len(rule), match=(alive == c["alive"] and top == c["top"]),
                                    has_old_triple=(0, 1, 2) in rule, alive_monotone=mono,
                                    last_change_alive=last_change(alive), last_change_top=last_change(top))) + "\n")


def parity():
    out = []
    for four in itertools.combinations(WINDOW, 4):
        for extra in ([], [(0, 1, 3)], [(1, 2, 4)]):
            alive, top = read(extra, parity=list(four))
            out.append(dict(parity=four, knots=extra, alive="".join("1" if a else "0" for a in alive),
                            top_changes=[t + 1 for t in range(1, TMAX) if top[t] != top[t - 1]],
                            last_change_alive=last_change(alive), last_change_top=last_change(top)))
            print(json.dumps(out[-1]), flush=True)
    json.dump(out, open(HERE / "result_parity.json", "w"), indent=1)


def boundary():
    """Affine rules read against one reference distinction (missing positions are the reference): beyond the class, since
    window-1 knots have no reference, but NAE-definable with fresh distinctions per position (P3a, P3b of NEST-COUNT)."""
    out = []
    for name, par in (("rule 150", ["n0", "o-1", "o0", "o+1"]), ("rule 90", ["n0", "o-1", "o+1", "r"]),
                      ("rule 102", ["n0", "o0", "o+1", "r"]), ("rule 60", ["n0", "o-1", "o0", "r"])):
        alive, top = read([], parity=par, boundary=True)
        out.append(dict(rule=name, parity=par, alive="".join("1" if a else "0" for a in alive),
                        dead_depths=[t + 1 for t, a in enumerate(alive) if not a],
                        top=top, last_change_alive=last_change(alive), last_change_top=last_change(top)))
        print(json.dumps({k: v for k, v in out[-1].items() if k != "top"}), flush=True)
    json.dump(out, open(HERE / "result_boundary.json", "w"), indent=1)


def classify(seq, pmax=10, amax=20):
    """The census's classifier, rewritten: constant; smallest period p <= 10 from some depth <= 20; else unexplained."""
    if all(x == seq[0] for x in seq):
        return "constant"
    for p in range(1, pmax + 1):
        for a in range(amax):
            if all(seq[t] == seq[t + p] for t in range(a, len(seq) - p)):
                return "eventually constant" if p == 1 else f"period {p}"
    return "unexplained"


def kboundary(worker, workers):
    """The 1,024 NAE rules with the row ends read against a reference distinction instead of dropping the knot."""
    with open(HERE / f"result_kboundary_{worker}.jsonl", "w") as f:
        for mask in range(1024):
            if mask % workers != worker:
                continue
            rule = [TRIPLES[j] for j in range(10) if mask >> j & 1]
            alive, top = read(rule, boundary=True)
            f.write(json.dumps(dict(mask=mask, knots=len(rule), alive_class=classify(alive), top_class=classify(top),
                                    last_change_alive=last_change(alive), last_change_top=last_change(top),
                                    alive="".join("1" if a else "0" for a in alive))) + "\n")


def summarize():
    rows = [json.loads(x) for n in sorted(HERE.glob("result_census_*.jsonl")) for x in open(n)]
    S = dict(rules=len(rows), match=sum(r["match"] for r in rows))
    old = [r for r in rows if r["has_old_triple"]]
    S["with_the_old_row_triple"] = dict(n=len(old), alive_monotone=sum(r["alive_monotone"] for r in old))
    S["last_change_alive"] = dict(Counter(r["last_change_alive"] for r in rows))
    S["last_change_top"] = dict(Counter(r["last_change_top"] for r in rows))
    kb = [json.loads(x) for n in sorted(HERE.glob("result_kboundary_*.jsonl")) for x in open(n)]
    if kb:
        S["ends_read_against_a_reference"] = dict(rules=len(kb), alive_class=dict(Counter(r["alive_class"] for r in kb)),
                                                  top_class=dict(Counter(r["top_class"] for r in kb)),
                                                  last_change_alive=dict(Counter(r["last_change_alive"] for r in kb)),
                                                  last_change_top=dict(Counter(r["last_change_top"] for r in kb)))
    for r in json.load(open(HERE / "result_boundary.json")):
        S.setdefault("affine_rules_against_a_reference", {})[r["rule"]] = dict(alive=r["alive"], classified=classify(r["alive"]),
                                                                                top_classified=classify(r["top"]))
    json.dump(S, open(HERE / "result_summary.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    {"census": lambda: census(int(sys.argv[2]), int(sys.argv[3])), "parity": parity, "boundary": boundary,
     "kboundary": lambda: kboundary(int(sys.argv[2]), int(sys.argv[3])),
     "summary": summarize}[sys.argv[1]]()
