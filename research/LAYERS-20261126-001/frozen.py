"""frozen.py SET OUT.jsonl [I0 I1]: the frozen test (README, "Frozen").  SET: census (every census start of three to five
knots of FORBID-EDITS-20261126-001, starts I0..I1-1) or heldout (300 starts each of 6, 7 and 8 knots of its extension's
weighting, forbid.sampled with the fresh seed 20261206 + n).  For each start, under parity and the ordinary count, one
round: the conditions read from the start and its round alone (it grows; no old knot keeps a loose distinction; no three
knots pairwise share a distinction), the predicted number of classes 2^p (p the connected pieces holding a shared
distinction), and then the computed classes (moves: every shortest change through each distinction, no tie cap), whether
each piece's parity of old shared distinctions is a label, and for two or more classes whether the labels are read knot
by knot."""
import sys, os, json, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layers as LY
import multi_class as MC
LY.TIE_CAP = 10 ** 6
forbid = LY.forbid


def pieces(supports):
    """connected pieces of the start that hold a shared distinction, each as its set of shared distinctions"""
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    shared = [x for x, h in holders.items() if len(h) == 2]
    parent = list(range(len(supports)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for x in shared:
        a, b = holders[x]; parent[find(a)] = find(b)
    groups = collections.defaultdict(list)
    for x in shared: groups[find(holders[x][0])].append(x)
    return list(groups.values())


def triangle(supports):
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    nb = collections.defaultdict(set)
    for h in holders.values():
        if len(h) == 2: nb[h[0]].add(h[1]); nb[h[1]].add(h[0])
    return any(b in nb[a] and c in nb[a] and c in nb[b] for a, b, c in itertools.combinations(range(len(supports)), 3))


def one(sup):
    rec = {'knots': len(sup)}
    st, status, births = forbid.grown(sup, 'parity', 'ordinary')
    if status != 'funded': rec['grows'] = False; rec['end'] = status; return rec
    rec['grows'] = True
    old = {x for r in sup for x in r}
    holders = collections.defaultdict(list)
    for k, r in enumerate(st):
        for x in r: holders[x].append(k)
    rec['an old knot keeps a loose distinction'] = any(len(holders[x]) == 1 for k in range(len(sup)) for x in st[k] if x in old)
    rec['three knots pairwise share'] = triangle(sup)
    P = pieces(sup); rec['predicted classes'] = 2 ** len(P)
    rec['in the conditions'] = not rec['an old knot keeps a loose distinction'] and not rec['three knots pairwise share']
    a, Z, idx = LY.analyse(st, P)                    # the pieces' parities read as the "ring" labels
    rec['classes'] = a['classes']; rec['each piece parity a label'] = sorted(a['ring labels']) == list(range(len(P)))
    if a['classes'] >= 4:
        m = MC.read(st); rec['labels read knot by knot'] = m['labels read knot by knot'] == m['label space']
    return rec


if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]
    if which == 'census':
        S = forbid.census(); lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(S))
        items = [(i, forbid.supports_of(S[i])) for i in range(lo, min(hi, len(S)))]
    else:
        items = []
        for n in (6, 7, 8):
            for j, s in enumerate(forbid.sampled(n, 300, 20261206 + n)): items.append(('%d-%d' % (n, j), forbid.supports_of(s)))
    with open(out, 'w') as f:
        for i, sup in items:
            try: rec = one(sup)
            except Exception as e: rec = {'error': repr(e)[:200]}
            rec['index'] = i; f.write(json.dumps(rec) + '\n'); f.flush()
