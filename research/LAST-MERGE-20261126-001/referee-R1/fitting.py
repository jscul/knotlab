"""Recount the earlier four growth archives using exact integer differences."""

import argparse
from collections import Counter, defaultdict
import gzip
import itertools
import json
from math import comb
from pathlib import Path
import resource
from time import perf_counter


EARLIER = Path(__file__).resolve().parents[2] / "SETTLE-BOUND-20261126-001"
READINGS = {"sig0": (5, 3), "sig1": (7, 5)}


def start_inventory(stars):
    """Recount the live knots, shared-neighbour blocks and round-1 groups."""
    holders = defaultdict(set)
    for knot, distinctions in enumerate(stars):
        for distinction in distinctions:
            holders[distinction].add(knot)
    loose = Counter(next(iter(knots)) for knots in holders.values() if len(knots) == 1)
    neighbours = [set().union(*(holders[d] for d in knot)) - {i}
                  for i, knot in enumerate(stars)]
    blocks = [group & loose.keys() for group in neighbours]
    common_neighbours = Counter(pair for block in blocks for pair in itertools.combinations(sorted(block), 2))
    pairs = set(common_neighbours)
    candidates = []
    for size in range(len(loose), 2, -1):
        for members in itertools.combinations(sorted(loose), size):
            group = set(members)
            if any(group <= larger for larger in candidates):
                continue
            if all(pair in pairs for pair in itertools.combinations(members, 2)):
                candidates.append(group)
    joins = [group for group in candidates if not any(group <= block for block in blocks)]
    covered = {pair for group in joins for pair in itertools.combinations(sorted(group), 2)}
    joins.extend(set(pair) for pair in pairs - covered)
    spent = Counter(knot for group in joins for knot in group)
    if all(spent[k] <= loose[k] for k in loose):
        leftover = loose.total() - spent.total()
        births = Counter(("join", len(group), tuple(sorted(len(stars[k]) for k in group)))
                         for group in joins)
        for knot, count in (loose - spent).items():
            births[("offshoot", 1, (len(stars[knot]),))] += count
    else:
        births = Counter()
        leftover = None
    map_conditions_failed = []
    if any(len(knots) > 2 for knots in holders.values()):
        map_conditions_failed.append("a distinction held by more than two knots")
    if any(len(group) >= 3 for group in joins):
        map_conditions_failed.append("a round-1 group of at least three")
    if any(count >= 2 for count in common_neighbours.values()):
        map_conditions_failed.append("two live knots with two common neighbours")
    if loose.total() < 2:
        map_conditions_failed.append("fewer than two loose distinctions")
    if leftover is None:
        map_conditions_failed.append("a round-1 shortage")
    return loose, max(map(len, blocks), default=0), leftover, births, map_conditions_failed


def dimension(totals):
    if len(totals) < 10:
        return None
    tail = totals[-8:]
    for degree in range(4):
        if min(tail) == max(tail) and tail[0] > 0:
            return degree + 1
        tail = [b - a for a, b in zip(tail, tail[1:])]
    return None


def settling_round(reading, dim):
    """Use the last nonzero order-D difference across every birth kind.

    A stencil that ends at a round after K tests the same degree-at-most-D−1
    polynomial as the fit through K−D+1 through K. Missing counts are zero.
    """
    weights = [(-1) ** (dim - i) * comb(dim, i) for i in range(dim + 1)]
    for end in range(len(reading), dim, -1):
        stencil = Counter()
        for weight, counts in zip(weights, reading[end - dim - 1:end]):
            for kind, count in counts.items():
                stencil[kind] += weight * count
        if any(stencil.values()):
            break
    else:
        end = dim
    cut = max(3, end)
    return cut if cut <= len(reading) - 2 else None


def sig0_rows(rows):
    return [{tuple(signature): count for signature, count in row["sig0"]}
            for row in rows]


def sig1_rows(rows):
    return [{(tuple(birth), tuple(map(tuple, parents))): count
             for (birth, parents), count in row["sig1"]}
            for row in rows]


def count_range(histogram):
    return [min(histogram), max(histogram)] if histogram else None


def recount(path, limit):
    summary = Counter()
    ranges = defaultdict(Counter)
    offsets = defaultdict(Counter)
    late = []
    maxima = {}
    with gzip.open(path, "rt") as archive:
        for line in itertools.islice(archive, limit):
            record = json.loads(line)
            summary["records"] += 1
            label = record["kind"]
            rows = record["rows"]
            index = record["index"]
            loose, block, leftover, births, map_conditions_failed = start_inventory(record["stars"])
            assert record["loose"] == [loose[k] for k in range(record["n knots"])], index
            first_round = rows[0]["sig0"] if rows else []
            fresh = max((kind[2] for kind, _ in first_round), default=0)
            M = max(block, fresh)
            assert M == record["M"], index
            first_with_parents = Counter()
            if rows:
                for (birth, parents), count in rows[0]["sig1"]:
                    first_with_parents[(birth[0], birth[1], tuple(p[3] for p in parents))] += count
            assert first_with_parents == births, (path.name, index, first_with_parents, births)
            totals = [row["n"] for row in rows]
            dim = None if label.startswith(("stalls", "closes")) else dimension(totals)
            assert (f"dim {dim}" if dim else None) == (label if label.startswith("dim") else None), index
            if dim is None:
                summary["outside dimension-labelled population"] += 1
                continue
            summary["dimension-labelled records"] += 1
            summary["dimension-labelled records stopping before round 24"] += len(rows) < 24
            with_fall = [round_number for round_number, (a, b) in enumerate(zip(totals, totals[1:]), 2)
                         if a > b]
            T = max(with_fall, default=1)
            ranges["M"][M] += 1
            ranges["T"][T] += 1
            views = {"sig0": sig0_rows(rows), "sig1": sig1_rows(rows)}
            cuts = {}
            is_late = {}
            for read, (m_offset, t_offset) in READINGS.items():
                reading = views[read]
                assert all(sum(counts.values()) == total for counts, total in zip(reading, totals)), index
                K = settling_round(reading, dim)
                if K is None:
                    summary[f"{read} unsettled"] += 1
                    continue
                cuts[read] = K
                is_late[read] = K > M + m_offset
                ranges[f"{read} K"][K] += 1
                ranges[f"{read} K minus T"][K - T] += 1
                summary[f"{read} combined bound violations"] += K > max(M + m_offset, T + t_offset)
                summary[f"{read} T bound violations"] += K > T + t_offset
                summary[f"{read} late"] += is_late[read]
                summary[f"{read} late and point law agrees"] += is_late[read] and K == T + t_offset
                summary[f"{read} combined bound equalities"] += K == max(M + m_offset, T + t_offset)
                key = f"{read} K minus T"
                witness = (K - T, index, M, T, K)
                maxima[key] = max(maxima.get(key, witness), witness)
            if len(cuts) == len(READINGS):
                offsets["strict fall" if with_fall else "no fall"][(cuts["sig0"] - T, cuts["sig1"] - T)] += 1
            if any(is_late.values()):
                proxy = len(loose) + leftover
                round_1_live = sum(count for kind, count in first_round if kind[2] > 0)
                late.append({
                    "census index": index, "dimension": dim, "saved rounds": len(totals),
                    "M": M, "T": T, "K": cuts, "late": is_late,
                    "strict falls at rounds": with_fall, "birth totals": totals,
                    "births at T": totals[T - 1],
                    "first singleton birth round": next((i for i, n in enumerate(totals, 1) if n == 1), None),
                    "live start knots": len(loose), "round 1 offshoots": leftover,
                    "failed conditions of the map theorem": map_conditions_failed,
                    "T minus (live start knots plus leftover)": T - proxy,
                    "T minus (live start knots plus leftover minus 1)": T - (proxy - 1),
                    "T minus (live round 1 births plus leftover)": T - (round_1_live + leftover),
                })
    return {
        "counts": dict(summary),
        "ranges": {name: count_range(hist) for name, hist in ranges.items()},
        "maxima witnesses [K minus T, census index, M, T, K]": maxima,
        "offsets [sig0, sig1, count]": {
            group: [[*pair, count] for pair, count in sorted(hist.items())] for group, hist in offsets.items()
        },
        "late records": late,
    }


def summarize(data):
    total = Counter()
    nae_offsets = Counter()
    late_nae = []
    for path, section in data.items():
        total.update(section["counts"])
        if "_nae." in path:
            for offset0, offset1, number in section["offsets [sig0, sig1, count]"].get("strict fall", []):
                nae_offsets[(offset0, offset1)] += number
            late_nae.extend(section["late records"])
    proxies = ["T minus (live start knots plus leftover)",
               "T minus (live start knots plus leftover minus 1)",
               "T minus (live round 1 births plus leftover)"]
    return {
        "counts across all archives": dict(total),
        "not-all-equal strict fall records": nae_offsets.total(),
        "not-all-equal strict-fall offsets [sig0, sig1, count]": [
            [*pair, number] for pair, number in sorted(nae_offsets.items())
        ],
        "late not-all-equal records": len(late_nae),
        "late not-all-equal records with first singleton at T": sum(
            row["first singleton birth round"] == row["T"] for row in late_nae
        ),
        "late not-all-equal records failing conditions of the map theorem": sum(
            bool(row["failed conditions of the map theorem"]) for row in late_nae
        ),
        "late not-all-equal proxy discrepancy ranges": {
            key: count_range(Counter(row[key] for row in late_nae)) for key in proxies
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="read this many records per archive", default=None)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    began = perf_counter()
    files = [EARLIER / f"grown_g{size}_{law}.jsonl.gz" for size in (5, 6) for law in ("nae", "par")]
    data = {path.name: recount(path, args.limit) for path in files}
    result = {
        "records per archive limit": args.limit,
        "seconds": round(perf_counter() - began, 3),
        "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "address space cap KiB": resource.getrlimit(resource.RLIMIT_AS)[0] // 1024,
        "summary": summarize(data),
        "archives": data,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
