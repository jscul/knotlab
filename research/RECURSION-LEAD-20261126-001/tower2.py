"""tower2.py SET OUT.jsonl: the tower's first step re-read (LAYERS-20261126-001's direction 3, run beside the recursion
lead).  For each start and each round t = 1..3 of ordinary growth under parity: the number of independent whole-held
facts (the dimension of the class labels less the dimension of those single knots read), under two readings of a small
change: SHORT, every shortest allowed change through each distinction (the record's, A291), and UPTO5, every allowed
change of at most five distinctions.  SET: census (a seeded sample of 400 census starts of three to five knots,
random.Random(20261208)), multi (the 16 starts with four or more classes in LAYERS-20261126-001), rings (built rings
joined in one start, LAYERS' structures).  A stage of more than MAX_DISTINCTIONS distinctions is not read."""
import sys, os, json, random, collections, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'LAYERS-20261126-001'))
import layers as LY, multi_class as MC
classes, forbid = LY.classes, LY.forbid
MAX_DISTINCTIONS = 400


def graph(supports):
    names = sorted({x for r in supports for x in r}); idx = {x: i for i, x in enumerate(names)}
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    U = len(supports); adj = collections.defaultdict(list)
    for x, h in holders.items():
        a, b = (h[0], h[1]) if len(h) == 2 else (h[0], U); adj[a].append((b, idx[x])); adj[b].append((a, idx[x]))
    return names, idx, adj, U


def moves_upto(supports, L=5):
    """every cycle of at most L distinctions of the graph reading (an allowed change), each once"""
    names, idx, adj, U = graph(supports); out = set()
    verts = sorted(adj)
    for s in verts:
        def dfs(v, used_e, used_v, mask, depth):
            for w, e in adj[v]:
                if e in used_e: continue
                if w == s and depth >= 1:
                    if depth + 1 >= 2 or True: out.add(mask | (1 << e))
                    continue
                if w in used_v or w < s or depth + 1 >= L: continue
                dfs(w, used_e | {e}, used_v | {w}, mask | (1 << e), depth + 1)
        dfs(s, frozenset(), frozenset([s]), 0, 0)
    return names, idx, sorted(out)


def whole_held(supports, moves, idx):
    n = len(idx)
    rows = [sum(1 << idx[x] for x in r) for r in supports]
    Z = classes.nullspace(rows, n); dH = classes.rank(moves); rR = classes.rank(rows)
    Hperp = classes.nullspace(moves, n)
    dim_labels = classes.rank(rows + Hperp) - rR
    local = []
    for r in supports:
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        local += [sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))]
    dim_local = classes.rank(rows + local) - rR
    return {'classes': 2 ** (len(Z) - dH), 'labels': dim_labels, 'read by single knots': dim_local,
            'whole-held': dim_labels - dim_local}


def read(start, rounds=3):
    out = []; st = start
    for t in range(1, rounds + 1):
        nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
        if status != 'funded': out.append({'round': t, 'end': status}); break
        nd = len({x for r in nxt for x in r})
        if nd > MAX_DISTINCTIONS: out.append({'round': t, 'end': 'not read: %d distinctions' % nd}); break
        names, idx, short = MC.moves_of(nxt)
        _, idx2, up = moves_upto(nxt, 5)
        out.append({'round': t, 'SHORT': whole_held(nxt, short, idx), 'UPTO5': whole_held(nxt, up, idx2)})
        st = nxt
    return out


def items(which):
    if which == 'census':
        S = forbid.census(); pick = random.Random(20261208).sample(range(len(S)), 400)
        for i in sorted(pick): yield 'census %d' % i, forbid.supports_of(S[i])
    elif which == 'multi':
        for x in json.load(open(ROOT / 'research/LAYERS-20261126-001/multi_class.json')):
            i = x['census index']; yield 'census %d (%s)' % (i, x['when']), forbid.supports_of(forbid.census()[i])
        for n, j in ((6, 105), (6, 228), (6, 293), (7, 37), (7, 193), (7, 236), (7, 239), (8, 191)):
            yield 'held out %d-%d' % (n, j), forbid.supports_of(forbid.sampled(n, 300, 20261206 + n)[j])
    else:
        for name, rings, joins in LY.STRUCTURES: yield name, LY.build(rings, joins)[0]


if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]
    seen = set()
    with open(out, 'w') as f:
        for name, sup in items(which):
            if name in seen: continue
            seen.add(name)
            try: rec = {'start': name, 'knots': len(sup), 'rounds': read(sup)}
            except Exception as e: rec = {'start': name, 'error': repr(e)[:200]}
            f.write(json.dumps(rec) + '\n'); f.flush()
