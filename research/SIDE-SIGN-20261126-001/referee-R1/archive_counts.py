"""Retally archived outcomes; count each physically different setting pair once per named reader and lift row."""
import ast
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import islice
import json
from math import comb
from pathlib import Path
import sys
from table_rebuild import HERE, GROWTH, forbid

STUDY = HERE.parent


def aggregate(limit=None):
    starts = json.loads((GROWTH / 'starts.json').read_text())
    archived_samples = json.loads((STUDY / 'census_hits.json').read_text())
    requests = defaultdict(set)
    for key, hits in archived_samples.items():
        for start, rd, kind, lift, side_sizes, h in hits:
            requests[(start, ast.literal_eval(key), lift, kind)].add((tuple(h[0]), tuple(h[1]), h[2]))
    results = defaultdict(Counter)
    best, stages, by_score = {}, defaultdict(set), defaultdict(Counter)
    stages_info, paired = Counter(), Counter()
    conflict = []
    with gzip.open(STUDY / 'census_results.jsonl.gz', 'rt') as archive:
        for batch in islice(archive, limit):
            batch = json.loads(batch)
            assert batch['status'] == 'ok'
            stages_info['batches'] += 1
            for r in batch['result']['rows']:
                start, law, rd = r['start'], r['law'], r['round']
                stages_info[f'{law}.{rd}.stage'] += 1
                if isinstance(r['classes'], str):
                    stages_info[f'{law}.{rd}.skipped'] += 1
                    continue
                rows = None
                lift_hits = defaultdict(dict)
                for c in r['classes']:
                    correction = 0
                    if c['kind'] == 'two':
                        if rows is None:
                            rows = forbid.supports_of(starts[start])
                            for i in range(rd):
                                rows, status, _ = forbid.grown(rows, law, 'ordinary')
                                assert status == 'funded'
                            holders = forbid.holders(rows)
                        p = c['perm']
                        moved = {i for i, j in enumerate(p) if i != j}
                        # An internal shared distinction is repeated by the study's candidate list.
                        # Rebuild both components using its minimal or maximal distinction lift.
                        partners = defaultdict(list)
                        for d, hs in holders.items():
                            partners[tuple(sorted(hs))].append(d)
                        adj = {i: set() for i in moved}
                        for (a, *tail), ds in partners.items():
                            if not tail:
                                continue
                            b = tail[0]
                            if a in moved and b in moved and (p[a] != b or c['lift']=='max' and len(ds)>1):
                                adj[a].add(b)
                                adj[b].add(a)
                        side = {min(moved)}
                        todo = list(side)
                        while todo:
                            for b in adj[todo.pop()] - side:
                                side.add(b)
                                todo.append(b)
                        other = moved - side
                        counts = [sum(set(hs)<=s for hs in holders.values()) for s in (side, other)]
                        original = [sum(len(hs) for hs in holders.values() if set(hs)<=s) for s in (side, other)]
                        assert sorted(original) == sorted(c['readers'])
                        correction = comb(original[0],2)*comb(original[1],2) - comb(counts[0],2)*comb(counts[1],2)
                    for nm,w in c['weightings'].items():
                        for reading in ('R1','R2'):
                            row = w[reading]; key=(law,rd,nm,reading)
                            a=results[key]
                            a['rows']+=1
                            a['zero signed total']+=w['Z']==0
                            for gate in ('placements','G0','G1','G2','G3'):
                                a[gate]+=row[gate]
                            a['physical placements']+=row['placements']-correction
                            hs={(tuple(h[0]),tuple(h[1]),h[2]) for h in row['hits']}
                            assert all(x!=y and v!=z for (x,y),(v,z),s in hs)
                            a['raw hits']+=len(row['hits'])
                            a['physical hits']+=len(hs)
                            if hs:
                                stages[key].add(start)
                                by_score[key].update(h[2] for h in hs)
                                k=(start,key,c['lift'],c['kind'])
                                if k in requests:
                                    requests[k]-=hs
                            for h in row['hits']:
                                if len(h)>3:
                                    a['annotated']+=1
                                    a['annotated four-name constant']+=h[3]['sign on the reads only']
                            if row['best'] is not None:
                                best[key]=max(best.get(key,0),Fraction(row['best']))
                            if nm=='W1' and reading=='R1' and law=='parity':
                                lift_hits[tuple(c['perm'])][c['lift']]=bool(hs)
                            if nm=='W1c' and c['weightings']['W1'][reading]['hits']:
                                other_hits={(tuple(h[0]),tuple(h[1])) for h in c['weightings']['W1'][reading]['hits']}
                                if {(h[0],h[1]) for h in hs}!=other_hits:
                                    conflict.append([start,law,rd,c['lift'],reading])
                for flags in lift_hits.values():
                    if len(flags)==2 and any(flags.values()):
                        paired['both' if all(flags.values()) else 'one']+=1
    out = dict(archive=dict(stages_info),sample_records=sum(map(len,archived_samples.values())),
               sample_keys_unmatched=sum(map(len,requests.values())),two_lifts_with_hit=dict(paired),
               W1c_difference=conflict,totals={})
    for k,a in sorted(results.items()):
        a['starts with hit']=len(stages[k])
        out['totals']['/'.join(map(str,k))]=dict(**a,best=str(best[k]) if k in best else None,
                                                   physical_hit_scores=dict(by_score[k]))
    if limit is None:
        mismatches=[]
        seen=set()
        for line in (STUDY/'census_tally.md').read_text().splitlines():
            if not line.startswith(('| parity |','| nae |')): continue
            cells=[v.strip().replace(',','') for v in line.strip('|').split('|')]
            key='/'.join(cells[:4]); seen.add(key)
            rec=out['totals'][key]
            actual=[str(rec[k]) for k in ('rows','zero signed total','placements','G0','G1','G2','G3')]
            actual.extend([rec['best'] or '—',str(rec['raw hits'])])
            if actual!=cells[4:]:mismatches.append(key)
        assert seen==set(out['totals'])
        out['published aggregate rows compared']=len(seen)
        out['published aggregate rows differing']=mismatches
    return out


if __name__=='__main__':
    out=aggregate(int(sys.argv[1]) if len(sys.argv)>1 else None)
    print(json.dumps(out,indent=1))
