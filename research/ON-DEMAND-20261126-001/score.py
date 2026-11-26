"""score.py OUT.json RESULTS.jsonl...: the frozen predictions (README, "Frozen") tallied over run.py's records."""
import sys, json, collections


def main(out, paths):
    T = collections.Counter(); miss = []; prov = collections.Counter(); need = collections.defaultdict(list)
    for p in paths:
        for l in open(p):
            x = json.loads(l); P = x['population']
            if 'not read' in x:
                T[(P, 'start not read', x['not read'])] += 1; continue
            for law, r in x['laws'].items():
                if r['end'] == 'stall':
                    q = r['least steps whose knots stall']
                    T[(P, law, 'stalls in round 1', 'seen within %s steps' % q if q is not None else 'beyond the reader piece')] += 1
                    continue
                T[(P, law, 'starts read')] += 1
                for t, ok in r['H1 within t + 1 steps agrees'].items():
                    T[(P, law, 'H1 (reader, round)', 'agree' if ok else 'differ')] += 1
                    if not ok:
                        T[(P, law, 'H1 differs, region growth ends', r['region ends where H1 differs'][t])] += 1
                        miss.append([P, x['index'], law, x['reader'], int(t), r['region ends where H1 differs'][t]])
                for t, ok in r['within t steps agrees'].items():
                    T[(P, law, 'within t steps', 'agree' if ok else 'differ')] += 1
                for h in r['H2']:
                    oks = h[2] if isinstance(h[2], list) else [h[2]]
                    for ok in oks: T[(P, law, 'H2 regions and admission steps', 'agree' if ok else 'differ')] += 1
                for c in r.get('region growths stopped at the cap, not read', []): T[(P, law, 'region growth stopped at the cap, not read', c[0])] += 1
                for t, (a, b) in r["births of the region not in the full growth, of all the region's births, at round t"].items():
                    prov[(P, law, 'provisional')] += a; prov[(P, law, 'all')] += b
                last = max(r['births needed, of all births, through round t'], key=int, default=None)
                if last is not None:
                    a, b = r['births needed, of all births, through round t'][last]
                    if b: need[(P, law)].append(a / b)
    shares = {' / '.join(k): {'median': sorted(v)[len(v) // 2], 'least': min(v), 'starts': len(v)} for k, v in need.items() if v}
    res = {'tally': {' / '.join(k): v for k, v in sorted(T.items())},
           'provisional births': {' / '.join(k): v for k, v in sorted(prov.items())},
           'share of births the view rests on, at the last round read': shares, 'H1 differs': miss}
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'H1 differs'}, indent=1)); print('H1 differs:', len(miss))
    for m in miss[:12]: print(m)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
