"""Independent truth-column check of the row classes used in the obstruction."""

from itertools import combinations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def rooted_rows(dimension):
    count = 1 << dimension
    ones = (1 << count) - 1
    cut = {0, ones}
    for axis in range(dimension):
        word = sum(((v >> axis) & 1) << v for v in range(count))
        cut.update((word, ones ^ word))
    # Choose original 0 as root; p0 and p1 are its two fresh parity outputs.
    return {word | (u << count) | ((u ^ (word & 1)) << (count + 1))
            for word in cut for u in (0, 1)}


def test_rows(base, size, pair):
    a, b = pair
    rows = []
    for word in sorted(base):
        a_value = (word >> a) & 1
        b_value = (word >> b) & 1
        for left in (0, 1):
            for right in (0, 1):
                if left != right or a_value == b_value == left:
                    rows.append(word | (left << size) | (right << (size + 1)))
    return rows


class Projection:
    def __init__(self, rows, width):
        self.all_rows = (1 << len(rows)) - 1
        self.columns = []
        for bit in range(width):
            ones = sum(((row >> bit) & 1) << j for j, row in enumerate(rows))
            self.columns.append((self.all_rows ^ ones, ones))

    def full(self, *bits):
        parts = [self.all_rows]
        for bit in bits:
            parts = [part & chosen for part in parts for chosen in self.columns[bit]]
            if 0 in parts:
                return False
        return True


def toward_endpoint(rows, permanent):
    """Every minimal support involving a test endpoint also contains its mate."""
    end, mate = permanent, permanent + 1
    proj = Projection(rows, permanent + 2)
    assert all(proj.full(a, b) for a, b in combinations(range(permanent + 2), 2))
    free_threes = {i for i in range(permanent) if proj.full(end, mate, i)}
    distances = {}
    for old in range(1, permanent - 2):
        if old not in free_threes:
            distances[old] = 2
        else:
            # Both projections without an endpoint are free: one unpaired end
            # has both values above every permanent pair. The other deletions
            # are precisely the two free three-place tests.
            assert any(not proj.full(end, mate, old, j) for j in free_threes - {old})
            distances[old] = 3
    return distances


def check(dimension):
    old_count = 1 << dimension
    permanent = old_count + 2
    anchors = {0, old_count, old_count + 1}
    neighbors = {1 << i for i in range(dimension)}
    unused = set(range(1, old_count))
    base = rooted_rows(dimension)
    all_tests = list(combinations(range(permanent), 2))
    favorable = {tuple(sorted((a, n))) for a in anchors for n in neighbors}
    adverse = [None, *(pair for pair in all_tests if pair not in favorable)]
    by_test = {}
    measured = 0
    for a, b in all_tests:
        seen = toward_endpoint(test_rows(base, permanent, (a, b)), permanent)
        if b < old_count:
            interval = {v for v in unused if (v ^ a) & ~(a ^ b) == 0}
        else:
            interval = {a} & unused
        assert seen == {v: 2 if v in interval else 3 for v in unused}
        by_test[a, b] = interval
        measured += len(seen)
    by_test[None] = set()
    escaping_types = []
    replacement_orbits = 0
    for query in adverse:
        inside = by_test[query]
        groups = [g for g in [inside, unused - inside] if g]
        if any(g <= neighbors for g in groups):
            escaping_types.append(query)
            continue
        colors = {a: a for a in anchors}
        for group in groups:
            colors.update(dict.fromkeys(group, min(group)))
        possible = {}
        for new_query in all_tests:
            kind = tuple(sorted(colors[v] for v in new_query))
            possible.setdefault(kind, []).append(new_query)
        assert all(any(q not in favorable for q in options) for options in possible.values())
        replacement_orbits += len(possible)
    if dimension >= 3:
        assert not escaping_types
    else:
        # A single marked opposite leaves just the two genuine neighbors.
        assert (3, old_count) in escaping_types
    return {'dimension': dimension, 'originals': old_count, 'rooted_probe_choices': len(all_tests),
            'endpoint_distances_to_unused_originals_checked': measured,
            'adverse_probes_plus_idle': len(adverse),
            'adverse_types_with_a_class_entirely_of_neighbors': len(escaping_types),
            'replacement_orbits_with_a_verified_adverse_resolution': replacement_orbits,
            'full_mixed_tables_computed_here': False}


def exact_target_prefix():
    """Could a different parity presentation of the literal I4 absorb a wrong move?"""
    root = Path(__file__).resolve().parents[3]
    source = (root / 'proofs/ALIGNED-NEXT-JOIN-20261117-001'
              / 'ALIGNED-NEXT-JOIN-20261117-001-P001_aligned_reader/check_aligned.py')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == (
        'caeec42b1cb75491e43d0510d8af6ac53c96b8bf754189eb45cd6af01e006b14'
    )
    spec = importlib.util.spec_from_file_location('one_probe_literal_target', source)
    aligned = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = aligned
    spec.loader.exec_module(aligned)
    data = aligned.short_supports(4)
    model = data.model
    marks = aligned.mask_of(model.mark_bits)
    even = {}
    for size in (3, 4):
        wanted = {w for w in range(1 << size) if w.bit_count() % 2 == 0}
        even[size] = [mask for mask in data.mixed if mask.bit_count() == size
                      and aligned.projected_rows(model, mask) == wanted]
    first, = (m for m in even[3] if (m & marks).bit_count() == 1)
    second = [m for m in even[4] if (m & first).bit_count() == 1]
    old_counts = [(m & marks & ~first).bit_count() for m in second]
    actual = [m for m in second if (m & marks & ~first).bit_count() == 1]
    coords = sorted(model.wires[bit][0] for m in actual for bit in aligned.bits(m & marks & ~first))
    assert first in model.stars and all(m in model.stars for m in actual)
    assert coords == [(0, 0, 1), (0, 1, 0), (1, 0, 0)]
    assert sorted(old_counts) == [1, 1, 1, 3]
    return {'full_even_ternaries': len(even[3]), 'full_even_quaternaries': len(even[4]),
            'first_stars_reusing_one_original': 1,
            'second_supports_by_number_of_newly_used_originals': sorted(old_counts),
            'source_compatible_second_originals': coords}


if __name__ == '__main__':
    print(json.dumps({'first_neighbor_size_controls': [check(d) for d in (2, 3, 4)],
                      'exact_target_prefix': exact_target_prefix()}, indent=2))
