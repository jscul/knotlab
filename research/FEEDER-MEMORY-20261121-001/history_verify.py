"""Audit every terminal prefix, observation class and matched pair from the saved raw data."""

from collections import Counter, defaultdict
from functools import lru_cache
import gzip
from hashlib import blake2s
from itertools import combinations
import json
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "KNOT-RATION-GAME-20261121-001"
sys.path.insert(0, str(PRIOR))
from world import sample_world


def seedpart(domain, *values):
    payload = "|".join((domain, *(str(x) for x in values))).encode("ascii")
    return int.from_bytes(blake2s(payload, person=b"RATGAME1", digest_size=8).digest(), "big")


@lru_cache(maxsize=4096)
def layout(seed, law, variant):
    world = sample_world(seed, law, rounds=2)
    largest = max(x for stage in world.stages for holding in stage.holdings for x in holding)
    name = (lambda x: largest - x) if variant == "renamed" else (lambda x: x)
    snapshot = []
    for stage in world.stages:
        owned = defaultdict(list)
        for h, row in enumerate(stage.holdings):
            for distinction in row:
                owned[name(distinction)].append(h)
        links = [[] for _ in stage.holdings]
        for d, holders in owned.items():
            if len(holders) == 2:
                a, b = holders
                links[a].append((d, b))
                links[b].append((d, a))
        snapshot.append(tuple(tuple(x) for x in links))
    versions = []
    newborns = set()
    stage_index = 0
    for i in range(2):
        if len(world.attempts) > i:
            a = world.attempts[i]
            stage_index = a.stage
            newborns.update(b.holder for b in a.births)
        versions.append((snapshot[stage_index], frozenset(newborns)))
    start = Random(seedpart("cursor", seed)).randrange(len(world.stages[0].holdings))
    return start, versions


@lru_cache(maxsize=32768)
def controls(seed, tape, pos, raw_links):
    return tuple(sorted(raw_links, key=lambda linked: (seedpart("slot", seed, tape, pos, linked[0]), linked[0])))


@lru_cache(maxsize=32768)
def move(tape, turn, count):
    return Random(seedpart("port", tape, turn)).randrange(count)


def read_gzip(path):
    with gzip.open(path, "rt") as stream:
        return json.load(stream)


def identity(meta):
    return tuple(meta[k] for k in ("law", "seed", "tape", "variant"))


def audit(suffix=""):
    results = json.loads((HERE / f"history_results{suffix}.json").read_text())
    runs = read_gzip(HERE / f"history_runs{suffix}.json.gz")
    pairs = read_gzip(HERE / f"history_pairs{suffix}.json.gz")
    expected = defaultdict(set)
    per_law = defaultdict(Counter)
    classes = defaultdict(lambda: ({}, {}))
    raw_prefixes = {}
    schedules = [w for n in range(3) for w in combinations(range(1, 11), n)]
    for meta in runs:
        cell = identity(meta)
        law, seed, tape, variant = cell
        origin, versions = layout(seed, law, variant)
        prefix_rows = {}
        finished = set()
        for trial in meta["terminal_prefixes"]:
            energy = 6
            pos = origin
            previous = 0
            route = []
            past = []
            attempts = []
            paid = []
            spent = set()
            used = tuple(trial["attempt_turns"])
            for turn, raw in enumerate(trial["public"], 1):
                links, born = versions[turn >= 5]
                offered = controls(seed, tape, pos, links[pos])
                full = pos in born and pos not in spent
                local = (pos in born, energy, previous, len(offered))
                assert local == tuple(raw[:-1]), (cell, turn, local, raw)
                assert trial["route"][turn - 1] == pos
                route.append(pos)
                public = (*past, (*local, -1))
                entry = (len(past) + 1, pos, local, len(paid), full, public, tuple(sorted(spent)), tuple(route))
                prefix = (turn, tuple(attempts))
                if prefix in prefix_rows:
                    assert prefix_rows[prefix] == entry
                else:
                    prefix_rows[prefix] = entry
                bit = turn in used
                gained = 0
                if bit:
                    assert raw[-1] == 0
                    attempts.append(turn)
                    if full:
                        gained = 4
                        spent.add(pos)
                        paid.append(turn)
                    previous = 1
                else:
                    assert offered
                    slot = move(tape, turn, len(offered))
                    assert raw[-1] == slot + 1
                    pos = offered[slot][1]
                    previous = 2
                past.append(tuple(raw))
                assert energy > 0
                energy = min(10, energy - 1 + gained)
            assert energy == trial["end_energy"] == 0
            assert list(paid) == trial["meal_turns"]
            stopped = [s for s in schedules if tuple(t for t in s if t <= len(past)) == used]
            assert len(stopped) == trial["schedules_represented"]
            assert not finished.intersection(stopped)
            finished.update(stopped)
            per_law[law]["schedule_decisions"] += len(stopped) * len(past)
        assert len(finished) == 56
        per_law[law]["schedules"] += len(finished)
        per_law[law]["distinct_visits"] += len(prefix_rows)
        groups = defaultdict(lambda: [[], []])
        for prefix, value in prefix_rows.items():
            turn, pos, local, n_paid, full, public, spent, route = value
            if not local[0]:
                continue
            for sname in (variant, "paired_mixture"):
                for i, key in enumerate((local, public)):
                    st = classes[law, sname][i]
                    st[key] = st.get(key, 0) | (2 if full else 1)
            raw_prefixes[cell, prefix] = value
            if local[2] == 2 and n_paid:
                groups[turn, pos, local, n_paid][full].append(prefix)
        for lows, highs in groups.values():
            expected[cell].update((low, high) for low in lows for high in highs)

    observed = defaultdict(set)
    for p in pairs:
        cell = identity(p)
        prefix_pair = []
        target = p["target_holder"]
        for label in ("empty", "full"):
            branch = p[label]
            k = p["turn"], tuple(branch["attempt_turns"])
            prefix_pair.append(k)
            _, pos, local, n_paid, full, public, spent, route = raw_prefixes[cell, k]
            assert pos == target and local == tuple(p["current"])
            assert full == (label == "full") and n_paid >= 1
            assert spent == tuple(branch["spent_holders"]) and tuple(branch["route"]) == route
            assert public == tuple(tuple(x) for x in branch["public"])
        index = tuple(prefix_pair)
        assert index not in observed[cell]
        observed[cell].add(index)
    assert all(observed[cell] == v for cell, v in expected.items())
    assert all(expected[cell] == v for cell, v in observed.items())
    for law, vals in results["per_law"].items():
        assert per_law[law]["schedules"] == vals["runs"]["fixed_schedules"]
        assert per_law[law]["schedule_decisions"] == vals["runs"]["turns_counting_all_schedules"]
        assert per_law[law]["distinct_visits"] == vals["support"]["paired_mixture"]["counts"]["all_visits"]
        for variant, summary in vals["support"].items():
            for i, name in enumerate(("current_only_finite", "complete_history_finite")):
                buckets = classes[law, variant][i]
                assert len(buckets) == summary[name]["classes"]
                assert sum(v == 3 for v in buckets.values()) == summary[name].get("mixed_classes", 0)
        witness = vals["opposite_history_example"]
        if witness:
            assert witness["empty"]["public"] == witness["full"]["public"]
            for label in ("empty", "full"):
                w = witness[label]
                cell = identity(w)
                prefix = len(w["public"]), tuple(w["attempt_turns"])
                assert raw_prefixes[cell, prefix][4] == (label == "full")
        per_law[law]["matched_pairs"] = sum(len(s) for cell, s in observed.items() if cell[0] == law)
    out = {"independent_source": "Per-name owner lists in ordinary growth, independent seeded movement and energy reconstruction.",
           "per_law": {k: dict(v) for k, v in per_law.items()}, "all_checks_passed": True}
    (HERE / f"history_verification{suffix}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    audit("_extension" if "--extension" in sys.argv[1:] else "")
