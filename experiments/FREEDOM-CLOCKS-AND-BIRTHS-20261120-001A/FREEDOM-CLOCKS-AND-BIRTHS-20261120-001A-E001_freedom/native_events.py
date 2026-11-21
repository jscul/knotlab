"""Compare actual full-word flips, projected input freedoms, birth and state-changing guards."""
from fractions import Fraction as F
import json
import sys
from words import ROOT,compact,op_moment,Question,save,states
from ordinary import NotAllEqualSupport,Parity,advance,certify,experiment,module_at,nea_contraction


def eight(extra):
    source=module_at('freedom_eight_fixture',experiment('BOND-CLOSURE-20261120-001A')/'eight_inputs.py')
    names,meet,_=source.fixture(extra)
    return [[b for b,p in enumerate(meet) if j in p] for j in range(len(names)-1)],list(range(8))


def projection(stars,marks,law):
    n=len(marks)
    if law=='parity':
        q=Parity(stars);rows=q.projected_rows(marks)
        def lift(x):return sum(((x>>i)&1)<<b for i,b in enumerate(marks))
        return [x for x in range(1<<n) if all((r&lift(x)).bit_count()%2==0 for r in rows)]
    with NotAllEqualSupport(stars) as sat:
        return [x for x in range(1<<n) if sat.solver.solve(assumptions=[(b+1)*(1 if x>>i&1 else -1) for i,b in enumerate(marks)])]


def measure(stars,marks,law):
    assert all(certify(stars,law));marked=set(marks);width=max(map(max,stars))+1;d=sum(1<<i for i in marks)
    P=set(projection(stars,marks,law));full=(1<<len(marks))-1
    if law=='parity':
        q=Parity(stars);n=q.total;cnt=n*int(all((row&d).bit_count()%2==0 for row in q.rows))
    else:
        assert all(len(marked.intersection(s))<=1 for s in stars)
        n=int(nea_contraction(stars,[])[0,0]);residual=[[b for b in h if b not in marked] for h in stars]
        cnt=(1<<len(marked))*int(nea_contraction(residual,[])[0,0]);assert 0<=cnt<=n
    if width<=12:
        S=states(stars,law);assert len(S)==n and sum(x^d in S for x in S)==cnt
        assert P=={compact(x,marks) for x in S}
    outcome,grown=advance(stars,law,False)
    old_width=1+max(map(max,stars));matching=[r for r in outcome['new'] if set(v for v in r['places'] if v<old_width)==marked]
    assert len(matching)==1
    return dict(stars=stars,marks=marks,allowed=n,free_states=cnt,full_word_freedom=str(F(cnt,n)),
                proposed_change_plus=str(F(n+cnt,2*n)),projected_words=sorted(P),
                projected_all_flip_freedom=str(F(sum(x^full in P for x in P),len(P))),
                projected_single_flip_freedom=[str(F(sum(x^(1<<i) in P for x in P),len(P))) for i in range(len(marks))],
                birth=matching[0],step_status=outcome['status'],births=len(outcome['new']))


def run():
    twins={}
    for p in (3,8):
        for extra in (False,True):
            if p==3:
                stars=[[0,1,3],[0,2,4],[1,2,5]];marks=[3,4,5]
                if extra:stars[0].append(6)
            else:stars,marks=eight(extra)
            twins[f'{p}/{int(extra)}']={law:measure(stars,marks,law) for law in ('parity','nae')}
    small=[[0,1,2],[0,3,4,5]];swap={};d=6
    for law in ('parity','nae'):
        S=states(small,law);pairs=[[x,x^d if bool(x&2)!=bool(x&4) else x] for x in sorted(S)]
        assert {y for _,y in pairs}==S
        moving=sum(x!=y for x,y in pairs);free=set(x for x in S if x^d in S)
        differs=[x for x,y in pairs if (x!=y)!=(x in free)]
        if law=='nae':assert not differs
        swap[law]=dict(allowed=len(S),free_words=sorted(free),attempts=pairs,freedom_indicator_disagreements=differs,ordinary_move_rate=str(F(moving,len(S))),
                       plus_chance=str(F(len(S)+len(free),2*len(S))))
    previous=experiment('READS-HOLDERS-SOURCES-20261120-001A');sys.path.insert(0,str(previous))
    motion=module_at('freedom_prior_motion',previous/'motion.py');guard=motion.directed_guard()
    path=next((ROOT/'artifacts'/'READS-HOLDERS-SOURCES-20261120-001A').glob('*/motion.json'))
    prior=json.loads(path.read_text());assert guard==prior['directed_guard']
    stage=motion.motion_stage.load_stage('R31',1);w=guard['idling_collision'];assert stage.allowed_change(w['named_event'])
    switch=motion.switch_at_four();assert switch==prior['restored_switch']
    save('ordinary_events.json',dict(funded_contrasts=twins,archived_swap=swap,guard=guard,
                guard_named_translation_always_free_on_parity=True,switch=switch))
