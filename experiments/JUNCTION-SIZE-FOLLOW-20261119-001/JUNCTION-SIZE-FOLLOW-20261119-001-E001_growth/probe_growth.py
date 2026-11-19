"""Exact compact roster growth with arity and explicit lookahead censorship."""

from collections import Counter
from dataclasses import dataclass
from functools import cache
from itertools import combinations, permutations
from math import comb


def bits(mask):
    while mask:
        one = mask & -mask
        yield one.bit_length() - 1
        mask ^= one


def maximum_blocks(blocks):
    keep = []
    for block in sorted(set(blocks), key=lambda x: (-x.bit_count(), x)):
        if block.bit_count() >= 2 and not any(block & other == block for other in keep):
            keep.append(block)
    return tuple(sorted(keep))


@cache
def small_name(loose, blocks):
    """Canonicalize only a small start, using exact relabelings of every block."""
    order_loose = sorted(loose)
    images = (naming for naming in permutations(range(len(loose)))
              if all(loose[v] == order_loose[i] for v, i in enumerate(naming)))
    return tuple(order_loose), min(tuple(sorted(sum(1 << naming[u] for u in bits(block)) for block in blocks))
                                   for naming in images)


def initial_roster(sizes, links):
    degree = Counter(v for pair in links for v in pair)
    loose = [size - degree[v] for v, size in enumerate(sizes)]
    assert min(loose) >= 0
    live = [v for v, count in enumerate(loose) if count]
    name = {v: i for i, v in enumerate(live)}
    seen = [0] * len(sizes)
    for u, v in links:
        if u in name:
            seen[v] |= 1 << name[u]
        if v in name:
            seen[u] |= 1 << name[v]
    start = tuple(loose[v] for v in live), maximum_blocks(seen)
    return small_name(*start) if len(live) <= 5 else start


def start_metrics(sizes, links):
    degree = Counter(v for pair in links for v in pair)
    return [len(sizes), sum(sizes) - len(links), max(sizes),
            max((size for u, size in enumerate(sizes) if size == degree[u]), default=0)]


@dataclass(frozen=True)
class GroupDeck:
    demand: tuple
    large: tuple
    pairs: tuple
    count: int

    def groups(self):
        yield from self.large
        for u, neighbors in enumerate(self.pairs):
            for v in bits(neighbors >> (u+1)):
                yield (1 << u) | (1 << (v+u+1))


class Unfinished(Exception):
    def __init__(self, gate, lower=None):
        self.gate = gate
        self.lower = lower


def group_deck(points, blocks, clique_limit):
    full = (1 << points) - 1
    if not blocks:
        zeros = (0,) * points
        return GroupDeck(zeros, (), zeros, 0)
    if blocks == (full,):
        neighbors = tuple(full ^ (1 << j) for j in range(points))
        return GroupDeck((points-1,) * points, (), neighbors, comb(points, 2))
    rows = [0] * points
    for block in blocks:
        for u in bits(block):
            rows[u] |= block
    active = 0
    for u, adjacent in enumerate(rows):
        if adjacent:
            rows[u] = adjacent ^ (1 << u)
            active |= 1 << u

    large = []
    covered = [0] * points
    demand = [0] * points
    holders = set(blocks)
    pending = [(0, active, 0)]
    scans = 0
    while pending:
        shore, candidates, used = pending.pop()
        scans += 1
        if scans > clique_limit:
            raise Unfinished("clique_search_cap", len(large))
        if not candidates:
            if not used and shore.bit_count() >= 3 and shore not in holders:
                large.append(shore)
                for u in bits(shore):
                    covered[u] |= shore
                    demand[u] += 1
            continue
        pivot = max(bits(candidates | used), key=lambda u: (rows[u] & candidates).bit_count())
        for v in bits(candidates & ~rows[pivot]):
            one = 1 << v
            pending.append((shore | one, candidates & rows[v], used & rows[v]))
            candidates ^= one
            used |= one
    pairs = tuple(row & ~cover for row, cover in zip(rows, covered, strict=True))
    degrees = [row.bit_count() for row in pairs]
    demand = tuple(a+b for a,b in zip(demand, degrees, strict=True))
    return GroupDeck(demand, tuple(sorted(large)), pairs, len(large) + sum(degrees)//2)


def complete_subsets(state):
    loose, blocks = state
    count = len(loose)
    return count if count >= 3 and blocks == ((1 << count) - 1,) and set(loose) == {count-1} else None


def summary_for(keys, mode, roster_size=None):
    count = sum(amount for _, amount in keys)
    fresh = sum(f*amount for (_, f), amount in keys)
    return {"mode": mode, "births": count, "maximum_born_size": max(p+f for (p, f), amount in keys),
            "maximum_parent_count": max(p for (p, f), amount in keys),
            "maximum_birth_loose_count": max(f for (p, f), amount in keys),
            "maximum_live_size": max((p+f for (p, f), amount in keys if f), default=0),
            "maximum_exhausted_at_birth": max((p for (p, f), amount in keys if not f), default=0),
            "new_distinctions": fresh, "birth_histogram": [[p, f, amount] for (p, f), amount in keys],
            **({"subset_population": roster_size} if roster_size is not None else {})}


def follow(start, depth=24, birth_limit=12000, clique_limit=400000, use_subsets=True):
    """Exact time-indexed birth rows. Incomplete fresh lookahead never yields a reached row."""
    state, deck = start, None
    history = []
    seen = {}
    while len(history) < depth:
        loose, blocks = state
        age = len(history)
        if not loose:
            return {"rows": history, "end": "closed", "last_complete_age": age}
        if state in seen:
            old = seen[state]
            cycle = history[old:]
            for i in range(depth-age):
                history.append(cycle[i % len(cycle)] | {"mode": "periodic_exact_roster"})
            return {"rows": history, "end": "horizon", "last_complete_age": depth,
                    "proven_periodicity": {"start_age": old, "period": len(cycle)}}
        seen[state] = age
        subset_count = complete_subsets(state) if use_subsets else None
        if subset_count:
            for k in range(2, min(subset_count, depth-age+1)+1):
                hist = [((k, subset_count-k), comb(subset_count, k))]
                history.append(summary_for(hist, "single_block_exact", subset_count))
            complete_age = age + subset_count - 1
            return {"rows": history, "end": "closed" if complete_age <= depth else "horizon",
                    "last_complete_age": len(history), "single_block": {"at_age": age, "population": subset_count,
                    "closing_age": complete_age, "all_later_births": (1 << subset_count)-subset_count-1,
                    "all_later_fresh": subset_count * (1 << (subset_count-1)) - subset_count**2}}
        births = max_parent = None
        try:
            if deck is None:
                deck = group_deck(len(loose), blocks, clique_limit)
            if deficits := [(j, d, loose[j]) for j,d in enumerate(deck.demand) if d > loose[j]]:
                return {"rows": history, "end": "demand_stall", "last_complete_age": age, "deficits": deficits}
            remainder = [have-use for have,use in zip(loose, deck.demand, strict=True)]
            births = deck.count + sum(remainder)
            assert births >= 1
            if births > birth_limit:
                raise Unfinished("birth_count_cap", births)
            parents = sorted([*deck.groups(), *(1 << j for j, free in enumerate(remainder) for _ in range(free))])
            assert len(parents) == births
            max_parent = max(p.bit_count() for p in parents)
            if births == 1 and loose == (1,) * len(loose) and parents[0] == (1 << len(loose))-1:
                history.append(summary_for([((max_parent, 0), 1)], "literal_roster"))
                return {"rows": history, "end": "closed", "last_complete_age": age+1}
            holders = [0] * len(loose)
            for child, parent in enumerate(parents):
                for u in bits(parent):
                    holders[u] |= 1 << child
            next_blocks = maximum_blocks(holders)
            deck = group_deck(births, next_blocks, clique_limit)
            open_counts = tuple(max(d, 3-p.bit_count(), 1) for p,d in zip(parents, deck.demand, strict=True))
            keys = sorted(Counter((p.bit_count(), f) for p,f in zip(parents, open_counts, strict=True)).items())
            history.append(summary_for(keys, "literal_roster"))
            state = open_counts, next_blocks
        except Unfinished as limit:
            return {"rows": history, "end": "capped", "last_complete_age": age, "attempted_age": age+1,
                    "cap": {"gate": limit.gate, "lower_count": limit.lower, "proposed_births": births,
                            "known_maximum_parent_count": max_parent}}
    return {"rows": history, "end": "horizon", "last_complete_age": len(history)}


def sizes_by_round(initial, history):
    junctions, distinctions, live_and_exhausted, exhausted = initial
    previous = live_and_exhausted
    yield [junctions, distinctions, live_and_exhausted, exhausted]
    for born in history:
        junctions += born["births"]
        distinctions += born["new_distinctions"]
        exhausted = max(exhausted, previous, born["maximum_exhausted_at_birth"])
        live_and_exhausted = max(exhausted, born["maximum_live_size"])
        previous = born["maximum_live_size"]
        yield [junctions, distinctions, live_and_exhausted, exhausted]
