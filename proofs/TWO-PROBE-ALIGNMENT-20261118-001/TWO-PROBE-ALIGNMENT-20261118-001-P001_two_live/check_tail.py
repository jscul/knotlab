"""Check a present-table policy for the 27 ordinary joins after the marked block."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import sys
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "proofs/ALIGNED-NEXT-JOIN-20261117-001"
          / "ALIGNED-NEXT-JOIN-20261117-001-P001_aligned_reader/check_aligned.py")
spec = importlib.util.spec_from_file_location("aligned_supports_for_tail", SOURCE)
aligned = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = aligned
spec.loader.exec_module(aligned)

DATA = aligned.short_supports(4)
MODEL = DATA.model
INDEX = {wire: i for i, wire in enumerate(MODEL.wires)}
N = len(INDEX)
SITE_BLOCK = frozenset(aligned.MARK_VERTICES)
MARKS = frozenset(MODEL.mark_bits)
BITS = aligned.bits
MASK = aligned.mask_of
ALL_ROWS = (1 << len(aligned.CUT_WORDS)) - 1


def site(word):
    return tuple(map(int, word))


def at(word, axis=2):
    return INDEX[site(word), axis]


PORT_PROBE = (at("101", 0), at("011"))
FACE_PROBE = (at("110"), at("011"))
ROOT_FACE = (at("000"), at("011"))
CROSS_FACE = (at("100"), at("001"))
LAST_JOINS = (
    "003", "012", "030", "102", "120", "210", "300", "004", "013", "022",
    "031", "040", "103", "112", "121", "130", "202", "211", "220", "301", "310", "400",
)


def submasks(word):
    value = word
    while value:
        yield value
        value = (value - 1) & word


@lru_cache(maxsize=1)
def conditional_words():
    """All words of at most six permanent bits determined given the original eight."""
    marked = MASK(MODEL.mark_bits)
    old_rows = [aligned.embed(row, MODEL.mark_bits) for row in sorted(aligned.CUT_WORDS)]
    mark_words = [aligned.embed(i, MODEL.mark_bits) for i in range(256)]
    values = {m: sum(((row & m).bit_count() % 2) << i for i, row in enumerate(old_rows))
              for m in mark_words}
    words = {}
    for cut in aligned.small_cuts(MODEL)[0].values():
        unmarked = cut & ~marked
        for obs in mark_words:
            word = unmarked | obs
            if word.bit_count() <= 6:
                signature = values[(cut & marked) ^ obs]
                assert words.setdefault(word, signature) == signature
    return words


def equal_slices(probes, arity):
    """Affine checks remaining on observations when all selected probe ends agree."""
    fixed = MASK({bit for probe in probes for bit in probe})
    for levels in product((0, 1), repeat=len(probes)):
        assignments = {}
        compatible = True
        for probe, level in zip(probes, levels):
            for bit in probe:
                if assignments.setdefault(bit, level) != level:
                    compatible = False
        if not compatible:
            yield 0, {}
            continue
        ones = MASK(i for i, level in assignments.items() if level)
        old_rows = ALL_ROWS
        reduced = {}
        for word, values in conditional_words().items():
            residual = word & ~fixed
            if residual.bit_count() > arity:
                continue
            expected = values ^ (ALL_ROWS if (word & ones).bit_count() % 2 else 0)
            if residual == 0:
                old_rows &= ~expected
            previous = reduced.setdefault(residual, expected)
            old_rows &= ~(previous ^ expected)
        # Re-express an observed tested middle after substitution.
        for i, level in assignments.items():
            reduced[1 << i] = ALL_ROWS if level else 0
        yield old_rows, reduced


def slice_is_free(observed, old_rows, words):
    if not old_rows:
        return False
    basis = {}
    for sub in submasks(observed):
        if sub not in words:
            continue
        vector, value = sub, words[sub]
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (vector, value)
                break
            vector ^= basis[pivot][0]
            value ^= basis[pivot][1]
    if (1 << len(basis)) > old_rows.bit_count():
        return False
    images = {tuple((values >> k) & 1 for _, values in basis.values()) for k in BITS(old_rows)}
    return len(images) == 1 << len(basis)


@lru_cache(None)
def short_bonds(probes):
    """Conditional parity calculation for all supports of size at most six."""
    answer = set(DATA.mixed)
    for count in range(1, len(probes) + 1):
        for indices in combinations(range(len(probes)), count):
            selected = tuple(probes[i] for i in indices)
            ends = MASK(N + 2*i + j for i in indices for j in (0, 1))
            cap = 6 - 2 * count
            slices = list(equal_slices(selected, cap))
            words = {word for _, family in slices for word in family if word}
            # Every member of a minimal candidate participates in a supported
            # conditional check. Otherwise it is free given the remaining bits.
            candidates = {0}
            for word in words:
                candidates.update({u | word for u in candidates if (u | word).bit_count() <= cap})
            for observed in sorted(candidates, key=lambda u: (u.bit_count(), u)):
                support = ends | observed
                if any(word in answer for word in submasks(support)):
                    continue
                if any(not slice_is_free(observed, rows, family) for rows, family in slices):
                    answer.add(support)
    assert all(3 <= m.bit_count() <= 6 for m in answer)
    return frozenset(answer)


@lru_cache(None)
def direct_permanent_rows(mask):
    ordered = tuple(BITS(mask))
    return tuple(aligned.embed(row, ordered) for row in aligned.projected_rows(MODEL, mask))


def direct_projection_size(support, probes):
    """Independent projection from actual ordinary components and literal betweennesses."""
    fixed = support & ((1 << N) - 1)
    selected = []
    for i, probe in enumerate(probes):
        ends = (3 << (N + 2*i)) & support
        if ends.bit_count() == 2:
            selected.append((ends, probe))
    necessary = fixed | MASK({bit for _, pair in selected for bit in pair})
    projected = set()
    for row in direct_permanent_rows(necessary):
        partial = {row & fixed}
        for ends, (a, b) in selected:
            i, j = BITS(ends)
            choices = [1 << i, 1 << j]
            left, right = (row >> a) & 1, (row >> b) & 1
            if left == right:
                choices.append(ends if left else 0)
            partial = {old | extension for old in partial for extension in choices}
        projected.update(partial)
    # Every single end without its mate is free independently.
    single = (support.bit_count() - fixed.bit_count() - 2 * len(selected))
    return len(projected) << single


def grade_projections(probes):
    bonds = short_bonds(probes)
    extra = bonds - DATA.mixed
    supports = {f ^ (1 << i) for f in extra for i in BITS(f)} | extra
    for f in supports:
        size = direct_projection_size(f, probes)
        if f in extra:
            assert 0 < size < 1 << f.bit_count()
        else:
            assert size == 1 << f.bit_count()
    # Exercise the canonical knot test on a genuine ternary betweenness.
    if probes:
        p, q = N, N + 1
        a, b = probes[0]
        allowed = {(v >> a & 1, x, y) for v in direct_permanent_rows(MASK((a, b)))
                   for x, y in product((0, 1), repeat=2)
                   if x != y or ((v >> a) & 1) == ((v >> b) & 1) == x}
        labels = ("middle", "p", "q")
        assert aligned.check_knot(aligned.Relation(labels, allowed), labels[:-1], labels[-1]).is_knot
    return {"new_short_bonds": len(extra), "literal_projections_checked": len(supports)}


def current_table(points, probes):
    ids = tuple(sorted([INDEX[v, a] for v in points for a in range(3)]
                       + list(range(N, N + 2*len(probes)))))
    where = {name: i for i, name in enumerate(ids)}
    present = MASK(ids)
    matrix = [[6] * len(ids) for _ in ids]
    for i in range(len(ids)):
        matrix[i][i] = 0
    # Every prefix is a marginal of the completed I4 with these same tests.
    # Restrict the SUPPORTS first, then minimize; restricting a matrix is wrong.
    for word in short_bonds(probes):
        if word & ~present:
            continue
        for i, j in combinations((where[k] for k in BITS(word)), 2):
            matrix[i][j] = matrix[j][i] = min(matrix[i][j], word.bit_count() - 1)
    return ids, matrix


def observe(matrix):
    """Invariant color refinement and complete dispatch key, without variable names."""
    colors = [0] * len(matrix)
    while True:
        profiles = [(colors[i], tuple(sorted((colors[j], distance) for j, distance in enumerate(row)
                                             if i != j))) for i, row in enumerate(matrix)]
        names = {signature: n for n, signature in enumerate(sorted(set(profiles)))}
        updated = [names[signature] for signature in profiles]
        if len(set(updated)) == len(set(colors)):
            return tuple(sorted(profiles)), updated
        colors = updated


def read(matrix, policy):
    """The running policy uses only this renamed matrix."""
    key, colors = observe(matrix)
    kind, requested = policy[key]
    choices = []
    pools = [[i for i, shade in enumerate(colors) if shade == target] for target in requested]
    for indices in product(*pools):
        if len(set(indices)) == len(indices):
            choices.append(tuple(sorted(indices)))
    return kind, set(choices)


def neighbor(v, axis, step):
    return tuple(x + (step if i == axis else 0) for i, x in enumerate(v))


def inputs(point):
    return tuple(INDEX[neighbor(point, a, -1), a] for a in range(3) if point[a])


def legal_parent_group(points, target):
    parents = [MODEL.wires[wire][0] for wire in target]
    if len(set(parents)) != len(parents) or not 1 <= len(parents) <= 3:
        return False
    neighbors = [{neighbor(u, a, step) for a in range(3) for step in (-1, 1)} & points
                 for u in parents]
    return (all(left & right for left, right in combinations(neighbors, 2))
            and (len(parents) < 3 or not set.intersection(*neighbors)))


def source_ties(points, probes, target):
    """Genuine input symmetries fixing every old mark and both middle identities of every probe."""
    held = MARKS | {bit for probe in probes for bit in probe}
    options = []
    for wire in target:
        point, axis = MODEL.wires[wire]
        assert point in points and neighbor(point, axis, 1) not in points
        if wire in held:
            options.append((wire,))
        else:
            options.append(tuple(INDEX[point, a] for a in range(3)
                                 if neighbor(point, a, 1) not in points and INDEX[point, a] not in held))
    return {tuple(sorted(choice)) for choice in product(*options)}


def trace():
    points = SITE_BLOCK
    probes = (PORT_PROBE, FACE_PROBE)
    program = ([("join", v) for v in ("200", "201", "020", "021")]
               + [("erase", 1), ("probe", ROOT_FACE), ("join", "002"),
                  ("erase", 1), ("probe", CROSS_FACE)]
               + [("join", v) for v in LAST_JOINS]
               + [("erase", 1), ("erase", 0)])
    for kind, arg in program:
        if kind == "join":
            point = site(arg)
            target = inputs(point)
            assert point not in points and all(MODEL.wires[x][0] in points for x in target)
            assert legal_parent_group(points, target)
            ties = source_ties(points, probes, target)
            next_state = points | {point}, probes
        elif kind == "erase":
            target = (N + 2*arg, N + 2*arg + 1)
            ties = {target}
            next_state = points, probes[:arg] + probes[arg+1:]
        else:
            target = tuple(sorted(arg))
            ties = {target}
            assert len(probes) < 2 and all(MODEL.wires[x][0] in points for x in target)
            next_state = points, probes + (arg,)
        yield points, probes, kind, target, ties, arg
        points, probes = next_state
    assert points == frozenset(MODEL.vertices) and not probes


def check_tail():
    policy = {}
    steps = list(trace())
    cases = []
    configurations = {probes for _, probes, *_ in steps}
    for points, probes, kind, target, allowed, arg in steps:
        ids, matrix = current_table(points, probes)
        key, shades = observe(matrix)
        assert key not in policy, "Two equal observations would request different updates"
        selected = tuple(sorted(shades[ids.index(bit)] for bit in target))
        policy[key] = kind, selected
        cases.append((ids, matrix, kind, target, allowed))
    terminal_ids, terminal_matrix = current_table(frozenset(MODEL.vertices), ())
    assert len(terminal_ids) == 105 and observe(terminal_matrix)[0] not in policy
    summary = []
    for step, case in zip(steps, cases):
        ids, matrix, kind, target, allowed = case
        base_choices = None
        for seed in (None, 131, 719):
            order = list(range(len(ids)))
            if seed is not None:
                random.Random(seed + len(ids)).shuffle(order)
            observation = [[matrix[i][j] for j in order] for i in order]
            operation, choices = read(observation, policy)
            lifted = {tuple(sorted(ids[order[i]] for i in choice)) for choice in choices}
            assert operation == kind and tuple(sorted(target)) in lifted and lifted <= allowed
            if base_choices is None:
                base_choices = lifted
            assert lifted == base_choices
        summary.append({"junctions_before": len(step[0]), "width": len(ids), "action": kind,
                        "site_or_pair": step[-1], "admitted_choices": len(base_choices)})
    total = Counter(case[2] for case in cases)
    assert total == {"join": 27, "probe": 2, "erase": 4}
    # This false upper/lower pairing would require parents four steps apart.
    bad = tuple(sorted([at("011", 1), at("200", 2)]))
    at_bridge = next(i for i, step in enumerate(steps) if step[-1] == "201")
    ids, matrix, _, _, _ = cases[at_bridge]
    _, choices = read(matrix, policy)
    assert bad not in {tuple(sorted(ids[i] for i in pair)) for pair in choices}
    assert not legal_parent_group(steps[at_bridge][0], bad)
    entry = cases[0][1]
    return {"entry_tests": [PORT_PROBE, FACE_PROBE],
            "entry_histogram": dict(sorted(Counter(entry[i][j] for i, j in combinations(range(len(entry)), 2)).items())),
            "entry_observation_sha256": hashlib.sha256(json.dumps(observe(entry)[0], separators=(",", ":")).encode()).hexdigest(),
            "probe_meanings": {"port": "x101,k011", "face": "k110,k011", "root_face": "k000,k011",
                               "cross_face": "k100,k001"},
            "permanent_joins": total["join"], "separate_probe_additions": total["probe"],
            "separate_pair_erasures": total["erase"], "policy_tables": len(policy),
            "base_permanent_short_bonds": len(DATA.mixed), "cutoff": 5,
            "conditional_projection_checks": [
                {"probes": pp, **grade_projections(pp)} for pp in sorted(configurations, key=repr)],
            "false_reflected_bridge_rejected": True, "tested_renaming_seeds": [131, 719],
            "terminal_width": len(terminal_ids), "steps": summary,
            "source_checker_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}


if __name__ == "__main__":
    print(json.dumps(check_tail(), indent=2, sort_keys=True))
