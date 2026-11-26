"""Compare the two archived readings, including every field their formats can compare."""
import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from itertools import combinations, islice
import json
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
TICKET = STUDY.with_name(STUDY.name + "A")
DATA = next((ROOT / "artifacts" / TICKET.name).glob("*E001*"))
RUNSETS = ("R2", "R2u", "R3", "R4")


def rows(path):
    with gzip.open(path, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def run_key(record):
    sp = record["spec"]
    dataset = "R3" if sp["family"] == "chains" else "R4" if sp["knot_law"] == "parity" else "R2" if sp["linked"] else "R2u"
    return (dataset, sp["knot_law"], sp["family"], sp["first"], "sole" if sp["take"] else "none", sp["ration"], sp["treatment"])


def depth_pairs():
    chains = json.loads((TICKET / "seeds.json").read_text())["second"]["chains"]
    def chain_counts(seed):
        ks = seed["knots"]
        holds = Counter(i for knot in ks for i in knot)
        i = seed["at"]
        visited = set()
        counts = []
        while i is not None:
            visited.add(i)
            counts.append(sum(holds[d] == 1 for d in ks[i]))
            following = [j for j, knot in enumerate(ks) if j not in visited and set(knot) & set(ks[i])]
            assert len(following) <= 1
            i = next(iter(following), None)
        assert len(visited) == len(ks)
        return counts
    counts = {s["name"]: chain_counts(s) for s in chains}
    pairs = {}
    for a, b in combinations(counts, 2):
        x, y = sorted((counts[a], counts[b]), key=len)
        mismatches = [i for i, (v, w) in enumerate(zip(x, y)) if v != w]
        if len(x) == len(y) and len(mismatches) == 1:
            pairs[a, b] = f"depth {mismatches[0]}"
        if len(y) == len(x) + 1 and not mismatches:
            pairs[a, b] = f"{len(x)} against {len(y)} knots"
    return pairs


def compare(s, other):
    groups = defaultdict(set)
    for name, c in other["class of each form"].items():
        groups[c].add(name)
    ours = {frozenset(g) - {"(none)"} for g in s["classes"]}
    ours.discard(frozenset())
    p = Counter(other["pairs"])
    fate_names = {"ends: no births in the cone": "ends, no births", "ends: every birth is of both": "ends, taken up"}
    after = s["after"]
    pairs = {"total": (after["pairs"], other["pairs in all"]), "apart": (after["told apart at R*"], p["told apart at R*"]),
             "later": (after["first told apart in round 2 or later"], p["in round 2 or later"]),
             "later after matching round 1": (after["of those, the wider record of round 1 the same"], p["in round 2 or later, the round-1 record of every birth with a first-seed ancestor the same"]),
             "later after matching rounds 1 and 2": (after["in round 3 or later with the wider records the same through round 2"], p["in round 3 or later, those records the same through round 2"])}
    for r in range(1, 11):
        pairs[f"first apart in round {r}"] = s["first_told_apart"].get(str(r), 0), p[f"first told apart in round {r}"]
    for term in ("never", "not read further"):
        pairs[term] = s["first_told_apart"].get(term, 0), p[term]
    profiles = s["profile_function"]
    checks = {
        "common round": s["R*"] == other["R*"],
        "last round": s["L"] == other["L"],
        "bare separate": s["bare_own_class"] == other["bare start alone"],
        "own membership": ours == {frozenset(g) for g in groups.values()},
        "own count": len(ours) == other["classes among forms, own"],
        "wider count": s["n_classes_wider"] == other["classes among forms, cone"],
        "profile flags": all(v == other["class is a function of " + k] for k, v in profiles.items()),
        "fate totals": Counter(s["fates"].values()) == {fate_names.get(k, k): v for k, v in other["fates"].items()},
        "all pair tallies": all(x == y for x, y in pairs.values()),
    }
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="one study at each of the four settings")
    a = parser.parse_args()
    t = perf_counter()
    second = {}
    for other in rows(STUDY / "checks/second_count/ffp_held.jsonl.gz"):
        k = run_key(other)
        assert k not in second
        second[k] = other
    assert len(second) == 360
    pairs = depth_pairs()
    depth = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    totals = {}
    checked = set()
    for table in RUNSETS:
        per = Counter()
        records = rows(DATA / f"studies_{table}.jsonl.gz")
        for s in islice(records, 1 if a.pilot else None):
            k = tuple(s["key"])
            assert k not in checked
            checked.add(k)
            other = second[k]
            for label, same in compare(s, other).items():
                if not same:
                    raise ValueError((k, label))
                per[label] += 1
            if table == "R3":
                classes = other["class of each form"]
                law = ", ".join(k[-3:])
                for (x, y), cell in pairs.items():
                    d = depth[law][cell]
                    d[0] += classes[x] != classes[y]
                    d[1] += 1
        totals[table] = per
    contract = json.loads(next((ROOT / "experiments" / TICKET.name).glob("*/contract.json")).read_text())
    pins = dict(contract["data_files"])
    for field in ("definitions", "claim", "preregistration", "growth_engine", "growth_definitions", "second_growth_engine"):
        pins[contract[field]] = contract[field + "_sha256"]
    for path, expected in pins.items():
        assert sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    if not a.pilot:
        assert set(second) == checked
        ref = json.loads((DATA / "tables_R3.json").read_text())
        assert depth == next(v for k, v in ref.items() if k.startswith("depth,"))
    result = {"studies": totals, "depth_cells": sum(map(len, depth.values())), "depth": dict(depth),
              "frozen_hashes_matched": len(pins),
              "archive_limit": "Own membership is present for every form. Wider classes and fates are present as aggregate counts only in the second reading."}
    if not a.pilot:
        (HERE / "readings_counts.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(checked)} studies, {result['depth_cells']} depth cells, {perf_counter()-t:.3f} s")


if __name__ == "__main__":
    main()
