"""Independent finite-relation controls for the pinning predicates."""
from __future__ import annotations
from itertools import combinations
import time
import checks
import top_data as data


def direct(rows, V, X):
    labels = tuple(V)+tuple(X)
    def image(support):
        return {tuple(row >> x & 1 for x in support) for row in rows}
    def full(support):
        return len(image(support)) == 1 << len(support)
    plain = len(image(labels)) != len(image(V))*len(image(X))
    cross = False
    for n in range(2,len(labels)+1):
        for support in combinations(labels,n):
            if not set(support)&set(V) or not set(support)&set(X) or full(support):
                continue
            if all(full(support[:j]+support[j+1:]) for j in range(n)):
                cross = True
    return plain,cross


def run():
    started = time.monotonic()
    fixtures=[]
    # Advisor's relation: bit positions p,q,r,t,x; excluded 0011,x=1 and complement.
    rows=[v for v in range(32) if v&15 not in (0,15) and v not in (28,3)]
    fixtures.append(('advisor_hiding',rows,(0,1,2,3),(4,),(True,False)))
    fixtures.append(('full',list(range(8)),(0,1),(2,),(False,False)))
    fixtures.append(('opposite_pair',[1,2],(0,),(1,),(True,True)))
    fixtures.append(('NAE3',list(range(1,7)),(0,1),(2,),(True,True)))
    checked=[]
    for name,rows,V,X,expected in fixtures:
        proj=dict(labels=list(range(len(V)+len(X))),allowed=rows,root_labels=list(V),own_labels=list(X))
        observed=checks.projection_flags(proj)
        actual=(observed['plain_pinned'],observed['bond_pinned'])
        independent=direct(rows,V,X)
        if actual!=expected or actual!=independent:
            raise ValueError((name,actual,independent,expected))
        checked.append(dict(name=name,rows=len(rows),plain_pinned=actual[0],bond_pinned=actual[1]))
    count=0
    for mask in range(1,256):
        rows=[r for i in range(8) if mask>>i&1 for r in (i,i^15)]
        p=dict(labels=list(range(4)),allowed=rows,root_labels=[0,1],own_labels=[2,3])
        a=checks.projection_flags(p)
        if (a['plain_pinned'],a['bond_pinned'])!=direct(rows,(0,1),(2,3)):
            raise ValueError('exhaustive complement-closed control mismatch')
        count+=1
    result=dict(passed=True,fixtures=checked,independent_exhaustive_relations=count,
                independent_method='all minimal non-full supports and every one-variable deletion; no maximal-side shortcut',
                seconds=time.monotonic()-started)
    data.dump('controls.json',result)
    return result


if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
