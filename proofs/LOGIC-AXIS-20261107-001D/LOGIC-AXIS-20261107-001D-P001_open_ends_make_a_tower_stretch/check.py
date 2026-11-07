#!/usr/bin/env python3
"""Finite checks for LOGIC-AXIS-20261107-001D-P001 (open ends make a tower stretch).

Each check states its range and has a control that must be rejected.

    python3 -B check.py          verify against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from knotgraph_lib import (GADGETS, KnotGraph, implied, is_knot, random_cubic_gadget,  # noqa: E402
                           random_cubic_tree, smallest_knot)

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


def random_gadgets(count: int):
    out = []
    while len(out) < count:
        n = RNG.randint(3, 9)
        k = RNG.randint(0, 3)
        if (3 * n - 3 - k) % 2:
            continue
        g = random_cubic_gadget(RNG, n, k)
        if g is not None:
            out.append(g)
    return out


def check_criterion() -> dict:
    """(1) One substitution of the seed keeps {a,b,c} as an implied check iff the gadget has no open end."""
    gadgets = list(GADGETS.items()) + [(f"random {i}", g) for i, g in enumerate(random_gadgets(300))]
    by_k: dict[int, dict[str, int]] = {}
    violations = []
    for name, g in gadgets:
        t = KnotGraph.seed().substitute(g)
        col = t.columns()
        kept = implied(col, t.legs)
        k = len(g["open_ends"])
        row = by_k.setdefault(k, {"kept": 0, "dissolved": 0})
        row["kept" if kept else "dissolved"] += 1
        if kept != (k == 0):
            violations.append(name)
    # control: the weaker rule "kept iff at most one open end" is refuted by the same data
    control = by_k.get(1, {}).get("dissolved", 0) > 0
    return {"pass": not violations and control and by_k.get(0, {}).get("kept", 0) > 20,
            "info": {"gadgets": len(gadgets), "by number of open ends": by_k, "violations": violations,
                     "control: 'kept iff at most one open end' is refuted": control}}


def check_conservative() -> dict:
    """(1) Without open ends every substitution step is a conservative extension: implied checks among the
    old distinctions are unchanged, and every old knot stays a knot. With open ends the legs' check is lost."""
    zero = [g for g in random_gadgets(200) if not g["open_ends"]][:25] + [GADGETS["G0 corner triangle"]]
    bad, tested = 0, 0
    for g in zero:
        l1 = KnotGraph.seed().substitute(g)
        l2 = l1.substitute(g)
        c1, c2 = l1.columns(), l2.columns()
        old = sorted(l1.ends)
        for _ in range(60):
            s = RNG.sample(old, RNG.randint(2, min(6, len(old))))
            tested += 1
            if implied(c1, s) != implied(c2, s):
                bad += 1
        for v, inc in l1.inc.items():
            if not is_knot(c2, inc):
                bad += 1
    star = KnotGraph.seed().substitute(GADGETS["G1 star"])
    control = not implied(star.columns(), star.legs)
    return {"pass": bad == 0 and tested > 1000 and control,
            "info": {"gadgets without open ends": len(zero), "random old subsets compared across a step": tested,
                     "differences": bad, "control: with open ends (G1) the legs' check is lost": control}}


def check_collapse() -> dict:
    """(1) G0 tower: the original corners keep bond distance 2 and leg a gains bond-2 neighbours per level."""
    t = KnotGraph.seed()
    rows = []
    for level in range(5):
        col = t.columns()
        a, b, c = t.legs
        keep = is_knot(col, (a, b, c))
        lookup: dict[int, list] = {}
        for e, v in col.items():
            lookup.setdefault(v, []).append(e)
        neighbours = set()
        for x in col:
            if x == a:
                continue
            for y in lookup.get(col[a] ^ col[x], []):
                if y not in (a, x) and is_knot(col, (a, x, y)):
                    neighbours.update((x, y))
        rows.append({"level": level, "legs a,b,c still a knot": keep, "bond-2 neighbours of a": len(neighbours)})
        t = t.substitute(GADGETS["G0 corner triangle"])
    growing = all(r["bond-2 neighbours of a"] >= 2 * (r["level"] + 1) for r in rows)
    ok = all(r["legs a,b,c still a knot"] for r in rows) and growing
    t1 = KnotGraph.seed().substitute(GADGETS["G1 star"]).substitute(GADGETS["G1 star"])
    control = not is_knot(t1.columns(), t1.legs)
    return {"pass": ok and control,
            "info": {"G0 levels": rows, "neighbours grow by at least 2 per level": growing,
                     "control: in the G1 tower the legs are not a knot": control}}


def check_trees() -> dict:
    """(2) In a hub-free law whose knot graph is a tree, the bond distance between two open ends is the
    number of knots on the path between them plus one (exhaustive search on random trees)."""
    tested, bad = 0, []
    for _ in range(150):
        t = random_cubic_tree(RNG, RNG.randint(2, 8))
        col = t.columns()
        outside = t.outside_edges()
        e, f = RNG.sample(outside, 2)
        path = t.tree_path(t.knot_of(e), t.knot_of(f))
        found = smallest_knot(col, e, f, len(path) + 3)
        tested += 1
        cut = t.cut(path)
        if found is None or found - 1 != len(path) + 1 or not (is_knot(col, cut) and e in cut and f in cut):
            bad.append((len(path), found))
    # the star tower: exhaustive at levels 0-2, path cuts at levels 3-5
    tower = []
    t = KnotGraph.seed()
    for level in range(6):
        a, b, _ = t.legs
        path = t.tree_path(t.knot_of(a), t.knot_of(b))
        entry = {"level": level, "knots on the a-b path": len(path), "3^k": 3 ** level}
        col = t.columns()
        cut = t.cut(path)
        entry["path cut is a knot of 3^k + 2 distinctions"] = is_knot(col, cut) and len(cut) == 3 ** level + 2
        if level <= 2:
            entry["exhaustive bond distance"] = smallest_knot(col, a, b, 3 ** level + 3) - 1
        tower.append(entry)
        t = t.substitute(GADGETS["G1 star"])
    tower_ok = all(r["knots on the a-b path"] == r["3^k"] and r["path cut is a knot of 3^k + 2 distinctions"]
                   for r in tower) and all(r.get("exhaustive bond distance", 3 ** r["level"] + 1) == 3 ** r["level"] + 1
                                           for r in tower)
    # control: on the prism (not a tree) the path formula fails at level 1
    p = KnotGraph.seed().substitute(GADGETS["G4 prism"])
    a, b, _ = p.legs
    path = p.tree_path(p.knot_of(a), p.knot_of(b))
    true = smallest_knot(p.columns(), a, b, 8) - 1
    control = true != len(path) + 1
    return {"pass": not bad and tested >= 150 and tower_ok and control,
            "info": {"random cubic trees tested": tested, "mismatches": bad, "star tower": tower,
                     "control: prism level 1, shortest path gives %d but the bond distance is %d" % (len(path) + 1, true): control}}


def run() -> dict:
    checks = {
        "0 dependency artifacts bound by hash; upstream proofs Proved": check_dependencies(),
        "1 criterion: one substitution keeps the old knot iff no open end (4 named + 300 random gadgets; control: weaker rule)": check_criterion(),
        "2 conservative steps without open ends: implied checks among old distinctions unchanged (control: G1 loses the legs' check)": check_conservative(),
        "3 collapse of the G0 tower: corners stay a knot, bond-2 neighbours grow (control: G1 tower)": check_collapse(),
        "4 trees: bond distance = path knots + 1 (150 random trees; star tower 3^k + 1; control: prism)": check_trees(),
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
