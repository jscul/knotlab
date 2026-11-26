"""Read forced sums of separate simple-cycle parities on an arbitrary parity stage."""

from collections import defaultdict, deque
from functools import reduce
from operator import or_, xor


def bits(word):
    while word:
        least = word & -word
        yield least.bit_length() - 1
        word ^= least


def mask(values):
    return sum(1 << i for i in values)


def span(words):
    rows = {}
    for word in words:
        while word:
            p = word.bit_length() - 1
            if p not in rows:
                rows[p] = word
                break
            word ^= rows[p]
    return rows


def normal(word, basis):
    remainder = 0
    while word:
        p = word.bit_length() - 1
        if p in basis:
            word ^= basis[p]
        else:
            leading = 1 << p
            remainder |= leading
            word ^= leading
    return remainder


def kernel(equations, names):
    basis = span(equations)
    pivots = sorted(basis.items())
    for i in names:
        if i not in basis:
            word = 1 << i
            for p, row in pivots:
                if (row & word).bit_count() % 2:
                    word ^= 1 << p
            yield word


def words(generators):
    values = [0]
    for generator in generators:
        values.extend([prior ^ generator for prior in values])
    return values


class Incidence:
    def __init__(self, supports):
        self.supports = supports
        self.checks = [mask(support) for support in supports]
        self.laws = span(self.checks)
        self.all_names = reduce(or_, self.checks, 0)
        self.owners = defaultdict(list)
        for knot, row in enumerate(supports):
            assert len(row) == len(set(row))
            for name in row:
                self.owners[name].append(knot)
        self.loose = 0
        self.bundles = defaultdict(list)
        for name, own in self.owners.items():
            assert len(own) in (1, 2)
            if len(own) == 1:
                self.loose |= 1 << name
            endpoints = tuple(own) if len(own) == 2 else (own[0], len(supports))
            self.bundles[endpoints].append(name)

    def forced(self):
        # A sum with knot coefficients x has value XOR of its holders' x at
        # each distinction. Impose evenness at each knot and zero at each loose name.
        conditions = [reduce(xor, (mask(self.owners[d]) for d in row), 0)
                      for row in self.supports]
        conditions.extend(1 << self.owners[d][0] for d in bits(self.loose))
        return tuple(span(reduce(xor, (self.checks[k] for k in bits(choice)), 0)
                          for choice in kernel(conditions, range(len(self.supports)))).values())

    def reader_spaces(self):
        single = {d: normal(1 << d, self.laws) for d in self.owners}
        listed = []
        verified = []
        for row in self.supports:
            readable = span(single[d] for d in row)
            listed.append(readable)
            # The given row is itself the full-support parity equation. Its
            # projection passes K1–K3 iff that is the only equation there.
            if len(row) >= 3 and len(readable) == len(row) - 1:
                verified.append(readable)
        return listed, verified

    def projected_moves(self, keep):
        """Equations for invariance on shortest changes, on the coordinates in keep."""
        adjacency = [[] for _ in range(len(self.supports) + 1)]
        equations = []
        for (a, b), names in self.bundles.items():
            first = names[0]
            adjacency[a].append((b, first))
            adjacency[b].append((a, first))
            # Parallel meetings give every pair as a shortest two-change.
            for other in names[1:]:
                equations.append(((1 << first) ^ (1 << other)) & keep)
        for (a, b), names in self.bundles.items():
            if len(names) > 1:
                continue
            omitted = names[0]
            levels = {a: 0}
            prefix = {a: 0}
            pending = deque([a])
            while pending and b not in levels:
                knot = pending.popleft()
                for other, via in adjacency[knot]:
                    if via != omitted and other not in levels:
                        levels[other] = levels[knot] + 1
                        prefix[other] = prefix[knot] ^ ((1 << via) & keep)
                        pending.append(other)
            if b not in levels:
                continue
            equations.append(prefix[b] ^ ((1 << omitted) & keep))
            pending = [b]
            seen = {b}
            while pending:
                knot = pending.pop()
                for other, via in adjacency[knot]:
                    if via == omitted or levels.get(other, -2) != levels[knot] - 1:
                        continue
                    # A chosen path to each knot fixes a prefix. These changes
                    # generate all differences between shortest returns.
                    equations.append(prefix[knot] ^ ((1 << via) & keep) ^ prefix[other])
                    if other not in seen:
                        seen.add(other)
                        pending.append(other)
        return tuple(span(equations).values())


class SearchLimit(Exception):
    pass


def possible_cycles(stage, union, effort):
    """Every invariant simple cycle within the forced supports is among these."""
    adjacency = defaultdict(dict)
    cycles = []
    for (a, b), names in stage.bundles.items():
        inside = [d for d in names if union & (1 << d)]
        if not inside:
            continue
        assert b < len(stage.supports)
        if len(names) == 1:
            adjacency[a][b] = adjacency[b][a] = 1 << inside[0]
        elif len(names) == len(inside) == 2:
            cycles.append(mask(inside))
        # A label contains all or none of a parallel bundle (two-change).
        # A simple cycle uses both only if these two form its whole support.
    visited_steps = 0
    for root, neighbors in sorted(adjacency.items()):
        for second, start_bit in neighbors.items():
            if second <= root:
                continue
            stack = [(second, (1 << root) | (1 << second), start_bit)]
            while stack:
                here, visited, support = stack.pop()
                visited_steps += 1
                if visited_steps > effort:
                    raise SearchLimit("simple-cycle search")
                for there, bit in adjacency[here].items():
                    if there == root and second < here:
                        cycles.append(support | bit)
                    elif there > root and not (visited & (1 << there)):
                        stack.append((there, visited | (1 << there), support | bit))
    return cycles


def cycle_blocks(stage, union):
    """Separate supports between which a simple cycle cannot pass."""
    adjacency = defaultdict(dict)
    blocks = []
    for (a, b), names in stage.bundles.items():
        present = mask(names) & union
        if not present:
            continue
        if len(names) == 1:
            adjacency[a][b] = adjacency[b][a] = present
        elif len(names) == present.bit_count() == 2:
            blocks.append(present)
    discovery = {}
    lowest = {}
    walked = []

    def visit(knot, parent):
        discovery[knot] = lowest[knot] = len(discovery)
        for other, bit in adjacency[knot].items():
            if other not in discovery:
                walked.append(bit)
                visit(other, knot)
                lowest[knot] = min(lowest[knot], lowest[other])
                if lowest[other] >= discovery[knot]:
                    block = 0
                    while True:
                        last = walked.pop()
                        block |= last
                        if last == bit:
                            break
                    if block.bit_count() >= 3:
                        blocks.append(block)
            elif other != parent and discovery[other] < discovery[knot]:
                walked.append(bit)
                lowest[knot] = min(lowest[knot], discovery[other])

    for knot in adjacency:
        if knot not in discovery:
            visit(knot, None)
    return blocks


def simple(stage, support):
    meetings = defaultdict(list)
    for d in bits(support):
        a, b = stage.owners[d]
        meetings[a].append(b)
        meetings[b].append(a)
    if not meetings or any(len(encounters) != 2 for encounters in meetings.values()):
        return False
    seen = {next(iter(meetings))}
    pending = list(seen)
    while pending:
        knot = pending.pop()
        for other in meetings[knot]:
            if other not in seen:
                seen.add(other)
                pending.append(other)
    return len(seen) == len(meetings)


def invariant_by_blocks(stage, union, effort):
    """Test all cycle parities on each block against the move equations first."""
    moves = stage.projected_moves(union)
    readers = stage.reader_spaces()
    retained = []
    for block in cycle_blocks(stage, union):
        within = list(kernel((w & block for w in (*stage.checks, *moves)), bits(block)))
        values = tuple(span(normal(c, stage.laws) for c in within).values())
        # If one valid knot reads all the values, it reads every cycle here.
        if not values or any(all(not normal(c, reader) for c in values) for reader in readers[1]):
            continue
        if len(values) <= 8 and all(any(not normal(v, reader) for reader in readers[1])
                                    for v in words(values)[1:]):
            continue
        if len(within) <= 15:
            retained.extend(c for c in words(within)[1:] if normal(c, stage.laws) and simple(stage, c))
        else:
            retained.extend(c for c in possible_cycles(stage, block, effort)
                            if normal(c, stage.laws) and all((c & m).bit_count() % 2 == 0 for m in moves))
    return retained, readers


def confined(basis, allowed):
    unwanted = reduce(or_, basis, 0) & ~allowed
    conditions = (mask(i for i, generator in enumerate(basis) if generator & (1 << d))
                  for d in bits(unwanted))
    return [reduce(xor, (basis[i] for i in bits(choice)), 0)
            for choice in kernel(conditions, range(len(basis)))]


def find_splits(candidates, forced, laws, previous, source, effort, cap):
    """Exact-cover test; per-scope positive counts distinguish a redundant sum from a knot."""
    output = {"candidate cycles": len(candidates), "eligible forced dimension": 0,
              "complete": True, "complete splits": 0, "minimal splits": 0,
              "new since start": 0, "new at this growth": 0}
    if len(candidates) < 3:
        return output
    feasible = confined(forced, reduce(or_, candidates, 0))
    output["eligible forced dimension"] = len(feasible)
    if not feasible:
        return output
    if len(feasible) > cap:
        output.update(complete=False, reason="eligible forced dimension cap")
        return output
    by_name = defaultdict(list)
    for cycle in candidates:
        for d in bits(cycle):
            by_name[d].append(cycle)
    signatures = {cycle: normal(cycle, laws) for cycle in candidates}
    steps = 0
    for total in words(feasible)[1:]:
        pending = [(total, ())]
        while pending:
            todo, selected = pending.pop()
            steps += 1
            if steps > effort:
                output.update(complete=False, reason="disjoint-cover search")
                return output
            if todo:
                left = next(bits(todo))
                for cycle in by_name[left]:
                    if cycle & todo == cycle:
                        pending.append((todo ^ cycle, (*selected, cycle)))
            elif len(selected) >= 3:
                output["complete splits"] += 1
                minimal = len(span(signatures[c] for c in selected)) == len(selected) - 1
                source_new = source is not None and bool(normal(total, source.laws))
                previous_new = previous is not None and bool(normal(total, previous.laws))
                kind = "example of redundant split"
                if minimal:
                    output["minimal splits"] += 1
                    output["new since start"] += int(source_new)
                    output["new at this growth"] += int(previous_new)
                    kind = ("example newly forced in last growth" if previous_new else
                            "example since start" if source_new else "example of inherited relation")
                if kind not in output:
                    output[kind] = {"carrier distinctions": [list(bits(c)) for c in selected],
                                    "joint rank": len(span(signatures[c] for c in selected)),
                                    "all carriers use start distinctions": source is None
                                    or not (total & ~source.all_names),
                                    "all carriers use preceding distinctions": previous is None
                                    or not (total & ~previous.all_names)}
    return output


def inspect(stage, previous=None, source=None, *, effort=120000, cap=16, include_carriers=False):
    forced = stage.forced()
    union = reduce(or_, forced, 0)
    previous_gain = 0
    new_forced = 0
    if previous is not None:
        assert not union & ~previous.all_names
        zero_fresh = [row for row in stage.checks[len(previous.checks):]
                      if not row & ~previous.all_names]
        previous_gain = len(span(normal(row, previous.laws) for row in zero_fresh))
        new_forced = len(span(normal(row, previous.laws) for row in forced))
        assert new_forced <= previous_gain
    result = {"knots": len(stage.supports), "distinctions": len(stage.owners),
              "forced dimension": len(forced), "old state rank removed": previous_gain,
              "forced dimension newly added by this growth": new_forced,
              "forced dimension outside start laws": 0 if source is None
              else len(span(normal(row, source.laws) for row in forced))}
    try:
        candidates = possible_cycles(stage, union, effort) if forced else []
    except SearchLimit:
        try:
            invariant, (listed, knots) = invariant_by_blocks(stage, union, effort)
        except SearchLimit as error:
            result.update(complete=False, reason=str(error))
            return result
        result["used independent block constraints on possible label cycles"] = True
    else:
        possible = [c for c in candidates if normal(c, stage.laws)]
        possible_support = reduce(or_, possible, 0)
        moves = stage.projected_moves(possible_support) if possible else ()
        invariant = [c for c in possible if all((c & m).bit_count() % 2 == 0 for m in moves)]
        listed, knots = stage.reader_spaces() if invariant else ([], [])
        result["simple cycles tested after the parallel-meeting screen"] = len(candidates)
    labels = [(c, normal(c, stage.laws)) for c in invariant]
    for name, readers in (("all listed supports", listed), ("only supports passing K1–K3", knots)):
        unread = [c for c, code in labels if all(normal(code, reader) for reader in readers)]
        result[name] = find_splits(unread, forced, stage.laws, previous, source, effort, cap)
        if include_carriers:
            result[name]["all candidate supports"] = [list(bits(c)) for c in sorted(unread)]
    result["complete"] = all(result[k]["complete"] for k in
                             ("all listed supports", "only supports passing K1–K3"))
    return result
