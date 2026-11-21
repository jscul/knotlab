"""Stress the unbounded twin statements on complete lawful source/reached catalogues."""
from collections import Counter,defaultdict
from itertools import combinations
from select_target import OUT, ROOT, OLD, PREV, HISTORY, read,save
from census_stages import connected_archive,owners,width
from census_rate_tables import nae_table
from census_rates import twin_classes


def matrix_of(n,total,values):
    c=[[total if i==j else 0 for j in range(n)] for i in range(n)]
    for (i,j),k in zip(combinations(range(n),2),values,strict=True):
        c[i][j]=c[j][i]=total-2*k
    return c


def grouped(n,c):
    # A pair is a twin if and only if transposing its names preserves all
    # indicated correlations. This direct test uses fixed names.
    return [(i,j) for i,j in combinations(range(n),2) if all(c[i][x]==c[j][x] for x in range(n) if x not in (i,j))]


def audit_source(through=10):
    source_types=connected_archive()['nae']
    bysize={}
    cases=[]
    for n,sources in source_types.items():
        if n>through:continue
        box=Counter()
        for idx,source in enumerate(sources):
            rows=source.rows;inc=owners(rows)
            loose={i for i,any_holders in inc.items() if len(any_holders)==1}
            total,raw,_=nae_table(rows,())
            c=matrix_of(n,total,[raw[k] for k in combinations(range(n),2)])
            box['physical_types']+=1
            for i,j in combinations(sorted(loose),2):
                box['loose_pairs']+=1
                if inc[i]!=inc[j]:box['different_holder_pairs']+=1
                twins=all(c[i][x]==c[j][x] for x in range(n) if x not in (i,j))
                if not twins:continue
                box['twin_loose_pairs']+=1
                if inc[i]==inc[j]:
                    assert c[i][j]<0
                    box['same_holder_negative']+=1
                    continue
                A=set(rows[inc[i][0]])-{i}
                B=set(rows[inc[j][0]])-{j}
                assert A==B and c[i][j]>0
                box['distinct_holder_identical_companions_positive']+=1
                cases.append(dict(width=n,index=idx,pair=[i,j],companion_size=len(A),words=total,signed_sum=c[i][j]))
        bysize[n]=dict(box)
    return dict(by_width=bysize,different_holder_twin_examples=cases)


def reached_pass(rows,youngest,c):
    n=len(c)
    inc=owners(rows)
    twins=set(grouped(n,c))
    earliest={x for x,hs in inc.items() if len(hs)==1}
    stat=Counter()
    for k in youngest:
        H=rows[k]
        f=earliest&set(H)
        old=set(H)-f
        assert f and old
        for x,y in combinations(H,2):
            pair=tuple(sorted((x,y)))
            stat['same_latest_holder_pairs']+=1
            if {x,y}<=old:stat['old_input_pairs']+=1
            if {x,y}<=f:stat['loose_sibling_pairs']+=1
            if pair in twins:
                stat['in_holder_twin_pairs']+=1
                assert {x,y}<=f
            elif {x,y}<=f:raise AssertionError('interchangeable siblings should be twins')
    return stat


def archived_stages():
    original=read(HISTORY/'census_stages.json.gz')['nae']
    counts=read(HISTORY/'census_rate_tables.json.gz')['nae']['records']
    sums=Counter()
    for d in counts:
        s=original[d['source_index']]['stages'][d['age']-1]
        c=matrix_of(d['width'],d['allowed_states'],d['disagreement_counts'])
        sums.update(reached_pass(s['rows'],s['youngest'],c))
        sums['earned_stages']+=1
    return dict(sums)


def main():
    report=dict(uniform_sources=audit_source(),uniform_archive_reached=archived_stages())
    save(OUT/'twin_checks.json',report)
    total=Counter()
    for d in report['uniform_sources']['by_width'].values():total.update(d)
    print(dict(total),report['uniform_archive_reached'])
if __name__=='__main__':main()
