"""Recount the saved certificates and compare the reported finite growth ranges."""

import argparse
import ast
from collections import Counter
from itertools import islice
import json
from pathlib import Path
import resource
from statistics import geometric_mean, mean, median
from time import perf_counter


ROOT = Path(__file__).resolve().parents[1]
NOT_CERTIFIED = "not certified (past the prefix)"
REPORTED = {
    "grow_10": ("1.39", "1.39"),
    "tree+_7": ("1.25", "2.45"),
    "tree+_8": ("1.32", "2.35"),
    "tree+_9": ("1.21", "2.48"),
    "tree+_10": ("1.17", "2.52"),
    "tree+_11": ("1.17", "2.51"),
}


def read_rows(path, limit):
    with path.open() as saved:
        return [json.loads(line) for line in islice(saved, limit)]


def growth_summary(records):
    estimators = {"arithmetic": mean, "geometric": geometric_mean, "median": median}
    selections = {
        "all pieces": lambda candidates: candidates,
        "first piece": lambda candidates: candidates[:1],
        "smallest piece rate": lambda candidates: [min(candidates)],
        "largest piece rate": lambda candidates: [max(candidates)],
    }
    comparisons = {}
    for name, estimate in estimators.items():
        for rank_count in (4, 5):
            for omit_last in (False, True):
                per_start = []
                for draw, ranks_by_piece in records:
                    candidates = []
                    for counts in ranks_by_piece:
                        selected = counts[:-1] if omit_last else counts
                        tail = selected[-rank_count:]
                        if len(tail) < 2:
                            continue
                        rate = estimate(next_count / count for count, next_count in zip(tail, tail[1:]))
                        candidates.append((rate, draw, tail))
                    if candidates:
                        per_start.append(candidates)
                for selection, select in selections.items():
                    label = f"{selection}: {name}, {rank_count} ranks, omit final rank {omit_last}"
                    estimates = [result for candidates in per_start for result in select(candidates)]
                    rates = [result[0] for result in estimates]
                    if estimates:
                        comparisons[label] = {"min": min(estimates), "max": max(estimates), "mean": mean(rates),
                                              "median": median(rates), "eligible samples or pieces": len(estimates)}
    return comparisons


def audit_cell(rows, metadata, kinds, exit_receipt):
    classes = Counter(row["class"] for row in rows)
    pieces = Counter(piece["class"] for row in rows for piece in row["pieces"])
    assert [row["draw"] for row in rows] == sorted({row["draw"] for row in rows})
    records = []
    subset_finishes = []
    decreases = []
    plateaus = []
    terminal_jumps = []
    totals_over_50000 = []
    rank_60 = []
    coverage = []
    for row in rows:
        unresolved = []
        for piece in row["pieces"]:
            if piece["class"] == "subset finish":
                remaining = 2 ** piece["m"] - piece["m"] - 1
                subset_finishes.append({"draw": row["draw"], **piece, "remaining births": remaining,
                                        "births already made": piece["births"] - remaining})
            if piece["class"] != "unresolved":
                continue
            counts = piece["births by rank"]
            assert counts and all(c > 0 for c in counts)
            unresolved.append(counts)
            coverage.append((sum(counts), len(counts), row["draw"]))
            if len(counts) >= 2:
                terminal_jumps.append((counts[-1] / counts[-2], row["draw"], counts[-2:]))
            if sum(counts) > 50_000:
                totals_over_50000.append((sum(counts), row["draw"], len(counts), counts[-1]))
            if len(counts) == 60:
                rank_60.append(row["draw"])
            if any(after < before for before, after in zip(counts, counts[1:])):
                decreases.append(row["draw"])
            if any(after == before for before, after in zip(counts, counts[1:])):
                plateaus.append(row["draw"])
        if unresolved:
            assert row["class"] == "unresolved"
            records.append((row["draw"], unresolved))

    ranges = growth_summary(records)
    result = {
        "starts by class": dict(classes),
        "pieces by class": dict(pieces),
        "piece compositions by start class": {f"{status}, {kind}": count for (status, kind), count in kinds.items()},
        "subset certificates": subset_finishes,
        "growth statistics": ranges,
        "largest final rank jump": max(terminal_jumps, default=None),
        "final rank jumps exceeding 2.52": sum(jump[0] > 2.52 for jump in terminal_jumps),
        "final rank at most penultimate count": [jump[1] for jump in terminal_jumps if jump[0] <= 1],
        "pieces with a decrease": decreases,
        "pieces with a plateau": plateaus,
        "pieces reaching rank 60": rank_60,
        "pieces exceeding 50000 accumulated births": totals_over_50000,
        "least observed births, with rank and draw": min(coverage, default=None),
        "most observed births, with rank and draw": max(coverage, default=None),
        "maximum recorded rank, with births and draw": max(coverage, key=lambda item: item[1], default=None),
        "recorded exit receipt": exit_receipt,
    }
    if metadata is not None:
        distinct = metadata["capped distinct starts"]
        draws = metadata["capped accepted draws with repeats"]
        supplied_classes = {status: count for status, count in distinct.items() if status != NOT_CERTIFIED}
        assert classes == supplied_classes
        assert len(rows) == min(metadata["per"], sum(distinct.values()))
        assert all(row["draw"] < metadata["draws"] for row in rows)
        assert all(draws[status] >= distinct[status] for status in distinct)
        assert len(draws) == len(distinct) and set(draws) == set(distinct)
        assert Counter({status: sum(c for (s, _), c in kinds.items() if status == s) for status in classes}) == classes
        assert sum(len(kind.split("+")) * count for (_, kind), count in kinds.items()) == sum(pieces.values())
        label = f"{metadata['weighting']}_{metadata['knots']}"
        result.update({
            "metadata": metadata,
            "capped distinct starts": sum(distinct.values()),
            "capped draws": sum(draws.values()),
            "uncertified distinct starts": distinct.get(NOT_CERTIFIED, 0),
            "piece compositions": {kind: sum(c for (_, other), c in kinds.items() if other == kind)
                                   for _, kind in kinds},
            "excess capped draws above distinct starts by class": {status: draws[status] - distinct[status]
                                                                    for status in distinct},
            "reported growth endpoints": REPORTED[label],
            "exact matches to both reported endpoints after rounding": [name for name, values in ranges.items()
                if tuple(format(values[bound][0], ".2f") for bound in ("min", "max")) == REPORTED[label]],
        })
    return result


def read_piece_compositions():
    result = {}
    for line in (ROOT / "pieces.txt").read_text().splitlines():
        count, fields = line.split(" ", 1)
        weighting, knots, status, kind = ast.literal_eval(fields)
        cell = result.setdefault(f"{weighting}_{knots}", Counter())
        cell[(status, kind.removeprefix("pieces: "))] += int(count)
    return result


def predecessor_counts(cells):
    earlier_table = ROOT.parent / "TWO-EXCEPTIONS-20261127-001" / "counts_table.md"
    accepted = Counter()
    comparison = {}
    for line in earlier_table.read_text().splitlines():
        if not line.startswith("| `"):
            continue
        weighting, knots, admitted, *_, capped = (field.strip() for field in line.strip("|").split("|"))
        accepted_draws, accepted_distinct = (int(x) for x in admitted.split("/"))
        capped_draws, capped_distinct = (int(x) for x in capped.split("/"))
        weighting = weighting.strip("`")
        accepted[weighting] += accepted_distinct
        label = f"{weighting}_{knots}"
        if label not in cells:
            assert capped_distinct == 0
            continue
        here = cells[label]
        comparison[label] = {
            "admitted draws, distinct": [accepted_draws, accepted_distinct],
            "predecessor capped draws, distinct": [capped_draws, capped_distinct],
            "saved rerun capped draws, distinct": [here["capped draws"], here["capped distinct starts"]],
            "saved rerun minus predecessor capped draws, distinct": [here["capped draws"] - capped_draws,
                                                                   here["capped distinct starts"] - capped_distinct],
            "saved capped share of accepted draws": here["capped draws"] / accepted_draws,
        }
    return {"distinct accepted starts summed over knot counts": dict(accepted), "cells": comparison}


def earlier_examples(current_rows):
    previous_audit = ROOT.parent / "CYCLE-READ-20261127-001" / "referee-R1" / "weightings.json"
    source = json.loads(previous_audit.read_text())
    cohort = "W1_tree+_9_seed20261130.json"
    earlier_rows = {row["first sample index"]: row["pieces"][0] for row in source["relaxed sample replay"][cohort]}
    results = {}
    for row in source["certificates"][cohort]:
        draw = row["first sample index"]
        certificate = row["pieces"][0]
        finite = certificate["finite completion"]
        earlier = earlier_rows[draw]
        starting_knots, *prior_counts = earlier["counts by rank"]
        assert starting_knots == earlier["live start knots"]
        possible_matches = []
        for current in current_rows:
            assert len(current["pieces"]) == 1
            piece = current["pieces"][0]
            if piece["class"] == "unresolved":
                current_counts = piece["births by rank"]
                overlap = min(len(current_counts), len(prior_counts))
                if current_counts[:overlap] == prior_counts[:overlap]:
                    possible_matches.append(current["draw"])
            elif finite and piece["rank"] == finite["rank"] - 1 and piece["m"] == len(finite["parent lists"]):
                possible_matches.append(current["draw"])
        result = {
            "live start knots": starting_knots,
            "first three recorded non-start rank widths": prior_counts[:3],
            "compatible new saved draws by rank widths or first subset size and rank": possible_matches,
        }
        if finite:
            total = finite["total nodes including live start knots"]
            m = len(finite["parent lists"])
            base_rank = finite["rank"]
            assert sum(prior_counts[:base_rank - 1]) + starting_knots + 2**m - m - 1 == total
            result.update({"total nodes including live start knots": total, "total births": total - starting_knots,
                           "subset width": m, "subset rank excluding live start knots": base_rank - 1})
        else:
            period = certificate["period certificate"]
            result["birth counts in one period"] = period["birth counts in one period"]
        results[str(draw)] = result
    return {"previous cohort": cohort, "cases by zero-based draw": results}


def totals(cells):
    result = {name: sum(cell[name] for cell in cells.values()) for name in (
        "capped distinct starts", "capped draws", "uncertified distinct starts", "final rank jumps exceeding 2.52"
    )}
    for key in ("starts by class", "pieces by class", "piece compositions"):
        combined = Counter()
        for cell in cells.values():
            combined.update(cell[key])
        result[key] = dict(combined)
    result["pieces with a decrease"] = sum(len(cell["pieces with a decrease"]) for cell in cells.values())
    result["pieces with a plateau"] = sum(len(cell["pieces with a plateau"]) for cell in cells.values())
    result["starts with a cycle piece by weighting"] = {
        weighting: sum(count for label, cell in cells.items() if label.startswith(f"{weighting}_")
                       for kind, count in cell["piece compositions"].items() if "cycle" in kind.split("+"))
        for weighting in ("grow", "tree+")
    }
    result["methods matching all reported endpoints after rounding"] = sorted(set.intersection(*(
        set(cell["exact matches to both reported endpoints after rounding"]) for cell in cells.values()
    )))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="use the first start row of each run")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1_000_000_000, 1_000_000_000))
    started = perf_counter()
    compositions = read_piece_compositions()
    cells = {}
    saved_rows = {}
    for file in sorted((ROOT / "runs").glob("*.jsonl")):
        rows = read_rows(file, 1 if args.pilot else None)
        metadata = None if args.pilot else rows.pop()
        if metadata is not None:
            assert metadata["seed"] == 2026112701 and metadata["draws"] == 3000
            assert metadata["big"] == 50_000 and metadata["per"] == 40
        cells[file.stem] = audit_cell(rows, metadata, compositions[file.stem], file.with_suffix(".err").read_text().strip())
        saved_rows[file.stem] = rows
    previous = earlier_examples(saved_rows["tree+_9"])
    result = {"cells": cells, "address space cap bytes": 1_000_000_000,
              "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "elapsed seconds": round(perf_counter() - started, 6)}
    if args.pilot:
        print(json.dumps({key: value for key, value in result.items() if key != "cells"}))
    else:
        result.update({"totals": totals(cells), "predecessor counts": predecessor_counts(cells),
                       "earlier examples": previous,
                       "limits of the saved records": [
                           "Draw indices identify retained rows. Repeated draws and unclassified starts have only aggregate totals, so their identities and individual stop reasons are unavailable.",
                           "The piece composition table counts every piece of each retained start. It has no per-draw link from a piece kind to a particular stopping reason.",
                           "The six receipts record successful exit. The rows do not record the pair limit or the reason an unresolved piece stopped.",
                           "Source inspection found one inherited PAIR_CAP value for both screening and certification, default 250000, and both stages catch RuntimeError broadly. The saved records do not establish whether a shell override or an unrelated exception occurred.",
                           "The producer yields a whole rank before checking cumulative births, so the nominal budget is not a strict bound on the last recorded rank.",
                       ]})
        Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
