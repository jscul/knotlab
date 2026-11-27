"""post/upper_replay.py OUT.json: the thread's own replay of referee R1's bond one layer up (twelve knots, closed).
Enumerates the source states, reads the six lower agreements and the three upper agreements, and checks the upper
relation: seven of eight words, pairs full, every source law essential (deleting a law restores the missing word)."""
import sys, json, itertools
import numpy as np
W = json.load(open('referee-R1/layer_witness.json'))
K = [tuple(k) for k in W['source_knots_not_all_equal']]; L = W['lower_carriers_in_A0_A1_B0_B1_C0_C1_order']
n = 18; s = np.arange(1 << n, dtype=np.uint32)
bit = lambda x, st: ((st >> np.uint32(x)) & 1).astype(bool)
def ok_mask(knots, st):
    m = np.ones(len(st), dtype=bool)
    for k in knots:
        c = sum(bit(x, st).astype(int) for x in k); m &= (c > 0) & (c < len(k))
    return m
def agree(C, st):
    b = [bit(x, st) for x in C]; v = np.ones(len(st), dtype=bool)
    for y in b[1:]: v &= (y == b[0])
    return v
def upper_words(st):
    low = [agree(C, st) for C in L]
    up = [low[0] == low[1], low[2] == low[3], low[4] == low[5]]
    return set(zip(*[u.astype(int).tolist() for u in up])), up, low
A = s[ok_mask(K, s)]
words, up, low = upper_words(A)
out = {'states': int(len(A)), 'upper words': sorted(map(list, words)),
       'upper pairs': [len({(a, b) for a, b, c in [(w[i], w[j], 0) for w in words]}) for i, j in ((0, 1), (0, 2), (1, 2))],
       'lower words': len(set(zip(*[l.astype(int).tolist() for l in low])))}
out['deleting each source law restores 000'] = []
for q in range(len(K)):
    Aq = s[ok_mask([k for i, k in enumerate(K) if i != q], s)]
    out['deleting each source law restores 000'].append((0, 0, 0) in upper_words(Aq)[0])
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out))
