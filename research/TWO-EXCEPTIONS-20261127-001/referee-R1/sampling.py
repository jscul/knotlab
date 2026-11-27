"""Redraw the two start weightings and check N1–N3 on independently built cores.

The sampled unit is one labeled draw from WEIGHTINGS-20261119-001B. Admission
uses Lemma R and the late-views piece count. The primary observables are class
counts among completed cores and separate counts of cap crossings. A cap
crossing leaves later ranks unexamined. The controls use earlier witnessed
starts and direct subset checks on small synthetic parent rosters.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import json
import math
from pathlib import Path
import random
import resource
import time


ROOT = Path(__file__).resolve().parents[3]
KNOT_COUNTS = tuple(range(7, 12))
WEIGHTINGS = ("grow", "tree+")


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def as_mask(indices):
    return sum(1 << index for index in indices)


def adjacent_rosters(width, holders):
    neighbours = [0] * width
    for roster in set(holders):
        if roster.bit_count() < 2:
            continue
        for member in members(roster):
            neighbours[member] |= roster ^ (1 << member)
    return neighbours


def maximal_families(neighbours, eligible):
    """List maximal pairwise-sharing families, including singletons."""
    stack = [(0, eligible, 0)]
    while stack:
        chosen, possible, excluded = stack.pop()
        if all(not (possible & ~(neighbours[i] | (1 << i))) for i in members(possible)):
            if not any(not (possible & ~neighbours[i]) for i in members(excluded)):
                yield chosen | possible
            continue
        pivot = max(members(possible | excluded), key=lambda i: (possible & neighbours[i]).bit_count())
        for i in members(possible & ~neighbours[pivot]):
            bit = 1 << i
            stack.append((chosen | bit, possible & neighbours[i], excluded & neighbours[i]))
            possible ^= bit
            excluded |= bit


def group_roster(width, holders, remaining=None, pair_cap=None):
    """Apply Lemma R, with the two count guards from the earlier weighted study."""
    if not width:
        return (), None, {}
    incidences = sum(math.comb(roster.bit_count(), 2) for roster in holders)
    detail = {"parent_pair_incidences": incidences}
    if pair_cap is not None and incidences > pair_cap:
        return (), "parent-pair cap", detail

    neighbours = adjacent_rosters(width, holders)
    holders = set(holders)
    covered = [0] * width
    groups = []
    candidates = 0
    for candidate in maximal_families(neighbours, (1 << width) - 1):
        candidates += 1
        if remaining is not None and candidates > remaining:
            detail["maximal_families_lower_bound"] = candidates
            return (), "maximal-family cap", detail
        # A maximal family with a common holder equals that holder's roster.
        if candidate.bit_count() >= 3 and candidate not in holders:
            groups.append(candidate)
            for i in members(candidate):
                covered[i] |= candidate

    detail["maximal_families"] = candidates
    pairs = [neighbours[i] & ~covered[i] & ~((1 << (i + 1)) - 1) for i in range(width)]
    detail["next_births"] = len(groups) + sum(later.bit_count() for later in pairs)
    if remaining is not None and detail["next_births"] > remaining:
        return (), "birth cap", detail
    groups.extend((1 << i) | (1 << j) for i, later in enumerate(pairs) for j in members(later))
    return tuple(sorted(groups)), None, detail


def create_stars(sizes, shares):
    stars = [[] for _ in sizes]
    for distinction, (a, b) in enumerate(shares):
        stars[a].append(distinction)
        stars[b].append(distinction)
    distinction = len(shares)
    for star, size in zip(stars, sizes):
        stop = distinction + size - len(star)
        star.extend(range(distinction, stop))
        distinction = stop
    return stars


def draw_start(weighting, n, rng):
    if weighting == "grow":
        sizes = [rng.choice((3, 4, 5))]
        loose = sizes.copy()
        shares = []
        for new in range(1, n):
            sizes.append(rng.choice((3, 4, 5)))
            loose.append(sizes[-1])
            held = [i for i in range(new) if loose[i]]
            count = 2 if rng.random() < 1 / 3 else 1
            for _ in range(min(count, len(held))):
                old = rng.choices(held, [loose[i] for i in held])[0]
                held.remove(old)
                loose[old] -= 1
                loose[new] -= 1
                shares.append((old, new))
        return create_stars(sizes, shares)

    code = [rng.randrange(n) for _ in range(n - 2)]
    degree = [1 + code.count(i) for i in range(n)]
    shares = []
    for holder in code:
        leaf = degree.index(1)
        shares.append(tuple(sorted((holder, leaf))))
        degree[leaf] = 0
        degree[holder] -= 1
    shares.append(tuple(i for i, value in enumerate(degree) if value == 1))
    drawn = set(shares)
    other_pairs = [pair for pair in combinations(range(n), 2) if pair not in drawn]
    extras = 0
    product = rng.random()
    while product > math.exp(-1):
        extras += 1
        product *= rng.random()
    shares.extend(rng.sample(other_pairs, min(extras, len(other_pairs))))

    neighbours = [0] * n
    for a, b in shares:
        neighbours[a] |= 1 << b
        neighbours[b] |= 1 << a
    groups, _, _ = group_roster(n, neighbours)
    demand = Counter(i for group in groups for i in members(group))
    sizes = [max(3, neighbours[i].bit_count() + demand[i]) for i in range(n)]
    return create_stars(sizes, shares)


@dataclass(frozen=True, slots=True)
class Node:
    parents: int
    bases: int


@dataclass(frozen=True, slots=True)
class Piece:
    live: tuple
    first: tuple
    chain_bases: tuple
    cycle: bool


def read_start(stars):
    owners = defaultdict(list)
    for knot, star in enumerate(stars):
        if len(star) < 3 or len(star) != len(set(star)):
            raise ValueError("Each start knot needs at least three distinct places")
        for distinction in star:
            owners[distinction].append(knot)
    neighbours = [0] * len(stars)
    loose_distinctions = [[] for _ in stars]
    for distinction, holds in owners.items():
        if len(holds) == 1:
            loose_distinctions[holds[0]].append(distinction)
        elif len(holds) == 2:
            a, b = holds
            neighbours[a] |= 1 << b
            neighbours[b] |= 1 << a
        else:
            raise ValueError("A distinction has more than two holders")
    loose = list(map(len, loose_distinctions))
    live = as_mask(i for i, count in enumerate(loose) if count)
    if not live:
        return "no loose distinction", 0, ()

    raw = set(nb & live for nb in neighbours)
    groups, _, _ = group_roster(len(stars), raw)
    demand = Counter(i for group in groups for i in members(group))
    if any(demand[i] > loose[i] for i in members(live)):
        return "shortage", sum(loose), ()

    cells = {group for group in groups if group.bit_count() >= 3}
    blocks = {block for block in raw if block.bit_count() >= 2
              and not any(block != bigger and block & bigger == block for bigger in raw)
              and not any(block & cell == block for cell in cells)}
    connections = adjacent_rosters(len(stars), blocks | cells)
    pieces = []
    while live:
        component = 0
        pending = live & -live
        while pending:
            bit = pending & -pending
            component |= bit
            pending = (pending | connections[bit.bit_length() - 1]) & ~component
        live &= ~component
        knots = tuple(members(component))
        local = {k: i for i, k in enumerate(knots)}
        piece_blocks = [block for block in blocks if block & component]
        piece_cells = [cell for cell in cells if cell & component]
        incidences = 1 - len(knots) + sum(mask.bit_count() - 1 for mask in piece_blocks + piece_cells)
        filled = sum(max(0, (block & cell).bit_count() - 1)
                     for block in piece_blocks for cell in piece_cells)

        first = [Node(as_mask(local[k] for k in members(group)), 0) for group in groups if group & component]
        bases = []
        for k in knots:
            for distinction in loose_distinctions[k][demand[k]:]:
                base = 1 << len(bases) if loose[k] < 3 else 0
                first.append(Node(1 << local[k], base))
                if base:
                    bases.append((distinction, 3 - loose[k]))
        pieces.append(Piece(knots, tuple(first), tuple(bases), incidences != filled))
    return "admitted", sum(loose), tuple(pieces)


def holder_rosters(current, earlier_width):
    rosters = [0] * earlier_width
    for i, node in enumerate(current):
        for parent in members(node.parents):
            rosters[parent] |= 1 << i
    return rosters


def check_twins_and_lifts(rank, current, earlier, grandparents, failures):
    """N1 indexes reused pairs of parents. N2 tests their full base overlap."""
    basis_holders = as_mask(i for i, node in enumerate(earlier) if node.bases)
    if basis_holders.bit_count() < 2:
        return
    chained_grandparents = as_mask(i for i, node in enumerate(grandparents) if node.bases)
    twins = {}
    for child, node in enumerate(current):
        if "N1" in failures and "N2" in failures:
            return
        for a, b in combinations(members(node.parents & basis_holders), 2):
            parents = (a, b)
            needed = earlier[a].bases & earlier[b].bases
            if not needed:
                continue
            common = earlier[a].parents & earlier[b].parents
            chained = common & chained_grandparents
            if "N1" not in failures and chained:
                if parents in twins:
                    witness = next(members(chained))
                    failures["N1"] = {"rank": rank, "nodes": [twins[parents], child],
                                      "parents": parents, "grandparent": witness,
                                      "bases": list(members(grandparents[witness].bases))}
                twins[parents] = child
            if "N2" not in failures and not any(grandparents[i].bases & needed == needed for i in members(common)):
                failures["N2"] = {"rank": rank, "node": child, "parents": parents,
                                  "bases": list(members(needed)),
                                  "grandparent_bases": {i: list(members(grandparents[i].bases)) for i in members(common)}}


def n3_witness(earlier, holders, width, children):
    """Test each distinct parent filter induced by one or more required bases."""
    available = defaultdict(int)
    for i, (parent, roster) in enumerate(zip(earlier, holders)):
        if roster.bit_count() >= 2:
            for base in members(parent.bases):
                available[base] |= 1 << i

    patterns = {}
    for base, containing in available.items():
        if containing.bit_count() < 2:
            continue
        intersections = {mask & containing: bases | (1 << base) for mask, bases in patterns.items()
                         if (mask & containing).bit_count() >= 2}
        patterns.update(intersections)
        patterns[containing] = 1 << base
    for eligible, bases in patterns.items():
        if not any((holders[i] & holders[j]).bit_count() >= 2
                   for i in members(eligible) for j, roster in enumerate(holders)
                   if i != j and roster.bit_count() >= 2):
            # Each eligible pair has a unique ordinary parent. A family with a
            # common ordinary parent therefore passes. Otherwise it extends to
            # an ordinary group without a common parent, giving a common child.
            continue
        rosters = {holders[i] for i in members(eligible)}
        neighbours = adjacent_rosters(width, rosters)
        universe = as_mask(i for i, nb in enumerate(neighbours) if nb.bit_count() >= 2)
        for family in maximal_families(neighbours, universe):
            if family.bit_count() >= 3 and family not in rosters and not any(family & child == family for child in children):
                return {"family": list(members(family)), "parents_holding_bases": list(members(eligible)),
                        "bases": list(members(bases))}
    return None


def core_check(piece, node_cap, pair_cap, rank_cap):
    widths = [len(piece.live)]
    live = tuple(Node(0, 0) for _ in piece.live)
    grandparents, earlier, current = (), live, piece.first
    failures = {}
    total = len(live)
    while current:
        rank = len(widths)
        widths.append(len(current))
        total += len(current)
        if piece.chain_bases:
            check_twins_and_lifts(rank, current, earlier, grandparents, failures)
        if total > node_cap:
            reason, detail = "birth cap", {"core_nodes": total}
            break
        if rank_cap and rank >= rank_cap:
            reason, detail = "rank cap", {"current_rank": rank}
            break
        holders = holder_rosters(current, len(earlier))
        children, reason, detail = group_roster(len(current), holders, node_cap - total, pair_cap)
        if reason:
            break
        if piece.chain_bases and "N3" not in failures:
            witness = n3_witness(earlier, holders, len(current), children)
            if witness:
                failures["N3"] = {"rank": rank, **witness}
        if not children:
            break
        next_nodes = []
        for family in children:
            bases = 0
            for parent in members(family):
                bases |= current[parent].bases
            next_nodes.append(Node(family, bases))
        grandparents, earlier, current = earlier, current, next_nodes
    else:
        reason, detail = None, {}
    return {"status": reason or "finished", "ranks": widths, "cap_detail": detail if reason else {},
            "witnesses": failures, "live": piece.live, "chain_bases": piece.chain_bases}


def start_check(stars, node_cap, pair_cap, rank_cap, domain, law):
    status, loose, pieces = read_start(stars)
    if status != "admitted":
        return status, None, loose, []
    if law == "parity" and loose == 1:
        return "one loose distinction under parity", None, loose, []
    portion = "has a cycle piece" if any(piece.cycle for piece in pieces) else "tree pieces only"
    if domain == "tree" and portion == "has a cycle piece":
        return "cycle piece outside scope", portion, loose, []
    status, results = check_pieces(pieces, (node_cap, pair_cap, rank_cap))
    return status, portion, loose, results


def check_pieces(pieces, limits):
    results = []
    for piece in pieces:
        result = core_check(piece, *limits)
        results.append(result)
        if result["status"] != "finished":
            return result["status"], results
    return "finished", results


def failure_mask(results):
    return sorted({name for piece in results for name in piece["witnesses"]})


def subset_n3(earlier, current, children):
    """Exhaust nonempty base sets and subsets of the rank for the small controls."""
    base_universe = 0
    for parent in earlier:
        base_universe |= parent.bases
    required = base_universe
    while required:
        eligible = as_mask(i for i, parent in enumerate(earlier) if parent.bases & required == required)
        for count in range(3, len(current) + 1):
            for family in combinations(range(len(current)), count):
                if not all(current[a].parents & current[b].parents & eligible for a, b in combinations(family, 2)):
                    continue
                common = eligible
                for i in family:
                    common &= current[i].parents
                mask = as_mask(family)
                # Failure persists on extending a family, so maximality is immaterial here.
                if not common and not any(child & mask == mask for child in children):
                    return True
        required = (required - 1) & base_universe
    return False


def run_controls():
    rng = random.Random(99271)
    n3_checks = 0
    positive_controls = 0
    for _ in range(240):
        width = rng.randint(2, 8)
        earlier = [Node(0, rng.randrange(8)) for _ in range(rng.randint(2, 7))]
        current = [Node(rng.randrange(1, 1 << len(earlier)), 0) for _ in range(width)]
        holders = holder_rosters(current, len(earlier))
        children, reason, _ = group_roster(width, holders)
        assert reason is None
        observed = bool(n3_witness(earlier, holders, width, children))
        assert observed == subset_n3(earlier, current, children)
        n3_checks += 1
        positive_controls += observed

    report = {"N3 small rank comparisons": n3_checks, "N3 small rank failures": positive_controls}
    earlier = (ROOT / "research" / "CHAIN-COUNT-20261127-001" / "referee-R1" / "witness.json")
    witness = json.loads(earlier.read_text())["two_bases"]
    status, _, _, results = start_check(witness["stars"], 5000, 250000, 0, "all", "nae")
    failures = sorted({name for p in results for name in p["witnesses"]})
    assert status == "finished" and failures == ["N2"]
    assert results[0]["ranks"] == witness["rank_sizes"][:-1]
    report["earlier multibase control"] = {"start_knots": len(witness["stars"]), **results[0]}
    return report


def sample(cell, args, exception_rows, capped_rows):
    weighting, knots = cell
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    rng = random.Random(args.seed)
    counts = defaultdict(Counter)
    cap_examples = 0
    for draw in range(args.draws):
        stars = draw_start(weighting, knots, rng)
        status, portion, loose, result = start_check(stars, args.node_cap, args.pair_cap,
                                                    args.rank_cap, args.domain, args.law)
        failures = sorted({name for piece in result for name in piece["witnesses"]})
        category = "+".join(failures) if status == "finished" and failures else status
        counts["all draws"][category] += 1
        if portion:
            counts[portion][category] += 1
        if result:
            counts["admitted draws"][category] += 1
        if status == "finished" and any(piece["chain_bases"] for piece in result):
            counts["finished with chains"][category] += 1
        if failures or (result and status != "finished" and cap_examples < args.retain_caps):
            row = {"weighting": weighting, "knots": knots, "seed": args.seed, "draw": draw, "stars": stars,
                   "loose": loose, "piece_type": portion, "status": status, "failures": failures, "pieces": result}
            if status == "finished":
                exception_rows.append(row)
            else:
                capped_rows.append(row)
                cap_examples += 1
    return {"weighting": weighting, "knots": knots, "seed": args.seed, "draws": args.draws,
            "counts": counts, "cap_rows_retained": cap_examples,
            "wall_seconds": time.perf_counter() - wall_start, "cpu_seconds": time.process_time() - cpu_start}


def fingerprint(stars):
    import networkx as nx

    ownership = {}
    multiplicity = Counter()
    graph = nx.Graph()
    for i, star in enumerate(stars):
        graph.add_node(i, p=str(len(star)))
        for distinction in star:
            if distinction in ownership:
                multiplicity[ownership[distinction], i] += 1
            else:
                ownership[distinction] = i
    graph.add_edges_from((i, j, {"m": str(count)}) for (i, j), count in multiplicity.items())
    return nx.weisfeiler_lehman_graph_hash(graph, node_attr="p", edge_attr="m", iterations=4)


def closing_category(status, failures, pieces):
    if status == "rank cap":
        return "core does not finish by rank 25"
    if status != "finished":
        return "core over the cap"
    for name, category in (("N1", "fails N1 (chained twins)"), ("N2", "fails N2 only (lifts do not meet)"),
                           ("N3", "fails N3 only")):
        if name in failures:
            return category
    return "in the class, with chains" if any(piece.chain_bases for piece in pieces) else "in the class, no chains"


def read_core_outcome(pieces, limits):
    status, outcomes = check_pieces(pieces, limits)
    failures = failure_mask(outcomes)
    category = closing_category(status, failures, pieces)
    if status == "rank cap" and limits[2] != 25:
        category = f"core does not finish by rank {limits[2]}"
    return {"category": category, "stop": status, "checked_failures": failures, "pieces": outcomes}


def raise_guards(pieces, baseline, limits):
    node_cap, pair_cap, rank_cap = limits
    stop = baseline["stop"]
    raised = (2 * node_cap, 2 * pair_cap, 2 * rank_cap)
    if stop == "rank cap":
        first = (node_cap, pair_cap, raised[2])
    elif stop == "parent-pair cap":
        first = (node_cap, raised[1], rank_cap)
    else:
        first = (raised[0], pair_cap, rank_cap)
    single = read_core_outcome(pieces, first)
    # If only the changed bound still stops the same piece, changing unused
    # bounds cannot reach a further rank. A different piece may stop for
    # the same named reason and need the full replay for its own prefix.
    single_stop = single["stop"]
    same_bound = (single_stop == stop or first[0] != node_cap and single_stop in {"maximal-family cap", "birth cap"})
    same_piece = len(single["pieces"]) == len(baseline["pieces"])
    combined = single if single_stop == "finished" or (same_bound and same_piece) else read_core_outcome(pieces, raised)
    return {"first_guard_raised": single, "all_guards_raised": combined}


def record_counts(counters, outcome):
    counters["categories"][outcome["category"]] += 1
    counters["stopping reasons"][outcome["stop"]] += 1
    names = "+".join(outcome["checked_failures"]) or "none"
    if outcome["stop"] == "finished":
        counters["finished failure sets"][names] += 1
    else:
        counters["capped prefix failure sets"][names] += 1


def replay(cell, args, exception_rows, capped_rows):
    weighting, knots = cell
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    rng = random.Random(args.seed)
    limits = (args.node_cap, args.pair_cap, args.rank_cap)
    repeated = defaultdict(Counter)
    distinct = defaultdict(Counter)
    prefix = {mode: defaultdict(Counter) for mode in ("with repeats", "distinct")}
    census = {}
    for draw in range(args.draws):
        stars = draw_start(weighting, knots, rng)
        status, loose, pieces = read_start(stars)
        if status != "admitted":
            repeated["categories"]["not accepted"] += 1
            continue
        key = fingerprint(stars)
        first = key not in census
        if first:
            outcome = read_core_outcome(pieces, limits)
            record_counts(distinct, outcome)
            piece_type = "has a cycle piece" if any(piece.cycle for piece in pieces) else "tree pieces only"
            row = {"weighting": weighting, "knots": knots, "seed": args.seed, "draw": draw, "stars": stars,
                   "loose": loose, "piece_type": piece_type, "status": outcome["stop"],
                   "failures": outcome["checked_failures"], "pieces": outcome["pieces"]}
            raised = {}
            if outcome["stop"] == "finished" and outcome["checked_failures"]:
                exception_rows.append(row)
                if outcome["checked_failures"] == ["N2"]:
                    print("N2-only", json.dumps(row), flush=True)
            elif draw < args.challenge_prefix and outcome["stop"] != "finished":
                raised = raise_guards(pieces, outcome, limits)
                capped_rows.append({**row, **raised})
            census[key] = (outcome, raised, piece_type)
        outcome, raised, piece_type = census[key]
        record_counts(repeated, outcome)
        repeated[piece_type][outcome["category"]] += 1
        if first:
            distinct[piece_type][outcome["category"]] += 1
        if draw < args.challenge_prefix:
            modes = [prefix["with repeats"]]
            if first:
                modes.append(prefix["distinct"])
            for tally in modes:
                tally["baseline"][outcome["category"]] += 1
                tally["first guard raised"][raised.get("first_guard_raised", outcome)["category"]] += 1
                tally["all guards raised"][raised.get("all_guards_raised", outcome)["category"]] += 1
                if not raised:
                    continue
                for name, result in raised.items():
                    tally[name + " transitions"][f"{outcome['stop']} -> {result['stop']}"] += 1
                    known = set(outcome["checked_failures"])
                    discovered = "+".join(sorted(set(result["checked_failures"]) - known)) or "none"
                    tally[name + " newly witnessed failures"][discovered] += 1

    measured = {"accepted draws with repeats": repeated["categories"], "distinct accepted starts": distinct["categories"]}
    published_file = ROOT / "research" / "TWO-EXCEPTIONS-20261127-001" / "counts" / f"{weighting}_{knots}.json"
    recorded = json.loads(published_file.read_text())
    matches_settings = (recorded["draws"] == args.draws and recorded["seed"] == args.seed and limits == (5000, 250000, 25))
    deltas = {}
    if matches_settings:
        for key, tally in measured.items():
            reference = Counter(recorded[key])
            deltas[key] = {category: tally[category] - reference[category] for category in tally.keys() | reference.keys()
                           if tally[category] != reference[category]}
    seconds = time.process_time() - cpu_start
    print(weighting, knots, dict(repeated["categories"]), round(seconds, 3), "CPU seconds", flush=True)
    return {"weighting": weighting, "knots": knots, "seed": args.seed, "draws": args.draws,
            "repeated": repeated, "distinct": distinct,
            "study_matches_settings": matches_settings, "differences_from_study": deltas,
            "prefix_draws": min(args.challenge_prefix, args.draws), "cap_challenge": prefix,
            "wall_seconds": time.perf_counter() - wall_start, "cpu_seconds": seconds}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weighting", action="append", choices=WEIGHTINGS)
    parser.add_argument("--knots", type=int, nargs="+", choices=KNOT_COUNTS, default=KNOT_COUNTS)
    parser.add_argument("--seed", type=int, default=27112709)
    parser.add_argument("--draws", type=int, required=True)
    parser.add_argument("--domain", choices=("all", "tree"), default="all")
    parser.add_argument("--law", choices=("nae", "parity"), default="nae")
    parser.add_argument("--node-cap", type=int, default=5000)
    parser.add_argument("--pair-cap", type=int, default=250000)
    parser.add_argument("--rank-cap", type=int, default=0)
    parser.add_argument("--retain-caps", type=int, default=12)
    parser.add_argument("--published", action="store_true", help="Use the published fingerprint and class labels")
    parser.add_argument("--challenge-prefix", type=int, default=0, help="Raise limits on a prefix of the published replay")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.draws < 0 or args.node_cap < 1 or args.pair_cap < 1 or args.rank_cap < 0:
        parser.error("Require nonnegative draws and rank cap, and positive node and pair caps")
    if args.published and (args.domain != "all" or args.law != "nae" or args.rank_cap != 25):
        parser.error("The published replay uses all pieces, not-all-equal admission and rank 25")
    if args.challenge_prefix < 0 or (args.challenge_prefix and not args.published):
        parser.error("Set a nonnegative challenge prefix for a published replay")
    if args.output.exists():
        parser.error("Choose a fresh output path")

    memory = 2 * 1024**3
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (memory if hard < 0 else min(memory, hard), hard))
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    controls = run_controls() if args.check else {}
    exceptions, caps = [], []
    draw_cell = replay if args.published else sample
    cells = [draw_cell((weighting, knots), args, exceptions, caps)
             for weighting in args.weighting or WEIGHTINGS for knots in args.knots]
    output = {"weighting unit": "One count per draw, including repeats",
              "domain": args.domain, "law": args.law,
              "caps": {"all_core_nodes_per_piece": args.node_cap, "parent_pair_incidences_per_rank": args.pair_cap,
                       "rank": args.rank_cap or None},
              "controls": controls, "cells": cells, "exceptions": exceptions, "capped_examples": caps,
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "cpu_seconds": time.process_time() - cpu_start, "wall_seconds": time.perf_counter() - wall_start}
    if args.challenge_prefix:
        output["cap challenge"] = "On the given prefix, double the first bound a start reaches. Then double all three bounds."
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    if not args.published:
        for cell in cells:
            print(cell["weighting"], cell["knots"], dict(cell["counts"]["all draws"]), round(cell["cpu_seconds"], 3))
    print(len(exceptions), "exception rows", len(caps), "cap rows retained",
          round(output["cpu_seconds"], 3), "CPU seconds", output["peak_rss_kib"], "KiB peak RSS")


if __name__ == "__main__":
    main()
