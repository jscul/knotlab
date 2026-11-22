"""Check the one changed physical return offer, original isolation and credit."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

import device


HERE = Path(__file__).resolve().parent
A = device.first
sys.path.append(str(HERE.parents[1] / "FEEDER-MEMORY-20261121-001"))
from feeder_game import FeederGame, Observation, sample_world


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def observation(cue, menu, previous, energy=6):
    return Observation(bool(cue), energy, "eat" if previous else "move", tuple(range(menu)))


def ready(kind, law, memory, returned, selected, pattern, training):
    board = kind(law).begin_episode(training)
    before = board.memory_word
    after = A.old.MEMORY_CODES[memory]
    if before != after:
        board._offer(A.offer("prepare a test word on first memory", "M",
                             A.old.difference(A.old.M, before, after)))
    board._force("x_here", returned, "X")
    board._force("selector", selected, "S")
    for i in range(3):
        paid = A.SECOND_FIELDS[i+2]
        current = A.ARRIVAL[i]
        # Unknown/unknown must abstain. Otherwise independently give each
        # detector equal or different nonzero marks on the two actual records.
        board._force(paid, 0 if pattern == 8 else 1)
        board._force(current, 0 if pattern == 8 else 1 if pattern & 1 << i else 2)
    assert A.lawful(board._word, law)
    return board


def physical_guard():
    old, = A.DETECTORS[0]
    new, = device.DETECTORS[0]
    holder, pair = old.holder, old.operands
    expected = ((A.NAMES["cue"][1],1),(A.NAMES["previous_on"][0],1),(A.NAMES["x_here"][1],1))
    assert tuple(new.guard)==expected and tuple(old.guard)==((A.NAMES["paid"][1],1),*expected)
    assert holder==new.holder=="J" and pair==new.operands==A.NAMES["vote_0"]
    assert tuple(A.OWNERS[pair[0]])==tuple(A.OWNERS[pair[1]])==("J",)
    assert all(name in A.STARS[holder] and name not in pair for name,_ in new.guard)
    assert all(group is A.DETECTORS[i] for i,group in enumerate(device.DETECTORS[1:],1))
    assert old is device.original_offer and new is not old
    assert A.NAMES is device.NAMES and A.OWNERS is device.OWNERS and A.STARS is device.STARS
    assert device.LearnedKnotBot.__mro__[1] is A.LearnedKnotBot
    inherited = ["before_decision","after_turn","read_prepared","begin_episode","exchange_second",
                 "exchange_selected","erase_second","sham","export","checkpoint","decide"]
    assert all(getattr(device.LearnedKnotBot,k) is getattr(A.LearnedKnotBot,k) for k in inherited)
    proof = json.loads((HERE.parent/"device_verified.json").read_bytes())
    assert all(proof["laws"][law]["unrestricted_projections"]["old_relation_identical"]
               and all(p["K1_K2_K3"] for p in proof["laws"][law]["unrestricted_projections"]
                       ["per_holder_full_projections"].values()) for law in ("parity","nae"))
    return {"holder":holder,"operands":pair,"old_guard":old.guard,"new_guard":new.guard,
            "actual_guard_holders":[[i,A.OWNERS[i]] for i,_ in new.guard],
            "identical_holding_objects":True,"shape":proof["physical_shape"]["arity"],
            "inherited_methods":inherited,"inherited_K1_K2_K3":True}


def complete_queries(law):
    counts = Counter()
    source_serial = tuple(tuple(o.guard for o in group) for group in A.DETECTORS)
    for mem,returned,sel,pat,train in product(range(3),range(2),range(5),range(9),range(2)):
        old_init = ready(A.LearnedKnotBot,law,mem,returned,sel,pat,train)
        new_init = ready(device.LearnedKnotBot,law,mem,returned,sel,pat,train)
        assert old_init._word == new_init._word
        for cue,menu,prev in product(range(2),range(3),range(2)):
            obs = observation(cue,menu,prev)
            a,b=deepcopy(old_init),deepcopy(new_init)
            a.checkpoint(obs); b.checkpoint(obs)
            assert a._word==b._word
            current = int(cue==1 and prev==0)
            match = bool(mem==menu and mem!=0)
            others = tuple(int(current and match and pat!=8 and (pat & 1 << i)!=0) for i in range(3))
            votes_a=(int(current and match and returned),*others)
            votes_b=(int(current and returned),*others)
            bit_a,bit_b=a.read_prepared(),b.read_prepared()
            assert a.candidate_votes()==votes_a and b.candidate_votes()==votes_b
            assert bit_a==int(current and (train or not sel or not votes_a[sel-1]))
            assert bit_b==int(current and (train or not sel or not votes_b[sel-1]))
            expected_change = (A.BANK_MASK["vote_0"] if votes_a[0]!=votes_b[0] else 0)
            if bit_a != bit_b:
                expected_change |= (1<<A.old.A[1])|(1<<A.old.A[2])
            assert a._word ^ b._word == expected_change
            assert a.memory_word==b.memory_word==A.old.MEMORY_CODES[mem]
            assert A.lawful(a._word,law) and A.lawful(b._word,law)
            counts["tested"]+=1
            counts["strict_vote_added"]+=votes_b[0]-votes_a[0]
            counts["action_became_off"]+=bit_a-bit_b
            counts["unmodified_A_rejects_mismatch"]+=bool(current and returned and not match)
            counts["training_actuator_agrees"]+=bool(train and bit_a==bit_b)
    assert tuple(tuple(o.guard for o in g) for g in A.DETECTORS)==source_serial
    return counts


def paid_fixture(law):
    # An actual earlier, completed archival game contains this persisting older
    # ration. Its identities are evidence for the reader of this audit only.
    data = json.loads((HERE.parent/"device_science.json").read_bytes())
    path = data["forced_traces"]["earlier_forced"]["first_older"][law]
    rows=path["public"]
    by_code=("start","eat","move","refused")
    def obs(row):
        return Observation(bool(row[0]),row[1],by_code[row[2]],tuple(range(row[3])))
    def arm(kind,train):
        board=kind(law,mode="strict_return" if not train else "learned").begin_episode(train)
        for row,nxt in zip(rows, rows[1:]):
            o=obs(row); action=row[4]
            board.decide(o)
            board.after_turn(o,int(action==0),action-1 if action>0 else None,nxt[1],training=False)
        board.checkpoint(obs(rows[-1]))
        return board
    a=arm(A.LearnedKnotBot,False); b=arm(device.LearnedKnotBot,False)
    assert a._word==b._word
    state=dict(b.snapshot())
    bit_a,ta=a.read_prepared(detail=True)
    bit_b,tb=b.read_prepared(detail=True)
    phys_a=next(o for o in ta if o.get("offer")=="physical strict return veto")
    phys_b=next(o for o in tb if o.get("offer")=="physical strict return veto")
    assert phys_a["status"]=="guard refused" and phys_b["status"]=="changed"
    assert (bit_a,bit_b)==(1,0) and b.memory_word==a.memory_word=="101"
    assert state["x_here"]=="01" and path["current_degree"]>=2
    # Exchange against an otherwise identical local preparation after the
    # known paid history. Only one X comparison differs, and A was not changed.
    pair=[arm(device.LearnedKnotBot,False) for _ in range(2)]
    pair[1]._force("x_here",0,"X")
    needle={}
    for name in ("unaltered","sham","full_X","selected","erasure"):
        p,q=map(deepcopy,pair)
        start=[d._word for d in (p,q)]
        if name=="sham": p.sham();q.sham()
        if name=="full_X":p.exchange_second(q)
        if name=="selected":p.exchange_selected(q)
        if name=="erasure":p.erase_second();q.erase_second()
        outside=~sum(A.BANK_MASK[key] for key in A.SECOND_FIELDS)
        assert all((before & outside)==(d._word & outside) for before,d in zip(start,(p,q)))
        needle[name]=[p.read_prepared(),q.read_prepared()]
    assert needle=={"unaltered":[0,1],"sham":[0,1],"full_X":[1,0],"selected":[1,0],"erasure":[1,1]}
    # Play the corresponding physical game up to the archived query and
    # advance two clones for the real ON and OFF counterfactuals. The old
    # archive's first witness uses its original naming in both laws.
    assert path["variant"] == "original"
    game=FeederGame(sample_world(path["seed"],law,rounds=2),tape=path["tape"])
    for i,row in enumerate(rows[:-1]):
        assert game.observe()==obs(row)
        assert game.snapshot()["holder"]==path["route"][i]
        turn=game.step(int(row[4]==0))
        assert (1+turn.outgoing_slot if turn.outgoing_slot is not None else 0)==row[4]
        assert turn.energy_after==rows[i+1][1]
    o=game.observe()
    snap=game.snapshot()
    assert o==obs(rows[-1]) and snap["holder"]==path["current_holder"]
    assert snap["holder"] not in snap["available"]
    actual={}
    for bit in (0,1):
        replay=game.clone()
        turn=replay.step(bit)
        event=replay.last_event
        actual[str(bit)]={k:event[k] for k in ("turn","holder_before","holder_after","action","slot","consumed","energy_before","energy_after")}
    assert not actual["1"]["consumed"] and actual["1"]["energy_after"]==o.energy-1
    learned={}
    for name,kw in (("true",None),("opposite_credit",min(10,o.energy+3)),("disabled",None)):
        board=arm(device.LearnedKnotBot,True)
        assert board.read_prepared()==1 and board.candidate_votes()[0]
        new=board.after_turn(o,1,None,o.energy-1,training=name!="disabled",credit_energy_after=kw)
        learned[name]={"score":board.export(),"detected":new["detected"],"votes":new["votes"],
                       "credit_paid":new["credit_paid"],"final_M":new["memory_after"],
                       "final_X":new["second_after"]}
    assert [learned[k]["score"]["scores"][0] for k in learned]==[1,-4,0]
    assert [learned[k]["score"]["selector"] for k in learned]==[1,0,0]
    assert len({(x["final_M"],x["final_X"]) for x in learned.values()})==1
    return {"archive_seed":path["seed"],"archive_tape":path["tape"],"turn":path["turn"],
            "public":rows,"validation_only_route":path["route"],"latest_paid_holder":path["latest_paid"],
            "current_older_paid_holder":path["current_holder"],"M":state["m"],"X_here":state["x_here"],
            "fixed_strict_A_B":[bit_a,bit_b],"old_offer":phys_a,"repaired_offer":phys_b,
            "paired_prepared_word_actions":needle,"actual_archived_game_clones":actual,"charged_ON_control":learned,
            "outcome_scope":"single real archived public prefix and separately imposed local words and feedback"}


def result():
    files=(Path(__file__),HERE/"device.py",HERE/"device_design.md",HERE/"preregistration.md",HERE/"advisor.json",
           HERE.parent/"device.py",HERE.parent/"device_verified.json",HERE.parent/"device_science.json")
    return {"schema":"single-strict-guard-audit-v1","source_sha256":{str(p.relative_to(HERE.parent)):digest(p) for p in files},
            "physical_guard":physical_guard(),"law":{law:{"complete_queries":complete_queries(law),
                                                          "archived_example":paid_fixture(law)} for law in ("parity","nae")}}


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--verify",action="store_true");args=ap.parse_args()
    path=HERE/"device_verified.json"
    raw=(json.dumps(result(),indent=2,sort_keys=True)+"\n").encode()
    if args.verify:
        if raw!=path.read_bytes():raise SystemExit("Guard replay differs")
    else:
        path.write_bytes(raw)
    print(sha256(raw).hexdigest())
