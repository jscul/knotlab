"""Referee LEVEL-REACH-R1: from the full records (not the study's summarizer), the outcome rule as frozen, the union-undecided and
per-s undecided structure, and tightened bounds for Q0-Q2: an undecided profile counts toward the ruler's (direct's) upper bound only
if its decided levels are compatible with the ruler (a constant). Writes referee_bounds.json."""
import gzip, json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/results.jsonl.gz'
res = {}
for l in gzip.open(P, 'rt'):
    r = json.loads(l)
    if r['status'] == 'ok': res[r['result']['case']] = r['result']
W = collections.Counter()
for c, a in res.items():
    for m in a['memberships']:
        if m['family'] == 'W_R' and m['index'] < 2000: W[c] += 1
def outcome(a):
    fl = a['flags']; un = a['union']['verdict']; Ls = [l['L_N'] for l in a['levels']]
    if fl['no_join']: return 'no join'
    if un == 'dead': return 'dead'
    if un != 'alive': return 'undecided (union)'
    if any(x == 'none' for x in Ls): return 'no bond'
    if any(x == 'undecided' for x in Ls): return 'undecided (levels)'
    if all(isinstance(x, int) for x in Ls) and len(set(Ls)) == 1: return 'direct'
    if all(isinstance(x, int) for x in Ls) and all(Ls[i] == i + 3 for i in range(len(Ls))): return 'chained'
    return 'other'
def compat(a):
    Ls = [l['L_N'] for l in a['levels']]
    dec = [(i, x) for i, x in enumerate(Ls) if x != 'undecided']
    ruler = all(x == i + 3 for i, x in dec)
    ints = [x for _, x in dec if isinstance(x, int)]
    direct = all(isinstance(x, int) for _, x in dec) and len(set(ints)) <= 1
    return ruler, direct, Ls
wt = collections.Counter(); und = collections.Counter(); pats = collections.Counter()
for c, w in W.items():
    o = outcome(res[c]); wt[o] += w
    if o.startswith('undecided'):
        if o == 'undecided (union)':
            und['union undecided'] += w
        else:
            ru, di, Ls = compat(res[c]); und[('ruler-compatible' if ru else 'not ruler') + ' / ' + ('direct-compatible' if di else 'not direct')] += w
            pats[str(Ls)] += w
alive = sum(wt.values()) - wt['dead']
U = wt['undecided (union)'] + wt['undecided (levels)']
none = wt['no join'] + wt['no bond']
ruc = sum(v for k, v in und.items() if k.startswith('ruler-compatible')) + und['union undecided']
dic = sum(v for k, v in und.items() if 'direct-compatible' in k and not k.startswith('union')) + und['union undecided']
S = wt['chained'] + wt['direct'] + wt['other'] + U
out = {"weights": dict(wt), "alive": alive, "undecided split": dict(und), "undecided level patterns (top 15)": pats.most_common(15),
       "Q0": {"none": [none / alive, (none + U) / alive], "chained": [wt['chained'] / alive, (wt['chained'] + U) / alive],
              "direct (frozen bounds)": [wt['direct'] / alive, (wt['direct'] + U) / alive],
              "direct upper, tightened": (wt['direct'] + dic) / alive, "chained upper, tightened": (wt['chained'] + ruc) / alive},
       "Q1": {"set": S, "ruler (frozen bounds)": [wt['chained'] / S, (wt['chained'] + U) / S], "ruler upper, tightened": (wt['chained'] + ruc) / S},
       "Q2": {"direct (frozen bounds)": [wt['direct'] / S, (wt['direct'] + U) / S], "direct upper, tightened": (wt['direct'] + dic) / S}}
(Path(__file__).with_suffix('.json')).write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
