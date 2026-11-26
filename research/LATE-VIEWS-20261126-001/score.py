"""score.py OUT.json: the frozen predictions (predictions.jsonl.gz, committed before any grown file was opened) against
the grown held-out sets.  README.md, "Frozen".  The comparison is late.py's: each round's multiset of births in sig0
and in sig1; a growth that closes must have no predicted births from its closing round on, and an accepted start must
not stall."""
import sys, os, json, gzip, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import late
phase2 = late.phase2

GROWN = {('uniform', 'nae'): 'held_out_nae.jsonl.gz', ('uniform', 'parity'): 'held_out_parity.jsonl.gz',
         ('stratified', 'nae'): 'grown_stratified_nae.jsonl.gz', ('stratified', 'parity'): 'grown_stratified_parity.jsonl.gz',
         ('handbuilt', 'nae'): 'grown_handbuilt_nae.jsonl.gz', ('handbuilt', 'parity'): 'grown_handbuilt_parity.jsonl.gz',
         ('grow7', 'nae'): 'grown_grow7_nae.jsonl.gz', ('grow7', 'parity'): 'grown_grow7_parity.jsonl.gz',
         ('horizon', 'nae'): 'grown_horizon_nae.jsonl.gz'}


def compare(P, x):
    """the first round where the predicted rows P and the grown record x differ, in either reading; None if none"""
    g = x['rows']
    if x['end'].startswith('stalls'): return 'stalls at round %d' % (len(g) + 1)
    for t in range(len(g)):
        for R in ('sig0', 'sig1'):
            if late.cnt(g[t], R) != late.cnt(P[t], R): return t + 1
    if x['end'].startswith('closes'):
        for t in range(len(g), len(P)):
            if P[t]['n']: return t + 1
    return None


def main(out):
    pred = {}
    for l in gzip.open(os.path.join(HERE, 'predictions.jsonl.gz'), 'rt'):
        p = json.loads(l); pred[(p['set'], p['knot law'], p['index'])] = p
    res = collections.Counter(); misses = []; stalls = collections.Counter(); settle = collections.Counter()
    grown = {}
    for (S, law), fn in GROWN.items():
        for l in late.opener(os.path.join(HERE, fn)):
            x = json.loads(l); p = pred[(S, law, x['index'])]; grown[(S, law, x['index'])] = x
            part = 'proved class' if p['stratum'] == 'proved class' else 'a new reading'
            if p['read'] == 'stall':
                stalls[(S, law, 'read as stalling: grown ' + ('stalls at round 1' if x['end'] == 'stalls at round 1' else x['end']))] += 1
                continue
            if p['read'] != 'predicted':
                res[(S, law, 'not predicted: ' + p['read'])] += 1; continue
            first = compare(p['rows'], x)
            ok = first is None
            res[(S, law, part, 'agree in every round read' if ok else 'differ')] += 1
            if not ok:
                misses.append({'set': S, 'knot law': law, 'index': x['index'], 'stratum': p['stratum'],
                               'rare strata': p['rare strata'], 'first differing round': first, 'stars': x['stars']})
            k = x['kind']
            if k.startswith('dim'):
                D = int(k.split()[1]); V = phase2.views(x)
                settle[(S, law, 'grown D equals the predicted' if D == p['D'] else 'grown D differs')] += 1
                for R, Kp in (('sig0', p['K0']), ('sig1', p['K1'])):
                    if Kp > len(x['rows']) - 2: settle[(S, law, R, 'predicted K past the rounds read')] += 1; continue
                    settle[(S, law, R, 'K as predicted' if phase2.settles(V[R], D) == Kp else 'K differs')] += 1
            else:
                settle[(S, law, 'kind ' + k.split()[0])] += 1
    ctl = collections.Counter()                  # P4: the negative controls on the uniform set
    for (S, law, i), x in grown.items():
        if S != 'uniform' or pred[(S, law, i)]['read'] != 'predicted': continue
        n = len(x['rows'])
        if law == 'nae':
            for a in ('relay', 'cells'):
                P, why = late.predict(x['stars'], len(pred[(S, law, i)]['rows']), 'nae', (a,))
                ctl[('without the ' + ('relay' if a == 'relay' else 'group cells'), 'differ' if P is None or compare(P, x) else 'agree')] += 1
        else:
            P, why = late.predict(x['stars'], len(pred[(S, law, i)]['rows']), 'nae')
            ctl[('the not-all-equal predictor on parity growth', 'differ' if P is None or compare(P, x) else 'agree')] += 1
    r = {'P1 and P3': {' / '.join(k): v for k, v in sorted(res.items())},
         'P2': {' / '.join(k): v for k, v in sorted(settle.items())},
         'P4': {' / '.join(k): v for k, v in sorted(ctl.items())},
         'read as stalling': {' / '.join(k): v for k, v in sorted(stalls.items())},
         'misses': misses}
    json.dump(r, open(out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in r.items() if k != 'misses'}, indent=1)); print('misses:', len(misses))
    for m in misses[:10]: print(m)


if __name__ == '__main__':
    main(sys.argv[1])
