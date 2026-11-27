"""Check every retained starting description, stored round, flag and first differing round."""
from collections import Counter, defaultdict
from itertools import combinations
import argparse
import json
import resource
import time

from fresh import HERE, late, view

STUDY = HERE.parent


def load(name):
    with (STUDY / f'{name}.jsonl').open() as stream:
        return [json.loads(line) for line in stream]


def independent(stars, m):
    holders = defaultdict(list)
    for k, places in enumerate(stars):
        for d in places:
            holders[d].append(k)
    adj = [set() for _ in stars]
    for pair in holders.values():
        if len(pair) == 2:
            a, b = pair
            adj[a].add(b)
            adj[b].add(a)
    blocks = {frozenset(a & m.live) for a in adj if len(a & m.live) >= 2}
    kept = [s for s in blocks if not any(s < t for t in blocks) and not any(s <= t for t in m.cells)]
    two_cells = any(len(a & b) >= 2 for a, b in combinations(m.cells, 2))
    two_blocks = any(len(a & b) >= 2 for a, b in combinations(kept, 2))
    route = two_cells or any(len(a & b & g) >= 2 for a, b in combinations(kept, 2) for g in m.cells)
    proper_split = rank_split = cover_diffs = False
    for ids, _, _ in m.pieces:
        valid = {}
        # Build connected subsets by adding one member. This lists disconnected-by-removal
        # group cells too: intermediate subsets used for enumeration need not themselves be valid.
        front = {frozenset([v]) for v in ids}
        while front:
            nxt = set()
            for s in front:
                if s & m.live and all(len(s & g) <= 1 or g <= s for g in m.cells):
                    valid[s] = len(s)-1-sum(len(g)-2 for g in m.cells if g <= s)
                for v in set.union(*(m.adj[x] for x in s))-s:
                    nxt.add(s | {v})
            front = nxt
        rank_parents, order_parents = {}, {}
        for s, rank in valid.items():
            subs = [t for t in valid if t < s]
            actual = set()
            for t in sorted(subs, key=len, reverse=True):
                if not any(t < bigger for bigger in actual):
                    actual.add(t)
            by_rank = {t for t in subs if valid[t] == rank-1}
            cover_diffs |= by_rank != actual
            for parents, here, flag in [(rank_parents, by_rank, 'rank'), (order_parents, actual, 'actual')]:
                parents[s] = here
                if rank >= 2 and any(not parents[a] & parents[b] for a,b in combinations(here, 2)):
                    if flag == 'rank':
                        rank_split = True
                    else:
                        proper_split = True
    return (route, rank_split, two_cells), (two_blocks, proper_split, cover_diffs)


def audit(limit):
    stats = Counter()
    flags_seen = {}
    for src in ['fresh7_treeplus', 'fresh7_grow', 'replays']:
        seeds = load(src)
        for law in ['nae', 'parity']:
            name = f'{src}_{law}'
            grown, scored = load('grown_'+name), load('scored_'+name)
            assert len(seeds) == len(grown) == len(scored)
            for seed, g, score in list(zip(seeds, grown, scored))[:limit]:
                assert all(g[k]==v for k,v in seed.items())
                assert score['draw']==seed.get('draw') and score['name']==seed.get('name')
                assert score['weighting']==seed.get('weighting') and score['law']==g['knot law']==law
                assert score['end']==g['end'] and score['rounds read']==len(g['rows'])
                m = late.Map(g['stars'], law)
                assert all(tree for _, tree, _ in m.pieces) and m.cls=='in'
                assert score['stratum']==m.stratum and score['pendant points']==len(m.chains)
                key = tuple(map(tuple, g['stars']))
                if key not in flags_seen:
                    flags_seen[key] = independent(g['stars'], m)
                flags, (two_blocks, proper_split, cover_diffs) = flags_seen[key]
                for obj in [score] + ([seed] if src != 'replays' else []):
                    assert tuple(obj[k] for k in ['route cycle','split pair','cells share two'])==flags
                p, why = late.predict(g['stars'], 24, law, general=True)
                assert p is not None, why
                rows = list(g['rows'])
                if g['end'].startswith('closes'):
                    rows += [{'n':0,'sig0':[],'sig1':[]}]*(24-len(rows))
                first = []
                for reading in ('sig0','sig1'):
                    diffs = []
                    for t,(a,b) in enumerate(zip(p,rows),1):
                        aa, bb = view(a,reading), view(b,reading)
                        assert sum(aa.values())==a['n'] and sum(bb.values())==b['n']
                        if aa != bb: diffs.append(t)
                    first.append(diffs[0] if diffs else None)
                assert (min(t for t in first if t) if any(first) else None) == score['first differing round']
                out = dict(source=src, law=law, sample=score['draw'] if src!='replays' else score['name'],
                           route=flags[0], split=flags[1], cells=flags[2], literal_split=proper_split,
                           covers_differ=cover_diffs, blocks_share_two=two_blocks, chains=sum(m.chains.values()),
                           attachments=len(m.chains), end=g['end'], observed=len(g['rows']), compares=len(rows),
                           first=first, sizes=[len(k) for k in g['stars']])
                print(json.dumps(out,sort_keys=True),flush=True)
                stats[(src,law)] += 1
    return stats


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--per-file',type=int)
    resource.setrlimit(resource.RLIMIT_AS,(3 << 30,3 << 30))
    start = time.monotonic()
    stats = audit(args.parse_args().per_file)
    print(dict(stats),f'{time.monotonic()-start:.3f} seconds',file=__import__('sys').stderr)
