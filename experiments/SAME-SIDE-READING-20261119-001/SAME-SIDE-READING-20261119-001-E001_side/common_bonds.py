"""Exact and bounded sizes of one parity bond through fixed original marks."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from heapq import heappop, heappush
from itertools import combinations, count, product
import json
from pathlib import Path
from random import Random
import sys
from time import monotonic

import side_sources


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = side_sources.OLDER.parent
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.insert(0, str(PREVIOUS))
from bond_distances import Wiring, bitset, literal_states_distances  # noqa: E402
from bond_age_two import PairPartitions  # noqa: E402
from bond_later import PinFlow  # noqa: E402
import world_ring_distance_dp as partitions  # noqa: E402


WIDTH_LIMIT = 14
WORK_LIMIT = 2_000_000
PANEL_CASES = tuple(side_sources.AGES)
INFINITY = "infinity"
COLUMNS = ("lower_size", "upper_size", "witness_index", "method", "limit", "work")


def split_pins(wire, marks):
    """Enumerate consistent side assignments, fixing the auxiliary exterior outside."""
    edges = tuple(wire.edge[d] for d in marks)
    for choices in product((0, 1), repeat=len(edges)):
        inside = bitset(edge[c] for c, edge in zip(choices, edges, strict=True))
        outside = (1 << wire.exterior) | bitset(edge[1-c] for c, edge in zip(choices, edges, strict=True))
        if not inside & outside:
            yield inside, outside


def by_partitions(kernel, marks):
    budget = partitions.Budget(kernel.deadline)
    rows, _ = kernel.read_table(kernel.wire.exterior, marks, budget)
    entry = rows.get(0, {}).get(((), 3, 0))
    if entry is None:
        # A restricted ceiling is only used for this query when a verified
        # witness already proves that the optimum fits below that ceiling.
        assert kernel.ceiling == len(kernel.wire.edge)
        return INFINITY, None, budget.steps
    cost, mask = entry
    kernel.wire.witness(mask, marks, cost)
    return cost, mask, budget.steps


def by_flows(solver, marks, warm, limit):
    """Complete connected cuts by disjoint branches when a colored shore disconnects."""
    wire = solver.wiring
    unrestricted = len(wire.edge) + 1
    best = unrestricted if warm is None else len(wire.witness(warm, marks)["distinctions"])
    waiting, order = [], count()
    before = solver.evaluations

    def evaluate(inside, outside):
        nonlocal best, warm
        weight, shore = solver.minimum(inside, outside)
        if weight >= best:
            return
        failed = solver.flaw(shore, inside, outside)
        if failed is None:
            wire.witness(shore, marks, weight)
            best, warm = weight, shore
        else:
            opposite, boundary = failed
            if boundary:
                heappush(waiting, (weight, next(order), inside, outside, opposite, boundary))

    for pins in sorted(set(split_pins(wire, marks))):
        evaluate(*pins)
    stopped = False
    while waiting and waiting[0][0] < best:
        _, _, inside, outside, opposite, boundary = waiting[0]
        if solver.evaluations - before + boundary.bit_count() > limit:
            stopped = True
            break
        heappop(waiting)
        while boundary:
            bit = boundary & -boundary
            boundary ^= bit
            if opposite:
                evaluate(inside, outside | bit)
                inside |= bit
            else:
                evaluate(inside | bit, outside)
                outside |= bit
    high = best if best < unrestricted else INFINITY
    low = waiting[0][0] if stopped else high
    return low, high, warm, solver.evaluations - before, "flow budget" if stopped else None


def controls():
    """Recompute bonds by enumerating actual allowed assignments and every projection."""
    original = [[0, 4], [0, 1, 5], [1, 2, 6], [2, 3, 7], [3, 8]]
    fixtures = {
        "path": original,
        "binary connection": original + [[5, 7, 9]],
        "three meetings": [[0, 2, 3], [0, 1, 4], [1, 2, 5]],
    }
    result = {}
    for name, stars in fixtures.items():
        wire = Wiring(stars)
        _, states, bonds = literal_states_distances(stars)
        kernel = PairPartitions(wire, len(wire.edge), monotonic() + 15)
        tally = Counter()
        for k in (2, 3, 4):
            for marks in combinations(wire.edge, k):
                expected = min((len(cut) for cut in bonds if set(marks) <= set(cut)), default=INFINITY)
                got, _, _ = by_partitions(kernel, marks)
                assert got == expected
                tally["infinite" if got == INFINITY else "finite"] += 1
        flow = PinFlow(wire)
        for marks in ((0, 1), (0, 1, 2), (0, 1, 2, 3)):
            got, _, _ = by_partitions(kernel, marks)
            low, high, *_ = by_flows(flow, marks, None, 200)
            assert low == high == got
        result[name] = {"allowed_states": states, "minimal_nonfree_projections": len(bonds), **tally}
    return result


def recoding_control(wire, marks, value):
    """Permute both old and new physical names, moving the scored marks with them."""
    rng = Random(202611190392)
    domains = list(wire.edge)
    names = domains.copy()
    rng.shuffle(names)
    transport = dict(zip(domains, names, strict=True))
    shuffled = [tuple(transport[d] for d in star) for star in wire.stars]
    rng.shuffle(shuffled)
    recoded = Wiring(shuffled)
    kernel = PairPartitions(recoded, len(recoded.edge), monotonic() + 10)
    actual, _, _ = by_partitions(kernel, tuple(sorted(transport[d] for d in marks)))
    assert actual == value
    return actual


def mark_registry(spec, panel):
    path = spec["roles"]["anchors"]
    named = side_sources.marksets(spec, full=panel == "core")
    if panel == "later":
        seams = spec["roles"]["seams"] or [4]
        named = [marks for marks in named
                 if len(marks) >= 3 and min(side_sources.offset(marks, s) for s in seams) <= 2]
        if len(seams) == 1:
            donor = seams[0]
            if donor + 8 < len(path):
                named.append((donor + 4, donor + 8))
            for d in (0, 1, 2, 3, 4):
                for left in (False, True):
                    pair = (donor - d - 3, donor - d - 1) if left else (donor + d, donor + d + 2)
                    if 0 <= pair[0] < pair[1] < len(path):
                        named.append(pair)
    named = set(named)
    derived = {pair for marks in named for pair in combinations(marks, 2)} - named
    query_indices = sorted(named | derived, key=lambda marks: (len(marks), marks))
    registry = [tuple(sorted(path[i] for i in indices)) for indices in query_indices]
    return registry, query_indices, [indices in named for indices in query_indices]


def frame_reader(stars, queries, previous, seconds, flows):
    wire = Wiring(stars)
    deadline = monotonic() + seconds
    choice = dict(previous)
    # Each carried witness is checked on the physical current incidence before
    # it can restrict any minimization. Grouping shares partial tables.
    ceilings = {q: len(wire.witness(mask, q)["distinctions"]) for q, mask in choice.items()}
    groups = {False: [], True: []}
    for q in queries:
        groups[q in choice].append(q)
    all_rows, witnesses, tested_widths = {}, {}, []
    solver = None
    for fitted in (True, False):
        if not groups[fitted]:
            continue
        cost = max(ceilings[q] for q in groups[fitted]) if fitted else len(wire.edge)
        prep_failed = None
        try:
            kernel = PairPartitions(wire, cost, deadline)
            tested_widths.append(kernel.width)
        except partitions.Limit as exception:
            prep_failed = str(exception)
        for query in groups[fitted]:
            mask = choice.get(query)
            problem = prep_failed
            work = 0
            if problem is None:
                try:
                    low, mask, work = by_partitions(kernel, query)
                    high = low
                    method = "separator"
                except partitions.Limit as exception:
                    problem = str(exception)
            if problem is not None:
                if flows and monotonic() < deadline:
                    if solver is None:
                        solver = PinFlow(wire)
                    low, high, mask, work, cap = by_flows(solver, query, mask, flows)
                    method = "integer flows"
                    problem = None if cap is None else problem + "; " + cap
                else:
                    low, high = len(query), ceilings.get(query, INFINITY)
                    method = "carried witness" if mask is not None else "mark count"
            ix = None
            if mask is not None:
                if mask not in witnesses:
                    witnesses[mask] = len(witnesses), wire.witness(mask, query, high)
                ix, _ = witnesses[mask]
                choice[query] = mask
            all_rows[query] = [low, high, ix, method, problem, work]
    results = [all_rows[q] for q in queries]
    summary = Counter("infinite" if low == high == INFINITY else
                      "finite" if low == high else "bounded"
                      for low, high, *_ in results)
    return ({"knots": wire.n, "distinctions": len(wire.edge), "tested_widths": tested_widths,
             "readings": results, "coverage": dict(summary),
             "witnesses": [w for _, w in witnesses.values()]}, choice)


def comparisons(frames, named, indices):
    quiet_code = next(k for k, trace in frames.items() if not trace["active_source_knots"])
    quiet = frames[quiet_code]["frames"]
    result = {}
    for code, trace in frames.items():
        if code == quiet_code:
            continue
        by_age = {}
        for age, reading in trace["frames"].items():
            if age not in quiet:
                continue
            counts = {k: Counter() for k in (2, 3, 4)}
            witnessed_changes = []
            for i, (is_named, q, l) in enumerate(zip(named, quiet[age]["readings"], reading["readings"], strict=True)):
                if not is_named:
                    continue
                qlo, qhi = q[:2]
                llo, lhi = l[:2]
                if qlo == qhi == llo == lhi:
                    outcome = "equal_infinity" if qlo == INFINITY else "equal_finite"
                elif qhi != INFINITY and (llo == INFINITY or qhi < llo):
                    outcome = "larger"
                elif lhi != INFINITY and (qlo == INFINITY or lhi < qlo):
                    outcome = "smaller"
                else:
                    outcome = "unresolved"
                counts[len(indices[i])][outcome] += 1
                if outcome in ("smaller", "larger"):
                    witnessed_changes.append([i, qlo, qhi, llo, lhi, outcome])
            by_age[age] = {"by_arity": {k: dict(x) for k, x in counts.items()},
                           "strict_comparisons": witnessed_changes}
        result[code] = by_age
    return result


def run_case(spec, panel, through, seconds, flows):
    q, indices, named = mark_registry(spec, panel)
    arms = side_sources.loads(spec)
    original = side_sources.growth.predecessor().source_stars(spec)
    source_sets = tuple(map(frozenset, original))
    same_activity = {}
    assignments = {}
    source_result = None
    recoding = None
    traces = {}
    for code, load in arms.items():
        active = tuple(v for v, star in enumerate(source_sets) if not star.isdisjoint(load))
        if active in same_activity:
            assignments[code] = {"activity": same_activity[active], "occupied": sorted(load)}
            continue
        same_activity[active] = code
        assignments[code] = {"activity": code, "occupied": sorted(load)}
        try:
            iterator = side_sources.generate(spec, load, max_age=through, caps=side_sources.CAPS)
            ages = {}
            previous = {}
            while True:
                age, frame = next(iterator)
                if age == 0:
                    if source_result is None:
                        source_result, source_witnesses = frame_reader(frame["stars"], q, {}, seconds, flows)
                        for marks, (a, b, *_) in zip(q, source_result["readings"], strict=True):
                            if len(marks) > 2:
                                assert a == b == INFINITY
                    row, previous = source_result, source_witnesses
                else:
                    if not active:
                        assert not frame["occupied"]
                    row, previous = frame_reader(frame["stars"], q, previous, seconds, flows)
                    for earlier, later in zip(ages[str(age - 1)]["readings"], row["readings"], strict=True):
                        if earlier[1] != INFINITY and later[1] != INFINITY:
                            assert later[1] <= earlier[1]
                ages[str(age)] = row
                print(spec["id"], code, age, row["coverage"], row["tested_widths"], flush=True)
                if spec["id"] == "J1" and panel == "core" and age == 1 and recoding is None:
                    path = spec["roles"]["anchors"]
                    control = ((8, 12), (4, 5, 6), (4, 5, 6, 7))
                    wire = Wiring(frame["stars"])
                    recoding = {str(keys): recoding_control(wire, tuple(path[i] for i in keys),
                                                           row["readings"][indices.index(keys)][0])
                                for keys in control}
        except StopIteration as stop:
            traces[code] = {"active_source_knots": list(active), "frames": ages, "termination": stop.value}
    return {"query_indices": indices, "physical_distinctions": q, "primary_mark_sets": named,
            "activity_traces": traces, "assignments": assignments, "recoding": recoding,
            "against_quiet": comparisons(traces, named, indices)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--panel", choices=("core", "translated", "later"), default="core")
    parser.add_argument("--cases", nargs="+", choices=PANEL_CASES)
    parser.add_argument("--through", type=int)
    parser.add_argument("--seconds", type=int, default=95)
    parser.add_argument("--width", type=int, choices=range(1, WIDTH_LIMIT + 1), default=WIDTH_LIMIT)
    parser.add_argument("--flows", type=int, default=0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cores = ("J1",)
    cases = args.cases or (cores if args.panel != "translated" else PANEL_CASES)
    if args.through is None:
        args.through = {"core": 2, "translated": 1, "later": 6}[args.panel]
    if args.flows and args.flows < 16:
        parser.error("A flow fallback budget includes up to sixteen initial orientations.")
    outfile = args.out or OUTPUT / ("common_bonds_" + args.panel + ".json")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    partitions.WIDTH_LIMIT = args.width
    partitions.WORK_LIMIT = WORK_LIMIT
    result = {"schema": 1, "measurement": "least physical bond size containing every marked distinction",
              "pair_conversion": "subtract one from a finite size",
              "unit": "count of distinct physical distinctions", "columns": COLUMNS,
              "inputs_sha256": sha256((HERE / "inputs.json").read_bytes()).hexdigest(),
              "limits": {"width": args.width, "transitions_per_query": WORK_LIMIT,
                         "seconds_per_frame": args.seconds, "flows_per_fallback": args.flows},
              "panel": args.panel, "requested_through": args.through,
              "controls": controls(), "cases": {}}
    available = side_sources.cases()
    for code in cases:
        result["cases"][code] = run_case(available[code], args.panel,
                                         min(args.through, side_sources.AGES[code]),
                                         args.seconds, args.flows)
        outfile.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
