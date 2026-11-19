"""Shared-runner census and sampled starts, with exact birth counts by roster."""

import argparse
from collections import Counter, defaultdict
from functools import cache
import gzip
from hashlib import sha256
from heapq import heapify, heappop, heappush
from itertools import combinations
import json
from pathlib import Path
from random import Random
import sys

from probe_growth import follow, initial_roster, sizes_by_round, start_metrics


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "runs/touch-census/results.jsonl"
SEED = 20261119091
WEIGHTS = ("uniform_labelled_tree", "uniform_recursive_tree", "uniform_tree_plus_links")
SIZES = (6, 8, 12, 20, 32)
REPLICATES = 64
CONFIG = {"depth": 24, "birth_limit": 12_000, "clique_limit": 400_000}
LIMITS = CONFIG.copy()


def read_results(path):
    with path.open() as handle:
        return {x["case"]: x for line in handle if (x := json.loads(line))}


@cache
def census_starts():
    rows = read_results(SOURCE)
    assert len(rows) == 265 and all(x["status"] == "ok" for x in rows.values())
    starts = sorted((tuple(row["key"][0]), tuple(row["key"][1])) for shard in rows.values()
                    for row in shard["result"]["arrangements"])
    assert len(starts) == len(set(starts)) == 26_441
    assert Counter(map(lambda key: len(key[0]), starts)) == {1: 3, 2: 22, 3: 154, 4: 1760, 5: 24502}
    return starts


@cache
def census_rosters():
    grouped = defaultdict(list)
    for index, (sizes, counts) in enumerate(census_starts()):
        links = [pair for pair, copies in zip(combinations(range(len(sizes)), 2), counts, strict=True)
                 for _ in range(copies)]
        grouped[initial_roster(sizes, links)].append([index, *start_metrics(sizes, links)])
    return sorted(grouped.items())


def encode_sample(weighting, m, rep):
    digest = sha256(f"{SEED}|{weighting}|{m}|{rep}".encode()).hexdigest()
    rng = Random(int(digest, 16))
    if weighting == "uniform_recursive_tree":
        parents = [rng.randrange(j) for j in range(1, m)]
        p = list(range(m))
        rng.shuffle(p)
        links = {tuple(sorted((p[u], p[v]))) for v,u in enumerate(parents, 1)}
    else:
        word = [rng.randrange(m) for _ in range(m-2)]
        degree = [1] * m
        for u in word:
            degree[u] += 1
        leaves = [u for u in range(m) if degree[u] == 1]
        heapify(leaves)
        links = set()
        for v in word:
            links.add(tuple(sorted((heappop(leaves), v))))
            degree[v] -= 1
            if degree[v] == 1:
                heappush(leaves, v)
        links.add(tuple(sorted(leaves)))
        if weighting == "uniform_tree_plus_links":
            choices = [edge for edge in combinations(range(m), 2) if edge not in links]
            links.update(rng.sample(choices, min(len(choices), (m+2)//4)))
    degree = Counter(v for edge in links for v in edge)
    sizes = [max(3, degree[v]) for v in range(m)]
    return digest, sizes, sorted(links)


def sample_admissible(sizes, links):
    """The wired holder graph loses no ordinary junction as a cut holder and has no one-name cut."""
    import networkx as nx

    m = len(sizes)
    graph = nx.Graph()
    graph.add_nodes_from(range(m+1))
    graph.add_edges_from(links)
    mult = Counter()
    for u, a in enumerate(sizes):
        loose = a-graph.degree(u)
        if loose:
            mult[u, m] = loose
    graph.add_edges_from(mult)
    if graph.degree(m) == 0:
        # All-closed starts have no positive age under the same law.
        graph.remove_node(m)
    ordinary_cut = sorted(set(nx.articulation_points(graph)) - {m})
    forced = sorted((min(u,v), max(u,v)) for u,v in nx.bridges(graph) if mult.get((min(u,v), max(u,v)), 1) == 1)
    return {"allowed": not ordinary_cut and not forced, "ordinary_cut_holders": ordinary_cut, "forced_meetings": forced}


def setup(params):
    global LIMITS
    LIMITS = {k: int(params.get(k, v)) for k,v in CONFIG.items()}
    census_rosters()


def cases():
    classes = len(census_rosters())
    for lo in range(0, classes, 12):
        yield f"census-{lo:05d}", {"census": [lo, min(lo+12, classes)]}
    for weighting in WEIGHTS:
        for m in SIZES:
            for rep in range(0, REPLICATES, 8):
                yield f"sample-{weighting}-{m:02d}-{rep:02d}", {"sample": [weighting, m, rep, rep+8]}


def run(case_id, payload):
    if "census" in payload:
        lo, high = payload["census"]
        items = census_rosters()[lo:high]
        return {"census": [{"roster": [list(start[0]), [list(indices(block)) for block in start[1]]],
                            "members": members, "history": follow(start, **LIMITS)} for start,members in items]}
    weighting, m, lo, high = payload["sample"]
    records = []
    for rep in range(lo, high):
        digest, sizes, links = encode_sample(weighting, m, rep)
        gate = sample_admissible(sizes, links)
        result = (follow(initial_roster(sizes, links), **LIMITS) if gate["allowed"] else
                  {"rows": [], "end": "invalid_start", "last_complete_age": 0})
        records.append({"weighting": weighting, "m": m, "replicate": rep, "seed_sha256": digest,
                        "sizes": sizes, "meetings": links, "gate": gate, "initial": start_metrics(sizes, links),
                        "history": result})
    return {"sample": records}


def indices(mask):
    return (j for j in range(mask.bit_length()) if mask & (1 << j))


def group_summary(records, depth):
    totals, endpoints, proof = Counter(), Counter(), Counter()
    censored, exceeds = [], defaultdict(list)
    ages = [defaultdict(Counter) for _ in range(depth+1)]
    for key, initial, hist in records:
        rows = hist["rows"]
        totals[hist["end"]] += 1
        if hist["end"] == "capped":
            censored.append({"key": key, "last_complete_age": hist["last_complete_age"], "cap": hist["cap"]})
        if "proven_periodicity" in hist:
            proof["periodic"] += 1
        if "single_block" in hist:
            proof["single_block"] += 1
        cells = list(sizes_by_round(initial, rows))
        endpoints[cells[-1][3]] += 1
        for age, (J,n,maximum,exhausted) in enumerate(cells):
            ages[age]["junctions"][J] += 1
            ages[age]["distinctions"][n] += 1
            ages[age]["maximum_current_size"][maximum] += 1
            ages[age]["maximum_exhausted_size"][exhausted] += 1
            if age:
                row = rows[age-1]
                ages[age]["maximum_born_size"][row["maximum_born_size"]] += 1
                ages[age]["maximum_parent_count"][row["maximum_parent_count"]] += 1
                ages[age]["enumeration_mode"][row["mode"]] += 1
            if age and exhausted > cells[age-1][3]:
                ages[age]["new_exhausted_record"][exhausted] += 1
        for field,col in (("current", 2), ("exhausted", 3)):
            found = next(((age, vals[col]) for age,vals in enumerate(cells) if vals[col] > 8), None)
            if found:
                exceeds[field].append([key, *found])
    return {"outcomes": dict(totals), "symbolic_starts": dict(proof), "capped": censored,
            "exceeding_eight_first": dict(exceeds), "end_exhausted_sizes": dict(endpoints),
            "ages": [{field: dict(hist) for field,hist in stats.items()} for stats in ages]}


def collect(source, out, depth):
    expected = {name for name, _ in cases()}
    rows = read_results(source / "results.jsonl")
    assert set(rows) == expected and all(row["status"] == "ok" for row in rows.values())
    census = [case for name,r in sorted(rows.items()) for case in r["result"].get("census", [])]
    sampled = [case for name,r in sorted(rows.items()) for case in r["result"].get("sample", [])]
    assert sum(len(c["members"]) for c in census) == 26_441 and len(sampled) == 960
    assert sorted(member[0] for c in census for member in c["members"]) == list(range(26441))
    assert len({x["seed_sha256"] for x in sampled}) == 960
    c = group_summary(((row[0], row[1:], c["history"]) for c in census for row in c["members"]), depth)
    samples = {}
    for w in WEIGHTS:
        samples[w] = {}
        for m in SIZES:
            selected = [r for r in sampled if r["weighting"] == w and r["m"] == m]
            assert len(selected) == 64
            samples[w][str(m)] = group_summary(((r["replicate"], r["initial"], r["history"]) for r in selected), depth)
    for fname, content in [("probe_census.json.gz", census), ("probe_samples.json.gz", sampled)]:
        with gzip.open(out / fname, "wt") as dest:
            json.dump(content, dest, separators=(",", ":"))
    digest = {"depth_target": depth, "case_count": len(rows), "census_start_count": 26441, "sampler_draw_count": 960,
              "census_roster_classes": len(census), "distinct_sampler_starts": len({x["seed_sha256"] for x in sampled}),
              "census_raw_source_sha256": sha256(SOURCE.read_bytes()).hexdigest(), "samples": samples, "census": c}
    (out / "probe_summary.json").write_text(json.dumps(digest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runner", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--depth", type=int, default=24)
    args = parser.parse_args()
    collect(args.runner, args.output, args.depth)
