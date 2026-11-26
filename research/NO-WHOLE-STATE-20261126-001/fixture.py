"""fixture.py: the advisor's fixture (README.md, part C). The ring of three knots, each with one loose distinction,
grown one round by ordinary growth under parity: does it close on an implied birth, and is the closed pattern the holder
pattern of the three-reader argument (four knots, six distinctions, every two knots sharing one)? Then, reading it part
by part (a context's part: the knots lying wholly within the three distinctions read), with the readers the three pairs
of distinctions no knot holds together, and the closing knot's sign reversed: the 64 probabilities against the
three-reader target (each scored context uniform on the words of its knot's parity, each unscored context uniform on all
eight), agreement on overlaps, and the control (a scored triple's parity as the other three knots imply it). With the
closing sign as growth makes it (even), the same reading as the comparison."""
import sys, itertools, json
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import parts, forbid

ring3 = ((0, 1, 2), (1, 3, 4), (3, 0, 5))
stage, info = forbid.grow(ring3, 'parity', 'ordinary', forbid.ENGINE) if hasattr(forbid, 'grow') else (None, None)
print(json.dumps({'grown stage': stage, 'births': [(b['parents'], b['inputs'], b['f']) for b in info['births']],
                  'next round': info['following_funding']['status']}))
closing = tuple(stage[-1])
holders = forbid.holders(stage)
assert all(len(h) == 2 for h in holders.values())
knotsets = [set(k) for k in stage]
pairs = [p for p in itertools.combinations(sorted(holders), 2) if not any(set(p) <= k for k in knotsets)]
print(json.dumps({'closing knot': closing, 'pairs no knot holds together': pairs,
                  'every two knots share one distinction': all(len(a & b) == 1 for a, b in itertools.combinations(knotsets, 2))}))
readers = pairs                                        # three disjoint pairs, one per reader
assert len(readers) == 3 and len({d for p in readers for d in p}) == 6
for sign in (0, 1):
    pattern = [(tuple(k), sign if tuple(k) == closing else 0) for k in stage]
    contexts = {s: [readers[i][s[i]] for i in range(3)] for s in itertools.product((0, 1), repeat=3)}
    T = {s: parts.table(pattern, list(r), 'closed') for s, r in contexts.items()}
    match = 0
    for s, r in contexts.items():
        k = [(kk, p) for kk, p in pattern if set(kk) == set(r)]
        target = {w: (Fraction(1, 4) if sum(w) % 2 == k[0][1] else Fraction(0)) for w in itertools.product((0, 1), repeat=3)} if k \
            else {w: Fraction(1, 8) for w in itertools.product((0, 1), repeat=3)}
        got = {w: T[s].get(w, Fraction(0)) for w in target}
        match += sum(1 for w in target if got[w] == target[w])
    agree = all(parts.marginal(T[a], contexts[a], sorted(set(contexts[a]) & set(contexts[b]))) ==
                parts.marginal(T[b], contexts[b], sorted(set(contexts[a]) & set(contexts[b])))
                for a, b in itertools.combinations(contexts, 2) if set(contexts[a]) & set(contexts[b]))
    whole = bool(parts.allowed(pattern, sorted(holders)))
    # the control: each scored triple's parity as the other three knots imply it (each distinction outside it held twice)
    control = {}
    for kk, p in pattern:
        others = sum(q for k2, q in pattern if k2 != kk) % 2
        control[str(kk)] = {'own parity': p, 'implied by the other three': others, 'opposite': p != others}
    # Mermin win, with each reader's relabelling chosen freely
    best = 0
    for rl in itertools.product((0, 1), repeat=6):
        w = Fraction(0)
        for kk, p in pattern:
            s = next(s for s, r in contexts.items() if set(r) == set(kk))
            want = (p + sum(rl[2 * i + s[i]] for i in range(3))) % 2
            w += sum(q for word, q in T[s].items() if (sum(word) + sum(rl[2 * i + s[i]] for i in range(3))) % 2 == want) / 4
        best = max(best, w)
    print(json.dumps({'closing sign': 'odd' if sign else 'even (as growth makes it)', 'whole has an allowed state': whole,
                      'probabilities matching the three-reader target': '%d of 64' % match, 'overlaps agree': agree,
                      'control': control}))
