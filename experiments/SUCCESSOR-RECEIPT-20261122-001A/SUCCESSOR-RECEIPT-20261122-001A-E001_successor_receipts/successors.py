"""Exact single-successor records, with shared contributing parents counted once."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
B307='HIDDEN-SENDER-MARKS-20261122-001A'
OLD=ROOT/'artifacts'/B307/(B307+'-E001_hidden_sends')
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
sys.path.append(str(ROOT/'experiments'/B307/(B307+'-E001_hidden_sends')))
from projection import Frame, lawful, fresh_words, mask, bits, setbank
from growth import load, original_values

RECEIVER=294
SUCC=(631,633,634)
SEND=(510,563)
VIEWS=('fresh','anonymous','calibrated')


def encode(obj):
    return (json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()


def write_gz(file,obj):
    file.write_bytes(gzip.compress(encode(obj),compresslevel=9,mtime=0))


def view(which,wi,u,v):
    if which=='fresh':return v
    incoming=wi+u
    if which=='anonymous':incoming=''.join(sorted(incoming))
    return incoming+'/'+v


def resolution(table):
    total=sum((sum(values.values(),Fraction()) for values in table.values()),Fraction())
    if not total:return {'available':False}
    prior=Counter()
    for v in table.values():prior.update(v)
    identified=sum(sum(v.values()) for v in table.values() if len(v)==1)
    return {'available':True,'records':len(table),'certain_records':sum(len(v)==1 for v in table.values()),
            'distinct_truth_per_record':{str(k):v for k,v in sorted(Counter(len(v) for v in table.values()).items())},
            'certain_mass':str(identified/total),'best_accuracy':str(sum(max(v.values()) for v in table.values())/total),
            'best_prior':str(max(prior.values())/total),'mass':str(total),
            'certainty_all':all(len(v)==1 for v in table.values())}


class Branch:
    def __init__(self,frame,h,old):
        self.frame,self.h,self.old=frame,h,old
        self.r=frame.births[RECEIVER];self.b=frame.births[h]
        self.pos=SUCC.index(h)
        p_index=self.b['parents'].index(RECEIVER)
        self.p=frame.births[self.b['parents'][1-p_index]]
        self.rbit=self.b['consumed_names'][p_index]
        self.pbit=self.b['consumed_names'][1-p_index]
        assert self.rbit==self.r['fresh_names'][self.pos]
        self.qix=self.p['fresh_names'].index(self.pbit)
        self.affected=[b['holder'] for b in frame.cuts[0] if set(b['consumed_names']) & set(SEND)]
        self.first=sorted(set(self.r['parents'])|set(self.p['parents'])|set(self.affected))
        self.input_slots={}
        for b in (self.r,self.p):
            self.input_slots[b['holder']]=[(i,frame.births[i]['fresh_names'].index(d)) for i,d in
                                           zip(b['parents'],b['consumed_names'],strict=True)]

    def factors(self):
        law=self.frame.law
        options=[self.frame.options(h,self.old) for h in self.first]
        nalloc=1
        for v in options:nalloc*=len(v)
        types=Counter(); representatives={}
        for choice in product(*options):
            a=dict(zip(self.first,choice,strict=True))
            p,q=( ''.join(a[k][j] for k,j in self.input_slots[h]) for h in (RECEIVER,self.p['holder']))
            ok=all(lawful(2+self.frame.births[h]['grant'],bits(self.old^mask(SEND),self.frame.births[h]['consumed_names']).count('1')+a[h].count('1'),law) for h in self.affected)
            types[ok,p,q]+=1
            representatives.setdefault((ok,p,q),a)
        dist=Counter(); witnesses={}
        for (ok,p,q),n in types.items():
            r_opts=fresh_words(law,p,self.r['grant']); q_opts=fresh_words(law,q,self.p['grant'])
            for w in r_opts:
                wi=w[self.pos]
                for u, multiplicity in sorted(Counter(y[self.qix] for y in q_opts).items()):
                    h_opts=fresh_words(law,wi+u,self.b['grant'])
                    mass=Fraction(n*multiplicity,nalloc*len(r_opts)*len(q_opts)*len(h_opts))
                    for fresh in h_opts:
                        code=(ok,w,u,fresh);dist[code]+=mass
                        witnesses.setdefault(code,representatives[ok,p,q] | {RECEIVER:w,self.p['holder']:next(y for y in q_opts if y[self.qix]==u), self.h:fresh})
        assert sum(dist.values())==1
        return dist,witnesses


def metric_tables(both,pos,operation):
    tables={v:{key:defaultdict(Counter) for key in ('W','paid_bit','early_action','late_request','late_moved','bit_and_late','W_and_late')} for v in VIEWS}
    conditional={}; raw=Counter()
    for early,d in enumerate(both):
        for (can,w,u,fresh),value in d.items():
            wi=w[pos]
            for req in (0,1):
                realized='I' if req==0 else ('M' if operation=='pointwise' and can else 'U')
                raw[(early,req,realized,w,u,fresh)]+=value/4
                group=(early,req,realized)
                if group not in conditional:
                    conditional[group]={v:{k:defaultdict(Counter) for k in ('W','paid_bit')} for v in VIEWS}
                for v in VIEWS:
                    rec=view(v,wi,u,fresh)
                    vals=(w,wi,str(early),str(req),'M' if realized=='M' else 'no-move',wi+('/M' if realized=='M' else '/no-move'),w+('/M' if realized=='M' else '/no-move'))
                    for key, truth in zip(tables[v],vals,strict=True):tables[v][key][rec][truth]+=value/4
                    conditional[group][v]['W'][rec][w]+=value/4
                    conditional[group][v]['paid_bit'][rec][wi]+=value/4
    assert sum(raw.values())==1
    tiny={v:{k:resolution(mapping) for k,mapping in content.items()} for v,content in tables.items()}
    cold={f'{e}-{r}-{s}':{v:{k:resolution(mapping) for k,mapping in vs.items()} for v,vs in b.items()}
          for (e,r,s),b in conditional.items()}
    # Exact complete W/bit supports conditional on both requests and the status; the full raw joint retains the weights.
    supports={}
    for key,views in conditional.items():
        sub={}
        for v,topics in views.items():
            sub[v]={obs:sorted(vals) for obs,vals in topics['W'].items()}
            assert all(set(topics['paid_bit'][obs])=={w[pos] for w in val} for obs,val in sub[v].items())
        supports['-'.join(map(str,key))]=sub
    return tiny,cold,supports


def finish_ext(frame,fourth,third_word):
    nold=1+max(max(star) for star in frame.stages[3]);out=third_word
    for row in fourth[len(frame.stages[3]):]:
        count=(out & mask(row)).bit_count()
        if not lawful(len(row),count,frame.law):
            free=next(d for d in reversed(row) if d>=nold)
            out|=1<<free
    assert all(lawful(len(row),(out & mask(row)).bit_count(),frame.law) for row in fourth)
    return out


def select_traces(branch,prob,reps):
    chosen=[]; canonical=sorted(prob)
    for ok in sorted({k[0] for k in prob}):
        cohort=[k for k in canonical if k[0]==ok]
        # A real move/refusal, followed by comparisons at identical local histories and fixed second status.
        chosen.append(('same_preoffer_skip_or_attempt',cohort[0],None))
        for look, name, differ_bit in [('calibrated','same_entire_oriented_H_distinct_W',False),('anonymous','same_anonymous_H_opposite_paid_bit',True)]:
            buckets=defaultdict(list)
            for k in cohort:
                _,w,u,v=k;buckets[view(look,w[branch.pos],u,v)].append(k)
            pair=next(((a,b) for arr in buckets.values() for a in arr for b in arr
                       if a[1]!=b[1] and (not differ_bit or a[1][branch.pos]!=b[1][branch.pos])),None)
            if pair:chosen.append((name,*pair))
        equal=next((k for k in cohort if k[1][branch.pos]==k[2]),None)
        if equal:chosen.append(('equal_incoming_tracks_witness',equal,None))
    return chosen


def witnessed(frame,fourth,branch,key,reps):
    ok,w,u,v=key
    before=frame.complete(branch.old,reps[key]);candidate=before^mask(SEND)
    try:frame.check(candidate); actually_ok=True
    except AssertionError:actually_ok=False
    assert actually_ok==ok
    later=finish_ext(frame,fourth,before)
    if ok:
        flipped=later^mask(SEND)
        assert all(lawful(len(row),(flipped & mask(row)).bit_count(),frame.law) for row in fourth)
    else:flipped=later
    h_row=frame.stages[3][branch.h]
    assert bits(before,h_row)==bits(later,h_row)==bits(flipped,h_row)
    assert bits(later,branch.r['fresh_names'])==w
    return {'W':w,'r_inheritance':w[branch.pos],'coparent_bit':u,'H_fresh':v,'H_actual':bits(before,h_row),
            'late_pointwise_admitted':ok,'third_before_late':hex(before),'after_idle_finish':hex(later),
            'after_pointwise_T_finish':hex(flipped),'background':hex(branch.old)}


def canonical_transport(stars,example,b):
    from random import Random
    rng=Random(202611220312); n=max(max(row) for row in stars)+1; ids=list(range(n));rng.shuffle(ids)
    hs=list(range(len(stars)));rng.shuffle(hs);w=int(example['after_idle_finish'],16)
    renamed=mask(ids[i] for i in range(n) if w>>i&1)
    assert bits(renamed,[ids[d] for d in b['consumed_names']])==bits(w,b['consumed_names'])
    orig=bits(w,b['consumed_names']);reverse=bits(renamed,[ids[d] for d in reversed(b['consumed_names'])]); assert ''.join(sorted(orig))==''.join(sorted(reverse))
    new=[None]*len(hs)
    for h,row in enumerate(stars):new[hs[h]]=tuple(ids[d] for d in row)
    return renamed,new


def main():
    from holders import grown
    all_factors={};metric={};scoped={};support={};traces={};geom={}
    data=load(); previous={}
    with gzip.open(OLD/'supports.json.gz','rt') as f:
        archive=json.load(f)
    for x in archive['projections']:
        if x['target']=='R' and x['side']=='00':previous[x['law'],x['route']]=x['weighted']
    for law in ('parity','nae'):
        common=mask(d for d,val in original_values(data,law).items() if val)
        for route in ('intact','interrupted','sham'):
            frame=Frame(data,route,law); fourth=grown(law,route)
            assert tuple(map(tuple,fourth[:len(frame.stages[3])]))==tuple(map(tuple,frame.stages[3]))
            for h in SUCC:
                key=f'{law}-{route}-{h}';pair=[]
                for e in (0,1):
                    branch=Branch(frame,h,common^(mask(SEND) if e else 0)); d,reps=branch.factors();pair.append(d)
                    geom[key]={'H':h,'R':RECEIVER,'other_parent':branch.p['holder'],'scorer_R_mark':branch.rbit,
                          'scorer_second_parent_mark':branch.pbit,'first_contributing_holders':branch.first,'H_fresh':branch.b['fresh_names']}
                    wk=f'{key}-{e}'
                    all_factors[wk]=[{'pointwise_ok':bool(ok),'W':w,'u':u,'H_fresh':v,'mass':str(m)} for (ok,w,u,v),m in sorted(d.items())]
                    rcheck=Counter()
                    for (_,w,_,_),mass in d.items():rcheck[w]+=mass
                    assert {w:str(x) for w,x in rcheck.items()}==previous[law,route]['swap' if e else 'idle']
                    traces[wk]=[]
                    for what,left,right in select_traces(branch,d,reps):
                        a=witnessed(frame,fourth,branch,left,reps); b=witnessed(frame,fourth,branch,right,reps) if right else None
                        if what=='same_entire_oriented_H_distinct_W':assert a['H_actual']==b['H_actual'] and a['W']!=b['W']
                        if what=='same_anonymous_H_opposite_paid_bit':
                            assert a['r_inheritance']!=b['r_inheritance'] and a['H_fresh']==b['H_fresh'] and sorted(a['H_actual'][:2])==sorted(b['H_actual'][:2])
                        traces[wk].append({'kind':what,'first':a,'other':b})
                    renamed,stars=canonical_transport(fourth,traces[wk][0]['first'],branch.b)
                    assert all(lawful(len(row),(renamed&mask(row)).bit_count(),law) for row in stars)
                for operation in ('structural','pointwise'):
                    mk=key+'-'+operation; metric[mk],scoped[mk],support[mk]=metric_tables(pair,SUCC.index(h),operation)
    for law in ('parity','nae'):
        for h in SUCC:
            for operation in ('pointwise','structural'):
                a=f'{law}-intact-{h}-{operation}';b=f'{law}-sham-{h}-{operation}'
                assert metric[a]==metric[b] and scoped[a]==scoped[b] and support[a]==support[b]
    write_gz(OUT/'joint.json.gz',{'schema':'successor-local-joint-v1','geometry':geom,'factors':all_factors,
           'meaning':'conditional on indicated early action; later I/T independent equal prior, I is unchanged, T physically turns only if pointwise_ok under permissive reading'})
    write_gz(OUT/'readouts.json.gz',{'overall':metric,'by_early_late_request_status':scoped,'whole_W_support_given_request_and_status':support})
    write_gz(OUT/'witnesses.json.gz',{'schema':'successor-physical-witnesses-v1','traces':traces})
    print('36 exact conditional distributions;',len(metric),'joint reading conditions;',sum(len(v) for v in traces.values()),'physical comparisons')


if __name__=='__main__':main()
