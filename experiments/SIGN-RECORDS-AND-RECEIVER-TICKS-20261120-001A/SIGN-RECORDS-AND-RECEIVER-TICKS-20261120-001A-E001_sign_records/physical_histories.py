"""Ordinary local swaps act on the eleven physical bits; no sign or preparation label enters act()."""
from collections import Counter, deque
from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
RESEARCH=ROOT/'research'/HERE.parent.name
KNOTS=((0,1,8),(0,1,2,3),(2,3,4,5,6,7,9),(6,7,10))
# Holders are ordinary constraint rows. Gates are named uses of the claimed physical input/output marks.
TARGET={'F':0,'C':2,'B':0,'P':6,'V':6,'L':4}
CONTROL={'F':None,'C':0,'B':2,'P':2,'V':4,'L':2}
HOLDER={'F':0,'C':1,'B':1,'P':2,'V':2,'L':2}
ARMS={'adjacent_repeats':'FFCC','interleaved':'FCFC'}
LAW=('parity','nae')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(filename,obj,check):
    raw=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()
    if filename.endswith('.gz'):
        raw=gzip.compress(raw,mtime=0)
    dest=OUT/filename
    if check:
        if dest.read_bytes()!=raw:raise ValueError(f'Changed evidence: {dest}')
    else: dest.write_bytes(raw)


def bit(word,index):
    return (word>>index)&1


def swap(word,pair):
    if bit(word,pair)!=bit(word,pair+1):
        return word^(3<<pair)
    return word


def recode(word):
    for pair in (0,2,4,6):word=swap(word,pair)
    return word


def encode(d,m,w=0,r=0,orientation=0):
    raw=(7<<8) + sum(1<<(p+1-value) for p,value in zip((0,2,4,6),(d,m,w,r)))
    return recode(raw) if orientation else raw


def codeword(word,orientation=0):
    return tuple(bit(word,p+orientation) for p in (0,2,4,6))


def legal(word,law):
    weights=[sum(bit(word,b) for b in row) for row in KNOTS]
    if law=='parity':return all(k%2==0 for k in weights)
    return all(0<k<len(row) for k,row in zip(weights,KNOTS))


def act(word,gate,orientation=0):
    control=CONTROL[gate];target=TARGET[gate]; row=KNOTS[HOLDER[gate]]
    assert target in row and target+1 in row and (control is None or control+orientation in row)
    enabled=control is None or bool(bit(word,control+orientation))
    nxt=swap(word,target) if enabled else word
    return nxt,enabled


def path(word,program,orientation=0):
    trajectory=[word];offers=[]; firings=[]
    for g in program:
        changed,enabled=act(word,g,orientation)
        offers.append([g,enabled,changed!=word]);firings.append(changed!=word)
        trajectory.append(changed);word=changed
    return dict(states=trajectory,offers=offers,firings=firings)


def histogram(values):
    return Counter(values)


def probability_table(values):
    counts=histogram(values);n=sum(counts.values());return [[k,str(Fraction(v,n))] for k,v in sorted(counts.items())]


def tv(a,b):
    a=histogram(a);b=histogram(b);na=sum(a.values());nb=sum(b.values())
    return str(sum((abs(Fraction(a[k],na)-Fraction(b[k],nb)) for k in a.keys()|b.keys()),Fraction())/2)


def projection_gate(width,patterns):
    variables=[f'b{i}' for i in range(width)]
    missing=[x for x in range(1<<width) if x not in patterns]
    clauses=[' '.join(('~' if bit(x,i) else '')+v for i,v in enumerate(variables)) for x in missing]
    cmd=[sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),'--loops',*variables[:-1],'--contact',variables[-1],'--json']
    obs=json.loads(subprocess.check_output(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')},text=True))
    return {k:obs[k] for k in ('binding','loss_on_erasure','coexistence','is_knot')}


def unrestricted():
    out={}
    for law in LAW:
        words=tuple(w for w in range(1<<11) if legal(w,law));valid=set(words);gates={};checks=[]
        for row in KNOTS:
            projection={sum(bit(w,b)<<i for i,b in enumerate(row)) for w in words}
            full={x for x in range(1<<len(row)) if (x.bit_count()%2==0 if law=='parity' else 0<x.bit_count()<len(row))}
            assert projection==full;gate=projection_gate(len(row),projection);assert gate['is_knot']
            checks.append(dict(support=row,projection=sorted(projection),verdict=gate))
        for g in TARGET:
            images=[act(w,g) for w in words]; assert {i for i,on in images}==valid
            assert all(act(i,g)[0]==w for w,(i,on) in zip(words,images))
            for w,(i,on) in zip(words,images):
                assert act(recode(w),g,1)==(recode(i),on)
            gates[g]=dict(enabled=sum(on for i,on in images),moving=sum(i!=w for w,(i,on) in zip(words,images)),
                          ordered_images=[[w,i,int(on)] for w,(i,on) in zip(words,images)])
        out[law]=dict(words=words,gates=gates,physical_projections=checks)
    return out


def compare(left,right,cut,orientation):
    names=('full_word','data','memory','witness','reader','data_memory','memory_witness','state_prefix','offered_prefix','executed_prefix','initial_final_memory')
    tvs={k:[] for k in names};stage_laws=[]
    for i in range(len(left[0]['states'])):
        def entries(sample):
            rows=[]
            for g in sample:
                word=g['states'][i];d,m,w,r=codeword(word,orientation)
                offers=g['offers'][:i]; hist=tuple(g['states'][:i+1])
                rows.append((word,d,m,w,r,(d,m),(m,w),hist,tuple(s[0] for s in offers),
                    tuple((s[0],s[1],s[2]) for s in offers),(bit(g['states'][0],2+orientation),m)))
            return list(zip(*rows))
        a,b=entries(left),entries(right)
        stage_laws.append({key:[probability_table(x),probability_table(y)] for key,x,y in zip(names[:7],a[:7],b[:7])})
        for key,x,y in zip(names,a,b):tvs[key].append(tv(x,y))
    def report(sample):
        return dict(reader_cut=probability_table(bit(a['states'][cut],6+orientation) for a in sample),
            reader_out=probability_table(bit(a['states'][-1],6+orientation) for a in sample),
            zero_to_one=str(Fraction(sum(bit(a['states'][cut],6+orientation)==0 and bit(a['states'][-1],6+orientation)==1 for a in sample),len(sample))))
    return dict(cut=cut,total_variations=tvs,first_difference={k:next((i for i,v in enumerate(values) if Fraction(v)),None) for k,values in tvs.items()},
         exact_stage_laws=stage_laws,arm_readers=[report(left),report(right)],literal_histories=[left,right])


def matched_histories():
    records={}
    for orientation,random_memory,copy_witness,reset,ready,reader in product((0,1),(0,1),(0,1),(0,1),(0,1),('P','PV')):
        births=[encode(d,m,r=ready,orientation=orientation) for d in (0,1) for m in (range(2) if random_memory else (0,))]
        assert all(legal(v,l) for l in LAW for v in births)
        first='L' if copy_witness else '';cut=len(first)+4+int(reset)
        batches=[]
        for preparation in ARMS.values():
            batch=[]
            for seed in births:
                result=path(seed,first+preparation,orientation); old=result['states'][-1]
                if reset:
                    now=swap(old,2) if bit(old,2+orientation) else old
                    result['states'].append(now);result['offers'].append(['reset-M',True,old!=now]);result['firings'].append(old!=now);old=now
                tail=path(old,reader,orientation)
                result['states']+=tail['states'][1:];result['offers']+=tail['offers'];result['firings']+=tail['firings']
                assert all(legal(v,law) for v in result['states'] for law in LAW)
                batch.append(result)
            batches.append(batch)
        k=f'{orientation}/{random_memory}/{copy_witness}/{reset}/{ready}/{reader}'
        records[k]=compare(*batches,cut,orientation)
    return records


def transform(d,m,gates):
    w=path(encode(d,m),gates)['states'][-1]
    return bit(w,0),bit(w,2)


def real_code_check(physical_group, words, classes):
    """Independently compare the four encoded preparation/readout classes with real two-word operators."""
    initial=((1,1),(1,-1),(1,0),(0,1))
    categories=('history_a','history_b','singleton_0','singleton_1')
    def reduced(x,y):
        common=gcd(abs(x),abs(y));a,b=x//common,y//common
        return (-a,-b) if a<0 or a==0 and b<0 else (a,b)
    def image(state,operation):
        x,y=state
        if operation=='X':return reduced(y,x)
        if operation=='Z':return reduced(x,-y)
        return reduced(x+y,x-y)
    gates={'X':'F','Z':'FCFC','H':'CBC'}
    seen={initial:('', '')};queue=deque([initial]);cases=[]
    while queue:
        rays=queue.popleft();op_program,ordinary_program=seen[rays]
        permutation=tuple(words.index(transform(*a,ordinary_program)) for a in words)
        matched=[]
        for name,(x,y) in zip(categories,rays):
            locations=[words[permutation[i]] for i in classes[name]]
            n=x*x+y*y
            physical=[Fraction(sum(v[j] for v in locations),len(locations)) for j in (0,1)]
            signed=[Fraction(y*y,n),Fraction((x-y)**2,2*n)]
            assert physical==signed
            matched.append(dict(input=name,word_one_and_change_minus=list(map(str,signed))))
        cases.append(dict(abstract_operations=op_program,physical_operations=ordinary_program,permutation=permutation,rays=rays,checks=matched))
        for g,code in gates.items():
            nxt=tuple(image(ray,g) for ray in rays)
            if nxt not in seen:seen[nxt]=(op_program+g,ordinary_program+code);queue.append(nxt)
    assert {tuple(x['permutation']) for x in cases}=={tuple(x['permutation']) for x in physical_group if x['preserves_chosen_classes']}
    return cases


def covariance():
    words=tuple(product(range(2),repeat=2));start=tuple(range(4));generators={g:tuple(words.index(transform(*v,g)) for v in words) for g in 'FCB'}
    program={start:''};q=deque([start]);reps=[]
    while q:
        p=q.popleft();reps.append((p,program[p]))
        for g,h in generators.items():
            new=tuple(h[i] for i in p)
            if new not in program:program[new]=program[p]+g;q.append(new)
    classes={}
    for name,sequence in [('history_a','FFCC'),('history_b','FCFC'),('singleton_0','CBC'),('singleton_1','CBCF')]:
        classes[name]=tuple(sorted(words.index(transform(d,0,sequence)) for d in range(2)))
    group=[];selected=set(classes.values())
    for p,seq in reps:
        images={k:tuple(sorted(p[i] for i in row)) for k,row in classes.items()}
        readouts={k:[probability_table(words[i][a] for i in row) for a in (0,1)] for k,row in images.items()}
        group.append(dict(program=seq,permutation=p,preparations=images,preserves_chosen_classes=set(images.values())==selected,readouts=readouts))
    assert all(transform(*p,'CBC')==p[::-1] for p in words)
    singletons=[]
    for d,m in words:
        w=encode(d,m); out=path(w,'P')['states'][-1]
        singletons.append(dict(data=d,memory=m,initial=w,out=out,reader=bit(out,6),new_coin=False))
    return dict(group=group,generators=generators,classes=classes,all_apparatus_word_singletons=singletons,
                independent_signed_four_state_comparison=real_code_check(group,words,classes))


def run(check=False):
    gates=unrestricted();histories=matched_histories();group=covariance()
    raw=dict(schema=1,holders=KNOTS,gate_target=TARGET,gate_control=CONTROL,gate_support=HOLDER,laws=gates,
             programs=ARMS,history_key='orientation/random_initial_M/copy_W/reset_M/initial_R/reader',histories=histories,covariance=group)
    save('physical_histories.json.gz',raw,check)
    return dict(allowed_full_words={law:len(gates[law]['words']) for law in LAW},matched_scenarios=len(histories),
                programs=len(group['group']),preserve_four=sum(row['preserves_chosen_classes'] for row in group['group']))
