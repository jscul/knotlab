#!/usr/bin/env python3
"""Finite checks for OPEN-END-GROWTH-20261107-001B-P001 (bond distance is a boundary).

Each check states its range and has a control that must be rejected.

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

from knotgraph_lib import INF, KnotGraph, implied, is_knot, rank, smallest_knot  # noqa: E402

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


# --- building knot graphs ------------------------------------------------------------------------------
class Builder:
    def __init__(self):
        self.ends, self.inc, self.next = {}, {}, 0

    def knot(self, name):
        self.inc.setdefault(name, [])

    def edge(self, a, b):
        e = self.next
        self.next += 1
        self.ends[e] = [a, b]
        for x in (a, b):
            if x != INF:
                self.inc.setdefault(x, []).append(e)
        return e

    def graph(self, legs=None):
        assert all(len(v) == 3 for v in self.inc.values()), {k: len(v) for k, v in self.inc.items() if len(v) != 3}
        outside = [e for e, en in self.ends.items() if INF in en]
        return KnotGraph(self.ends, self.inc, tuple(legs or outside[:3]))


def random_growth(n: int, rng: random.Random, p_close: float) -> KnotGraph:
    """From one knot with three open ends: sprout at a random open end, or close two open ends of distinct
    knots, until n knots."""
    b = Builder()
    b.knot(0)
    opens = [b.edge(0, INF) for _ in range(3)]
    k = 1
    while k < n:
        holders = {}
        for e in opens:
            holders.setdefault(b.ends[e][0], []).append(e)
        pairs = [(e, f) for e, f in itertools.combinations(opens, 2) if b.ends[e][0] != b.ends[f][0]]
        if pairs and rng.random() < p_close:
            e, f = rng.choice(pairs)
            w = k
            k += 1
            b.knot(w)
            for x in (e, f):
                b.ends[x][1] = w
                b.inc[w].append(x)
                opens.remove(x)
            opens.append(b.edge(w, INF))
        else:
            e = rng.choice(opens)
            w = k
            k += 1
            b.knot(w)
            b.ends[e][1] = w
            b.inc[w].append(e)
            opens.remove(e)
            opens += [b.edge(w, INF), b.edge(w, INF)]
    return b.graph()


def connected(nodes, ends, allowed_edges=None):
    nodes = set(nodes)
    if not nodes:
        return True
    adj = {x: set() for x in nodes}
    for e, (a, b) in ends.items():
        if a in nodes and b in nodes and a != b:
            adj[a].add(b)
            adj[b].add(a)
    start = next(iter(nodes))
    seen, stack = {start}, [start]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return seen == nodes


def boundary_distance(t: KnotGraph, e, f, outside_connected=True):
    """Least |cut(U)| - 1 over sets U of knots, U connected and (optionally) the rest with INF connected,
    with e and f on the cut and the cut of size >= 3; None if there is none (exhaustive over subsets)."""
    knots = list(t.inc)
    best = None
    for r in range(1, len(knots) + 1):
        for U in itertools.combinations(knots, r):
            cut = t.cut(U)
            if e not in cut or f not in cut or len(cut) < 3:
                continue
            if not connected(U, t.ends):
                continue
            if outside_connected and not connected(set(knots) - set(U) | {INF}, t.ends):
                continue
            if best is None or len(cut) - 1 < best:
                best = len(cut) - 1
    return best


# --- 1. bond distance is a two-sided boundary ------------------------------------------------------------
def check_boundary() -> dict:
    tested, mismatches, control_hits = 0, [], 0
    for trial in range(60):
        t = random_growth(RNG.randint(4, 9), RNG, RNG.choice([0.3, 0.5, 0.7]))
        col = t.columns()
        edges = sorted(t.ends)
        for _ in range(4):
            e, f = RNG.sample(edges, 2)
            s = smallest_knot(col, e, f, len(edges))
            brute = None if s is None else s - 1
            formula = boundary_distance(t, e, f)
            tested += 1
            if brute != formula:
                mismatches.append((trial, e, f, brute, formula))
            if boundary_distance(t, e, f, outside_connected=False) != brute:
                control_hits += 1
    return {"pass": not mismatches and tested >= 200 and control_hits > 0,
            "info": {"random pairs in random grown knot graphs (4-9 knots)": tested, "mismatches": mismatches[:5],
                     "control: dropping the outside-connectivity condition changes the value": control_hits}}


# --- 2. one seam pins -----------------------------------------------------------------------------------
def sealed_cluster(k: int, rng: random.Random):
    """A random connected cubic cluster on k knots (k odd) with one free stub, no self-loops or parallels."""
    for _ in range(500):
        stubs = [v for v in range(k) for _ in range(3)]
        rng.shuffle(stubs)
        seam_end = stubs.pop()
        pairs = [(stubs[i], stubs[i + 1]) for i in range(0, len(stubs), 2)]
        if any(a == b for a, b in pairs) or len({frozenset(p) for p in pairs}) != len(pairs):
            continue
        adj = {v: set() for v in range(k)}
        for a, b in pairs:
            adj[a].add(b)
            adj[b].add(a)
        seen, stack = {0}, [0]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if len(seen) == k:
            return pairs, seam_end
    return None


def check_one_seam() -> dict:
    tested, bad = 0, []
    for trial in range(40):
        k = RNG.choice([3, 5, 7])
        built = sealed_cluster(k, RNG)
        if built is None:
            continue
        pairs, seam_end = built
        b = Builder()
        inside = [b.edge(f"u{a}", f"u{c}") for a, c in pairs]
        seam = b.edge(f"u{seam_end}", "o0")
        # outside: a short chain o0 - o1 - o2 with open ends
        b.edge("o0", "o1")
        b.edge("o0", INF)
        b.edge("o1", "o2")
        b.edge("o1", INF)
        b.edge("o2", INF)
        b.edge("o2", INF)
        t = b.graph()
        col = t.columns()
        outside = [e for e, (x, y) in t.ends.items() if not str(x).startswith("u") and not str(y).startswith("u")]
        pinned = implied(col, [seam])
        # X_(inside u outside) = X_inside x X_outside  <=>  ranks add; then no knot meets both sides
        product = rank(col[e] for e in inside + outside) == rank(col[e] for e in inside) + rank(col[e] for e in outside)
        # and, as an illustration, no knot of up to 6 places through a few crossing pairs
        sample = [(g, h) for g in inside[:2] for h in outside[:2]]
        small = [(g, h) for g, h in sample if smallest_knot(col, g, h, 6) is not None]
        tested += 1
        if not pinned or not product or small:
            bad.append((trial, pinned, product, small[:3]))
    # control: two seams tie but do not decouple
    b = Builder()
    for a, c in [("u0", "u1"), ("u0", "u2"), ("u1", "u2"), ("u1", "u3"), ("u2", "u3")]:
        b.edge(a, c)
    s0 = b.edge("u0", "o0")
    s1 = b.edge("u3", "o1")
    b.edge("o0", "o1")
    b.edge("o0", INF)
    b.edge("o1", INF)
    t = b.graph()
    col = t.columns()
    tied = implied(col, [s0, s1])
    cross = smallest_knot(col, 0, 7, len(t.ends)) is not None
    return {"pass": not bad and tested >= 30 and tied and cross,
            "info": {"random sealed clusters with one seam": tested, "failures": bad[:3],
                     "control: with two seams the seams are tied, yet a knot crosses": tied and cross}}


# --- 3. a short boundary is a shortcut ------------------------------------------------------------------
def strip(L: int) -> tuple[KnotGraph, list, list]:
    """Beads 0..L of two knots p_i, q_i; between beads the three seams p_i-p_(i+1), q_i-p_(i+1), q_i-q_(i+1);
    open ends only at the two ends. Returns the graph and the seam lists between consecutive beads."""
    b = Builder()
    for _ in range(2):
        b.edge("p0", INF)
    b.edge("q0", INF)
    seams = []
    for i in range(L):
        seams.append([b.edge(f"p{i}", f"p{i + 1}"), b.edge(f"q{i}", f"p{i + 1}"), b.edge(f"q{i}", f"q{i + 1}")])
    b.edge(f"p{L}", INF)
    for _ in range(2):
        b.edge(f"q{L}", INF)
    return b.graph(), seams


def check_short_boundary() -> dict:
    # (a) random connected regions with connected outside: their boundary is a knot
    tested, bad = 0, 0
    for _ in range(120):
        t = random_growth(RNG.randint(5, 12), RNG, 0.5)
        knots = list(t.inc)
        U = RNG.sample(knots, RNG.randint(1, len(knots) - 1))
        cut = t.cut(U)
        if len(cut) < 3 or not connected(U, t.ends) or not connected(set(knots) - set(U) | {INF}, t.ends):
            continue
        tested += 1
        if not is_knot(t.columns(), cut):
            bad += 1
    # (b) the three-seam strip: any two cross-sections are bonded at distance <= 5, at every length
    rows = []
    t, seams = strip(30)
    col = t.columns()
    for i, j in [(1, 3), (0, 5), (0, 12), (3, 20), (0, 29)]:  # regions of at least two beads are connected
        region = [f"{x}{k}" for k in range(i + 1, j + 1) for x in "pq"]
        cut = t.cut(region)
        exact = smallest_knot(col, seams[i][0], seams[j][2], 7)
        rows.append({"cross-sections": (i, j), "region boundary is a knot of 6": is_knot(col, cut) and len(cut) == 6,
                     "bond distance between them (exhaustive, <= 6 places)": None if exact is None else exact - 1})
    strip_ok = all(r["region boundary is a knot of 6"] and r["bond distance between them (exhaustive, <= 6 places)"] is not None
                   and r["bond distance between them (exhaustive, <= 6 places)"] <= 5 for r in rows)
    # control: the thread of the same length keeps open ends inside, and its bond distance grows
    b = Builder()
    b.edge("t0", INF)
    b.edge("t0", INF)
    prev = "t0"
    links = []
    for i in range(1, 31):
        links.append(b.edge(prev, f"t{i}"))
        b.edge(f"t{i}", INF)
        prev = f"t{i}"
    b.edge(prev, INF)
    th = b.graph()
    tcol = th.columns()
    far = smallest_knot(tcol, links[0], links[8], 12)
    control = far is not None and far - 1 >= 8
    return {"pass": bad == 0 and tested >= 40 and strip_ok and control,
            "info": {"random regions with both sides connected": tested, "boundaries that are not knots": bad,
                     "three-seam strip of 31 beads (regions of >= 2 beads)": rows,
                     "control: on the thread, links 8 apart are at bond distance >= 8": control}}


# --- 4. the two-open-ends rule grows the two-way thread ---------------------------------------------------
def two_open_ends_rule(n: int, rng: random.Random) -> KnotGraph:
    b = Builder()
    b.knot(0)
    opens = {0: [b.edge(0, INF) for _ in range(3)]}
    k = 1
    while k < n:
        holders = [v for v, es in opens.items() if len(es) >= 2]
        v = rng.choice(holders)
        e = rng.choice(opens[v])
        opens[v].remove(e)
        w = k
        k += 1
        b.knot(w)
        b.ends[e][1] = w
        b.inc[w].append(e)
        opens[w] = [b.edge(w, INF), b.edge(w, INF)]
    return b.graph()


def check_thread_rule() -> dict:
    structure_bad, dist_bad, cut_bad = [], [], []
    for n in list(range(2, 13)) + [40, 120, 300]:
        for seed in range(3):
            t = two_open_ends_rule(n, random.Random(seed * 1000 + n))
            deg = {v: sum(1 for e in inc if INF not in t.ends[e]) for v, inc in t.inc.items()}
            opens = {v: sum(1 for e in inc if INF in t.ends[e]) for v, inc in t.inc.items()}
            ends_ = [v for v in t.inc if deg[v] <= 1]
            path = max(deg.values()) <= 2 and len(ends_) == 2 and all(
                opens[v] == (2 if v in ends_ else 1) for v in t.inc)
            if not path:
                structure_bad.append((n, seed))
                continue
            col = t.columns() if n <= 120 else None
            if n <= 10:
                outside = t.outside_edges()
                for e, f in itertools.combinations(outside, 2):
                    p = t.tree_path(t.knot_of(e), t.knot_of(f))
                    s = smallest_knot(col, e, f, len(p) + 3)
                    if s is None or s - 1 != len(p) + 1:
                        dist_bad.append((n, seed, e, f))
            elif col is not None:
                a, z = ends_
                p = t.tree_path(a, z)
                cut = t.cut(p)
                if not (is_knot(col, cut) and len(cut) == n + 2):
                    cut_bad.append((n, seed))
    # control: random sprouting does not grow a path
    t = random_growth(20, random.Random(3), 0.0)
    deg = {v: sum(1 for e in inc if INF not in t.ends[e]) for v, inc in t.inc.items()}
    control = max(deg.values()) == 3
    return {"pass": not structure_bad and not dist_bad and not cut_bad and control,
            "info": {"runs (n = 2..12, 40, 120, 300; three seeds)": 42, "not a two-way thread": structure_bad,
                     "bond distance != path knots + 1 (exhaustive, n <= 10)": dist_bad[:5],
                     "whole-path cut not a knot of n + 2 (n = 11..120)": cut_bad,
                     "control: random sprouting has a knot joined to three knots": control}}


def run() -> dict:
    checks = {
        "0 dependency artifacts bound by hash; upstream proofs Proved": check_dependencies(),
        "1 bond distance = least two-sided boundary (exhaustive on random grown graphs; control: one-sided)": check_boundary(),
        "2 one seam pins and decouples (random sealed clusters; control: two seams still cross)": check_one_seam(),
        "3 short boundaries are shortcuts (random regions; three-seam strip; control: the thread)": check_short_boundary(),
        "4 the two-open-ends rule grows the two-way thread (control: random sprouting)": check_thread_rule(),
    }
    failures = [name for name, value in checks.items() if not value["pass"]]
    return {"checks": checks, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
              "claim": manifest["claim"], **outcome}
    print(json.dumps(outcome, indent=1, default=str)[:6000])
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not outcome["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
