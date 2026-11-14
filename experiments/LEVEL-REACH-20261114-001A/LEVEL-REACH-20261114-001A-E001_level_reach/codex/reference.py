"""Independent, plain-Python reference computations for the stage-1 gates.

``pattern(key, N)`` returns a sorted list of distinct, sorted id triples.
It does not import the producing implementation, NumPy, or a SAT solver.

``brute_bonds(rows, nvars, A, B, kmax=7)`` interprets every row as a
not-all-equal constraint.  It visits every one of the ``2**nvars`` states,
then every support of size zero through ``min(kmax, nvars)``.  Integer
bitsets implement exact existential projection; no SAT search is used.
The intended gate has 15 variables, rather than the much larger run cases.

Its result has ``L`` equal to a least cross-bond size, ``"none"`` when
nonexistence is proved, or ``"> kmax"`` after bounded exhaustion.  ``bond``
and ``forbidden_assignment`` give one least witness; ``bonds`` lists all
minimal nonfull supports within the enumerated boundary.  Counts include
the empty support.  A dead relation has ``alive=False`` and ``L=None``:
the specification defines the observable only for alive relations.

Importing this module starts no run and writes no files.
"""

from functools import lru_cache
from itertools import combinations
from math import comb


def _key_parts(key):
    if len(key) != 5:
        raise ValueError("key must contain s, swap, successor0, successor1, placements")
    s = int(key[0])
    if s < 1:
        raise ValueError("an automaton must have at least one state")
    sw, d0, d1 = (tuple(int(item) for item in row) for row in key[1:4])
    if any(len(row) != s for row in (sw, d0, d1)):
        raise ValueError("automaton rows must agree with the state count")
    if any(bit not in (0, 1) for bit in sw):
        raise ValueError("swap entries must be bits")
    if any(q < 0 or q >= s for q in d0 + d1):
        raise ValueError("successor outside the automaton")
    term_count = 3 * (1 + s + s * s)
    placements = set()
    for row in key[4]:
        triple = tuple(sorted(int(item) for item in row))
        if len(triple) != 3 or len(set(triple)) != 3:
            raise ValueError("a placement must contain three distinct term indices")
        if triple[0] < 0 or triple[-1] >= term_count:
            raise ValueError("placement term index outside T_s")
        placements.add(triple)
    return s, sw, d0, d1, tuple(sorted(placements))


def _state_image(q, address, length, sw, d0, d1):
    """Read input letters from first to last, updating the current state."""
    image = 0
    for shift in range(length - 1, -1, -1):
        letter = (address >> shift) & 1
        image = (image << 1) | (letter ^ sw[q])
        q = d1[q] if letter else d0[q]
    return image


def pattern(key, N):
    """Construct the union up to level N using only scalar address loops.

    Terms have index ``3 * word_index + letter_slot``, with slots
    ``none, 0, 1``.  State products act right to left.  The letter, if any,
    is appended after the entire word has acted.
    """
    s, sw, d0, d1, placements = _key_parts(key)
    N = int(N)
    if N < 0:
        raise ValueError("N must be nonnegative")
    words = [()]
    for q in range(s):
        words.append((q,))
    for q in range(s):
        for r in range(s):
            words.append((q, r))
    used_words = sorted({term // 3 for row in placements for term in row})
    result = set()
    for n in range(N + 1):
        usable = []
        for row in placements:
            if n < N or all(term % 3 == 0 for term in row):
                usable.append(row)
        if not usable:
            continue
        level_offset = (1 << n) - 1
        next_offset = (1 << (n + 1)) - 1
        for address in range(1 << n):
            images = {}
            for word_index in used_words:
                image = address
                for q in reversed(words[word_index]):
                    image = _state_image(q, image, n, sw, d0, d1)
                images[word_index] = image
            for row in usable:
                ids = []
                for term in row:
                    word_index, letter_slot = divmod(term, 3)
                    image = images[word_index]
                    if letter_slot == 0:
                        ids.append(level_offset + image)
                    else:
                        ids.append(next_offset + 2 * image + letter_slot - 1)
                triple = tuple(sorted(ids))
                if triple[0] != triple[1] and triple[1] != triple[2]:
                    result.add(triple)
    return sorted(result)


def _rows(rows, nvars):
    result = set()
    for row in rows:
        triple = tuple(sorted(int(item) for item in row))
        if len(triple) != 3 or len(set(triple)) != 3:
            raise ValueError("a pattern row must have three distinct ids")
        if triple[0] < 0 or triple[-1] >= nvars:
            raise ValueError("pattern id outside range(nvars)")
        result.add(triple)
    return tuple(sorted(result))


@lru_cache(maxsize=256)
def _drop_masks(nbits, position):
    """Masks for merging and compacting a Boolean coordinate.

    There are 2**nbits truth-table entries.  At each step the lower half
    of each equal-sized pair of blocks survives.  The final entries have
    the removed coordinate absent and all other coordinates in order.
    """
    width = 1 << nbits
    universe = (1 << width) - 1
    block = 1 << position
    first = True
    result = []
    while block < width:
        alternating = universe // ((1 << (2 * block)) - 1)
        # The first step merges the two values of the removed variable.
        # Later steps compact the surviving blocks; their gaps are half
        # the new block width.
        shift = block if first else block >> 1
        result.append((shift, alternating * ((1 << block) - 1)))
        first = False
        block <<= 1
    return tuple(result)


def _drop_coordinate(relation, nbits, position):
    for block, mask in _drop_masks(nbits, position):
        relation = (relation | (relation >> block)) & mask
    return relation


@lru_cache(maxsize=4)
def _all_bonds(rows, nvars, limit):
    """Exhaust every state and support; return only immutable summaries."""
    state_total = 1 << nvars
    encoded = bytearray((state_total + 7) // 8)
    knot_masks = tuple(sum(1 << item for item in row) for row in rows)
    for state in range(state_total):
        allowed = True
        for mask in knot_masks:
            selected = state & mask
            if selected == 0 or selected == mask:
                allowed = False
                break
        if allowed:
            encoded[state >> 3] |= 1 << (state & 7)
    relation = int.from_bytes(encoded, "little")
    state_count = relation.bit_count()
    all_variables = (1 << nvars) - 1

    @lru_cache(maxsize=None)
    def project(support):
        if support == all_variables:
            return relation
        # Add the largest omitted variable to get one canonical parent.
        missing = all_variables ^ support
        added = 1 << (missing.bit_length() - 1)
        parent = support | added
        position = (support & (added - 1)).bit_count()
        return _drop_coordinate(project(parent), parent.bit_count(), position)

    full = {}
    bonds = []
    counts = []
    for size in range(limit + 1):
        supports_count = 0
        full_count = 0
        bond_count = 0
        for support in combinations(range(nvars), size):
            support_mask = sum(1 << item for item in support)
            projected = project(support_mask)
            all_assignments = (1 << (1 << size)) - 1
            is_full = projected == all_assignments
            full[support_mask] = is_full
            supports_count += 1
            if is_full:
                full_count += 1
            elif all(full[support_mask ^ (1 << item)] for item in support):
                # All maximal proper subsets full is equivalent to every
                # proper subset full, by downward closure of fullness.
                missing_assignments = all_assignments ^ projected
                first_missing = (missing_assignments & -missing_assignments).bit_length() - 1
                bonds.append((support, first_missing))
                bond_count += 1
        counts.append((size, supports_count, full_count, supports_count - full_count,
                       bond_count))
    return (state_count, tuple(bonds), tuple(counts), project.cache_info().currsize)


def _cross_connected(rows, nvars, A, B):
    parent = list(range(nvars))

    def root(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for row in rows:
        first = root(row[0])
        for item in row[1:]:
            parent[root(item)] = first
    roots_a = {root(item) for item in A}
    return any(root(item) in roots_a for item in B)


def brute_bonds(pattern, nvars, A, B, kmax=7):
    """Return exact tiny-case cross-bond sizes and enumeration evidence.

    ``A`` and ``B`` are iterables of distinction ids.  ``bonds`` contains
    every minimal nonfull support through the requested boundary, including
    ones that do not meet both sets.  ``counts_by_size`` records all supports,
    full and nonfull projections, and minimal nonfull supports at each size.
    The returned forbidden assignment is a dict from id to its zero/one value.
    """
    nvars, kmax = int(nvars), int(kmax)
    if nvars < 0 or kmax < 0:
        raise ValueError("nvars and kmax must be nonnegative")
    rows = _rows(pattern, nvars)
    A, B = frozenset(int(item) for item in A), frozenset(int(item) for item in B)
    if any(item < 0 or item >= nvars for item in A | B):
        raise ValueError("A or B contains an id outside range(nvars)")
    limit = min(kmax, nvars)
    state_count, bonds, counts, projections = _all_bonds(rows, nvars, limit)
    cross = [(support, forbidden) for support, forbidden in bonds
             if A.intersection(support) and B.intersection(support)]
    connected = _cross_connected(rows, nvars, A, B)
    bond = None
    forbidden_assignment = None
    if not state_count:
        least = None
    elif cross:
        bond, forbidden = cross[0]
        least = len(bond)
        forbidden_assignment = {item: (forbidden >> position) & 1
                                for position, item in enumerate(bond)}
    elif not connected or limit == nvars:
        least = "none"
    else:
        least = f"> {kmax}"
    cross_counts = {}
    for support, _ in cross:
        cross_counts[len(support)] = cross_counts.get(len(support), 0) + 1
    counts_by_size = []
    for size, supports_count, full_count, nonfull_count, bond_count in counts:
        counts_by_size.append({
            "size": size,
            "supports": supports_count,
            "full": full_count,
            "nonfull": nonfull_count,
            "bonds": bond_count,
            "cross_bonds": cross_counts.get(size, 0),
        })
    support_total = sum(row["supports"] for row in counts_by_size)
    expected_total = sum(comb(nvars, size) for size in range(limit + 1))
    if support_total != expected_total:
        raise AssertionError("support enumeration did not reach its exact boundary")
    return {
        "alive": bool(state_count),
        "L": least,
        "bond": list(bond) if bond is not None else None,
        "forbidden_assignment": forbidden_assignment,
        "bonds": [list(support) for support, _ in bonds],
        "components": connected,
        "state_count": state_count,
        "states_examined": 1 << nvars,
        "support_count": support_total,
        "expected_support_count": expected_total,
        "counts_by_size": counts_by_size,
        "exhausted_through": limit,
        "all_supports_exhausted": limit == nvars,
        "projection_bitsets_computed": projections,
        "optimality_proved": bool(state_count) and (isinstance(least, int) or least == "none"),
        "method": "all Boolean states; every support; exact integer-bitset projection",
    }
