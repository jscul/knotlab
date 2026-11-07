#!/usr/bin/env python3
"""Finite checks for OPEN-END-GROWTH-20261107-001C-P001 (the logical Cartesian plane).

    python3 -B check.py          verify against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from axis_lib import ParityLaw, all_knots_through, rank  # noqa: E402

RNG = random.Random(20261107)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_dependencies() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    mismatched, statuses = {}, {}
    for path, digest in manifest["parent_bindings"].items():
        if sha256(ROOT / path) != digest:
            mismatched[path] = "digest"
        statuses[path] = json.loads((ROOT / path).read_text()).get("status")
    ok = not mismatched and all(s in ("Proved", "passed") for s in statuses.values())
    return {"pass": ok, "info": {"mismatched": mismatched, "statuses": statuses}}


def thread(n: int) -> ParityLaw:
    """The parity thread on a segment: links x0..xn, loops L1..Ln, knots x(t-1)+L(t)+x(t)=0."""
    names = [f"x{t}" for t in range(n + 1)] + [f"L{t}" for t in range(1, n + 1)]
    return ParityLaw(names, [[f"x{t - 1}", f"L{t}", f"x{t}"] for t in range(1, n + 1)])


def random_law(n: int, m: int, rng: random.Random) -> ParityLaw:
    names = [f"v{i}" for i in range(n)]
    return ParityLaw(names, [rng.sample(names, 3) for _ in range(m)])


class Product:
    """The product law: arrays whose columns are allowed states of A and whose rows are allowed states of B.
    Its allowed states are spanned by u v^T, so the column of entry (p, q) is col_A(p) (x) col_B(q)."""

    def __init__(self, A: ParityLaw, B: ParityLaw):
        self.A, self.B = A, B
        kB = len(B.solutions)
        self.col = {}
        for p in A.vars:
            a = A.col[p]
            for q in B.vars:
                m, i = 0, 0
                while a >> i:
                    if a >> i & 1:
                        m |= B.col[q] << (i * kB)
                    i += 1
                self.col[(p, q)] = m

    def is_knot(self, s) -> bool:
        s = list(s)
        total = 0
        for v in s:
            total ^= self.col[v]
        return len(s) >= 3 and len(set(s)) == len(s) and total == 0 and rank(self.col[v] for v in s) == len(s) - 1

    def vanishes(self, s) -> bool:
        total = 0
        for v in s:
            total ^= self.col[v]
        return total == 0

    def smallest(self, u, v, max_size: int):
        others = [w for w in self.col if w not in (u, v)]
        target = self.col[u] ^ self.col[v]
        for extra in range(1, max_size - 1):
            half = extra // 2
            table: dict[int, list] = {}
            for combo in itertools.combinations(others, half):
                x = 0
                for w in combo:
                    x ^= self.col[w]
                table.setdefault(x, []).append(combo)
            for combo in itertools.combinations(others, extra - half):
                x = target
                for w in combo:
                    x ^= self.col[w]
                for partner in table.get(x, ()):
                    if set(partner) & set(combo):
                        continue
                    s = (u, v) + partner + combo
                    if self.is_knot(s):
                        return len(s) - 1
        return None


def l_shape(K1, K2, p, q2):
    return [(r, q2) for r in K1 if r != p] + [(p, c) for c in K2 if c != q2]


def check_l_shapes() -> dict:
    """(1) L-shaped sets are knots of size |K1| + |K2| - 2, for thread products and random parity laws."""
    tested, bad = 0, []
    laws = [(thread(a), thread(b)) for a, b in [(2, 3), (3, 3), (4, 2), (5, 4)]]
    laws += [(random_law(7, 4, RNG), random_law(7, 4, RNG)) for _ in range(6)]
    control_ok = True
    for A, B in laws:
        P = Product(A, B)
        knotsA = list({k for v in A.vars for k in all_knots_through(A, v, 6)})
        knotsB = list({k for v in B.vars for k in all_knots_through(B, v, 6)})
        if not knotsA or not knotsB:
            continue
        for _ in range(25):
            K1, K2 = sorted(RNG.choice(knotsA), key=str), sorted(RNG.choice(knotsB), key=str)
            p, p2 = RNG.sample(K1, 2)
            q, q2 = RNG.sample(K2, 2)
            L = l_shape(K1, K2, p, q2)
            tested += 1
            if not (P.is_knot(L) and len(L) == len(K1) + len(K2) - 2 and (p, q) in L and (p2, q2) in L):
                bad.append((K1, K2, p, q2))
            if P.vanishes(L + [(p, q2)]):
                control_ok = False
    return {"pass": not bad and tested >= 150 and control_ok,
            "info": {"L-shapes tested (4 thread products, 6 random law pairs)": tested, "failures": bad[:3],
                     "control: the full cross, corner included, is never a check": control_ok}}


def axis_distance(law: ParityLaw, a, b):
    if a == b:
        return 0
    s = law.smallest_knot(a, b, len(law.vars))
    return None if s is None else len(s) - 1


def check_equality() -> dict:
    """(3) Exact bond distance on thread products = delta1 + delta2 - 1 (both axes moved), or the moved axis's
    distance (one axis fixed); exhaustive search."""
    rows, bad = [], []
    for (a, b), sample in [((2, 3), None), ((3, 3), 260)]:
        A, B = thread(a), thread(b)
        P = Product(A, B)
        entries = list(P.col)
        pairs = list(itertools.combinations(entries, 2))
        if sample:
            pairs = RNG.sample(pairs, sample)
        for (p, q), (p2, q2) in pairs:
            d1, d2 = axis_distance(A, p, p2), axis_distance(B, q, q2)
            if d1 is None or d2 is None:
                continue
            predicted = d2 if d1 == 0 else d1 if d2 == 0 else d1 + d2 - 1
            got = P.smallest((p, q), (p2, q2), predicted + 2)
            rows.append((d1, d2, got))
            if got != predicted:
                bad.append(((p, q), (p2, q2), d1, d2, got))
    # control: the plain sum d1 + d2 is refuted by the same data
    control = any(g is not None and g != d1 + d2 for d1, d2, g in rows if d1 and d2)
    return {"pass": not bad and len(rows) > 600 and control,
            "info": {"pairs checked (all of thread(2) x thread(3), 260 of thread(3) x thread(3))": len(rows),
                     "mismatches": bad[:5], "control: d1 + d2 without the -1 is refuted": control}}


def check_splitting() -> dict:
    """(2) A thread product splits at range 1: far-apart sets of entries have independent projections."""
    A = B = thread(8)
    P = Product(A, B)

    def site(name):
        return int(name[1:])

    entries = list(P.col)
    tested = 0
    for _ in range(300):
        a = RNG.sample(entries, RNG.randint(1, 3))
        b = [e for e in RNG.sample(entries, 40)
             if all(max(abs(site(e[0]) - site(x[0])), abs(site(e[1]) - site(x[1]))) > 1 for x in a)][:RNG.randint(1, 3)]
        if not b:
            continue
        tested += 1
        ra = rank(P.col[e] for e in a)
        rb = rank(P.col[e] for e in b)
        if rank(P.col[e] for e in a + b) != ra + rb:
            return {"pass": False, "info": {"failure": (a, b)}}
    # control: entries one apart can be bonded (a three-place knot inside a row)
    control = not (rank(P.col[e] for e in [("x2", "x3"), ("x2", "L4")]) + rank([P.col[("x2", "x4")]])
                   == rank(P.col[e] for e in [("x2", "x3"), ("x2", "L4"), ("x2", "x4")]))
    return {"pass": tested >= 250 and control,
            "info": {"random pairs of sets more than 1 apart in thread(8) x thread(8)": tested,
                     "control: a row knot {x2x3, x2L4, x2x4} is not a product of its parts": control}}


def run() -> dict:
    checks = {
        "0 dependency artifacts bound by hash; upstream proofs Proved": check_dependencies(),
        "1 L-shaped sets are knots of size |K1| + |K2| - 2 (control: the full cross is not a check)": check_l_shapes(),
        "2 thread products split at range 1 (control: a row knot)": check_splitting(),
        "3 exact bond distance on thread products = delta1 + delta2 - 1 (control: the plain sum)": check_equality(),
    }
    failures = [name for name, value in checks.items() if not value["pass"]]
    return {"checks": checks, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
              "claim": manifest["claim"], **outcome}
    print(json.dumps(outcome, indent=1, default=str)[:5000])
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not outcome["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
