"""Replay the strict return scope and the physically learned cue controls.

Only the event scorer below sees actual holders and rations. Inputs to the
device are the public rows or the observation and publicly exposed outcome.
"""
import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import gzip
import json
from pathlib import Path

from bank import HERE, B306, LAWS, TAPES, Start, movement_tape, sample_pair
from device import CUES, LearnedKnotBot, SECOND_FIELDS
from feeder_game import FeederGame, Observation
from history_reader import PREVIOUS_CODE


PREVIOUS = {v: k for k, v in PREVIOUS_CODE.items()}
COUNT_NAMES = ("prefixes", "turns", "public_current_on", "on_same_first_memory",
               "raw_here", "raw_here_older", "strict_votes", "strict_votes_older")


@dataclass
class Marks:
    here: bool = False
    departed: bool = False
    last_type: int = 0

    def advance(self, move, paid, degree, turn):
        if paid:
            self.last_type = min(degree, 2)
        if move:
            self.here, self.departed = (self.departed and degree == 1 and turn >= 5,
                                        self.here and turn >= 5)
        else:
            self.here = self.here or paid


def unpack(public):
    feeder, energy, prev, degree, action = public
    return Observation(bool(feeder), energy, PREVIOUS[prev], tuple(range(degree))), action


def read_trace(public, route, meals, counts=None):
    known, last, m, last_older = set(), None, Marks(), None
    if counts is not None:
        counts["prefixes"] += 1
    for turn, (row, holder) in enumerate(zip(public, route, strict=True), 1):
        feeder, energy, prev, degree, action = row
        current = bool(feeder and prev != PREVIOUS_CODE["eat"])
        same = bool(current and m.last_type and m.last_type == min(degree, 2))
        strict = bool(same and m.here)
        if m.here and holder not in known:
            raise AssertionError("A physical certificate identified an unconsumed ration.")
        if strict and holder != last:
            raise AssertionError("A strict vote identified an older paid site.")
        if counts is not None:
            counts["turns"] += 1
            counts["public_current_on"] += current
            counts["on_same_first_memory"] += same
            counts["raw_here"] += m.here
            counts["raw_here_older"] += m.here and holder != last
            counts["strict_votes"] += strict
            counts["strict_votes_older"] += strict and holder != last
        if m.here and holder != last and last_older is None:
            last_older = {"turn": turn, "current_holder": holder, "latest_paid": last,
                          "current_degree": degree, "paid_menu_type": m.last_type,
                          "strict_vote": strict, "public": public[:turn], "route": route[:turn],
                          "meal_turns": sorted(t for t in meals if t < turn)}
        if turn in meals:
            assert feeder and action == 0 and holder not in known
            known.add(holder)
            last = holder
        m.advance(action > 0, turn in meals, degree, turn)
    return strict, last_older


def raw_counts():
    out = {}
    for name, path in (("earlier_forced", B306/"history_runs.json.gz"),
                       ("fresh_forced", HERE/"panel_runs.json.gz")):
        summary = {law: Counter({k: 0 for k in COUNT_NAMES}) for law in LAWS}
        fixtures = {}
        with gzip.open(path, "rt") as h:
            blocks = json.load(h)
        for block in blocks:
            law = block["law"]
            for prefix in block["terminal_prefixes"]:
                _, older = read_trace(prefix["public"], prefix["route"], set(prefix["meal_turns"]), summary[law])
                if older is not None and law not in fixtures:
                    fixtures[law] = {k: block[k] for k in ("seed","variant","tape","replicate") if k in block} | older
        out[name] = {"counts": summary, "first_older": fixtures,
                     "weighting": "one counted prefix per stored terminal path, one appearance per turn of that prefix"}
    return out


def natural_counts():
    starts = json.loads((HERE/"bank.json").read_bytes())["folds"]
    out = {}
    for fold in ("train","survival"):
        stats = {}
        for data in starts[fold]:
            start = Start(**data)
            worlds = sample_pair(start, fold)
            for law, world in worlds.items():
                for replicate in range(TAPES):
                    tape = movement_tape(fold, start.source_key, replicate)
                    game = FeederGame(world,tape=tape)
                    public, route, meals = [], [], set()
                    while not game.done:
                        obs = game.observe()
                        bit = int(obs.feeder and obs.previous != "eat")
                        t = game.step(bit)
                        s = t.outgoing_slot
                        event = game.last_event
                        public.append([obs.feeder, obs.energy, PREVIOUS_CODE[obs.previous], len(obs.slots),
                                       0 if bit else -2 if s is None else 1 + s])
                        route.append(event["holder_before"])
                        if event["consumed"]:
                            meals.add(len(route))
                    read_trace(public,route,meals,stats.setdefault(law,Counter({k: 0 for k in COUNT_NAMES})))
        out[fold] = stats
    return out


def board_checkpoint(law, public):
    board = LearnedKnotBot(law,mode="strict_return").begin_episode()
    for i,row in enumerate(public[:-1]):
        obs, action = unpack(row)
        board.decide(obs)
        board.after_turn(obs,int(action==0),action-1 if action>0 else None,public[i+1][1])
    board.checkpoint(unpack(public[-1])[0])
    return board


def pair_reads(pair):
    boards = [board_checkpoint(pair["law"],pair[side]["public"]) for side in ("empty","full")]
    marks = {k:[dict(b.snapshot())[k] for b in boards] for k in ("m","a","selector",*SECOND_FIELDS)}
    reads = {}
    for arm in ("original","sham","exchange","selected_only","erased","equal_input"):
        a,b = deepcopy(boards[0]),deepcopy(boards[1])
        if arm=="sham":
            a.sham(); b.sham()
        if arm=="exchange":
            a.exchange_second(b)
        if arm=="selected_only":
            a.exchange_selected(b)
        if arm in ("erased","equal_input"):
            a.erase_second(); b.erase_second()
        if arm=="equal_input":
            a.exchange_second(b)
        reads[arm]=[a.read_prepared(),b.read_prepared()]
    assert reads == {"original":[0,1],"sham":[0,1],"exchange":[1,0],"selected_only":[1,0],
                     "erased":[1,1],"equal_input":[1,1]}
    return {"roles":{side:{k:pair[side][k] for k in ("public","route","meal_turns","verdict","tape")
                           if k in pair[side]} for side in ("empty","full")},
            "identity":{k:pair[k] for k in ("seed","source_key","law","variant","turn","panel","A","B")
                        if k in pair},
            "words_at_checkpoint":marks,"actions_by_intervention":reads}


def forced_positives():
    out = {}
    for name,path in (("older", B306/"history_pairs.json.gz"), ("fresh", HERE/"panel_pairs.json.gz")):
        with gzip.open(path,"rt") as s:
            pairs = json.load(s)
        rows = {l:{} for l in LAWS}
        first = {}
        for p in pairs:
            l=p["law"]; panel=p.get("panel","B306 archive")
            rec=rows[l].setdefault(panel,Counter(pairs=0,positive=0,both_certified_positive=0))
            rec["pairs"]+=1
            required=("empty","full")
            types=[b["first_memory"] if "first_memory" in b else
                   min(2,b["public"][b["meal_turns"][-1]-1][3]) if b["meal_turns"] else 0
                   for b in (p[s] for s in required)]
            if types[0]!=types[1]:
                continue
            strict=[read_trace(p[s]["public"],p[s]["route"],set(p[s]["meal_turns"]))[0] for s in required]
            if strict!=[True,False]:
                continue
            rec["positive"]+=1
            proven=all(p[side]["verdict"]==side for side in required)
            rec["both_certified_positive"]+=proven
            if panel in ("primary","B306 archive") and (l not in first or proven and not first[l][0]):
                first[l]=(proven,p)
        out[name]={"panels":rows,"witness":{l:pair_reads(pair) for l,(_,pair) in first.items()}}
    return out


def changed_experience(law):
    fixture=[(False,6,"start",2,0,0,5), (True,5,"move",2,1,None,8),
             (True,8,"eat",2,0,0,7), (False,7,"move",1,0,0,6),
             (True,6,"move",2,1,None,5)]
    boards={k:LearnedKnotBot(law).begin_episode(training=True) for k in ("true","opposite_credit","disabled_update")}
    rows={}
    for k,b in boards.items():
        for i,(f,e,prev,deg,bit,s,ea) in enumerate(fixture):
            obs=Observation(f,e,prev,tuple(range(deg)))
            assert bit==b.decide(obs)
            result=b.after_turn(obs,bit,s,ea,training=k!="disabled_update",
                                credit_energy_after=9 if k=="opposite_credit" and i==len(fixture)-1 else None)
        rows[k]={"words":b.export(),"votes_on_final":result["votes"],"actual_paid":result["detected"],
                 "physical_credit":result["credit_paid"],"final_M":b.memory_word,"final_X":list(b.second_word)}
    for k in rows:
        d=LearnedKnotBot.from_frozen(law,rows[k]["words"]).begin_episode()
        for f,e,prev,deg,bit,s,ea in fixture[:-1]:
            obs=Observation(f,e,prev,tuple(range(deg)))
            d.decide(obs); d.after_turn(obs,bit,s,ea)
        target=Observation(True,6,"move",(0,1))
        d.checkpoint(target)
        rows[k]["action_same_query"]=d.read_prepared()
    assert [rows[k]["action_same_query"] for k in rows]==[0,1,1]
    assert len({(v["final_M"],tuple(v["final_X"])) for v in rows.values()})==1
    return {"public_fixture":[list(x) for x in fixture],"controls":rows,
            "scope":"constructed local public-input control, not a sampled game or the fitted deployment"}


def credit_sequence():
    raw=json.loads((HERE/"learning_training.json").read_bytes())["packets_by_law"]
    out={}
    for law,packets in raw.items():
        votes=[[0,0] for _ in range(4)]; s=[0]*4; counts=Counter(); prev=0; switches=[]
        ordinal=0
        for packet in packets:
            for row in packet["ordered_evidence"]:
                ordinal+=1
                for i,v in enumerate(row["votes"]):
                    if v:
                        votes[i][int(row["paid"])]+=1
                        s[i]=max(-7,min(7,s[i]+(-4 if row["paid"] else 1)))
                selected=1+s.index(max(s)) if max(s)>0 else 0
                counts[CUES[selected]]+=1
                if selected!=prev:
                    switches.append({"informative_receipt":ordinal,"from":CUES[prev],"to":CUES[selected],
                                     "scores":list(s),"seed":row["seed"],"tape":row["tape"],"turn":row["turn"]})
                    prev=selected
            assert s==packet["trained"]["scores"] and selected==packet["trained"]["selector"]
        out[law]={"informative_receipts":ordinal,"votes_unpaid_paid":votes,"post_informative_selectors":counts,
                  "switches":switches,"final_scores":s,"final_selector":CUES[selected]}
    return out


def run():
    return {"schema":"second-cue-device-scope-v1","credit":credit_sequence(),
            "natural_current_only":natural_counts(),"forced_traces":raw_counts(),"strict_pairs":forced_positives(),
            "physical_credit_calibration":{l:changed_experience(l) for l in LAWS}}


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--verify", action="store_true");args=p.parse_args()
    path=HERE/"device_science.json"
    payload=(json.dumps(run(),indent=2,sort_keys=True)+"\n").encode()
    if args.verify:
        if payload!=path.read_bytes():
            raise SystemExit("Device science replay differs")
    else:
        path.write_bytes(payload)
    print("Device scope receipts verified." if args.verify else "Device scope receipts written.")
