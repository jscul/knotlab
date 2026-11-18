"""Score TOUCH-CENSUS-20261118-001B-E001's frozen predictions.  python3 -B merge.py <run dir> [<out json>]"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from longrun import load_results  # noqa: E402

recs = load_results(sys.argv[1])
bad = [c for c, r in recs.items() if r.get('status') != 'ok']
A = [a for c, r in recs.items() if r.get('status') == 'ok' for a in r['result']['arrangements']]
score, notes = {}, {}
N = len(A)
L = sum(a['labelled'] for a in A)


def nk(a):
    return len(a['key'][0])


growing = [a for a in A if a['outcome'] in ('alive', 'big')]
settled = [a for a in growing if a['dim'] is not None]
unsettled = [a for a in growing if a['dim'] is None]

# P1a: every settled growing arrangement without a birth has dimension 1; P1b: with a birth, dimension = largest class
p1a = [a for a in settled if not a['any_birth'] and a['dim'] != 1]
p1b = [a for a in settled if a['any_birth'] and a['dim'] != a['rule']]
closed_bad = [a for a in A if a['outcome'] == 'closed' and a['dim'] != 0]
score['P1a'] = not p1a
score['P1b'] = not p1b
notes['P1'] = {'birthless growing': sum(1 for a in settled if not a['any_birth']), 'P1a exceptions': [(a['key'], a['dim']) for a in p1a[:10]],
               'P1b exceptions': [(a['key'], a['dim'], a['rule'], a['births']) for a in p1b[:10]], 'n P1b exceptions': len(p1b),
               'birth rounds seen': dict(Counter(r for a in A for r in a['birth_rounds']))}

# distribution
def dist(sel, weight):
    c = Counter()
    for a in sel:
        key = 'stall' if a['outcome'] == 'stall' else ('unsettled' if a['dim'] is None else a['dim'])
        c[key] += weight(a)
    return {str(k): v for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))}


notes['distribution, distinct'] = dist(A, lambda a: 1)
notes['distribution, labelled'] = dist(A, lambda a: a['labelled'])
by_n = defaultdict(list)
for a in A:
    by_n[nk(a)].append(a)
notes['by knots, distinct'] = {n: dist(v, lambda a: 1) for n, v in sorted(by_n.items())}
notes['by knots, labelled'] = {n: dist(v, lambda a: a['labelled']) for n, v in sorted(by_n.items())}

# P2: dimension >= 3 in under 2% of distinct arrangements and of labelled weight; 2 the most common among settled growing
hi_d = sum(1 for a in settled if a['dim'] >= 3)
hi_l = sum(a['labelled'] for a in settled if a['dim'] >= 3)
dc = Counter(a['dim'] for a in settled)
score['P2'] = hi_d < 0.02 * N and hi_l < 0.02 * L and dc.most_common(1)[0][0] == 2
notes['P2'] = {'dim>=3 distinct': hi_d, 'of': N, 'dim>=3 labelled': hi_l, 'of labelled': L, 'settled dims': dict(dc)}

# P3: no settled dimension >= 5, no unsettled case after the rerun, exactly one arrangement of dimension 4
d4 = [a['key'] for a in settled if a['dim'] == 4]
score['P3'] = not unsettled and all(a['dim'] <= 4 for a in settled) and len(d4) == 1
notes['P3'] = {'unsettled': [(a['key'], a['last']) for a in unsettled[:10]], 'n unsettled': len(unsettled), 'dimension 4': d4,
               'max': max((a['dim'] for a in settled), default=None), 'reruns': sum(1 for a in A if a['rerun'])}

# P4: every stall in round 1
stalls = [a for a in A if a['outcome'] == 'stall']
score['P4'] = all(a['stall_round'] == 1 for a in stalls)
notes['P4'] = {'stalls': len(stalls), 'rounds': dict(Counter(a['stall_round'] for a in stalls))}

# P5: stall share rises with the number of knots and exceeds 40% at five knots; among settled growing, the share of dimension 2
# rises and that of dimension 1 falls from two to five knots
share_stall = {n: sum(1 for a in v if a['outcome'] == 'stall') / len(v) for n, v in by_n.items()}
sg = {n: [a for a in v if a['outcome'] in ('alive', 'big') and a['dim'] is not None] for n, v in by_n.items()}
s2 = {n: (sum(1 for a in v if a['dim'] == 2) / len(v) if v else None) for n, v in sg.items()}
s1 = {n: (sum(1 for a in v if a['dim'] == 1) / len(v) if v else None) for n, v in sg.items()}
ns = [2, 3, 4, 5]
score['P5'] = (all(share_stall[ns[i]] < share_stall[ns[i + 1]] for i in range(3)) and share_stall[5] > 0.4
               and all(s2[ns[i]] < s2[ns[i + 1]] for i in range(3)) and all(s1[ns[i]] > s1[ns[i + 1]] for i in range(3)))
notes['P5'] = {'stall share': share_stall, 'dim 2 share of settled growing': s2, 'dim 1 share': s1}

# P6: no forced distinction anywhere
score['P6'] = all(a['forced'] == 0 for a in A)
notes['P6'] = {'with forced': sum(1 for a in A if a['forced'])}

out = {'arrangements': N, 'labelled': L, 'not_ok_cases': bad, 'score': score, 'notes': notes}
txt = json.dumps(out, indent=1, default=str)
print(txt)
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(txt)
