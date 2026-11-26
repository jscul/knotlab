"""Compare complete late readings and sufficient start descriptions between the fitting and held-out samples."""
import argparse
from collections import Counter, defaultdict
import gzip
from itertools import permutations, islice
import json
from pathlib import Path
from time import perf_counter

OUT = Path(__file__).resolve().parent
FIT = OUT.parent.parent / "SETTLE-BOUND-20261126-001"


def tuples(value):
    if isinstance(value, list):
        return tuple(tuples(v) for v in value)
    return value


def ticks(record):
    return tuple(tuple(sorted((tuples(kind), count) for kind, count in r['sig0'])) for r in record['rows'])


def exceeds_cut(stages, degree_plus_one, cut):
    # After the cut every difference of order D must vanish for every birth kind.
    for kind in set(k for s in stages for k, _ in s):
        values = [dict(s).get(kind, 0) for s in stages]
        for _ in range(degree_plus_one):
            values = [v - u for u, v in zip(values, values[1:])]
        if any(values[cut - degree_plus_one:]):
            return True
    return False


def start_description(stars, with_places):
    # Lemma R. Singletons cannot supply a pair or a larger group, so can be omitted.
    holdings = [set(knot) for knot in stars]
    occurs = Counter(d for knot in holdings for d in knot)
    loose = [sum(occurs[d] == 1 for d in knot) for knot in holdings]
    live = [i for i, n in enumerate(loose) if n]
    blocks = {frozenset(i for i in live if i != w and holdings[w] & holdings[i]) for w in range(len(stars))}
    blocks = [b for b in blocks if len(b) >= 2 and not any(b < c for c in blocks)]
    colors = {i: (loose[i], len(stars[i])) if with_places else (loose[i],) for i in live}
    # Fix the order of colors first; every permutation within equal colors is admitted.
    pattern = tuple(sorted(colors.values()))
    descriptions = []
    for order in permutations(live):
        if tuple(colors[i] for i in order) == pattern:
            rename = {i: j for j, i in enumerate(order)}
            descriptions.append(tuple(sorted(tuple(sorted(rename[i] for i in b)) for b in blocks)))
    return pattern, min(descriptions)


def collect(path, limit):
    examples = []
    with gzip.open(path, "rt") as data:
        for line in islice(data, limit):
            x = json.loads(line)
            if not x['kind'].startswith('dim ') or len(x['rows']) != 24:
                continue
            basic = ticks(x)
            d = int(x['kind'].split()[1])
            if not exceeds_cut(basic, d, x['M'] + 5):
                continue
            rich = tuple(tuple(sorted((tuples(k), n) for k, n in r['sig1'])) for r in x['rows'])
            total = tuple(row['n'] for row in x['rows'])
            keys = {
                'birth totals': total,
                'reading without parents': basic,
                'both readings from round two': (basic[1:], rich[1:]),
                'both readings from round one': (basic, rich),
                'reduced start, loose counts': start_description(x['stars'], False),
                'reduced start, loose counts and places of live knots': start_description(x['stars'], True),
            }
            last_fall = max((i for i in range(2, 25) if total[i - 1] < total[i - 2]), default=1)
            joins = [sum(n for k, n in row if k[1] >= 2) for row in basic]
            examples.append(({'knots': len(x['stars']), 'census index': x['index'],
                              'last fall': last_fall, 'joins at fall': joins[last_fall - 1],
                              'joins at round 24': joins[-1], 'births at fall': total[last_fall - 1]},
                             {k: (d, x['M'], v) for k, v in keys.items()}))
    return examples


def summarize(earlier, fresh):
    methods = list(next((keys for _, keys in earlier + fresh), {}))
    result = {}
    for method in methods:
        known = defaultdict(list)
        for meta, keys in earlier:
            known[keys[method]].append(meta)
        counts = Counter(keys[method] for _, keys in fresh)
        matched = [m for m, k in fresh if k[method] in known]
        result[method] = {
            'earlier unique': len(known), 'fresh unique': len(counts), 'matched fresh starts': len(matched),
            'matched distinct descriptions': len(set(counts).intersection(known)),
            'classes': [{
                'fresh starts': [m['census index'] for m, k in fresh if k[method] == key],
                'matching earlier starts': [[m['knots'], m['census index']] for m in known.get(key, [])],
            } for key in counts],
        }
    return {'number earlier': len(earlier), 'number fresh': len(fresh),
            'starts': [m for m, _ in fresh], 'comparison': result}


def first_round_lookup(paths, fresh_path, limit):
    """An earlier lookup can answer only keys that gave one verdict in the fitting runs."""
    def labelled(path):
        with gzip.open(path, "rt") as stream:
            for line in islice(stream, limit):
                rec = json.loads(line)
                if len(rec['rows']) != 24 or not rec['kind'].startswith('dim '):
                    continue
                m = rec['M']
                d = int(rec['kind'].split()[1])
                readings = ticks(rec)
                late = exceeds_cut(readings, d, m + 5)
                yield ((m, readings[0]), late, (len(rec['stars']), rec['index']))

    earlier = defaultdict(dict)
    for path in paths:
        for key, verdict, start in labelled(path):
            earlier[key].setdefault(verdict, start)
    results = defaultdict(Counter)
    conflicts = []
    for key, late, start in labelled(fresh_path):
        verdicts = earlier.get(key, {})
        outcome = ('unknown' if not verdicts else 'mixed earlier verdicts' if len(verdicts) > 1
                   else 'correct' if late in verdicts else 'incorrect')
        results['late' if late else 'at or below M plus five'][outcome] += 1
        if late and False in verdicts:
            conflicts.append({'late held-out start': start, 'earlier start within cutoff': verdicts[False], 'M': key[0]})
    return {'key': 'M and the first round without parent descriptions; full 24-round runs labelled 1 through 4',
            'counts': {k: dict(v) for k, v in results.items()}, 'conflicts': conflicts}


def audit(limit):
    answer = {}
    t0 = perf_counter()
    for law, suffix in [('nae', 'nae'), ('parity', 'par')]:
        paths = [FIT / f'grown_g{size}_{suffix}.jsonl.gz' for size in (5, 6)]
        fresh_path = OUT.parent / f'grown_fresh_{law}.jsonl.gz'
        earlier = [case for path in paths for case in collect(path, limit)]
        fresh = collect(fresh_path, limit)
        answer[law] = summarize(earlier, fresh)
        answer[law]['earlier first-round lookup'] = first_round_lookup(paths, fresh_path, limit)
    answer['comparison rule'] = 'Same law, dimension label, M, and indicated description. Both samples restricted to late complete 24-round runs. Earlier starts are given as [number of knots, census index].'
    answer['elapsed seconds'] = round(perf_counter() - t0, 3)
    return answer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='first 200 records per archive')
    args = parser.parse_args()
    result = audit(200 if args.pilot else None)
    target = OUT / ('overlap_pilot.json' if args.pilot else 'overlap.json')
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(target.name, result['elapsed seconds'])
    for law in ('nae', 'parity'):
        print(law, [(k, v['fresh unique'], v['matched fresh starts']) for k, v in result[law]['comparison'].items()])
