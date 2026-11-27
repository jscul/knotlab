"""Reconstruct the archived systems, count exact bonds and boxes, and compare."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import subprocess
import time

import networkx as nx


HERE = Path(__file__).resolve().parent
CUT = HERE.parent
CLOSED = CUT.parent / "UPPER-GROWN-20261127-001"
PUBLISHED_WITNESS = ("cubic_12_3.jsonl", 1)
WITNESS_CARRIERS = (
    ((0, 1, 10), (3, 4, 17)),
    ((2, 6, 18), (8, 11, 14)),
    ((5, 7, 9), (12, 13, 15)),
)


def records(directory, pattern):
    for path in sorted(directory.glob(pattern)):
        for line, data in enumerate(path.read_text().splitlines(), 1):
            yield (path.name, line, json.loads(data))


def archive_key(links):
    # Preserve the order within every named pair. The saved labels use this order.
    return tuple(sorted(map(tuple, links)))


def support_table(links, n):
    holders = [[] for _ in range(n)]
    for distinction, (a, b) in enumerate(links):
        holders[a].append(distinction)
        holders[b].append(distinction)
    return tuple(map(tuple, holders))


def meeting_invariant(graph):
    """An isomorphism invariant to avoid unnecessary exact pair comparisons."""
    triangles = nx.triangles(graph)
    return tuple(sorted(
        (tuple(sorted(Counter(lengths.values()).items())), triangles[knot])
        for knot, lengths in nx.all_pairs_shortest_path_length(graph)
    ))


def recover_closed():
    sources = list(records(CLOSED / "out", "cubic_12_*.jsonl"))
    keys = {archive_key(row["links"]) for _, _, row in sources}
    if len(sources) != 85 or len(keys) != len(sources):
        raise ValueError("the closed archive should contain 85 distinct labelled systems")

    pending = set(keys)
    matches = {}
    buckets = defaultdict(list)
    examined = 0
    for seed in range(1012, 4012):
        graph = nx.random_regular_graph(3, 12, seed=seed)
        examined += 1
        if not nx.is_connected(graph):
            continue
        key = archive_key(graph.edges())
        inv = meeting_invariant(graph)
        earlier = next((old for old in buckets[inv] if nx.is_isomorphic(graph, old)), None)
        if earlier is not None:
            if key in pending:
                raise ValueError(f"archived representative is not first in its class at {seed}")
            continue
        buckets[inv].append(graph)
        if key not in pending:
            raise ValueError(f"first representative missing from the archive at {seed}")
        pending.remove(key)
        links = list(graph.edges())
        matches[key] = seed, support_table(links, 12), list(nx.bridges(graph))
    if pending:
        raise ValueError(f"{len(pending)} closed representatives could not be reconstructed")

    rows = []
    for file, line, raw in sources:
        key = archive_key(raw["links"])
        seed, supports, bridges = matches[key]
        if raw["points"] != 12 or Counter(map(len, supports)) != {3: 12}:
            raise ValueError(f"not a twelve-knot, three-place system at {file}:{line}")
        rows.append({"source": [file, line], "seed": seed, "supports": supports,
                     "bridges": bridges, "archived": raw})
    rows.sort(key=lambda row: archive_key(row["archived"]["links"]))
    return rows, {
        "seeded_draws": examined,
        "connected_isomorphism_classes": sum(map(len, buckets.values())),
        "first_archived_representatives": len(matches),
        "last_first_occurrence_seed": max(seed for seed, _, _ in matches.values()),
    }


def cut_at(supports, distinction):
    endpoints = [i for i, knot in enumerate(supports) if distinction in knot]
    if len(endpoints) != 2:
        raise ValueError(f"expected two holders at distinction {distinction}")
    new_place = max(max(k) for k in supports) + 1
    split = tuple(
        tuple(sorted(new_place if p == distinction and i == endpoints[1] else p for p in knot))
        for i, knot in enumerate(supports)
    )
    return split, endpoints


def recover_seeded_cuts(closed):
    cut_records = list(records(CUT / "out", "cut_*.jsonl"))
    archive = {row["graph"]: (file, line, row) for file, line, row in cut_records}
    positive = [source for source in closed if source["archived"]["boxes"]]
    if len(positive) != 49 or len(cut_records) != len(positive) or archive.keys() != set(range(len(positive))):
        raise ValueError("the seed order should cover each of the 49 archived positives once")
    rows = []
    for rank, source in enumerate(positive):
        file, line, raw = archive[rank]
        cut = random.Random(20261129 + rank).randrange(18)
        supports, holders = cut_at(source["supports"], cut)
        if cut != raw["cut distinction"] or holders != raw["knots at its ends"]:
            raise ValueError(f"cannot reconstruct archived split at {file}:{line}")
        counts = Counter(p for knot in supports for p in knot)
        if counts.keys() != set(range(19)) or Counter(counts.values()) != {1: 2, 2: 17}:
            raise ValueError(f"bad split at {file}:{line}")
        if raw["boxes before"] != source["archived"]["boxes"]:
            raise ValueError(f"before-cut box count differs from source at {file}:{line}")
        rows.append({
            "source": source["source"], "seed": source["seed"], "supports": supports,
            "cut_source": [file, line], "seeded_rank": rank, "split_distinction": cut,
            "split_holders": holders, "archived": raw,
        })
    return rows


def key_box(box):
    return tuple(sorted(
        tuple(sorted((tuple(sorted(carrier)), sign) for carrier, sign in pair))
        for pair in box
    ))


def evaluate_many(binary, cases):
    proc = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    with proc:
        for supports in cases:
            width = max(max(knot) for knot in supports) + 1
            masks = (sum(1 << p for p in knot) for knot in supports)
            print(width, len(supports), *masks, file=proc.stdin, flush=True)
            response = proc.stdout.readline()
            if not response:
                raise RuntimeError("the recount engine stopped before it answered")
            yield json.loads(response)
        proc.stdin.close()
        if proc.wait():
            raise RuntimeError(f"the recount engine exited with code {proc.returncode}")


def compare_to_archive(result, row):
    raw = row["archived"]
    issues = []
    for key, ours in [("bonds", result["bonds"]), ("boxes", len(result["boxes"]))]:
        if ours != raw[key]:
            issues.append({"field": key, "ours": ours, "archived": raw[key]})
    boxes = {key_box(box) for box in result["boxes"]}
    if len(boxes) != len(result["boxes"]):
        issues.append({"field": "duplicate canonical boxes"})
    for example in raw["example"]:
        if key_box(example["box"]) not in boxes:
            issues.append({"field": "archived example missing", "example": example})
    return issues


def brute_small(supports):
    """Independent scalar semantics for controls, with no complement reduction."""
    width = max(max(k) for k in supports) + 1
    allowed = [state for state in product((0, 1), repeat=width) if all(
        len({state[p] for p in law}) == 2 for law in supports
    )]
    eligible = []
    for size in (2, 3):
        for carrier in combinations(range(width), size):
            values = [len({row[p] for p in carrier}) == 1 for row in allowed]
            if len(set(values)) != 2:
                continue
            determined = False
            for law in supports:
                on_knot = [tuple(state[p] for p in law) for state in allowed]
                if len(set(zip(on_knot, values, strict=True))) == len(set(on_knot)):
                    determined = True
                    break
            if not determined:
                eligible.append((set(carrier), values))
    candidates = 0
    bonds = 0
    missing_count = [0] * 9
    for chosen in combinations(eligible, 3):
        places, values = zip(*chosen, strict=True)
        if len(set.union(*places)) != sum(map(len, places)):
            continue
        if any(len(set(zip(a, b, strict=True))) != 4 for a, b in combinations(values, 2)):
            continue
        candidates += 1
        gap = 8 - len(set(zip(*values, strict=True)))
        if gap:
            bonds += 1
            missing_count[gap] += 1
    return (len(allowed), len(eligible), candidates, bonds, missing_count)


def small_controls(binary):
    closed_four = support_table(combinations(range(4), 2), 4)
    cases = {
        "one knot": ((0, 1, 2),),
        "three-knot ring": ((0, 1, 3), (1, 2, 4), (0, 2, 5)),
        "open three-knot chain": ((0, 1, 2), (2, 3, 4), (4, 5, 6)),
        "closed four-knot system": closed_four,
        "split four-knot system": cut_at(closed_four, 0)[0],
    }
    results = {}
    fields = ("allowed_states", "eligible_readings", "triple_candidates",
              "bonds", "bonds_by_missing_word_count")
    for (label, supports), actual in zip(cases.items(), evaluate_many(binary, cases.values()), strict=True):
        independent = brute_small(supports)
        if tuple(actual[key] for key in fields) != independent or actual["boxes"]:
            raise ValueError(f"the direct scalar control failed for {label}")
        results[label] = {"supports": supports, **actual}
    if not results["open three-knot chain"]["bonds"]:
        raise ValueError("expected a nonzero control from the open three-knot chain")
    output = subprocess.check_output([binary, "--join-control"], text=True)
    results["signed box join"] = json.loads(output)
    return results


def witness_controls(binary, closed):
    source = next(row for row in closed if tuple(row["source"]) == PUBLISHED_WITNESS)
    supports, holders = cut_at(source["supports"], 0)
    permutation = list(range(19))
    random.Random(7432).shuffle(permutation)
    inverse = {p: i for i, p in enumerate(permutation)}
    recoded = [tuple(permutation[p] for p in law) for law in reversed(supports)]
    intact, opened, recoded_result = list(evaluate_many(binary, [source["supports"], supports, recoded]))
    keys = {key_box(box) for box in opened["boxes"]}
    witness = key_box([[(carrier, 1) for carrier in pair] for pair in WITNESS_CARRIERS])
    if witness not in keys:
        raise ValueError("the documented alternate cut did not give its strict witness")
    recoded_keys = {
        key_box([[(tuple(inverse[p] for p in carrier), sign) for carrier, sign in pair] for pair in box])
        for box in recoded_result["boxes"]
    }
    count_fields = ("allowed_states", "eligible_readings", "triple_candidates", "bonds",
                    "bonds_by_missing_word_count", "boxes_with_every_carrier_place_used",
                    "boxes_by_carrier_distinction_count")
    if keys != recoded_keys or any(opened[key] != recoded_result[key] for key in count_fields):
        raise ValueError("relabeling changed exact box identities or census counts")
    return {
        "source": source["source"], "split_distinction": 0, "holders": holders,
        "relabeling": permutation, "supports": supports, "closed": intact,
        "opened": opened, "relabeling_preserved_results": True,
    }


def summary(rows):
    result = {}
    for kind in ("closed", "seeded cut"):
        cases = [r for r in rows if r["kind"] == kind]
        if not cases:
            continue
        result[kind] = {
            "cases": len(cases),
            "bond_total": sum(r["bonds"] for r in cases),
            "bond_range": [min(r["bonds"] for r in cases), max(r["bonds"] for r in cases)],
            "box_total": sum(len(r["boxes"]) for r in cases),
            "box_positive_cases": sum(bool(r["boxes"]) for r in cases),
            "box_total_with_every_carrier_place_used": sum(r["boxes_with_every_carrier_place_used"] for r in cases),
            "boxes_by_carrier_distinction_count": list(map(sum, zip(
                *(r["boxes_by_carrier_distinction_count"] for r in cases), strict=True
            ))),
            "mismatches": sum(bool(r["archive_mismatches"]) for r in cases),
            "candidate_triples": sum(r["triple_candidates"] for r in cases),
            "signed_first_pairs_with_four_shared_links": sum(r["signed_first_pairs_with_four_shared_links"] for r in cases),
            "signed_two_pairs_with_two_common_readings": sum(r["signed_two_pairs_with_two_common_readings"] for r in cases),
            "bonds_by_missing_word_count": list(map(sum, zip(
                *(r["bonds_by_missing_word_count"] for r in cases), strict=True
            ))),
            "single_missing_bonds_by_word": list(map(sum, zip(
                *(r["single_missing_bonds_by_word"] for r in cases), strict=True
            ))),
            "engine_seconds": sum(r["seconds"] for r in cases),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--limit", type=int, help="read a prefix of each of the two panels")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    start = time.perf_counter()
    closed, generation = recover_closed()
    cuts = recover_seeded_cuts(closed)
    cases = [("closed", r) for r in closed[:args.limit]] + [("seeded cut", r) for r in cuts[:args.limit]]
    rows = []
    for (kind, case), actual in zip(
        cases, evaluate_many(args.binary.resolve(), (r["supports"] for _, r in cases)), strict=True
    ):
        metadata = {key: value for key, value in case.items() if key != "archived"}
        rows.append({
            "kind": kind, **metadata, **actual,
            "archive_mismatches": compare_to_archive(actual, case),
        })
    controls = small_controls(args.binary.resolve())
    alternate = witness_controls(args.binary.resolve(), closed)
    document = {
        "closed_source": "../UPPER-GROWN-20261127-001/out/cubic_12_*.jsonl",
        "seeded_cut_source": "out/cut_*.jsonl",
        "generation": generation,
        "prefix_per_panel": args.limit,
        "summary": summary(rows),
        "controls": controls,
        "alternate_cut_control": alternate,
        "rows": rows,
        "wall_seconds": time.perf_counter() - start,
        "peak_child_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    }
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps(document["summary"], indent=2), flush=True)
    if any(r["archive_mismatches"] for r in rows):
        raise SystemExit("archived discrepancies are recorded in the output")


if __name__ == "__main__":
    main()
