#!/usr/bin/env python3
"""Referee (odd_referee.py) for ODD-SEARCH-20261112-001A, fresh code: it imports nothing from odd_lib and reads only the result files.
R1: for every fully blocked word, its patterns recomputed directly (never constant on any translate), every residue confirmed blocked,
and its certificate (if any) checked compatible with a flippable residue. R2: 3,000 random words at each of p = 31 and 37 (any defect
number) analysed directly: each with a pattern must have its own certificate or be listed among the fully blocked words up to
rotation, reflection, complement and multipliers."""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def pats_of(c):
    p = len(c)
    out = set()
    for a in range(1, p):
        for b in range(a + 1, p):
            if all(len({c[r], c[(r + a) % p], c[(r + b) % p]}) > 1 for r in range(p)):
                out.add((a, b))
    return out


def blocked_at(c, P, r):
    p = len(c)
    for a, b in P:
        for T in ((r, r + a, r + b), (r - a, r, r - a + b), (r - b, r - b + a, r)):
            o = [t % p for t in T if t % p != r % p]
            if len(o) == 2 and c[o[0]] == c[o[1]] != c[r]:
                return True
    return False


def compatible(c, P):
    p = len(c)
    return all(len({c[r], c[(r + a) % p], c[(r + b) % p]}) > 1 for r in range(p) for a, b in P)


def classes(c):
    p = len(c)
    out = set()
    for u in range(1, p):
        w = [c[(u * x) % p] for x in range(p)]
        for v in (w, [1 - x for x in w], w[::-1]):
            out.add(min(tuple(v[r:] + v[:r]) for r in range(p)))
    return out


def main():
    rows = {}
    for name in ("p31", "p37", "targeted"):
        f = HERE / ("result_%s.json" % name)
        if f.exists():
            for r in json.loads(f.read_text())["checks"]["result"]["rows"]:
                rows.setdefault(r["p"], []).extend(r["fully blocked"])
    bad1, n1 = [], 0
    blocked_classes = {}
    for p, bl in rows.items():
        for b in bl:
            n1 += 1
            c = [int(x) for x in b["word"]]
            P = pats_of(c)
            if not P or any(not blocked_at(c, P, r) for r in range(p)):
                bad1.append(("not fully blocked", b["word"]))
            if b["certificate"]:
                w = [int(x) for x in b["certificate"]]
                if not (compatible(w, P) and not blocked_at(w, P, 0)):
                    bad1.append(("bad certificate", b["word"]))
            blocked_classes.setdefault(p, set()).update(classes(c))
    rng = random.Random(1112)
    bad2, n2, stats = [], 0, {}
    for p in (31, 37):
        st = {"no pattern": 0, "own certificate": 0, "fully blocked, listed": 0}
        for _ in range(3000):
            c = [rng.randint(0, 1) for _ in range(p)]
            if len(set(c)) == 1:
                continue
            P = pats_of(c)
            n2 += 1
            if not P:
                st["no pattern"] += 1
            elif any(not blocked_at(c, P, r) for r in range(p)):
                st["own certificate"] += 1
            elif min(tuple(c[r:] + c[:r]) for r in range(p)) in blocked_classes.get(p, set()):
                st["fully blocked, listed"] += 1
            else:
                bad2.append("".join(map(str, c)))
        stats[str(p)] = st
    out = {"R1 fully blocked words checked": n1, "R1 problems": bad1[:10], "R2 sample": stats, "R2 unlisted fully blocked": bad2[:10],
           "passed": not bad1 and not bad2}
    (HERE / "referee.json").write_text(json.dumps(out, indent=1) + "\n")
    print("referee passed" if out["passed"] else "referee FAILED")
    sys.exit(0 if out["passed"] else 1)


if __name__ == "__main__":
    main()
