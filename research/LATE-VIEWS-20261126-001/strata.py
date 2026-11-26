"""strata.py: the six-knot census read by structure alone (no growth): which starts the late-view predictor accepts, and
in which stratum, with the rare strata the advisor named before the freeze.  LATE-VIEWS-20261126-001.

    strata.py census OUT.json                 every census start of six knots: stall, cycle, or accepted, by stratum
    strata.py draw OUT.jsonl PER SEED         up to PER accepted starts of each rare stratum, outside the 5,000 sampled
                                              before (the three seeded samples), by random.Random(SEED).sample"""
import sys, os, json, random, collections, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import late, sample


def rare(M):
    """the rare strata a start falls in (a start can be in several)"""
    out = []
    ch = {q for q in M.chains if M.chains[q]}
    piece_of = {p: i for i, (pts, _, _) in enumerate(M.pieces) for p in pts}
    chained = {i for i, (pts, _, nch) in enumerate(M.pieces) if nch}
    if any(len(G) >= 4 and piece_of[next(iter(G))] in chained for G in M.cells): out.append('a group cell of four or more, with chains')
    if any(len(G) >= 4 for G in M.cells): out.append('a group cell of four or more')
    if len(M.cells) >= 2 and all(not (G & G2) for G, G2 in itertools.combinations(M.cells, 2)): out.append('two disjoint group cells')
    if any(len(G & G2) == 1 for G, G2 in itertools.combinations(M.cells, 2)): out.append('group cells sharing a knot')
    if M.overlap[1]: out.append('group cells sharing two knots')
    if M.overlap[0] and any(piece_of[next(iter(G))] in chained for G in M.cells): out.append('a block meeting a group cell, with chains')
    return out


def read(stars):
    M = late.Map(stars)
    if M.cls != 'in': return M, M.cls, []
    if not all(tree for _, tree, _ in M.pieces): return M, 'a piece with a cycle', []
    return M, 'accepted', rare(M)


if __name__ == '__main__':
    if sys.argv[1] == 'census':
        res = collections.Counter(); st = collections.Counter(); rr = collections.Counter()
        for i, gi, loose, stars in sample.alike.census(6):
            M, what, r = read(stars)
            res[what] += 1
            if what == 'accepted': st[M.stratum] += 1
            for x in r: rr[x] += 1
        out = {'six-knot census starts': sum(res.values()), 'read': dict(res), 'accepted, by stratum': dict(st),
               'accepted, rare strata': dict(rr)}
        json.dump(out, open(sys.argv[2], 'w'), indent=1); print(json.dumps(out, indent=1))
    elif sys.argv[1] == 'draw':
        out, per, seed = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        C = sample.alike.census(6)
        first = random.Random(20261126).sample(C, 1000)
        rest = [c for c in C if c[0] not in {x[0] for x in first}]
        second = random.Random(20261127).sample(rest, 2000)
        rest = [c for c in rest if c[0] not in {x[0] for x in second}]
        third = random.Random(20261128).sample(rest, 2000)
        used = {x[0] for x in first + second + third}
        pool = collections.defaultdict(list)
        for i, gi, loose, stars in C:
            if i in used: continue
            M, what, r = read(stars)
            for x in r: pool[x].append([i, gi, loose, stars])
        rng = random.Random(seed); chosen = {}
        for name in sorted(pool):
            for c in rng.sample(pool[name], min(per, len(pool[name]))):
                chosen.setdefault(c[0], (c, name))
        with open(out, 'w') as f:
            for i in sorted(chosen):
                c, name = chosen[i]
                f.write(json.dumps({'index': i, 'graph': c[1], 'loose': c[2], 'stars': c[3], 'drawn for': name}) + '\n')
        print({k: len(v) for k, v in pool.items()}, len(chosen))
