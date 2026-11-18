"""Gate checks for FIRST-KNOT-20261118-001B-E001.  python3 -B checks.py"""
import json
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import startlib as S  # noqa: E402

F = S.F
results = {}


def gate(name, ok, detail=''):
    results[name] = {'pass': bool(ok), 'detail': detail}
    print(('PASS ' if ok else 'FAIL ') + name + (f'  {detail}' if detail else ''))


# H1: a one-junction start reproduces FRESH-COUNT's single-seed growth (uniform and fewest)
ok = True
for a in (3, 4):
    P1, o1 = S.grow([list(range(a))], F.uniform(a), 6)
    P2, o2, _ = F.run(a, F.uniform(a), 6)
    ok &= P1.counts_by_round() == P2.counts_by_round() and o1 == o2
    Q1, p1 = S.grow([list(range(a))], F.fewest, 8)
    Q2, p2, _ = F.run(a, F.fewest, 8)
    ok &= Q1.counts_by_round() == Q2.counts_by_round() and p1 == p2
gate('H1 one-junction start = single-seed growth', ok)

# H2: the GF(2) implied test closes two separate knots (the structural test of the single-seed library would not)
P, o = S.grow(S.pair(3, 3, 0), F.fewest, 10)
gate('H2 two separate three-place knots close under fewest', o == 'closed' and P.counts_by_round() == [2, 6, 6, 2],
     f'{o} {P.counts_by_round()}')

# H3: pieces: with a start of two knots sharing one distinction, no junction of one piece ever neighbours one of the other,
# except the two start junctions themselves
P, o = S.grow(S.pair(4, 5, 1), F.fewest, 12)
piece = {0: 0, 1: 1}
for j in range(2, len(P.bits_of)):
    pars = {x for b in P.bits_of[j] for x in P.owner[b] if x < j}
    ps = {piece[x] for x in pars}
    piece[j] = ps.pop() if len(ps) == 1 else None
mixed = [j for j, v in piece.items() if v is None]
gate('H3 two pieces never mix (4 + 5 sharing one, fewest, 12 rounds)', not mixed, f'{len(P.bits_of)} junctions, mixed {mixed[:5]}')

# H4: a mutant start (a distinction in three junctions) is refused
try:
    S.from_junctions([[0, 1, 2], [0, 3, 4], [0, 5, 6]])
    refused = False
except ValueError:
    refused = True
gate('H4 a distinction in three knots is refused', refused)

# H5: the two-product count formula on a known case: two separate N^3
P, o = S.grow(S.pair(3, 3, 0), F.uniform(3), 6)
gate('H5 two separate three-place knots with count 3: two N^3', all(P.counts_by_round()[t] == 2 * comb(t + 2, 2) for t in range(1, 7)),
     str(P.counts_by_round()))

json.dump(results, open(HERE / 'checks_output.json', 'w'), indent=1)
print(f'{sum(r["pass"] for r in results.values())} of {len(results)} gates pass')
