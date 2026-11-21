"""Named physical founder deletions, actual sign changes and local knot checks."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json
import os
import subprocess
import sys

from catalog import PAIRS, RENAMINGS, ROOT, is_connected, renumber_flags, renumber_pairs
from source_mechanisms import initial_read, named_phys, positive_grant_control
from panels_certificates import scalar


def check_local(arity, law):
    variables=['x'+str(i) for i in range(arity)]
    words=tuple(product((0,1),repeat=arity))
    forbidden = [w for w in words if sum(w)%2] if law=='parity' else [w for w in words if len(set(w))==1]
    clauses = [' '.join('~'+name if bit else name for name,bit in zip(variables,w,strict=True)) for w in forbidden]
    cmd=[sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),'--loops',
         *variables[:-1],'--contact',variables[-1],'--json']
    proc=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':'tools'},check=True,capture_output=True,text=True)
    data=json.loads(proc.stdout)
    assert data['is_knot'] and len(data['allowed'])==len(words)-len(forbidden)
    assert set(data['allowed']) == {''.join(map(str,w)) for w in set(words)-set(forbidden)}
    return data


def deletions(edges, flags):
    sym=[p for p in RENAMINGS if renumber_pairs(edges,p)==edges and renumber_flags(flags,p)==flags]
    possible={e for e in edges if is_connected(tuple(v for v in edges if v!=e))}
    while possible:
        choice=min(possible)
        orbit={tuple(sorted((p[choice[0]],p[choice[1]]))) for p in sym}
        assert orbit<=possible
        possible-=orbit
        yield choice,sorted(orbit)


def named_control(typ):
    edges = tuple(map(tuple,typ['edges']))
    flags = tuple(typ['flags'])
    degree = Counter(i for e in edges for i in e)
    private = [max(0,3-degree[h])+flags[h] for h in range(6)]
    founder=named_phys(6,edges,flags,private)
    deletion=[]
    for cut, orbit in deletions(edges,flags):
        one=tuple(e for e in edges if e!=cut)
        lower=Counter(i for e in one for i in e)
        required=[max(0,3-lower[h]) for h in range(6)]
        same_flags=[a+b for a,b in zip(required,flags,strict=True)]
        felt=[a-b for a,b in zip(private,required,strict=True)]
        invalid=[h for h in range(6) if private[h]+lower[h]<3]
        cell={'deleted':cut,'equivalent_deletions':orbit,'fixed_flags':named_phys(6,one,flags,same_flags),
              'fixed_supply_flags':felt,'fixed_supply_too_few_places':invalid}
        if not invalid:
            assert all(v in (0,1) for v in felt)
            cell['fixed_supply']=named_phys(6,one,felt,private)
        deletion.append(cell)
    result={'edges':edges,'flags':flags,'founder':founder,'one_meeting_comparisons':deletion}
    result['positive_fresh_sign_control']=positive_grant_control(result)
    return result


def ending_words(founder):
    history=founder['laws']['parity']
    cuts=history['cuts']
    assert history['termination']=='closed' and len(cuts)<=4
    before=tuple(map(tuple,founder['source_rows']))
    for cut in cuts[:-1]:
        before+=tuple(tuple(b['support']) for b in cut['births'])
    closing,=cuts[-1]['births']
    after=before+(tuple(closing['support']),)
    using=Counter(x for row in before for x in row)
    assert set(closing['inputs'])=={h for h,v in using.items() if v==1}
    old=scalar(before,tuple(range(len(before))))
    even=scalar(after,tuple(range(len(after))))
    odd=scalar(after,tuple(range(len(after))),(len(before),))
    assert old['words']==even['words']>0 and odd['words']==0
    assert sorted(closing['old_span_rows'])==list(range(len(before)))
    return {'preceding_rows':before,'closing':closing,'old_even':old,'ordinary_even':even,'supplied_odd':odd}
