"""Construct both boundary-support tables and join witnesses at one crossing name."""

from itertools import product


BITS = (0, 1)


def _compact(labels, domain):
    lookup = [-1] * domain
    values = []
    count = 0
    for label in labels:
        if lookup[label] < 0:
            lookup[label] = count
            count += 1
        values.append(lookup[label])
    return values, lookup, count


def _block(middles, pads, flags, port, domain):
    """Eight boundary/port pins, each with one witness if feasible."""
    stages = len(middles) // 2
    mid, mid_lookup, nmid = _compact(middles, domain)
    pad, pad_lookup, npad = _compact(pads, domain)
    mid_offset = stages + 1
    pinned_pad = pad_lookup[port // 2] if port % 2 else -1
    pinned_mid = -1 if port % 2 else mid_offset + mid_lookup[port // 2]
    edges = []
    signs = [0] * npad
    for j, name in enumerate(mid):
        m = mid_offset + name
        i = j // 2
        for edge, (u, v) in enumerate(((i, m), (m, i+1)), start=2*j):
            p, flag = pad[edge], flags[edge]
            edges.append((u, v, p, flag))
            if flag in (1, 2):
                signs[p] |= flag
    mixed = [p for p in range(npad) if signs[p] == 3 and p != pinned_pad]
    # Bit v of a flag is on exactly when pad value v forces the implication.
    pad_values = [int(sign == 1) for sign in signs]
    table = {}
    for port_value in BITS:
        if pinned_pad >= 0:
            pad_values[pinned_pad] = port_value
        for values in product(BITS, repeat=len(mixed)):
            for p, value in zip(mixed, values):
                pad_values[p] = value
            successors = [[] for _ in range(mid_offset + nmid)]
            for u, v, p, flag in edges:
                if flag & (1 << pad_values[p]):
                    successors[u].append(v)
            for left, right in product(BITS, repeat=2):
                key = (left, right, port_value)
                if key in table:
                    continue
                pins = [(0, left), (stages, right)]
                if pinned_mid >= 0:
                    pins.append((pinned_mid, port_value))
                reached = bytearray(len(successors))
                work = [u for u, value in pins if value]
                for u in work:
                    reached[u] = 1
                while work:
                    for v in successors[work.pop()]:
                        if not reached[v]:
                            reached[v] = 1
                            work.append(v)
                if any(reached[u] != value for u, value in pins):
                    continue
                occurrence_values = []
                for j, m in enumerate(mid):
                    occurrence_values.extend((reached[mid_offset+m], pad_values[pad[2*j]],
                                              pad_values[pad[2*j+1]]))
                table[key] = tuple(reached[:mid_offset]), tuple(occurrence_values)
    return table, len(mixed)


class CutAnalysis:
    def __init__(self, port, left, right, mixed, start_on, end_on):
        self.port = port
        self.left = left
        self.right = right
        self.mixed = mixed
        self.start_on = start_on
        self.end_on = end_on

    def masks(self, a, y, b):
        """Possible shared-name values with these boundaries, before endpoint units."""
        left = sum(1 << v for v in BITS if (a, y, v) in self.left)
        right = sum(1 << v for v in BITS if (y, b, v) in self.right)
        return left, right

    def lost_triples(self):
        lost = []
        for triple in product(BITS, repeat=3):
            left, right = self.masks(*triple)
            if left and right and not (left & right):
                lost.append(triple)
        return tuple(lost)

    def lost_outer_pairs(self):
        lost = []
        for a, b in product(BITS, repeat=2):
            options = [self.masks(a, y, b) for y in BITS]
            if any(l and r for l, r in options) and not any(l & r for l, r in options):
                lost.append((a, b))
        return tuple(lost)

    def witness(self, a, y, b):
        """Internal witness for this displayed triple, before external endpoint units."""
        for v in BITS:
            left = self.left.get((a, y, v))
            right = self.right.get((y, b, v))
            if left is not None and right is not None:
                return left[0][:-1] + right[0], left[1] + right[1]
        return None

    def solve(self):
        """Witness respecting the actual external guard vector, or None."""
        for a, y, b in product(BITS, repeat=3):
            if (self.start_on and a == 0) or (self.end_on and b == 1):
                continue
            witness = self.witness(a, y, b)
            if witness is not None:
                return witness
        return None


def analyze_cut(middles, pads, raw, cut):
    """Use the predecessor's indexed names/guard order and a cut after stage 'cut'.

    Blocks must be nonempty and share exactly one middle or pad name. The
    returned port ID is 2*j for middle j and 2*j+1 for pad j.
    """
    stages = len(middles) // 2
    domain = 6 * stages
    if len(middles) != 2*stages or len(pads) != 4*stages or not 0 < cut < stages:
        raise ValueError("expected two nonempty stage blocks with a proper cut")
    if len(raw) != 24*(stages + 1) or any(bit not in BITS for bit in raw):
        raise ValueError("invalid raw guard vector")
    uses = [0] * (2 * domain)
    locations = [0] * (2 * domain)
    for role, (labels, boundary) in enumerate(((middles, 2*cut), (pads, 4*cut))):
        for i, name in enumerate(labels):
            if not isinstance(name, int) or not 0 <= name < domain:
                raise ValueError("expected indexed name within the input domain")
            typed = 2*name + role
            uses[typed] += 1
            if uses[typed] > 2:
                raise ValueError("one typed name occurs more than twice")
            locations[typed] |= 1 if i < boundary else 2
    crossing = [name for name, mask in enumerate(locations) if mask == 3]
    if len(crossing) != 1:
        raise ValueError("expected precisely one crossing typed name")
    port = crossing[0]
    flags = []
    for j in range(24, len(raw), 6):
        flags.append(2*int(all(raw[j:j+3])) + int(all(raw[j+3:j+6])))
    left, q_left = _block(middles[:2*cut], pads[:4*cut], flags[:4*cut], port, domain)
    right, q_right = _block(middles[2*cut:], pads[4*cut:], flags[4*cut:], port, domain)
    return CutAnalysis(port, left, right, (q_left, q_right), all(raw[:12]), all(raw[12:24]))


def complete_raw_witness(clauses, guard_vars, hidden_vars, raw, witness):
    """Extend a returned witness on the predecessor's concrete strict clause numbering.

    The first three arguments are the predecessor raw_layout emitter's output.
    Return a signed DIMACS assignment including all switches and private witnesses.
    """
    bounds, occurrences = witness
    if len(guard_vars) != len(raw) or len(hidden_vars) != len(occurrences):
        raise ValueError("wrong number of pins for the raw formula")
    last = max(abs(lit) for clause in clauses for lit in clause)
    values = [-1] * (last+1)

    def put(var, bit):
        if values[var] not in (-1, bit):
            raise ValueError("occurrence values disagree on an identified raw variable")
        values[var] = bit

    def holds(lit):
        value = values[abs(lit)]
        if value < 0:
            raise ValueError("missing value for a padded literal")
        return value == (lit > 0)

    for var, bit in enumerate(bounds, start=1):
        put(var, bit)
    for var, bit in zip(hidden_vars, occurrences):
        put(var, bit)
    for var, bit in zip(guard_vars, raw):
        put(var, bit)
    for first in (0, 4):
        # A false endpoint literal needs an inactive slot. Falsify its two
        # padding literals; every other sign combination then has a true one.
        slot = first
        if not holds(clauses[4*first + 1][-1]):
            slot = next((i for i in range(first, first+4) if not all(raw[3*i:3*i+3])), None)
            if slot is None:
                raise ValueError("false endpoint has all four slots active")
        for j in (2, 3):
            lit = clauses[4*slot + j][-1]
            put(abs(lit), int(lit < 0))
    for i in range(len(clauses)//4):
        ws = clauses[4*i]
        chosen = next((j for j in range(3) if not raw[3*i+j] or holds(clauses[4*i+j+1][-1])),
                      None)
        if chosen is None:
            raise ValueError("an active padded clause has no true literal")
        for j, var in enumerate(ws):
            put(var, int(j == chosen))
    return tuple(v if values[v] == 1 else -v for v in range(1, last+1))
