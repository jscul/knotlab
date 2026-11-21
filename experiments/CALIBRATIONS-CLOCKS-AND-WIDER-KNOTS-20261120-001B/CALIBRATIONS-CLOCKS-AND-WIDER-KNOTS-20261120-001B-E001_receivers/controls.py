"""Independent true-parent replays for clock origin, separation and hidden marks."""
from collections import Counter
from itertools import product
import sys

import networkx as nx

from receivers import ROOT,LAWS,fix,end,clocks,write

CONE=next((ROOT/'experiments/INFLUENCE-CONE-20261120-001A').iterdir())
sys.path.insert(0,str(CONE))
import interventions as cone


def combine(a,b,h,k):
    shift=1+max(d for r in a for d in r)
    out=[list(r) for r in a]+[[d+shift for d in r] for r in b]
    marker=1+max(d for r in out for d in r)
    out[h].append(marker);out[len(a)+k].append(marker)
    return tuple(map(tuple,out))


def actual_windows(a,b,frames,offset,law):
    outcomes=[]
    ids={(v,):v for v in set(a+b)}
    words=set(sum((clocks.windows(a*k+b,z) for k in (1,2,3) for z in range(1,len(frames)-offset+2)),[]))
    for m,(births,_) in enumerate(frames[offset:],2):
        pairs={frozenset(x.parents):x for x in births if len(x.parents)==2}
        new={}
        for w in words:
            if len(w)!=m:continue
            key=frozenset((ids[w[1:]],ids[w[:-1]]))
            assert len(key)==2
            new[w]=pairs[key].knot
        ids.update(new);outcomes.append({'size':m,'distinct_physical_windows':len(set(new.values()))})
    # First appearance in each of the position-matched, structurally typed languages.
    result=[]
    for k in range(1,9):
        w=a*k+b;p=len(w);mark=b[-1]
        seq=(w*5)
        def excluded(block):
            spots=[j for j,x in enumerate(block) if x==mark]
            for i,first in enumerate(spots):
                for second in spots[i+1:]:
                    d=second-first
                    for pos in range(max(0,second-2*d+1),min(first,len(block)-2*d)+1):
                        if block[pos:pos+d]==block[pos+d:pos+2*d]:return True
            return False
        assert not any(excluded(seq[i:i+2*p-1]) for i in range(p))
        assert all(excluded(seq[i:i+2*p]) for i in range(p))
        assert all(seq[i:i+2*p][:p]==seq[i:i+2*p][p:] for i in range(p))
        result.append({'index':k,'period_in_phases':p,'first_physical_age':offset+2*p-1})
    return {'origin':offset,'true_returns':[a,b],'initial_replay':outcomes,'release_batches':result}


def anchors():
    meetings=[(0,1),(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6)]
    opens=[3,0,3,3,3,2,2]
    a=fix.source_from(meetings+[(2,4)],opens)
    b=fix.source_from(meetings+[(1,2)],opens)
    host=combine(a,b,1,1)
    out={'source':host}
    assert nx.is_connected(fix.incidence(host)[1])
    for law in LAWS:
        fix.certify_source(host,law)
        _,layers=fix.trajectory(host,law,5)
        labels={i:i//7 for i in range(14)}
        for births,_ in layers:
            for x in births:
                sides={labels[v] for v in x.parents};assert len(sides)==1
                labels[x.knot]=sides.pop()
        first={x.parents:x for x in layers[0][0]}
        def pick(*raw): return first[tuple(7+r for r in raw)].knot
        u=(pick(4,6),pick(3,6),pick(0,3),pick(0,4))
        v=(pick(4,6),pick(3,6),pick(2,3),pick(2,4,5))
        assert len(first[tuple(7+r for r in (2,4,5))].fresh)==4
        left=actual_windows((4,0,2,5),(4,0,3,6),layers,0,law)
        right=actual_windows(u,v,layers,1,law)
        def count(t,h):return max(0,(t-h+1)//8-1)
        for t in range(15,255):
            assert count(t,0)==count(t+1,1)
            assert count(t,0)-count(t,1)==int((t+1)%8==0)
        out[law]={'left':left,'right':right,'count_sequence':[(t,count(t,0),count(t,1)) for t in range(13,81)],
                  'true_group_sizes':[dict(Counter(len(b.parents) for b in batch)) for batch,_ in layers]}
    return out


def source_distance():
    a,p=clocks.cycle_words(4)
    rows=[]
    for n,r in [(1,2),(2,3),(1,3)]:
        s=4*(n+1);q=4*(r+1);l=2*min(s,q)-3
        assert not (clocks.language_parts(n,l+1)&clocks.language_parts(r,l+1))
        for m in range(2*max(s,q),2*max(s,q)+65):
            old=a*n+p[0];new=a*r+p[0]
            right={v[:l]:v for v in clocks.windows(new,m)}
            u=next(w for w in clocks.windows(old,m) if w[-l:] in right)
            v=right[u[-l:]]
            joint=u+v[l:]
            assert all(joint[j]!=joint[j+2] for j in range(len(joint)-2))
            assert clocks.source(u) and clocks.source(v)
            assert joint[:-1][:m]==u and joint[1:][-m:]==v
            rows.append({'spacings':[s,q],'m':m,'common':u[-l:],'d':m-l,'actual_joint_size':len(joint)})
    return {'current_sources':rows,'previous_epoch_sends':[clocks.inclusive(1,2,e) for e in range(1,13)]}


def mark_swap():
    out={}
    for length in range(4):
        data=[]
        for mode in (False,True):
            raw,ids,receiver=cone.structural_source(length,mode)
            data.append((tuple(raw.values()),ids,receiver))
        left,right=data
        # Ordinary spent-to-spent bridge; it neither contributes a live witness
        # pair nor changes any old holder's loose count.
        both=combine(left[0],right[0],left[1]['switch'],right[1]['switch'])
        q=[left[2],len(left[0])+right[2]]
        # Place a redundant repeated physical holding on the same original
        # receiver meeting of the two queried arms in alternative preparations.
        def tag(which):
            rows=[list(r) for r in both]
            new=1+max(d for r in rows for d in r)
            zone=data[which]; offset=which*len(left[0])
            witness=zone[1][('w_r_r1' if length==1 else 'w_r'+str(length-1)+'_r'+str(length)) if length else 'w_r_a']
            for i in (q[which],offset+witness):rows[i].extend((new,new+1,new+2))
            return tuple(map(tuple,rows))
        z=tag(0),tag(1)
        assert end.from_stars(z[0])==end.from_stars(z[1])
        for law in LAWS:
            snapshots=[]
            for arm,rows in enumerate(z):
                state=end.from_stars(rows)
                fix.certify_source(rows,law)
                marked={q[arm]}
                for step in range(1,length+2):
                    result=end.step(state,law)
                    assert result.status=='extend'
                    marked={i for i,ps in enumerate(result.parents) if marked.intersection(ps)}
                    state=result.end
                graph=nx.Graph(end.neighbors(state))
                fresh={i:state.opens[i] for i in marked}
                non2=[i for i,f in fresh.items() if f!=2]
                assert len(non2)==1 and list(fresh[i] for i in non2)==[arm+3]
                # Rival end role: non-two knots adjacent to some two-fresh knot.
                candidates=sorted(i for i in state.opens if state.opens[i] in (3,4) and any(state.opens[j]==2 for j in graph[i]))
                snapshots.append({'marked':non2[0],'role_fresh':state.opens[non2[0]],
                                  'anonymous_role_counts':dict(Counter(state.opens[i] for i in candidates)),
                                  'witnessed_live':len(state.opens),'counts':sorted(fresh.values()),'selected':non2[0] in candidates})
            assert snapshots[0]['anonymous_role_counts']==snapshots[1]['anonymous_role_counts']
            unpadded=[]
            for raw,_,query in data:
                state=end.from_stars(raw); targets={query}
                for step in range(1,length+2):
                    plan=end.step(state,law);targets={i for i,ps in enumerate(plan.parents) if targets.intersection(ps)};state=plan.end
                adj=end.neighbors(state)
                candidates=[i for i in state.opens if state.opens[i] in (3,4) and any(state.opens[j]==2 for j in adj[i])]
                unpadded.append({'role_counts':dict(Counter(state.opens[i] for i in candidates)),
                                 'requested_hits':[state.opens[i] for i in targets if i in candidates]})
            out[f'{length+2}_{law}']={'unpadded':unpadded,'source':both,'query_by_arm':q,'tag_rule':'add three shared at original query and its incident path witness','snapshots':snapshots}
    return out


def minimal_open():
    starts=fix.source_from([(0,1),(0,1),(1,2)],[2,1,2])
    data={'physical':starts}
    for law in LAWS:
        fix.certify_source(starts,law)
        frames,layers=fix.trajectory(starts,law,12)
        receiver=2;left=0;history=[]
        for births,_ in layers:
            keep=next(b for b in births if set(b.parents)=={receiver,left})
            other=next(b for b in births if b.parents==(left,))
            assert len(keep.fresh)==len(other.fresh)==2
            history.append({'queried':keep.knot,'exact_parents':keep.parents,'continuing_tip':other.knot})
            left,receiver=other.knot,keep.knot
        data[law]=history
    sym=[]
    for k in range(1,8):
        # Put a second active component alongside to exercise the nonclosing
        # rule even when the first part has its only full-set birth.
        host=fix.source_from([(0,1),(0,1)],[k,2])
        st=end.from_stars(host);old={0};path=[]
        for j in range(k+7):
            plan=end.step(st,'parity');assert plan.status=='extend'
            old={i for i,g in enumerate(plan.parents) if old.intersection(g)}
            st=plan.end
            graph=nx.Graph(end.neighbors(st)).subgraph(old)
            path.append({'size':len(old),'degrees':dict(Counter(dict(graph.degree).values())),
                         'opens':dict(Counter(st.opens[v] for v in old))})
        if k>=3:
            import math
            assert [r['size'] for r in path[:k]]==[math.comb(k,i) for i in range(1,k+1)]
        assert all(max(map(int,q['degrees']))<=2 for q in path[-4:])
        sym.append({'k':k,'component':path})
    return {'three_holder':data,'singleton_starts':sym}


def delayed_turns():
    a,p=clocks.cycle_words(4);result=[]
    for n in (1,2):
        words=[a*n+p[0]+a*n+p[j] for j in (1,2)]
        per=len(words[0]);assert len(words[1])==per
        for q in (per+2,2*per):
            readings=[]
            for word,mark,launch in zip(words,('b1','b2'),(q,per)):
                hits=[]
                for m in range(launch,5*per+2):
                    phase=[w for w in clocks.windows(word,m) if w[0]==mark]
                    assert len(phase)==1
                    if phase[0][-1]==mark:hits.append(m)
                assert hits==[m for m in range(launch,5*per+2) if (m-1)%per==0]
                readings.append({'marked_original':mark,'launch_size':launch,'turns':hits})
            result.append({'n':n,'period':per,'physical_packets':readings})
    return result


if __name__=='__main__':
    write('anchor_controls.json.gz',{'anchors':anchors(),'delayed':delayed_turns(),'minimum':minimal_open()})
    write('distances.json.gz',source_distance())
    write('hidden_receiver.json.gz',mark_swap())
