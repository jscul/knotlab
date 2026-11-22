"""Rebuild choices, ledgers, match membership and both energy comparisons from holdings."""

from collections import Counter, defaultdict
from functools import lru_cache
import gzip
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "FEEDER-MEMORY-20261121-001"
sys.path.append(str(OLD))
from history_verify import controls, move, seedpart
from bank import sample_pair, select_starts


def read(path):
    with gzip.open(path, "rt") as f:
        return json.load(f)


def layout(world):
    stages = []
    for s in world.stages:
        owners = defaultdict(list)
        for h, names in enumerate(s.holdings):
            for name in names:
                owners[name].append(h)
        links = [[] for _ in s.holdings]
        for name, pair in owners.items():
            if len(pair) == 2:
                a, b = pair
                links[a].append((name, b))
                links[b].append((name, a))
        stages.append(tuple(tuple(port) for port in links))
    epochs = []
    born = set()
    idx = 0
    for j in range(2):
        if j < len(world.attempts):
            a = world.attempts[j]
            idx = a.stage
            born.update(b.holder for b in a.births)
        epochs.append((stages[idx], frozenset(born), idx))
    init = Random(seedpart("cursor", world.seed)).randrange(len(world.stages[0].holdings))
    return init, epochs


def identity(p, side):
    branch = p[side]
    return (p["law"], p["seed"], branch["replicate"], p["turn"], tuple(branch["attempt_turns"]))


def energy_control(v, epochs):
    seed, tape, turn, pos, energy, spent = (v[k] for k in ("seed", "tape", "turn", "holder", "energy", "spent"))
    links, born, _ = epochs[turn >= 5]
    result = []
    for bit in (0, 1):
        meals = set(spent)
        where = pos
        charge = energy - 1
        if bit == 1:
            if where in born and where not in meals:
                meals.add(where)
                charge = min(10, charge + 4)
        else:
            slots = controls(seed, tape, pos, links[pos])
            where = slots[move(tape, turn, len(slots))][1]
        if charge:
            _, new_born, _ = epochs[turn + 1 >= 5]
            charge = min(10, charge - 1 + 4 * (where in new_born and where not in meals))
        result.append(charge)
    return result


def verify():
    source_list = {s.seed: s for s in select_starts("mechanism")}
    @lru_cache(maxsize=128)
    def physical(seed, law):
        return layout(sample_pair(source_list[seed], "mechanism")[law])
    stats = defaultdict(Counter)
    raw = {}
    contexts = defaultdict(lambda: [[], []])
    finite = defaultdict(lambda: ({}, {}))
    all_schedules = [t for n in range(3) for t in combinations(range(1, 11), n)]
    for cell in read(HERE / "panel_runs.json.gz"):
        law, seed, rep, tape = [cell[k] for k in ("law", "seed", "replicate", "tape")]
        init, epochs = physical(seed, law)
        finished = set()
        seen = set()
        for ep in cell["terminal_prefixes"]:
            pos, energy, previous = init, 6, 0
            paid, spent, attempts, path, public = [], [], [], [], []
            for turn, row in enumerate(ep["public"], 1):
                links, born, stage = epochs[turn >= 5]
                slot_list = controls(seed, tape, pos, links[pos])
                local = (pos in born, energy, previous, len(slot_list))
                full = pos in born and pos not in spent
                assert local == tuple(row[:-1]) and pos == ep["route"][turn - 1]
                path.append(pos)
                word = (*public, (*local, -1))
                key = (law, seed, rep, turn, tuple(attempts))
                if key not in seen:
                    seen.add(key)
                    stats[law]["distinct_visits"] += 1
                    if local[0]:
                        stats[law]["feeder_visits"] += 1
                        for c, k in zip(finite[law], (local, word)):
                            c[k] = c.get(k, 0) | (1 << full)
                    if paid and local[0]:
                        stats[law]["after_paid_feeder_visits"] += 1
                        first = 1 if public[paid[-1]-1][3] == 1 else 2
                        contexts[law, seed, turn, local, first, len(paid)][full].append(key)
                        raw[key] = {"seed": seed, "tape": tape, "turn": turn, "holder": pos, "energy": energy,
                                    "first": first, "public": word, "full": full, "route": tuple(path),
                                    "spent": tuple(spent), "meal_turns": tuple(paid), "stage": stage}
                issued = turn in ep["attempt_turns"]
                after = energy - 1
                if issued:
                    assert row[-1] == 0
                    attempts.append(turn)
                    if full:
                        paid.append(turn)
                        spent.append(pos)
                        after = min(10, after + 4)
                    previous = 1
                else:
                    slot = move(tape, turn, len(slot_list))
                    assert row[-1] == slot + 1
                    pos = slot_list[slot][1]
                    previous = 2
                public.append(tuple(row))
                assert energy > 0
                energy = after
            assert energy == 0 and list(paid) == ep["meal_turns"]
            represented = {w for w in all_schedules if tuple(t for t in w if t <= len(public)) == tuple(attempts)}
            assert len(represented) == ep["schedules_represented"] and not represented & finished
            finished.update(represented)
            stats[law]["schedule_decisions"] += len(represented) * len(public)
        assert len(finished) == 56
        stats[law]["scheduled_games"] += len(finished)

    expected = set()
    for (law, seed, turn, local, old_m, n_paid), (empty, full) in contexts.items():
        _, epochs = physical(seed, law)
        links, _, _ = epochs[turn >= 5]
        for k1, k2 in product(empty, full):
            if k1[2] // 2 != k2[2] // 2:
                continue
            e, f = raw[k1], raw[k2]
            a, b = e["holder"], f["holder"]
            assert a in e["spent"] and b not in f["spent"]
            if a != b and a in f["spent"] and b not in e["spent"] and len(links[a]) == len(links[b]):
                expected.add(("primary" if k1[2] == k2[2] else "cross", k1, k2))
            if (k1[2] == k2[2] and a == b and
                    any(h not in e["spent"] and len(links[h]) == len(links[a]) for h in f["spent"])):
                expected.add(("secondary", k1, k2))
    result = json.loads((HERE / "panel_results.json").read_text())
    checked = set()
    for p in read(HERE / "panel_pairs.json.gz"):
        k1, k2 = [identity(p, side) for side in ("empty", "full")]
        key = (p["panel"], k1, k2)
        assert key in expected and key not in checked
        checked.add(key)
        _, epochs = physical(p["seed"], p["law"])
        links, born, idx = epochs[p["turn"] >= 5]
        a, b = p["A"], p["B"]
        assert a != b and {a, b} <= born and len(links[a]) == len(links[b]) == p["degree"] and p["stage"] == idx
        vals = []
        for side, k in (("empty", k1), ("full", k2)):
            v = raw[k]
            spec = p[side]
            assert v["full"] == (side == "full")
            assert v["holder"] == spec["holder"] and v["route"] == tuple(spec["route"])
            assert v["public"] == tuple(map(tuple, spec["public"])) and v["spent"] == tuple(spec["paid_in_order"])
            assert v["meal_turns"] == tuple(spec["meal_turns"]) and spec["first_memory"] == v["first"]
            vals.append(energy_control(v, epochs))
        assert vals == p["two_turn_energy_off_on"]
        assert (vals[0][0] > vals[0][1] and vals[1][1] > vals[1][0]) == p["strict_opposite_two_turn_gain"]
        stats[p["law"]][p["panel"] + "_pairs"] += 1
    assert expected == checked
    for law, s in result["per_law"].items():
        for k in ("scheduled_games", "schedule_decisions", "distinct_visits", "feeder_visits", "after_paid_feeder_visits"):
            assert stats[law][k] == s["all"][k]
        for name, buckets in zip(("current_only_finite", "complete_history_finite"), finite[law]):
            data = s["support"][name]
            assert len(buckets) == data["classes"] and sum(v == 3 for v in buckets.values()) == data.get("mixed_classes", 0)
        for panel, counts in s["panels"].items():
            assert stats[law][panel + "_pairs"] == counts.get("pairs", 0)
    out = {"passed": True, "checked": "Physical movements and energy, each schedule partition, both observation class counts, every pair and its two counterfactual outcomes per branch.",
           "per_law": {l: dict(s) for l, s in stats.items()}}
    (HERE / "panel_verified.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    verify()
