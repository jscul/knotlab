"""Find a kind whose last departure is earlier after its binomial terms are summed."""

import argparse
import gzip
import json
import resource
import time
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

from map_predict import Piece, Start, elements, evaluate, make_piece, subsets, with_extra_loose


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'LOOK-ALIKE-20261126-001' / 'phase1_grown.jsonl.gz'


def series_for_start(stars):
    start = Start(stars, 'nae')
    if start.reason != 'predicted':
        return None
    pieces = []
    for live in start.pieces:
        p = make_piece(start, live, 'frozen', None)
        relay = not p.ray_owner
        pieces.append((p, relay, 0))
        if relay:
            w = p.rank[p.whole]
            desc = with_extra_loose(p.sig(p.whole, 0))
            pieces.append((Piece({1: w, 3: w+1}, [], {1: 2, 2: 2}, {1: desc}, 'frozen'), False, 1))
    grouped = {'unsplit birth kind': defaultdict(Counter), 'with parent kinds': defaultdict(Counter)}
    dimension = 0
    for p, relay, skip in pieces:
        for s, weight in p.rank.items():
            if s == skip:
                continue
            for rays in subsets(p.active[s]):
                k = rays.bit_count()
                dimension = max(dimension, k)
                sig = p.sig(s, rays)
                if s == p.whole and relay:
                    sig = with_extra_loose(sig)
                # A single (core, active chains) contributes x^(w-1+k)/(1-x)^k
                # when the reading omits the descriptions of the parents.
                first = weight - 1 + k
                grouped['unsplit birth kind'][sig][first, k] += 1
                core_parents = tuple(p.sig(t, rays) for t in p.parents(s, rays))
                for short in subsets(rays):
                    q = k - short.bit_count()
                    parents = core_parents + tuple(p.sig(s, rays ^ a) for a in elements(short)) + (sig,) * q
                    grouped['with parent kinds'][sig, tuple(sorted(parents))][first+q, q] += 1
    return grouped, dimension


def extended_binomial(top, bottom):
    return (-1)**bottom * comb(bottom - top - 1, bottom) if top < 0 else comb(top, bottom)


def coefficients(terms, t):
    observed, eventual = 0, 0
    for (first, q), multiplicity in terms.items():
        if q == 0:
            observed += multiplicity * (t == first)
        else:
            term = multiplicity * extended_binomial(t - first + q - 1, q - 1)
            eventual += term
            if t >= first:
                observed += term
    return observed, eventual


def describe(terms):
    nominal = max(first-q for first, q in terms)
    last = max((t for t in range(1, nominal+1) if len(set(coefficients(terms, t))) != 1), default=0)
    return nominal, last


def observed_cut(views, dimension):
    kinds = set().union(*(r.keys() for r in views))
    for k in range(max(3, dimension), len(views)-1):
        for name in kinds:
            samples = [row.get(name, 0) for row in views[k-dimension:]]
            for _ in range(dimension):
                samples = [b-a for a, b in zip(samples, samples[1:])]
            if any(samples):
                break
        else:
            return k
    return None


def witness(raw, groups, dimension, read):
    by_kind = groups[read]
    departures = {key: describe(terms) for key, terms in by_kind.items()}
    nominal_cut = max(3, dimension, max(a+dimension for a, _ in departures.values()))
    actual_cut = max(3, dimension, max(b+dimension for _, b in departures.values()))
    archived = evaluate(raw['stars'], 24, 'nae')
    if archived['K1' if read == 'with parent kinds' else 'K0'] != actual_cut:
        raise AssertionError('disagreement with numerator-degree method')
    cancellers = [(key, a, b) for key, (a, b) in departures.items() if a > b and a >= 1]
    if not cancellers:
        return None
    key, nominal, actual = max(cancellers, key=lambda item: (item[1], item[1]-item[2]))
    terms = by_kind[key]
    level = 'sig1' if read == 'with parent kinds' else 'sig0'
    views = [{json.dumps(j): n for j, n in r[level]} for r in raw['rows']]
    observed = [view.get(json.dumps(key), 0) for view in views]
    if observed != [coefficients(terms, t)[0] for t in range(1, len(views)+1)]:
        raise AssertionError('selected kind disagrees with the saved births')
    fit_cut = observed_cut(views, dimension)
    if fit_cut != actual_cut:
        raise AssertionError('predicted cut disagrees with the saved births')
    return {'sample': 'one- through four-knot census, not-all-equal', 'start knots': raw['stars'],
            'census entry for its knot count': raw['index'], 'number of knots': len(raw['stars']),
            'reading': read, 'kind': key, 'dimension': dimension,
            'individual last departure, largest': nominal, 'summed last departure for this kind': actual,
            'global cut using largest individual departure': nominal_cut, 'true global cut': actual_cut,
            'interpolation cut from the saved counts': fit_cut, 'saved counts for the selected kind': observed,
            'terms, each multiplicity times x^first / (1-x)^q': [
                {'first': first, 'q': q, 'multiplicity': n} for (first, q), n in sorted(terms.items())],
            'individual contributions at largest departure': [
                {'first': first, 'q': q, 'multiplicity': n, 'count, eventual polynomial': coefficients({(first, q): n}, nominal)}
                for (first, q), n in sorted(terms.items())],
            'round, count, eventual polynomial': [[t, *coefficients(terms, t)] for t in range(1, nominal+3)]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', required=True, type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    beginning = time.monotonic()
    count = 0
    first = {}
    global_impact = {}
    with gzip.open(SOURCE, 'rt') as stream:
        for line in stream:
            if count >= args.limit:
                break
            raw = json.loads(line)
            count += 1
            computed = series_for_start(raw['stars'])
            if computed is None:
                continue
            groups, dim = computed
            for read in groups:
                case = witness(raw, groups, dim, read)
                if case:
                    first.setdefault(read, case)
                    if case['global cut using largest individual departure'] > case['true global cut']:
                        global_impact.setdefault(read, case)
            if len(global_impact) == 2:
                break
    result = {'prefix limit': args.limit, 'number of starts examined': count, 'first cancellations': first,
              'first cancellations that change the global cut': global_impact,
              'elapsed seconds': round(time.monotonic()-beginning, 4),
              'peak KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print('starts read', count, 'readings with local, global cancellation', len(first), len(global_impact))


if __name__ == '__main__':
    main()
