"""Search for an additional first failure using prescribed groups and one chain."""
import argparse
from collections import Counter
from itertools import combinations, islice
import json
from pathlib import Path
import signal
from time import process_time

import networkx as nx

from rebuild import Reading, families, first_failure


def cells_with_one_offshoot(graph, root):
    """Each pair of joined groups shares its own live knot."""
    cells = [set() for _ in graph]
    next_knot = 0
    for a, b in sorted(graph.edges):
        cells[a].add(next_knot)
        cells[b].add(next_knot)
        next_knot += 1
    for common in graph.graph.get("shared_groups", ()):
        for x in common:
            cells[x].add(next_knot)
        next_knot += 1
    marked = None
    for i, cell in enumerate(cells):
        if i == root:
            marked = next_knot
        fresh = max(1, 3 - len(cell))
        cell.update(range(next_knot, next_knot + fresh))
        next_knot += fresh
    return cells, marked


def realize(cells, marked):
    """Make exactly these initial groups and one funded offshoot."""
    meetings = nx.Graph()
    cells = {frozenset(cell) for cell in cells}
    for cell in cells:
        meetings.add_edges_from(combinations(sorted(cell), 2))
    witnesses = {frozenset(pair) for pair in meetings.edges}
    for group in nx.find_cliques(meetings):
        group = frozenset(group)
        if len(group) >= 3 and group not in cells:
            witnesses.add(group)
    n = max(meetings) + 1
    stars = [[] for _ in range(n + len(witnesses))]
    identity = 0
    for x in range(n):
        loose = sum(x in cell for cell in cells) + int(x == marked)
        for _ in range(loose):
            stars[x].append(identity)
            identity += 1
    for j, witness in enumerate(sorted(witnesses, key=lambda v: tuple(sorted(v))), n):
        for x in sorted(witness):
            stars[x].append(identity)
            stars[j].append(identity)
            identity += 1
    for j in range(n, len(stars)):
        k = j + 1 if j + 1 < len(stars) else n
        stars[j].append(identity)
        stars[k].append(identity)
        identity += 1
    assert all(len(star) >= 3 and len(set(star)) == len(star) for star in stars)
    return stars


def pair_shares_mark(x, y, parents, marked):
    return bool(parents[x] & parents[y] & marked)


def finish(cells, mark, rank_cap, width_cap):
    now = [frozenset(cell) for cell in cells] + [frozenset({mark})]
    widths = [len(now)]
    for _ in range(rank_cap):
        if not now:
            return "finished", widths
        if len(now) > width_cap:
            return "width_cut", widths
        now = sorted(families(dict(enumerate(now))), key=lambda g: tuple(sorted(g)))
        widths.append(len(now))
    return ("finished" if not now else "rank_cut"), widths


def first_obstruction(cells, mark, rank_cap, width_cap):
    # Parent incidence of the prescribed first rank agrees with realize().
    now = {i: frozenset(cell) for i, cell in enumerate(cells)}
    offshoot = len(now)
    now[offshoot] = frozenset({mark})
    marked = {offshoot}
    previous_marked = set()
    widths = []
    for rank in range(1, rank_cap + 1):
        n = len(now)
        widths.append(n)
        if n <= 1:
            return "finished", widths, None
        if n > width_cap:
            return "width_cut", widths, None
        groups = sorted(families(now), key=lambda x: tuple(sorted(x)))
        after = dict(enumerate(groups))
        next_marked = {x for x, ps in after.items() if ps & marked}

        # Every N1 witness with these two upper members has all of their
        # common children as eligible pure members of the same mixed family.
        common_children = Counter(pair for ps in groups for pair in combinations(sorted(ps & marked), 2))
        bad_pairs = {pair for pair, count in common_children.items()
                     if count >= 2 and pair_shares_mark(*pair, now, previous_marked)}
        first_split = []
        if rank >= 2:
            for child, ps in after.items():
                lifts = ps & marked
                missed = [pair for pair in combinations(sorted(lifts), 2)
                          if not pair_shares_mark(*pair, now, previous_marked)]
                if missed:
                    sharing = nx.Graph()
                    sharing.add_nodes_from(lifts)
                    sharing.add_edges_from(set(combinations(sorted(lifts), 2)) - set(missed))
                    pieces = sorted(map(len, nx.find_cliques(sharing)))
                    first_split.append(dict(child=child, lifts=len(lifts), missed=len(missed),
                                            maximal_lifts=pieces))

        # All three obstructions tested here would first be visible when
        # the members being compared have total rank + 1.
        if rank >= 2 and len(marked) >= 3:
            eligible = {x: now[x] & previous_marked for x in marked}
            for group in families(eligible):
                if len(group) >= 3 and not any(group <= ps for ps in groups):
                    return "one_vector", widths, {"member_rank": rank + 1, "family": sorted(group)}
        if bad_pairs or first_split:
            multiplicity = max((common_children[pair] for pair in bad_pairs), default=0)
            upper = 0
            for ca, cb in combinations(next_marked, 2):
                together = after[ca] & after[cb] & marked
                if len(together) <= max(2, upper):
                    continue
                choices = nx.Graph()
                choices.add_nodes_from(together)
                choices.add_edges_from(p for p in combinations(sorted(together), 2)
                                       if pair_shares_mark(*p, now, previous_marked))
                upper = max(upper, max(map(len, nx.find_cliques(choices))))
            return "first_N1_N2", widths, {
                "member_rank": rank + 1, "largest_lower": multiplicity,
                "largest_upper_over_two": upper if upper > 2 else 0,
                "failed_lifts": first_split,
            }
        previous_marked, now, marked = marked, after, next_marked
    return "rank_cut", widths, None


def designs(max_nodes):
    for i, graph in enumerate(nx.graph_atlas_g()):
        if len(graph) not in range(2, max_nodes + 1) or not nx.is_connected(graph):
            continue
        for root in graph:
            yield i, graph, root


def branch_variants():
    # Two marked positions connected through several further groups; grow
    # independent unmarked continuations from the two ends of this pattern.
    for count in range(2, 8):
        for left_len in range(4):
            for right_len in range(left_len, 5):
                graph = nx.Graph()
                graph.add_edge(0, 1)
                for j in range(2, 2 + count):
                    graph.add_edges_from(((0, j), (1, j)))
                for home, length in ((0, left_len), (1, right_len)):
                    current = home
                    for _ in range(length):
                        new = len(graph)
                        graph.add_edge(current, new)
                        current = new
                for root in graph:
                    yield [count, left_len, right_len], graph, root


def extended_variants():
    # Start at the six-group pattern having a finished three-lift split.
    # Append each possible nonempty set of attachments at two successive steps.
    graph = nx.graph_atlas_g()[120]
    for first in range(1, 1 << len(graph)):
        base = graph.copy()
        base.add_edges_from((k, 6) for k in graph if (first >> k) & 1)
        for second in range(1, 1 << len(base)):
            case = base.copy()
            case.add_edges_from((k, 7) for k in base if (second >> k) & 1)
            for root in (3, 4, 6, 7):
                yield [first, second], case, root


def overlapping_variants(max_nodes):
    # Give a chosen set of mutually meeting groups an additional common live
    # knot. This suppresses that group in the next round and changes which
    # pairs are uncovered, while retaining the original pair incidences.
    for i, graph in enumerate(nx.graph_atlas_g()):
        if len(graph) not in range(3, max_nodes + 1) or not nx.is_connected(graph):
            continue
        eligible = sorted(sorted(g) for g in nx.find_cliques(graph) if len(g) >= 3)
        for bits in range(1, 1 << len(eligible)):
            graph.graph["shared_groups"] = [g for j, g in enumerate(eligible) if (bits >> j) & 1]
            for root in graph:
                yield [i, bits], graph, root


def stress_completion(cells, mark):
    def stop(*_):
        raise TimeoutError
    saved = signal.signal(signal.SIGPROF, stop)
    signal.setitimer(signal.ITIMER_PROF, 0.30)
    try:
        return finish(cells, mark, 25, 512)
    except TimeoutError:
        return "stress_cut", []
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, saved)


def tied_pieces(pilot):
    graph = nx.graph_atlas_g()[120]
    cells, mark = cells_with_one_offshoot(graph, 3)
    split = realize(cells, mark)
    source = Path(__file__).resolve().parents[2] / "CYCLE-READ-20261127-001" / "twin9_draw.jsonl"
    twin = next(row["stars"] for row in map(json.loads, source.read_text().splitlines()) if row["draw"] == 194)
    offset = 1 + max(d for row in split for d in row)
    whole = [row.copy() for row in split] + [[offset + d for d in row] for row in twin]
    spent_counts = Counter(d for row in split for d in row)
    spent = [i for i, star in enumerate(split) if all(spent_counts[d] == 2 for d in star)]
    new_ids = 1 + max(d for row in whole for d in row)
    attached = [spent[0], spent[1], len(split)]
    for j, i in enumerate(attached):
        whole[i].append(new_ids + j)
    whole.append(list(range(new_ids, new_ids + len(attached))))
    held = {}
    for i, star in enumerate(whole):
        for d in star:
            held.setdefault(d, []).append(i)
    assert min(map(len, whole)) >= 3 and max(map(len, held.values())) == 2
    connectivity = nx.Graph()
    connectivity.add_nodes_from(range(len(whole)))
    connectivity.add_edges_from(owners for owners in held.values() if len(owners) == 2)
    assert nx.is_connected(connectivity)
    cases = [("twins", twin), ("split", split), ("together", whole)]
    results = {kind: first_failure(stars, 9) for kind, stars in (cases[:1] if pilot else cases)}
    if not pilot:
        assert {r["child_round"] for r in results.values()} == {8}
        both = results["together"]
        assert both["twins"] == results["twins"]["twins"] and both["splits"] == results["split"]["splits"]
    sizes = []
    core = Reading(whole)
    meetings = nx.Graph()
    meetings.add_nodes_from(core.ranks[0])
    for x in core.ranks[1]:
        meetings.add_edges_from(combinations(core.parents[x], 2))
    for component in nx.connected_components(meetings):
        sizes.append(len(component))
    all_widths = [len(core.ranks[-1])]
    while core.ranks[-1]:
        core.next_rank()
        all_widths.append(len(core.ranks[-1]))
    return dict(knots=len(whole), twins_source="CYCLE-READ-20261127-001/twin9_draw.jsonl",
                twins_draw=194, split_source={"case":120,"marked_group":3}, attachment=attached,
                connected=True, live_knots_by_piece=sorted(sizes), rank_widths=all_widths,
                stars=whole, checks=results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--design", choices=("atlas", "branches", "extended", "overlap", "tie"), default="atlas")
    parser.add_argument("--max-nodes", type=int, default=7)
    parser.add_argument("--rank-cap", type=int, default=12)
    parser.add_argument("--width-cap", type=int, default=26)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    tally = Counter()
    examples = {}
    begin = process_time()
    if args.design == "tie":
        result = tied_pieces(args.limit == 0)
        result["cpu_seconds"] = round(process_time()-begin, 5)
        print(json.dumps({k: result[k] for k in ("knots", "live_knots_by_piece", "cpu_seconds")}))
        if args.output:
            args.output.write_text(json.dumps(result, indent=2) + "\n")
        return
    cases = {"atlas": lambda: designs(args.max_nodes), "branches": branch_variants,
             "extended": extended_variants, "overlap": lambda: overlapping_variants(args.max_nodes)}[args.design]()
    for i, graph, root in islice(cases, args.limit):
        tally["cases"] += 1
        cells, mark = cells_with_one_offshoot(graph, root)
        tag, widths, indicator = first_obstruction(cells, mark, args.rank_cap, args.width_cap)
        tally[tag] += 1
        if tag not in {"one_vector", "first_N1_N2"}:
            continue
        if tag == "one_vector":
            kinds = [tag]
        else:
            kinds = []
            if indicator["largest_lower"] > 2:
                kinds.append("three_or_more_lower")
            if indicator["largest_upper_over_two"]:
                kinds.append("three_or_more_upper")
            if indicator["failed_lifts"]:
                kinds.append("one_chain_split")
                if max(row["lifts"] for row in indicator["failed_lifts"]) > 2:
                    kinds.append("three_or_more_lifts")
                if max(len(row["maximal_lifts"]) for row in indicator["failed_lifts"]) > 2:
                    kinds.append("at_least_three_pieces")
        if not kinds:
            continue
        status, all_widths = finish(cells, mark, 25, args.width_cap)
        if status != "finished" and ("one_vector" in kinds or "at_least_three_pieces" in kinds):
            status, all_widths = stress_completion(cells, mark)
        for kind in kinds:
            tally[kind + "_" + status] += 1
            if status == "finished":
                key = kind
            elif kind in {"one_vector", "at_least_three_pieces"}:
                key = "incomplete_" + kind
            else:
                continue
            if key in examples:
                continue
            stars = realize(cells, mark)
            direct = first_failure(stars, horizon=indicator["member_rank"] + 2)
            assert direct["member_round"] == indicator["member_rank"]
            examples[key] = dict(case=i, root=root, groups=list(map(sorted, cells)), mark=mark,
                                 completion=status, rank_widths=all_widths,
                                 static=indicator, stars=stars, direct=direct)
    result = dict(settings={k: v for k, v in vars(args).items() if k != "output"},
                  counts=tally, first=examples, cpu_seconds=round(process_time()-begin, 5))
    print(json.dumps(dict(counts=tally, examples=list(examples), seconds=result["cpu_seconds"])))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
