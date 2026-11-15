"""Check the finite induction bases, affine branch embeddings and failure controls."""
from collections import Counter
from itertools import combinations
import json

from conditional_bases import AffineSearch, finite_bases


def parity(value):
    return value.bit_count() & 1


def truth(n, function):
    return sum(int(function(x)) << x for x in range(1 << n))


def point(table, x):
    return (table >> x) & 1


def polar(table, x, y):
    return point(table, 0) ^ point(table,x) ^ point(table,y) ^ point(table,x^y)


def eigen_lifts():
    n = 4
    points = list(range(1 << n))
    q = truth(n,lambda x:parity((x & (x >> 1)) & 5))
    monos = [truth(n,lambda x:bool((x >> i) & (x >> j) & 1)) for i,j in combinations(range(n),2)]
    quadratics = [0]
    for mon in monos:
        quadratics += [a ^ mon for a in quadratics]
    linear = [truth(n,lambda x:parity(x & z)) for z in points]
    counts = Counter()

    def check(a, v, eps, g, h, row, name):
        w = next(w for w in points if polar(q,v,w))
        residual = [z for z in points if not polar(q,v,z) and not polar(q,w,z)]
        assert len(residual) == 4 and any(polar(q,z,y) for z in residual for y in residual)
        selected = next(c for c in (0,1) if parity(row & v) ^ (g & (point(q,v)^c)) ^ (h & (point(a,v)^(c & eps))))
        cw = selected*w
        dq,da = point(q,v)^selected,point(a,v)^(selected & eps)
        for answer in range(2):
            images = set()
            for z in residual:
                base = z^cw
                assert point(q,base) ^ point(q,base^v) == dq
                assert point(a,base) ^ point(a,base^v) == da
                for s in (0,1):
                    for u in (0,1):
                        eta = answer ^ parity(base & row) ^ (g & s) ^ (h & u)
                        x,ss,uu=base^(v*eta),s^(eta & dq),u^(eta & da)
                        assert parity(x & row) ^ (g & ss) ^ (h & uu) == answer
                        assert ((s,u)==(point(q,base), point(a,base))) == ((ss,uu)==(point(q,x),point(a,x)))
                        assert (s!=point(q,base)) == (ss!=point(q,x))
                        images.add((x,ss,uu))
            assert len(images) == 16
        counts[name] += 1

    for mat in quadratics:
        eigen = {eps:[v for v in points[1:] if all(polar(mat,v,z)==(eps & polar(q,v,z)) for z in points)] for eps in (0,1)}
        choices = [(eps,v) for eps in (0,1) for v in eigen[eps]]
        if choices:
            eps,v = choices[0]
            for row in points:
                check(mat ^ linear[7],v,eps,1,0,row,'mixed_total_queries')
        if eigen[1]:
            for ell in linear:
                check(mat ^ ell,eigen[1][0],1,0,1,0,'normalized_private_queries')
    return dict(sorted(counts.items()))


def pinned_two_counter():
    n=4
    q,f=0x8777,0xe248
    solver=AffineSearch(n)
    full=solver.universe
    domain=full^f
    costs=[]
    for orient in (q,full^q):
        rich=(full^orient)&domain
        cost=next(k for k in range(1,4) if solver.fits(rich,orient,k))
        costs.append(cost)
    def radical_size(table):
        return sum(all(not polar(table,x,1<<j) for j in range(n)) for x in range(1<<n))
    assert radical_size(q)==radical_size(q^f)==1
    assert domain.bit_count()==10 and costs==[1,2]
    return {'f':hex(f),'q':hex(q),'domain_size':10,'sources':16,'exact_cost_by_pinned_sign':costs}


def guarded_support_controls():
    n=4
    q=truth(n,lambda x:parity((x & 3) & (x >> 2)))
    f=truth(n,lambda x:x & 3 == 3)
    full=(1 << (1 << n))-1
    solver=AffineSearch(n+1)
    plain=q | ((full^q) << (1 << n))
    costs=[]
    for d in (full^f,f):
        rich=(d&(full^q)) | ((d&q) << (1 << n))
        costs.append(next(k for k in range(1,5) if solver.fits(rich,plain,k)))
    assert costs==[3,1]

    covers=[{0,1,2,3,4,6},{5,6,8,9,10,11},{6,7,12,13,14,15}]
    assert set.union(*covers)==set(range(16)) and set.intersection(*covers)=={6}
    for S in covers:
        rich=sum(1 << (x | (point(q,x) << n)) for x in S)
        assert solver.fits(rich,plain,1)
    # Use two actual one-sided Boolean labels to route a point to the first covering set.
    labels=[next(i for i,S in enumerate(covers) if x in S) for x in range(16)]
    solver2=AffineSearch(n+3)
    plain2=truth(n+3,lambda z:((z>>n)&1)!=point(q,z & 15))
    rich2=sum(1 << (x | (point(q,x)<<n) | (labels[x]<<(n+1))) for x in range(16))
    cells=[truth(n+3,lambda z:(z>>(n+2))==1),
           truth(n+3,lambda z:(z>>(n+1))==0),truth(n+3,lambda z:(z>>(n+1))==1)]
    for cell in cells:
        while cell:
            reduced=solver2.hull(cell & rich2) & solver2.hull(cell & plain2)
            if reduced==cell:break
            cell=reduced
        assert cell==0
    return {'rank_two_promise_costs_majority_minority':costs,'three_scalar_terminal_source_sets':[sorted(S) for S in covers],
            'two_arbitrary_labels_verified_tree_leaves':len(cells)}


def short_path_leaves():
    m=17
    prefix=(1,3,5,7,12,14,16)
    forced=(9,10)
    known=set(prefix+forced)
    assert all(bool({j,j+1}&known) for j in range(m))
    even_edges=sum(1<<j for j in range(1,m,2))
    affine_edges=even_edges ^ (1 << 9)
    assert all(bool({j,j+1} & set(prefix)) for j in range(1,m,2) if j!=9)
    count=0
    for x in range(1 << (m+1)):
        products=x & (x >> 1)
        query=parity(products & even_edges) ^ parity(products & affine_edges)
        assert query==((x>>9)&(x>>10)&1)
        count+=query
    return {'source_assignments_checked':1 << (m+1),'prefix_answers':1<<len(prefix),
            'query_depth_of_short_branches':len(prefix)+1,'honest_sources_on_short_branches':count}


def main():
    finite=finite_bases()
    for t,kind,count in ((1,'free',16),(2,'free',1792),(3,'pinned',3555328)):
        assert sum(finite[str(t)]['represented_cases_by_required_leaves'][kind].values())==count
    result={'status':'passed','finite_bases':finite,'zero_rank_free_base':'one leaf suffices',
            'root_eigenvector_embeddings':eigen_lifts(),'pinned_rank_two_counterexample':pinned_two_counter(),
            'guarded_support_controls':guarded_support_controls(),'seventeen_edge_short_branches':short_path_leaves()}
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':
    main()
