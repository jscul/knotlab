"""Replay the marked histories selected by the round-five implication screen."""

import argparse
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass, field
import gzip
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

import replay


SCREEN = Path(__file__).resolve().with_name("mark_heard5.jsonl")
PILOT = ("n4:g17:0232@0", "g7:122@0", ("ORD", "J-EACH-PART", None))
PILOT_TARGET = 70


def key(row):
    return row["A"], row["B"], tuple(row["law"])


class RosterRead:
    """Record the roster before births and the demand before fresh distinctions."""

    def __init__(self, engine):
        self.engine = engine
        self.members = None
        self.demand = Counter()

    def build_roster(self, state, members, where, guard, parts=False):
        if where == "roster":
            self.members = {"members": len(members), "own members": sorted(
                state.names[u] for u, _, _ in members if state.roles[u] == replay.RECEIVER)}
        roster = self.engine.build_roster(state, members, where, guard, parts=parts)
        counts = Counter(u for group in roster.groups for u in group)
        if where == "roster":
            short = [u for u, held, _ in members if counts[u] > held]
            self.members.update({"short": len(short), "made short": sum(bool(state.parents[u]) for u in short),
                                 "own short": sum(state.roles[u] == replay.RECEIVER for u in short)})
        else:
            self.demand = counts
        return roster


@dataclass
class Trace:
    growth: replay.Growth = field(default_factory=replay.Growth)
    rosters: list = field(default_factory=list)
    births: list = field(default_factory=list)
    refused_roster: dict | None = None


def trace(engine, state, names, take, choice, prefix=None, tracked=None):
    """Use the independent round and save birth details before releasing each state."""
    if prefix is None:
        result = Trace()
    else:
        first = replay.EDIT_AFTER
        result = Trace(replay.Growth(rounds=prefix.growth.rounds[:first]),
                       prefix.rosters[:first], prefix.births[:first])
    growth = result.growth
    guard = engine.Guard(replay.GUARD_MULT)
    while len(growth.rounds) < replay.ROUNDS:
        current = len(growth.rounds) + 1
        roster = RosterRead(engine)
        count, distinctions = len(state.places), len(state.holders)
        try:
            state, observation = replay.step(roster, state, names, take, choice, guard)
        except engine.GuardStop as error:
            growth.ended = "guard"
            growth.guard = {"round": current, "count": error.what, "value": error.value, "step": error.where}
            result.refused_roster = roster.members
            break
        growth.rounds.append(observation)
        result.rosters.append(roster.members)
        if prefix is None:
            growth.linked.append(replay.affiliation(state)[0])
            if current == replay.EDIT_AFTER:
                growth.edit_state = state
        births = {}
        for u in range(count, len(state.places)):
            name = state.names[u]
            places = state.places[u]
            # Only the fresh suffix is numbered at or above the previous bound.
            ninputs = bisect_left(places, distinctions)
            birth = {"knot": u, "parents": state.parents[u], "role": state.roles[u],
                     "inputs": ninputs, "provisional demand": roster.demand[u],
                     "fresh": len(places) - ninputs, "places": len(places),
                     "implied": name in observation.implied}
            if tracked and u in tracked.get(current, ()):
                birth["input distinctions"] = places[:ninputs]
            births[name] = birth
        result.births.append(births)
        if len(state.places) > replay.KNOT_BOUND:
            growth.ended = "knots"
            break
    growth.knots = len(state.places)
    return result


def summarize(read):
    return {
        "endpoint": read.growth.endpoint(),
        "rounds": [dict(roster, **{"own births": len(obs.own), "implied": len(obs.implied),
                                    "implied with demand": obs.implied_owed})
                   for roster, obs in zip(read.rosters, read.growth.rounds)],
        "roster at guard": read.refused_roster,
    }


def verify_discrepancies(screen, baseline, recorded, actual):
    contrast = replay.comparison(recorded.growth, actual.growth)
    first = screen["first differing round"]
    assert contrast["implied births differing by identity"][0][0] == first
    a, b = recorded.growth.rounds[first - 1], actual.growth.rounds[first - 1]
    ra, rb = recorded.births[first - 1], actual.births[first - 1]
    details = []
    for name in sorted(a.implied ^ b.implied):
        left, right = ra[name], rb[name]
        expected = next(row for row in screen["births"] if row["id"] == left["knot"])
        assert left["knot"] == right["knot"]
        assert left["parents"] == right["parents"] == tuple(expected["parents"])
        assert left["provisional demand"] == right["provisional demand"] == expected["demand"]
        assert left["input distinctions"] == right["input distinctions"] == tuple(expected["inputs"])
        assert left["implied"] == expected["archived rule"] and right["implied"] == expected["rule of current places"]
        # The basis first changes funding at one already specified birth.
        # Retain the input count and its archive location without copying the roster.
        details.append({"identity": name, "receiver's own": left["role"] == replay.RECEIVER,
                        "baseline": baseline.births[first - 1].get(name),
                        "recorded": {k: v for k, v in left.items() if k != "input distinctions"},
                        "actual": {k: v for k, v in right.items() if k != "input distinctions"}})
    assert len(details) == len(screen["births"])
    return {"round": first, "births": details}


def run(engine, archived, discrepancies):
    started = perf_counter()
    ration, take, choice = archived["law"]
    assert ration == "ORD" and archived["knot law"] == "parity"
    start = replay.joined_start(archived["A"], archived["B"])
    names = replay.BirthNames(len(start.places))
    baseline = trace(engine, start, names, take, choice)
    base = baseline.growth
    assert len(base.rounds) == archived["rounds"] and base.ended == archived["ended"]
    assert base.linked == archived["linked"]
    assert [r.made_short for r in base.rounds] == archived["made short"]
    targets = list(replay.targets(base.edit_state))
    assert len(targets) == len(archived["changes"])
    archive_by_knot = {u: (placement, row) for (u, placement), row in zip(targets, archived["changes"])}
    comparisons = []
    for screen in discrepancies:
        placement_started = perf_counter()
        u, first = screen["target"], screen["first differing round"]
        expected_ids = {first: [b["id"] for b in screen["births"]]}
        recorded_state, actual_state, witness = replay.edited_states(base.edit_state, u)
        layout, archive_read = archive_by_knot[u]
        recorded = trace(engine, recorded_state, names, take, choice, baseline, expected_ids)
        actual = trace(engine, actual_state, names, take, choice, baseline, expected_ids)
        old_read = replay.comparison(base, recorded.growth)
        new_read = replay.comparison(base, actual.growth)
        old_first, new_first = (next(iter(c["own birth difference rounds"]), None) for c in (old_read, new_read))
        assert archive_read == screen["archive reading"] == dict(**layout, heard=old_first,
                                                                  rounds=old_read["common rounds"])
        comparisons.append({
            "target": u, **layout, "basis witness": witness, "archived intervention": summarize(recorded),
            "actual basis intervention": summarize(actual), "archived first hearing": old_first,
            "actual basis first hearing": new_first, "baseline against archived": old_read,
            "baseline against actual": new_read,
            "archived against actual": replay.comparison(recorded.growth, actual.growth),
            "first implication discrepancy": verify_discrepancies(screen, baseline, recorded, actual),
            "wall seconds": round(perf_counter() - placement_started, 4),
        })
        print(json.dumps({"key": key(archived), "target": u, "first hearings": [old_first, new_first],
                          "wall seconds": comparisons[-1]["wall seconds"]}), file=sys.stderr, flush=True)
    return {"key": key(archived), "baseline": summarize(baseline), "placements": comparisons,
            "wall seconds": round(perf_counter() - started, 4),
            "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("pilot", "remaining"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (replay.MEMORY_LIMIT, replay.MEMORY_LIMIT))
    archive = [json.loads(line) for line in gzip.decompress(replay.verified(replay.ARCHIVE, replay.ARCHIVE_SHA)).splitlines()]
    found = {key(row): row for row in archive if any(c["heard"] == 5 for c in row.get("changes", []))}
    screened = [json.loads(line) for line in SCREEN.read_text().splitlines()]
    keys = [key(row) for row in screened]
    if len(keys) != len(set(keys)) or not set(keys) <= found.keys():
        raise ValueError("The screen contains repeated or unsupported pair-and-law entries")
    if args.mode == "remaining" and set(keys) != found.keys():
        raise ValueError(f"The screen has read {len(keys)} of {len(found)} required entries")

    replay.verified(replay.KERNEL, replay.KERNEL_SHA)
    sys.path.insert(0, str(replay.KERNEL.parent))
    import eng

    started = perf_counter()
    results = []
    for row in screened:
        case = key(row)
        selected = [d for d in row["discrepancies"]
                    if ((case, d["target"]) == (PILOT, PILOT_TARGET)) == (args.mode == "pilot")]
        if selected:
            results.append(run(eng, found[case], selected))
    assert args.mode != "pilot" or len(results) == 1
    output = {"commit": "0e332122a3", "mode": args.mode, "round-five hearing records": len(found),
              "records screened at launch": len(keys), "wall seconds": round(perf_counter() - started, 4),
              "address space bytes": replay.MEMORY_LIMIT, "results": results}
    with args.out.open("x", encoding="utf-8") as out:
        json.dump(output, out, indent=2)
        out.write("\n")


if __name__ == "__main__":
    main()
