"""Score FIRST-KNOT-20261118-001B-E001's frozen predictions.  python3 -B merge.py <run dir> [<out json>]"""
import json
import sys
from collections import Counter
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from longrun import load_results  # noqa: E402

recs = load_results(sys.argv[1])
res = {c: r['result'] for c, r in recs.items() if r.get('status') == 'ok'}
bad = [c for c, r in recs.items() if r.get('status') != 'ok']
score, notes = {}, {}

# Q1: one count, every start: survival, stall round and junctions per round as predicted from the open counts alone
ok, fails, grid = True, [], {}
out_of_scope = []
for cid, r in res.items():
    if 'predicted' not in r:
        continue
    pr = r['predicted']
    surv = r['outcome'] in ('alive', 'big')
    good = surv == pr['survives']
    if good and not surv:
        good = r['stall_round'] == pr['stall_round']
    if good and surv:
        good = r['counts'] == pr['counts'][:len(r['counts'])]
    if not good and r['in_scope']:
        ok = False
        fails.append((cid, r['outcome'], r['stall_round'], r['open'], pr))
    if not good and not r['in_scope']:
        out_of_scope.append((cid, r['outcome'], r['stall_round']))
    if cid.startswith('uniform-'):
        key = cid.rsplit('-c', 1)[0][8:]
        grid.setdefault(key, {})[int(cid.rsplit('-c', 1)[1])] = 'run' if surv else f"x{r['stall_round']}"
score['Q1'] = ok
notes['Q1'] = {'fails': fails[:10], 'outside Lemma 1, prediction missed (reported)': out_of_scope, 'runs': sum(1 for r in res.values() if 'predicted' in r), 'grid (start: count -> outcome)': grid}

# Q2: fewest counts on two first knots: apart closes as two Boolean patterns; sharing one, the exact per-round counts; relays
ok, fails, table = True, [], {}
for a in range(3, 7):
    for b in range(a, 7):
        r0 = res[f'fewest-{a}-{b}-s0']
        want0 = [2] + [comb(a, j) + comb(b, j) for j in range(1, b + 1)]
        g0 = r0['outcome'] == 'closed' and r0['counts'] == want0 and r0['forced_bits'] == 0
        r1 = res[f'fewest-{a}-{b}-s1']
        g1 = (r1['outcome'] in ('alive', 'big') and r1['counts'] == r1['predicted_counts'] and r1['forced_bits'] == 0
              and all(r1['relay']) and len(r1['relay']) == (a > 3) + (b > 3))
        r2 = res[f'fewest-{a}-{b}-s2']
        table[f'{a}+{b}'] = {'apart': r0['outcome'], 'sharing one': r1['outcome'], 'relays': len(r1['relay']),
                             'sharing two': (r2['outcome'], r2['offshoots'][-1], r2['counts'][-3:])}
        if not (g0 and g1):
            ok = False
            fails.append((a, b, r0['outcome'], r0['counts'][:8], r1['outcome'], r1['counts'][:10], r1['predicted_counts'][:10],
                          r1['relay']))
score['Q2'] = ok
notes['Q2'] = {'fails': fails, 'table': table}

# Q4: small starts and two-distinction touches under fewest: closed exactly when every demand-0 junction was implied; otherwise
# junctions per round with constant differences over the last ten rounds (at most quadratic in all); no forced distinction
ok, table = True, {}
for cid, r in res.items():
    if not (cid.startswith('small-') and not cid.startswith('small-uniform')) and not (cid.startswith('fewest-') and cid.endswith('s2')):
        continue
    closed = r['outcome'] == 'closed'
    all_implied = r['demand0'] == r['demand0_implied']
    c = r['counts'][-11:]
    diffs = [c[i + 1] - c[i] for i in range(len(c) - 1)]
    good = (closed == all_implied) and r['forced_bits'] == 0 and (closed or len(set(diffs)) == 1)
    table[cid] = {'outcome': r['outcome'], 'demand0': r['demand0'], 'implied': r['demand0_implied'], 'last diffs': sorted(set(diffs)),
                  'offshoots last': r['offshoots'][-1], 'last counts': r['counts'][-3:]}
    if not good:
        ok = False
score['Q4'] = ok
notes['Q4'] = table

# Q5: the floor control: floor 2 gives eventually constant junctions per round; floor 4 gives junctions per round with growing
# differences (more than two-dimensional)
ok, table = True, {}
for cid, r in res.items():
    if not cid.startswith('floor'):
        continue
    c = r['counts'][-6:]
    d = [c[i + 1] - c[i] for i in range(len(c) - 1)]
    m = int(cid[5])
    good = (len(set(c)) == 1) if m == 2 else (r['outcome'] in ('alive', 'big') and all(d[i + 1] > d[i] for i in range(len(d) - 1)))
    table[cid] = {'outcome': r['outcome'], 'last counts': c, 'offshoots last': r['offshoots'][-1]}
    if not good:
        ok = False
score['Q5'] = ok
notes['Q5'] = table

out = {'cases': len(recs), 'not_ok': bad, 'score': score, 'notes': notes}
txt = json.dumps(out, indent=1, default=str)
print(txt)
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(txt)
