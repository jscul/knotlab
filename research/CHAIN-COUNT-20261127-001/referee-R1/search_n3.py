"""Seek a finished start that separates the chained-twin and family conditions."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, islice
import json
from pathlib import Path
import random
import resource
import time

from rebuild import Core, TooLarge, cliques, draw, families, realize, sample


SCOPE = Path(__file__).resolve().parents[1]
ORIGINAL_DRAWS = {
    "twin8_draw.jsonl": {5631},
    "twin9_draw.jsonl": {71, 1188, 3676},
}
RANK_LIMIT = 25
WIDTH_LIMIT = 96
CLIQUE_LIMIT = 512
DIRECT_SEED = 2026112703
COHOLDING = (0.20, 0.40, 0.60, 0.80)


def replay_starts():
    yield "independent construction at seed 271248", sample(271248)
    for filename, draws in ORIGINAL_DRAWS.items():
        path = SCOPE.parent / "CYCLE-READ-20261127-001" / filename
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row["draw"] in draws:
                yield f"{filename} draw {row['draw']} from {row['weighting']}", row["stars"]


def start_parts(stars):
    holders = defaultdict(set)
    for knot, distinctions in enumerate(stars):
        assert len(distinctions) >= 3 and len({tuple(d) if isinstance(d, list) else d
                                              for d in distinctions}) == len(distinctions)
        for distinction in distinctions:
            key = tuple(distinction) if isinstance(distinction, list) else distinction
            holders[key].add(knot)
    assert max(map(len, holders.values())) <= 2
    loose = Counter(next(iter(owners)) for owners in holders.values() if len(owners) == 1)
    live = sorted(loose)
    labels = {knot: i for i, knot in enumerate(live)}
    witnesses = [set() for _ in stars]
    for owners in holders.values():
        if len(owners) == 2:
            a, b = sorted(owners)
            if a in labels:
                witnesses[b].add(labels[a])
            if b in labels:
                witnesses[a].add(labels[b])
    blocks = sorted({tuple(sorted(w)) for w in witnesses if len(w) >= 2})
    opens = [loose[knot] for knot in live]
    return live, blocks, opens


def wide_families(parents):
    neighbors = {x: set() for x in parents}
    for x, y in combinations(parents, 2):
        if parents[x] & parents[y]:
            neighbors[x].add(y)
            neighbors[y].add(x)
    maximal = list(islice(cliques(neighbors), CLIQUE_LIMIT + 1))
    if len(maximal) > CLIQUE_LIMIT:
        raise TooLarge
    groups = [g for g in maximal if len(g) >= 3 and not frozenset.intersection(*(parents[x] for x in g))]
    covered = {frozenset((x, y)) for g in groups for x, y in combinations(g, 2)}
    pairs = [frozenset((x, y)) for x in parents for y in neighbors[x] if x < y
             and frozenset((x, y)) not in covered]
    return sorted(groups + pairs, key=lambda g: tuple(sorted(g)))


def finished_core(stars):
    core = Core.__new__(Core)
    try:
        core.__init__(stars)
        return core, True
    except TooLarge:
        pass  # The independent constructor has already built its capped prefix.
    return finish_levels(core, len(stars))


def finish_levels(core, identity_offset):
    while core.level[-1]:
        latest = core.level[-1]
        if len(latest) > WIDTH_LIMIT or len(core.level) - 1 > RANK_LIMIT:
            break
        try:
            groups = wide_families({x: core.parent[x] for x in latest})
        except TooLarge:
            break
        next_level = []
        for group in groups:
            child = identity_offset + len(core.parent)
            core.parent[child] = group
            core.points[child] = frozenset.union(*(core.points[x] for x in group))
            for x in group:
                core.children[x].add(child)
            next_level.append(child)
        core.level.append(next_level)
    core.tops = [x for row in core.level[1:] for x in row if not core.children[x]]
    core.bases = {x: frozenset(core.chain.values()) & points for x, points in core.points.items()}
    return core, not core.level[-1]


def start_from_quota(blocks, quota):
    memberships = {i: {j for j, block in enumerate(blocks) if i in block} for i in range(len(quota))}
    degree = Counter(i for group in families(memberships) for i in group)
    opens = [max(1, degree[i] + extra) for i, extra in enumerate(quota)]
    return realize(len(opens), blocks, opens)


def edited_blocks(blocks, n):
    block_set = set(blocks)
    for block in blocks:
        for x in range(n):
            if x in block:
                remaining = tuple(p for p in block if p != x)
                replacement = {remaining} if len(remaining) >= 2 else set()
                yield f"remove {x} from witness {block}", (block_set - {block}) | replacement
            else:
                added = tuple(sorted((*block, x)))
                yield f"add {x} to witness {block}", (block_set - {block}) | {added}
    for pair in combinations(range(n), 2):
        if pair not in block_set:
            yield f"add pair witness {pair}", block_set | {pair}


def perturbation_starts():
    originals = list(replay_starts())
    originals.append(("construction with distinct lifts at the two marked ends",
                      draw(6, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 5)], {4: 1, 5: 1})))
    for name, stars in originals:
        live, blocks, opens = start_parts(stars)
        n = len(live)
        memberships = {i: {j for j, block in enumerate(blocks) if i in block} for i in range(n)}
        degree = Counter(i for group in families(memberships) for i in group)
        quota = tuple(opens[i] - degree[i] for i in range(n))
        assert min(quota) >= 0
        seen = {tuple(blocks)}
        for edit, variant in edited_blocks(blocks, n):
            normalized = tuple(sorted(variant))
            if normalized in seen:
                continue
            seen.add(normalized)
            yield f"{name} / {edit}", start_from_quota(normalized, quota)
        for i in range(n):
            yield f"{name} / attach a funded offshoot through a new pair at {i}", (
                start_from_quota([*blocks, (i, n)], (*quota, 1)))
            extra = tuple(q + int(j == i) for j, q in enumerate(quota))
            yield f"{name} / fund one further offshoot at {i}", start_from_quota(blocks, extra)


def direct_design(index):
    rng = random.Random(DIRECT_SEED + index)
    count = 4 + index % 6
    probability = COHOLDING[(index // 6) % len(COHOLDING)]
    cells = [set() for _ in range(count)]
    n = 0
    for a, b in combinations(range(count), 2):
        if rng.random() < probability:
            cells[a].add(n)
            cells[b].add(n)
            n += 1
    homes = []
    marked_cells = [rng.randrange(count) for _ in range(rng.randint(1, 3))]
    for i, cell in enumerate(cells):
        marked = marked_cells.count(i)
        private = max(1, 3 - len(cell), marked)
        homes.extend(range(n, n + marked))
        cell.update(range(n, n + private))
        n += private
    return sorted(map(frozenset, cells), key=lambda g: tuple(sorted(g))), homes, n, probability


def core_from_design(cells, homes, n):
    core = Core.__new__(Core)
    core.live = list(range(n))
    core.parent = {i: frozenset() for i in core.live}
    core.points = {i: frozenset((i,)) for i in core.live}
    core.children = defaultdict(set)
    core.chain = {}
    core.cell_count = len(cells)
    core.level = [core.live, []]
    for group, points in [(g, g) for g in cells] + [
        (frozenset((home,)), frozenset((home, -i-1))) for i, home in enumerate(homes)
    ]:
        node = n + len(core.parent)
        core.level[1].append(node)
        core.parent[node] = group
        core.points[node] = points
        for parent in group:
            core.children[parent].add(node)
    core.chain = {i: -i-1 for i in range(len(homes))}
    return finish_levels(core, n)


def realize_design(cells, homes, original, disabled):
    live = original.live
    blocks = {pair for cell in cells for pair in combinations(sorted(cell), 2)}
    coheld = {i: set() for i in live}
    for a, b in blocks:
        coheld[a].add(b)
        coheld[b].add(a)
    for group in cliques(coheld):
        if len(group) >= 3 and group not in cells:
            blocks.add(tuple(sorted(group)))
    degrees = Counter(i for cell in cells for i in cell)
    opens = [degrees[i] + int(i in homes) for i in live]
    substitute = {}
    for i, home in enumerate(homes):
        if original.chain[i] in disabled:
            substitute[original.chain[i]] = len(opens)
            blocks.add((home, len(opens)))
            opens.append(1)
    stars = realize(len(opens), sorted(blocks), opens)
    actual, complete = finished_core(stars)
    assert complete
    verify_substitution(original, actual, live, substitute, disabled)
    return stars, actual


def chained_twins(core):
    by_base = {}
    all_bases = set(core.chain.values())
    if not all_bases:
        return by_base
    for rank, row in enumerate(core.level):
        for x, y in combinations(row, 2):
            for c, d in combinations(sorted(core.parent[x] & core.parent[y]), 2):
                for z in sorted(core.parent[c] & core.parent[d]):
                    for base in sorted(core.bases[z]):
                        by_base.setdefault(base, {"rank": rank, "twins": [x, y],
                                                  "parents": [c, d], "common_parent": z})
                        if len(by_base) == len(all_bases):
                            return by_base
    return by_base


def family_failure(core, allowed):
    if not allowed:
        return None
    for rank, row in enumerate(core.level[1:-1], 1):
        # A relevant set of bases must be held by a parent of at least two members.
        base_sets = set()
        for p in core.level[rank - 1]:
            if len(core.children[p]) < 2:
                continue
            available = sorted(core.bases[p] & allowed)
            for size in range(1, len(available) + 1):
                base_sets.update(combinations(available, size))
        for bases in sorted(base_sets, key=lambda b: (len(b), b)):
            required = set(bases)
            parents = {x: {p for p in core.parent[x] if required <= core.bases[p]}
                       for x in row if required <= core.bases[x]}
            for group in families(parents):
                if len(group) >= 3 and not set.intersection(*(core.children[x] for x in group)):
                    return {
                        "rank": rank,
                        "bases": bases,
                        "family": sorted(group),
                        "parents_holding_bases": {x: sorted(parents[x]) for x in sorted(group)},
                        "all_parents": {x: sorted(core.parent[x]) for x in sorted(group)},
                        "all_children": {x: sorted(core.children[x]) for x in sorted(group)},
                    }
    return None


def without_bases(stars, core, disabled):
    """Replace each disabled chain offshoot by a round-1 pair with a new live knot."""
    live, blocks, opens = start_parts(stars)
    substitute = {}
    for node in core.level[1]:
        for base in core.bases[node] & disabled:
            home, = core.parent[node]
            substitute[base] = len(opens)
            blocks.append((live.index(home), len(opens)))
            opens.append(1)
    assert set(substitute) == disabled
    candidate = realize(len(opens), blocks, opens)
    rebuilt, complete = finished_core(candidate)
    assert complete
    verify_substitution(core, rebuilt, live, substitute, disabled)
    return candidate, rebuilt


def verify_substitution(core, rebuilt, live, substitute, disabled):
    # Verify the rank-1 substitutions and all later parent identities by rank.
    node_map = {old: new for old, new in zip(live, range(len(live)))}
    available = defaultdict(list)
    for node in sorted(rebuilt.level[1], reverse=True):
        available[rebuilt.parent[node], bool(rebuilt.bases[node])].append(node)
    for node in core.level[1]:
        parents = {node_map[p] for p in core.parent[node]}
        parents.update(substitute[b] for b in core.bases[node] & disabled)
        key = frozenset(parents), bool(core.bases[node] - disabled)
        node_map[node] = available[key].pop()
    assert not any(available.values())
    assert len(core.level) == len(rebuilt.level)
    for before, after in zip(core.level[2:], rebuilt.level[2:]):
        by_parents = {rebuilt.parent[x]: x for x in after}
        assert len(before) == len(after) == len(by_parents)
        for node in before:
            node_map[node] = by_parents[frozenset(node_map[p] for p in core.parent[node])]

    base_map = {}
    for node in core.level[1]:
        if core.bases[node] - disabled:
            old, = core.bases[node]
            new, = rebuilt.bases[node_map[node]]
            base_map[old] = new
    for node in core.parent:
        assert rebuilt.bases[node_map[node]] == {base_map[b] for b in core.bases[node] - disabled}


def replacement_evidence(stars, independent):
    assert not chained_twins(independent)
    failure = family_failure(independent, set(independent.chain.values()))
    assert failure
    verdict = independent.failures()
    assert verdict in {"N3", "N2N3"}
    return {"result": "counterexample", "stars": stars, "replacement_verdict": verdict,
            "replacement_rank_sizes": list(map(len, independent.level)),
            "replacement_chains": independent.chain, "replacement_failure": failure}


def inspect_start(name, stars, replay):
    core, complete = finished_core(stars)
    bases = set(core.chain.values())
    vulnerable = chained_twins(core)
    safe = bases - set(vulnerable)
    if not complete:
        result = "not run: core cap" if safe else "ruled out by chained twins in the checked prefix"
        row = {"start": name, "result": result, "chain_bases": len(bases),
               "bases_in_chained_twins": len(vulnerable), "full_core": False}
        if replay:
            row.update({"first_prefix_failure": family_failure(core, bases),
                        "prefix_rank_sizes": list(map(len, core.level)),
                        "chained_twins_in_prefix": vulnerable})
        return row
    failure_safe = family_failure(core, safe)
    if not replay and failure_safe is None:
        return {"start": name, "result": "no failure using bases outside chained twins",
                "chain_bases": len(bases), "bases_in_chained_twins": len(vulnerable), "full_core": True}
    failure_before = family_failure(core, bases)
    row = {"start": name, "knots": len(stars), "rank_sizes": list(map(len, core.level)),
           "chain_bases": len(bases), "bases_in_chained_twins": len(vulnerable), "full_core": True,
           "first_original_failure": failure_before,
           "first_original_failure_chained_twin_witnesses": {
               b: vulnerable[b] for b in (failure_before or {}).get("bases", ()) if b in vulnerable
           }}
    if failure_safe is None:
        row["result"] = "no failure using bases outside chained twins"
        return row
    stars, independent = without_bases(stars, core, set(vulnerable))
    row.update(replacement_evidence(stars, independent))
    return row


def inspect_direct(index):
    cells, homes, n, probability = direct_design(index)
    core, complete = core_from_design(cells, homes, n)
    bases = set(core.chain.values())
    vulnerable = chained_twins(core)
    safe = bases - set(vulnerable)
    row = {"draw": index, "group_cells": len(cells), "pair_coholding_probability": probability,
           "chain_bases": len(bases), "bases_in_chained_twins": len(vulnerable), "full_core": complete}
    if not complete:
        row["result"] = "not run: core cap" if safe else "ruled out by chained twins in the checked prefix"
        return row
    failure = family_failure(core, safe)
    if failure is None:
        row["result"] = "no failure using bases outside chained twins"
        return row
    stars, independent = realize_design(cells, homes, core, set(vulnerable))
    row.update({"desired_cells": [sorted(g) for g in cells], "original_chain_homes": homes})
    row.update(replacement_evidence(stars, independent))
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("series", choices=("replay", "perturb", "direct"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--count", type=int, default=1200)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (119, 119))
    started_cpu = time.process_time()
    started_wall = time.perf_counter()
    rows = []
    if args.series == "direct":
        cases = range(args.count)
    else:
        cases = list(replay_starts() if args.series == "replay" else perturbation_starts())
    for item in islice(cases, args.offset, None):
        if (args.limit is not None and len(rows) >= args.limit) or time.process_time() - started_cpu > 105:
            break
        if args.series == "direct":
            rows.append(inspect_direct(item))
        else:
            rows.append(inspect_start(*item, replay=args.series == "replay"))
        if rows[-1]["result"] == "counterexample":
            break
    weighting = {
        "replay": "One count per recorded N3-miss start: the independent seed and the four recorded draws.",
        "perturb": "One count per distinct edited witness roster within each of the six starts, and for each of the two funded offshoot edits at each live knot. Labelled starts can have equivalent cores.",
        "direct": "One count per seeded design. Each block of 24 draws crosses four pair-coholding probabilities with six counts of group cells. Cell pairs are chosen independently at the selected probability. Draw one to three chain bases uniformly, assigning each to a cell uniformly with replacement and giving each base its own private live knot.",
    }
    report = {
        "question": "Does a finished admitted start satisfy N1 and violate N3?",
        "series": args.series,
        "offset": args.offset,
        "limit": args.limit,
        "weighting": weighting[args.series],
        "method": "Check every set of bases outside chained twins on the same core. Realize a survivor by replacing every disabled offshoot with a pair at a fresh live knot, then recheck.",
        "core_caps": {"rank": RANK_LIMIT, "width": WIDTH_LIMIT, "maximal_families_per_rank": CLIQUE_LIMIT},
        "planned": len(cases),
        "tested": sum(row["result"] != "not run: core cap" for row in rows),
        "fully_rebuilt": sum(row["full_core"] for row in rows),
        "not_run": len(cases) - len(rows) + sum(row["result"] == "not run: core cap" for row in rows),
        "wall_seconds": time.perf_counter() - started_wall,
        "cpu_seconds": time.process_time() - started_cpu,
        "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rows": rows,
    }
    if args.series == "direct":
        report["seed_rule"] = f"{DIRECT_SEED} + draw index"
        report["method"] += " Compute cores from the designed groups, realizing a start only on a separating design."
    if args.output:
        aggregate = json.loads(args.output.read_text()) if args.output.exists() else {}
        if "question" in aggregate:
            aggregate = {"pilots": aggregate.get("pilots", [])}
        if args.pilot:
            aggregate.setdefault("pilots", []).append({k: v for k, v in report.items() if k != "rows"})
            if rows and rows[-1]["result"] == "counterexample":
                aggregate[args.series] = report
        else:
            aggregate[args.series] = report
        args.output.write_text(json.dumps(aggregate, indent=2) + "\n")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
