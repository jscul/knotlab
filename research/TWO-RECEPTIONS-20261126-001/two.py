"""two.py: can a far pattern's own knots send two distinct changes that the receiver's own knots both receive and keep?
First study of TWO-RECEPTIONS-20261126-001 (a check by the thread, not registered); README.md has the design and the
expectations, written before the full run.

The pairs: the 28 far ends that stay linked to the switch kind through round 16 under the caps of three and four
(LINKED-UNDER-CAP-20261126-001), joined by a meeting through two link knots, waiting, 32 rounds or 10,000 knots.
    W    the growth without a change
    G1   one more loose distinction at the nearest, or the second nearest, member of the far end's own knots in a part
         linked to the receiver's, after round 3; r1 the first round the receiver's own births differ from W
    G2   in G1, one more loose distinction at each of the eight nearest such members of G1 after round t, for each
         t = 4 .. r1 - 1 (a second change made before the first is heard)
Read for each G2, round by round from t: whether the receiver's own births equal W's and G1's.  Kinds:
    cancels     G2's own births equal W's from some round on (the second undoes the first)
    merges      G2 differs from G1 at r1 or earlier (the first response itself changes)
    two         G2 equals G1 at r1 (the first response kept), differs from G1 at some later round r2, and differs
                from both W and G1 at the last round read (both responses persist)
    second, not kept   G2 equals G1 at r1, differs later, and equals W or G1 at the last round read
    unheard     G2 equals G1 in every round read

    two.py run LAW I0 I1      the pairs I0..I1-1 of the 28 under LAW, a JSON line per second change"""
import sys, os, json, gzip
HERE = os.path.dirname(os.path.abspath(__file__))
LK = os.path.join(HERE, '..', 'LINKED-UNDER-CAP-20261126-001')
sys.path.insert(0, LK)
import linked
second, receivers, ring_line, jam, bench, eng = linked.second, linked.receivers, linked.ring_line, linked.jam, linked.bench, linked.eng
ROUNDS, BOUND = 32, 10000
second.ROUNDS, second.BOUND = ROUNDS, BOUND


def pairs(law):
    out = []
    for l in gzip.open(os.path.join(LK, 'linked_runs.jsonl.gz'), 'rt'):
        r = json.loads(l)
        if r.get('law') == law and r['A'].startswith('tri') and len(r['linked']) >= 16 and r['linked'][15]: out.append((r['A'], r['B']))
    return sorted(out)


def own(g): return [r['own'] for r in g.rows]


def kind(W, G1, G2, r1, t):
    n = min(len(W.rows), len(G1.rows), len(G2.rows))
    w, a, b = own(W)[:n], own(G1)[:n], own(G2)[:n]
    if a == b: return 'unheard', None, n
    r2 = next(i + 1 for i in range(t, n) if a[i] != b[i])
    if any(b[i:] == w[i:] for i in range(r1 - 1, n)): return 'cancels', r2, n
    if r2 <= r1: return 'merges', r2, n
    if b[n - 1] != w[n - 1] and b[n - 1] != a[n - 1]: return 'two', r2, n
    return 'second, not kept', r2, n                  # a later difference from G1 that does not last (the advisor's)


if __name__ == '__main__':
    receivers.register()
    law, i0, i1 = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    for A, B in pairs(law)[i0:i1]:
        a = int(A.split(':')[1][0]); bench.STARS[A], bench.SITE[A] = second.tri(a), 0
        st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
        W = ring_line.Growth(st, ro, jam.law_of(law, 'CANCEL-WAIT')); W.run(ROUNDS, BOUND)
        ms1, d1 = linked.far_members(W, 3, True)
        for k1, u1 in enumerate(ms1[:2]):
            G1 = second.changed_at(W, 3, u1, 'add'); r1, _ = ring_line.first_own_diff(W, G1, 3)
            if r1 is None:
                print(json.dumps({'A': A, 'B': B, 'law': law, 'first': [k1, u1, d1.get(u1)], 'r1': None}), flush=True); continue
            for t in range(4, r1):
                ms2, d2 = linked.far_members(G1, t, True)
                for u2 in ms2[:8]:
                    G2 = second.changed_at(G1, t, u2, 'add')
                    kd, r2, n = kind(W, G1, G2, r1, t)
                    print(json.dumps({'A': A, 'B': B, 'law': law, 'first': [k1, u1, d1.get(u1)], 'r1': r1, 't': t, 'second': [u2, d2.get(u2)],
                                      'kind': kd, 'r2': r2, 'rounds': n}), flush=True)
