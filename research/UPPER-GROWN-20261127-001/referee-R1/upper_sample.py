"""Seek a connected set of four signed lower clauses on the post-birth sample."""
import argparse
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
from time import perf_counter

from census_recount import compiled_search, names, read_roster, rebuild_stages, supports_of
from upper_readings import agree, columns, four_clauses, rectangles, words

HERE = Path(__file__).resolve().parent


def encode(raw,sign):
    # A common position per name preserves disjointness across both signs.
    return sum((1 | (2 << sign)) << (3*i) for i in names(raw))


def confirm(supports,k0,groups,clauses,encoding,index):
    n=max(max(k) for k in supports)+1
    universe,raw = columns(n)
    obey = [universe ^ agree(k,raw,universe) for k in supports]
    allowed = universe
    for s in obey:
        allowed &= s
    parts=[r for group in groups for r in group]
    pos={r:i for i,r in enumerate(parts)}
    chosen=[encoding[r] for r in parts]
    readings=[]
    for mask,v in chosen:
        val=agree(names(mask),raw,universe)
        readings.append(val if v else universe^val)
    cc=[[pos[r] for r in clause] for clause in clauses]
    assert all(words(allowed,[readings[i] for i in clause])==list(range(7)) for clause in cc)
    uu=[readings[2*i]&readings[2*i+1] if i==index else readings[2*i]|readings[2*i+1] for i in range(3)]
    if words(allowed,uu)!=list(range(7)):
        return
    triple=uu[0]&uu[1]&uu[2]
    drops=[]
    for i in range(len(obey)):
        st=triple
        for j,s in enumerate(obey):
            if j!=i:
                st &= s
        drops.append(st.bit_count())
    if not any(drops[k0:]):
        return
    for clause in cc:
        cells=[allowed]
        for i in clause:
            r=readings[i]
            cells=[v for s in cells for v in (s&r,s&~r) if v]
        if not all(any(s&u and s&~u for s in cells) for u in uu):
            return
    for (m,_),r in zip(chosen,readings):
        for j in names(m):
            if not (allowed & ~raw[j] & (allowed>>(1<<j)) & (r^(r>>(1<<j)))):
                return
    abstract_rows=list(product((0,1),repeat=6))
    def abstract(drop):
        return {tuple(w[2*i]&w[2*i+1] if i==index else w[2*i]|w[2*i+1] for i in range(3))
                for w in abstract_rows if all(j==drop or not all(w[k] for k in c) for j,c in enumerate(cc))}
    if len(abstract(-1))!=7 or not all(len(abstract(j))==8 for j in range(4)):
        return
    return dict(source=supports,source_knots=k0,raw_agreements_and_selected_value=[(names(m),v) for m,v in chosen],
                lower_clauses=cc,both_tests_pair=index,restored_upper_111_by_dropped_law=drops,
                actual_lower_words=words(allowed,readings),actual_upper_words=words(allowed,uu))


def seek(search,supports,k0):
    table={}
    pairs=defaultdict(set)
    clauses=[]
    with search.finite_bonds(supports) as (buf,number,_):
        for bond in buf[:number]:
            miss=bond.missing
            if miss.bit_count()!=1:
                continue
            word=miss.bit_length()-1
            signed=[]
            for i,m in enumerate(bond.carriers):
                v=(word>>(2-i))&1
                k=encode(m,v)
                table[k]=(m,v)
                signed.append(k)
            a,b,c=sorted(signed)
            for x,y,z in ((a,b,c),(a,c,b),(b,c,a)):
                pairs[x,y].add(z)
            clauses.append((a,b,c))
    found=0
    for build in (rectangles,four_clauses):
        for groups,laws in build(clauses,pairs):
            found+=1
            for i in range(2 if build is rectangles else 3):
                w=confirm(supports,k0,groups,laws,table,i)
                if w:
                    return number,found,w
    return number,found,None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit',type=int,required=True)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    archive,_,sample,rows,_=read_roster()
    selected=sorted((-rr['bonds'],i,rr['round']) for i in sample for rr in rows[i]['rounds'][1:]
                    if rr['search']=='full' and rr['distinctions']>=12 and rr['bonds']>=4)
    output=[]
    with compiled_search() as search:
        for count,i,t in selected[:args.limit]:
            begin=perf_counter()
            source=supports_of(archive[i])
            stage=rebuild_stages(source)[0][t]
            num,found,w=seek(search,stage,len(source))
            assert num==-count
            output.append(dict(census_rank=i,round=t,stage_laws=len(stage),signed_bonds=num,
                               qualifying_four_clause_patterns_reached=found,witness=w,seconds=perf_counter()-begin))
            if w:
                break
    print('tested',len(output),'patterns',sum(r['qualifying_four_clause_patterns_reached'] for r in output),
          'found',bool(output[-1]['witness']),'seconds',round(sum(r['seconds'] for r in output),2),flush=True)
    if not args.pilot:
        (HERE/'upper_sample.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':
    main()
