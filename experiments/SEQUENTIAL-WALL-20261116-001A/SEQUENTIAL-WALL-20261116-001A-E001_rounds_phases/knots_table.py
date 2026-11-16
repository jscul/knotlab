"""Where each three-place knot law sits, with the outside allowed to hold values.

Every relation on three distinctions that passes K1-K3 (constrained as a
whole, free after forgetting any one variable, some state allowed) is listed
with its excluded states and its closure under the four Schaefer operations
(and, or, majority, minority).  With held values (constants) available:
  - no Schaefer operation: NP-complete (Schaefer 1978);
  - closed under minority (parity): parity-L-complete (Allender, Bauland,
    Immerman, Schnoor and Vollmer 2009);
  - closed under and or or: P-complete when the atom, or its dual
    a or b or not c, is pp-definable from the knot and constants (found here by
    an explicit search with at most two copies and two hidden distinctions;
    the definition is recorded), since atom patterns are P-complete; a
    single-sign clause (excluding only 000 or only 111) is in AC0 (a pattern
    of such clauses with held values is unsatisfiable exactly when a clause
    has all three members held to the excluded value).
Each knot is also confirmed by tools/knotlab's checker.
"""

import itertools
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")
STATES = list(itertools.product((0, 1), repeat=3))


def is_knot(rel):
    if not rel or len(rel) == 8:
        return False
    for drop in range(3):
        keep = [i for i in range(3) if i != drop]
        if len({tuple(s[i] for i in keep) for s in rel}) != 4:
            return False
    return True


def closed(rel, op, arity):
    for ts in itertools.product(sorted(rel), repeat=arity):
        if tuple(op(*[t[i] for t in ts]) for i in range(3)) not in rel:
            return False
    return True


AND = lambda x, y: x & y
OR = lambda x, y: x | y
MAJ = lambda x, y, z: (x & y) | (y & z) | (x & z)
MIN = lambda x, y, z: x ^ y ^ z
ATOM = frozenset(s for s in STATES if not (s[0] and s[1] and not s[2]))
DUAL_ATOM = frozenset(s for s in STATES if not (not s[0] and not s[1] and s[2]))


def pp_search(rel, target, copies=2):
    """Find R(slots) [and R(slots)] over a, b, c, w1, w2, 0, 1 whose projection on
    (a, b, c) equals target.  Returns the slot assignment or None."""
    slots = ["a", "b", "c", "w1", "w2", "0", "1"]
    rel = set(rel)
    assigns = list(itertools.product((0, 1), repeat=5))
    for combo in itertools.product(range(len(slots)), repeat=3 * copies):
        groups = [combo[3 * k:3 * k + 3] for k in range(copies)]
        proj = set()
        for asg in assigns:
            val = dict(zip(slots[:5], asg))
            val["0"], val["1"] = 0, 1
            if all(tuple(val[slots[i]] for i in g) in rel for g in groups):
                proj.add(asg[:3])
        if proj == target:
            return [[slots[i] for i in g] for g in groups]
    return None


def cnf_of(rel):
    clauses = []
    for s in STATES:
        if s not in rel:
            lits = []
            for name, v in zip("ABc", s):
                lits.append(("~" if v else "") + name)
            clauses.append(" ".join(lits))
    return "; ".join(clauses)


def knotlab_ok(rel):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools"))
    res = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf_of(rel),
                          "--loops", "A", "B", "--contact", "c", "--json"],
                         capture_output=True, text=True, env=env, cwd=ROOT, check=True)
    return json.loads(res.stdout)["is_knot"]


def main():
    rows = []
    for mask in range(256):
        rel = frozenset(STATES[i] for i in range(8) if mask >> i & 1)
        if not is_knot(rel):
            continue
        assert knotlab_ok(rel), "knotlab disagrees"
        excl = sorted("".join(map(str, s)) for s in STATES if s not in rel)
        row = {"excluded": excl, "and": closed(rel, AND, 2), "or": closed(rel, OR, 2),
               "majority": closed(rel, MAJ, 3), "minority": closed(rel, MIN, 3)}
        if row["majority"]:
            row["class"] = "bijunctive (impossible for a knot)"
        elif row["minority"]:
            row["class"] = "parity-L-complete"
        elif row["and"] or row["or"]:
            target = ATOM if row["and"] else DUAL_ATOM
            found = pp_search(rel, target)
            if found:
                row["class"] = "P-complete"
                row["defines"] = ("atom" if row["and"] else "dual atom") + " by " + repr(found)
            elif excl in (["000"], ["111"]):
                row["class"] = "AC0 (single-sign clause)"
            else:
                row["class"] = "unresolved"
        else:
            row["class"] = "NP-complete"
        rows.append(row)
    summary = {}
    for r in rows:
        summary[r["class"]] = summary.get(r["class"], 0) + 1
    res = {"knots": len(rows), "classes": summary, "rows": rows}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "knots_table.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({"knots": len(rows), "classes": summary}, indent=1))


if __name__ == "__main__":
    main()
