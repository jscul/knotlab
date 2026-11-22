"""Verify the registered sibling test using per-parent completion counts."""
from collections import Counter
from fractions import Fraction
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LITERALS = tuple(product((0,1), repeat=3))


def word(bits):
    return ''.join(map(str,bits))


def allowed(law, values):
    return (sum(values)%2==0 if law=='parity' else len(set(values))>1)


def canonical(law):
    names=['i','j','k','l']
    bad=[v for v in product((0,1),repeat=4) if not allowed(law,v)]
    cnf=';'.join(' '.join(('~' if bit else '')+name for name,bit in zip(names,v,strict=True)) for v in bad)
    result=subprocess.check_output([sys.executable,'-B','-m','knotlab','check','--cnf',cnf,
                '--loops',*names[:-1],'--contact',names[-1],'--json'],text=True,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')})
    d=json.loads(result)
    assert d['binding'] and d['loss_on_erasure'] and d['coexistence'] and d['is_knot']
    assert set(d['allowed'])=={word(v) for v in product((0,1),repeat=4) if allowed(law,v)}
    return {k:d[k] for k in ('binding','loss_on_erasure','coexistence','is_knot','allowed')}


def verdict(law):
    donors=list(product((0,1),repeat=4))
    legal=[v for v in donors if allowed(law,v)]
    possible_paid={a:{u for u,receives,_,_ in legal if receives==a} for a in (0,1)}
    fresh={a:[x for x in LITERALS if allowed(law,(a,*x))] for a in (0,1)}
    k=len(fresh[0])
    assert k==len(fresh[1])
    cohort={group:{u:Counter() for u in (0,1)} for group in ('all','intact','interrupted')}
    kernel={}
    for u,a,b,c in legal:
        event=a==b==c
        image=(b==c and b!=a and allowed(law,(u,a,1-b,1-c)))
        assert not (event and image)
        groups=['all']+(['intact'] if event else [])+(['interrupted'] if image else [])
        for group in groups:
            rec=cohort[group][u]
            rec['founding_words']+=1
            for r in fresh[a]:
                # The focal bank and the other two sibling banks may each be independently completed.
                mass=k**3
                notice=len(set(r))==1
                rec['available']+=mass
                rec['marked_event']+=mass*event
                rec['correct_bit']+=mass*(notice and r[0]==u)
                rec['wrong_bit']+=mass*(notice and r[0]!=u)
                rec['silent']+=mass*(not notice)
                rec['false_event_indication']+=mass*(notice and not event)
                rec['true_event_indication']+=mass*(notice and event)
                rec['refused']+=0
                rec['locally_certain_bit']+=mass*(len(possible_paid[a])==1)
        for f in fresh[u]:
            for r in fresh[a]:
                # Same multiplicity per (u,a,b,c,full F,full A), without pairing the two other completions.
                kernel[(u,a,b,c,word(f),word(r))]=k**2

    pairs=[]
    for (u,a,b,c,f,r), total in kernel.items():
        if a==b==c:
            assert kernel[u,a,1-b,1-c,f,r]==total
            assert Fraction(total,k**3)==Fraction(1,k)
            pairs.append(total)
    joint={}
    for a in (0,1):
        by_u={u:sum(x[:2]==(u,a) for x in legal) for u in (0,1)}
        assert all(by_u.values())
        for r in fresh[a]:
            joint[str(a)+word(r)]={str(u):count*k**3 for u,count in by_u.items()}
    optimum=Fraction(sum(max(masses.values()) for masses in joint.values()),len(legal)*k**4)
    for grp in cohort.values():
        for row in grp.values():
            assert row['correct_bit']+row['wrong_bit']+row['silent']==row['available']
    for u in (0,1):
        p,q=cohort['intact'][u],cohort['interrupted'][u]
        assert p['available']==q['available']==k**4
        assert p['correct_bit']==q['correct_bit'] and p['silent']==q['silent']
        assert len(fresh[u])==k
    assert sum(pairs)==2*k**4
    assert all(allowed(law,tuple(1-i for i in v)) for v in legal)
    relation=canonical(law)
    assert set(joint)==set(relation['allowed'])=={word(v) for v in legal}
    return {'law':law,'source_label':'finite ordinary','canonical_local_law':relation,
            'founder_words':len(legal),'legal_fresh_given_paid':{str(a):list(map(word,x)) for a,x in fresh.items()},
            'cohorts_per_original_paid_value':{s:{str(u):dict(row) for u,row in grp.items()} for s,grp in cohort.items()},
            'matched_F_A_strata':len(pairs),'completions_per_stratum_per_arm':k**2,
            'paired_launches':sum(pairs),'all_launches':len(legal)*k**4,
            'full_A_by_u':joint,'best_bit_guess_full_A_all':str(optimum)}


if __name__=='__main__':
    out={law:verdict(law) for law in ('parity','nae')}
    (HERE/'independent_counts.json').write_text(json.dumps(out,indent=2)+'\n')
    for law,r in out.items():
        print(law,r['all_launches'],r['paired_launches'],r['matched_F_A_strata'],r['cohorts_per_original_paid_value']['all']['0'],r['best_bit_guess_full_A_all'])
