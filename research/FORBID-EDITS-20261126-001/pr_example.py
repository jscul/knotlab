"""pr_example.py: the abstract example of part A3 (README.md). Eight equally weighted worlds on Alice's two old values
(p, q) and Bob's two (r, s), allowed exactly when q + s = p r (mod 2); Alice's edit x keeps only her worlds with p = x,
Bob's edit y those with r = y; each reads her second value (q) and his (s). Prints the four tables, CHSH, and checks
that each reader's complete record (both values) has the same distribution for either far setting."""
import itertools
from fractions import Fraction
W = [(p, q, r, s) for p, q, r, s in itertools.product((0, 1), repeat=4) if (q ^ s) == (p & r)]
E, rec = {}, {}
for x, y in itertools.product((0, 1), repeat=2):
    V = [w for w in W if w[0] == x and w[2] == y]          # the worlds the two edits leave
    E[x, y] = Fraction(sum(1 if w[1] == w[3] else -1 for w in V), len(V))
    rec[x, y] = (sorted((w[0], w[1]) for w in V), sorted((w[2], w[3]) for w in V))
print('worlds', len(W), 'correlations', {k: str(v) for k, v in E.items()})
print('CHSH', E[0, 0] + E[0, 1] + E[1, 0] - E[1, 1])
print("Alice's record the same for either far setting:", all(rec[x, 0][0] == rec[x, 1][0] for x in (0, 1)),
      "; Bob's:", all(rec[0, y][1] == rec[1, y][1] for y in (0, 1)))
