"""Reproduce the starting-width and all-ages-within-current-bound census."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LAW = ROOT / "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py"
CONTROL = ((0, 2, 7, 8, 9), (1, 3, 5, 6), (0, 1, 4), (2, 3, 4), (5, 10, 11), (6, 12, 13))
SHARD = 96


def setup(params):
    global engine, roster, low, high, current
    engine = params["engine"]
    low, high = int(params.get("low", 3)), int(params.get("high", 14))
    current = int(params.get("current", 16))
    roster = [line for line in Path(params["roster"]).read_text().splitlines() if low <= int(line.split()[0]) <= high]


def cases():
    for offset in range(0, len(roster), SHARD):
        yield f"W{low}-{high}-{offset//SHARD:04d}", [offset, min(offset + SHARD, len(roster))]


def native(engine, mode, text, value=None):
    command = [engine, mode] + ([str(value)] if value is not None else [])
    return subprocess.run(command, input=text, text=True, capture_output=True, check=True).stdout


def run(case_id, payload):
    first, past = payload
    rows = [json.loads(line) for line in native(engine, "audit", "\n".join(roster[first:past]) + "\n", current).splitlines()]
    assert sum(row["counts"]["starts"] for row in rows if "origin" in row) == past - first, case_id
    return rows


def prepare(folder, width):
    folder.mkdir(parents=True, exist_ok=True)
    binary = folder / "census"
    subprocess.run(["c++", "-std=c++20", "-O3", "-Wno-return-type", str(HERE / "census.cpp"), "-o", binary], check=True)
    population = folder / f"starts{width}.txt"
    population.write_text(native(binary, "population", "", width))
    print(population)


def collect(runs, output):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results
    origins, stages, witnesses = defaultdict(Counter), defaultdict(Counter), {}
    inputs = []
    seen_widths = set()
    for folder in runs:
        job = json.loads((folder / "job.json").read_text())
        setup(job["params"])
        records = load_results(folder)
        expected = {case_id for case_id, _ in cases()}
        assert set(records) == expected, (expected - records.keys(), records.keys() - expected)
        assert all(record["status"] == "ok" for record in records.values())
        assert not seen_widths.intersection(range(low, high + 1)), "overlapping starting-width runs"
        assert all(part["current_site_cap"] == current for part in inputs), "inconsistent current limits"
        seen_widths.update(range(low, high + 1))
        inputs.append({"starting_widths": [low, high], "current_site_cap": current,
                       "starts": len(roster), "shards": len(expected),
                       "roster_sha256": sha256(("\n".join(roster) + "\n").encode()).hexdigest()})
        for case_id in sorted(records):
            for row in records[case_id]["result"]:
                if "origin" in row:
                    origins[tuple(row["origin"])].update(row["counts"])
                else:
                    key = tuple(row["stage"])
                    stages[key].update(row["counts"])
                    if "witness" in row:
                        witnesses.setdefault(key, row["witness"])
    assert sum(count["starts"] for count in origins.values()) == sum(part["starts"] for part in inputs)
    assert all(count["starts"] == sum(count[k] for k in (
        "stall_at_start", "stall_after_growth", "closed_at_start", "closed_after_growth", "next_outside_current_bound"
    )) for count in origins.values())
    assert all(not any(n for k, n in count.items() if k.startswith("unresolved")) for count in stages.values())

    def summary(scope):
        terminations = Counter()
        total, ages = Counter(), defaultdict(Counter)
        for (w, n, _, a), count in origins.items():
            if scope(w, n, a):
                terminations.update(count)
        for (w, n, _, a, age, _), count in stages.items():
            if scope(w, n, a):
                total.update(count)
                ages[age].update(count)
        return {"starts": terminations.pop("starts"), "terminations": dict(sorted(terminations.items())),
                "stages_by_age": {age: dict(values) for age, values in sorted(ages.items())}, "total": dict(total)}

    overall = {"all": summary(lambda w, n, a: True),
               "admissible": summary(lambda w, n, a: a),
               "admissible_at_most_five_starting_sites": summary(lambda w, n, a: a and n <= 5),
               "all_at_most_five_starting_sites": summary(lambda w, n, a: n <= 5),
               "admissible_through_width_14": summary(lambda w, n, a: w <= 14 and a),
               "all_through_width_14": summary(lambda w, n, a: w <= 14)}
    data = {"freeze": "d5b1aba64", "inputs": inputs, "summary": overall,
            "by_width": {w: {"all": summary(lambda width, n, a: w == width),
                             "admissible": summary(lambda width, n, a: w == width and a)}
                         for w in sorted(seen_widths)},
            "origin_dimensions": ["starting_width", "starting_sites", "starting_loose", "all_stars_are_bonds"],
            "stage_dimensions": ["starting_width", "starting_sites", "starting_loose", "all_stars_are_bonds", "age", "current_sites"],
            "origins": [{"key": key, "counts": count} for key, count in sorted(origins.items())],
            "stages": [{"key": key, "counts": count, **({"witness": witnesses[key]} if key in witnesses else {})}
                       for key, count in sorted(stages.items())]}
    output.write_text(json.dumps(data, indent=2) + "\n")


def production_law():
    spec = spec_from_file_location("census_production_law", LAW)
    law = module_from_spec(spec)
    spec.loader.exec_module(law)
    return law


def holders(rows):
    users = defaultdict(list)
    for j, row in enumerate(rows):
        assert len(row) == len(set(row))
        for b in row:
            users[b].append(j)
    assert sorted(users) == list(range(len(users)))
    return [tuple(users[b]) for b in range(len(users))]


def literal_stages(law, start, depth):
    grown = law.from_junctions(start)
    stages = [tuple(tuple(row) for row in start)]
    for _ in range(depth):
        assert grown.step(law.gf2(law.F.fewest), None)["new"] and grown.implied_mismatch == 0
        stages.append(tuple(tuple(sorted(row)) for row in grown.bits_of))
    for stage in stages:
        users = holders(stage)
        shared = [meet for meet in users if len(meet) == 2]
        assert all(len(row) >= 3 for row in stage) and all(1 <= len(meet) <= 2 for meet in users)
        assert len(shared) == len(set(shared)), "a pair of junctions meets twice"
    return stages


def literal_table(binary, rows):
    users = holders(rows)
    n = len(rows) + any(len(meet) == 1 for meet in users)
    endpoints = [meet if len(meet) == 2 else (*meet, len(rows)) for meet in users]
    weight = Counter(endpoints)
    classes = {pair: index for index, pair in enumerate(weight)}
    m = len(classes)
    fields = [n, m, m, *(value for pair, count in weight.items() for value in (*pair, count)), *range(m)]
    values = tuple(map(int, native(binary, "compare-tables", " ".join(map(str, fields)) + "\n").split()))
    assert len(values) == m * m
    return {(a, b): values[classes[endpoints[a]] * m + classes[endpoints[b]]]
            for a, b in combinations(range(len(users)), 2)}


def rejected_input_swap(table, movable):
    for a, b in combinations(range(movable), 2):
        for other in range(movable):
            if other in (a, b):
                continue
            left, right = tuple(sorted((a, other))), tuple(sorted((b, other)))
            if table[left] != table[right]:
                return {"swap": [a, b], "current_pair": left, "current_pair_image": right,
                        "current_K": [table[left], table[right]]}
    raise AssertionError("the negative-control deck has no ineligible swap")


def replay_witness(law, binary, witness, age):
    stages = literal_stages(law, witness["start"], age + 1)
    users = holders(stages[age])
    pinned_sites = {meet[0] for meet in users if len(meet) == 1}
    pinned = {b for b, meet in enumerate(users) if pinned_sites.intersection(meet)}
    order = sorted(range(len(users)), key=lambda b: (b in pinned, b))
    rebase = {b: i for i, b in enumerate(order)}

    def normalize(rows):
        return sorted(tuple(sorted(row)) for row in rows)

    for name, stage in (("current", stages[age]), ("next", stages[age + 1])):
        assert normalize(witness[name]) == normalize(tuple(rebase.get(b, b) for b in row) for row in stage)
    old = witness["current"]
    p = witness["old_movable_permutation"]
    image = p + list(range(len(p), len(users)))
    assert sorted(image) == list(range(len(users))) and all(image[rebase[b]] == rebase[b] for b in pinned)
    assert len(p) == len(users) - len(pinned)

    def transport(pair):
        return tuple(sorted(image[b] if b < len(image) else b for b in pair))

    before = literal_table(binary, old)
    assert all(value == before[transport(pair)] for pair, value in before.items())
    a, b = witness["old_pair"]
    assert a >= 0 and b >= 0
    assert all(len(users[order[i]]) == 2 for i in {a, b, image[a], image[b]})
    after = literal_table(binary, witness["next"]) if len(witness["next"]) <= 22 else None
    if after is not None:
        assert (after[a, b], after[transport((a, b))]) == tuple(witness["successor_K"])

    return {"junctions_and_width_by_age": [[len(row), len(holders(row))] for row in stages],
            "age": age, "current_pinned_distinctions": len(pinned), "current_pair_entries_verified": len(before),
            "successor_pair_entries_verified": len(after) if after is not None else None,
            "stable_pair": [a, b], "stable_pair_image": transport((a, b)),
            "successor_bond_distances": [k - 1 for k in witness["successor_K"]],
            "input_swap_rejected": rejected_input_swap(before, len(p)),
            "complete_old_map": image, "witness": witness}


def control(binary, census=None):
    law = production_law()
    stages = literal_stages(law, CONTROL, 3)
    assert list(map(len, stages)) == [6, 12, 19, 25]
    origin = [set(row) for row in CONTROL]
    bits = sum(1 << i for i, (a,b) in enumerate((a,b) for a in range(6) for b in range(a+1,6)) if origin[a] & origin[b])
    users = holders(CONTROL)
    loose = [sum(len(users[b]) == 1 for b in row) for row in CONTROL]
    record = [json.loads(line) for line in native(binary, "audit", " ".join(map(str, (14,6,1,bits,*loose))) + "\n", 20).splitlines()]
    scope, first, second = record
    assert first["counts"]["exact_successor"] == 1 and not first["counts"]["failing_generators"]
    assert second["counts"]["failure"] == second["counts"]["rooted_successors"] == 1
    assert sorted(second["witness"]["successor_K"]) == [3,4]
    assert len(second["witness"]["next"]) == len(stages[-1])
    data = {"production_stages": stages, "exact_census_control": [scope, first, second],
            "larger_age_two_control": replay_witness(law, binary, second["witness"], 2)}
    if census is not None:
        broken = [row for row in census["stages"] if "witness" in row]
        data["census_witnesses"] = [replay_witness(law, binary, row["witness"], row["key"][4]) for row in broken]
    return data


def main():
    parser = ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    make = sub.add_parser("prepare")
    make.add_argument("folder", type=Path)
    make.add_argument("--width", type=int, default=15)
    check = sub.add_parser("control")
    check.add_argument("binary", type=Path)
    check.add_argument("--census", type=Path)
    combine = sub.add_parser("collect")
    combine.add_argument("output", type=Path)
    combine.add_argument("runs", nargs="+", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.folder, args.width)
    elif args.mode == "control":
        census = json.loads(args.census.read_text()) if args.census is not None else None
        print(json.dumps(control(args.binary, census), indent=2))
    else:
        collect(args.runs,args.output)


if __name__ == "__main__":
    main()
