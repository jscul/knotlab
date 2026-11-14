"""Frozen read-out of LEVEL-REACH-20261114-001A (pre-registration Q0-Q5) from the registered run. Writes summary.json and prints."""
import sys, json, collections, random, math
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from longrun import load_results
import input_addr as addr
RUN = 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex/registered'
R = load_results(RUN)
res = {v['result']['case']: v['result'] for v in R.values() if v.get('status') == 'ok'}
out = dict(cases=dict(collections.Counter(v.get('status') for v in R.values())), descriptions=len(res))

def outcome(a):
    fl = a['flags']; un = a['union']['verdict']; Ls = [l['L_N'] for l in a['levels']]
    if fl['no_join']: return 'no join'
    if un == 'dead': return 'dead'
    if un != 'alive': return 'undecided'
    if any(x == 'none' for x in Ls): return 'no bond'
    if any(x == 'undecided' for x in Ls): return 'undecided'
    if all(isinstance(x, int) for x in Ls) and len(set(Ls)) == 1: return 'direct'
    if all(isinstance(x, int) for x in Ls) and all(Ls[i] == i + 3 for i in range(len(Ls))): return 'chained'
    return 'other'

W = collections.Counter(); E = set()
for a in res.values():
    for m in a['memberships']:
        if m['family'] == 'W_R' and m['index'] < 2000: W[a['case']] += 1
        if m['family'] == 'E_R': E.add(a['case'])
cls = {c: a['classes']['relative']['class'] for c, a in res.items()}
oc = {c: outcome(a) for c, a in res.items()}
def aclass(a):
    try: return str(addr.automaton_class(a['key']))
    except Exception: return str(a['key'][:4])
ac = {c: aclass(a) for c, a in res.items()}
out['outcomes_by_description'] = dict(collections.Counter(oc.values()))
out['outcomes_by_weight_W'] = dict(collections.Counter({o: 0 for o in set(oc.values())}) + collections.Counter({oc[c]: 0 for c in W}))
wt = collections.Counter()
for c, w in W.items(): wt[oc[c]] += w
out['outcomes_by_weight_W'] = dict(wt); totW = sum(wt.values())
alive = totW - wt['dead']
none = wt['no join'] + wt['no bond']; direct = wt['direct']; und = wt['undecided']; chained = wt['chained']; other = wt['other']
out['Q0'] = dict(alive_draws=alive, none_lo=none / alive, none_hi=(none + und) / alive, chained_lo=chained / alive, chained_hi=(chained + und) / alive,
                 direct_lo=direct / alive, direct_hi=(direct + und) / alive, other=other / alive, undecided=und / alive)
q0fail_both = (out['Q0']['none_hi'] < 0.25) or (out['Q0']['direct_lo'] > 0.15)
q0fail_any = (out['Q0']['none_lo'] < 0.25) or (out['Q0']['direct_hi'] > 0.15)
out['Q0']['verdict'] = 'fails' if q0fail_both else ('holds' if not q0fail_any else 'holds on the point reading; open with undecided read against it')
S = wt['chained'] + wt['direct'] + wt['other'] + wt['undecided']
out['Q1'] = dict(set_weight=S, ruler_lo=chained / S, ruler_hi=(chained + und) / S)
out['Q1']['verdict'] = 'fails' if out['Q1']['ruler_hi'] < 0.70 else ('holds' if out['Q1']['ruler_lo'] >= 0.70 else 'holds on the upper bound only')
out['Q2'] = dict(direct_lo=direct / S, direct_hi=(direct + und) / S)
out['Q2']['verdict'] = 'fails' if out['Q2']['direct_lo'] > 0.10 else ('holds' if out['Q2']['direct_hi'] <= 0.10 else 'holds on the lower bound only')
below = []
for c, a in res.items():
    for l in a['levels']:
        x, y = l['L_N'], l.get('L_target')
        if isinstance(x, int) and (not isinstance(y, int) or y > x) and y != 'undecided': below.append((c[:12], l['s'], x, y))
out['Q3'] = dict(found_bonds=sum(1 for a in res.values() for l in a['levels'] if isinstance(l['L_N'], int)), needing_member_below=below[:20],
                 count_below=len(below), verdict='holds' if not below else 'fails')
# Q4: W_R draws, decided members of the Q1 set, non-ruler share exponential vs finitary, cluster bootstrap by automaton class
def units(klass):
    u = collections.defaultdict(lambda: [0, 0])
    for c, w in W.items():
        if cls[c] != klass or oc[c] not in ('chained', 'direct', 'other'): continue
        u[ac[c]][0] += w * (oc[c] != 'chained'); u[ac[c]][1] += w
    return list(u.values())
ex, fi = units('exponential'), units('finitary')
def share(us): n = sum(t for _, t in us); return (sum(x for x, _ in us) / n) if n else None
rng = random.Random(20261124); boots = []
for _ in range(2000):
    be = [ex[rng.randrange(len(ex))] for _ in ex] if ex else []; bf = [fi[rng.randrange(len(fi))] for _ in fi] if fi else []
    if be and bf and share(be) is not None and share(bf) is not None: boots.append(share(be) - share(bf))
boots.sort()
d = (share(ex) - share(fi)) if ex and fi else None
ci = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]) if boots else (None, None)
out['Q4'] = dict(exponential_nonruler=share(ex), finitary_nonruler=share(fi), delta=d, ci95=ci, clusters=(len(ex), len(fi)),
                 verdict='holds' if ci[0] is not None and ci[0] > 0 else 'fails')
# Q5: E_R descriptions (unweighted), bounded and polynomial: ruler and direct shares among decided Q1-type outcomes, Wilson intervals
def wilson(k, n):
    if n == 0: return (None, None)
    z = 1.96; p = k / n; den = 1 + z * z / n; cen = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (cen - h, cen + h)
q5 = {}
for k in ('bounded', 'polynomial'):
    cs = [c for c in E if cls[c] == k]
    o = collections.Counter(oc[c] for c in cs); dec = o['chained'] + o['direct'] + o['other']
    q5[k] = dict(descriptions=len(cs), outcomes=dict(o), ruler=(o['chained'] / dec if dec else None), ruler_ci=wilson(o['chained'], dec),
                 direct=(o['direct'] / dec if dec else None), direct_ci=wilson(o['direct'], dec))
exw = [c for c in W if cls[c] == 'exponential']; o = collections.Counter()
for c in exw: o[oc[c]] += W[c]
dec = o['chained'] + o['direct'] + o['other']
q5['exponential_W'] = dict(weight=sum(W[c] for c in exw), outcomes=dict(o), ruler=(o['chained'] / dec if dec else None), direct=(o['direct'] / dec if dec else None))
out['Q5'] = q5
# by class (W, weight) and per-s L distributions
byc = collections.defaultdict(collections.Counter)
for c, w in W.items(): byc[cls[c]][oc[c]] += w
out['outcomes_by_class_W'] = {k: dict(v) for k, v in byc.items()}
pers = collections.defaultdict(collections.Counter)
for c, w in W.items():
    for l in res[c]['levels']: pers[l['s']][str(l['L_N'])] += w
out['L_by_s_W'] = {s: dict(v) for s, v in sorted(pers.items())}
json.dump(out, open('research/LEVEL-REACH-20261114-001/summary.json', 'w'), indent=1, default=str)
for k in ('cases', 'descriptions', 'outcomes_by_description', 'outcomes_by_weight_W', 'Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'outcomes_by_class_W', 'L_by_s_W'):
    print(k, json.dumps(out[k], default=str)[:900])
