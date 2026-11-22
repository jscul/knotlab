"""Lawful second-receipt memory, score holders, cue selector and single-mark actuator.

The original keeper's 55 distinctions and its complete knot holdings remain
literal. On the second coupling holder every formula below is compiled from
finite, co-held unchanged marks. No game, cursor, stock label or offline
policy result is a controller input.
"""
from dataclasses import dataclass
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
old_spec = spec_from_file_location("b306_physical_keeper", HERE.parent / "FEEDER-MEMORY-20261121-001" / "keeper.py")
old = module_from_spec(old_spec)
sys.modules[old_spec.name] = old
old_spec.loader.exec_module(old)

CUES = ("none","strict_return","approach_feeder","approach_menu","approach_slot")
CATALOGUE = CUES[1:]
SECOND_FIELDS = ("x_here","x_departed","x_paid_from","x_paid_menu","x_paid_slot")
SELECTED_FIELD = {1:"x_here",2:"x_paid_from",3:"x_paid_menu",4:"x_paid_slot"}
ARRIVAL = ("arr_from","arr_menu","arr_slot")
SCORES = tuple(f"score_{i}" for i in range(4))
VOTES = tuple(f"vote_{i}" for i in range(4))
BRIDGE = ("paid","previous_on","previous_menu","cue","menu","energy_before")
NEW_WIDTH = {
    "x_here":2,"x_departed":2,"x_paid_from":3,"x_paid_menu":4,"x_paid_slot":3,
    "x_slack":1,"arr_from":3,"arr_menu":4,"arr_slot":3,"phase":5,"real_slot":3,
    "credit_energy":11,"credit_paid":2,"selector":5,"selector_slack":1,
    **{name:2 for name in VOTES}, **{name:15 for name in SCORES},
    **{f"{name}_slack":1 for name in SCORES},
}
BUFFERED = (*SECOND_FIELDS,*ARRIVAL,"phase",*SCORES,"selector")
for target in BUFFERED:
    for prefix in ("new_","saved_"):
        NEW_WIDTH[prefix+target] = NEW_WIDTH[target]
NEW_WIDTH["j_slack"] = 1
NAMES = dict(old.NAMES)
cursor=len(old.ALL)
for bank,width in NEW_WIDTH.items():
    NAMES[bank]=tuple(range(cursor,cursor+width))
    cursor+=width
ALL = tuple(range(cursor))
J_PRIVATE_SLACKS = {"x_slack", "selector_slack",*{q+"_slack" for q in SCORES}}
STARS={**old.STARS,
       "X":tuple(n for bank in (*SECOND_FIELDS,"x_slack") for n in NAMES[bank]),
       "S":(*NAMES["selector"],*NAMES["selector_slack"]),
       **{f"C{i}":(*NAMES[name],*NAMES[name+"_slack"]) for i,name in enumerate(SCORES)},
       "J":tuple(n for bank in (*BRIDGE,*NEW_WIDTH) if bank not in J_PRIVATE_SLACKS for n in NAMES[bank])}
OWNERS={n:tuple(h for h,scope in STARS.items() if n in scope) for n in ALL}
STAR_MASK={h:sum(1<<n for n in scope) for h,scope in STARS.items()}
BANK_MASK={b:sum(1<<n for n in row) for b,row in NAMES.items()}
BANK_START={b:row[0] for b,row in NAMES.items()}
CREDIT_ZERO=7


def index(word,bank):
    marked=(word & BANK_MASK[bank]) >> BANK_START[bank]
    if not marked or marked & (marked-1):
        raise ValueError(f"Invalid single marked alternative in {bank}")
    return marked.bit_length()-1


def marked(word,bank,position):
    return (word & ~BANK_MASK[bank]) | (1<<NAMES[bank][position])


def bits(word,bank):
    return old.code(word,NAMES[bank])


def lawful(word,law):
    for h,scope in STARS.items():
        ones=(word & STAR_MASK[h]).bit_count()
        if (law=="parity" and ones%2) or (law=="nae" and ones in (0,len(scope))): return False
    return True


@lru_cache(maxsize=None)
def offer(label,holder,pair,guard=()):
    a,b=pair; guard=tuple(guard)
    ok=(a!=b and holder in OWNERS[a] and OWNERS[a]==OWNERS[b]
        and all(holder in OWNERS[n] and n not in pair and value in (0,1) for n,value in guard))
    if not ok:
        raise ValueError(f"Unsupported physical offer {label}, {holder}, {pair}, {guard}")
    if len({n for n,v in guard})!=len(guard):
        raise ValueError(f"Repeated local guard name in {label}")
    return old.Offer(label,holder,pair,guard,sum(1<<n for n,v in guard),
                     sum(v<<n for n,v in guard),(1<<a)|(1<<b),True)


def literal(bank,which):
    return (NAMES[bank][which],1)


def exchange(label,bank,a,b,guards=(),holder="J"):
    return offer(label,holder,(NAMES[bank][a],NAMES[bank][b]),tuple(guards))


def input_guard(names,state):
    return tuple(literal(name,i) for name,i in zip(names,state,strict=True))


@dataclass(frozen=True,slots=True)
class Table:
    target:str
    inputs:tuple
    rows:dict


def table(target,inputs,fn):
    """Compile all finite local alternatives before observation, including abstentions."""
    inputs=tuple(inputs); rows={}
    for row in product(*(range(len(NAMES[n])) for n in inputs)):
        output=fn(*row)
        if not 0<=output<len(NAMES[target]): raise ValueError((target,row,output))
        rows[row]=None if output==0 else exchange("prepare "+target,"new_"+target,0,output,input_guard(inputs,row))
    return Table(target,inputs,rows)


def next_here(here,departed,slot,menu,paid,phase):
    if slot==0: return int(here or paid)
    return int(departed and menu==1 and phase==4)


def next_departed(here,departed,slot,phase):
    return int(here and phase==4) if slot else departed


DYNAMICS=(
    table("x_here",("x_here","x_departed","real_slot","previous_menu","paid","phase"),next_here),
    table("x_departed",("x_here","x_departed","real_slot","phase"),next_departed),
    *(table(x,(x,a,"paid"),lambda prior,arrival,paid:arrival if paid else prior)
      for x,a in zip(SECOND_FIELDS[2:],ARRIVAL)),
    table("arr_from",("arr_from","cue","real_slot"),lambda prior,cue,slot:cue+1 if slot else prior),
    table("arr_menu",("arr_menu","previous_menu","real_slot"),lambda prior,menu,slot:menu+1 if slot else prior),
    table("arr_slot",("arr_slot","real_slot"),lambda prior,slot:slot if slot else prior),
    table("phase",("phase",),lambda phase:min(4,phase+1)),
)
CREDITS=tuple(table(s,(s,v,"credit_paid","previous_on"),
                    lambda score,vote,paid,on:max(0,min(14,score+(-4 if paid else 1))) if vote and on else score)
              for s,v in zip(SCORES,VOTES))
# Original H reads the old actual menu memory to a genuinely shared mark.
MATCH=tuple(exchange("original memory matches present menu","paid",0,1,
                     (*old.clauses(old.M,old.MEMORY_CODES[t]),literal("menu",t)),"H") for t in (1,2))
ELIGIBLE=(literal("paid",1),literal("cue",1),literal("previous_on",0))
DETECTORS=[(exchange("physical strict return veto",VOTES[0],0,1,(*ELIGIBLE,literal("x_here",1))),)]
for i,(x,a) in enumerate(zip(SECOND_FIELDS[2:],ARRIVAL),1):
    DETECTORS.append(tuple(exchange("actual matched arrival features",VOTES[i],0,1,
                                    (*ELIGIBLE,literal(x,j),literal(a,j))) for j in range(1,len(NAMES[x]))))
VETO=tuple(exchange("selected physical veto to original coupler","previous_menu",0,1,
                    (literal("selector",i+1),literal(v,1))) for i,v in enumerate(VOTES))
OUTPUT=[]
for cue,prev,veto in product((0,1),repeat=3):
    wanted=2 if cue and not prev and not veto else 1
    OUTPUT.append(offer("actual original action coupling","H",old.difference(old.A,old.ACTION_CODES[0],old.ACTION_CODES[wanted]),
                        (literal("cue",cue),literal("previous_on",prev),literal("previous_menu",veto))))
CREDIT_DETECT=tuple(exchange("counterfactual public energy for credit only","credit_paid",0,1,
                            (literal("previous_on",1),literal("energy_before",a),literal("credit_energy",b)))
                    for a in range(1,11) for b in range(a,11))
TRUE_CREDIT=exchange("actual paid mark to credit input","credit_paid",0,1,(literal("paid",1),))
WINNER=[]
for i,s in enumerate(SCORES):
    for value in range(8,15):
        guard=[literal(s,value)]
        for j,other in enumerate(SCORES):
            if j==i: continue
            guard.extend((NAMES[other][v],0) for v in range(value+(j>i),15))
        WINNER.append(exchange("highest positive actual score","new_selector",0,i+1,tuple(guard)))


def prepared(law):
    w=old.initial_word(law)
    for b in NEW_WIDTH:
        if b.endswith("slack"):continue
        pos=CREDIT_ZERO if b in SCORES else 0
        w=marked(w,b,pos)
    for holder,slack in [("X","x_slack"),("S","selector_slack"),
                         *((f"C{i}",f"score_{i}_slack") for i in range(4)),("J","j_slack")]:
        if law=="parity" and (w & STAR_MASK[holder]).bit_count()%2:
            w|=1<<NAMES[slack][0]
    return w


class LearnedKnotBot(old.KnotKeeper):
    __slots__=("mode","training")

    def __init__(self,law,*,mode="learned"):
        if mode not in {"learned","current","zero","erased","permuted",*CATALOGUE}:
            raise ValueError(f"Unknown second-cue mode: {mode}")
        super().__init__(law)
        self.mode=mode
        self.training=False
        self._word=prepared(law)
        self._set_mode()

    def _set_mode(self):
        if self.mode in CATALOGUE:
            self._force("selector",CUES.index(self.mode),"S")
        elif self.mode in {"current","zero"}:
            self._force("selector",0,"S")
            if self.mode=="zero":
                for i,s in enumerate(SCORES):self._force(s,CREDIT_ZERO,f"C{i}")

    def _force(self,bank,target,holder="J",trace=None,label="supplied prepared intervention"):
        current=index(self._word,bank)
        if current!=target:
            self._offer(exchange(label,bank,current,target,holder=holder),trace=trace)

    def _input(self,bank,val,trace=None):
        self._force(bank,val,"J",trace,"supplied raw public input "+bank)

    def _table(self,stage,trace):
        state=tuple(index(self._word,b) for b in stage.inputs)
        row=stage.rows[state]
        if row is not None:self._offer(row,trace=trace)
        if trace is not None:
            trace.append({"fixed_local_table":stage.target,"actual_inputs":dict(zip(stage.inputs,state)),
                          "disjoint_input_rows":len(stage.rows),"prepared":index(self._word,"new_"+stage.target)})

    def _commit(self,target,trace=None):
        """Four reversible local blocks with an explicit outgoing old-word bank.

        Disjoint guard alternatives can be dispatched at the occupied physical
        slot. Sources remain unchanged within their corresponding block.
        """
        n="new_"+target; s="saved_"+target
        old_v=index(self._word,target); new_v=index(self._word,n)
        if old_v:
            self._offer(exchange("retain old "+target,s,0,old_v,(literal(target,old_v),)),trace=trace)
        if old_v!=new_v:
            self._offer(exchange("deposit local "+target,target,old_v,new_v,(literal(s,old_v),literal(n,new_v))),trace=trace)
        if new_v:
            self._offer(exchange("return copied new "+target,n,0,new_v,(literal(target,new_v),)),trace=trace)
        # A fresh private one-hot token replaces the egress bank. The old
        # symbol is exported; a finite closed lift retains it in another
        # equally held, fresh one-hot bank via name-for-name exchanges.
        before=self._word
        self._word=marked(self._word,s,0)
        if trace is not None:
            trace.append({"external_exchange":"export previous "+target,"bank":s,"exported_index":old_v,
                          "incoming_index":0,"before":before,"after":self._word})

    def _update(self,tables,trace=None):
        # Prepare all targets before committing any of them. This is required
        # for the old current-anchor and arrival values in the update formulas.
        for t in tables:self._table(t,trace)
        for t in tables:self._commit(t.target,trace)

    def export(self):
        return {"schema":"second-cue-frozen-v1","selector":index(self._word,"selector"),
                "selector_word":bits(self._word,"selector"),
                "scores":[index(self._word,b)-CREDIT_ZERO for b in SCORES],
                "score_words":[bits(self._word,b) for b in SCORES]}

    @classmethod
    def from_frozen(cls,law,export,*,mode="learned"):
        d=cls(law,mode=mode)
        scores=export["scores"];sel=export["selector"]
        if len(scores)!=4 or any(type(x) is not int or not -7<=x<=7 for x in scores) or type(sel) is not int or not 0<=sel<=4:
            raise ValueError("Malformed physically learned credit/selector")
        for i,(b,v) in enumerate(zip(SCORES,scores)):
            d._force(b,v+CREDIT_ZERO,f"C{i}")
        d._force("selector",sel,"S")
        if d.export()["selector_word"]!=export["selector_word"] or d.export()["score_words"]!=export["score_words"]:
            raise ValueError("Decoded state contradicts transported physical word")
        d._set_mode()
        if mode=="permuted":
            for i in (3,2,1):
                d._offer(exchange("supplied cyclic permutation of the four cue marks","selector",i,i+1,holder="S"))
        return d

    def begin_episode(self,training=False):
        # Preserve the learned physical words exactly, replacing only transient
        # episode registers with their declared legal preparation.
        w=prepared(self.law)
        for b in (*SCORES,"selector"):
            w=(w & ~BANK_MASK[b]) | (self._word & BANK_MASK[b])
        self._word=w;self._stage="idle";self.training=bool(training)
        return self

    @property
    def second_word(self):
        return tuple(bits(self._word,b) for b in SECOND_FIELDS)

    @property
    def selector(self):
        return index(self._word,"selector")

    def snapshot(self):
        return (("law",self.law),("mode",self.mode),("training",self.training),("stage",self._stage),
                *((b,bits(self._word,b)) for b in NAMES))

    def candidate_votes(self):
        return tuple(index(self._word,b) for b in VOTES)

    def checkpoint(self,obs,*,detail=False):
        tr=[] if detail else None
        # Actual preceding old actuator is exported and reset. No winner,
        # detector vote or action is determined at this checkpoint.
        self._run(old.CLEAR_ACTION,trace=tr);self._export("action",tr)
        self._reset_public(tr)
        self._prepare_public("cue",int(bool(obs.feeder)),tr)
        self._prepare_public("menu",old.menu_type(obs.slots),tr)
        self._prepare_public("previous_on",int(obs.previous=="eat"),tr)
        for v in VOTES:self._force(v,0,trace=tr,label="renew old candidate flag")
        self._stage="ready to read"
        if self.mode=="erased":
            erased=self.erase_second(detail=detail)
            if detail:tr.extend(erased)
        return tr

    def read_prepared(self,*,detail=False):
        if self._stage!="ready to read": raise ValueError("Prepare the current public query first")
        tr=[] if detail else None
        self._run(MATCH,trace=tr)
        for g in DETECTORS:self._run(g,trace=tr)
        coupled=not self.training
        self._run(VETO,coupled,tr)
        self._run(OUTPUT,trace=tr)
        self._run(reversed(VETO),coupled,tr)
        self._run(reversed(MATCH),trace=tr)
        self._stage="issued"
        bit=old.get(self._word,old.A[2])
        return (bit,tr) if detail else bit

    def decide(self,obs):
        self.checkpoint(obs)
        return self.read_prepared()

    def after_turn(self,obs,action_on,outgoing_slot,energy_after,*,training=None,credit_energy_after=None,detail=False):
        learn=self.training if training is None else bool(training)
        if self._stage=="idle":self.checkpoint(obs)
        if self._stage=="ready to read":self.read_prepared()
        if self._stage!="issued":raise ValueError("Missing pre-action physical sensor record")
        tr=[] if detail else None
        menus=old.menu_type(obs.slots)
        e=obs.energy
        allowed={e-1}
        if action_on and obs.feeder:allowed.add(min(10,e+3))
        if type(e) is not int or not 1<=e<=10 or action_on not in (0,1) or energy_after not in allowed:
            raise ValueError("Illegal publicly observed ration-game transition")
        if outgoing_slot is not None and (action_on or type(outgoing_slot) is not int or outgoing_slot not in obs.slots):
            raise ValueError("A completed move must expose a real anonymous outgoing slot")
        if not action_on and obs.slots and outgoing_slot is None:
            raise ValueError("A successful OFF needs its actual outgoing slot")
        if credit_energy_after is not None and (credit_energy_after not in {e-1,min(10,e+3)} or not learn):
            raise ValueError("Alternative credit energy is a separately supplied training control")
        earlier=self.export() if learn or detail else None
        votes=self.candidate_votes()
        before_m=self.memory_word
        self._reset_public(tr)
        for bank,val in (("cue",int(bool(obs.feeder))),("previous_on",int(action_on)),("previous_menu",menus),
                         ("energy_before",e),("energy_after",energy_after)):
            self._prepare_public(bank,val,tr)
        self._input("real_slot",0 if outgoing_slot is None else 1+outgoing_slot%2,tr)
        self._run(old.DETECT,trace=tr)
        self._run(old.ADDRESS,trace=tr)
        paid=index(self._word,"paid")
        if learn:
            if credit_energy_after is None:self._offer(TRUE_CREDIT,trace=tr)
            else:
                self._input("credit_energy",credit_energy_after,tr);self._run(CREDIT_DETECT,trace=tr)
            credit=index(self._word,"credit_paid")
            self._update(CREDITS,tr)
            self._run(WINNER,trace=tr);self._commit("selector",tr)
            if credit_energy_after is None:self._offer(TRUE_CREDIT,trace=tr)
            else:
                self._run(reversed(CREDIT_DETECT),trace=tr);self._input("credit_energy",0,tr)
        else:credit=None
        self._update(DYNAMICS,tr)
        self._run(old.COMMIT,trace=tr)
        self._export("memory",tr)
        self._run(reversed(old.DETECT),trace=tr)
        self._reset_public(tr);self._input("real_slot",0,tr)
        for v in VOTES:self._force(v,0,trace=tr,label="retire observed physical candidate flag")
        self._stage="idle"
        return {"votes":list(votes),"detected":bool(paid),"credit_paid":credit,"memory_before":before_m,
                "memory_after":self.memory_word,"second_after":self.second_word,
                **({"before":earlier,"after":self.export()} if learn or detail else {}),
                **({"offers":tr} if detail else {})}

    def _intervene(self,fields,values,detail):
        if self._stage!="ready to read":raise ValueError("Intervene only on the prepared action checkpoint")
        tr=[] if detail else None
        for b,val in zip(fields,values,strict=True):
            self._force(b,val,"X",tr,"physical intervention on selected receipt marks")
        return tr

    def sham(self,*,detail=False):
        if self._stage!="ready to read":raise ValueError("Prepare the action checkpoint before sham")
        tr=[] if detail else None
        op=exchange("same physical X pair offered twice","x_here",0,1,holder="X")
        self._run((op,op),trace=tr)
        return tr

    def _bilateral(self,other,fields,detail):
        if self.law!=other.law:raise ValueError("Compare like-law copies")
        if self._stage!="ready to read" or other._stage!="ready to read":
            raise ValueError("Both intervention copies must be at their prepared checkpoint")
        a=[index(self._word,b) for b in fields];b=[index(other._word,x) for x in fields]
        ta=self._intervene(fields,b,detail);tb=other._intervene(fields,a,detail)
        return (ta,tb) if detail else None

    def exchange_second(self,other,*,detail=False):
        return self._bilateral(other,SECOND_FIELDS,detail)

    def exchange_selected(self,other,*,detail=False):
        if self.selector!=other.selector:raise ValueError("The two frozen selectors must agree")
        field=SELECTED_FIELD.get(self.selector)
        return self._bilateral(other,(field,) if field else (),detail)

    def erase_second(self,*,detail=False):
        return self._intervene(SECOND_FIELDS,[0]*len(SECOND_FIELDS),detail)
