"""tally.py: the census's counts against the frozen predictions (README.md, "Results").

    tally.py RESULTS            the census results: the longrun output folder, or census_results.jsonl.gz unpacked"""
import sys, json, collections, gzip
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from longrun import load_results
import sides as S

HERE = Path(__file__).resolve().parent


def rows_of(path):
    recs = load_results(path)
    bad = [c for c, r in recs.items() if r['status'] != 'ok']
    rows = [row for r in recs.values() if r['status'] == 'ok' for row in r['result']['rows']]
    return rows, bad, len(recs)


def main(path):
    rows, bad, ncases = rows_of(path)
    print(f'# Census tally\n\n{ncases} cases, {len(bad)} not ok {bad[:5]}; {len(rows)} stages with a swap.\n')
    notrun = collections.Counter((r['law'], r['round']) for r in rows if isinstance(r['classes'], str))
    print('Stages not run (too many states):', dict(notrun), '\n')
    # P2: flipped states
    viol_fixed, viol_parity, flipped, flipped_m = 0, [], collections.Counter(), collections.Counter()
    for r in rows:
        if isinstance(r['classes'], str): continue
        for c in r['classes']:
            L = c.get('labels')
            if not L: continue
            if L['n_A'] and L['fixed_distinctions']: viol_fixed += 1
            if L['n_A']: flipped[(r['law'], r['round'], c['kind'], c['lift'])] += 1
            if L['n_A_moved']: flipped_m[(r['law'], r['round'], c['kind'], c['lift'])] += 1
            if L['n_A'] and r['law'] == 'parity': viol_parity.append((r['start'], r['round']))
    odd = 0
    F = S.forbid(); starts = S.census_starts()
    for i, rd in viol_parity:
        st, _ = S.grow_rounds(F.supports_of(starts[i]), 'parity', rd)
        if any(len(k) % 2 for k in st[rd]): odd += 1
    print(f'P2: flipped states under a swap keeping a distinction: {viol_fixed}; parity stages with flipped states: '
          f'{len(viol_parity)}, of which with a knot of odd places: {odd}')
    print('  swaps with flipped states, by (law, round, kind, lift):', dict(sorted(flipped.items())))
    print('  swaps with states flipped on the moved distinctions:', dict(sorted(flipped_m.items())), '\n')
    # gates and hits
    agg = collections.defaultdict(lambda: collections.Counter())
    best = collections.defaultdict(Fraction)
    hits = collections.defaultdict(list)
    w1c_same = collections.Counter()
    for r in rows:
        if isinstance(r['classes'], str): continue
        for c in r['classes']:
            if c.get('labels'): w1c_same[(r['law'], c['labels']['W1c is plus or minus W1'])] += 1
            for nm, wv in c['weightings'].items():
                for rd in ('R1', 'R2'):
                    g = wv[rd]; key = (r['law'], r['round'], nm, rd)
                    a = agg[key]
                    a['swap rows'] += 1; a['Z = 0'] += (wv['Z'] == 0)
                    for k in ('placements', 'G0', 'G1', 'G2', 'G3'): a[k] += g[k]
                    a['hits'] += len(g['hits'])
                    if g['best'] is not None: best[key] = max(best[key], Fraction(g['best']))
                    for h in g['hits']:
                        hits[key].append((r['start'], r['round'], c['kind'], c['lift'], c['sides'], h))
    print('| Law | Round | Weighting | Reading | Swap rows | Normalizer 0 | Placements | G0 | G1 | G2 | G3 | Largest CHSH past G0-G3 | Hits |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for key in sorted(agg):
        a = agg[key]
        print(f"| {key[0]} | {key[1]} | {key[2]} | {key[3]} | {a['swap rows']:,} | {a['Z = 0']:,} | {a['placements']:,} | "
              f"{a['G0']:,} | {a['G1']:,} | {a['G2']:,} | {a['G3']:,} | {best.get(key, '—')} | {a['hits']:,} |")
    print('\nW1c equal to plus or minus W1 on every state (the convention swap tests nothing there):', dict(w1c_same))
    print('\n## Hits\n')
    for key in sorted(hits):
        H = hits[key]
        starts_hit = sorted({h[0] for h in H})
        ann = collections.Counter()
        chs = collections.Counter()
        for h in H:
            info = h[5][3] if len(h[5]) > 3 else None
            if info: ann[(('on the reads only' if info['sign on the reads only'] else 'through the completions'),
                          ('holders meet' if info['holders meet'] else 'holders apart'))] += 1
            chs[h[5][2]] += 1
            kinds = (h[2], h[3])
        kinds = collections.Counter((h[2], h[3]) for h in H)
        print(f'- {key}: {len(H)} hits at {len(starts_hit)} starts (first {starts_hit[:8]}); CHSH values {dict(chs)}; '
              f'kinds {dict(kinds)}; annotated (first 20 per swap): {dict(ann)}')
    json.dump({str(k): v[:50] for k, v in hits.items()}, open(HERE / 'census_hits.json', 'w'), default=str, indent=0)


if __name__ == '__main__':
    main(sys.argv[1])
