# Thread's separate checks of study C (the census under rule R, and one added knot).
# Own enumeration of words (reach_enumeration), own census of added knots (added_knot_sample), own round 1 of rule R
# with groups from the RECORDED operator's group rule on an end built here from full holdings.
# Run from the repository root:
#   .venv/bin/python -B research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/reread_reach_check.py PART
import gzip, json, glob, collections, itertools, os, sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import reach_enumeration as v
import added_knot_sample as aks
sys.path.insert(0, 'experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test')
import lib
EO = lib.EO
C = 'artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/'
def lines(pat):
    for f in sorted(glob.glob(C + pat)):
        for l in gzip.open(f, 'rt'): yield json.loads(l)
def start_knots(tid, mask):
    tk = [v.parse(k) for k in v.targets[tid]['knots']]
    return [tk[i] for i in range(len(tk)) if mask >> i & 1]
def numbered(knots):
    names = {}
    return [tuple(names.setdefault(m, len(names)) for m in mem) for _, mem in knots], names
def round1(stars, conv):
    """Round 1 of rule R on full holdings: recorded group rule, own payments.  Returns births as (parents, inputs, paid)."""
    holders = collections.defaultdict(list)
    for k, s in enumerate(stars):
        for d in s: holders[d].append(k)
    loose = {k: [d for d in s if len(holders[d]) == 1] for k, s in enumerate(stars)}
    opens = {k: len(r) for k, r in loose.items() if r}
    if not opens: return dict(status='no live knot')
    wit = collections.defaultdict(set)
    for k in opens:
        for d in stars[k]:
            for j in holders[d]:
                if j != k: wit[j].add(k)
    end = EO.End(opens, tuple(tuple(sorted(b)) for b in wit.values()))
    groups = EO.proposals(end)
    used = collections.Counter(x for g in groups for x in g)
    short = {k: used[k] - n for k, n in opens.items() if used[k] > n}
    pool = {k: list(r) for k, r in loose.items()}
    paid_by = collections.defaultdict(set); births = []; unpaid = 0
    parents = list(groups) + [(k,) for k, n in opens.items() for _ in range(max(0, n - used[k]))]
    for g in parents:
        ins = []; pd = []
        for p in g:
            if pool[p]: ins.append(pool[p].pop()); pd.append(False); continue
            cands = sorted(d for d in stars[p] if len(holders[d]) >= 2 and d not in paid_by[p] and not any(q in g and q != p for q in holders[d]))
            if not cands: unpaid += 1; ins.append(None); pd.append(None); continue
            d = cands[0] if conv == 'O' else cands[-1]
            paid_by[p].add(d); ins.append(d); pd.append(True)
        births.append((tuple(g), tuple(ins), tuple(pd)))
    return dict(status='residual' if unpaid else 'round', short=len(short), births=births, unpaid=unpaid)
part = sys.argv[1]
if part == 'arm2':
    rows = {r['si']: r for r in lines('arm2_all_*.jsonl.gz')}
    tot = collections.Counter()
    for r in rows.values():
        tot['starts'] += 1; tot['sets'] += r['sets']; tot['gains'] += len(r['gains']); tot['starts with a gain'] += bool(r['gains'])
        for g in r['gains']:
            tot[('shared distinctions in T', g['shared'])] += 1; tot[('size of T', g['size'])] += 1
            tot[('observer class', g['obs_class'])] += 1; tot[('known shape', g['known_shape'])] += 1
            tot[('rule R makes T', g['origin_R'])] += 1; tot[('ordinary growth makes T', g['origin_ordinary'])] += 1
            tot[('score', g['score'])] += 1
            lo = [x for x in g['T'] if x in r['loose']]
            tot[('loose distinctions in T', len(lo), tuple(sorted(lo)) if len(lo) == 1 else '')] += 1
    for k, n in sorted(tot.items(), key=str): print(k, n)
    # the thread's own census on every start with a gain, and on the sampled starts
    sample = json.load(open(sys.argv[2]))['rows'] if len(sys.argv) > 2 else []
    todo = {r['si']: (r['tid'], r['mask']) for r in rows.values() if r['gains']}
    mine = {r['si']: {(tuple(T), s) for T, s, _, _ in r['gains']} for r in sample}
    for si, (tid, mask) in todo.items():
        if si not in mine:
            mine[si] = {(tuple(T), s) for T, s, _, _ in aks.census(start_knots(tid, mask))[3]}
    same = sum(1 for si in mine if mine[si] == {(tuple(sorted(g['T'])), g['score']) for g in rows[si]['gains']})
    print('starts censused separately:', len(mine), '(sampled', len(sample), '); same set of gains and scores as the study:', same,
          '; of them with a gain:', sum(1 for si in mine if mine[si]))
if part == 'arm1two':
    tot = collections.Counter()
    seen = set()
    for r in lines('arm1_two_*.jsonl.gz'):
        tot[('histories', r['kind'])] += 1
        tot['gains'] += sum(s['gains'] for s in r['stages']); tot['tables'] += sum(s['tables'] for s in r['stages'][1:])
        tot['support changes'] += sum(s['support_changes'] for s in r['stages'])
        b = max((s['best_hidden_float'] for s in r['stages'][1:] if s['best_hidden_float'] is not None), default=0)
        tot['best'] = max(tot['best'], b)
        tot[('law mode', r['law_mode'])] += 1
        if r['kind'] in 'ON':
            stars, _ = numbered(start_knots(r['tid'], r['mask']))
            m = round1(stars, r['kind'])
            if m['status'] == 'residual': ok = r['residual'] is not None and len(r['n_at']) == 1
            else: ok = r['residual'] is None and len(r['n_at']) > 1 and r['n_at'][1] - r['n_at'][0] == len(m['births']) and r['short'][0] == m['short']
            tot[('round 1 agrees with the thread', r['kind'])] += bool(ok); tot[('round 1 compared', r['kind'])] += 1
            tot[('residual stall at round 1', r['kind'])] += m['status'] == 'residual'
        seen.add(r['si'])
    tot['starts'] = len(seen)
    for k, n in sorted(tot.items(), key=str): print(k, n)
if part == 'arm1three':
    tot = collections.Counter(); starts = collections.defaultdict(set); done = 0
    hist = collections.Counter()
    for r in lines('arm1_three_*.jsonl.gz'):
        hist[('histories', r['kind'])] += 1; hist['grow'] += len(r['n_at']) > 1
        hist['gain histories'] += sum(s['gains'] for s in r['stages']) > 0; hist['gain tables'] += sum(s['gains'] for s in r['stages']); hist['gain tables through a payment'] += sum(s['gains_pay'] for s in r['stages'])
        if len(r['n_at']) > 1: starts['grow'].add(r['si'])
        if sum(s['gains'] for s in r['stages']) > 0: starts['gain'].add(r['si'])
        starts['all'].add(r['si'])
    print(sorted(hist.items(), key=str), {k: len(s) for k, s in starts.items()})
    for r in lines('arm1_gains_three_*.jsonl.gz'):
        tot['written gain tables'] += 1; tot[('through a payment', r['through_payment'])] += 1
        ks = [v.parse(k) for k in r['knots']]
        nd = len({m for _, mem in ks for m in mem})
        # round 1 replayed by the thread
        stars, names = numbered(start_knots(r['tid'], r['mask']))
        if r['kind'] in 'ON' and r['t'] == 1:
            m = round1(stars, r['kind'])
            rec = [(tuple(b['parents']), tuple(b['inputs']), tuple(b['paid'])) for b in r['births'][0]]
            tot['round 1 births equal to the thread\'s'] += m.get('births') == rec; tot['round 1 compared'] += 1
        if nd <= 24:
            s = v.score(ks); done += 1
            ok = s[1] and s[0] == Fraction(r['eval'][3]) and s[0] > 2 and s[3].reshape(-1).tolist() == list(r['table'])
            tot['enumerated by the thread'] += 1; tot['enumeration agrees'] += bool(ok)
            pay = set(r['paying_cols']); n0 = len(ks) - len(r['newborn_laws'])
            ks2 = [(('even' if (i - n0) in pay else law), mem) for i, (law, mem) in enumerate(ks)]
            s2 = v.score(ks2)
            tot['with paying births even: no hidden excess'] += not (s2[1] and s2[0] > 2)
            tot['through-payment flag agrees'] += (not (s2[1] and s2[0] > 2)) == bool(r['through_payment'])
    for k, n in sorted(tot.items(), key=str): print(k, n)
