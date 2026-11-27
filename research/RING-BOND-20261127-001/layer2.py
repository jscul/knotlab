"""layer2.py OUT.json [ROUNDS] [MAXB]: the layer above the ring's bonds.  RING-BOND-20261127-001; README.md.

On the grown ring's stage at rounds 1..ROUNDS, take the bonds of the full search (agreement readings) as laws on their
readings: each bond forbids its missing triples.  A cluster is a connected set of at most MAXB bonds (two meet when they
share a reading) whose distinct readings lie on pairwise disjoint carriers (with --overlap: any distinct readings, the
overlapping ones then treated as separate variables in conj, a swap of the scaffold).  For each cluster:
  conj   the words on its readings allowed by its bonds alone (the bonds as the laws of a system of their own)
  J      the words its readings take on the stage's allowed states
  L1     bonds of the layer above on conj: three agreement readings on disjoint carriers of two or three of the
         cluster's readings, every two free, a triple missing, every bond of the cluster essential (its removal from
         conj lets a missing triple occur), none read at a single bond (ringbond.bonds on a RelStage)
  L2     whether J equals conj (the bonds present the readings' joint image) or is smaller (the stage holds a relation
         among the readings that its bonds do not)
The bonds taken as laws, and the cluster rule, are scaffolds (README.md, "Scaffolds")."""
import sys, json, itertools, collections, time
import numpy as np
import ringbond as RB


def name(C): return '[' + '='.join(map(str, C)) + ']'


def run(sup, born, maxb, overlap=False):
    st = RB.Stage(sup, 'nae'); res = RB.bonds(st, 'agree', born=born)
    bl = [b for b in res['bonds']]
    rd = [[(tuple(C), lab) for C, lab in b['readings']] for b in bl]
    by_r = collections.defaultdict(list)
    for k, rs in enumerate(rd):
        for r in rs: by_r[r].append(k)
    def disjoint(rs):
        if overlap: return True
        seen = set()
        for C, lab in rs:
            if seen & set(C): return False
            seen |= set(C)
        return True
    # clusters of connected bonds, at most maxb, readings on pairwise disjoint carriers
    clusters = set(); frontier = set()
    for k in range(len(bl)):
        for r in rd[k]:
            for k2 in by_r[r]:
                if k2 > k:
                    c = (k, k2); u = set(rd[k]) | set(rd[k2])
                    if disjoint(sorted(u)): frontier.add(c)
    clusters |= frontier
    for _ in range(maxb - 2):
        nxt = set()
        for c in frontier:
            u = set().union(*(set(rd[q]) for q in c))
            for r in u:
                for k2 in by_r[r]:
                    if k2 in c: continue
                    c2 = tuple(sorted(c + (k2,)))
                    if c2 in clusters or c2 in nxt: continue
                    if disjoint(sorted(u | set(rd[k2]))): nxt.add(c2)
        clusters |= nxt; frontier = nxt
    out = collections.Counter(); ex = []
    for c in sorted(clusters):
        laws = [([name(C) for C, lab in rd[q]], {int(m, 2) for m in bl[q]['missing']}) for q in c]
        s2 = RB.RelStage(laws)
        r2 = RB.bonds(s2, 'agree', born=0)
        b2 = [b for b in r2['bonds'] if len(b['essential']) == len(c)]
        # J: the readings' words on the stage
        u = sorted(set().union(*(set(rd[q]) for q in c)), key=lambda r: name(r[0]))
        idx = {name(C): p for p, (C, lab) in enumerate(u)}
        code = np.zeros(len(st.A), dtype=np.int64)
        for C, lab in u:
            b = [st.bits(x, st.A) for x in C]; v = np.ones(len(st.A), dtype=bool)
            for y in b[1:]: v &= (y == b[0])
            code = code * 2 + v
        J = set(np.unique(code).tolist())
        conj = set()
        for s in s2.A.tolist():
            w = 0
            for C, lab in u: w = w * 2 + ((s >> s2.idx[name(C)]) & 1)
            conj.add(w)
        assert J <= conj
        out['clusters %d bonds' % len(c)] += 1
        out['L1 clusters with a bond of the layer above'] += bool(b2)
        out['L1 bonds of the layer above'] += len(b2)
        out['L2 J equals conj'] += J == conj
        out['L2 J smaller than conj'] += J != conj
        if (b2 or J != conj) and len(ex) < 6:
            ex.append({'cluster': [bl[q]['readings'] for q in c], 'layer-above bonds': b2[:2], 'J': len(J), 'conj': len(conj)})
    return {'bonds': len(bl), 'clusters': len(clusters), 'tally': dict(out), 'examples': ex}


if __name__ == '__main__':
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 2; maxb = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    overlap = '--overlap' in sys.argv
    S = ((0, 1, 3), (1, 2, 4), (2, 0, 5)); res = {}
    for t, (sup, born) in enumerate(RB.stages(S, 'nae', rounds)):
        if t == 0: continue
        t0 = time.time(); res['round %d' % t] = run(sup, born, maxb, overlap); res['round %d' % t]['seconds'] = round(time.time() - t0, 1)
        print(t, json.dumps(res['round %d' % t]['tally']), res['round %d' % t]['seconds'], flush=True)
    json.dump(res, open(sys.argv[1], 'w'), indent=1, default=str)
