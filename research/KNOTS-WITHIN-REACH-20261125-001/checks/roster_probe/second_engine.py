"""A second growth engine for the probe's headline: the record's own round (lr_core.own_round of
LOCAL-ROUND-20261123-001A, ORD with STALL = the ordinary count), with the roster, its meetings and the counts
recomputed here from scratch (no code of the reach study)."""
import sys, json, collections, gzip
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, ROOT + '/experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round')
import lr_core

def stage(stars, rounds):
    S = lr_core.Str([list(s) for s in stars])
    for _ in range(rounds):
        rec = lr_core.own_round(S, 'ORD', 'STALL')
        assert not rec.get('stalled')
    members = [u for u in range(len(S.places)) if S.usable(u)]
    mset = set(members)
    met = collections.defaultdict(set)          # knot w -> members it meets (shares a distinction with)
    for u in members:
        for d in S.places[u]:
            for w in S.holders[d]:
                if w != u:
                    met[w].add(u)
    adj = {u: set() for u in members}
    for w, M in met.items():
        if len(M) >= 2:
            for a in M:
                adj[a] |= M - {a}
    env = []; nb = collections.Counter(len(adj[u]) for u in members)
    seqs = []
    for s in members:
        dist = {s: 0}; frontier = [s]; counts = [1]
        while frontier:
            nxt = []
            for a in frontier:
                for b in adj[a]:
                    if b not in dist:
                        dist[b] = dist[a] + 1; nxt.append(b)
            if nxt: counts.append(counts[-1] + len(nxt))
            frontier = nxt
        seqs.append(counts)
    L = max(len(s) for s in seqs)
    env = [max(s[r] if r < len(s) else s[-1] for s in seqs) for r in range(L)]
    comp = len(seqs[0]) and max(s[-1] for s in seqs)
    return {'knots': len(S.places), 'members': len(members), 'largest part reached from a member': comp,
            'neighbours': dict(sorted(nb.items())), 'greatest count at each r': env}

cs = json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))
probe = [json.loads(l) for l in gzip.open(os.path.join(HERE, 'probe_runs.jsonl.gz'), 'rt')]
for idx, rounds in ((19, 10), (19, 20), (177, 10), (177, 15), (218, 10), (178, 20)):
    mine = stage(cs[idx]['stars'], rounds)
    p = next(d for d in probe if d['start'] == f'census:{idx}' and d['law'] == 'L0')
    st = next(s for s in p['stages'] if s['round'] == rounds)
    pe = st['greatest count at each r (first 30)']
    pn = {int(k): v for k, v in st['neighbours within one step, by count of members'].items()}
    print(f'census {idx} round {rounds}: knots {mine["knots"]} / {st["knots"]}; members {mine["members"]} / {st["members"]}; '
          f'neighbours equal {mine["neighbours"] == pn}; counts equal {mine["greatest count at each r"] == pe[:len(mine["greatest count at each r"])] or mine["greatest count at each r"][:len(pe)] == pe}')
    print('   ', mine['greatest count at each r'][:12], mine['neighbours'])
