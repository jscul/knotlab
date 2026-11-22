"""Exact keeper receipts at the public interface and native-offer controls.

The short synthetic transcripts here are device calibrations. A separate game
census must verify reachability, matching and ration truth on real game paths.
"""
import argparse
from collections import Counter
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import keeper as k

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "keeper_receipts.json"


def summarize_events(events, law, retain_changed=False):
    counts = Counter()
    kept = []
    for row in events:
        assert k.admissible(row["before"], law) and k.admissible(row["after"], law)
        if "external_exchange" in row:
            counts["supplied ready token"] += 1
            if retain_changed and row["before"] != row["after"]:
                kept.append(row)
            continue
        counts[row["status"]] += 1
        actually = tuple(i for i in k.ALL if k.get(row["before"], i) != k.get(row["after"], i))
        assert list(row["toggled"]) == [i for i in row["operands"] if i in actually]
        assert all(i in row["operands"] for i in actually)
        if row["status"] == "changed":
            assert len(actually) == 2
            if retain_changed:
                kept.append(row)
    result = {"offers_by_disposition": dict(counts), "checked_complete_words": 2 * len(events)}
    if retain_changed:
        result["changed_offers_and_nonready_exports"] = kept
    return result


def word_diff(a, b):
    return {n: [dict(a)[n], dict(b)[n]] for n in dict(a) if dict(a)[n] != dict(b)[n]}


def receipt_calibration(law, typ, *, writer=True, reader=True):
    dev = k.KnotKeeper(law, writer=writer, reader=reader)
    # A controlled historical ON at menu type 1/2. The decision read is under
    # the same query later. These public histories alone are not a claim about
    # the existence of a particular itinerary in the underlying growth game.
    payment = dev.after_turn(True, typ, 6, 1, 9, detail=True)
    capture = summarize_events(payment.pop("offers"), law, True)
    if writer:
        assert payment["addressed_receipt_word"] == k.MEMORY_CODES[typ]
    assert dev.memory_word == (k.MEMORY_CODES[typ] if writer else k.MEMORY_CODES[0])
    costs = []
    payment_memory = dev.memory_word
    for cue, slots, e, on, following in [(False, 1, 9, 0, 8), (True, 1, 8, 1, 7)]:
        event = dev.after_turn(cue, slots, e, on, following, detail=True)
        costs.append(summarize_events(event.pop("offers"), law))
        assert not event["detected"] and dev.memory_word == payment_memory
    prep = summarize_events(dev.checkpoint(True, 1, detail=True), law)
    return dev, {"write": payment, "actual_write": capture, "later_retention_turns": costs, "prepared": prep}


def paired(law):
    a, ra = receipt_calibration(law, 1)
    b, rb = receipt_calibration(law, 2)
    x, y = deepcopy(a), deepcopy(b)
    before = [d.snapshot() for d in (x, y)]
    assert set(word_diff(before[0], before[1])) == {"m"}
    events = x.exchange_memory(y, detail=True)
    after = [d.snapshot() for d in (x, y)]
    assert all(set(word_diff(ref, new)) == {"m"} for ref, new in zip(before, after))
    assert x.memory_word == b.memory_word and y.memory_word == a.memory_word
    def arms(first, second):
        rs = []
        for d in (first, second):
            bit, t = d.read_prepared(detail=True)
            rs.append({"action_bit": bit, "actual_word": d.action_word,
                       "physical_read": summarize_events(t, law, True)})
        return rs
    base = arms(deepcopy(a),deepcopy(b))
    exchanged = arms(x,y)
    shams = []
    for d in (a,b):
        s = deepcopy(d)
        undo = s.sham(detail=True)
        assert s.snapshot() == d.snapshot()
        shams.append(summarize_events(undo, law, True))
    assert [r["action_bit"] for r in base] == [0,1]
    assert [r["action_bit"] for r in exchanged] == [1,0]
    clamp = []
    for mark in k.MEMORY_CODES:
        c,d = deepcopy(a),deepcopy(b)
        c.clamp_memory(mark);d.clamp_memory(mark)
        s,t = c.snapshot(), d.snapshot()
        c.exchange_memory(d)
        assert (s,t) == (c.snapshot(),d.snapshot())
        u,v = c.read_prepared(), d.read_prepared()
        assert u == v
        clamp.append({"retained_memory":mark,"common_bit":u})
    disabled = []
    for writer,reader in [(False,True),(True,False),(False,False)]:
        e, _ = receipt_calibration(law,1, writer=writer,reader=reader)
        f, _ = receipt_calibration(law,2, writer=writer,reader=reader)
        data = arms(e,f)
        assert data[0]["action_bit"] == data[1]["action_bit"]
        disabled.append({"writer":writer,"reader":reader,"action_words":[p["actual_word"] for p in data],
                         "action_bits":[p["action_bit"] for p in data]})
    return {"one_type_history":ra,"many_type_history":rb,"ready_states":list(map(dict,before)),
            "crossed_states":list(map(dict, after)), "cross_offers":[summarize_events(t,law,True) for t in events],
            "sham_double_transpositions":shams,"original_reads":base,"reciprocal_reads":exchanged,
            "equal_mark_controls":clamp,"disabled_arms":disabled}


def complete_interface(law):
    trials = 0
    menus = (0,1,2,5)
    # Build both nonempty records by genuine previous receipts.
    produced = {}
    for old in range(3):
        d = k.KnotKeeper(law)
        if old:
            d.after_turn(True,old,6,1,9)
        for cue,n in product((False,True),menus):
            physical = deepcopy(d)
            physical.checkpoint(cue,n)
            a, trace = physical.read_prepared(detail=True)
            expected = int(cue and not (n and min(n,2)==old))
            assert a==expected and physical.action_word==k.ACTION_CODES[1+expected]
            assert sum(r["status"]=="changed" for r in trace)==1
            produced[f"{d.memory_word}/{int(cue)}/{n}"]=[a,physical.action_word]
        for e,n,cue,act in product(range(1,11), menus, (False,True), (0,1)):
            possibilities = {e-1}
            if cue and act:
                possibilities.add(min(10,e+3))
            for e1 in sorted(possibilities):
                trial=deepcopy(d)
                rec=trial.after_turn(cue,n,e,act,e1,detail=True)
                detected=bool(act and e1>=e)
                address=min(2,n) if detected else 0
                wanted=k.MEMORY_CODES[address] if address else d.memory_word
                assert rec["detected"]==detected and trial.memory_word==wanted
                assert rec["exported_previous_memory"]==(d.memory_word if address else k.MEMORY_CODES[0])
                summarize_events(rec["offers"],law)
                trials+=1
    return {"public_transition_cases_including_no_receipt_unaddressed_overwrite_and_cap":trials,
            "query_outputs_from_one_fixed_action_name":produced}


def physical_prefix(public, law):
    """Use only the sealed public transcript, independent of host route/stock labels."""
    dev = k.KnotKeeper(law)
    paid = []
    for turn, (previous, following) in enumerate(zip(public, public[1:]), 1):
        cue, energy, _, slots, action_code = previous
        rec = dev.after_turn(cue, slots, energy, int(action_code == 0), following[1])
        if rec["detected"]:
            paid.append({"turn": turn, "old_menu": slots, "energy": [energy, following[1]],
                         "memory_word": rec["memory_after"]})
    cue, _, _, slots, pending = public[-1]
    assert pending == -1
    dev.checkpoint(cue, slots)
    return dev, paid


def game_witness():
    records = json.loads((HERE / "decisive_replays.json").read_text())["by_law"]
    out = {}
    for law, obj in records.items():
        selected = obj["pair"]
        branches = {side: physical_prefix(selected[side]["public"], law) for side in ("empty","full")}
        pre = [branches[s][0] for s in ("empty","full")]
        assert set(word_diff(pre[0].snapshot(), pre[1].snapshot())) == {"m"}
        rows = {}
        for arm in ("original","sham","swapped"):
            l, r = (deepcopy(b) for b in pre)
            if arm == "swapped":
                l.exchange_memory(r)
            elif arm == "sham":
                l.sham()
                r.sham()
            actual = []
            for side, b in zip(("empty","full"), (l,r)):
                assert dict(b.snapshot()) == obj["arms"][arm][side]["after_intervention"]
                paid_type = b.memory_word
                bit = b.read_prepared()
                assert bit == obj["arms"][arm][side]["bit"]
                actual.append({"side":side,"memory_after_intervention":paid_type,
                               "action_word":b.action_word,"single_bit":bit})
            rows[arm] = actual
        out[law] = {"turn":selected["turn"],"seed":selected["seed"],"tape":selected["tape"],
                    "current_public":selected["current"],"paid_public_updates":{s:d[1] for s,d in branches.items()},
                    "actual_outputs":rows,"agreement_with_host_physical_states_and_bits":True,
                    "prefix_is_natural_keeper_rollout":{s:obj["branches"][s]["prefix_agrees_with_own_output"]
                                                        for s in branches}}
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--verify",action="store_true")
    ap.add_argument("--game",action="store_true",help="Check the coordinator's two actual selected public prefixes")
    args=ap.parse_args()
    if args.game:
        path=HERE / "keeper_game_check.json"
        data=game_witness()
        raw=json.dumps(data,indent=2,sort_keys=True)+"\n"
        if args.verify:
            assert raw == path.read_text()
        else:
            path.write_text(raw)
        print({law:v["actual_outputs"]["swapped"] for law,v in data.items()})
        return
    data={"schema":"B306-keeper-1","scope":"Lawful device calibrations. Actual matched ration-game paths are counted separately.",
          "physical_holdings": k.STARS,"physical_named_banks":k.NAMES,
          "one_actuator_mark":k.A[2],"one_many_intervention_sole_marks": k.M[:2],"laws":{}}
    for law in k.LAW:
        data["laws"][law]={"matched_calibration":paired(law),"complete_interface":complete_interface(law)}
    raw=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if args.verify:
        assert raw==OUTPUT.read_text()
    else:
        OUTPUT.write_text(raw)
    print({law:v["complete_interface"]["public_transition_cases_including_no_receipt_unaddressed_overwrite_and_cap"]
           for law,v in data["laws"].items()})


if __name__=="__main__":
    main()
