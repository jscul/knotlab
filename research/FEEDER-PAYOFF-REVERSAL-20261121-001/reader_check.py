"""Replay the local reader on synthetic public transitions without opening a study world."""
from collections import Counter
from copy import copy
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

import reader as r

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.append(str(r.source.parent))
from feeder_game import Observation


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(x):
    return json.dumps(x, sort_keys=True, indent=2) + "\n"


def summary_hash(rows):
    return sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def fixture(score):
    """Externally prepared calibration only, independent of the update circuit."""
    word = "".join("01" if (score >> n) & 1 else "10" for n in range(32))
    return {"schema": r.SCHEMA, "bits": 32, "word": word, "score": score}


def view(feeder, energy, previous, width):
    return Observation(bool(feeder), energy, previous, tuple(range(width)))


def move(device, outward, width=3, energy=8, *, detail=False):
    obs = view(False, energy, "start", width)
    bit = device.decide(obs, probe_bit=0)
    return device.after_turn(obs, bit, outward, energy - 1, detail=detail)


def prepared(law, score, route, training):
    device = r.PayoffReader.from_memory(law, fixture(score)).begin_episode(training)
    if route is not None:
        move(device, 0 if route == "A" else 1)
    assert device.route_cue == route and device.score == score
    return device


def count_law(word, law):
    if word < 0 or word >= 1 << len(r.ALL):
        return False
    for holding in r.STARS.values():
        bits = [bool((word >> name) & 1) for name in holding]
        if law == "parity" and sum(bits) % 2:
            return False
        if law == "nae" and not (any(bits) and not all(bits)):
            return False
    return True


def audit_trace(before, after, trace, law, counts):
    current = before
    for row in trace:
        assert row["before"] == current
        following = row["after"]
        if "offer" in row:
            a, b = row["operands"]
            owners_a = {h for h, marks in r.STARS.items() if a in marks}
            owners_b = {h for h, marks in r.STARS.items() if b in marks}
            assert a != b and owners_a == owners_b and row["holder"] in owners_a
            guard = [(n, v) for n, v in row["guard"]]
            assert len({n for n, v in guard}) == len(guard)
            assert all(n not in (a,b) and n in r.STARS[row["holder"]] for n,v in guard)
            actual = [(current >> n) & 1 for n, v in guard]
            assert actual == row["guard_actual"]
            unequal = (current >> a) & 1 != (current >> b) & 1
            guard_holds = all(x == v for x, (n,v) in zip(actual, guard, strict=True))
            predicted = "guard refused" if not guard_holds else ("changed" if unequal else "equal operands")
            assert row["status"] == predicted
            flipped = (1 << a) | (1 << b) if predicted == "changed" else 0
            assert current ^ following == flipped
            assert row["toggled"] == ([a,b] if flipped else [])
            counts[predicted] += 1
        else:
            bank = row["bank"]
            assert bank in ("route_out", "a_out", "m_out")
            assert not ((current ^ following) & ~r.BANK_MASK[bank])
            assert row["exported"] == r.old.code(current, r.NAMES[bank])
            assert row["incoming"] == r.old.code(following, r.NAMES[bank])
            assert row["exported"].count("1") == row["incoming"].count("1")
            counts["external token replacement"] += 1
        if following != current:
            assert count_law(following, law) and r.lawful(following,law)
        current = following
    assert current == after


def structural():
    private = {"M":"memory_slack", "K":"action_slack", "R":"route_slack", "C":"score_slack",
               "H":"coupler_slack"}
    for h, name in private.items():
        assert r.OWNERS[r.NAMES[name][0]] == (h,)
    for h in ("M","K","R","C"):
        others = set(r.STARS[h]) - set(r.NAMES[private[h]])
        assert all(set(r.OWNERS[n]) == {h,"H"} for n in others)
    assert len(r.STARS["H"]) >= 3 and all(1 <= len(owners) <= 2 for owners in r.OWNERS.values())
    checked = {}
    for law in ("nae","parity"):
        symbols = ("a","b","c","s")
        forbidden = [w for w in product((0,1), repeat=4)
                     if (sum(w) in (0,4) if law=="nae" else sum(w) % 2 == 1)]
        cnf = ";".join(" ".join(("~" if val else "") + sym for sym, val in zip(symbols, w))
                       for w in forbidden)
        env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
        proc = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
                               "--loops", *symbols[:3], "--contact", symbols[-1], "--json"],
                              cwd=ROOT, env=env, capture_output=True, text=True, check=True)
        actual = json.loads(proc.stdout)
        assert all(actual[k] for k in ("is_knot","binding","coexistence","invisible_in_parts"))
        checked[law] = {"width":4, "allowed":len(actual["allowed"]), "canonical":actual["is_knot"]}
        assert count_law(r.initial_word(law), law)
    return {"names":len(r.ALL), "actual_holder_widths":{h:len(s) for h,s in r.STARS.items()},
            "maximum_holders_per_name":max(map(len,r.OWNERS.values())),
            "canonical_representative_four_place_checker":checked,
            "full_projection_argument": [
                "Every leaf has one private slack and shares its other names only with H. Any allowed H word extends separately to each leaf. At parity its private slack fixes parity. At NAE choose a slack opposite any already assigned mark.",
                "Any allowed leaf word extends to H using the private H slack, and to the other leaves using their respective private slacks. Thus every displayed full relation is the local projection of the actual joint system.",
                "At all five actual widths both full relations have a forbidden word, a permitted word, and every complete assignment after forgetting any mark has a completion. The finite check on four marks represents M, K and R exactly; the construction proves the large widths without materializing their truth tables.",
            ]}


def actions():
    rows = []
    for law, score, route, training in product(("nae","parity"),(-29, 0, 23),(None,"A","B"),(False,True)):
        base = prepared(law, score, route, training)
        for previous, n, feeder in product(("start","move","eat","refused"), range(6),(False,True)):
            obs = view(feeder,7,previous,n)
            fast, full = copy(base), copy(base)
            is_current = feeder and previous != "eat"
            veto = not training and is_current and n == 3 and (
                (score < 0 and route == "A") or (score > 0 and route == "B"))
            expected = int(is_current and not veto)
            fast.checkpoint(obs)
            full.checkpoint(obs,detail=True)
            assert fast.word == full.word and fast.action_word == "100"
            got = fast.read_prepared()
            actual, log = full.read_prepared(detail=True)
            assert got == actual == expected == ((full.word >> 6) & 1)
            assert full.action_word == ("001" if expected else "010") and full.word == fast.word
            assert r.lawful(full.word,law) and full.score == score
            for forced in (0,1):
                p = copy(base)
                assert p.decide(obs, probe_bit=forced) == forced
                assert p.action_word == ("001" if forced else "010")
            rows.append([law,score,route,training,previous,n,feeder,got])
    return {"natural_rows":len(rows),"forced_rows":2*len(rows),"natural_bites":sum(row[-1] for row in rows),
            "full_offer_and_indexed_word_equality_rows":len(rows),"rows_sha256":summary_hash(rows)}


def receipt_matrix(counts):
    rows = []
    for law, route, e, actual, alternate in product(("nae","parity"),(None,"A","B"),(1,7,10),
                                                   (False,True),(None,False,True)):
        dev = prepared(law,0,route,True)
        obs = view(True,e,"move" if route else "start",3)
        fast = copy(dev)
        start = dev.word
        trace = dev.checkpoint(obs,detail=True)
        audit_trace(start,dev.word,trace,law,counts)
        start = dev.word
        bit, trace = dev.read_prepared(probe_bit=1,detail=True)
        audit_trace(start,dev.word,trace,law,counts)
        assert fast.decide(obs,probe_bit=1) == bit
        energy = min(10,e+3) if actual else e-1
        start = dev.word
        rec = dev.after_turn(obs,bit,None,energy,credit_override=alternate,detail=True)
        audit_trace(start,dev.word,rec["offers"],law,counts)
        simple = fast.after_turn(obs,1,None,energy,credit_override=alternate)
        assert dev.word == fast.word and simple == {k:v for k,v in rec.items() if k != "offers"}
        accepted = actual if alternate is None else alternate
        expected = int(accepted)*(int(route=="A")-int(route=="B"))
        assert rec["eligible"] == (route is not None) and rec["actual_paid"] == actual
        assert rec["credit_paid"] == accepted and rec["score_after"] == expected
        assert dev.memory_word == ("011" if actual else "110")
        rows.append([law,route,e,actual,alternate,rec["score_after"],dev.memory_word])
    return {"rows":len(rows),"public_before_energies":[1,7,10],"rows_sha256":summary_hash(rows)}


def carry_checks():
    rows = []
    def signed(u):
        u %= 2**32
        return u-2**32 if u >= 2**31 else u
    for law, cue, size in product(("nae","parity"),("A","B"),range(33)):
        old = signed((1 << size)-1 if cue=="A" else 1 << size)
        dev = prepared(law,old,cue,True)
        obs = view(True,7,"move",3)
        b = dev.decide(obs)
        val = dev.after_turn(obs,b,None,10)["score_after"]
        assert val == signed(old + (1 if cue=="A" else -1))
        rows.append([law,cue,size,old,val])
    return {"rows":len(rows),"all_carry_and_borrow_lengths_up_to":32,
            "operational_fit_maximum_eligible_bites":16*4*2, "exact_signed_training_limit":2**31-1,
            "rows_sha256":summary_hash(rows)}


def route_checks(counts):
    rows = []
    for law, prior, width in product(("nae","parity"),(None,"A","B"),range(6)):
        for outward in range(width) if width else (None,):
            dev = prepared(law,0,prior,False)
            obs = view(False,7,"move",width)
            dev.checkpoint(obs)
            bit = dev.read_prepared(probe_bit=0)
            start=dev.word
            rec=dev.after_turn(obs,bit,outward,6,detail=True)
            audit_trace(start,dev.word,rec["offers"],law,counts)
            next_cue = prior if outward is None else (
                ("A","B")[outward%2] if (outward ^ 1) < width else None)
            assert dev.route_cue == rec["next_route_cue"] == next_cue
            meal=view(True,6,"move",3)
            bit=dev.decide(meal,probe_bit=1)
            assert dev.after_turn(meal,bit,None,9)["next_route_cue"] == next_cue
            dev.begin_episode()
            assert dev.route_cue is None
            rows.append([law,prior,width,outward,next_cue])
    return {"actual_move_or_refusal_rows":len(rows),"bite_stays_checked":len(rows),
            "rows_sha256":summary_hash(rows)}


def illustrative_fit(law, version, alternate_order, arm):
    device = r.PayoffReader(law)
    score_trail = []
    payments = []
    for pair in range(4):
        order = ("B","A") if (pair % 2 == 1) ^ alternate_order else ("A","B")
        for cue in order:
            device.begin_episode(training=True)
            move(device,0 if cue=="A" else 1)
            obs=view(True,7,"move",3)
            bit=device.decide(obs,probe_bit=1)
            genuine = (cue == ("A" if pair < 3 else "B")) ^ bool(version)
            credit = None if arm=="outcome" else (True if arm=="count" else (cue=="A") == (pair < 2))
            receipt=device.after_turn(obs,bit,None,10 if genuine else 6,credit_override=credit)
            score_trail.append([cue,receipt["actual_paid"],receipt["credit_paid"],device.score])
            payments.append(int(receipt["actual_paid"]))
    return device.export_memory(), score_trail, payments


def synthetic_fit():
    rows={}
    for law in ("nae","parity"):
        for version in (0,1):
            for order in (False,True):
                for arm in ("outcome","count","shuffled"):
                    word,trail,paid=illustrative_fit(law,version,order,arm)
                    assert word["score"] == ((2 if not version else -2) if arm=="outcome" else 0)
                    assert sum(paid)==4 and Counter(r[0] for r in trail)=={"A":4,"B":4}
                    rows[f"{law}/{version}/{int(order)}/{arm}"] = {"score":word["score"],
                          "public_payment_sequence":paid,"score_trail_sha256":summary_hash(trail)}
        assert rows[f"{law}/0/0/outcome"]["public_payment_sequence"] == rows[f"{law}/1/1/outcome"]["public_payment_sequence"]
    return {"purpose":"Synthetic wiring calibration; independent primary training uses actual paid game bites.",
            "eight_bites_per_fixture":True,"trained":rows}


def interventions(counts):
    rows = []
    for law, cue in product(("nae","parity"),("A","B")):
        devices=[]
        for version in (0,1):
            export, _, _ = illustrative_fit(law,version,False,"outcome")
            dev=r.PayoffReader.from_memory(law,export).begin_episode()
            one=view(True,7,"start",1)
            bit=dev.decide(one)
            dev.after_turn(one,bit,None,10)
            move(dev,0 if cue == "A" else 1,energy=10)
            obs=view(True,9,"move",3)
            dev.checkpoint(obs)
            assert dev.memory_word=="101" and dev.action_word=="100" and dev.route_cue==cue
            devices.append(dev)
        x,y=devices
        n=x.nonmemory_snapshot()
        assert n==y.nonmemory_snapshot()
        ox,oy=x.snapshot(),y.snapshot()
        bx,by=x.word,y.word
        tx,ty=x.swap_learned(y,detail=True)
        audit_trace(bx,x.word,tx,law,counts)
        audit_trace(by,y.word,ty,law,counts)
        assert x.nonmemory_snapshot()==y.nonmemory_snapshot()==n
        assert x.snapshot()==oy and y.snapshot()==ox
        transferred=[copy(x).read_prepared(),copy(y).read_prepared()]
        x.swap_learned(y)
        assert x.snapshot()==ox and y.snapshot()==oy
        original=[copy(x).read_prepared(),copy(y).read_prepared()]
        assert transferred == original[::-1] and original[0]!=original[1]
        b=x.word
        trace=x.sham(detail=True)
        audit_trace(b,x.word,trace,law,counts)
        assert x.snapshot()==ox
        exported,trace=x.clear_learned(detail=True)
        audit_trace(b,x.word,trace,law,counts)
        assert x.score==0 and x.nonmemory_snapshot()==n and copy(x).read_prepared()==1
        b=x.word
        trace=x.restore_learned(exported,detail=True)
        audit_trace(b,x.word,trace,law,counts)
        assert x.snapshot()==ox
        rows.append({"law":law,"route":cue,"observed_first_memory":"101","ready":"100",
                     "original_bits":original,"transferred_bits":transferred,"erased_bit":1,
                     "reciprocal_changed_pairs":len(tx),"restored_entire_word":True})
    return rows


def explicit_refusals():
    cases = {}
    def rejects(name, dev, call):
        prior=dev.snapshot()
        try:
            call()
        except ValueError as exc:
            assert prior == dev.snapshot()
            cases[name]=str(exc)
        else:
            raise AssertionError(name)
    dev=r.PayoffReader("nae").begin_episode()
    obs=view(True,8,"start",3)
    rejects("missing_checkpoint",dev,lambda:dev.read_prepared())
    rejects("interference_outside_checkpoint",dev,lambda:dev.clear_learned())
    dev.checkpoint(obs)
    rejects("occupied_preparation",dev,lambda:dev.checkpoint(obs))
    rejects("nonbit_prefix",dev,lambda:dev.read_prepared(probe_bit=3))
    broken=dev.export_memory()
    broken["score"]=1
    rejects("damaged_donor_word",dev,lambda:dev.restore_learned(broken))
    assert dev.read_prepared(probe_bit=0)==0
    rejects("wrong_physical_action",dev,lambda:dev.after_turn(obs,1,None,10))
    rejects("missing_real_move",dev,lambda:dev.after_turn(obs,0,None,7))
    rejects("undisplayed_control",dev,lambda:dev.after_turn(obs,0,3,7))
    rejects("unpaid_move_made_energy",dev,lambda:dev.after_turn(obs,0,1,10))
    rejects("different_starting_observation",dev,lambda:dev.after_turn(view(True,9,"start",3),0,1,8))
    rejects("deployed_counterfactual_receipt",dev,lambda:dev.after_turn(obs,0,1,7,credit_override=1))
    dev.after_turn(obs,0,1,7)
    assert dev.route_cue=="B"
    return cases


def record():
    counts=Counter()
    return {"study":"FEEDER-PAYOFF-REVERSAL-20261121-001",
            "evidence":"synthetic structural and public-transition calibrations; no held-out games sampled",
            "bound_sources":{"reader_design.md":digest(HERE/"reader_design.md"),
                             "reader.py":digest(HERE/"reader.py"), "reader_check.py":digest(Path(__file__)),
                             "inherited_keeper.py":digest(r.source)},
            "structure":structural(),"actions":actions(), "receipt_control_matrix":receipt_matrix(counts),
            "arithmetic":carry_checks(), "route":route_checks(counts),"synthetic_balanced_exposure":synthetic_fit(),
            "prepared_interventions":interventions(counts),"explicit_refusals":explicit_refusals(),
            "independently_audited_detailed_events":dict(sorted(counts.items()))}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=record()
    target=HERE/"reader_checks.json"
    calculated=dump(data)
    if args.write:
        target.write_text(calculated,encoding="utf-8")
    elif target.read_text(encoding="utf-8")!=calculated:
        raise SystemExit("Reader calibration receipt differs")
    print(f"{'wrote' if args.write else 'verified'} {digest(target)} {target.name}")
