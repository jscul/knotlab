"""Independent short physical replays, real source projections and return-word checks."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import random
import subprocess
import sys

import networkx as nx
from survey import OUT,ROOT,H,CAP,prior,fix,end,cycword,phase_rows,is_source,source


def restore(rows):
    return tuple(tuple(r) for r in rows)


def physical(stars,letters,law):
    """Rebuild early cohorts from physical distinctions; recover every sampled two-parent window."""
    fix.certify_source(stars,law)
    prev=stars
    windows={w[0]:w[0] for word in letters for w in phase_rows(word,1)}
    ids={(v,):v for v in windows}
    out=[]
    for size in (2,3,4):
        cut=end.from_stars(prev)
        if end.step(cut,law,max_births=CAP).status=='cap':
            break
        _,births,_=fix.literal_turn(prev,law)
        by={frozenset(b.parents):b.knot for b in births if len(b.parents)==2}
        nxt={}
        for word in letters:
            for w in set(phase_rows(word,size)):
                ps=frozenset((ids[w[1:]],ids[w[:-1]]))
                assert len(ps)==2 and ps in by
                nxt[w]=by[ps]
        prev=prev+tuple(b.support for b in births)
        ids=nxt
        loose=end.from_stars(prev).opens
        assert sorted(loose)==sorted(b.knot for b in births)
        assert len(set().union(*(set(b.support) for b in births))) == sum(len(b.support) for b in births)
        out.append({'size':size,'physical_births':len(births),'distinct_phase_prefixes':len(set(nxt.values())),
                    'knots':len(prev),'distinctions':len(set().union(*map(set,prev)))})
    return out


def certificate(r):
    widths={}
    proofs=[]
    for part in r['laws']['parity']['parts']:
        if not part['positive']: continue
        assert part['structural_candidates'][0]['age']==0
        cert=part['periodic_packets']
        for v in cert: widths[tuple(v['word'])]=(v['age'],v['width'])
        # First proof uses the shortest launch with one private marker, printed as an entire invariant orbit.
        p=cert[0]
        a,b=tuple(p['a']),tuple(p['b'])
        marks=set(p['marker_orbit'])
        assert marks<=set(a+b) and marks.intersection(set(b)-set(a))
        for k in (1,2,3,4):
            w=a*k+b
            assert all(is_source(x,marks) for x in phase_rows(w,2*len(w)-1))
            assert all(not is_source(x,marks) for x in phase_rows(w,2*len(w)))
        proofs.append({'a':a,'b':b,'marker_orbit':sorted(marks),'period_family':'k*len(a)+len(b) for k>=1',
                       'widths_for_k_1_to_4':[len(a)*k+len(b) for k in (1,2,3,4)],'checked_return_phases':sum(2*(len(a)*k+len(b)) for k in (1,2,3,4))})
    words=[tuple(x['word']) for p in r['laws']['parity']['parts'] for x in p['periodic_packets']]
    assert words
    stars=fix.source_from(r['edges'],r['loose'])
    early={law:physical(stars,words,law) for law in ('parity','nae')}
    # Independently permute both sorts. A numerical tie-breaker may not change the returned set.
    rng=random.Random(20261120317)
    names=list(range(r['distinctions']));rng.shuffle(names)
    renamed_stars=tuple(tuple(names[d] for d in star) for star in stars)
    for law in ('parity','nae'):
        assert physical(renamed_stars,words,law)==early[law]
    perm=list(range(r['n']));rng.shuffle(perm)
    if 'supply' in r:
        permuted=dict(r);permuted['edges']=sorted(tuple(sorted((perm[u],perm[v]))) for u,v in r['edges'])
        permuted['coins']=[0]*r['n']
        for v,b in enumerate(r['coins']): permuted['coins'][perm[v]]=b
        again=source(permuted)
        target={cycword(tuple(perm[v] for v in w)) for w in words}
        recovered={tuple(x['word']) for p in again['laws']['parity']['parts'] for x in p['periodic_packets']}
        assert target==recovered
    widths=Counter((a,w) for a,w in widths.values())
    return {'n':r['n'],'distinctions':r['distinctions'],'ordinary_meetings':len(r['edges']),
            'holders':stars,'meeting_pairs':r['edges'],'loose':r['loose'],'returns':proofs,
            'width_tally':[{'age':a,'width':w,'families':v} for (a,w),v in sorted(widths.items())],
            'physical_replay':early,'renaming_checked':True}


def verify_nineteen():
    # Both ordinary cycles meet only at 0. Break the two orientation ties by the loose supply.
    g=nx.Graph()
    cycles=[[0]+list(range(1,8)),[0]+list(range(8,19))]
    for c in cycles:g.add_edges_from(zip(c,c[1:]+c[:1]))
    n=len(g)
    row={'size_group':'built','draw':0,'n':n,'word':None,'coins':[int(i in (1,8)) for i in range(n)],
         'extra':2,'extra_meetings':None,'edges':sorted(tuple(sorted(p)) for p in g.edges),'supply':'funded_sensitivity'}
    r=source(row)
    proof=certificate(r)
    assert len(r['edges'])==n+1 and not len(r['edges'])-len(set(r['edges']))
    assert [(x['age'],x['width']) for x in proof['width_tally']]==[(19,10),(27,14)]
    return proof


def main():
    rows=[json.loads(l) for l in (OUT/'draws.jsonl').read_text().splitlines()]
    pos=[]
    for r in rows:
        if any(p['positive'] for p in r['laws']['parity']['parts']):
            proof=certificate(r)
            pos.append({'stratum':r['size_group'],'extra':r['extra'],'supply':r['supply'],'draw':r['draw'],
                        'prufer':r['word'],'coins':r['coins'],'added':r['extra_meetings'],**proof})
    pos.sort(key=lambda p:(p['n'],p['distinctions'],p['draw']))
    historical=next((ROOT/'artifacts/FOUR-READINGS-20261120-001D').rglob('draws.jsonl'))
    counts={}
    for l in historical.open():
        r=json.loads(l)
        for law,x in r['laws'].items():
            key=law+'/'+r['weighting']
            n=x['certified_releases']
            assert n==sum(1 for p in x['parts'] for t in p['roots'] if t['certified_at'] is not None)
            counts[key]=counts.get(key,0)+n
    proof19=verify_nineteen()
    all_stars=[s for row in pos+[proof19] for s in row['holders']]
    arities=sorted(set(map(len,all_stars)))
    # Every source support was projected above; separately run the canonical CLI on the local law types.
    env=dict(__import__('os').environ,PYTHONPATH=str(ROOT/'tools'))
    canonical=[]
    for width in arities:
        names=['x'+str(i) for i in range(width)]
        for law in ('parity','nae'):
            forbid=[w for w in range(1<<width) if w.bit_count()%2] if law=='parity' else [0,(1<<width)-1]
            cnf=';'.join(' '.join(('~' if w>>i&1 else '')+x for i,x in enumerate(names)) for w in forbid)
            v=json.loads(subprocess.check_output([sys.executable,'-B','-m','knotlab','check','--cnf',cnf,
                        '--loops',*names[:-1],'--contact',names[-1],'--json'],env=env))
            assert v['is_knot'];canonical.append({'law':law,'arity':width,'is_knot':v['is_knot']})
    out={'proved_draws':pos,'nineteen':proof19,'previous_draws_sha256':hashlib.sha256(historical.read_bytes()).hexdigest(),
         'previous_tip_family_totals':counts,'canonical_relation_types':canonical}
    (OUT/'certificates.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
