"""Ordinary identified parent replay. Earliest receipt by native portal paths and a separate word search."""
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import pairwise
from pathlib import Path
import gzip
import hashlib
import json
import sys

import networkx as nx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
PRIMARY=('absent','active','short','one_port','rewired')
NODES=('v','r1','r2','r3','s','t','b0','b1','b2')


def base(zone):
    a=tuple(zone+x for x in ('v','r1','r2','r3'))
    exits=[tuple(zone+x for x in ('v','s','b'+str(j),'t')) for j in range(3)]
    return a,exits


def layout(arm,d):
    g=nx.Graph()
    for zone in ('S','R'):
        neutral,marked=base(zone)
        for loop in (neutral,*marked):
            g.add_edges_from(pairwise((*loop,loop[0])))
    ref=['a',*('h'+str(i) for i in range(1,46)),'b']
    g.add_edges_from(pairwise(ref))
    g.add_edges_from([('Rr1','Sb2'),('Rb2','a'),('b','Sb2')])
    if arm!='absent':
        closed=arm!='short'
        n=2*d+1 if closed else d+1
        c=['c'+str(i) for i in range(n)]
        g.add_edges_from(pairwise(c))
        if closed: g.add_edge(c[-1],c[0])
        g.add_edge('a',c[0])
        if arm!='one_port': g.add_edge(c[d],'b')
        if arm=='rewired':
            assert d==32
            g.remove_edges_from([('c48','c49'),('h23','h24')])
            g.add_edges_from([('h23','c49'),('c48','h24')])
    assert min(dict(g.degree()).values())>=2 and nx.is_connected(g) and not any(nx.triangles(g).values())
    return g


@cache
def send(j):
    neutral,exits=base('S')
    unit0=neutral+exits[0];unit1=neutral+exits[1]
    period=unit0*(j-1)+unit1
    i=period.index('Sb1')-1
    p=period[i:]+period[:i]
    return p+p


@cache
def left(k):
    neutral,exits=base('R')
    word=neutral*2+exits[0]
    zero=word.index('Rb0')
    return tuple(word[(zero+i)%len(word)] for i in range(-k,0))


def canonical(word):
    return min(tuple(word),tuple(reversed(word)))


def orientation(word):
    """Recognition uses only the marked original roles in the current ordinary straight member."""
    if not word: return None
    for w in (tuple(word),tuple(reversed(word))):
        k=len(w)//2
        if w.count('Rb1')!=1 or w[k]!='Rb1' or w[:k]!=left(k):
            continue
        intake=w[k+1:]
        if intake[:3]!=('Rt','Rb2','a')[:len(intake)] or any(v.startswith('R') for v in intake[3:]):
            continue
        return w
    return None


def factors(word,part):
    return [i for i in range(len(word)-len(part)+1) if tuple(word[i:i+len(part)]) in (part,part[::-1])]


def intrinsic_decodes(word, parents):
    """No arm name, global age, sender ID, previous chosen route, or expected release is an input."""
    if not isinstance(word,(tuple,list)) or len(parents)!=2: return []
    w=orientation(word)
    if w is None: return []
    p=[canonical(x) for x in parents]
    if len(set(p))!=2 or set(p)!={canonical(w[:-1]),canonical(w[1:])}: return []
    marked=[x for x in parents if orientation(x) is not None]
    if len(marked)!=1: return []
    inside=marked[0]
    outside=next(x for x in parents if canonical(x)!=canonical(inside))
    right=w[len(w)//2+1:]
    registered=[]
    for j in range(2,len(right)//16+1):
        actual=send(j)
        endings=factors(right,actual)
        if endings and not factors(inside,actual) and factors(outside,actual):
            registered.append(j)
    return registered


def shortest_port_routes(g):
    internal=[x for x in g if not x.startswith(('S','R'))]
    return sorted(map(tuple,nx.all_shortest_paths(g.subgraph(internal),'a','b')))


def prefix_next(pattern):
    """KMP transitions for a single orientation of a specific escaped packet."""
    alphabet=set(pattern)
    table={};m=len(pattern)
    for i in range(m):
        for symbol in alphabet:
            candidate=pattern[:i]+(symbol,)
            for k in range(min(m,i+1),-1,-1):
                if not k or candidate[-k:]==pattern[:k]:
                    table[i,symbol]=k;break
    return table


def exact_rights(g,target):
    """Breadth-first search of the labelled nonretracing intake with both target orientations."""
    m=len(target); forward=prefix_next(target);reverse=prefix_next(target[::-1])
    start=('Rb2','a',0,0)
    todo=deque([start]);length={start:3};predecessors=defaultdict(list)
    final=[];best=None
    while todo:
        cur=todo.popleft()
        previous,last,f,r=cur;k=length[cur]
        if best is not None and k>=best: continue
        for v in sorted(g[last]):
            if v==previous or v.startswith('R'):continue
            n=(last,v,forward.get((f,v),0),reverse.get((r,v),0))
            if n not in length:
                length[n]=k+1
                if m in n[2:]:
                    best=k+1;final.append(n)
                else:
                    todo.append(n)
            if length[n]==k+1: predecessors[n].append(cur)
    def unwind(state):
        if state==start:
            yield ('Rt','Rb2','a')
        else:
            for parent in predecessors[state]:
                for p in unwind(parent):
                    yield p+(state[1],)
    paths={path for state in final for path in unwind(state)}
    assert paths and all(len(p)==best for p in paths)
    return sorted(paths),len(length)


def legal_word(g,w):
    return all(g.has_edge(a,b) for a,b in pairwise(w)) and all(w[i]!=w[i+2] for i in range(len(w)-2))


def window(g,word):
    assert legal_word(g,word)
    if len(word)>1: assert canonical(word[:-1])!=canonical(word[1:])
    return {'originals':word,'actual_parent_windows':[(0,len(word)-1),(1,len(word))] if len(word)>1 else [],
            'fresh':2+sum(g.degree(x)-2 for x in word)}


def c_blocks(w):
    result=[];start=None
    for i,x in enumerate((*w,'STOP')):
        if x.startswith('c') and start is None:start=i
        if not x.startswith('c') and start is not None:
            result.append((start,i));start=None
    return result


def ancestry_chain(w,start,stop):
    """An inclusive route of exact ordinary endpoint-deletion parents down to the chosen subword."""
    left_index,right_index=0,len(w);line=[(left_index,right_index)]
    while left_index<start:
        left_index+=1;line.append((left_index,right_index))
    while right_index>stop:
        right_index-=1;line.append((left_index,right_index))
    assert all((a,b)==(c+1,d) or (a,b)==(c,d-1) for (c,d),(a,b) in pairwise(line))
    assert tuple(w[start:stop])==tuple(w[line[-1][0]:line[-1][1]])
    return line


def receiver_history(g,w,m):
    """Follow the unique internal true parent backwards and evaluate the physical endpoints."""
    start=0;stop=len(w);history=[];ticks=[];launch=None
    while stop>start:
        x=w[start:stop];size=len(x)
        assert orientation(x)==x and legal_word(g,x)
        turn=size%2==0 and x[0]=='Rb0'
        if turn:ticks.append(size)
        if size==m:launch=x
        history.append((start,stop,turn))
        if size==1:
            assert x==('Rb1',);break
        parents=(x[:-1],x[1:])
        actual=[y for y in parents if orientation(y) is not None]
        assert len(actual)==1 and canonical(parents[0])!=canonical(parents[1])
        if size%2==0:
            assert actual[0]==x[1:];start+=1
        else:
            assert actual[0]==x[:-1];stop-=1
    ticks.sort()
    assert launch is not None and ticks==list(range(24,len(w)+1,24))
    return launch,history,ticks


def common_match(x,y):
    """All-site overlap of rooted words up to reversal; independent of the passage formula."""
    best=(0,0,0,1)
    for direction,v in [(1,y),(-1,y[::-1])]:
        prev=[0]*(len(v)+1)
        for i,a in enumerate(x):
            curr=[0]*(len(v)+1)
            for j,b in enumerate(v):
                if a==b:
                    cur=prev[j]+1;curr[j+1]=cur
                    if cur>best[0]:best=(cur,i-cur+1,j-cur+1,direction)
            prev=curr
    return best


def hull(g,x,y):
    """An actual minimum connected hull of lifts of these two specified straight holdings."""
    m=len(x);assert m==len(y)
    overlap,i,j,direction=common_match(x,y)
    second=y if direction==1 else y[::-1]
    nodes=list(x);edges=list(pairwise(range(m)));xids=list(range(m));yids=[None]*m
    if overlap:
        for k in range(overlap):yids[j+k]=i+k
        for k in range(m):
            if yids[k] is None:yids[k]=len(nodes);nodes.append(second[k])
        edges+=list(pairwise(yids));native_dist=0
    else:
        route=min((tuple(nx.shortest_path(g,a,b)) for a in set(x) for b in set(y)),key=lambda routes:(len(routes),routes))
        native_dist=len(route)-1
        i=x.index(route[0]);j=second.index(route[-1])
        middle=[i]
        for type_name in route[1:-1]:middle.append(len(nodes));nodes.append(type_name)
        yids=list(range(len(nodes),len(nodes)+m));nodes+=list(second)
        edges+=list(pairwise(yids))+list(pairwise(middle+[yids[j]]))
    tree=nx.Graph();tree.add_nodes_from(range(len(nodes)));tree.add_edges_from(edges)
    assert nx.is_tree(tree) and all(g.has_edge(nodes[a],nodes[b]) for a,b in tree.edges)
    for u in tree:
        assert len({nodes[v] for v in tree[u]})==tree.degree(u)
    def prune(retained):
        t=tree.copy();del_order=[]
        while len(t)>len(retained):
            v=next(v for v in t if t.degree(v)==1 and v not in retained)
            del_order.append(v);t.remove_node(v)
        assert set(t)==set(retained)
        return del_order
    return {'types':nodes,'ordinary_meetings':sorted(tuple(sorted(x)) for x in tree.edges),
            'sender_vertices':yids,'receiver_vertices':xids,'prune_to_sender':prune(yids),'prune_to_receiver':prune(xids),
            'all_parent_removed_vertices':[v for v in tree if tree.degree(v)==1],
            'shared_word':overlap,'holder_gap':native_dist,'inclusive_lag':len(nodes)-m,
            'fresh':2+sum(g.degree(v)-2 for v in nodes)}


def receiver_certificate(g,right,target):
    m=len(target);j=m//16;k=len(right)
    word=left(k)+('Rb1',)+right
    assert len(word)==2*k+1 and len(word)<=4096
    inside,outside=word[:-1],word[1:]
    cell=window(g,word);pi=window(g,inside);po=window(g,outside)
    assert orientation(inside)==inside and orientation(outside) is None
    assert j in intrinsic_decodes(word,[inside,outside])
    assert j in intrinsic_decodes(word[::-1],[outside[::-1],inside[::-1]])
    assert j not in intrinsic_decodes(inside,[inside[:-1],inside[1:]])
    assert j not in intrinsic_decodes(word,[inside]) and j not in intrinsic_decodes(word,[inside,outside,inside])
    launch,internal,ticks=receiver_history(g,word,m)
    locations=factors(outside,target)
    assert len(locations)==1 and locations[0]+m==len(outside)
    path=ancestry_chain(outside,locations[0],len(outside))
    # A real same-arity, same-price member with Sb0 in place of both Sb1 occurrences.
    sham=tuple('Sb0' if x=='Sb1' else x for x in word)
    sham_p=(sham[:-1],sham[1:])
    assert intrinsic_decodes(sham,sham_p)==[] and orientation(sham)==sham
    assert all(window(g,x)['fresh']==window(g,y)['fresh'] for x,y in zip((word,inside,outside),(sham,*sham_p),strict=True))
    blocks=c_blocks(outside);longest=max((b-a for a,b in blocks),default=0)
    third=[(a,a+m) for i,jj in blocks for a in range(i,jj-m+1)]
    return {'member':cell,'continuing_input':pi,'incoming_input':po,'intrinsic_decoded_emissions':intrinsic_decodes(word,[inside,outside]),
            'parent_input_name_policy':'distinct charged old private slot of each listed physical parent, up to private-slot bijections',
            'physical_sham':{'member':window(g,sham),'parents':[window(g,y) for y in sham_p],'decoded':intrinsic_decodes(sham,sham_p)},
            'actual_receiver_chain_intervals_and_ticks':internal,'tick_sizes':ticks,'ticks_since_origin':len(ticks),
            'ticks_since_receiver_launch_anchor':sum(t>m for t in ticks),'launch_anchor':launch,
            'receiver_launch_half_lengths':(len(launch)//2,(len(launch)-1)//2),
            'incoming_to_send':path,'incoming_c_blocks':blocks,'longest_c_word':longest,
            'sending_cut_c_ancestor_windows':third,'incoming_to_one_c_member':ancestry_chain(outside,*third[0]) if third else [],
            'inclusive_hull_from_this_launch_member':hull(g,launch,target)}


def case(arm,d,send_sizes):
    g=layout(arm,d);routes=shortest_port_routes(g)
    portals=len(routes[0])-1;gap=portals+5
    c_nodes=[x for x in g if x.startswith('c')]
    core=g.subgraph(c_nodes)
    persists=bool(c_nodes) and all(core.degree(x)==2 for x in c_nodes)
    if c_nodes and not persists:assert nx.is_tree(core) and max(dict(core.degree).values())<=2
    rows=[]
    for m in send_sizes:
        target=send(m//16);assert window(g,target) and target[:2]==('Ss','Sb1') and target[-1]=='Sv'
        right,explored=exact_rights(g,target)
        expected=sorted(('Rt','Rb2')+p+('Sb2',)+target for p in routes)
        assert right==expected
        certs=[receiver_certificate(g,r,target) for r in right]
        lag=min(m+1,m+gap-(m-1)//2-1)
        assert all(c['inclusive_hull_from_this_launch_member']['inclusive_lag']==lag for c in certs)
        n=len(certs[0]['member']['originals'])
        assert n==2*(gap+m-1)+1
        rows.append({'send_size':m,'true_phase':window(g,target),'strict_registration_size':n,'strict_delay':n-m,
                     'intake_length_to_first_send_endpoint':gap,'registering_members':len(right),
                     'all_minimizing_port_routes':routes,'search_states':explored,'inclusive_launch_separation':lag,
                     'inclusive_receipt_size':m+lag,'third_persistent':persists,
                     'third_exists_at_launch':persists or len(core)>=m,
                     'third_exists_at_receipt':persists or len(core)>=n,
                     'some_sending_cut_third_in_intake':any(c['sending_cut_c_ancestor_windows'] for c in certs),
                     'every_sending_cut_third_in_intake':all(c['sending_cut_c_ancestor_windows'] for c in certs),
                     'certificates':certs})
    return {'variant':arm,'d':d,'candidate_pairs':sorted(sorted(e) for e in g.edges),
            'ordinary_live_degrees':dict(sorted(g.degree)),'c_release':{'present':bool(core),'infinite':persists,
            'maximum_size_if_finite':None if persists else len(c_nodes)},'laws':['parity','not-all-equal'],'sends':rows}


def legacy_controls():
    source=ROOT/'experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B-E001_receivers'
    sys.path.insert(0,str(source))
    import receivers
    original=layout('absent',32)
    one=nx.relabel_nodes(original.subgraph([v for v in original if v.startswith('S')]),
                         {v:'A'+v[1:] for v in original if v.startswith('S')},copy=True)
    assert len(one)==9 and one.number_of_edges()==12
    full=layout('active',32)
    result=[]
    for m in (32,48,64,80):
        w=receivers.centred(4,1,m,'A')
        hits=receivers.admission(one,w,4,1,m//2)
        assert hits==receivers.receiver_read(one,w,'Ab1')
        assert sorted(h['parents_in_union'] for h in hits)==[2,3]
        straight=w+('Ab1',)
        straight_parents=(w,w[1:]+('Ab1',))
        assert set(map(canonical,straight_parents))=={canonical(straight[:-1]),canonical(straight[1:])}
        fork={'base':w[1:],'two_new_leaves_at_start':(w[0],'Ab1')}
        fork_parents=[w,('Ab1',)+w[1:],{'base':w[1:-1],'two_new_leaves_at_start':(w[0],'Ab1')}]
        assert intrinsic_decodes(fork,fork_parents)==[]
        assert receivers.word_on_clock(straight_parents[1],4,1,m//2)
        assert receivers.word_on_clock(fork_parents[1],4,1,m//2) or receivers.word_on_clock(fork_parents[1][::-1],4,1,m//2)
        root_only=tuple('R'+x[1:] for x in receivers.centred(4,2,m,'A'))
        # Enumerate every straight phase that could share ANY true child with this R-only member.
        candidates=list(receivers.adjacent_outside_phases(full,root_only))
        strict=sum(bool(factors(v,send(m//16))) for v,_ in candidates)
        assert not strict
        neutral,marked=base('R');pure=(neutral*2+marked[0])*(m//12+1)
        pure=pure[:m]
        assert legal_word(full,pure) and not factors(pure,send(m//16))
        turns=[k for k in range(2,m+2,2) if receivers.centred(4,1,k,'A')[0]=='Ab0']
        assert turns==list(range(16,m+2,16))
        result.append({'send':m,'archive':'one original 21-holder frame, choose all Q8 packet phases',
             'direct_straight':window(one,straight),'its_two_exact_input_words':straight_parents,
             'three_parent_fork':fork,'all_fork_input_records':fork_parents,'own_output_parent_multiplicities':[2,3],
             'addressed_hits':len(hits),'standalone_turns':turns,'new_strict_reader_on_actual_fork':[],
             'R_only_centered_member':root_only,'R_only_output_candidates_tested':len(candidates),'specified_S_phase_in_R_only_outputs':strict,
             'pure_R_all_neutral_interval':window(full,pure),'S_phase_in_that_member':False})
    return result


def main():
    arms=[(a,32,(32,48,64,80)) for a in PRIMARY]
    arms += [(a,d,(32,48,64)) for d in (8,20,44) for a in ('active','short')]
    result={'preparations':[case(*arm) for arm in arms],'archived_direct_outputs':legacy_controls()}
    raw=(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode()
    OUT.mkdir(exist_ok=True,parents=True);out=OUT/'registered.json.gz'
    out.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
    print(len(arms),'physical preparations;',sum(len(c['sends']) for c in result['preparations']),
          'matched sends;',out.stat().st_size,'compressed bytes;',hashlib.sha256(out.read_bytes()).hexdigest())


if __name__=='__main__': main()
