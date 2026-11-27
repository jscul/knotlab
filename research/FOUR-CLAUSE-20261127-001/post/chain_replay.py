"""post/chain_replay.py OUT.json: the thread's replay of referee R1's chain finding.  Bare chains of L three-place
not-all-equal knots, (2i, 2i+1, 2i+2) for i < L, no growth: the full bond search, the four-clause patterns, and each
pattern's three readings (upper words, pairs free, read at one lower bond, laws needed)."""
import sys, json
sys.path.insert(0, '.'); sys.path.insert(0, '../UPPER-GROWN-20261127-001')
import fourclause as FC, boxes as BX
RB = BX.RB
out = {}
for L in (6, 7, 8, 9):
    S = tuple((2 * i, 2 * i + 1, 2 * i + 2) for i in range(L))
    st = RB.Stage(S, 'nae'); b = RB.bonds(st, 'agree')['bonds']; P = FC.find_patterns(b)
    rel = [r for p in P for r in FC.read_pattern(st, p, L)]
    out['chain of %d' % L] = {'bonds': len(b), 'patterns': len(P),
                              'steps': sum(1 for r in rel if len(r['upper words']) < 8 and r['pairs free'] and not r['an upper reading read at one lower bond']),
                              'every law needed': sum(1 for r in rel if len(r.get('laws needed', [])) == L),
                              'example': [[list(x[0][0]), x[1]] for pair in P[0] for x in pair] if P else None}
    print(L, json.dumps(out['chain of %d' % L]), flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
