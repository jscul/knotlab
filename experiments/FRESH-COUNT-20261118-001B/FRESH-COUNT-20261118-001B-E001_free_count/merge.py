"""Score FRESH-COUNT-20261118-001B-E001's frozen predictions from the shared runner's results.

python3 -B merge.py <run dir> [<out json>]"""
import json
import statistics
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from longrun import load_results  # noqa: E402

run_dir = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) > 2 else None
recs = load_results(run_dir)
R = {cid: r for cid, r in recs.items()}
bad = [cid for cid, r in R.items() if r.get('status') != 'ok']
res = {cid: r['result'] for cid, r in R.items() if r.get('status') == 'ok'}
score, notes = {}, {}


def stall_round_expected(a, c):
    if c <= a - 2:
        return 2
    if c == a - 1:
        return 4
    if c >= a + 1:
        return 3
    return None


# P1, P2
for cap, key in ((None, 'P1'), (3, 'P2')):
    ok, fails = True, []
    for a in range(3, 8):
        for c in range(1, a + 4):
            r = res[f'uniform-cap{cap}-a{a}-c{c}']
            if cap is None or a == 3:
                exp_survive = (c == a)
                exp_round = stall_round_expected(a, c)
            else:
                exp_survive = False
                exp_round = 4 if c == a else stall_round_expected(a, c)
            survived = r['outcome'] in ('alive', 'big')
            good = survived == exp_survive and (survived or r['stall_round'] == exp_round)
            if survived:
                good &= r['matches_Na']
            if not good:
                ok = False
                fails.append((a, c, r['outcome'], r['stall_round']))
    score[key] = ok
    notes[key] = fails[:10]

# P3
ok, fails = True, []
for a in range(3, 7):
    f = res[f'menu-fewest-a{a}']
    good = f['outcome'] == 'closed' and f['matches_boolean'] and f['arities'] == [a] and f['forced_bits'] == 0
    for name in ('axis', 'inherit_max', 'inherit_min'):
        r = res[f'menu-{name}-a{a}']
        good &= r['outcome'] in ('alive', 'big') and r['matches_Na']
    b = res[f'menu-balance-a{a}']
    good &= b['outcome'] == 'stall' and (b['stall_round'] == 2 if a >= 4 else b['stall_round'] <= 6)
    if not good:
        ok = False
        fails.append(a)
score['P3'] = ok
notes['P3'] = {'fails': fails, 'balance_stall_rounds': {a: res[f'menu-balance-a{a}']['stall_round'] for a in range(3, 7)}}

# P4
checked, errs = 0, []
for cid, r in res.items():
    if 'ideals' in r:
        checked += 1
        if r['ideals']['errors'] or r['ideals']['missing']:
            errs.append(cid)
score['P4'] = not errs
notes['P4'] = {'runs_checked': checked, 'failing': errs[:10]}

# P5
ok, table = True, {}
for a in (3, 4):
    for K in range(2, 7):
        rs = [res[f'blind-a{a}-K{K}-s{s}'] for s in range(200)]
        alive = sum(1 for r in rs if r['outcome'] in ('alive', 'big'))
        table[f'a{a}K{K}'] = {'not_stalled': alive, 'stall_rounds': dict(Counter(r['stall_round'] for r in rs if r['stall_round'])),
                              'runs_with_forced_bits': sum(1 for r in rs if r['forced_bits'])}
        ok &= alive <= 20
score['P5'] = ok
notes['P5'] = table

# P6
ok, table = True, {}
for a in (3, 4):
    prev = -1
    for q in (0.05, 0.1, 0.2, 0.4):
        rs = [res[f'surplus-a{a}-q{q}-s{s}'] for s in range(200)]
        stalls = sum(1 for r in rs if r['outcome'] == 'stall')
        unclosed = [r for r in rs if r['outcome'] in ('alive', 'big')]
        last = [r['offshoots'][r['rounds']] for r in unclosed]
        med = statistics.median(last) if last else None
        table[f'a{a}q{q}'] = {'outcomes': dict(Counter(r['outcome'] for r in rs)), 'median_offshoots_last_round': med,
                              'forced_bit_runs': sum(1 for r in rs if r['forced_bits']),
                              'closed_at_round': dict(Counter(r['rounds'] for r in rs if r['outcome'] == 'closed'))}
        ok &= stalls == 0 and len(unclosed) > prev and all(r['forced_bits'] == 0 for r in rs)
        if q >= 0.2:
            ok &= med is not None and med >= 3
        prev = len(unclosed)
score['P6'] = ok
notes['P6'] = table

# P7
ok, fails, table = True, [], Counter()
for s in range(200):
    r = res[f'handover-s{s}']
    if 'handover_offshoots_demand1' not in r:
        table['ended before hand-over'] += 1
        continue
    h = r['h']
    seq = r['offshoots'][h + 2: r['rounds'] + 1]
    good = all(x == r['handover_offshoots_demand1'] for x in seq)
    table[(r['outcome'], r['handover_offshoots_demand1'])] += 1
    if not good:
        ok = False
        fails.append((s, h, r['handover_offshoots_demand1'], seq[:8]))
for a in range(3, 7):
    r = res[f'crossed-a{a}']
    seq = r['offshoots'][a + 1: r['rounds'] + 1]
    good = r['outcome'] in ('alive', 'big') and seq and all(x == a for x in seq)
    if not good:
        ok = False
        fails.append(('crossed', a, r['outcome'], seq[:8]))
score['P7'] = ok
notes['P7'] = {'fails': fails[:10], 'outcome_by_chains': {str(k): v for k, v in table.items()},
               'crossed_counts': {a: res[f'crossed-a{a}']['counts'] for a in range(3, 7)}}

# P8
uni = {cid: r for cid, r in res.items() if cid.startswith('reader-uniform')}
few = {cid: r for cid, r in res.items() if cid.startswith('reader-fewest')}
okA = all(r.get('verdict') == 'exact' for r in uni.values() if 'skipped' not in r)
okB = True
for cid, r in few.items():
    a = int(cid.split('-a')[1].split('-')[0])
    T = int(cid.split('-r')[1])
    if 'skipped' in r:
        continue
    want = 'exact_plus_all_loose' if T == a - 1 else 'exact'
    okB &= r['verdict'] == want
mixed = [st for cid, r in res.items() if cid.startswith('reader-mixed') for st in r['stages'] if 'verdict' in st]
mixed_counts = Counter(st['verdict'] for st in mixed)
okC = mixed_counts.get('misread', 0) >= 1
score['P8'] = okA and okB and okC
notes['P8'] = {'uniform': {k: v.get('verdict', v.get('skipped')) for k, v in uni.items()},
               'fewest': {k: v.get('verdict', v.get('skipped')) for k, v in few.items()},
               'mixed': dict(mixed_counts), 'mixed_uniform_size_stages': sum(1 for st in mixed if st['verdict'] != 'misread'),
               'all_loose_small_bond_when_plus': sum(1 for st in mixed if st['verdict'] == 'exact_plus_all_loose' and st['all_loose_small_bond'])}

# P9
ok, rounds, disagree = True, 0, 0
for cid, r in res.items():
    if cid.startswith('surplus-') and 'cap_rounds' in r:
        for agrees, mg in r['cap_rounds']:
            rounds += 1
            disagree += (not agrees)
            if agrees != (mg <= 3):
                ok = False
score['P9'] = ok
notes['P9'] = {'rounds': rounds, 'rounds_where_cap_differs': disagree}

summary = {'cases': len(R), 'not_ok': bad[:20], 'n_not_ok': len(bad), 'score': score, 'notes': notes}
txt = json.dumps(summary, indent=1, default=str)
print(txt)
if out_path:
    Path(out_path).write_text(txt)
