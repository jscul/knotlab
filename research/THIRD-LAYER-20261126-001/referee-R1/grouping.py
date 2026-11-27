"""Test the proposed binding claim for arbitrary loose groups on a funded ring."""
import argparse
from collections import defaultdict
import itertools
import json
from pathlib import Path
import resource
import time


def as_mask(names):
    return sum(1 << x for x in names)


def reduced(v, pivots):
    for p in sorted(pivots, reverse=True):
        if v >> p & 1:
            v ^= pivots[p]
    return v


def pivots_for(rows):
    pivots = {}
    for row in rows:
        value = reduced(row, pivots)
        if value:
            pivots[value.bit_length() - 1] = value
    return pivots


def check_first_sizes(stage, facts):
    """All changing sets through size three; joint images follow by row elimination."""
    names = sorted(set(itertools.chain.from_iterable(stage)))
    columns = defaultdict(int)
    for i, knot in enumerate(stage):
        for d in knot:
            columns[d] |= 1 << i
    # A three-change x,y,z is allowed iff the first two columns sum to the third.
    by_column = defaultdict(list)
    for d in names:
        by_column[columns[d]].append(d)
    masks = [as_mask(g) for g in facts]
    changes = {2: [], 3: []}
    for i, x in enumerate(names):
        assert columns[x]
        for y in names[i+1:]:
            total = columns[x] ^ columns[y]
            if total == 0:
                changes[2].append((x, y))
            for z in by_column.get(total, ()):
                if z > y:
                    changes[3].append((x, y, z))
    found = [None] * len(facts)
    for size, moves in changes.items():
        for move in moves:
            v = as_mask(move)
            for j, g in enumerate(masks):
                if (v & g).bit_count() % 2 and found[j] is None:
                    found[j] = list(move)
    rows = [as_mask(knot) for knot in stage]
    pivots = pivots_for(rows)
    relations = []
    for bits in itertools.product((0, 1), repeat=3):
        f = 0
        for bit, g in zip(bits, masks):
            if bit:
                f ^= g
        if reduced(f, pivots) == 0:
            relations.append(bits)
    words = [''.join(map(str, w)) for w in itertools.product((0, 1), repeat=3)
             if all(sum(a*b for a, b in zip(w, rel)) % 2 == 0 for rel in relations)]
    # A parity readable on a single knot belongs to the span of that knot's
    # individual coordinates and the laws. Test all three separately.
    readers = [0, 0, 0]
    for knot in stage:
        local = pivots_for([*pivots.values(), *(1 << x for x in knot)])
        for j, fact in enumerate(masks):
            readers[j] += reduced(fact, local) == 0
    return {'distinctions': len(names), 'knots': len(stage), 'tuples': words,
            'single-knot readers': readers, 'witnesses of at most three': found,
            'allowed changes at size 2, 3': [len(changes[k]) for k in (2, 3)]}


def run(rounds):
    from growth import grow, families
    n = 9
    # Distinction i joins starting knots i and i+1. The other two names are loose.
    start = tuple(((i - 1) % n, i, n + 2*i, n + 2*i + 1) for i in range(n))
    supports = [tuple(d for knot in start[j:j+3] for d in knot[2:]) for j in (0, 3, 6)]
    actual_families, _ = families(start)
    assert len(actual_families) == 1
    stage = start
    certificate = []
    witnesses = []
    for t in range(rounds + 1):
        counts = check_first_sizes(stage, supports)
        assert counts['tuples'] == ['000', '011', '101', '110']
        assert counts['single-knot readers'] == [0, 0, 0]
        if t == 0:
            assert all(len(w) == 3 for w in counts['witnesses of at most three'])
            counts['least flipping sizes'] = [3, 3, 3]
        else:
            assert counts['witnesses of at most three'] == [None] * 3
            for group, w in enumerate(witnesses):
                assert len(w) == 4 and len(set(supports[group]) & set(w)) % 2
                assert all(len(set(knot) & set(w)) % 2 == 0 for knot in stage)
            counts['least flipping sizes'] = [4, 4, 4]
        counts['round'] = t
        certificate.append(counts)
        if t != rounds:
            stage, status, births = grow(stage)
            assert status == 'funded'
            if t == 0:
                for group in range(3):
                    # Two parents i,i+2 lie in different groups. Their joint
                    # birth and the two consecutive start links close the change.
                    i = 3 * group + 1
                    j = (i + 2) % n
                    b, = [b for b in births if set(b['parents']) == {i, j}]
                    witnesses.append(sorted([i, (i + 1) % n, *b['inputs']]))
    return {'start': start, 'three chosen groups of loose distinctions': supports,
            'true candidate families': actual_families, 'fixed four-changes': witnesses, 'stages': certificate}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (1536 << 20, 1536 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    t = time.perf_counter()
    counts = run(1 if args.pilot else 12)
    if not args.pilot:
        Path(__file__).with_name('grouping_counts.json').write_text(json.dumps(counts, indent=2) + '\n')
    print('Rounds checked', len(counts['stages']), 'elapsed seconds', round(time.perf_counter() - t, 3))


if __name__ == '__main__':
    main()
