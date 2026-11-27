"""Compare the exhaustive bond reduction with literal enumeration on eight distinctions."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import resource
import time

from step_nonpaired import Stage, encode


HERE = Path(__file__).resolve().parent
SUPPORTS = ((0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0))


def lower_agreement(word, carrier):
    return word & carrier in (0, carrier)


def main(pilot):
    began = time.monotonic()
    laws = list(map(encode, SUPPORTS))
    stages = [word for word in range(256) if all(not lower_agreement(word, law) for law in laws)]
    allowed = set(stages)
    all_carriers = [encode(carrier) for size in (2, 3) for carrier in combinations(range(8), size)]
    local = {}
    for c in all_carriers:
        local[c] = False
        for law in laws:
            on, off = ({word & law for word in stages if lower_agreement(word, c) == v} for v in (1, 0))
            if not on & off:
                local[c] = True
                break
    nonlocal_carriers = sorted(c for c in all_carriers if not local[c])
    lower_bits = {c: sum(1 << i for i, word in enumerate(stages) if lower_agreement(word, c))
                  for c in all_carriers}
    bonds = {}
    tested = 0
    for a, b, c in combinations(nonlocal_carriers, 3):
        if a & b or b & c or a & c:
            continue
        tested += 1
        by_lower = [0] * 8
        for i, word in enumerate(stages):
            low = tuple(lower_agreement(word, k) for k in (a, b, c))
            w = 4 * low[0] + 2 * low[1] + low[2]
            by_lower[w] |= 1 << i
        realizable = {w for w, present in enumerate(by_lower) if present}
        if 0 < len(realizable) < 8 and all(len({w & pair for w in realizable}) == 4 for pair in (3, 5, 6)):
            bonds[a, b, c] = by_lower

    result = Counter()
    examples = {}
    possible_shapes = Counter()
    stage = Stage(SUPPORTS)
    covers_by_shape = {}
    one_witness = Stage(SUPPORTS, n_samples=1)
    checked_sparse = set()
    for a, b in combinations(all_carriers, 2):
        if a & b or (a | b).bit_count() < 5:
            continue
        for both in (True, False):
            upper_bits = lower_bits[a] & lower_bits[b] if both else lower_bits[a] | lower_bits[b]
            u0 = {word for i, word in enumerate(stages) if not (upper_bits >> i) & 1}
            u1 = allowed - u0
            mandatory = [d for d in range(8) if (a | b) & (1 << d)]
            if not all(any((word ^ (1 << d)) in u1 for word in u0) for d in mandatory):
                continue
            if pilot and result['queries'] >= 4:
                continue
            direct = {cs for cs, parts in bonds.items() if not (a in cs and b in cs) and
                      not any(part & upper_bits and part & ~upper_bits for part in parts)}
            counts, reduced = stage.consider(a, b, both)
            assert direct == set(reduced), (a, b, both, direct, reduced)
            arities = tuple(sorted((a.bit_count(), b.bit_count())))
            if arities not in covers_by_shape:
                direct_covers = sum(not (x & y or x & z or y & z)
                                    and (x | y | z) & (a | b) == a | b
                                    and not (a in (x, y, z) and b in (x, y, z))
                                    for x, y, z in combinations(all_carriers, 3))
                assert counts['all_disjoint_nonpaired_covers'] == direct_covers
                covers_by_shape[arities] = direct_covers
            shapes = tuple(sorted({sum(bool(c & (a | b)) for c in cs) for cs in direct}))
            if shapes not in checked_sparse:
                assert set(one_witness.consider(a, b, both)[1]) == direct
                checked_sparse.add(shapes)
            for n_touch in (2, 3):
                term = f'determining_{n_touch}'
                subset = {cs for cs in direct if sum(bool(c & (a | b)) for c in cs) == n_touch}
                assert counts[term] == len(subset)
                if subset:
                    possible_shapes[n_touch] += 1
                    if n_touch not in examples:
                        examples[n_touch] = {'named_masks': [a, b], 'both': both,
                                             'lower_carrier_masks': sorted(subset)[0]}
            result.update(counts)
            result['queries'] += 1
    stage.close()
    one_witness.close()
    out = {'source_knots': SUPPORTS, 'allowed_states': len(stages),
           'disjoint_nonlocal_triples': tested, 'eligible_stage_bonds': len(bonds),
           'direct_agreement_with_reduction': dict(result), 'queries_with_determiner_by_shape': possible_shapes,
           'direct_raw_disjoint_covers_by_named_arities': {str(k): v for k, v in covers_by_shape.items()},
           'one_raw_assignment_pool_checked_shapes_including_empty': sorted(checked_sparse),
           'positive_controls': examples, 'seconds': round(time.monotonic() - began, 4),
           'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if not pilot:
        assert examples.keys() == {2, 3}
    path = HERE / ('step_nonpaired_controls_pilot.json' if pilot else 'step_nonpaired_controls.json')
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pilot', action='store_true')
    main(ap.parse_args().pilot)
