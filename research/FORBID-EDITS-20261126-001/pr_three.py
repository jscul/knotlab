"""pr_three.py: the three-reader form of part A3 (README.md). Worlds on each reader's two values (p_i, q_i), equally
weighted, allowed when q_1 + q_2 + q_3 equals the Mermin target of (p_1, p_2, p_3) (0 at 000, 1 at 011, 101, 110; 0
elsewhere); reader i's edit keeps its worlds with p_i = its setting; each reads q_i. Prints the Mermin win and checks
that every reader's and every pair's complete record has the same distribution for any setting of the others."""
import itertools, collections
from fractions import Fraction
target = {(0, 0, 0): 0, (0, 1, 1): 1, (1, 0, 1): 1, (1, 1, 0): 1}
W = [w for w in itertools.product((0, 1), repeat=6) if (w[3] ^ w[4] ^ w[5]) == target.get(w[:3], 0)]
win, recs = Fraction(0), {}
for st in itertools.product((0, 1), repeat=3):
    V = [w for w in W if w[:3] == st]
    if st in target: win += Fraction(sum(1 for w in V if (w[3] ^ w[4] ^ w[5]) == target[st]), len(V)) / 4
    for keep in ((0,), (1,), (2,), (0, 1), (0, 2), (1, 2)):
        d = collections.Counter(tuple((w[i], w[3 + i]) for i in keep) for w in V)
        recs[keep, st] = {a: Fraction(b, len(V)) for a, b in d.items()}
same = all(recs[keep, st] == recs[keep, st2] for keep in ((0,), (1,), (2,), (0, 1), (0, 2), (1, 2))
           for st in itertools.product((0, 1), repeat=3) for st2 in itertools.product((0, 1), repeat=3)
           if all(st[i] == st2[i] for i in keep))
print('worlds', len(W), 'Mermin win', win, '; every one- and two-reader record unchanged by the other settings:', same)
