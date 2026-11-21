"""Present holdings, first releases, and inclusive and strict clock reception."""
from collections import Counter, defaultdict
from itertools import product, combinations
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import sys

import networkx as nx
from scipy.stats import beta

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DEFAULT=ROOT/'artifacts'/HERE.parent.name/HERE.name
PAST=next((ROOT/'experiments/READS-HOLDERS-SOURCES-20261120-001C').iterdir())
sys.path.insert(0,str(PAST))
import survey as previous
import verify as previous_verify
GEN=next((ROOT/'experiments/GENERATORS-20261120-001A').iterdir())
sys.path.insert(0,str(GEN))
import periodic as recorded
fix,end=previous.fix,previous.end
LAWS=('parity','nae')


def cycle_words(neutral_length):
    neutral=('v',)+tuple('r'+str(i) for i in range(1,neutral_length))
    marked=[('v','s','b'+str(i),'t') for i in range(3)]
    return neutral,marked


def physical_frame(length,rng=None):
    neutral,marked=cycle_words(length)
    arcs=list(zip(neutral,neutral[1:]+neutral[:1])) + [('v','s'),('t','v'),('s','b0'),('t','b0'),('s','b1'),('b1','t'),('t','b2'),('b2','s')]
    names=sorted(set(v for pair in arcs for v in pair)|{'w'+str(i) for i in range(len(arcs))})
    ids={v:i for i,v in enumerate(names)}
    pairs=[]; loose=[0]*len(names); multiples=[]
    for i,(tail,head) in enumerate(arcs):
        w=ids['w'+str(i)]; k=2+(rng.randrange(2) if rng else 0);multiples.append(k)
        pairs.append((ids[tail],w)); pairs.extend([(ids[head],w)]*k)
        loose[ids[tail]]+=1;loose[ids[head]]+=1
    stars=fix.source_from(pairs,loose)
    return names,stars,multiples


def decode_frame(stars):
    """Find physical original directions and labeled dispositions without a supplied order."""
    owners=defaultdict(list)
    for v,star in enumerate(stars):
        for bit in star:owners[bit].append(v)
    weights=Counter(tuple(sorted(vs)) for vs in owners.values() if len(vs)==2)
    orig={v for pair,k in weights.items() if k>=2 for v in pair}
    graph=nx.Graph();graph.add_nodes_from(orig)
    graph.add_weighted_edges_from((v,w,k) for (v,w),k in weights.items() if v in orig and w in orig)
    live={v for v in orig if len(stars[v])>sum(graph[v][w]['weight'] for w in graph[v])}
    arrows=nx.DiGraph(); arrows.add_nodes_from(live)
    for w in orig-live:
        assert len(graph[w])==2
        tail,head=sorted(graph[w], key=lambda v:graph[w][v]['weight'])
        assert graph[w][tail]['weight']==1<graph[w][head]['weight']
        arrows.add_edge(tail,head)
    ordinary=arrows.to_undirected()
    forks={p for p in live if ordinary.degree(p)==4}
    v,= [p for p in forks if len(forks.intersection(ordinary[p]))==2]
    s,=forks.intersection(arrows.successors(v)); t,=forks.intersection(arrows.predecessors(v))
    shared=set(ordinary[s])&set(ordinary[t])-{v}
    b0,=[b for b in shared if arrows.has_edge(s,b) and arrows.has_edge(t,b)]
    b1,=[b for b in shared if arrows.has_edge(s,b) and arrows.has_edge(b,t)]
    b2,=shared-{b0,b1}
    path=[v]; r,=set(arrows.successors(v))-{s}
    while r!=v:
        path.append(r);r,=arrows.successors(r)
    return {'orig':orig,'all_live':live,'neutral':path,'marked':[[v,s,b,t] for b in (b0,b1,b2)]}


def frame_check(length,stars,names,deep=False):
    reader=decode_frame(stars)
    neutral,marked=cycle_words(length)
    assert [names[x] for x in reader['neutral']]==list(neutral)
    assert [[names[x] for x in w] for w in reader['marked']]==list(map(list,marked))
    current=end.from_stars(stars); roster=end.proposals(current)
    assert all(len(g)==2 for g in roster) and Counter(v for g in roster for v in g)==Counter(current.opens)
    rec={'star_count':len(stars),'distinctions':len(set(d for s in stars for d in s)),
         'original_directed_arcs':len(roster),'neutral':reader['neutral'],'marked':reader['marked']}
    if deep:
        rng=random.Random(20261120425)
        patterns=[tuple(reader['neutral']*n+reader['marked'][i]) for n in (1,2,3) for i in (0,1)]
        per_law={}
        for law in LAWS:
            fix.certify_source(stars,law)
            frames,layers=fix.trajectory(stars,law,3)
            for cut,frame in enumerate(frames):
                rr=decode_frame(frame)
                assert rr==reader
                perm=list(range(len(frame)));rng.shuffle(perm)
                bits=sorted({d for s in frame for d in s}); bits2=bits[:];rng.shuffle(bits2);dt=dict(zip(bits,bits2)); recoded=[None]*len(frame)
                for i,s in enumerate(frame):recoded[perm[i]]=tuple(dt[d] for d in s)
                rp=decode_frame(recoded)
                assert rp['neutral']==[perm[v] for v in rr['neutral']]
                assert rp['marked']==[[perm[v] for v in w] for w in rr['marked']]
            ids={(v,):v for p in patterns for v in p}
            examined=[]
            for size,(cohort,_) in enumerate(layers,2):
                by={frozenset(b.parents):b.knot for b in cohort if len(b.parents)==2}
                words={w for p in patterns for w in windows(p,size)}
                ids={w:by[frozenset((ids[w[:-1]], ids[w[1:]]))] for w in words}
                assert len(set(ids.values()))==len({min(w,w[::-1]) for w in words})
                examined.append({'physical_births':len(cohort),'word_prefixes':len(words)})
            per_law[law]=examined
        rec['literal_replay']=per_law
    return rec


def windows(word,size):
    long=word*(2+(size//len(word)))
    return [long[i:i+size] for i in range(len(word))]


def source(word):
    return recorded.compact_source(word)


def receipt(word):
    p=len(word); numbers=[]
    for size in (2*p-1,2*p,2*p+1):
        phases=windows(word,size)
        expected={min(w,w[::-1]) for w in windows(word,size-1)}
        assert all(min(w[:-1],w[:-1][::-1]) in expected and min(w[1:],w[1:][::-1]) in expected and min(w[:-1],w[:-1][::-1])!=min(w[1:],w[1:][::-1]) for w in phases)
        numbers.append([sum(map(source,phases)),len({min(w,w[::-1]) for w in phases})])
    return numbers


def binary_event_control():
    a,ps=cycle_words(4); u=[a+ps[i] for i in (0,1)]
    result=[]
    for q in range(2,8):
        events=[]
        for z in product((0,1),repeat=q):
            rot=[z[i:]+z[:i] for i in range(q)]
            if z!=min(rot) or len(set(rot))<q or len(set(z))<2: continue
            seq=sum((u[i] for i in z),()); p=len(seq)
            # A positive orientation is physically distinguishable. A reversed word
            # is the same unoriented path, never another forward word in this alphabet.
            assert all(w[:p]==w[p:] for w in windows(seq,2*p))
            ok=sum(map(source,windows(seq,2*p-1)))
            events.append({'blocks':''.join(map(str,z)),'length':p,'source_parents':ok,'phase_count':p,
                           'named_clock':sum(z)==1,'all_parents_in_source':ok==p})
        result.append(events)
    return result


def language_parts(n,subsize):
    """Superset of Q words including all consecutive binary choices, without exclusion."""
    a,p=cycle_words(4); u=[a*n+p[i] for i in (0,1)]
    span=2+subsize//len(u[0]);out=set()
    for types in product((0,1),repeat=span):
        seq=sum((u[i] for i in types),())
        for j in range(len(u[0])):
            z=seq[j:j+subsize];out.add(z);out.add(z[::-1])
    return out


def counts(t,s):
    return max(0,(t+1)//(2*s)-1)


def inclusive(n,r,ell):
    a,p=cycle_words(4); su=[a*n+p[i] for i in (0,1)];ru=[a*r+p[i] for i in (0,1)]
    s,h=len(su[0]),len(ru[0]); w=su[0]*ell+su[1]; m=2*len(w); age=m-1
    L=8*min(n,r)+5
    if m>=2*h:
        assert not (set(windows(w,L+1)) & language_parts(r,L+1))
        ys=windows(ru[0],m); prefixes={y[:L]:y for y in ys}
        x=next(x for x in windows(w,m) if x[-L:] in prefixes); y=prefixes[x[-L:]]
        assert x[-L:]==y[:L] and source(y) and not source(x)
        joint=x+y[L:]
        # Actual straight witness. End deletions are respectively descendants of the
        # sender and receiver at the very first depth at which both can contribute.
        assert all(joint[i]!=joint[i+2] for i in range(len(joint)-2))
        assert joint[:-1][:m]==x and joint[1:][-m:]==y
        assert len(joint)==2*m-L
        return {'ell':ell,'send_age':age,'separation':m-L,'longest_common':L,
                'shared_word':x[-L:],'joint_birth_age':len(joint)-1,'receiver_count_at_joint':counts(len(joint)-1,h),
                'strict_received':False,'straight_witness_sha256':hashlib.sha256(' '.join(joint).encode()).hexdigest(),
                'neighbor_phases':[x[-L-1],y[L]],'separation_after_h':[max(m-L-j,0) for j in (0,1,m-L-1,m-L,m-L+1)]}
    raise AssertionError('Receiver has not released')


def deterministic():
    a,p=cycle_words(4)
    names,stars,_=physical_frame(4)
    literal=frame_check(4,stars,names,True)
    # Test a new physical sharing away from either selected return. Original degrees
    # and directions are unchanged. Also compare a longer neutral return in the same design.
    matching=[list(s) for s in stars]; who=names.index('b2'); wit=names.index('w10'); shared=set(stars[who])&set(stars[wit]);assert len(shared)==2
    bit=1+max(v for star in stars for v in star);matching[who].append(bit);matching[wit].append(bit)
    alt=frame_check(4,tuple(map(tuple,matching)),names,True)
    other,extended,_=physical_frame(5); new=frame_check(5,extended,other,True)
    # The witnessed end erases all original directions. Exchanging b0 and b1
    # preserves every current witness and loose supply and exchanges the specified read.
    b0,b1=(names.index(name) for name in ('b0','b1'))
    z=end.from_stars(stars); sw=lambda v:b1 if v==b0 else b0 if v==b1 else v
    assert {frozenset(map(sw,q)) for q in z.blocks}==set(map(frozenset,z.blocks)) and all(z.opens[v]==z.opens[sw(v)] for v in z.opens)
    phase_checks=[]
    for n in (1,2,3):
        u0=a*n+p[0];u1=a*n+p[1]
        for ell in range(1,9):
            w=u0*ell+u1
            if 2*len(w)>129:break
            rc=receipt(w);assert rc==[[len(w),len(w)],[0,len(w)],[0,len(w)]]
            phase_checks.append({'n':n,'ell':ell,'period':len(w),'age':2*len(w)-1,'source_members_and_phases':rc})
    sent={f'{n}-{r}':[inclusive(n,r,i) for i in (*range(1,13),128)] for n,r in ((1,2),(2,1),(2,3),(3,2))}
    readout=[[t,counts(t,8),counts(t,12),counts(t,16)] for t in range(4097)]
    for t,c,d,h in readout[47:-48]:assert readout[t+48][1:3]==[c+3,d+2]
    for n,r in ((1,2),(2,1),(2,3),(3,2)):
        for j in sent[f'{n}-{r}']:assert j['joint_birth_age']==2*j['send_age']+1-j['longest_common']
    return {'native_frame_baseline':literal,'extra_held_distinction':alt,'longer_neutral_return':new,'physical_symbolic_checks':phase_checks,
            'inclusive_arrivals':sent,'binary_completion_sensitivity':binary_event_control(),'counts_by_age':readout,
            'originals':stars,'original_name_key':names,'end_permutation':{'exchanges':[b0,b1],'preserves_growing_end':True}}


def general_events(row,law):
    part=row['laws'][law];pieces=part['parts']
    clocks=[]
    for pc in pieces:
        for c in pc['structural_candidates']:
            if not c['readable']:continue
            for pair in c['pairs']:
                a,b=pair['a'],pair['b']; period=2*len(a); first=c['age']+period+2*len(b)-1
                clocks.append((period,first))
    asserted=any(p['positive'] for p in pieces); assert bool(clocks)==asserted
    unknown=any(not p['bounded'] and not p['positive'] for p in pieces)
    return {'legal':part['legal'],'funded':part['funded'],'proved':asserted,'possible':asserted or unknown,
            'first_by32':any(t<=32 for _,t in clocks),'two_by32':any(t+d<=32 for d,t in clocks),
            'clock_periods':sorted({d for d,_ in clocks}),'distinct_certificates':sorted(set(clocks)),
            'two_unequal':len({d for d,_ in clocks})>=2}


def general_draws():
    rng=random.Random(20261120421);missing_rng=random.Random(20261120422)
    for i in range(128):
        n=rng.randint(9,12);seq=[rng.randrange(n) for _ in range(n-2)];g=nx.from_prufer_sequence(seq)
        coins=[int(rng.randrange(4)==0) for _ in range(n)]; missing=[p for p in combinations(range(n),2) if not g.has_edge(*p)]; missing_rng.shuffle(missing)
        for k in (2,3):
            pairs=sorted({tuple(sorted(e)) for e in g.edges()}|set(missing[:k]));data={'size_group':'9-12','n':n,'draw':i,'word':seq,'coins':coins,'extra':k,'extra_meetings':missing[:k],'edges':pairs}
            for supply in ('original','funded_sensitivity'):
                row=previous.source(dict(data,supply=supply)); rules={law:general_events(row,law) for law in LAWS}
                yield {'weighting':f'{supply}_plus{k}','source':row,'observations':rules}


def special_draws():
    gen=random.Random(20261120423)
    for i in range(64):
        length=gen.randint(4,8);names,stars,decorations=physical_frame(length,gen);physical=frame_check(length,stars,names,i==0)
        # Projection at every actual original: in the factored proof each spent
        # witness can be completed from its other endpoint. All live knots have
        # two private places unless pinned. Certify the finite columns directly.
        for law in LAWS:fix.certify_source(stars,law)
        first,second=2*(length+4),2*(2*length+4)
        item={'legal':True,'funded':True,'proved':True,'possible':True,'clock_periods':[first,second],
              'first_by32':2*first-1<=32,'two_by32':3*first-1<=32,'two_unequal':True}
        yield {'weighting':'nested_physical_frames','draw':i,'neutral_length':length,'head_multiplicities':decorations,
               'source':stars,'sample_proof':physical,'observations':{law:item for law in LAWS}}
    gen=random.Random(20261120424)
    paired=[p for p in combinations(range(6),2) if p[0]//2!=p[1]//2]
    for i in range(64):
        orientations=[gen.randrange(2) for _ in paired];meetings=[]
        for j,((v,w),which) in enumerate(zip(paired,orientations)):
            witness=6+j
            if which:v,w=w,v
            meetings.extend([(v,witness),(w,witness),(w,witness)])
        stars=fix.source_from(meetings,[4]*6+[0]*len(paired));state=end.from_stars(stars)
        groups=end.proposals(state);actual=set(groups)
        expected={tuple(choice) for choice in product((0,1),(2,3),(4,5))};assert actual==expected
        per_law={}
        for law in LAWS:
            fix.certify_source(stars,law)
            _,new,_=fix.literal_turn(stars,law); assert {tuple(b.parents) for b in new}==expected
            per_law[law]={'legal':True,'funded':True,'proved':False,'possible':False,'clock_periods':[],
                          'first_by32':False,'two_by32':False,'two_unequal':False}
        yield {'weighting':'partnered_runaway','draw':i,'orientations':orientations,'source':stars,
               'first_true_groups':sorted(actual),'observations':per_law}


def exact(a,n):
    if n==0:return None
    return [0 if a==0 else float(beta.ppf(.025,a,n-a+1)),1 if a==n else float(beta.ppf(.975,a+1,n-a))]


def summarize(records):
    out=[]
    for key in sorted({r['weighting'] for r in records}):
        for law in LAWS:
            for den in ('all','legal','funded'):
                rows=[r['observations'][law] for r in records if r['weighting']==key and (den=='all' or r['observations'][law][den])]
                c={}
                for event in ('legal','funded','proved','first_by32','two_by32','two_unequal'):
                    k=sum(r[event] for r in rows); c[event]={'count':k,'exact95':exact(k,len(rows))}
                k=sum(r['proved'] for r in rows); z=sum(r['possible'] for r in rows); a=len(rows)
                limits=None if not a else [exact(k,a)[0],exact(z,a)[1]]
                two=sum(r['two_unequal'] for r in rows)
                out.append({'weighting':key,'law':law,'denominator':den,'n':a,'events':c,'observable_periods':dict(sorted(Counter(x for r in rows for x in r['clock_periods']).items())),
                            'recurring_release_existence':{'proved':k,'unresolved':z-k,'excluded':a-z,'count_interval':[k,z],'outer_exact95':limits},
                            'two_unequal_clock_existence':{'proved':two,'unresolved':z-two,'excluded':a-z,'count_interval':[two,z],
                              'outer_exact95':None if not a else [exact(two,a)[0],exact(z,a)[1]]},
                            'zero_detection_one_sided95':1-.05**(1/a) if a and k==0 else None})
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,default=DEFAULT);args=parser.parse_args()
    d=args.output_dir;d.mkdir(parents=True,exist_ok=True)
    result=deterministic()
    records=list(general_draws());records.extend(special_draws())
    witnesses=[]
    for row in records:
        if not row['weighting'].endswith(('plus2','plus3')) or not row['observations']['parity']['proved']:
            continue
        source=row['source']
        witnesses.append({'weighting':row['weighting'],'draw':source['draw'],'physical_start':previous_verify.certificate(source)})
    result['fresh_unbuilt_clock_certificates']=witnesses
    (d/'clocks.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
    with (d/'draws.jsonl').open('w') as f:
        for row in records:print(json.dumps(row,separators=(',',':')),file=f)
    (d/'rates.json').write_text(json.dumps(summarize(records),indent=1)+'\n')
    print('starts',len(records),'holdings verified at both laws. Count rows',len(result['counts_by_age']))


if __name__=='__main__':main()
