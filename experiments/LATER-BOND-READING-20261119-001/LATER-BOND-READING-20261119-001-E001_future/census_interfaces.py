"""Run the exact split-core attachment comparisons and replay the branch capacities."""

from argparse import ArgumentParser
from collections import Counter, deque
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings"
PRIOR = ROOT / "experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds"
VERIFY = ROOT / "experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup(params):
    global engine
    engine = params["engine"]


def cases():
    for fixed in (3, 4):
        for ports in (3, 4):
            yield f"fixed{fixed}-ports{ports}", [fixed, ports]


def run(case_id, payload):
    result = subprocess.run([engine, "independent", *map(str, payload)], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def literal_start(core, kinds):
    rows = [[] for _ in range(core["ordinary_junctions"])]
    width = 0

    def add(*junctions):
        nonlocal width
        for j in junctions:
            rows[j].append(width)
        width += 1

    for edge in core["edges"]:
        add(*edge)
    for hub, kind in zip(core["ports"], kinds, strict=True):
        offset = len(rows)
        if kind == 2:
            rows.extend([] for _ in range(5))
            u, v, s, t, w = range(offset, offset + 5)
            for edge in ((hub, u), (hub, v), (u, s), (u, t), (v, s), (v, w), (t, w)):
                add(*edge)
            for site in (s, s, t, w):
                add(site)
        else:
            rows.extend([] for _ in range(kind))
            for k in range(kind):
                add(hub, offset + k)
                for _ in range(max(2, kind - 1)):
                    add(offset + k)
    return rows


def separating_cut(edges, source, target):
    graph = {}
    for left, right in edges:
        for x, y in ((left, right), (right, left)):
            graph.setdefault(x, Counter())[y] += 1
    flow = 0
    while True:
        reached = {source: None}
        pending = deque([source])
        while pending and target not in reached:
            x = pending.popleft()
            for y, capacity in graph[x].items():
                if capacity > 0 and y not in reached:
                    reached[y] = x
                    pending.append(y)
        if target not in reached:
            return flow, set(reached)
        y = target
        while y != source:
            x = reached[y]
            graph[x][y] -= 1
            graph[y][x] += 1
            y = x
        flow += 1


def separating_cost(edges, source, target):
    return separating_cut(edges, source, target)[0]


def branch_membership(arrangement, core):
    """Solve for the physical branches with the ordinary core removed."""
    n = core["ordinary_junctions"]
    remaining = set(range(n, len(arrangement.stars)))
    branches = {}
    while remaining:
        known = {min(remaining)}
        todo = list(known)
        while todo:
            v = todo.pop()
            new = (arrangement.neighbors[v] & remaining) - known
            known.update(new)
            todo.extend(new)
        remaining -= known
        sites = {w for v in known for w in arrangement.neighbors[v] if w < n}
        assert len(sites) == 1
        hub = sites.pop()
        branches.setdefault(hub, set()).update(known)
    assert set(branches) == set(core["ports"])
    return branches


def expected_capacity(kind, age):
    return kind if age < max(2, kind - 1) else 1


def literal_control(core, kinds, verify, prior, ages=5):
    start = literal_start(core, kinds)
    ar = prior.literal_stages(prior.production_law(), start, ages)
    stages = [verify.Arrangement.parse([list(row) for row in stage]) for stage in ar]
    audit = verify.start_audit(stages[0])
    assert audit["census_open_legal"] and audit["meets_once"]
    for current, after in zip(stages, stages[1:]):
        verify.round_replay(current, after)
    record = []
    for age, stage in enumerate(stages):
        membership = branch_membership(stage, core)
        ends, _, exterior = stage.holder_graph()
        assert exterior is not None
        capacities = []
        for hub in core["ports"]:
            branch = membership[hub]
            branch_edges = [(a, b) for a, b in ends.values() if a in branch or b in branch]
            assert all(v in branch | {hub, exterior} for edge in branch_edges for v in edge)
            capacities.append(separating_cost(branch_edges, hub, exterior))
        assert capacities == [expected_capacity(kind, age) for kind in kinds]
        record.append({"age": age, "junctions": len(stage.stars), "distinctions": len(stage.labels),
                       "actual_capacities": capacities, "branch_junctions": [len(membership[h]) for h in core["ports"]]})
    return {"core": core, "branch_kinds": kinds, "stages": record, "start": start}


def prepare(scratch):
    scratch.mkdir(parents=True, exist_ok=True)
    binary = scratch / "census_interfaces"
    subprocess.run(["c++", "-std=c++20", "-O3", str(HERE / "census_interfaces.cpp"), "-o", binary], check=True)
    return binary


def collect(path):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results
    records = load_results(path)
    assert set(records) == {name for name, _ in cases()}
    assert all(r["status"] == "ok" for r in records.values())
    comparisons = [records[case]["result"] for case, _ in cases()]
    prior = load(PRIOR / "census.py", "prior_census")
    verify = load(VERIFY / "verify.py", "literal_verifier")
    dense = {"ordinary_junctions": 5, "edges": list(combinations(range(5), 2)), "ports": list(range(5))}
    controls = [literal_control(dense, [1, 2, 3, 4, 5], verify, prior)]
    for row in comparisons:
        control = row["pair_only_negative_control"]
        if control is not None:
            controls.append(literal_control(control["core"], control["branch_kinds"], verify, prior, control["later_age"]))
            break
    sums = Counter()
    for row in comparisons:
        sums.update(row["counts"])
    return {"freeze": "9d6a0f5b8", "last_age": 5, "branch_kinds": [1, 2, 3, 4, 5],
            "counts": dict(sums), "families": comparisons, "literal_capacity_controls": controls}


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("prepare")
    make.add_argument("scratch", type=Path)
    report = commands.add_parser("collect")
    report.add_argument("run", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare(args.scratch))
    else:
        print(json.dumps(collect(args.run), indent=2) + "\n", end="")


if __name__ == "__main__":
    main()
