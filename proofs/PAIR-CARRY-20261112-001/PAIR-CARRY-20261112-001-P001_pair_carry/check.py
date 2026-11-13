"""Compare the constructed projected bonds with the original archived rule."""
import argparse
import gzip
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SAMPLE = (ROOT / "artifacts/LIMIT-ONLY-20261112-001A"
          / "LIMIT-ONLY-20261112-001A-E001_limit_only/sample_0.jsonl.gz")
PORTS = list(product((0, 1), repeat=3))


def source_record():
    with gzip.open(SAMPLE, "rt") as stream:
        return next(json.loads(raw) for n, raw in enumerate(stream, 1) if n == 4710)


def source_steps(record):
    (definition,) = record["defs"]
    ports, own, calls = definition
    assert (ports, own) == (3, 2)
    knots = [args for kind, args in calls if kind == "K"]
    children = [args for kind, args in calls if kind == "SELF"]
    assert children == [[3, 0, 4], [2, 1, 4], [4, 2, 1]]
    raw = []
    for word in product((0, 1), repeat=ports + own):
        a, b, c, x, y = word
        allowed = all(len({word[i] for i in knot}) == 2 for knot in knots)
        assert allowed == (b == int(x + y + c < 2))
        if allowed:
            raw.append((word, tuple(word[i] for i in children[0])))
    # Every triple has a productive infinite completion using this choice at all copies.
    assert all(any(w[:3] == p and w[3:] == (1-p[1], 1-p[1]) for w, _ in raw) for p in PORTS)
    return raw


def projection(raw, s, fixed_root):
    """Quantify all unobserved bits using the full three-port relation at each copy."""
    p = s % 2
    # Positions within a local five-bit word: input (a,b,c), own (x,y).
    if fixed_root and p:
        root_slot = 1
        marks = {i: (4,) for i in range(0, s-1, 2)}
        # Use the last even x as a helper. At the odd target its b-port is x[s-2].
        marks[s-1] = (3,)
        marks[s] = (1, 4)
    else:
        root_slot = 1 - p
        marks = {i: (4,) for i in range(p, s, 2)}
        marks[s] = (4, 3)
    states = {(port, (port[root_slot],)) for port in PORTS}
    for depth in range(s+1):
        states = {(next_port, observed + tuple(w[j] for j in marks.get(depth, ())))
                  for port, observed in states for w, next_port in raw if w[:3] == port}
    return {observed for _, observed in states}


def expected_missing(n):
    result = set()
    for top in (0, 1):
        helpers = tuple(top ^ (j % 2) for j in range(n-2))
        result.add((top, *helpers, helpers[-1]))
    return result


def knotlab(rows, n):
    names = [f"v{i}" for i in range(n)]
    missing = sorted(set(product((0, 1), repeat=n)) - rows)
    clauses = [" ".join(("~" if bit else "") + name for name, bit in zip(names, word))
               for word in missing]
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
           "--loops", *names[:-1], "--contact", names[-1], "--json"]
    raw = subprocess.check_output(cmd, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT/"tools")))
    return json.loads(raw)["is_knot"]


def unrestricted_small_bonds(record):
    """Run the accepted fixed-budget test with observations anywhere in the full tree."""
    solver_path = (ROOT / "proofs/BRANCH-DEPTH-20261112-001D"
                   / "BRANCH-DEPTH-20261112-001D-P001_fixed_budget/check.py")
    spec = spec_from_file_location("accepted_fixed_budget", solver_path)
    solver = module_from_spec(spec)
    sys.modules[spec.name] = solver
    spec.loader.exec_module(solver)
    checks = []
    for budget, last in [(3, 1), (4, 4)]:
        result = solver.decide_dlang(record["defs"], budget=budget, max_profiles=50000)
        solver.Profiles.compose.cache_clear()
        orbit = result["orbit"]
        assert orbit["preperiod"] > last
        assert orbit["answers"] == [n <= last for n in range(len(orbit["answers"]))]
        checks.append({"budget": budget, "unrestricted_profiles": result["unrestricted_profiles"],
                       "preperiod": orbit["preperiod"], "period": orbit["period"],
                       "last_reachable_depth": last, "answers": orbit["answers"]})
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    record = source_record()
    raw = source_steps(record)
    # Confirm the smallest positive forgetting length at all three physical ports.
    relation = {(w[:3], following) for w, following in raw}
    power = {(p, p) for p in PORTS}
    sizes = []
    for _ in range(7):
        sizes.append(len(power))
        power = {(p, r) for p, q in power for u, r in relation if q == u}
    assert sizes == [8, 16, 28, 44, 54, 62, 64]
    checked_arities = set()
    counts = []
    for s in range(0, 15):
        n = s//2 + 3
        depth_row = {"depth": s}
        for fixed_root, name in [(False, "alternating_root"), (True, "fixed_b")]:
            width = n + int(fixed_root and s % 2)
            observed = projection(raw, s, fixed_root)
            assert set(product((0, 1), repeat=width)) - observed == expected_missing(width)
            for erase in range(width):
                assert len({row[:erase] + row[erase+1:] for row in observed}) == 2**(width-1)
            if width not in checked_arities:
                assert knotlab(observed, width)
                checked_arities.add(width)
            depth_row[name] = {"size": width, "allowed": len(observed)}
        counts.append(depth_row)
    # Add a binary constraint independent of the third distinction. Erasing that
    # third distinction still leaves a constraint on the other two.
    restricted = {w for w in PORTS if w[0] != w[1]}
    assert not knotlab(restricted, 3)
    result = {"ticket": "PAIR-CARRY-20261112-001", "proof": "PAIR-CARRY-20261112-001-P001",
              "sample": {"file": SAMPLE.name, "line": 4710}, "local_words": len(raw),
              "port_relation_sizes_including_identity": sizes, "depth_checks": counts,
              "knotlab_positive_arities": sorted(checked_arities), "negative_control_rejected": True,
              "unrestricted_fixed_budgets": unrestricted_small_bonds(record)}
    serialized = json.dumps(result, indent=2) + "\n"
    path = HERE / "result.json"
    if args.write:
        path.write_text(serialized)
    elif path.read_text() != serialized:
        raise SystemExit("stored result differs")
    print(f"Exact raw projections and all deletions at depths 0–14; knotlab arities {sorted(checked_arities)}.")


if __name__ == "__main__":
    main()
