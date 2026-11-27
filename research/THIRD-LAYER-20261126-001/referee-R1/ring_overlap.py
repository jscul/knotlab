"""Two readings already used on one frozen construction, on five disjoint carriers."""
import argparse
from itertools import combinations, product
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from growth import families, grow, ring_start
from minima import Incidence
from scale_audit import ParityState, Span, xor_all

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def check_relation(words):
    names = ('a', 'b', 'c')
    forbidden = sorted(set(product((0, 1), repeat=3)) - set(words))
    cnf = ';'.join(' '.join(('~' if bit else '') + name
                             for bit, name in zip(word, names)) for word in forbidden)
    verdicts = []
    for contact in names:
        result = subprocess.run(
            [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--contact', contact,
             '--loops', *[name for name in names if name != contact], '--json'],
            cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')},
            check=True, capture_output=True, text=True)
        verdicts.append(json.loads(result.stdout)['is_knot'])
    return verdicts


def joint_image(stage, supports, removed=None):
    state = ParityState(stage)
    laws = state.laws if removed is None else Span(r for k, r in enumerate(state.knot_masks) if k != removed)
    vectors = [laws.reduce(state.mask(c)) for c in supports]
    relations = [pick for pick in product((0, 1), repeat=5)
                 if not xor_all(v for b, v in zip(pick, vectors) if b)]
    words = [w for w in product((0, 1), repeat=5)
             if all(sum(b*c for b, c in zip(w, eq)) % 2 == 0 for eq in relations)]
    return state, relations, words


def layer_moves(words, indexes):
    moves = set()
    for i in range(5):
        through = [w for w in words if w[i]]
        minimum = min(map(sum, through))
        moves.update(w for w in through if sum(w) == minimum)
    as_int = lambda w: sum(b << j for j, b in enumerate(w))
    rank = len(Span(map(as_int, moves)))
    return {'distinct shortest changes': sorted(moves), 'rank of shortest changes': rank,
            'class-fact dimension': len(Span(map(as_int,words))) - rank,
            'triple indices':indexes}


def inspect(stage, supports, t):
    state, relations, words = joint_image(stage, supports)
    inputs = [(0, 1, 2), (3, 4, 0)]
    triples = [sorted({tuple(w[i] for i in ids) for w in words}) for ids in inputs]
    assert len(words) == 8 and len(relations) == 4
    assert all(triple == [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)] for triple in triples)
    # All are given actual disjoint carriers even across different triples.
    assert all(set(a).isdisjoint(b) for a, b in combinations(supports, 2))
    incidence = Incidence(stage)
    least = {state.mask(c): incidence.least(c) for c in supports}
    bounds = [least[state.mask(c)] for c in supports]
    profile = state.local_pair_minima()
    fixed = [len(state.knot_groups(m, p)) for m, p in zip(state.knot_masks, profile)]
    windows = {}
    for scale in sorted({5, min(bounds)-1, min(bounds)}):
        reader = state.reading_at_scale(scale, profile, fixed, least)
        windows[scale] = {'flags': reader.flags(supports), **reader.ranks(supports)}
    shortest = state.reading_of_moves(state.shortest_span())
    return {'round': t, 'knots':len(stage), 'distinctions':len(state.names), 'least flips': bounds,
            'supports':supports, 'words':words, 'relations including zero':relations,
            'two projected relations':triples, 'own shortest changes':layer_moves(words, inputs),
            'shortest':{'flags':shortest.flags(supports), **shortest.ranks(supports)}, 'by scale':windows}


def run(last):
    start, rings, ring_loose = ring_start(3, 4, 'split', 'double')
    group, _ = families(start)
    halves = [set(g) for g in group if set(g) <= set(rings[0])]
    assert len(halves) == 2
    stage = start
    rows = []
    for t in range(1, last + 1):
        stage, status, births = grow(stage)
        assert status == 'funded'
        if t == 1:
            # Entire first-round outputs of the two parts of the first ring.
            fresh = [tuple(d for b in births if set(b['parents']) <= half for d in b['fresh'])
                     for half in halves]
            assert all(fresh)
            supports = list(ring_loose) + fresh
        if t in (1, 4, 5, 6):
            row = inspect(stage, supports, t)
            state = ParityState(stage)
            for half, check in zip(halves, fresh):
                original = [d for i in half for d in start[i] if d in set(ring_loose[0])]
                assert state.laws.reduce(state.mask(original) ^ state.mask(check)) == 0
            if t in (1,5):
                # Dropping one original law and dropping one first-ring birth law
                # can separate the two equations on these exact five carriers.
                drops = {}
                keys = {0: 'one source ring law',
                        len(start): 'one first-ring birth law'}
                for i, what in keys.items():
                    _, rels, values = joint_image(stage, supports, removed=i)
                    drops[what] = {'removed knot': i, 'words':values, 'relations including zero':rels}
                assert set(drops['one source ring law']['relations including zero']) == {
                    (0,0,0,0,0), (1,0,0,1,1)}
                assert set(drops['one first-ring birth law']['relations including zero']) == {
                    (0,0,0,0,0), (1,1,1,0,0)}
                row['law deletions'] = drops
            rows.append(row)
    unique = {tuple(tuple(w) for w in projection)
              for row in rows for projection in row['two projected relations']}
    checks = [{'words': words, 'each contact passes': check_relation(words)} for words in unique]
    assert all(all(item['each contact passes']) for item in checks)
    return {'construction':'Three rings of four knots with split attachments and double links',
            'order of five facts':['whole first ring','whole second ring','whole third ring',
                                   'first alternating family of first ring','other alternating family of first ring'],
            'first-ring family holders':list(map(sorted,halves)), 'stages':rows, 'canonical checks':checks}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (1536 << 20, 1536 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    began = perf_counter()
    out = run(1 if args.pilot else 6)
    for row in out['stages']:
        print(row['round'],row['least flips'], {k:[f['a sum of single-knot facts'] for f in v['flags']]
                                               for k,v in row['by scale'].items()})
    if not args.pilot:
        (HERE / 'ring_overlap_counts.json').write_text(json.dumps(out, indent=2) + '\n')
    print('Elapsed seconds',round(perf_counter() - began, 3))


if __name__ == '__main__':
    main()
