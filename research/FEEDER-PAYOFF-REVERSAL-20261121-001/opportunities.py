"""Check actual fresh bite payoffs under matched approaches and all reached knot projections."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from paired_game import ReversalGame, derive_clue
from source_bank import BANK_PATH, LAWS, excluded_keys, movement_tape, sample_pair, select_starts


HERE = Path(__file__).resolve().parent
GENERATORS = "GENERATORS-20261120-001A"
FIXTURES = HERE.parents[1] / "experiments" / GENERATORS / (GENERATORS + "-E001_generators")
sys.path.append(str(FIXTURES))
from fixtures import certify_source  # noqa: E402


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def first_probe(world, tape, version, mirror):
    game = ReversalGame(world, tape=tape, version=version, mirror=mirror)
    clue = None
    for turn in range(1, 7):
        if game.done:
            break
        observation = game.observe()
        if (turn >= 2 and clue is not None and observation.feeder and
                observation.previous == "move" and len(observation.slots) == 3):
            bill = game.step(1)
            event = game.last_event
            paid = bill.energy_after >= observation.energy
            assert event["eligible"] and event["food_before"] and event["approach"] == clue
            assert paid == event["consumed"] and paid != event["denied"]
            return {"turn": turn, "holder": event["holder_before"], "clue": clue,
                    "paid": paid, "energy_before": observation.energy, "energy_after": bill.energy_after}
        move = game.step(0)
        if move.outgoing_slot is not None:
            clue = derive_clue(observation, move.outgoing_slot)
    return None


def run(weights_sha):
    if digest(HERE / "learned_words.json") != weights_sha:
        raise ValueError("This comparison requires the released physical words.")
    excluded = set(excluded_keys())
    seen = set()
    source = {}
    scores = {law: Counter() for law in LAWS}
    rewards = {law: {str(v): {k: 0 for k in ("A", "A_paid", "B", "B_paid")} for v in (0, 1)} for law in LAWS}
    probes = []
    for fold in ("train", "mechanism", "heldout"):
        source[fold] = {law: Counter() for law in LAWS}
        for start in select_starts(fold):
            assert start.source_key not in seen | excluded
            seen.add(start.source_key)
            for law, world in sample_pair(start, fold).items():
                counts = source[fold][law]
                counts["founders"] += 1
                counts["growth_stalls_on_first_attempt"] += int(len(world.stages) == 1)
                for stage in world.stages:
                    certify_source(stage.holdings, law)
                    counts["reached_stages"] += 1
                    counts["projected_holders"] += len(stage.holdings)
                if fold != "heldout":
                    continue
                for replicate in range(8):
                    tape = movement_tape(fold, start.source_key, replicate)
                    block = [[first_probe(world, tape, v, m) for m in (False, True)] for v in (0, 1)]
                    sc = scores[law]
                    sc["original_founder_tapes"] += 1
                    if block[0][0] is None:
                        assert all(probe is None for pair in block for probe in pair)
                        sc["no_focal_arrival"] += 1
                        continue
                    assert all(probe is not None for pair in block for probe in pair)
                    assert len({(p["turn"], p["holder"], p["energy_before"]) for pair in block for p in pair}) == 1
                    for v, pair in enumerate(block):
                        assert {p["clue"] for p in pair} == {0, 1} and sum(p["paid"] for p in pair) == 1
                        for m, p in enumerate(pair):
                            q = "AB"[p["clue"]]
                            rewards[law][str(v)][q] += 1
                            rewards[law][str(v)][q+"_paid"] += int(p["paid"])
                            assert p["paid"] != block[1-v][m]["paid"]
                            assert p["paid"] == block[1-v][1-m]["paid"]
                    sc["matched"] += 1
                    probes.append({"law": law, "founder": start.seed, "replicate": replicate,
                                   "tape": tape, "versions_by_code": block})
    return {"bank_sha256": digest(BANK_PATH), "weights_sha256": weights_sha,
            "excluded_structures": len(excluded), "new_distinct_structures": len(seen),
            "verified_sources_by_fold": source, "first_arrival_coverage": scores,
            "real_bites": rewards, "first_arrivals": probes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights-sha", required=True)
    parser.add_argument("--out", type=Path, default=HERE / "opportunity_results.json")
    args = parser.parse_args()
    data = run(args.weights_sha)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"coverage": data["first_arrival_coverage"], "bites": data["real_bites"]}))


if __name__ == "__main__":
    main()
