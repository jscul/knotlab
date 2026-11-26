"""score.py OUT.json: the frozen predictions (README, "Frozen") over recur_*.jsonl and tower_*.jsonl."""
import sys, json, collections, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))


def main(out):
    T = collections.Counter(); breaks = []; orbits = collections.Counter(); returners = []
    for p in sorted(glob.glob(os.path.join(HERE, 'recur_*.jsonl'))):
        S = os.path.basename(p)[6:-6]
        for l in open(p):
            x = json.loads(l)
            if 'error' in x: T[(S, 'error')] += 1; continue
            pe = x.get('pinned exchange', ''); T[(S, 'pinned', pe)] += 1
            if pe == 'lawful':
                orbits[(S, ' -> '.join(x['orbit']))] += 1
                if x['returns']:
                    returners.append([S, x['start'], x['knots'], x['loose']])
                    ok = x['one ring'] and x['knots'] >= 5 and x['knots'] != 6 and all(v == 2 for v in x['loose'])
                    T[(S, 'R1 returns', 'a ring as predicted' if ok else 'BREAK')] += 1
                    if not ok: breaks.append(['R1', S, x['start']])
                ok3 = x['most shared distinctions at a knot'] <= 2
                T[(S, 'R3 lawful pinned', 'at most two shared at every knot' if ok3 else 'BREAK')] += 1
                if not ok3: breaks.append(['R3', S, x['start']])
            fe = x.get('free exchange', '')
            T[(S, 'R2 free', fe)] += 1
            if fe == 'lawful': breaks.append(['R2', S, x['start']])
    W = collections.Counter(); towers = []
    for p in sorted(glob.glob(os.path.join(HERE, 'tower_*.jsonl'))):
        S = os.path.basename(p)[6:-6]
        for l in open(p):
            x = json.loads(l)
            if 'error' in x: W[(S, 'error')] += 1; continue
            for r in x['rounds']:
                if 'end' in r: W[(S, 'round %d' % r['round'], r['end'].split(':')[0])] += 1; continue
                for reading in ('SHORT', 'UPTO5'):
                    w = r[reading]['whole-held']
                    W[(S, 'round %d' % r['round'], reading, 'whole-held %d' % w)] += 1
                    if w >= 2: towers.append([S, x['start'], r['round'], reading, w]); breaks.append(['T1', S, x['start'], r['round'], reading])
    res = {'recursion': {' / '.join(k): v for k, v in sorted(T.items())},
           'orbits of lawful pinned exchanges': {' / '.join(k): v for k, v in sorted(orbits.items())},
           'returners': returners,
           'tower': {' / '.join(k): v for k, v in sorted(W.items())}, 'tower steps': towers, 'breaks': breaks}
    json.dump(res, open(out, 'w'), indent=1); print(json.dumps({k: v for k, v in res.items() if k != 'returners'}, indent=1)[:6000])


if __name__ == '__main__':
    main(sys.argv[1])
