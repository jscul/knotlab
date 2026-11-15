"""Project a guarded positive implication block onto its named middle choices."""

from typing import NamedTuple


def reachable(successors, roots):
    marked = bytearray(len(successors))
    work = list(roots)
    for root in work:
        marked[root] = 1
    while work:
        for v in successors[work.pop()]:
            if not marked[v]:
                marked[v] = 1
                work.append(v)
    return marked


def _compact(labels, bound):
    indices = [-1] * bound
    counts = []
    occurrences = []
    for name in labels:
        if not isinstance(name, int) or not 0 <= name < bound:
            raise ValueError("name outside indexed domain")
        if indices[name] < 0:
            indices[name] = len(counts)
            counts.append(0)
        j = indices[name]
        counts[j] += 1
        if counts[j] > 2:
            raise ValueError("name used more than twice within one role")
        occurrences.append(j)
    return occurrences, indices, counts


class Report(NamedTuple):
    possible: bool
    forced: tuple  # port order: -1 free, 0 false, 1 true
    arrows: tuple  # pairs of distinct free port indices

    def accepts(self, values):
        if len(values) != len(self.forced) or any(bit not in (0, 1) for bit in values):
            raise ValueError("expected one Boolean value per port")
        return (self.possible and all(pin < 0 or bit == pin for pin, bit in zip(self.forced, values))
                and all(values[u] <= values[v] for u, v in self.arrows))


class ImplicationBlock:
    """Use one raw guard vector and distinct middle-port IDs in the requested order.

    A port occurs once in this block. With local dense names, name_bound defaults
    to 6*r. For names retained from a larger layout supply its indexed bound.
    report and witness enforce the endpoint guard units in raw. To expose both
    boundaries of a subblock, supply the conventional 24 off endpoint guards.
    pad_release may set a common releasing bit for selected present pad IDs.
    """
    def __init__(self, middles, pads, raw, ports, *, name_bound=None, pad_release=None):
        self.stages = len(middles) // 2
        if not self.stages or len(middles) != 2*self.stages or len(pads) != 4*self.stages:
            raise ValueError("expected a nonempty two-branch stage block")
        if len(raw) != 24*(self.stages+1) or any(bit not in (0, 1) for bit in raw):
            raise ValueError("invalid raw guard vector")
        bound = 6*self.stages if name_bound is None else name_bound
        if not isinstance(bound, int) or bound < 0:
            raise ValueError("invalid indexed name bound")
        middle_ids, lookup, counts = _compact(middles, bound)
        self.pad_ids, pad_lookup, pad_counts = _compact(pads, bound)
        self.ports = tuple(ports)
        used = bytearray(len(counts))
        self.port_vertices = []
        for name in self.ports:
            if not isinstance(name, int) or not 0 <= name < bound:
                raise ValueError("invalid middle port")
            j = lookup[name]
            if j < 0 or counts[j] != 1 or used[j]:
                raise ValueError("each distinct port must occur in exactly one middle position")
            used[j] = 1
            self.port_vertices.append(self.stages+1+j)
        self.middle_vertices = [self.stages+1+j for j in middle_ids]
        self.edges = [[] for _ in range(self.stages+1+len(counts))]
        self.reverse = [[] for _ in self.edges]
        signs = [0] * len(pad_counts)
        for j, m in enumerate(self.middle_vertices):
            i = j // 2
            for pos, (u, v) in enumerate(((i, m), (m, i+1)), start=2*j):
                first = 24 + 6*pos
                flag = 2*int(all(raw[first:first+3])) + int(all(raw[first+3:first+6]))
                if flag == 3:
                    self.edges[u].append(v)
                    self.reverse[v].append(u)
                elif flag:
                    signs[self.pad_ids[pos]] |= flag
        if 3 in signs:
            raise ValueError("opposite active single halves prevent simultaneous pad release")
        self.pad_values = [int(sign == 1) for sign in signs]
        for name, bit in (pad_release or {}).items():
            if (not isinstance(name, int) or not 0 <= name < bound or
                    pad_lookup[name] < 0 or bit not in (0, 1)):
                raise ValueError("invalid prescribed value for a present pad")
            j = pad_lookup[name]
            if signs[j] & (1 << bit):
                raise ValueError("prescribed value does not release every active single half")
            self.pad_values[j] = bit
        self.start_on = all(raw[:12])
        self.end_on = all(raw[12:24])
        self.port_arrows = []
        for i, source in enumerate(self.port_vertices):
            forward = reachable(self.edges, [source])
            self.port_arrows.extend((i, j) for j, v in enumerate(self.port_vertices)
                                    if i != j and forward[v])

    def _pins(self, a, b):
        if a not in (0, 1) or b not in (0, 1):
            raise ValueError("expected Boolean boundary pins")
        if (self.start_on and not a) or (self.end_on and b):
            return None
        endpoints = ((0, a), (self.stages, b))
        return [v for v, bit in endpoints if bit], [v for v, bit in endpoints if not bit]

    def report(self, a, b):
        impossible = Report(False, (-1,) * len(self.ports), ())
        pins = self._pins(a, b)
        if pins is None:
            return impossible
        true, false = pins
        forced_true = reachable(self.edges, true)
        if any(forced_true[v] for v in false):
            return impossible
        forced_false = reachable(self.reverse, false)
        forced = []
        for v in self.port_vertices:
            if forced_true[v]:
                forced.append(1)
            elif forced_false[v]:
                forced.append(0)
            else:
                forced.append(-1)
        arrows = tuple((i, j) for i, j in self.port_arrows if forced[i] == forced[j] == -1)
        return Report(True, tuple(forced), arrows)

    def witness(self, a, b, values):
        if len(values) != len(self.ports) or any(bit not in (0, 1) for bit in values):
            raise ValueError("expected one Boolean value per port")
        pins = self._pins(a, b)
        if pins is None:
            return None
        true, false = pins
        for v, bit in zip(self.port_vertices, values):
            (true if bit else false).append(v)
        actual = reachable(self.edges, true)
        if any(actual[v] for v in false):
            return None
        occurrences = []
        for j, m in enumerate(self.middle_vertices):
            occurrences.extend((actual[m], self.pad_values[self.pad_ids[2*j]],
                                self.pad_values[self.pad_ids[2*j+1]]))
        return tuple(actual[:self.stages+1]), tuple(occurrences)


def common_values(left, right):
    """Return a joint port assignment for reports in the same port order, or None."""
    if len(left.forced) != len(right.forced):
        raise ValueError("reports have different numbers of ports")
    if not left.possible or not right.possible:
        return None
    edges = [[] for _ in left.forced]
    true, false = [], []
    for report in (left, right):
        for i, value in enumerate(report.forced):
            if value == 1:
                true.append(i)
            elif value == 0:
                false.append(i)
        for i, j in report.arrows:
            edges[i].append(j)
    model = reachable(edges, true)
    return None if any(model[v] for v in false) else tuple(model)
