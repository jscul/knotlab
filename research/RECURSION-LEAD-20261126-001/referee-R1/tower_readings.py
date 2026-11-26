"""Exact allowed changes and class readings for the finite parity stages."""

from collections import Counter, deque
from dataclasses import dataclass


class BinarySpan:
    def __init__(self, vectors=()):
        self.pivots = {}
        for vector in vectors:
            self.add(vector)

    def remainder(self, vector):
        residue = 0
        while vector:
            pivot = vector.bit_length() - 1
            row = self.pivots.get(pivot)
            if row is None:
                bit = 1 << pivot
                residue |= bit
                vector ^= bit
            else:
                vector ^= row
        return residue

    def add(self, vector):
        vector = self.remainder(vector)
        if vector:
            self.pivots[vector.bit_length() - 1] = vector
        return bool(vector)

    def __len__(self):
        return len(self.pivots)


def selected_bits(vector):
    while vector:
        bit = vector & -vector
        yield bit
        vector ^= bit


@dataclass
class ParityStage:
    laws: tuple
    incidence: tuple
    neighbors: list
    allowed_basis: list

    @classmethod
    def from_stage(cls, stage):
        names = sorted(set().union(*stage))
        indices = {name: index for index, name in enumerate(names)}
        laws = tuple(sum(1 << indices[name] for name in knot) for knot in stage)
        holders = {name: [] for name in names}
        for knot, distinctions in enumerate(stage):
            for distinction in distinctions:
                holders[distinction].append(knot)

        # Parity at the common endpoint for loose distinctions follows from
        # summing the given laws. The endpoint carries no additional rule.
        loose_endpoint = len(stage)
        neighbors = [[] for _ in range(loose_endpoint + 1)]
        incidence = []
        basis = []
        elimination = {}
        for index, name in enumerate(names):
            ends = holders[name]
            if len(ends) == 1:
                a, b = ends[0], loose_endpoint
            else:
                a, b = ends
            incidence.append((a, b))
            neighbors[a].append((b, index))
            neighbors[b].append((a, index))
            syndrome = (1 << a) | (1 << b)
            change = 1 << index
            while syndrome:
                pivot = syndrome.bit_length() - 1
                if pivot not in elimination:
                    elimination[pivot] = (syndrome, change)
                    break
                known, support = elimination[pivot]
                syndrome ^= known
                change ^= support
            else:
                basis.append(change)
        if len(basis) != len(names) - len(BinarySpan(laws)):
            raise AssertionError("incidence elimination disagrees with the rank of the parity laws")
        return cls(laws, tuple(incidence), neighbors, basis)

    def shortest(self):
        per_distinction = []
        for omitted, (start, target) in enumerate(self.incidence):
            distances = {start: 0}
            predecessors = {start: []}
            pending = deque([start])
            while pending:
                current = pending.popleft()
                depth = distances[current] + 1
                if target in distances and depth > distances[target]:
                    break
                for neighbor, distinction in self.neighbors[current]:
                    if distinction == omitted:
                        continue
                    if neighbor not in distances:
                        distances[neighbor] = depth
                        predecessors[neighbor] = []
                        pending.append(neighbor)
                    if distances[neighbor] == depth:
                        predecessors[neighbor].append((current, 1 << distinction))

            tied = set()
            paths = [(target, 1 << omitted)] if target in distances else []
            while paths:
                current, change = paths.pop()
                if current == start:
                    tied.add(change)
                    continue
                paths.extend((previous, change | bit) for previous, bit in predecessors[current])
            per_distinction.append(tied)
        return per_distinction

    def short_cycles(self):
        """Simple cycles of at most five distinctions, each from its least name."""
        generators = set()
        for least, (start, target) in enumerate(self.incidence):
            paths = [(start, 1 << start, 1 << least, 1)]
            while paths:
                current, visited, change, size = paths.pop()
                for neighbor, distinction in self.neighbors[current]:
                    if distinction <= least:
                        continue
                    if neighbor == target:
                        generators.add(change | (1 << distinction))
                    elif size < 4 and not (visited & (1 << neighbor)):
                        paths.append((neighbor, visited | (1 << neighbor), change | (1 << distinction), size + 1))
        return generators


def label_counts(stage, changes, report_individual):
    moves = BinarySpan(sorted(changes))
    covered = BinarySpan(moves.pivots.values())
    representatives = [change for change in stage.allowed_basis if covered.add(change)]
    label_rank = len(representatives)

    # Project the move span onto each knot. The projected class changes
    # modulo those projected moves give exactly the locally readable labels.
    local_spans = []
    for knot in stage.laws:
        projected_moves = BinarySpan(move & knot for move in moves.pivots.values())
        projections = [projected_moves.remainder(change & knot) for change in representatives]
        local_spans.append(BinarySpan(
            sum(1 << index for index, projection in enumerate(projections) if projection & bit)
            for bit in selected_bits(knot)
        ))
    local_rank = len(BinarySpan(label for span in local_spans for label in span.pivots.values()))
    counts = {
        "classes": 1 << label_rank,
        "labels": label_rank,
        "read by single knots": local_rank,
        "whole-held": label_rank - local_rank,
    }
    diagnostics = {
        "move rank": len(moves),
        "allowed rank": len(stage.allowed_basis),
    }
    if report_individual:
        labels_unreadable_at_each_knot = [
            label for label in range(1, 1 << label_rank)
            if all(span.remainder(label) for span in local_spans)
        ]
        diagnostics["individually unreadable rank"] = len(BinarySpan(labels_unreadable_at_each_knot))
        diagnostics["individually unreadable labels"] = len(labels_unreadable_at_each_knot)
    return counts, diagnostics


def readings(stage, literal=False, report_individual=True):
    system = ParityStage.from_stage(stage)
    tied = system.shortest()
    shortest = set().union(*tied)
    bounded_generators = system.short_cycles()
    bounded_span = BinarySpan(bounded_generators)
    if any(bounded_span.remainder(move) for move in shortest if move.bit_count() <= 5):
        raise AssertionError("a shortest change of at most five is missing from the bounded span")
    data = {}
    extra = {}
    for name, changes in (("SHORT", shortest), ("UPTO5", bounded_generators)):
        data[name], extra[name] = label_counts(system, changes, report_individual)
        extra[name]["generators by size"] = dict(sorted(Counter(move.bit_count() for move in changes).items()))
    extra["maximum shortest ties through one distinction"] = max(map(len, tied), default=0)
    extra["unmoving distinctions under SHORT"] = sum(not changes for changes in tied)
    if literal:
        extra["literal"] = literal_check(system, tied, bounded_generators)
    return data, extra


def literal_check(system, shortest, bounded_generators):
    """Compare each exact tie set and the bounded span with all allowed states."""
    allowed = [0]
    for change in system.allowed_basis:
        allowed += [state ^ change for state in allowed]
    if len(set(allowed)) != len(allowed):
        raise AssertionError("allowed-change basis has a dependence")
    tied = [set() for _ in shortest]
    minimum = [len(shortest) + 1 for _ in shortest]
    bounded = set()
    for change in allowed:
        if any((row & change).bit_count() % 2 for row in system.laws):
            raise AssertionError("a constructed change has odd incidence")
        size = change.bit_count()
        if 0 < size <= 5:
            bounded.add(change)
        for bit in selected_bits(change):
            index = bit.bit_length() - 1
            if size < minimum[index]:
                minimum[index] = size
                tied[index] = set()
            if size == minimum[index]:
                tied[index].add(change)
    if tied != shortest:
        raise AssertionError("the shortest enumeration disagrees with the literal ties")
    if not bounded_generators <= bounded or len(BinarySpan(bounded)) != len(BinarySpan(bounded_generators)):
        raise AssertionError("the bounded generators disagree with literal bounded changes")
    return {
        "allowed assignments": len(allowed),
        "bounded nonzero changes": len(bounded),
        "bounded changes outside the simple generators": len(bounded - bounded_generators),
    }
