"""Exact marked pair costs of the finite family, quotienting only identical junctions."""
from itertools import product
from pathlib import Path
import json


def connected_shore(active, multiplicity, adjacency):
    """A type represents independent twins with identical neighbors."""
    if not active:
        return False
    if len(active) == 1:
        return multiplicity[next(iter(active))] == 1
    seen = {next(iter(active))}
    todo = list(seen)
    while todo:
        for other in adjacency[todo.pop()] & active - seen:
            seen.add(other)
            todo.append(other)
    return seen == active


def marked_pair(anchors, red_shields, blue_shields, test_weight, hub_weight, price, marks,
                *, test_anchor_weight=None, blue_price=None, blue_hub_weight=None):
    if test_anchor_weight is None:
        test_anchor_weight = test_weight
    if blue_price is None:
        blue_price = price
    if blue_hub_weight is None:
        blue_hub_weight = hub_weight
    # O is fixed on shore zero. Types include special v, weak anchor twins,
    # and separate colors for the two shield families. Each test middle is a singleton.
    counts = [1, 1, 1, 1, anchors-1, 1, 1, 1, 1, red_shields, blue_shields]
    names = ['O','h0','h1','v','weak','a','b','c','d','red','blue']
    adjacency = [set() for _ in names]
    weighted = []
    def add(u, v, weight):
        if weight:
            weighted.append((u, v, weight))
            adjacency[u].add(v)
            adjacency[v].add(u)
    for middle in range(5,11):
        test = middle <= 8
        red = middle in (5,6,9)
        spoke_cost = test_weight if test else (hub_weight if red else blue_hub_weight)
        add(middle,1 if red else 2,spoke_cost)
        add(middle,3,test_anchor_weight if test else 1)
        add(middle,4,1)
        if not test:
            add(middle,0,price if red else blue_price)
    best = None
    best_partition = None
    considered = 0
    for hub0,hub1,v in product(range(2), repeat=3):
        test_bits = [[1-(hub0 if j<2 else hub1)] if j in marks else [0,1] for j in range(4)]
        for test in product(*test_bits):
            for weak, red, blue in product(range(anchors),range(red_shields+1),range(blue_shields+1)):
                one = (0,hub0,hub1,v,weak,*test,red,blue)
                zero = tuple(n-i for n,i in zip(counts,one))
                value = sum(w*(one[u]*zero[vv] + zero[u]*one[vv]) for u,vv,w in weighted)
                considered += 1
                if best is not None and value>=best:
                    continue
                if all(connected_shore({i for i,n in enumerate(side) if n},side,adjacency)
                       for side in (zero,one)):
                    best=value
                    best_partition = {name:n for name,n in zip(names,one) if n}
    return dict(K=best,representative_shore=best_partition,assignments=considered)


def audit_unquotiented():
    # A small literal ordinary assignment independently checks the type calculation above.
    for anchors, s, left, hc, p in [(2,1,3,2,1),(2,2,2,3,2),(1,2,1,2,1)]:
        mids=4+2*s
        # O=0, hubs 1,2, ordinary anchors then middles
        first=3+anchors
        ends=[]
        spokes=[]
        for i in range(mids):
            w=first+i
            is_test=i<4
            color=0 if i<2 or (4<=i<4+s) else 1
            h=color+1
            if is_test:spokes.append((w,h))
            ends.extend([(w,h,left if is_test else hc),(w,3,left if is_test else 1)])
            ends.extend((w,j,1) for j in range(4,first))
            if not is_test:ends.append((w,0,p))
        n=first+mids
        adj=[0]*n
        for u,v,_ in ends:
            adj[u]|=1<<v;adj[v]|=1<<u
        def con(mask):
            if not mask:return False
            seen=todo=mask&-mask
            while todo:
                bit=todo&-todo;todo^=bit
                fresh=adj[bit.bit_length()-1]&mask&~seen
                seen|=fresh;todo|=fresh
            return seen==mask
        mins=[None,None]
        for mask in range(2,1<<n,2):
            def crosses(u,v):return bool(((mask>>u)^(mask>>v))&1)
            marked=[all(crosses(*spokes[j]) for j in js) for js in ((0,1),(2,1))]
            if not any(marked) or not con(mask) or not con(((1<<n)-1)^mask):continue
            cost=sum(ww for u,v,ww in ends if crosses(u,v))
            for j,yes in enumerate(marked):
                if yes and (mins[j] is None or cost<mins[j]):mins[j]=cost
        assert mins==[marked_pair(anchors,s,s,left,hc,p,js)['K'] for js in [(0,1),(2,1)]]
    return 3


def family(r):
    anchors=r+2
    s=2*r+1
    mids=4+2*s
    L=s*(anchors+1)//2+1
    M=max(L, (r*(anchors-2)+mids)//(s-2*r)+1)
    old_ceiling=mids+r*(2*M+anchors-2)
    assert old_ceiling<s*M and 2*L+s*(anchors+1)<4*L
    info=dict(r=r,anchors=anchors,shields_per_hub=s,middles=mids,L=L,M=M,
              folded_bond_upper=old_ceiling,hub_to_exterior_lower=s*M,
              later_explicit_bond_size=2*L+s*(anchors+1), later_image_lower=4*L)
    for age,price in [(1,M),(2,1)]:
        info[f'age_{age}']=[marked_pair(anchors,s,s,L,M,price,m) for m in ((0,1),(2,1))]
    assert info['age_1'][0]['K']==info['age_1'][1]['K']
    assert info['age_2'][0]['K']<info['age_2'][1]['K']
    return info


if __name__=='__main__':
    here=Path(__file__).resolve().parent
    result={'counting':'K is bond cardinality, pair distance is K minus one.',
            'literal_small_comparisons':audit_unquotiented(),
            'analytic_family':[family(r) for r in (3,4,5)]}
    output=here.parents[2]/'artifacts'/here.parent.name/here.name/'future_reading.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print([(v['r'],v['M'],[q['K'] for q in v['age_1']],[q['K'] for q in v['age_2']])
           for v in result['analytic_family']])
