"""Bounded exact compilation of NAE satisfiability under selected units.

The free selector ``2*v+1`` chooses value zero for distinction v, and
``2*v+2`` chooses value one.  Every other variable in ``clauses`` is a
Tseitin circuit variable.  ``root`` is true exactly when the original NAE
pattern has a state extending the selected units.  No constraint on the
root, or on selector consistency, is added here.

``root`` and ``presence[v]`` are signed DIMACS literals, except that root
may be the Python constant True or False.  Test ``type(root) is bool``
before treating it as an integer literal.  ``presence[v]`` represents the
OR of the two selectors for v and may also be a signed literal.

Width and gate limits are execution fallbacks, not approximate answers.
An unavailable compilation supplies no clauses or root for querying.
Importing this module starts no run and writes no files.
"""

import heapq


class _GateLimit(Exception):
    pass


def _negate(value):
    return not value if type(value) is bool else -value


class _Circuit:
    def __init__(self, selector_count, gate_limit):
        self.top_id = selector_count
        self.gate_limit = gate_limit
        self.gate_count = 0
        self.clauses = []
        self.interned = {}

    def conjunction(self, inputs):
        return self._gate("and", inputs)

    def disjunction(self, inputs):
        return self._gate("or", inputs)

    def _gate(self, operator, inputs):
        identity = operator == "and"
        absorber = not identity
        literals = set()
        for value in inputs:
            if type(value) is bool:
                if value is absorber:
                    return absorber
                continue
            if -value in literals:
                return absorber
            literals.add(value)
        if not literals:
            return identity
        if len(literals) == 1:
            return next(iter(literals))
        ordered = tuple(sorted(literals))
        key = (operator, ordered)
        if key in self.interned:
            return self.interned[key]
        dual = ("or" if operator == "and" else "and",
                tuple(sorted(-literal for literal in ordered)))
        if dual in self.interned:
            return -self.interned[dual]
        if self.gate_count >= self.gate_limit:
            raise _GateLimit("gate limit would be exceeded")
        self.top_id += 1
        output = self.top_id
        self.gate_count += 1
        self.interned[key] = output
        if operator == "and":
            self.clauses.extend([[-output, literal] for literal in ordered])
            self.clauses.append([output] + [-literal for literal in ordered])
        else:
            self.clauses.extend([[output, -literal] for literal in ordered])
            self.clauses.append([-output] + list(ordered))
        return output


def _pattern_rows(K, nvars):
    rows = set()
    for row in K:
        triple = tuple(sorted(int(value) for value in row))
        if len(triple) != 3 or len(set(triple)) != 3:
            raise ValueError("each NAE knot must have three distinct variable ids")
        if triple[0] < 0 or triple[-1] >= nvars:
            raise ValueError("NAE variable outside range(nvars)")
        rows.add(triple)
    return tuple(sorted(rows))


def _elimination_order(rows, nvars, width_limit, check=lambda: None):
    """Deterministic minimum-degree ordering with clique fill and a cap."""
    adjacent = [set() for _ in range(nvars)]
    for a, b, c in rows:
        adjacent[a].update((b, c))
        adjacent[b].update((a, c))
        adjacent[c].update((a, b))
    heap = [(len(neighbors), variable) for variable, neighbors in enumerate(adjacent)]
    heapq.heapify(heap)
    active = bytearray(b"\x01") * nvars
    order = []
    width = 0
    while heap:
        check()
        degree, variable = heapq.heappop(heap)
        if not active[variable] or degree != len(adjacent[variable]):
            continue
        width = max(width, degree)
        if degree > width_limit:
            return order, width, False
        neighbors = tuple(sorted(adjacent[variable]))
        order.append((variable, neighbors))
        active[variable] = 0
        for index, first in enumerate(neighbors):
            adjacent[first].remove(variable)
            for second in neighbors[index + 1:]:
                adjacent[first].add(second)
                adjacent[second].add(first)
        adjacent[variable].clear()
        for neighbor in neighbors:
            heapq.heappush(heap, (len(adjacent[neighbor]), neighbor))
    if len(order) != nvars:
        raise AssertionError("elimination order omitted a variable")
    return order, width, True


class CompiledPattern:
    """Compile an exact root circuit when min-degree width and gates fit.

    Public fields are ``available``, ``reason``, ``clauses``, ``root``,
    ``top_id``, ``presence`` and ``stats``.  Selector ids remain stable even
    for unused distinctions.  Width counts a variable's remaining neighbors,
    so width w creates at most 2**w entries in its elimination table.
    """

    def __init__(self, K, nvars, width_limit=7, gate_limit=500000, check=None):
        self._check = check or (lambda: None)
        self._check()
        self.nvars = int(nvars)
        self.width_limit = int(width_limit)
        self.gate_limit = int(gate_limit)
        if self.nvars < 0 or self.width_limit < 0 or self.gate_limit < 0:
            raise ValueError("nvars, width_limit and gate_limit must be nonnegative")
        rows = _pattern_rows(K, self.nvars)
        self.available = False
        self.reason = None
        self.clauses = []
        self.root = None
        self.top_id = 2 * self.nvars
        self.presence = []
        self.order = ()
        self.width = 0
        self.table_entries = 0
        self.gate_count = 0
        self.stats = {"nvars": self.nvars, "knots": len(rows),
                      "width_limit": self.width_limit, "gate_limit": self.gate_limit,
                      "selector_count": 2 * self.nvars,
                      "width": 0, "ordering_complete": False,
                      "variables_ordered": 0, "variables_compiled": 0,
                      "initial_table_entries": 2 * self.nvars + 8 * len(rows),
                      "elimination_table_entries": 0, "table_entries": 0,
                      "gate_count": 0, "clause_count": 0,
                      "max_bucket_factors": 0}
        order, self.width, complete = _elimination_order(rows, self.nvars, self.width_limit, self._check)
        self.order = tuple(variable for variable, _ in order)
        self.stats.update(width=self.width, ordering_complete=complete,
                          variables_ordered=len(order))
        if not complete:
            self.reason = f"min-degree width {self.width} exceeds width_limit {self.width_limit}"
            return
        circuit = _Circuit(2 * self.nvars, self.gate_limit)
        self.table_entries = self.stats["initial_table_entries"]
        try:
            root = self._compile(rows, order, circuit)
            presence = [circuit.disjunction((2 * variable + 1, 2 * variable + 2))
                        for variable in range(self.nvars)]
        except _GateLimit:
            self.reason = f"gate_limit {self.gate_limit} reached before compilation completed"
            self._record_circuit_stats(circuit)
            return
        self.available = True
        self.root = root
        self.presence = presence
        self.clauses = circuit.clauses
        self.top_id = circuit.top_id
        self._record_circuit_stats(circuit)

    def _record_circuit_stats(self, circuit):
        self.gate_count = circuit.gate_count
        self.stats.update(table_entries=self.table_entries, gate_count=self.gate_count,
                          clause_count=len(circuit.clauses))

    def _compile(self, rows, order, circuit):
        ranks = {variable: rank for rank, (variable, _) in enumerate(order)}
        buckets = [[] for _ in range(self.nvars)]
        nae = tuple(assignment not in (0, 7) for assignment in range(8))
        for scope in rows:
            buckets[min(scope, key=ranks.__getitem__)].append((scope, nae))
        for variable in range(self.nvars):
            # x=0 is allowed unless its opposite selector chose x=1;
            # x=1 is allowed unless its opposite selector chose x=0.
            unary = (-(2 * variable + 2), -(2 * variable + 1))
            buckets[variable].append(((variable,), unary))
        scalar_factors = []
        for variable, neighbors in order:
            self._check()
            factors = buckets[variable]
            buckets[variable] = []
            self.stats["max_bucket_factors"] = max(self.stats["max_bucket_factors"], len(factors))
            positions = {neighbor: position for position, neighbor in enumerate(neighbors)}
            entries = 1 << len(neighbors)
            lookups = []
            for scope, values in factors:
                variable_bit = 1 << scope.index(variable)
                mapping = [(position, positions[item]) for position, item in enumerate(scope)
                           if item != variable]
                indices = []
                for assignment in range(entries):
                    index = 0
                    for old_position, new_position in mapping:
                        index |= ((assignment >> new_position) & 1) << old_position
                    indices.append(index)
                lookups.append((values, variable_bit, indices))
            output = []
            for assignment in range(entries):
                zero = circuit.conjunction(values[indices[assignment]]
                                           for values, _, indices in lookups)
                one = circuit.conjunction(values[indices[assignment] | variable_bit]
                                          for values, variable_bit, indices in lookups)
                output.append(circuit.disjunction((zero, one)))
            self.table_entries += entries
            self.stats["elimination_table_entries"] += entries
            self.stats["variables_compiled"] += 1
            if neighbors:
                next_variable = min(neighbors, key=ranks.__getitem__)
                buckets[next_variable].append((neighbors, tuple(output)))
            else:
                scalar_factors.append(output[0])
        return circuit.conjunction(scalar_factors)
