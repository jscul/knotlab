"""closing.py SET LAW OUT.jsonl: the closing test.  BUILT-BINDING-20261126-001; README.md.

The advisor's reading of RELAY-IDENT's closing rule: the sum of every knot law of a connected structure is the parity of
its loose distinctions, so under parity a birth's law (the parity of its inputs, all of them loose distinctions of its
parents) already follows from the present laws exactly when its inputs are every loose distinction of the connected
structure holding its parents: when the rest of that structure holds no loose distinction.  On every birth of rounds 1
to 3 of ordinary growth from each start of SET (census: every census start of three to five knots; heldout: the 900
fresh starts of six to eight knots; built: the built start of built.py and its variants), under LAW (parity, or
not-all-equal as the control), record the engine's own flag (its inputs already imply its law, found by elimination
against every present knot), its fresh count, and whether its inputs are every loose distinction of its parents'
connected structure."""
import sys, json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import built as BU
forbid = BU.forbid


def components(st):
    h = forbid.holders(st); parent = list(range(len(st)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for x, hs in h.items():
        for k in hs[1:]: parent[find(k)] = find(hs[0])
    comp = collections.defaultdict(set)
    for k in range(len(st)): comp[find(k)].add(k)
    loose = {x for x, hs in h.items() if len(hs) == 1}
    of = {}
    for c in comp.values():
        lc = {x for k in c for x in st[k] if x in loose}
        for k in c: of[k] = lc
    return of


def items(which):
    if which == 'census':
        for i, s in enumerate(forbid.census()): yield 'census %d' % i, forbid.supports_of(s)
    elif which == 'heldout':
        for n in (6, 7, 8):
            for j, s in enumerate(forbid.sampled(n, 300, 20261206 + n)): yield 'held out %d-%d' % (n, j), forbid.supports_of(s)
    else:
        for var in ('base', 'no v', 'J loose', 'J two loose'): yield 'built ' + var, BU.build(var)[0]


if __name__ == '__main__':
    which, law, out = sys.argv[1], sys.argv[2], sys.argv[3]
    tally = collections.Counter()
    with open(out, 'w') as f:
        for name, S in items(which):
            st = S; rows = []
            for t in range(1, 4):
                comp = components(st)
                nxt, status, births = forbid.grown(st, law, 'ordinary')
                if status != 'funded': rows.append({'round': t, 'end': status}); break
                for b in births:
                    allc = set(b['inputs']) == comp[b['parents'][0]]
                    key = (law, 'implied' if b['old_inputs_already_imply_law'] else 'not implied',
                           'takes every loose distinction of its structure' if allc else 'leaves some',
                           'fresh 0' if b['f'] == 0 else 'fresh > 0')
                    tally[key] += 1
                    rows.append({'round': t, 'parents': b['parents'], 'p': b['p'], 'f': b['f'],
                                 'implied': b['old_inputs_already_imply_law'], 'takes all': allc})
                st = nxt
            f.write(json.dumps({'start': name, 'law': law, 'births': rows}) + '\n')
        f.write(json.dumps({'tally': [[list(k), v] for k, v in sorted(tally.items())]}) + '\n')
    for k, v in sorted(tally.items()): print(k, v)
