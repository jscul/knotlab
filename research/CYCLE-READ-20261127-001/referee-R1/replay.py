"""Reconcile stored starts, complete growth multisets, twin buckets, and count limits."""
import argparse
from collections import Counter, defaultdict
from dataclasses import replace
import gzip
from itertools import combinations
import json
from pathlib import Path
import resource
import time

from core import build_core
from reader import predict_core

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('cyc6_uniform', 'cyc7_treeplus', 'cyc7_grow', 'twin9', 'twin8')


def lines(name):
    path = ROOT / name
    op = gzip.open if name.endswith('.gz') else open
    with op(path, 'rt') as f:
        return [json.loads(line) for line in f if line.startswith('{')]


def oldest_twin(piece, first):
    """Any twin, including those without chains, independently of the chain flag."""
    for rank, nodes in piece.ranks.items():
        if rank < first:
            continue
        pairs = set()
        for v in nodes:
            parents = piece.nodes[v].parents
            if len(parents) < 3:
                continue
            for pair in combinations(sorted(parents), 2):
                if pair in pairs:
                    return rank - 1
                pairs.add(pair)
    return None


def boundary(piece, finite_rank):
    """Recover active guards from realised ranks, without enumerating all maximal families.

    Every maximal pairwise family is either an actual group of size >=3, a
    maximal common-parent roster that admits no additional member, or an
    isolated singleton. Isolated singletons also belong to the roster count.
    """
    count = len(piece.ranks[1])
    peak_pairs = 0
    for rank, nodes in piece.ranks.items():
        if rank == 1:
            continue
        count += len(nodes)
        if count > 5000:
            return 'nodes', rank-1
        if rank > finite_rank:
            break
        rosters = defaultdict(int)
        for i, v in enumerate(nodes):
            for p in piece.nodes[v].parents:
                rosters[p] |= 1 << i
        pairs = sum(r.bit_count() * (r.bit_count()-1)//2 for r in rosters.values())
        peak_pairs = max(pairs, peak_pairs)
        if pairs > 250000:
            return 'parent-pair incidences', rank-1
        next_rank = piece.ranks.get(rank + 1, ())
        if not next_rank and not piece.finished:
            return piece.stop, rank-1
        common = set(rosters.values())
        neighbours = [0] * len(nodes)
        for block in common:
            bits = block
            while bits:
                marked = bits & -bits
                neighbours[marked.bit_length()-1] |= block
                bits -= marked
        meaningful = sum(len(piece.nodes[n].parents)>=3 for n in next_rank)
        maximal_common = 0
        for block in common:
            possibles = (1 << len(nodes))-1
            bits = block
            while bits and possibles != block:
                marked = bits & -bits
                possibles &= neighbours[marked.bit_length()-1]
                bits -= marked
            maximal_common += int(possibles == block)
        if meaningful + maximal_common > 5000-count:
            return 'maximal families', rank-1
    return ('finished' if piece.finished and max(piece.ranks)<=finite_rank else 'rank limit',
            peak_pairs)


def score(g, rows):
    if g['end'].startswith('stalls'):
        return 'stalls'
    for i, actual in enumerate(g['rows']):
        if rows[i] != actual:
            return i+1
    if g['end'].startswith('closes'):
        for i in range(len(g['rows']), 24):
            if rows[i]['n']:
                return i+1
    return 'agrees'


def replay(group, idx, x, data, strata):
    stars = x['stars']
    cycle = group.startswith('cyc')
    max_rank = 26 if cycle else 130
    c = build_core(stars, max_rank=max_rank, group_work=5_000_000)
    boundaries = [boundary(p, max_rank - 1) for p in c.pieces]
    cap = any(why not in ('finished','rank limit') for why, _ in boundaries)
    pcs = [dict(cycle=p.cycle, chains=sum(p.chains.values()), core=b[0], detail=b[1],
                nodes=len(p.nodes), raw_stop=p.stop, size=max(p.ranks))
           for p,b in zip(c.pieces,boundaries)]
    twin = min((p.twin_rank-1 for p in c.pieces if p.twin), default=None)
    ordinary = min((t for p in c.pieces if (t:=oldest_twin(p, 3)) is not None), default=None)
    first_round = any(oldest_twin(p, 2)==1 for p in c.pieces) if not cap else None
    bucket = 'twins, chained' if twin is not None else 'twins, not chained' if ordinary else 'no twins'
    key = x.get('draw',x.get('index'))
    row = dict(group=group, line=idx+1, key=key, pcs=pcs, twin=twin, bucket=bucket, first_round_twins=first_round)
    errs = []
    if cycle:
        orig = strata[group+'.jsonl',idx+1]
        if orig['draw']!=key:
            errs.append('stratum identity')
        want = [{'cycle by count':p['cycle'], 'chains':p['chains'], 'core':
                'finishes' if p['core']=='finished' else 'does not finish by rank 25' if p['core']=='rank limit'
                else 'unending (over the cap)'} for p in pcs]
        if want != orig['pieces']:
            errs.append('stratum pieces')
        if not cap and bucket != orig['twins']:
            errs.append('stratum twin')
        if cap != orig['twins'].startswith('twins not read'):
            errs.append('stratum cap')
    else:
        expected_bucket = bucket
        if twin is None:
            expected_bucket += ', with chains' if any(p.chains for p in c.pieces) else ', no chains'
        if expected_bucket != x['twins']:
            errs.append('draw bucket')

    for law,(growth,nodes,scores) in data.items():
        g,n,s = growth[idx],nodes[idx],scores[key]
        if g['stars']!=stars or g.get('draw',g.get('index'))!=key or n['law']!=law:
            raise AssertionError('start identity')
        if n.get('draw') is not None and n['draw']!=key:
            raise AssertionError('node identity')
        original = s['verdict']
        if original=='differs' or original.startswith('differs from round'):
            original = s.get('first differing round') or int(original.split()[-1])
        elif original.startswith('not predicted:'):
            original = 'excluded'
        if g['end']=='not run (time limit)':
            actual = 'growth not run'
        elif cap:
            actual = 'excluded'
        else:
            read, why = predict_core(c, 24, law)
            actual = score(g,read) if read is not None else 'excluded'
        if actual != original:
            errs.append(law+' score')
        if cycle:
            if s['file']!=group+'.jsonl' or s['line']!=idx+1 or s['twins']!=orig['twins']:
                errs.append('score key')
        elif 'least rank of chained twins' in s and not cap and s['least rank of chained twins']!=twin:
            errs.append('twin rank')
        if 'rounds read' in n and (n['rounds read']!=len(g['rows']) or s['rounds read']!=len(g['rows'])):
            errs.append('growth length')
        raw = 'growth not run' if g['end']=='not run (time limit)' else 'excluded' if ('error' in n or isinstance(n['node reading'],str)) else n['node reading'] or 'agrees'
        if raw != original:
            errs.append(law+' stored raw score')
        row[law]=dict(actual=actual, stored=original, rounds=len(g['rows']), end=g['end'])
    row['errors']=errs
    return row


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--first', type=int, default=0)
    ap.add_argument('--count', type=int, default=10000)
    args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2200<<20,2200<<20))
    strata={(s['file'],s['line']):s for s in lines('strata.txt')}
    for group in GROUPS:
        cycle=group.startswith('cyc')
        starts=lines(group+('.jsonl' if cycle else '_draw.jsonl'))
        s=lines('scores.jsonl' if cycle else 'scores2.jsonl')
        s=[a for a in s if (a['file']==group+'.jsonl' if cycle else ('nine knots' in a['weighting'])==(group=='twin9'))]
        data={}
        for law in ('nae','parity'):
            g=lines(f'grown_{group}_{law}.jsonl.gz')
            n=lines(f'nodes_{group}_{law}.jsonl')
            scores={a['draw']:a for a in s if a['law']==law}
            assert len(starts)==len(g)==len(n)==len(scores)
            data[law]=g,n,scores
        for idx in range(args.first,min(len(starts),args.first+args.count)):
            t=time.perf_counter()
            row=replay(group,idx,starts[idx],data,strata)
            row['seconds']=round(time.perf_counter()-t,5)
            print(json.dumps(row),flush=True)

if __name__=='__main__':
    main()
