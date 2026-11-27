"""Count the two birth readings from the core, using chain-length compositions."""

from collections import Counter
from dataclasses import replace
from itertools import product, repeat
from math import comb

from core import Birth, build_core


def _chain_choices(outlets, budget):
    """Group the choices of named chains at each point by use and length one."""
    options = [
        [
            (point, used, single, comb(count, used) * comb(used, single))
            for used in range(min(count, budget) + 1)
            for single in range(used + 1)
            if 2 * used - single <= budget
        ]
        for point, count in outlets
    ]
    for choice in product(*options):
        used = sum(number for _, number, _, _ in choice)
        long = sum(number - single for _, number, single, _ in choice)
        if used + long > budget:
            continue
        multiplicity = 1
        for _, _, _, count in choice:
            multiplicity *= count
        yield choice, used, long, multiplicity


def _relay_piece(piece, relay_allowed):
    nodes = dict(piece.nodes)
    chains = dict(piece.chains)
    if piece.relay and relay_allowed:
        tip, = piece.ranks[max(piece.ranks)]
        last = nodes[tip]
        new_node = max(nodes) + 1
        outlet = max(piece.points) + 1
        nodes[tip] = replace(last, children=(new_node,))
        nodes[new_node] = Birth(last.rank + 1, (tip,), last.points | {outlet}, ())
        chains[outlet] = 2
    return nodes, chains


def _piece_terms(piece, sizes, rounds, relay_allowed):
    nodes, chains = _relay_piece(piece, relay_allowed)
    outlets = {
        label: [(point, chains[point]) for point in node.points if point in chains]
        for label, node in nodes.items()
    }
    fresh = {
        label: len(node.children) + sum(count for _, count in outlets[label])
        for label, node in nodes.items()
    }

    def sig0(label, used, anchors):
        node = nodes[label]
        if node.rank == 1:
            return ("start", 0, 0, sizes[label])
        parents = used + sum(anchors <= nodes[parent].points for parent in node.parents)
        demand = fresh[label]
        kind = "offshoot" if parents == 1 else "join"
        return (kind, parents, demand, parents + demand)

    for label, node in nodes.items():
        core_round = node.rank - 1
        if not 1 <= core_round <= rounds:
            continue
        for choice, used, long, multiplicity in _chain_choices(
            outlets[label], rounds - core_round
        ):
            anchors = frozenset(point for point, number, _, _ in choice if number)
            own = sig0(label, used, anchors)
            parents = [
                sig0(parent, used, anchors)
                for parent in node.parents
                if anchors <= nodes[parent].points
            ]
            parents.extend(repeat(own, long))
            for point, number, single, _ in choice:
                if single:
                    kept = anchors - {point} if number == 1 else anchors
                    parents.extend(repeat(sig0(label, used - 1, kept), single))
            # Each used chain takes one point and each longer chain one more.
            # The remaining points can be distributed among the longer chains.
            first_round = core_round + used + long
            yield own, own + (tuple(sorted(parents)),), first_round, long, multiplicity


def predict_core(read_core, rounds, knot_law="nae"):
    """Return (rows, 'predicted') or (None, reason) for a core of the same law."""
    if rounds < 0:
        raise ValueError("rounds must be nonnegative")
    if read_core.status != "in":
        return None, read_core.status
    for piece in read_core.pieces:
        if piece.stop not in ("finished", "rank cap"):
            return None, piece.stop
        if piece.finished:
            continue
        if piece.chains:
            return None, "unfinished core with chains"
        # The last read birth needs its children to count fresh distinctions.
        if max(piece.ranks) < rounds + 2:
            return None, "rank cap before final demand"

    counts0 = [Counter() for _ in range(rounds + 1)]
    counts1 = [Counter() for _ in range(rounds + 1)]
    relay_allowed = knot_law == "nae" or len(read_core.pieces) >= 2
    for piece in read_core.pieces:
        for own, with_parents, first, long, multiplicity in _piece_terms(
            piece, read_core.sizes, rounds, relay_allowed
        ):
            last = rounds if long else first
            for round_number in range(first, last + 1):
                count = multiplicity
                if long:
                    count *= comb(round_number - first + long - 1, long - 1)
                counts0[round_number][own] += count
                counts1[round_number][with_parents] += count

    rows = []
    for c0, c1 in zip(counts0[1:], counts1[1:]):
        rows.append({
            "n": sum(c0.values()),
            "sig0": sorted([list(sig), count] for sig, count in c0.items()),
            "sig1": sorted([
                [list(sig[:4]), [list(parent) for parent in sig[4]]], count
            ] for sig, count in c1.items()),
        })
    return rows, "predicted"


def predict(stars, rounds, knot_law="nae", *, cap=5000, max_rank=25):
    """Read the start's two birth-signature multisets at rounds 1 through rounds."""
    read_core = build_core(stars, knot_law, max_rank=max_rank, max_births=cap)
    return predict_core(read_core, rounds, knot_law)
