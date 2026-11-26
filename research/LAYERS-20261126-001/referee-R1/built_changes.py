"""Ordinary parity growth, shortest changes, and single-knot observations for built starts.

Set bits refer throughout to the original integer distinction names. This file reads
no study output or prior implementation. The shortlist of inputs is in built_search.py.
"""
from collections import Counter, defaultdict, deque
from itertools import combinations

import networkx as nx


def places(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def bits(indices):
    return sum(1 << i for i in indices)


def odd(mask):
    return mask.bit_count() % 2


class Span:
    def __init__(self, rows=()):
        self.rows = {}
        for row in rows:
            self.add(row)

    def remainder(self, row):
        while row:
            top = row.bit_length() - 1
            if top not in self.rows:
                break
            row ^= self.rows[top]
        return row

    def add(self, row):
        row = self.remainder(row)
        if row:
            self.rows[row.bit_length() - 1] = row
            return True
        return False

    def orthogonal(self, support):
        """Free-coordinate generators of the annihilator within support."""
        assert all(row & ~support == 0 for row in self.rows.values())
        ordered = sorted(self.rows.items())
        for coordinate in places(support & ~bits(self.rows)):
            word = 1 << coordinate
            for top, equation in ordered:
                if odd(word & equation):
                    word |= 1 << top
            yield word

    def __len__(self):
        return len(self.rows)


def incidences(knots):
    holders = defaultdict(list)
    for i, row in enumerate(knots):
        assert len(set(row)) == len(row)
        for x in row:
            holders[x].append(i)
    assert all(0 < len(h) <= 2 for h in holders.values())
    return holders


def groups(witness_sets):
    """Maximal pairwise-meeting groups unwitnessed as a whole, then uncovered pairs."""
    witness_sets = {frozenset(row) for row in witness_sets if len(row) >= 2}
    together = nx.Graph()
    for row in witness_sets:
        together.add_edges_from(combinations(sorted(row), 2))
    many = sorted(
        tuple(sorted(c)) for c in nx.find_cliques(together)
        if len(c) >= 3 and all(not set(c) <= row for row in witness_sets)
    )
    covered = {pair for group in many for pair in combinations(group, 2)}
    pairs = sorted(tuple(sorted(pair)) for pair in together.edges if tuple(sorted(pair)) not in covered)
    return many + pairs


def partners(holders, n):
    rows = [set() for _ in range(n)]
    for h in holders.values():
        if len(h) == 2:
            a, b = h
            rows[a].add(b)
            rows[b].add(a)
    return rows


def advance(knots):
    n = len(knots)
    holders = incidences(knots)
    available = [[x for x in row if len(holders[x]) == 1] for row in knots]
    live = {k for k, row in enumerate(available) if row}
    groups_now = groups([row & live for row in partners(holders, n)])
    owes = Counter(i for g in groups_now for i in g)
    if not live or any(owes[k] > len(available[k]) for k in live):
        return None, "no loose distinctions" if not live else "insufficient loose distinctions"
    rosters = list(groups_now)
    for k in sorted(live):
        rosters.extend([(k,)] * (len(available[k]) - owes[k]))
    children = [[] for _ in range(n)]
    new_knots = []
    for k, parents in enumerate(rosters):
        new_knots.append(tuple(available[p][len(children[p])] for p in parents))
        for p in parents:
            children[p].append(k)
    future = Counter(k for group in groups(children) for k in group)
    old_laws = Span(bits(row) for row in knots)
    fresh = max(holders) + 1
    born = []
    for k, row in enumerate(new_knots):
        count = future[k]
        if old_laws.remainder(bits(row)):
            count = max(count, 1, 3 - len(row))
        born.append(row + tuple(range(fresh, fresh + count)))
        fresh += count
    return tuple(knots) + tuple(born), None


def shortest_changes(knots):
    """Every shortest allowed change through each distinction, with all ties."""
    holders = incidences(knots)
    n = len(knots)
    lists = [[] for _ in range(n + 1)]
    for e, h in holders.items():
        a, b = h[0], h[-1] if len(h) == 2 else n
        lists[a].append((b, e))
        lists[b].append((a, e))
    moves = set()
    lengths, ties = {}, {}
    for e, h in holders.items():
        a, b = h[0], h[-1] if len(h) == 2 else n
        levels = {a: 0}
        todo = deque([a])
        while todo and b not in levels:
            u = todo.popleft()
            for v, d in lists[u]:
                if d != e and v not in levels:
                    levels[v] = levels[u] + 1
                    todo.append(v)
        if b not in levels:
            lengths[e], ties[e] = None, 0
            continue
        # Finish discovery at all levels that can precede b. The first b is
        # found while expanding level dist(b)-1, after all that level is known.
        stack = [(b, 1 << e)]
        number = 0
        while stack:
            u, partial = stack.pop()
            if u == a:
                number += 1
                moves.add(partial)
            else:
                stack.extend((v, partial | (1 << d)) for v, d in lists[u]
                             if d != e and levels.get(v, -2) == levels[u] - 1)
        lengths[e], ties[e] = levels[b] + 1, number
    laws = [bits(row) for row in knots]
    assert all(all(not odd(move & row) for row in laws) for move in moves)
    return moves, lengths, ties


def read(knots, named, *, certificate=False):
    holders = incidences(knots)
    active = bits(holders)
    laws = [bits(row) for row in knots]
    moves, lengths, ties = shortest_changes(knots)
    move_basis = Span(moves)
    law_basis = Span(laws)
    allowed = list(law_basis.orthogonal(active))
    assert all(law_basis.remainder(row) == 0 for row in laws)
    assert len(allowed) == len(holders) - len(law_basis)
    assert all(not odd(z & row) for z in allowed for row in laws)
    single_knots = Span(laws)
    annihilators = []
    local_dims = []
    knot_pass = []
    observable_pair_gains = []
    for row in laws:
        knot_pass.append(len(Span(z & row for z in allowed)) == row.bit_count() - 1)
        observed = Span(m & row for m in move_basis.rows.values())
        functions = list(observed.orthogonal(row))
        local = Span(laws)
        for f in functions:
            single_knots.add(f)
            local.add(f)
        annihilators.append(functions)
        local_dims.append(len(local) - len(law_basis))
        if certificate:
            # Joint new information in the named reads after fixing all places
            # of this holder. For linear states the rank is independent of the
            # chosen compatible observation. This also tests nonlinear readers.
            fitted = Span(laws + [1 << x for x in places(row)])
            before = len(fitted)
            for f in named:
                fitted.add(f)
            observable_pair_gains.append(len(fitted) - before)
    class_bits = len(allowed) - len(move_basis)
    local_bits = len(single_knots) - len(law_basis)
    label_status = []
    named_independent = Span(single_knots.rows.values())
    local_span = Span(single_knots.rows.values())
    for label in named:
        even = all(not odd(label & m) for m in moves)
        variable = any(odd(label & z) for z in allowed)
        independent = named_independent.add(label) if even and variable else False
        label_status.append([even, variable, independent])
    sums = []
    for k in range(1, 1 << len(named)):
        label = 0
        for i in places(k):
            label ^= named[i]
        if all(not odd(label & m) for m in moves) and any(odd(label & z) for z in allowed):
            sums.append({"members": list(places(k)), "outside_span_of_local_reads": bool(local_span.remainder(label))})
    back = {
        "knots": len(knots), "distinctions": len(holders), "class_bits": class_bits,
        "allowed_rank": len(allowed), "move_rank": len(move_basis), "distinct_shortest_changes": len(moves),
        "shortest_sizes": dict(sorted(Counter(lengths.values()).items(), key=lambda pair: str(pair[0]))),
        "greatest_shortest_tie_count": max(ties.values(), default=0),
        "local_span_rank_modulo_laws": local_bits, "whole_held_rank": class_bits - local_bits,
        "individual_knot_ranks": dict(sorted(Counter(local_dims).items())),
        "holders_passing_k1_k2_k3": sum(knot_pass),
        "named_even_variable_independent_modulo_local": label_status, "named_sums_that_are_labels": sums
    }
    def observed_rank(changes):
        return len(Span(bits(i for i, f in enumerate(named) if odd(z & f)) for z in changes))
    back["named_value_rank_on_states"] = observed_rank(allowed)
    back["named_change_rank_on_shortest_moves"] = observed_rank(move_basis.rows.values())
    if certificate:
        # All allowed changes that preserve *each* individual-knot class read.
        no_local_change = list(single_knots.orthogonal(active))
        pairings = [bits(i for i, f in enumerate(named) if odd(z & f)) for z in no_local_change]
        exchanges = []
        for i in range(len(named)):
            target = 1 << i
            pivot = {}
            for coords, z in zip(pairings, no_local_change):
                while coords and coords.bit_length() in pivot:
                    c, old = pivot[coords.bit_length()]
                    coords ^= c
                    z ^= old
                if coords:
                    pivot[coords.bit_length()] = (coords, z)
            z = 0
            residual = target
            while residual and residual.bit_length() in pivot:
                c, old = pivot[residual.bit_length()]
                residual ^= c
                z ^= old
            if residual:
                exchanges.append(None)
            else:
                assert all(not odd(z & f) for fs in annihilators for f in fs)
                assert all(not odd(z & row) for row in laws)
                assert bits(i for i, f in enumerate(named) if odd(z & f)) == target
                exchanges.append(list(places(z)))
        back["certificate"] = {
            "stage_in_distinction_order": knots, "named_supports": [list(places(z)) for z in named],
            "all_shortest_changes": [list(places(m)) for m in sorted(moves)],
            "all_shortest_sizes_by_distinction": lengths, "all_tie_counts_by_distinction": ties,
            "single_holder_annihilator_bases": [[list(places(f)) for f in fs] for fs in annihilators],
            "single_holder_class_ranks": local_dims,
            "all_knot_test_flags": knot_pass,
            "named_value_ranks_after_fixing_one_holder": observable_pair_gains,
            "exchanges_fixing_every_single_holder_class_read": exchanges,
            "named_pairing_with_exchanges": [
                [odd(label & bits(ex)) if ex is not None else None for ex in exchanges] for label in named
            ]
        }
    return back


def ring(start, n):
    return [(start + j, start + (j + 1) % n) for j in range(n)]


def assemble(count, meetings, loose):
    rows = [[] for _ in range(count)]
    for i, (a, b) in enumerate(meetings):
        assert a != b
        rows[a].append(i)
        rows[b].append(i)
    d = len(meetings)
    for k, h in enumerate(loose):
        rows[k].extend(range(d, d + h))
        d += h
    return tuple(tuple(row) for row in rows)


def first_funding(count, meetings, live):
    together = [set() for _ in range(count)]
    for a, b in meetings:
        together[a].add(b)
        together[b].add(a)
    return Counter(v for g in groups([row & live for row in together]) for v in g)


def linked_rings(n, m, inner, multiplicity, live_join, pairs=None, inner_bypass=False):
    """Two rings, an explicit sequence of shared meetings, and a funding choice."""
    old_count = n + m
    routes = pairs if pairs is not None else [(0, n)]
    meetings = ring(0, n) + ring(n, m)
    next_knot = old_count
    for a, b in routes:
        route = [a] + list(range(next_knot, next_knot + inner)) + [b]
        extra = []
        for p, q in zip(route, route[1:]):
            meetings.extend([(p, q)] * multiplicity)
            if inner_bypass:
                # Two extra knots at each meeting, with every pair among the
                # four knotted except the meeting already inserted.
                c, d = next_knot + inner + len(extra), next_knot + inner + len(extra) + 1
                extra.extend((c, d))
                meetings.extend([(p, c), (p, d), (q, c), (q, d), (c, d)])
        next_knot += inner + len(extra)
    assert nx.is_connected(nx.Graph(meetings))
    live = set(range(next_knot)) if live_join else set(range(old_count))
    demand = first_funding(next_knot, meetings, live)
    loose = [max(2, demand[i]) if i in live else 0 for i in range(next_knot)]
    starts = assemble(next_knot, meetings, loose)
    assert min(map(len, starts)) >= 3
    return starts, [bits(range(n)), bits(range(n, n + m))], loose
