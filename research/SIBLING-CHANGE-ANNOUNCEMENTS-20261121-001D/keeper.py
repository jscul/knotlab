"""The enrolled elementary, local value motions. Full words use physical bit IDs."""
from collections import Counter
from dataclasses import dataclass, field
from functools import cache, lru_cache
from itertools import combinations, product

X = ((7,8,9), (10,11,12), (13,14,15))
ABC = (16,17,18)
DEF = (19,20,21)
H_SLACK, K_SLACK, L_SLACK = 22,23,24
REG = tuple(tuple((25+6*i+2*j,26+6*i+2*j) for j in range(3)) for i in range(3))
ROOT = (0,1,2,3)
OLD = (ROOT, (0,4,5,6), *(tuple((i+1,*row)) for i,row in enumerate(X)))
TERNARY = tuple(product((0,1),repeat=3))
READY = (1,1,0)
WRITE = {0:(1,0,1),1:(0,1,1)}
PORT = {READY:'ready',WRITE[0]:'0',WRITE[1]:'1'}
HALF = ('restricted',)
WIRING = {'complete','restricted'}
ACTIVE = ('asymmetric','symmetric','some_motion','all_motion','restricted','passive')


def digits(seq):
    return ''.join(str(i) for i in seq)


def val(word,m):
    return (word>>m)&1


def at(word,row):
    return tuple(val(word,m) for m in row)


def assign(word,row,bits):
    for n,v in zip(row,bits,strict=True):
        word=(word|(1<<n)) if v else (word&~(1<<n))
    return word


def lawful(bits,law):
    return bool(sum(bits)%2==0) if law=='parity' else len(set(bits))>1


def legal_roots(law):
    return tuple(u for u in product((0,1),repeat=4) if lawful(u,law))


def local_states(law):
    return tuple((u,row) for u in (0,1) for row in TERNARY if lawful((u,*row),law))


@cache
def holdings(wiring='complete'):
    ext=tuple(n for row in X for n in row if
              (wiring!='restricted' or n!=row[-1]) and wiring!=f'missing{n}')
    bank=tuple(n for triple in REG for pair in triple for n in pair)
    return (*OLD, (*ext,*ABC,H_SLACK,*bank), (*ABC,*DEF,K_SLACK), (*DEF,L_SLACK))


@cache
def labels(wiring):
    return {n:tuple(h for h,row in enumerate(holdings(wiring)) if n in row) for n in range(43)}


def initial_old(u,rows):
    word=assign(0,ROOT,u)
    for i,row in enumerate(rows):
        word=assign(word,OLD[i+1][1:],row)
    return word


def ready(word,law,wiring):
    word=assign(assign(word, ABC,READY),DEF,READY)
    for triple in REG:
        for pair in triple:
            word=assign(word,pair,(1,0))
    if law=='parity':
        word=assign(word,(H_SLACK,),(sum(at(word,holdings(wiring)[5]))%2,))
    return word


def selected_sides(i,wiring):
    return REG[i] if wiring!='restricted' else (REG[i][0],)


def rotated(x,direction):
    a,b,c=x
    return (b,c,a) if direction==1 else (c,a,b)


def signature(x,direction):
    rotated_row=rotated(x,direction)
    return tuple(x[k]^rotated_row[k] for k in (0,1))


@cache
def decode(row,delta,law,symmetric):
    if len(set(row))==1:
        return (1-row[0] if law=='nae' else row[0]) if delta==(0,0) else None
    if symmetric:
        match=[b for b in (0,1) if delta==signature(row,b)]
        return match[0] if len(match)==1 else None
    return int(any(delta))


def guard(bills,bits):
    return tuple(zip(bills,bits,strict=True))


def resolved(wiring,holder,pair,guards):
    held=holdings(wiring)[holder]
    a,b=pair
    return a!=b and a in held and b in held and labels(wiring)[a]==labels(wiring)[b] and all(
        x in held and x not in pair for x,v in guards)


@dataclass(frozen=True)
class Offer:
    holder:int
    pair:tuple
    guards:tuple=()
    connected:bool=True
    label:str=''


def apply(word,offer,wiring):
    """The B286 guard checks topology before value comparison."""
    if not offer.connected: return word,'disconnected'
    if not resolved(wiring,offer.holder,offer.pair,offer.guards):return word,'unsupported'
    if any(val(word,m)!=v for m,v in offer.guards):return word,'refused'
    a,b=offer.pair
    return ((word,'equal') if val(word,a)==val(word,b) else
            (word^(1<<a)^(1<<b),'changed'))


def capture(i,r,word,wiring,connected=True):
    return [Offer(5,REG[i][a],((r[a],1),),connected,'record present exterior') for a in range(2)]


def motions(i,mode,connected):
    x=X[i];actor=i+2
    if mode=='restricted' or mode=='single_F':
        return [Offer(actor,x[:2],((i+1,1),),connected,'original sibling exchange')]
    seq=[]
    for direction in ((1,0) if mode in ('symmetric','some_motion','all_motion') else (1,)):
        pairs=(x[:2],x[1:]) if direction==1 else (x[1:],x[:2])
        for pair in pairs:
            seq.append(Offer(actor,pair,((i+1,direction),),connected,'original sibling exchange'))
    return seq


@dataclass
class Stage:
    word:int
    wiring:str
    trail:list=field(default_factory=list)
    status:Counter=field(default_factory=Counter)

    def offer(self,offer):
        before=self.word
        self.word,status=apply(before,offer,self.wiring)
        self.trail.append(offer)
        self.status[status]+=1
        return status

    def inverse(self,previous):
        for offered in reversed(previous):self.offer(offered)


@cache
def local(i,u,row,mode,law,decoder,wiring,off,comparison):
    """Evaluate all relevant literal guards on this live sibling.

    The Q predicate is a disjoint list of exact five-bit patterns. Every other
    co-held pattern fails on at least one unchanged bit; dispatching directly to
    the present one has the identical physical result. Missing guards stay invalid.
    """
    x=X[i]
    word=assign(assign(0,(i+1,),(u,)),x,row)
    for p in REG[i]:word=assign(word,p,(1,0))
    event=Stage(word,wiring); before=word
    passive=mode in ('passive','single_H0','single_H1','none')
    if passive:
        return (row,(0,0),0,None,0,(),True,word)
    connected=i not in off
    if mode=='single_F':
        events=motions(i,mode,connected) if i==0 else []
        statuses=tuple(event.offer(e) for e in events)
        return (at(event.word,x),(0,0),0,None,statuses.count('changed'),statuses,False,event.word)
    regs=REG[i]
    cap=capture(i,x,word,wiring,comparison)
    if mode=='restricted':cap=cap[:1]
    for o in cap:event.offer(o)
    move=motions(i,mode,connected)
    statuses=tuple(event.offer(o) for o in move)
    for o in cap:event.offer(o)
    event.inverse(move)
    assert at(event.word,x)==row
    delta=tuple(val(event.word,p[1]) for p in regs[:2])
    if mode=='restricted':
        admissible=(row[0]!=row[1])
        q=delta[0]
        pattern=guard((x[0],x[1],regs[0][1]),(row[0],row[1],q))
        expected=q if admissible else None
    else:
        sym=mode in ('symmetric','some_motion','all_motion')
        expected=decode(row,delta,decoder,sym)
        # Candidate 1's asymmetric predicate specifies all patterns, including
        # otherwise inconsistent homogeneous rows after an ablation.
        q=int(expected==1) if sym else int(any(delta) or row==((0,0,0) if decoder=='nae' else (1,1,1)))
        pattern=guard((*x,regs[0][1],regs[1][1]),(*row,*delta))
    if q and mode!='restricted':
        event.offer(Offer(5,regs[2],pattern,comparison,'local decoded Q'))
    # In the restricted apparatus the H write reads each first capture pair directly.
    raw_q=val(event.word,regs[0 if mode=='restricted' else 2][1])
    output=event.word
    prior=tuple(event.trail)
    event.inverse(prior)
    assert event.word==before
    return (row,delta,raw_q,expected,statuses.count('changed'),statuses,True,output)


@lru_cache(maxsize=16384)
def receipt(mode,law,decoder,code,wiring,off,comparison,write,relay,nonfocal):
    """Construct both complete keeper words and their inverse delivery."""
    cells=tuple(local(i,u,row,mode,law,decoder,wiring,off,comparison)
                for i,(u,row) in enumerate(nonfocal))
    # Display words use only physical nonfocal bits and true writable auxiliaries.
    raw=assign(assign(0,ABC,READY),DEF,READY)
    for i,c in enumerate(cells):
        for marks in (X[i],*REG[i]):
            raw=assign(raw,marks,at(c[-1],marks))
    if law=='parity':
        raw=assign(raw,(H_SLACK,),(sum(at(raw,holdings(wiring)[5]))%2,))
    q=tuple(c[2] for c in cells)
    r=Stage(raw,wiring)
    ext=tuple(n for row in X for n in row)
    qnames=tuple(p[0 if mode=='restricted' else 2][1] for p in REG)
    offered=[]
    if mode in ('passive','single_H0','single_H1'):
        for c in (0,1):
            if mode not in ('passive',f'single_H{c}'): continue
            pair=ABC[1:] if c==0 else (ABC[0],ABC[2])
            offered.append(Offer(5,pair,guard(ext,(c,)*9),write,'passive exterior'))
    elif mode not in ('none','single_F'):
        valid=(mode=='asymmetric' or all(c[3] is not None and c[2]==c[3] for c in cells))
        if mode=='restricted':valid=all(c[3] is not None and c[2]==c[3] for c in cells)
        if mode in ('some_motion','all_motion'):
            mixed=sum(len(set(c[0]))==2 for c in cells)
            valid=valid and (mixed>0 if mode=='some_motion' else mixed==3)
        unanimous=q[0]==q[1]==q[2]
        if valid and (code=='xor' or unanimous):
            result=(q[0]^q[1]^q[2] if code=='xor' else (q[0] if code=='parity' else 1-q[0]))
            cond=guard(qnames,q)
            # These are the exact fixed local conjunctions indexed by the current
            # row/T patterns. No true u or motion counter occurs in an H guard.
            if mode in ('symmetric','some_motion','all_motion'):
                cond+=sum((guard((*X[i],REG[i][0][1],REG[i][1][1]),(*c[0],*c[1]))
                           for i,c in enumerate(cells)),())
            if mode=='restricted':
                cond+=sum((guard((*X[i][:2],REG[i][0][1]),(*c[0][:2],c[1][0]))
                           for i,c in enumerate(cells)),())
            pair=ABC[1:] if result==0 else (ABC[0],ABC[2])
            offered.append(Offer(5,pair,cond,write,'physical conditional H write'))
    result_status=tuple(r.offer(o) for o in offered)
    first_k=at(r.word,(*ABC,*DEF,K_SLACK))
    first=PORT[at(r.word,ABC)]
    do_relay=relay and mode not in ('none','single_F','single_H0','single_H1')
    connects=[Offer(6,DEF[1:],guard(ABC,WRITE[0]),do_relay,'deliver answer 0'),
              Offer(6,(DEF[0],DEF[2]),guard(ABC,WRITE[1]),do_relay,'deliver answer 1')]
    for o in connects:r.offer(o)
    delivered=at(r.word,(*DEF,L_SLACK))
    delivery=PORT[delivered[:3]]
    pre_cleanup=r.word
    # A literal single offer stops here at K. All other writes have their H display
    # restored while L's actually shared delivery triple remains distinct.
    if mode not in ('single_H0','single_H1'):r.inverse(offered)
    post_k=at(r.word,(*ABC,*DEF,K_SLACK))
    h_reset=at(r.word,ABC)==READY
    assert at(r.word,(*DEF,L_SLACK))==delivered
    sequence=tuple(r.trail)
    r.inverse(sequence)
    assert r.word==raw
    for o in sequence:r.offer(o)
    assert at(r.word,(*DEF,L_SLACK))==delivered
    if mode not in ('single_H0','single_H1'):
        for o in sequence:r.offer(o)
        assert at(r.word,DEF)==READY
    connected_scopes=[]
    for i,c in enumerate(cells):
        connected_scopes.append(digits((int('changed' in c[5]),int('equal' in c[5]),
                                         int('refused' in c[5]),int('disconnected' in c[5]),int('unsupported' in c[5]))))
    return (first,delivery,tuple(c[4] for c in cells),q,
            tuple(c[1] for c in cells),tuple(connected_scopes),first_k,post_k,delivered,
            h_reset,tuple(result_status))
