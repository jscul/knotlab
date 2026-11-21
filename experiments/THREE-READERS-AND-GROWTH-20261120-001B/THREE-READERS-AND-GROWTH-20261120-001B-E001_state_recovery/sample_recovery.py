"""Frozen fresh panels. Check physical gates, NAE repair certificates, parity rivals."""
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from random import Random
import sys

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
OLD = 'READS-HOLDERS-SOURCES-20261120-001B'
sys.path.insert(0,str(ROOT / 'experiments' / OLD / (OLD + '-E001_irredundant')))
from controls import allowed, deletions, explosive_source, interval, lawful, next_stage, tree_source, unique_private
from certificates import preserved_class
from census_verify import covers, exact_candidates, indices, to_mask
from model import mask_of, ownership, reduced, width


def one_word_for_each_target(rows):
    out = []
    for target in rows:
        h = set(target)
        clauses = []
        for other in rows:
            if other is target:
                continue
            k = set(other)
            unpinned = [i+1 for i in sorted(k-h)]
            # The target is all zero. Each other rule must then hold and stay
            # true following any flip in the target.
            clauses.append(unpinned)
            if len(h & k) <= 1:
                clauses.append([-j for j in unpinned])
        with Solver(name='g3',bootstrap_with=clauses) as solver:
            if not solver.solve():
                out.append(None)
            else:
                word = mask_of(j-1 for j in (solver.get_model() or []) if j>0 and j-1 not in h)
                for i in range(width(rows)):
                    repaired=word ^ (1<<i)
                    if i in h:
                        for row in rows:
                            m=mask_of(row)
                            assert (repaired&m) not in (0,m)
                    else:
                        assert repaired & mask_of(h) == 0
                out.append(format(word,'x'))
    return out


def parity_alternative(rows):
    owners=ownership(rows)
    loose=tuple(sorted(x for x,who in owners.items() if len(who)==1))
    if len(loose)<3 or len(rows)==1:
        return None
    rival=(loose,*rows[1:])
    if set(map(frozenset,rows)) == set(map(frozenset,rival)):
        return None
    assert reduced(map(mask_of,rival)) == reduced(map(mask_of,rows))
    assert lawful(rival,'parity') and all(deletions(rival,'parity')[0])
    assert max(map(len,ownership(rival).values()))<=2
    done={0}
    while True:
        reached = {k for k,r in enumerate(rival) if any(set(r)&set(rival[i]) for i in done)}
        if reached <= done:
            break
        done|=reached
    assert len(done)==len(rival)
    return {'replaces_holder':0,'replacement':loose}


def stage(rows,law):
    v=lawful(rows,law)
    global_,local=deletions(rows,law)
    assert global_==local
    data={'lawful':v,'essential':all(global_),'names':width(rows),'holders':len(rows)}
    if not v or not all(global_):
        data['verdict']='ineligible'
        return data
    counts=Counter(i for r in rows for i in r)
    data['loose']=sum(q==1 for q in counts.values())
    if law=='nae':
        data['previous_preserved_class']=preserved_class(rows)
        data['private_at_each_holder']=unique_private(rows)
        data['simple_meetings']=all(len(set(a)&set(b))<=1 for a,b in combinations(rows,2))
        certs=one_word_for_each_target(rows)
        data['repair_witnesses_hex']=certs
        data['all_one_word']=all(w is not None for w in certs)
        data['earlier_tests_certify'] = data['all_one_word'] or data['private_at_each_holder'] or data['previous_preserved_class']
        is_six_exception = (len(rows)==4 and width(rows)==6 and data['loose']==0 and data['simple_meetings'])
        data['all_size_classification'] = not is_six_exception
        data['verdict'] = 'different' if is_six_exception else 'unique'
        assert not data['earlier_tests_certify'] or data['all_size_classification']
    else:
        rival=parity_alternative(rows)
        data['alternative']=rival
        if rival is not None:
            data['verdict']='different'
        elif len(rows)==1:
            data['verdict']='unique'
        elif width(rows)<=10:
            n=width(rows)
            words=allowed(rows,'parity')
            family=exact_candidates(n,words,'parity')
            excluded=((1<<(1<<n))-1) ^ to_mask(words)
            rosters=set(covers(n,family,excluded))
            actual=tuple(sorted(mask_of(row) for row in rows))
            assert actual in rosters
            data['exact_cover_count']=len(rosters)
            data['verdict']='unique' if len(rosters)==1 else 'different'
            if len(rosters)>1:
                other=min(rosters-{actual})
                data['alternative']={'full_rows':[list(indices(h)) for h in other]}
        else:
            data['verdict']='undecided'
    return data


def main():
    rng=Random(20261120473)
    panels,summary={},{}
    for panel in ('tree','supplemented','explosive'):
        draws=[]
        for q in range(128):
            seed=explosive_source(rng) if panel=='explosive' else tree_source(rng,panel=='supplemented')
            draw={'draw':q+1,'physical_start':seed}
            for law in ('nae','parity'):
                funding,next_rows,births=next_stage(seed,law)
                item={'source':stage(seed,law),'funding':funding,'births':len(births)}
                if funding=='births':
                    item['first_grown']=stage(next_rows,law)
                draw[law]=item
            draws.append(draw)
        panels[panel]=draws
        summary[panel]={}
        for law in ('nae','parity'):
            group={'funding':dict(Counter(d[law]['funding'] for d in draws))}
            for when in ('source','first_grown'):
                obs=[d[law][when] for d in draws if when in d[law]]
                verdict=Counter(s['verdict'] for s in obs)
                n=sum(s['lawful'] and s['essential'] for s in obs)
                group[when]={'observed':len(obs),'lawful':sum(s['lawful'] for s in obs),'essential_and_lawful':n,'by_verdict':dict(verdict),'interval_unique':interval(verdict['unique'],n),'positive_by_test':{t:sum(s.get(t,False) for s in obs) for t in ['private_at_each_holder','previous_preserved_class','all_one_word','simple_meetings','earlier_tests_certify','all_size_classification']}}
            summary[panel][law]=group
    (OUT/'sample_recovery.json').write_text(json.dumps({'seed':20261120473,'panels':panels,'summary':summary},separators=(',',':'))+'\n')
    print(json.dumps(summary))


if __name__=='__main__':
    main()
