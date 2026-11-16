"""Paid joint-program checker. The only specification is the pair of public truth tables."""
from itertools import combinations


class JointChecker:
    def __init__(self, n):
        self.n = n
        self.rows = 1 << n
        self.full = (1 << self.rows) - 1
        # Bit x of columns[i] is bit i of assignment x.
        self.columns = tuple(self.full // ((1 << (1 << i)) + 1) << (1 << i) for i in range(n))
        self.zero = tuple(self.full ^ c for c in self.columns)
        self.layouts = {}

    def _essential(self, table):
        return {i for i, lo in enumerate(self.zero) if (table ^ (table >> (1 << i))) & lo}

    def _classes(self, outputs, group, stop_above=None):
        layout = self.layouts.get(group)
        if layout is None:
            mask = self.full
            offsets = [0]
            for i in group:
                mask &= self.zero[i]
                offsets += [v + (1 << i) for v in offsets]
            layout = self.layouts[group] = (mask, offsets)
        mask, offsets = layout
        seen = set()
        for shift in offsets:
            seen.add(tuple((t >> shift) & mask for t in outputs))
            if stop_above is not None and len(seen) > stop_above:
                break
        return len(seen)

    def verify(self, targets, result):
        if result.get("status") != "exact" or result.get("n") != self.n:
            raise ValueError("incomplete synthesis return")
        circuit = result["circuit"]
        if int(circuit.get("n", self.n)) != self.n:
            raise ValueError("circuit input size changed")
        group = tuple(sorted(result["triple"]))
        common = self._essential(targets[0]) & self._essential(targets[1])
        if len(group) != 3 or len(set(group)) != 3 or not set(group) <= common:
            raise ValueError("invalid joint input group")
        actual = self._classes(targets, group)
        bits = (actual - 1).bit_length()
        taps = tuple(result["summary_wires"])
        if result["class_count"] != actual or result["width"] != bits or len(set(taps)) != len(taps) or len(taps) != bits:
            raise ValueError("local code or reported class count is incorrect")
        tried = 0
        # One bit is minimal for any admissible nonconstant group. For a
        # larger code, rule out every strictly narrower group from the tables.
        if bits > 1:
            bound = 1 << (bits - 1)
            for other in combinations(sorted(common), 3):
                if other != group:
                    tried += 1
                    if self._classes(targets, other, stop_above=bound) <= bound:
                        raise ValueError("some eligible group has a smaller sufficient summary")
        gates = circuit["gates"]
        ends = tuple(circuit["outputs"])
        start = self.n + 2
        values = [*self.columns, 0, self.full]
        raw_deps = [*(1 << i for i in range(self.n)), 0, 0]
        for gate in gates:
            if len(gate) != 2:
                raise ValueError("nonbinary NAND")
            a, b = gate
            if type(a) is not int or type(b) is not int or not (0 <= a < len(values) and 0 <= b < len(values)):
                raise ValueError("forward reference in circuit")
            values.append(self.full ^ (values[a] & values[b]))
            raw_deps.append(raw_deps[a] | raw_deps[b])
        if len(ends) != 2 or any(type(w) is not int or not 0 <= w < len(values) for w in ends + taps):
            raise ValueError("invalid output or summary wire")
        if tuple(values[w] for w in ends) != tuple(targets):
            raise ValueError("physical program disagrees with an output table")
        group_mask = sum(1 << i for i in group)
        if any(raw_deps[w] & ~group_mask for w in taps):
            raise ValueError("summary wire reads outside the selected group")
        # Stop only at a physically present summary wire. Every path out of
        # the selected source variables must pass through one of those wires.
        tapset = set(taps)
        def visit(output, cut):
            pending = [output]
            seen = set()
            while pending:
                wire = pending.pop()
                if wire in seen:
                    continue
                seen.add(wire)
                if cut and wire in tapset:
                    continue
                if wire >= start:
                    pending.extend(gates[wire - start])
                elif cut and wire < self.n and group_mask & (1 << wire):
                    raise ValueError("raw group wire bypasses the claimed summary")
            return seen
        used = [visit(w, True) & tapset for w in ends]
        if used[0] | used[1] != tapset:
            raise ValueError("declared summary wire never reaches an output")
        reach = [visit(w, False) for w in ends]
        ng = len(gates)
        return dict(exact=True, width=bits, classes=actual, common=len(common),
                    verified_assignments=self.rows, verified_output_bits=2 * self.rows,
                    alternatives_checked=tried, gates=ng, shared_gates=sum(i >= start for i in reach[0] & reach[1]),
                    active_gates=sum(i >= start for i in reach[0] | reach[1]),
                    shared_summary_wires=len(used[0] & used[1]),
                    structural_locality=True)
