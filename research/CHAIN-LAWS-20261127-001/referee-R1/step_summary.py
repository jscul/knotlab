"""Join independent decisions to the start-stage roster and audit the frozen rows."""

import argparse
import gzip
import json
import resource
import time
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SELECTIONS = ("first_three", "after_three", "all")
ARMS = ("one_fewer", "arity_floor")


def records(path):
    with gzip.open(path, "rt") as handle:
        for line in handle:
            yield json.loads(line)


def stage_rows(name, selected):
    rows = {}
    for row in records(HERE / name):
        key = row["stage"], row["chain_index"]
        if key[0] in selected:
            assert key not in rows
            rows[key] = row
    return rows


def metrics(reading, paired, nonpaired):
    """The row's every_law alone, its conjunction with frozen and all roles are distinct."""
    frozen = reading["frozen"]
    every_law = reading["every_law"]
    out = {"structural_chain": 1, "four_exact_lower_triples": all(i == 127 for i in reading["lower"]),
           "source_opacity": not any(reading["source_failures"]),
           "three_exact_upper_relations": all(i == 127 for i in reading["upper"]),
           "frozen": frozen, "every_law": every_law, "frozen_and_every_law": frozen and every_law}
    if paired is None:
        return out
    paired_bonds = paired["determining_bonds"]
    residual_bonds = nonpaired["determiners"]
    assert len(paired_bonds) == 3 and len(residual_bonds) == 6
    assert all(v >= 0 for v in (*paired_bonds, *residual_bonds))
    can_read = [n > 0 or paired_bonds[i // 2] > 0 for i, n in enumerate(residual_bonds)]
    base = out["four_exact_lower_triples"] and out["source_opacity"]
    localities = [not any(can_read[2 * j + (j != both)] for j in range(3)) for both in range(3)]
    full_roles = [bool(base and localities[i] and reading["upper"][i] == 127
                       and all(mask & (1 << i) for mask in reading["restore"])) for i in range(3)]
    locality = all(localities)
    out.update(paired_locality=not any(paired_bonds), nonpaired_locality=not any(residual_bonds),
               locality=locality, frozen_and_locality=frozen and locality,
               every_law_and_locality=every_law and locality, all_gates=frozen and every_law and locality,
               any_role_passes=any(full_roles),
               **{f"role_{i}_passes": value for i, value in enumerate(full_roles)})
    assert out["all_gates"] == all(full_roles)
    return out


def read_author_rows():
    archived = {}
    for arm in ARMS:
        starts = {}
        for path in sorted((HERE.parent / "out").glob(f"{arm}_*.jsonl")):
            for line in path.read_text().splitlines():
                row = json.loads(line)
                start = row["start"]
                assert start not in starts
                starts[start] = {record["round"]: record for record in row["rows"] if "round" in record}
        assert set(starts) == set(range(7075))
        archived[arm] = starts
    return archived


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pilot", action="store_true")
    cli.add_argument("--frozen-only", action="store_true")
    args = cli.parse_args()
    timer = time.perf_counter()
    stages = {row["id"]: row for row in records(HERE / "step_stages.jsonl.gz")
              if not args.pilot or row["id"] < 8}
    incidence = defaultdict(list)
    for row in records(HERE / "step_incidence.jsonl.gz"):
        if row["stage"] in stages:
            incidence[row["stage"]].append((row["arm"], row["start"], row["round"]))
    readings = stage_rows("step_reading_rows.jsonl.gz", stages)
    all_keys = {(sid, k) for sid, row in stages.items() for k in range(len(row["chains"]))}
    assert set(readings) == all_keys
    paired = {}
    nonpaired = {}
    if not args.frozen_only:
        paired = stage_rows("step_paired_rows.jsonl.gz", stages)
        nonpaired = stage_rows("step_nonpaired_rows.jsonl.gz", stages)
        assert all_keys == paired.keys() == nonpaired.keys()
    raw = read_author_rows()
    encountered = {arm: {} for arm in ARMS}
    stage_totals = {}
    extrema = {}
    saved = []
    for sid, row in stages.items():
        occurrences = sorted(incidence[sid])
        assert len(occurrences) == 2 and {a for a, _, _ in occurrences} == set(ARMS)
        assert occurrences[0][1:] == occurrences[1][1:]
        subtotal = {name: Counter() for name in SELECTIONS}
        for rank in range(len(row["chains"])):
            key = (sid, rank)
            counts = metrics(readings[key], paired.get(key), nonpaired.get(key))
            counted = {g: int(v) for g, v in counts.items()}
            for name in ("first_three" if rank < 3 else "after_three", "all"):
                subtotal[name].update(counted)
            if not args.frozen_only:
                saved.append({"stage": sid, "chain_index": rank, "frozen": bool(counts["frozen"]),
                              "every_law": bool(counts["every_law"]), "paired_locality": bool(counts["paired_locality"]),
                              "locality": bool(counts["locality"]), "all_gates": bool(counts["all_gates"]),
                              "full_roles": [counts[f"role_{i}_passes"] for i in range(3)]})
        stage_totals[sid] = subtotal
        for arm, start, rnd in occurrences:
            assert (start, rnd) not in encountered[arm]
            encountered[arm][start, rnd] = sid
            author = raw[arm][start][rnd]
            assert len(row["chains"]) == author["chains"]
            assert subtotal["first_three"]["frozen"] == author["carried steps"], (arm, start, rnd)
            assert subtotal["first_three"]["frozen_and_every_law"] == author["every law needed"], (arm, start, rnd)
        for name in ("first_three", "all"):
            if not args.frozen_only and subtotal[name]["all_gates"] == 0:
                extrema.setdefault(f"chain_positive_no_full_pass_{name}", []).append({
                    "start": occurrences[0][1], "round": occurrences[0][2],
                    "chains": subtotal[name]["structural_chain"], "frozen": subtotal[name]["frozen"]})
    if not args.pilot:
        for arm, starts in raw.items():
            assert {(start, rnd) for start, rounds in starts.items() for rnd, record in rounds.items() if record["chains"]} == encountered[arm].keys()
    assert encountered[ARMS[0]] == encountered[ARMS[1]]

    gates = list(stage_totals[next(iter(stages))]["all"])
    # Start and round of each chain-positive stage were checked to coincide
    # across arms. Their stage counts in the remaining (chain-free) cells can differ.
    cells = encountered[ARMS[0]]
    totals = {selection: Counter() for selection in SELECTIONS}
    round_counts = {selection: defaultdict(Counter) for selection in SELECTIONS}
    round_stages = {selection: defaultdict(Counter) for selection in SELECTIONS}
    appearances = {selection: defaultdict(dict) for selection in SELECTIONS}
    identities = {selection: defaultdict(set) for selection in SELECTIONS}
    for (start, rnd), sid in cells.items():
        for selection, cnts in stage_totals[sid].items():
            totals[selection].update(cnts)
            round_counts[selection][rnd].update(cnts)
            for gate, count in cnts.items():
                round_stages[selection][rnd][gate] += int(count > 0)
                if count:
                    by_start = appearances[selection][gate]
                    by_start[start] = min(by_start.get(start, rnd), rnd)
        for k, chain in enumerate(stages[sid]["chains"]):
            key = (sid, k)
            counts = metrics(readings[key], paired.get(key), nonpaired.get(key))
            identity = start, tuple(chain)
            for selection in ("all", "first_three" if k < 3 else "after_three"):
                for gate in ("structural_chain", "frozen", "frozen_and_every_law", "frozen_and_locality", "all_gates"):
                    if counts.get(gate):
                        identities[selection][gate].add(identity)

    first = {s: {k: dict(sorted(Counter(d.values()).items())) for k, d in choices.items()}
             for s, choices in appearances.items()}
    final_by_arm = {}
    for arm, starts in raw.items():
        growing = {start for start, rounds in starts.items() if 1 in rounds}
        reached_six = {start for start, rounds in starts.items() if 6 in rounds}
        counts = {}
        for selection in SELECTIONS:
            choices = {}
            for gate in gates:
                hits = set(appearances[selection][gate])
                at_six = {start for (start, rnd), sid in cells.items() if rnd == 6 and stage_totals[sid][selection][gate]}
                choices[gate] = {"ever": len(hits), "round_six": len(at_six),
                                 "ever_among_reached_six": len(hits & reached_six),
                                 "ever_among_growing_who_stopped_before_six": len((hits & growing) - reached_six),
                                 "ever_among_never_grew": len(hits - growing)}
            counts[selection] = choices
        final_by_arm[arm] = {"all_starts": len(starts), "grew_once": len(growing), "reached_six": len(reached_six),
                             "stage_rows_by_round": {rnd: sum(rnd in r for r in starts.values()) for rnd in range(7)},
                             "start_counts": counts}
    earlier = {}
    for gate in gates:
        before = appearances["first_three"][gate]
        after = appearances["all"][gate]
        earlier[gate] = {str(start): {"first_three": before.get(start), "all": val}
                         for start, val in after.items() if start not in before or before[start] > val}
    totals_by_identity = {s: {g: len(ids) for g, ids in by_gate.items()} for s, by_gate in identities.items()}
    rescued = {}
    for gate in (("frozen",) if args.frozen_only else ("frozen", "all_gates")):
        rescued[gate] = []
        for (start, rnd), sid in cells.items():
            if stage_totals[sid]["all"][gate] and not stage_totals[sid]["first_three"][gate]:
                rank = next(i for i in range(3, len(stages[sid]["chains"]))
                            if metrics(readings[sid, i], paired.get((sid, i)), nonpaired.get((sid, i)))[gate])
                rescued[gate].append({"start": start, "round": rnd, "stage": sid,
                                      "first_passing_chain_one_based": rank + 1, "total_chains": len(stages[sid]["chains"])})
    if not args.frozen_only:
        suffix = "_pilot" if args.pilot else ""
        target = HERE / f"step_passes{suffix}.jsonl.gz"
        temporary = target.with_suffix(".partial")
        with gzip.open(temporary, "wt") as out:
            for row in saved:
                print(json.dumps(row, separators=(",", ":")), file=out)
        temporary.replace(target)
    stats = {"scope": "Eight-knot chain occurrences on reached rounds 0 through 6. Both arms have the same chain-positive stage at each listed start and round.",
             "stages": len(stages), "frozen_rows_audited_per_arm": len(cells),
             "selection_totals_per_arm": totals, "counts_by_round_per_arm": round_counts,
             "positive_stages_by_round_per_arm": round_stages, "distinct_chains_per_arm_counted_once_per_start": totals_by_identity,
             "first_appearances_by_round_per_arm": first, "population_and_start_counts": final_by_arm,
             "improved_first_appearance_when_all_chains_examined": earlier,
             "stages_with_pass_only_after_first_three": rescued, "exceptions": extrema,
             "wall_seconds": time.perf_counter() - timer, "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    file = "step_frozen_counts" if args.frozen_only else "step_summary"
    suffix = "_pilot" if args.pilot else ""
    target = HERE / f"{file}{suffix}.json"
    temporary = target.with_suffix(".partial")
    temporary.write_text(json.dumps(stats, indent=2) + "\n")
    temporary.replace(target)
    print(json.dumps({"selection_totals_per_arm": totals, "wall_seconds": stats["wall_seconds"], "peak_kib": stats["peak_kib"]}))


if __name__ == "__main__":
    main()
