"""Enumerate public pass-only prefixes and pair first qualifying real feeder encounters."""

from collections import Counter, defaultdict
from hashlib import blake2s
import json

from paired_game import FeederGame
from source_bank import LAWS, movement_tape, sample_pair


TAPES = 64
MAX_BLOCKS = 16
POSITIONS = 4


def rank(domain, *parts):
    payload = json.dumps(["FEEDER-PAYOFF-REVERSAL-20261121-001", domain, *parts],
                         ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return int.from_bytes(blake2s(payload, digest_size=8, person=b"FDPTRAIN").digest(), "big")


def local(observation):
    return [bool(observation.feeder), observation.energy, observation.previous, list(observation.slots)]


def departure_clue(obs, slot):
    if slot is None or (slot ^ 1) >= len(obs.slots):
        return None
    return "B" if slot % 2 else "A"


def scan(world, rep, tape):
    game = FeederGame(world, tape=tape)
    clue = None
    transcript = []
    route = []
    first = None
    masks = Counter()
    for turn in range(1, 7):
        obs = game.observe()
        snap = game.snapshot()
        route.append(snap["holder"])
        if turn >= 2:
            # Each mask has one bit for each potential query at turns 2,3,4,5,6.
            bit = 1 << (turn - 2)
            masks["reached"] |= bit
            if obs.feeder and len(obs.slots) == 3 and obs.previous == "move":
                masks["three_exit_feeder"] |= bit
                masks[clue if clue else "unpaired"] |= bit
                if clue and first is None:
                    assert snap["holder"] in snap["available"]
                    first = {"replicate": rep, "tape": tape, "turn": turn, "clue": clue,
                             "holder": snap["holder"], "formation": snap["formation"],
                             "current": local(obs), "route": route.copy(),
                             "prefix": transcript.copy()}
        if turn == 6:
            break
        transition = game.step(0)
        slot = transition.outgoing_slot
        clue = departure_clue(obs, slot)
        transcript.append([*local(obs), 0, slot, transition.energy_after])
        if transition.next_observation is None:
            break
    return first, {k: masks[k] for k in ("reached", "three_exit_feeder", "unpaired", "A", "B")}


def enroll(starts):
    ledgers = {law: {"founders": [], "pool": []} for law in LAWS}
    for source in starts:
        worlds = sample_pair(source, "train")
        for law, world in worlds.items():
            groups = defaultdict(lambda: {"A": [], "B": []})
            masks = []
            counts = Counter()
            for rep in range(TAPES):
                tape = movement_tape("train", source.source_key, rep)
                probe, mask = scan(world, rep, tape)
                masks.append(mask)
                for field in mask:
                    counts[field] += mask[field].bit_count()
                if probe is None:
                    continue
                c = probe["current"]
                key = probe["turn"], probe["formation"], probe["holder"], c[0], c[1], c[2], tuple(c[3])
                groups[key][probe["clue"]].append(probe)
                counts["first_" + probe["clue"]] += 1

            nominal = []
            for key, clues in sorted(groups.items()):
                a, b = clues["A"], clues["B"]
                nominal.append({"turn": key[0], "formation": key[1], "holder": key[2],
                                "A_replicates": [p["replicate"] for p in a], "B_replicates": [p["replicate"] for p in b]})
                n = min(len(a), len(b))
                counts["unmatched_first_A"] += len(a) - n
                counts["unmatched_first_B"] += len(b) - n
                counts["matched_pairs"] += n
                for pa, pb in zip(a, b):
                    assert pa["current"] == pb["current"] and pa["tape"] != pb["tape"]
                    serial = (source.source_key, key[0], pa["replicate"], pb["replicate"])
                    ledgers[law]["pool"].append({
                        "seed": source.seed, "source_key": source.source_key, "candidate_index": source.candidate_index,
                        "turn": key[0], "formation": key[1], "holder": key[2], "A": pa, "B": pb,
                        "rank": rank("rank", *serial), "tie": serial,
                    })
            counts["tapes"] = TAPES
            counts["tapes_without_nomination"] = TAPES - counts["first_A"] - counts["first_B"]
            counts["later_eligible_A"] = counts["A"] - counts["first_A"]
            counts["later_eligible_B"] = counts["B"] - counts["first_B"]
            ledgers[law]["founders"].append({
                "seed": source.seed, "source_key": source.source_key, "candidate_index": source.candidate_index,
                "first_funded": bool(world.attempts and world.attempts[0].births),
                "counts": dict(counts), "replicate_masks": masks, "nomination_groups": nominal,
            })

    for data in ledgers.values():
        pool = sorted(data.pop("pool"), key=lambda pair: (pair["rank"], pair["tie"]))
        n_all_blocks = len(pool) // POSITIONS
        n_use = min(n_all_blocks, MAX_BLOCKS) * POSITIONS
        selected = pool[:n_use]
        summary = sum((Counter(r["counts"]) for r in data["founders"]), Counter())
        summary.update({"founders": len(data["founders"]), "funded_founders": sum(f["first_funded"] for f in data["founders"]),
                        "source_keys_with_pairs": sum(f["counts"].get("matched_pairs", 0) > 0 for f in data["founders"]),
                        "selected_source_keys": len({p["source_key"] for p in selected}),
                        "available_complete_blocks": n_all_blocks, "selected_blocks": n_use // POSITIONS,
                        "selected_pairs": n_use, "incomplete_suffix_pairs": len(pool) % POSITIONS,
                        "cap_surplus_pairs": max(0, n_all_blocks * POSITIONS - n_use)})
        data["counts"] = dict(summary)
        data["selected"] = selected
        data["unused_pair_ids"] = [[q["seed"],q["turn"],q["A"]["replicate"],q["B"]["replicate"]] for q in pool[n_use:]]
        for i, pair in enumerate(selected):
            block, pos = divmod(i, POSITIONS)
            exception_slots = sorted(range(POSITIONS), key=lambda k: (rank("exception-position", block // 4, k), k))
            a_first = sorted(range(POSITIONS), key=lambda k: (rank("arrival-order", block, k), k))[:2]
            shuffle_a = sorted(range(POSITIONS), key=lambda k: (rank("shuffle-payer", block, k), k))[:2]
            pair.update(block=block, position=pos, pair_index=i, exception=exception_slots[block % 4] == pos,
                        A_first=pos in a_first, shuffled_payer="A" if pos in shuffle_a else "B")
    return ledgers
