"""Checks independent of the primary structural enumeration and selected-score calculation."""
from collections import Counter,defaultdict
from functools import cache
from itertools import combinations,permutations,product
from math import factorial
from pathlib import Path
import gzip
import json
import sys
from observables import CONTEXTS, WORDS, OUTPUT, ROOT, PRIOR, SIGNS, freeze, measure, put
sys.path.insert(0,str(PRIOR))
import run as prior
sys.path.insert(0,str(ROOT/"research/ENTANGLEMENT-READ-20261120-001"))
from embodied_control import canonical_gate


def cycles(p):
    rem=set(range(len(p))); out=[]
    while rem:
        x=min(rem); loop=[]
        while x in rem:
            rem.remove(x);loop.append(x);x=p[x]
        out.append(len(loop))
    return tuple(sorted(out))


def burnside_counts(k):
    """Fixed holder incidence multisets, independent of the Atlas and its automorphisms."""
    types=tuple((i,) for i in range(k))+tuple(combinations(range(k),2))
    by_type=defaultdict(list)
    for p in permutations(range(k)):
        by_type[cycles(p)].append(p)
    total=[0]*11
    for ps in by_type.values():
        p=ps[0]
        todo=set(types); orbits=[]
        while todo:
            item=min(todo); items=[]
            while item in todo:
                todo.remove(item);items.append(item)
                item=tuple(sorted(p[i] for i in item))
            degree=tuple(sum(int(i in u) for u in items) for i in range(k))
            orbits.append((len(items),degree))
        can_touch=[tuple(any(g[1][i] for g in orbits[q:]) for i in range(k)) for q in range(len(orbits)+1)]
        @cache
        def visit(pos,remaining,needs):
            if remaining*2<sum(needs):return 0
            if any(a and not b for a,b in zip(needs,can_touch[pos])):return 0
            if pos==len(orbits):
                return int(remaining==0 and not any(needs))
            width,added=orbits[pos]
            return sum(visit(pos+1,remaining-t*width,tuple(max(0,x-t*d) for x,d in zip(needs,added)))
                       for t in range(remaining//width+1))
        for n in range(3,11):
            total[n]+=len(ps)*visit(0,n,(3,)*k)
        visit.cache_clear()
    assert all(v%factorial(k)==0 for v in total)
    return [x//factorial(k) for x in total]


def independent_tables(rows,marks):
    size=1+max(map(max,rows)); result=Counter()
    for w in product((0,1),repeat=size):
        if all(len({w[i] for i in row})>1 for row in rows):
            result[tuple(w[i] for i in marks)]+=1
    return [result[w] for w in WORDS]


def hypotheses_controls():
    # At 00 the pinned marked outputs 11 have no extension once a support
    # holds marks from both readers, even with ordinary ternary constraints.
    nonsep=((0,1,2),(3,4,5),(2,5,6),(0,3,6))
    marks=tuple(range(6));raw=independent_tables(nonsep,marks)
    obs=measure(raw)
    assert all(row["eligible"] for row in prior.certify(nonsep,"nae"))
    assert obs["I"]["joint"][0][3]==0
    # A path of three binary inequalities forces a1 != b1 while two-step
    # separation still holds; the two readers themselves keep the ordinary law.
    binary=((0,1,2),(3,4,5),(1,6),(6,7),(7,4))
    hist=independent_tables(binary,marks)
    assert sum(n for w,n in zip(WORDS,hist) if w[2]==w[5]==0 and w[1]==w[4]==1)==0
    # Any choices of pins on a three-holder odd cycle leave a completion.
    odd=((0,3,4),(1,4,5),(2,5,3))
    extensions=[]
    for pins in product((0,1),repeat=3):
        extensions.append(sum(all(len({word[i] for i in row})>1 for row in odd)
                              for rest in product((0,1),repeat=3) for word in [pins+rest]))
    assert all(extensions)
    from readings import step_neighborhoods,shortest_steps
    cross=shortest_steps(marks[:3],marks[3:],step_neighborhoods(nonsep)[0])
    binary_cross=shortest_steps(marks[:3],marks[3:],step_neighborhoods(binary)[0])
    assert cross==1 and binary_cross==3
    return {"nonseparated_supports":nonsep,"nonseparated_cross_steps":cross,"nonseparated_00_counts":obs["I"]["joint"][0],
            "binary_supports":binary,"binary_cross_steps":binary_cross,"binary_target_pin_completions":0,
            "odd_cycle_all_eight_pin_extensions":extensions}


def mixture_controls():
    all_tests=hidden=0
    for raw in product((0,1),repeat=8):
        left=(raw[:2],raw[2:4]);right=(raw[4:6],raw[6:])
        for q in product((0,1,2),repeat=4):
            joint=[]
            for idx,(s,t) in enumerate(CONTEXTS):
                counts=[0]*4
                for h,n in ((0,2-q[idx]),(1,q[idx])):
                    counts[2*left[s][h]+right[t][h]]+=n
                joint.append(counts)
            all_tests+=1
            if any(sum(joint[i][:2])!=sum(joint[j][:2]) for i,j in ((0,1),(2,3))): continue
            if any(sum(joint[i][::2])!=sum(joint[j][::2]) for i,j in ((0,2),(1,3))): continue
            hidden+=1
            cor=[a-b-c+d for a,b,c,d in joint]
            assert all(sum(s*y for s,y in zip(signs,cor))<=4 for signs in SIGNS)
    return {"conditional_binary_mixtures":all_tests,"both_hidden":hidden,"above_two":0}


def main():
    freeze()
    census=json.loads((OUTPUT/'census_summary.json').read_text())
    burned=[burnside_counts(k) for k in range(1,7)]
    for n in range(3,11):
        assert sum(row[n] for row in burned)==census['by_size'][str(n)]['structural']['presentations']
    gates={}
    for law in ('nae','parity'):
        gates[law]={}
        for arity in range(3,11):
            ok=tuple(w for w in range(1<<arity) if (w.bit_count()%2==0 if law=='parity' else 0<w<(1<<arity)-1))
            gate=canonical_gate(arity,ok)
            assert gate['is_knot']
            gates[law][arity]=gate
    extra=json.loads(gzip.decompress((OUTPUT/'stress_tables.json.gz').read_bytes()))[0]
    assert extra['name']=='archive_03'
    expected=json.loads(prior.ARCHIVE.read_text())['named_archive_starts']['start-03']['gate']['literal_supports']
    assert extra['old']==expected
    # Original built parity relay, reconstructed upstream by multiplying its
    # independent two-terminal counts. Recheck our six-mark register metric.
    import embodied_control_replay as relay
    relay_rows={}
    for law,allowed in (("nae",relay.not_all_equal),("parity",relay.even)):
        weights,ext=relay.registers(allowed,relay.group_counts(allowed))
        relay_rows[law]={}
        for age in (0,1):
            out=Counter()
            for w,unit,multiple in zip(relay.REGISTER_WORDS,weights,ext):
                x,a0,a1,p,y,b0,b1=w
                out[a0,a1,x,b0,b1,y]+=unit*(multiple if age else 1)
            raw=[out[w] for w in WORDS]
            e=measure(raw);f=measure(raw,False)
            relay_rows[law][age]={"total":sum(raw),"full_pair_tv":e['full_pair_tv'],"embodied_I":e['I']['maximum'],
                                  "external_I":f['I']['maximum'],"same_assignment_extensions":sorted(set(ext)-{0})}
            if law=='parity': assert e['I']['maximum']=='4' and e['full_pair_tv']==[['1','1'],['0','0']]
    output={"burnside_numbers_for_holder_counts_1_through_6":burned,"size_range":[3,10],
            "all_structural_counts_match":True,"canonical_K1_K2_K3_by_projected_relation":gates,
            "proof_hypothesis_controls":hypotheses_controls(),"binary_separator_check":mixture_controls(),
            "inherited_ten_knot_relay":relay_rows}
    put('verification.json',output)
    print('structural counts',sum(sum(row) for row in burned),'canonical projected relations',sum(map(len,gates.values())),
          'mixture check',output['binary_separator_check'])
if __name__=='__main__':
    main()
