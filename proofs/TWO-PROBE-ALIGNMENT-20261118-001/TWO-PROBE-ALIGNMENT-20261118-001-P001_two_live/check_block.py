"""Grade anonymous serial commands on the eight original parity junctions."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import combinations, permutations, product
import argparse
import hashlib
import json
import random
from pathlib import Path


# Replay names, inaccessible to the reader. The first eight are the original
# cut columns, with horizontal directions 1 and 2 and selected mark direction 4.
# Each tuple is (old marked output, incoming identities); two other outputs
# are fresh at each gate. Unused fresh outputs can exchange at their parent.
GATES = (
    (0, ()),
    (1, (8,)),
    (2, (9,)),
    (3, (10, 12)),
    (4, (0,)),
    (5, (1, 16)),
    (6, (2, 17)),
    (7, (3, 18, 20)),
)
Pair = tuple[int, int]


def pair(left, right):
    assert left != right
    return (left, right) if left < right else (right, left)


def cut_columns():
    rows = [0, 255]
    for axis in (1, 2, 4):
        cut = sum(1 << v for v in range(8) if v & axis)
        rows.extend((cut, cut ^ 255))
    return tuple(sum((r >> i & 1) << s for s, r in enumerate(rows)) for i in range(8))


@dataclass(frozen=True)
class Fibres:
    # Each variable is a linear form in independent binary freedoms plus one
    # constant per still-admitted original row. The different rows may yield
    # overlapping fibres, which are combined just by set union in full().
    forms: tuple[tuple[int, int], ...]
    admitted: int = 255

    def condition(self, requirements):
        pivots = {}
        admitted = self.admitted
        for bit, value in requirements:
            linear, offset = self.forms[bit]
            offset ^= 255 if value else 0
            while linear:
                pivot = linear.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = linear, offset
                    break
                known, value_rows = pivots[pivot]
                linear ^= known
                offset ^= value_rows
            if not linear:
                admitted &= ~offset
        transformed = []
        for linear, offset in self.forms:
            for pivot in sorted(pivots, reverse=True):
                if linear >> pivot & 1:
                    known, value_rows = pivots[pivot]
                    linear ^= known
                    offset ^= value_rows
            transformed.append((linear, offset))
        return Fibres(tuple(transformed), admitted)

    def full(self, bits):
        if not self.admitted:
            return False
        pivots = {}
        groups = [self.admitted]
        for bit in bits:
            linear, offset = self.forms[bit]
            while linear:
                pivot = linear.bit_length()
                if pivot not in pivots:
                    pivots[pivot] = linear, offset
                    break
                prior, value_rows = pivots[pivot]
                linear ^= prior
                offset ^= value_rows
            if not linear:
                following = []
                for group in groups:
                    ones = group & offset
                    zeroes = group & ~offset
                    if not ones or not zeroes:
                        return False
                    following.extend((ones, zeroes))
                groups = following
        return True


@cache
def base(stage):
    forms = [(0, column) for column in cut_columns()]
    for rank, (marked, incoming) in enumerate(GATES[:stage]):
        free, word = 1 << rank, 0
        forms.append((free, word))
        for bit in (marked, *incoming):
            linear, offset = forms[bit]
            free ^= linear
            word ^= offset
        forms.append((free, word))
    return Fibres(tuple(forms))


@cache
def permanent_supports(stage, limit):
    fibres = base(stage)
    genuine = tuple(range(len(fibres.forms)))
    bonds = []
    dependent = set()
    for n in range(1, limit + 2):
        for support in combinations(genuine, n):
            smaller = tuple(support[:i] + support[i + 1:] for i in range(n))
            if any(t in dependent for t in smaller):
                dependent.add(support)
            elif not fibres.full(support):
                dependent.add(support)
                assert n >= 3
                bonds.append(support)
    return tuple(bonds)


@cache
def conditions(stage, probes):
    return tuple(
        base(stage).condition((bit, value) for ab, value in zip(probes, values) for bit in ab)
        for values in product((0, 1), repeat=len(probes))
    )


@cache
def free_with_probes(stage, probes, genuine):
    return all(fibres.full(genuine) for fibres in conditions(stage, probes))


@cache
def table(stage, probes=(), limit=4):
    # An observed single endpoint always extends by its opposite. Thus a
    # minimal support contains neither endpoint or both from each probe.
    # To project both endpoints freely it suffices to realize all equal-value
    # patterns in the selected probe pairs; opposed endpoints release the test.
    n = len(base(stage).forms)
    pairs = [(n + 2 * k, n + 2 * k + 1) for k in range(len(probes))]
    width = n + len(pairs) * 2
    sentinel = limit + 1
    out = [[sentinel] * width for _ in range(width)]
    for i in range(width):
        out[i][i] = 0

    def include(support):
        distance = len(support) - 1
        for i, j in combinations(support, 2):
            out[i][j] = out[j][i] = min(out[i][j], distance)

    for support in permanent_supports(stage, limit):
        include(support)
    for count in range(1, 1 + len(probes)):
        for chosen in combinations(range(len(probes)), count):
            active = tuple(probes[i] for i in chosen)
            endpoints = tuple(bit for i in chosen for bit in pairs[i])
            for size in range(limit + 2 - len(endpoints)):
                for rest in combinations(range(n), size):
                    if free_with_probes(stage, active, rest):
                        continue
                    if not all(free_with_probes(stage, active, rest[:i] + rest[i + 1:])
                               for i in range(size)):
                        continue
                    if not all(free_with_probes(stage, active[:i] + active[i + 1:], rest)
                               for i in range(len(active))):
                        continue
                    include((*endpoints, *rest))
    return tuple(map(tuple, out))


def colors(matrix):
    assigned = (0,) * len(matrix)
    while True:
        profiles = [
            (assigned[i], tuple(sorted((value, assigned[j]) for j, value in enumerate(row))))
            for i, row in enumerate(matrix)
        ]
        ids = {v: i for i, v in enumerate(sorted(set(profiles)))}
        updated = tuple(ids[v] for v in profiles)
        if updated == assigned:
            return updated
        assigned = updated


def cells(matrix):
    marked = colors(matrix)
    return tuple(tuple(i for i, c in enumerate(marked) if c == v) for v in sorted(set(marked)))


@cache
def view(matrix):
    """The lookup key and vertex colors depend only on the current table."""
    label = colors(matrix)
    fingerprint = tuple(sorted(
        (label[i], tuple(sorted((distance, label[j]) for j, distance in enumerate(row))))
        for i, row in enumerate(matrix)
    ))
    return fingerprint, label


def ordered_forms(command):
    kind, *args = command
    if kind == "gate":
        for incoming in permutations(args[1]):
            yield (args[0], *incoming)
    elif kind == "clear":
        yield ()
    else:
        families = (args, args[::-1]) if kind == "bulk" else (args,)
        for family in families:
            for groups in product(*(permutations(ab) for ab in family)):
                yield tuple(bit for ab in groups for bit in ab)


def key_for(matrix, command):
    label = view(matrix)[1]
    def pattern(bits):
        return (
            tuple(label[bit] for bit in bits),
            tuple(matrix[x][y] for x, y in combinations(bits, 2)),
        )
    return command[0], min(map(pattern, ordered_forms(command)))


def command_from(kind, bits):
    if kind == "gate":
        return kind, bits[0], tuple(sorted(bits[1:]))
    if kind == "clear":
        return (kind,)
    ab = tuple(pair(*bits[i:i + 2]) for i in range(0, len(bits), 2))
    return (kind, *(sorted(ab) if kind == "bulk" else ab))


def commands_from(matrix, key):
    """Select every operand tuple passing the same observable finite test."""
    kind, (wanted, distances) = key
    label = view(matrix)[1]
    choices = [tuple(i for i, c in enumerate(label) if c == v) for v in wanted]
    return {
        command_from(kind, bits) for bits in product(*choices)
        if tuple(matrix[x][y] for x, y in combinations(bits, 2)) == distances
    }


def sorted_probes(probes):
    return tuple(sorted(pair(*ab) for ab in probes))


def endpoints(stage, probes, middles):
    slot = probes.index(pair(*middles))
    first = 8 + 2 * stage + 2 * slot
    return first, first + 1


@cache
def physical_maps(stage):
    # External universal-tie grader: the history-independent current incidence,
    # old cube adjacency and the roles of the reused eight bits are preserved.
    # The reader above does not receive these permutations or their arguments.
    positions = {marked: rank for rank, (marked, _) in enumerate(GATES[:stage])}
    output = []
    for axes in permutations((1, 2, 4)):
        old = tuple(sum(axis for i, axis in enumerate(axes) if v >> i & 1) for v in range(8))
        if any(old[marked] not in positions for marked in positions):
            continue
        for flips in product((0, 1), repeat=stage):
            renamed = list(old)
            for rank, (marked, _) in enumerate(GATES[:stage]):
                start = 8 + 2 * positions[old[marked]]
                renamed.extend((start + flips[rank], start + (1 - flips[rank])))
            if all({renamed[u] for u in incoming} == set(GATES[positions[old[m]]][1])
                   for m, incoming in GATES[:stage]):
                output.append(tuple(renamed))
    assert output
    return tuple(output)


def transfer(probes, rename):
    return sorted_probes((rename[a], rename[b]) for a, b in probes)


@cache
def normalized(stage, probes):
    return stage, min(transfer(probes, mapping) for mapping in physical_maps(stage))


def execute(stage, probes, command):
    """Reject an illegal command or a genuine gate with the wrong literal inputs."""
    kind, *args = command
    n = 8 + 2 * stage
    if kind == "gate":
        target, parents = GATES[stage]
        marked, incoming = args
        assert all(0 <= i < n for i in (marked, *incoming)) and marked not in incoming
        choices = [normalized(stage + 1, transfer(probes, mapping))
                   for mapping in physical_maps(stage)
                   if mapping[marked] == target and {mapping[u] for u in incoming} == set(parents)]
        assert choices and len(set(choices)) == 1, (stage, probes, command, choices)
        return choices[0]
    if kind == "clear":
        assert probes
        return normalized(stage, ())
    if kind == "bulk":
        assert len(args) == 2 and all(max(ab) < n for ab in args)
        return normalized(stage, sorted_probes(args))
    kept = list(probes)
    if kind in ("drop", "swap"):
        old = args.pop(0)
        matches = [ab for ab in kept if endpoints(stage, probes, ab) == old]
        assert len(matches) == 1, (stage, probes, command)
        kept.remove(matches[0])
    if args:
        assert len(args) == 1 and max(args[0]) < n and len(kept) < 2
        kept.append(args[0])
    return normalized(stage, sorted_probes(kept))


def reference_actions():
    """Offline finite recipe. Values here are replay names, stripped by key_for."""
    rules = []
    def issue(stage, active, kind, *operands):
        probes = sorted_probes(active)
        args = list(operands)
        if kind in ("drop", "swap"):
            args[0] = endpoints(stage, probes, args[0])
        rules.append((stage, probes, (kind, *args)))

    # The bulk commands are used only in the clean two-junction transfer.
    issue(2, (), "bulk", (2, 10), (0, 2))
    for a in range(2, 8):
        active = ((a, 10), (0, a))
        if a == 7:
            issue(2, active, "bulk", (a, 8), (a, 9))
            issue(2, ((a, 8), (a, 9)), "bulk", (2, 10), (0, 2))
            continue
        face = [v for v in (2, 4) if (v & ~a) == 0]
        assert face
        issue(2, active, "gate", face[0], (9,))
        # Universal normalized successors may exchange not-yet-assigned axes.
        # List every geometrically compatible gate image before clearing.
        probes = sorted_probes(active)
        for y in face:
            next_stage, remaining = execute(2, probes, ("gate", y, (9,)))
            issue(next_stage, remaining, "clear")

    issue(3, (), "add", (1, 2))
    issue(3, ((1, 2),), "gate", 3, (10, 12))
    issue(4, ((1, 2),), "drop", (1, 2))

    # The reader distinguishes 62 versus 66 pairs at distance three.
    # Both probes involve an old and a fresh identity and each is removable.
    issue(4, (), "add", (4, 8))
    for b in (4, 5, 6, 7):
        marker = pair(8, b)
        guard = (3, 9)
        center = 1 if b in (4, 7) else 0
        face = pair(center, b)
        issue(4, (marker,), "add", guard)
        if b in (4, 7):
            # Opposite diagonals of one old square impose identical tests.
            # Carry the classification in an actual different fresh operand.
            issue(4, (marker, guard), "swap", marker, (b, 14))
            marker = pair(b, 14)
        issue(4, (marker, guard), "swap", guard, face)
        if b == 7:
            issue(4, (marker, face), "swap", marker, (5, 10))
            issue(4, ((5, 10), face), "swap", face, (0, 5))
            marker, face = (5, 10), (0, 5)
        issue(4, (marker, face), "swap", marker, (4, 11))
        issue(4, ((4, 11), face), "gate", 4, (0,))
        if b == 6:
            issue(5, ((4, 11), face), "swap", face, (1, 4))

    low_marker = (4, 11)
    x_face, y_face = (1, 4), (2, 4)
    issue(5, (low_marker, x_face), "gate", 5, (1, 16))
    issue(6, (low_marker, x_face), "swap", x_face, y_face)
    high_marker = (6, 19)
    issue(6, (low_marker, y_face), "swap", low_marker, high_marker)
    issue(6, (high_marker, y_face), "gate", 6, (2, 17))
    issue(7, (high_marker, y_face), "swap", y_face, (3, 6))
    issue(7, (high_marker, (3, 6)), "gate", 7, (3, 18, 20))
    return rules


def atlas():
    """Public API: (raw capped anonymous matrix, representative command) pairs.

    A relabeling of a matrix and its command is an equivalent API entry.
    'swap' first takes the two separately observable departing endpoints.
    'bulk' clears the whole instrument and takes two unordered new middle pairs.
    """
    return tuple((table(stage, probes), command)
                 for stage, probes, command in reference_actions())


@cache
def policy():
    compiled = {}
    for matrix, command in atlas():
        observation = view(matrix)[0]
        action = key_for(matrix, command)
        assert compiled.setdefault(observation, action) == action, ("recipe collision", command)
    return compiled


def read_actions(matrix):
    # Clamp the supplied scalar table. A larger or infinite distance has the
    # same observation. No encoding of queried or permanent roles is accepted.
    short = tuple(tuple(min(v, 5) if v is not None else 5 for v in row) for row in matrix)
    key = policy().get(view(short)[0])
    return set() if key is None else commands_from(short, key)


def transported(command, perm):
    kind, *args = command
    if kind == "gate":
        return kind, perm[args[0]], tuple(sorted(perm[x] for x in args[1]))
    if kind == "clear":
        return (kind,)
    moved = tuple(pair(perm[a], perm[b]) for a, b in args)
    return (kind, *(sorted(moved) if kind == "bulk" else moved))


@cache
def walk(first):
    terminal = normalized(8, sorted_probes(((6, 19), (3, 6))))
    counts = {}
    actions = {}
    ranks = {terminal: 0}
    visiting = set()
    def visit(state):
        if state in ranks:
            return ranks[state]
        assert state not in visiting, ("permitted cycle", state)
        visiting.add(state)
        stage, probes = state
        matrix = table(stage, probes)
        moves = read_actions(matrix)
        assert moves, ("uncovered", state, cells(matrix))
        # Independently rename every whole input, including all endpoints,
        # before applying the very same public reader.
        order = list(range(len(matrix)))
        seed = hashlib.sha256(repr(state).encode()).digest()
        random.Random(seed).shuffle(order)
        perm = tuple(order.index(i) for i in range(len(order)))
        renamed = tuple(tuple(matrix[i][j] for j in order) for i in order)
        assert read_actions(renamed) == {transported(move, perm) for move in moves}
        successors = {execute(stage, probes, move) for move in moves}
        actions[state] = len(moves)
        counts[state] = len(successors)
        ranks[state] = 1 + max(visit(s) for s in successors)
        visiting.remove(state)
        return ranks[state]
    longest = visit(first)
    return ranks, {
        "maximum_commands": longest,
        "physical_positions": len(ranks),
        "permitted_operand_choices": sum(actions.values()),
        "physical_transitions": sum(counts.values()),
        "observed_stages": sorted({s for s, _ in ranks}),
        "maximum_live_pairs": max(len(p) for _, p in ranks),
        "individual_commands_only": all(
            move[0] not in ("bulk", "clear") for s, p in actions for move in read_actions(table(s, p))
        ),
    }


def explore(first):
    return walk(first)[1]


def reachable_templates():
    """Each reachable input and every allowed command, terminal included."""
    return tuple(
        (stage, probes, table(stage, probes), read_actions(table(stage, probes)))
        for stage, probes in sorted(walk((2, ()))[0])
    )


def direct_rows(stage, probes):
    """Independent explicit row generator: no affine elimination or fibre code."""
    cut_rows = {0, 255}
    for axis in range(3):
        lower = sum(1 << v for v in range(8) if not (v >> axis & 1))
        cut_rows.update((lower, 255 ^ lower))
    rows = list(cut_rows)
    n = 8
    for marked, incoming in GATES[:stage]:
        inputs = (marked, *incoming)
        previous = rows
        rows = [word | (left << n) | (right << (n + 1)) for word in previous
                for left, right in product((0, 1), repeat=2)
                if (left + right + sum(word >> i & 1 for i in inputs)) % 2 == 0]
        assert len(rows) == 2 * len(previous)
        n += 2
    for a, b in probes:
        previous = rows
        rows = [
            word | (left << n) | (right << (n + 1)) for word in previous
            for left, right in product((0, 1), repeat=2)
            if left != right or left == (word >> a & 1) == (word >> b & 1)
        ]
        assert {row & ((1 << n) - 1) for row in rows} == set(previous)
        n += 2
    return tuple(rows), n


def direct_table(rows, n, limit):
    # For each bit, one bitset of row indices containing 1. Intersecting with
    # a column and its complement partitions the actual allowed rows.
    columns = [bytearray((len(rows) + 7) // 8) for _ in range(n)]
    for i, word in enumerate(rows):
        while word:
            unit = word & -word
            columns[unit.bit_length() - 1][i // 8] |= 1 << (i % 8)
            word ^= unit
    columns = [int.from_bytes(column, "little") for column in columns]
    live = (1 << len(rows)) - 1
    out = [[limit + 1] * n for _ in range(n)]
    for i in range(n):
        out[i][i] = 0
    free = {()}
    for arity in range(1, limit + 2):
        for support in combinations(range(n), arity):
            if not all(support[:k] + support[k + 1:] in free for k in range(arity)):
                continue
            groups = [live]
            for i in support:
                new = []
                for group in groups:
                    ones = group & columns[i]
                    zeroes = group & ~columns[i]
                    if not ones or not zeroes:
                        break
                    new.extend((ones, zeroes))
                else:
                    groups = new
                    continue
                break
            else:
                free.add(support)
                continue
            assert arity >= 3
            for i, j in combinations(support, 2):
                out[i][j] = out[j][i] = min(out[i][j], arity - 1)
    return tuple(map(tuple, out))


def check_original_and_controls():
    fixtures = (
        ("first horizontal, antipodal comparison", 2, ((0, 7), (7, 10)), 4),
        ("lower square, unmarked diagonal class", 4, ((3, 9), (4, 8)), 4),
        ("lower square, unmarked side class", 4, ((3, 9), (5, 8)), 4),
        ("full marked block before the last gate", 7, ((3, 6), (6, 19)), 4),
        ("full marked block with its crossing marker", 8, ((3, 6), (6, 19)), 4),
    )
    checks = []
    for name, stage, probes, limit in fixtures:
        rows, width = direct_rows(stage, probes)
        matrix = direct_table(rows, width, limit)
        assert matrix == table(stage, probes, limit)
        checks.append({
            "case": name, "literal_rows": len(rows), "width": width,
            "capped_pair_entries": width * (width - 1) // 2, "through_distance": limit,
        })
    classifier = {}
    for b in (4, 5, 6, 7):
        matrix = table(4, ((3, 9), (b, 8)))
        classifier[b] = sum(row.count(3) for row in matrix) // 2
    assert classifier == {4: 66, 5: 62, 6: 62, 7: 66}
    trapped = table(2, ((0, 7), (7, 10)))
    # The cap is exact in this example because every minimum is at most 4.
    assert max(map(max, trapped)) == 4
    assert all(trapped[12][i] == trapped[2][i] for i in range(16) if i not in (2, 12))
    terminal_probes = sorted_probes(((3, 6), (6, 19)))
    before_last = table(7, terminal_probes)
    wrong_side = ("gate", 7, (3, 18, 19))
    used_marker = ("gate", 7, (3, 19, 20))
    assert wrong_side not in read_actions(before_last)
    assert used_marker not in read_actions(before_last)
    assert ("gate", 7, (3, 18, 20)) in read_actions(before_last)
    return {
        "independent_literal_projection": checks,
        "distance_three_pair_counts_by_external_upper_old_name": classifier,
        "antipodal_endpoint_and_unused_original_are_exact_twins": [12, 2],
        "rejected_same_parent_corner_inputs": wrong_side,
        "rejected_consumption_of_crossing_marker": used_marker,
    }


def run():
    return {
        "meanings": {
            "terminal": "Eight genuine marked parity junctions, with both observable probes live.",
            "upper_marker": "Old YZ and the unconsumed upper-X outward distinction at XZ.",
            "face_test": "Lower XY and upper YZ.",
            "cap": "4, with every larger or absent entry read identically.",
            "physical_names": "Only for the offline universal-tie grader.",
        },
        "from_clean_first_horizontal_using_bulk": explore((2, ())),
        "from_clean_two_horizontal_children_individual": explore((3, ())),
        "from_clean_lower_square_individual": explore((4, ())),
        "compiled_readings": len(policy()),
        "local_checks": check_original_and_controls(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true", help="emit the certificate on stdout")
    args = parser.parse_args()
    result = run()
    if args.check:
        assert json.loads(json.dumps(result)) == json.loads(args.check.read_text())
    if args.json or not args.check:
        print(json.dumps(result, indent=2, sort_keys=True))
