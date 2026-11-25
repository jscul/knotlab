"""A probe for sub-goal B334 (not a frozen study; the thread's own run): the count of members within r witnessed steps of a member, at one
round, from EVERY member (or an even sample of at most CAP), on the census starts whose births grow fastest under
the ordinary count.  Uses the reach study's engine unchanged, read-only."""
import sys, os, json, gzip, time, collections, resource
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
X = ROOT + '/experiments/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach'
sys.dont_write_bytecode = True
sys.path.insert(0, X)
import numpy as np
import kwr
from scipy.sparse.csgraph import shortest_path

CAP = 2500

def diffs(v, k):
    v = list(v)
    for _ in range(k):
        v = [v[i + 1] - v[i] for i in range(len(v) - 1)]
    return v

def poly_prefix(seq, deg):
    """longest R such that seq[0..R] has constant deg-th difference c > 0 (and is not of lower degree); (R, c)."""
    d = diffs(seq, deg)
    if not d or d[0] <= 0:
        return 0, None
    c = d[0]; n = 0
    while n < len(d) and d[n] == c:
        n += 1
    return n - 1 + deg, c

def read_stage(G, t):
    S = G.S
    members = G.members[t]
    upto = G.n_knots[t]
    ms = kwr.met_sets(S, members, upto)
    parts = kwr.parts_of(S, members, upto, ms)
    sizes = sorted((len(p) for p in parts), reverse=True)
    big = max(parts, key=len)
    out = {'round': t, 'knots': upto, 'members': len(members), 'parts': len(parts), 'part sizes (largest 5)': sizes[:5]}
    if len(big) < 30:
        return out
    bms = {w: M for w, M in ms.items() if next(iter(M)) in set(big)}
    step = max(1, len(big) // CAP + (1 if len(big) % CAP and len(big) > CAP else 0))
    sources = list(big)[::step]
    dist, idx = kwr.ws_from(S, list(big), sources, upto, bms)
    seqs = {}
    nb = collections.Counter()
    for s in sources:
        d = dist[s]
        d = d[np.isfinite(d)].astype(int)
        cnt = np.bincount(d)
        seq = np.cumsum(cnt).tolist()
        seqs[s] = seq
        nb[seq[1] - 1 if len(seq) > 1 else 0] += 1
    out['sources'] = len(sources); out['of members in the part'] = len(big)
    out['neighbours within one step, by count of members'] = dict(sorted(nb.items()))
    out['greatest steps, least and greatest over sources'] = [min(len(s) - 1 for s in seqs.values()), max(len(s) - 1 for s in seqs.values())]
    for deg in (1, 2, 3):
        best = None; tally = collections.Counter()
        for s, seq in seqs.items():
            R, c = poly_prefix(seq, deg)
            if c is None: continue
            # exclude sequences that are exactly of lower degree on that range
            if deg > 1 and poly_prefix(seq, deg - 1)[0] >= R: continue
            tally[(c, R)] += 1
            if best is None or R > best[0]:
                best = (R, c, s, seq[:R + 3])
        if best:
            byc = collections.Counter()
            for (c, R), n in tally.items():
                if R >= deg + 4: byc[c] += n
            out['degree %d' % deg] = {'longest exact prefix r': best[0], 'its top difference': best[1], 'member': best[2],
                                      'its counts': best[3], 'sources with an exact prefix through r >= %d, by top difference' % (deg + 4): dict(byc)}
    # the envelope: greatest count at each r over sources
    L = max(len(s) for s in seqs.values())
    env = [max((s[r] if r < len(s) else s[-1]) for s in seqs.values()) for r in range(L)]
    out['greatest count at each r (first 30)'] = env[:30]
    return out

def main():
    key, law, knot_law, rounds = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    stages = [int(x) for x in sys.argv[5].split(',')]
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    t0 = time.time()
    G = kwr.Grown(key, kwr.make_law(law, knot_law), rounds, parts_every_round=False)
    done = G.rounds_done() if callable(getattr(G, 'rounds_done', None)) else G.S.round
    rec = {'start': key, 'law': law, 'knot law': knot_law, 'rounds done': done, 'stop': G.stop, 'ended': G.ended,
           'knots': G.n_knots[-1], 'members per round': [len(m) for m in G.members], 'grow seconds': round(time.time() - t0, 1), 'stages': []}
    for t in stages + [done]:
        if t <= done and t not in [s['round'] for s in rec['stages']]:
            t1 = time.time()
            st = read_stage(G, t); st['seconds'] = round(time.time() - t1, 1)
            rec['stages'].append(st)
    print(json.dumps(rec))

if __name__ == '__main__':
    main()
