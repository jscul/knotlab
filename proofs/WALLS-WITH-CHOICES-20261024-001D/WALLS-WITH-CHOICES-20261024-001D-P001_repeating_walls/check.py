#!/usr/bin/env python3
"""Check of WALLS-WITH-CHOICES-20261024-001D-P001 (standard library only).

Uses the wall graph and the cover machinery of WALLS-WITH-CHOICES-20261024-001A-P001's check.

For placement 159 on the 3 x 4 torus in twist 11 and three configurations, each with one odd class:
- the own solver finds an assignment of a cyclic cover of the cylinder, verified clause by clause;
- the check traces the wall of that assignment that meets the cylinder's loop an odd number of times; its closed walk in the wall
  graph has valid moves, passes the criterion of the wall theorem, visits some wall state more than once, and the assignment
  rebuilt from it alone passes every triangle of a window;
- every simple cycle of the wall graph is enumerated (no cap), and none passes the criterion.
Control: for a configuration of placement 147 (walls without choices) every closed walk is a simple cycle, so the crossing wall of
a cover assignment visits no wall state twice.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

sys.setrecursionlimit(20000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "wall_check", ROOT / "proofs/WALLS-WITH-CHOICES-20261024-001A/WALLS-WITH-CHOICES-20261024-001A-P001_wall_theorem/check.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
DR = A.DR

WITNESSES = [  # (placement, L, M, twist, configuration, class), located by comparing walls.c with the producer's engine of A
    (159, 3, 4, (1, 1), 7860857, (2, 1)),
    (159, 3, 4, (1, 1), 7985754, (0, 1)),
    (159, 3, 4, (1, 1), 6433130, (1, 2)),
]


def witness(R, L, M, q, x, c):
    moves = DR.wall_moves(L, M)
    out = {"placement": R, "torus": f"{L}x{M}", "twist": f"{q[0]}{q[1]}", "configuration": x, "class": list(c)}
    out["odd"] = c in DR.odd_classes(DR.CLASSES + [c], DR.fitting(R, L, M), q)
    cov = A.cover_assignment(R, L, M, q, x, c, max_sheets=24)
    out["cover sheets"] = cov[0] if cov else None
    if cov is None:
        return out
    seq, hc, F = A.crossing_wall(R, L, M, q, x, c, *cov)
    ok, walk, e = A.closed_walk(seq, hc, R, L, M, q, x, F, moves)
    reps = [s for s, n in Counter(st for st, _pos in walk).items() if n > 1]
    tris = [t for t, n in Counter(st[0][:3] for st, _pos in walk).items() if n > 1]
    out.update({"closed walk length": len(walk), "class of the walk": list(e), "det(c, e)": DR.det(c, e), "moves valid": ok,
                "passes the criterion": A.good(c, e, A.overlaps(walk)), "wall states visited twice": len(reps),
                "torus triangles visited twice": len(tris),
                "rebuilt from the walk alone": A.rebuild_and_verify(R, L, M, q, x, c, walk, e)})
    G = A.wall_graph(R, L, M, q, x, moves)
    cyc, capped = A.simple_cycles(G, cap=10 ** 7)
    crossing = [abs(DR.det(c, ee)) for _p, ee in cyc if DR.det(c, ee) != 0]
    out.update({"simple cycles": len(cyc), "enumeration capped": capped, "simple cycles crossing the cylinder": len(crossing),
                "values of |det(c, e)| among them": sorted(set(crossing)),
                "simple cycles passing the criterion": sum(A.good(c, ee, A.overlaps(p)) for p, ee in cyc)})
    return out


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    ws = [witness(*w) for w in WITNESSES]
    ctrl = witness(147, 3, 3, (0, 1), 30817, (1, 1))
    controls = {"147: the crossing wall visits no wall state twice": ctrl.get("wall states visited twice") == 0
                and ctrl.get("passes the criterion") is True}
    ok = all(w["odd"] and w["cover sheets"] and w["moves valid"] and w["passes the criterion"] and w["wall states visited twice"] > 0
             and w["rebuilt from the walk alone"] and not w["enumeration capped"] and w["simple cycles passing the criterion"] == 0
             for w in ws) and all(controls.values())
    result["checks"] = {"witnesses": ws, "control configuration": ctrl}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
