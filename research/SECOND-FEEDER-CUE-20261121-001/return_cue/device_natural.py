"""Locate actual strict votes in natural games after locking B's physical words."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import bank
import device
from feeder_game import FeederGame


HERE = Path(__file__).resolve().parent
EXPECTED_WEIGHTS = "60767f960e50d2dbe499502a81c4605ca8480d61d5ad8b53b07b3d52fa777979"
FIELDS = ("episodes","turns","current_on_opportunities","raw_here","raw_older","strict_votes",
          "strict_votes_at_older_paid","strict_original_last_menu_mismatches","strict_current_empty",
          "actual_vetoes","strict_votes_at_latest","strict_votes_on_full","meals","older_certificates_off_opportunity")


def run():
    weights_raw = (HERE/"learning_weights.json").read_bytes()
    weights = json.loads(weights_raw)
    assert sha256(weights_raw).hexdigest() == EXPECTED_WEIGHTS
    data = {"weights_sha256":EXPECTED_WEIGHTS,"folds":{}}
    for fold in ("train","survival"):
        modes=("current",) if fold=="train" else ("current","learned")
        summary={}
        examples={}
        for start in bank.select_starts(fold):
            worlds=bank.sample_pair(start,fold)
            for mode in modes:
                for law,world in worlds.items():
                    board=device.LearnedKnotBot.from_frozen(law,weights["policies"][law]["trained"],mode=mode)
                    marks=summary.setdefault(mode,{}).setdefault(law,Counter({k:0 for k in FIELDS}))
                    for replicate in range(bank.TAPES):
                        tape=bank.movement_tape(fold,start.source_key,replicate)
                        game=FeederGame(world,tape=tape)
                        board.begin_episode()
                        meals=[]; paid=set()
                        marks["episodes"]+=1
                        while not game.done:
                            o=game.observe()
                            before_m=board.memory_word
                            here=bool(device.first.index(board._word,"x_here"))
                            bit=board.decide(o)
                            votes=board.candidate_votes()
                            turn=game.step(bit)
                            event=game.last_event
                            pos=event["holder_before"]
                            latest=meals[-1] if meals else None
                            current=bool(o.feeder and o.previous!="eat")
                            older=bool(here and pos!=latest)
                            full=event["food_before"]
                            marks["turns"]+=1
                            marks["current_on_opportunities"]+=current
                            marks["raw_here"]+=here
                            marks["raw_older"]+=older
                            marks["strict_votes"]+=votes[0]
                            marks["strict_votes_at_older_paid"]+=bool(votes[0] and older)
                            marks["strict_votes_at_latest"]+=bool(votes[0] and pos==latest)
                            marks["strict_votes_on_full"]+=bool(votes[0] and full)
                            marks["actual_vetoes"]+=bool(current and bit==0)
                            marks["older_certificates_off_opportunity"]+=bool(older and not current)
                            assert not here or pos in paid
                            assert votes[0] == int(current and here)
                            if votes[0]:
                                assert not full and older
                                assert before_m=="101" and len(o.slots)>=2
                                marks["strict_original_last_menu_mismatches"]+=1
                                marks["strict_current_empty"]+=1
                                x=examples.setdefault(mode,{})
                                x.setdefault(law,{"seed":start.seed,"tape":tape,"turn":event["turn"],
                                                  "previously_paid":list(meals),"current":pos,"latest_paid":latest,
                                                  "menu":len(o.slots),"M":before_m,"X_here":here,"bit":bit})
                            if event["consumed"]:
                                assert pos not in paid
                                paid.add(pos);meals.append(pos);marks["meals"]+=1
                            board.after_turn(o,bit,turn.outgoing_slot,turn.energy_after)
        data["folds"][fold]={"counts":summary,"first_strict_vote":examples}
    return data


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--verify",action="store_true");args=p.parse_args()
    raw=(json.dumps(run(),indent=2,sort_keys=True)+"\n").encode()
    path=HERE/"device_natural.json"
    if args.verify:
        if raw != path.read_bytes():raise SystemExit("Natural votes differ")
    else:path.write_bytes(raw)
    print(sha256(raw).hexdigest())
