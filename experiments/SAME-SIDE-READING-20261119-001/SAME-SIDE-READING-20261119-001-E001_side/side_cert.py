"""Targeted same-side common-bond certificates by residual cut feasibility."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import subprocess
import sys
from tempfile import TemporaryDirectory

import side_sources as sources

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.insert(0, str(sources.OLDER.parent))
from certify import Wired, direct_words


def orientations(graph, marks):
    for directions in product((0, 1), repeat=len(marks)):
        pins = {graph.outside: 0}
        for bit, color in zip(marks, directions, strict=True):
            a, b = graph.ends[bit]
            if pins.get(a, color) != color or pins.get(b, 1 - color) != 1 - color:
                break
            pins[a], pins[b] = color, 1 - color
        else:
            yield pins


def checked_shore(graph, marks, shore):
    if not graph.connected(shore) or not graph.connected(graph.all_knots - shore):
        return None
    row = graph.witness(sum(1 << v for v in shore))
    return row if set(marks) <= set(row["crossing_distinctions"]) else None


class Threshold:
    def __init__(self, graph, binary):
        self.graph = graph
        self.binary = binary

    def __enter__(self):
        self.pipe = subprocess.Popen([self.binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     text=True, bufsize=1)
        links = [(a, b, cost) for a, row in enumerate(self.graph.near)
                 for b, cost in sorted(row.items()) if a < b]
        header = (len(self.graph.all_knots), len(links), self.graph.outside, len(self.graph.ends))
        for row in (header, *links):
            self.pipe.stdin.write(" ".join(map(str, row)) + "\n")
        self.pipe.stdin.flush()
        return self

    def __exit__(self, *_exc):
        self.pipe.stdin.close()
        self.pipe.stdout.close()
        assert self.pipe.wait() == 0

    def check(self, marks, pins, threshold, work_limit):
        fields = (threshold, work_limit, len(pins),
                  *(entry for row in sorted(pins.items()) for entry in row))
        self.pipe.stdin.write(" ".join(map(str, fields)) + "\n")
        self.pipe.stdin.flush()
        status, *entries = self.pipe.stdout.readline().split()
        flow, nodes, work, cost, count, *shore = map(int, entries)
        assert status in {"witness", "excluded", "capped"} and count == len(shore)
        row = {"threshold_cost": threshold, "status": status, "unconstrained_lower_cost": flow,
               "search_nodes": nodes, "work": work}
        if status == "witness":
            actual = checked_shore(self.graph, marks, set(shore))
            assert actual and actual["cost"] == cost <= threshold
            assert all((v in shore) == c for v, c in pins.items())
            row["witness"] = actual
        return row


def read(engine, marks, older_witness, cost_cap, limit):
    """Return exact readings or certified bounds in bond-size units."""
    graph = engine.graph
    width = len(graph.ends)
    best = older_witness
    alternatives = []
    universe = tuple(orientations(graph, marks))
    for pins in universe:
        receipt = []
        lower = len(marks)
        while lower <= min(cost_cap, width, best["cost"] - 1 if best else width):
            threshold = min(cost_cap, width, best["cost"] - 1 if best else width)
            test = engine.check(marks, pins, threshold, limit)
            lower = max(lower, test["unconstrained_lower_cost"])
            receipt.append(test)
            if test["status"] == "witness":
                best = test["witness"]
            elif test["status"] == "capped":
                break
            else:
                lower = max(lower, threshold + 1)
                break
        alternatives.append({"pins": sorted(pins.items()), "lower_cost": lower if lower <= width else None,
                             "checks": receipt})

    lows = [row["lower_cost"] for row in alternatives if row["lower_cost"] is not None]
    lower = min(lows) if lows else None
    upper = best["cost"] if best else None
    assert upper is None or lower is not None and lower <= upper
    verdict = "infinite" if lower is None else "exact" if lower == upper else "bounded"
    return {"status": verdict, "lower_cost": lower, "upper_cost": upper,
            "witness": best, "orientations": alternatives}


def path_seed(graph, spec, frame, indices, marks):
    """Propose a literal upper witness from old path holders and first binary children."""
    positions = spec["roles"]["background"]
    bridges = {tuple(sorted(p)): child for child, p in frame["parent_sets"].items() if len(p) == 2}
    best = None
    for pins in orientations(graph, marks):
        inner = [i for i in range(indices[0], indices[-1] + 2) if pins.get(positions[i]) == 1]
        if not inner:
            continue
        old = {positions[i] for i in range(min(inner), max(inner) + 1) if pins.get(positions[i]) != 0}
        shore = set(old)
        for i in range(min(inner) + 1, max(inner)):
            if positions[i] in old:
                continue
            a, b = positions[i - 1], positions[i + 1]
            key = tuple(sorted((a, b)))
            if a not in old or b not in old or key not in bridges:
                break
            shore.add(bridges[key])
        else:
            candidate = checked_shore(graph, marks, shore)
            if candidate and (best is None or candidate["cost"] < best["cost"]):
                best = candidate
    return best


def controls(binary):
    cases = {
        "four_cycle": ((0, 3, 4), (0, 1, 5), (1, 2, 6), (2, 3, 7)),
        "two_lobes": ((0, 1, 2), (0, 3, 4), (5, 6, 7), (5, 8, 9)),
        "parallel": ((0, 1, 4), (0, 1, 2, 3), (2, 3, 5), (5, 6, 7)),
        "three_cycle": ((0, 2, 3), (0, 1, 4), (1, 2, 5)),
    }
    results = {}
    for name, stars in cases.items():
        graph = Wired(stars)
        words = direct_words(graph.stars)
        counts = Counter()
        with Threshold(graph, binary) as solver:
            for k in (2, 3, 4):
                for marks in combinations(sorted(graph.ends), k):
                    expected = min((len(word) for word in words if set(marks) <= word), default=None)
                    result = read(solver, marks, None, len(graph.ends), 1000000)
                    assert result["status"] == ("infinite" if expected is None else "exact")
                    assert result["upper_cost"] == expected
                    counts[k, result["status"]] += 1
            if name == "three_cycle":
                assert not tuple(orientations(graph, (0, 1, 2)))
        results[name] = [{"order": k, "status": status, "count": count}
                         for (k, status), count in sorted(counts.items())]
    return results


def recoded_control(binary):
    spec = sources.cases()["T4"]
    rng = Random(20261119031)
    result = {}
    for arm, state in sources.loads(spec).items():
        frame = dict(sources.generate(spec, state, 1, sources.CAPS))[1]
        original = Wired(frame["stars"])
        knots = list(range(original.outside))
        bits = sorted(original.ends)
        meanings = bits.copy()
        rng.shuffle(knots)
        rng.shuffle(meanings)
        bits = dict(zip(bits, meanings, strict=True))
        stars = [None] * len(knots)
        for old, knot in enumerate(knots):
            stars[knot] = tuple(bits[b] for b in original.stars[old])
        graph = Wired(stars)
        queries = ((4, 5, 6), (5, 6, 7))
        with Threshold(original, binary) as base, Threshold(graph, binary) as recoded:
            rows = []
            for positions in queries:
                marks = tuple(spec["roles"]["anchors"][i] for i in positions)
                old = read(base, marks, None, 18, 2000000)
                changed = tuple(bits[b] for b in marks)
                new = read(recoded, changed, None, 18, 2000000)
                assert old["status"] == new["status"] == "exact"
                assert old["upper_cost"] == new["upper_cost"]
                rows.append({"path_positions": positions, "recoded_marks": changed,
                             "cost": old["upper_cost"], "recoded_witness": new["witness"]})
        result[arm] = rows
    return {"random_seed": 20261119031, "cases": result}


def panel_sets(spec, panel):
    if panel == "remote":
        (s,) = spec["roles"]["seams"]
        return [(s + 4, s + 8)]
    if panel == "between":
        s, t = spec["roles"]["seams"]
        assert t - s == 4
        interior = range(s, t)
        return [m for k in (2, 3, 4) for m in combinations(interior, k)]
    registered = sources.marksets(spec)
    seams = spec["roles"]["seams"] or [4]
    offsets = {"near": {0, 1}, "translated": {0, 4, 8, 16}}[panel]
    return [m for m in registered if min(sources.offset(m, s) for s in seams) in offsets]


def evaluate(binary, spec, arm, occupied, queries, through, cost_cap, work):
    previous = {}
    rows = {}
    anchors = spec["roles"]["anchors"]
    stream = sources.generate(spec, occupied, through, sources.CAPS)
    while True:
        try:
            age, frame = next(stream)
        except StopIteration as stop:
            finish = stop.value or {}
            return {"frames": rows, "termination": {key: finish[key] for key in
                    ("status", "last_age", "planned_new_knots", "planned_total_knots",
                     "planned_total_distinctions", "planned_total_distinctions_lower") if key in finish}}
        graph = Wired(frame["stars"])
        scored = {}
        with Threshold(graph, binary) as solver:
            for indices in queries:
                marks = tuple(anchors[i] for i in indices)
                old = previous.get(indices)
                seed = None
                if old:
                    seed = checked_shore(graph, marks, set(old["shore"]))
                    assert seed == old
                if age <= 1:
                    newer = path_seed(graph, spec, frame, indices, marks)
                    if newer and (seed is None or newer["cost"] < seed["cost"]):
                        seed = newer
                budget = len(graph.ends) if age == 0 else max(cost_cap, seed["cost"] if seed else 0)
                result = read(solver, marks, seed, budget, work)
                if result["witness"]:
                    previous[indices] = result["witness"]
                scored[indices] = result
        counts = Counter(row["status"] for row in scored.values())
        rows[str(age)] = {
            "knots": graph.outside, "distinctions": len(graph.ends), "counts": dict(counts),
            "literal_stars_sha256": sha256(json.dumps(frame["stars"], separators=(",", ":")).encode()).hexdigest(),
            "queries": [{
                "path_positions": list(indices),
                "source_offsets": {
                    str(s): sources.offset(indices, s) for s in spec["roles"]["seams"]
                },
                **row,
            } for indices, row in scored.items()],
        }
        print(spec["id"], arm, age, dict(counts),
              [(indices, row["lower_cost"], row["upper_cost"])
               for indices, row in scored.items()] if len(queries) <= 4 else "", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", default=["J1"])
    parser.add_argument("--panel", choices=("remote", "near", "translated", "between"), default="remote")
    parser.add_argument("--through", type=int)
    parser.add_argument("--cost-cap", type=int, default=24)
    parser.add_argument("--work-limit", type=int, default=2000000)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="same-side-cert-") as scratch:
        binary = Path(scratch) / "side_cert"
        subprocess.run(["g++", "-std=c++20", "-O3", HERE / "side_cert.cpp", "-o", binary], check=True)
        result = {"unit": "bond size (subtract one for bond distance)", "panel": args.panel,
                  "work_units_per_threshold_orientation": args.work_limit, "cost_cap_without_witness": args.cost_cap,
                  "controls": controls(binary), "cases": {}}
        if args.panel == "between":
            result["renaming_control"] = recoded_control(binary)
        for name in args.cases:
            spec = sources.cases()[name]
            through = min(args.through if args.through is not None else sources.AGES[name], sources.AGES[name])
            queries = panel_sets(spec, args.panel)
            result["cases"][name] = {
                arm: evaluate(binary, spec, arm, state, queries, through, args.cost_cap, args.work_limit)
                for arm, state in sources.loads(spec).items()
            }
    output = args.out or ARTIFACTS / f"side_cert_{args.panel}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(output)


if __name__ == "__main__":
    main()
