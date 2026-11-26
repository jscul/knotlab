"""Replay selected confirmed form cases from the frozen starts and seeds."""

import argparse
import json
import math
import resource
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from random import Random
from statistics import NormalDist
from time import perf_counter

import networkx as nx

from c_growth import Law, Roster, State, descend, form, grow, initial_state, roster, same_form


ROOT = Path(__file__).resolve().parents[3]
CENSUS = ROOT / "research/MADE-COPIER-20261125-001C/starts_c.json"
RECORDS = ROOT / "artifacts/MADE-COPIER-20261125-001C/MADE-COPIER-20261125-001C-E001_copier_by_sampling"
KINDS = ("BN", "BY", "BX", "BM", "BT")
RATE_FIELDS = {"BN": "q1", "BY": "q0", "BX": "qY", "BM": "qM", "BT": "qT"}
MET_NAMES = {"BY": "Ybarred", "BX": "Yown", "BM": "masked", "BT": "fully_masked"}
Z95 = NormalDist().inv_cdf(0.975)


def loose_counts(reading: Roster, part: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((len(reading.usable[k]), len(reading.barred_loose.get(k, ()))) for k in part))


@dataclass(frozen=True)
class Form:
    counts: tuple[tuple[int, int], ...]
    incidence: nx.Graph | None

    @classmethod
    def of(cls, reading: Roster, part: tuple[int, ...]) -> "Form":
        # A two-member part has exactly one maximal met set, the pair.
        return cls(loose_counts(reading, part), form(reading, part) if len(part) > 2 else None)

    def matches(self, reading: Roster, part: tuple[int, ...]) -> bool:
        if len(part) != len(self.counts) or loose_counts(reading, part) != self.counts:
            return False
        return self.incidence is None or same_form(self.incidence, form(reading, part))


@dataclass(frozen=True)
class Outcome:
    meeting: int | None
    first_form: int | None
    form_after_meeting: int | None


def read_form(states: list[State], x: tuple[int, ...], y: tuple[int, ...],
              target: Form, x_matches_y: bool, y_own: bool = False) -> Outcome:
    start_round = states[0].round
    meeting = first_form = after_meeting = None
    wanted = 2 if y_own else 1
    for state in states[1:]:
        reading = roster(state)  # The mask affects growth and demand only.
        labels = descend(state, x, y, start_round)
        if meeting is None:
            for part in reading.parts:
                ancestry = 0
                for member in part:
                    ancestry |= labels[member]
                if ancestry == 3:
                    meeting = state.round
                    break
        if x_matches_y and not y_own:
            continue
        matches = 0
        for part in reading.parts:
            if (len(part) == len(target.counts)
                    and all(labels[k] == wanted for k in part)
                    and any(state.knots[k].made > start_round for k in part)
                    and target.matches(reading, part)):
                matches += 1
        if matches >= 2:
            if first_form is None:
                first_form = state.round
            if meeting is not None and after_meeting is None:
                after_meeting = state.round
    return Outcome(meeting, first_form, after_meeting)


def eligible_pairs(state: State, reading: Roster, seed: str, every_pair: bool):
    part_of = {k: part for part in reading.parts for k in part}
    linked = nx.Graph()
    linked.add_nodes_from(reading.parts)
    for holders in state.holders:
        holding_parts = {part_of[k] for k in holders if k in part_of}
        linked.add_edges_from(combinations(holding_parts, 2))
    class_of = {part: index for index, group in enumerate(nx.connected_components(linked)) for part in group}
    pairs = [(x, y) for x in sorted(reading.parts)
             if all(state.knots[k].made > 0 for k in x)
             for y in sorted(reading.parts) if class_of[x] != class_of[y]]
    if not every_pair and len(pairs) > 8:
        pairs = Random(f"{seed}|P|{state.round}").sample(pairs, 8)
    return pairs


def seed_for(case: dict, law: Law) -> str:
    seed = f"C|{case['start']}|{law.ration}|{law.treatment}|{law.relation}|{case['i']}"
    if law.taking != "MET":
        seed += f"|{law.taking}"
    if law.release == "HOLD":
        seed += "|HOLD"
    return seed + ("|T2" if law.weighting == "T2" else "")


def continue_seed(seed: str, kind: str, round_number: int, index: int) -> str:
    base = seed.removesuffix("|T2")
    suffix = "|T2" if base != seed else ""
    return f"{base}|{kind}|{round_number}|{index}{suffix}"


def read_arm(state: State, law: Law, seed: str, x: tuple[int, ...], y: tuple[int, ...],
             target: Form, x_matches_y: bool, kind: str, first: int, end: int) -> dict:
    arm = kind.removesuffix("3")
    event_indices = []
    any_form_indices = []
    meeting_indices = []
    limited = {}
    terminal = Counter()
    start = perf_counter()
    for index in range(first, end):
        states, reason = grow(
            state, law, continue_seed(seed, kind, state.round, index), x=x, y=y,
            barred={"BY": y, "BX": x}.get(arm, ()), mask=arm in ("BM", "BT"), fully_masked=arm == "BT",
        )
        outcome = read_form(states, x, y, target, x_matches_y, y_own=arm == "BX")
        event = outcome.form_after_meeting if arm == "BN" else outcome.first_form
        if event is not None:
            event_indices.append(index)
        if outcome.first_form is not None:
            any_form_indices.append(index)
        if outcome.meeting is not None:
            meeting_indices.append(index)
        terminal[reason or "round 8"] += 1
        if reason and (reason in ("knots", "residual stall") or reason.startswith("guard")):
            limited[index] = reason
    return {
        "seed_kind": kind, "range": [first, end], "trials": end - first,
        "events": len(event_indices), "any_form": len(any_form_indices), "meetings": len(meeting_indices),
        "stopped": len(limited),
        "not_stopped": [sum(index not in limited for index in event_indices), end - first - len(limited)],
        "event_indices": event_indices, "any_form_indices": any_form_indices,
        "meeting_indices": meeting_indices, "limited": limited, "last_state_reasons": dict(terminal),
        "wall_seconds": round(perf_counter() - start, 6),
    }


def fisher(a: int, n_a: int, b: int, n_b: int, *, two_sided: bool = False) -> Fraction:
    """Exact conditional probability with row sizes and success total fixed."""
    success = a + b
    high = min(success, n_a)
    if not two_sided:
        total = sum(math.comb(n_a, i) * math.comb(n_b, success - i) for i in range(a, high + 1))
    else:
        low = max(0, success - n_b)
        mass = [math.comb(n_a, i) * math.comb(n_b, success - i) for i in range(low, high + 1)]
        total = sum(w for w in mass if w <= mass[a - low])
    return Fraction(total, math.comb(n_a + n_b, success))


def difference_interval(a: int, n_a: int, b: int, n_b: int) -> list[float]:
    p_a, p_b = (a + 1) / (n_a + 2), (b + 1) / (n_b + 2)
    error = Z95 * math.sqrt(p_a * (1 - p_a) / (n_a + 2) + p_b * (1 - p_b) / (n_b + 2))
    return [round(p_a - p_b - error, 4), round(p_a - p_b + error, 4)]


def statistics(arms: dict, level: Fraction, confirmation: bool) -> dict:
    a, n_a = arms["BN"]["events"], arms["BN"]["trials"]
    p = {name: fisher(a, n_a, arm["events"], arm["trials"]) for name, arm in arms.items() if name != "BN"}
    intervals = {MET_NAMES[name]: difference_interval(a, n_a, arm["events"], arm["trials"])
                 for name, arm in arms.items() if name != "BN"}
    stats = {f"p_vs_{MET_NAMES[kind]}": float(value) for kind, value in p.items()}
    if confirmation:
        confirmed = all(p[kind] <= level for kind in ("BY", "BX", "BT"))
        stats.update(
            level=float(level), confirmed=confirmed, ac=intervals,
            way=("through joining" if p["BM"] <= level else "through takes") if confirmed else None,
            **{"needs the meeting": confirmed and arms["BY"]["events"] == arms["BT"]["events"] == 0},
            p_masked_two_sided=float(fisher(a, n_a, arms["BM"]["events"], arms["BM"]["trials"], two_sided=True)),
        )
    else:
        stats.update(passes_at_100=all(test <= level for test in p.values()), one_history=a <= 2,
                     **{f"ac_{name}": bounds for name, bounds in intervals.items()})
    return stats


def compare(arms: dict, stats: dict, recorded_arms: dict, recorded_stats: dict) -> list[dict]:
    differences = []

    def check(field, observed, recorded):
        if type(observed) is float and type(recorded) is float:
            equal = math.isclose(observed, recorded, rel_tol=1e-10)
        else:
            equal = observed == recorded
        if not equal:
            differences.append({"field": field, "observed": observed, "recorded": recorded})

    check("q1_any", arms["BN"]["any_form"], recorded_arms["q1_any"])
    if "kinds" in recorded_arms:
        check("seed kinds", [data["seed_kind"] for data in arms.values()], recorded_arms["kinds"])
    for arm, data in arms.items():
        rate = RATE_FIELDS[arm]
        check(rate, data["events"], recorded_arms[rate])
        check("n" + rate[1:], data["trials"], recorded_arms["n" + rate[1:]])
        for field in ("meetings", "stopped", "not_stopped"):
            check(f"{field}.{arm}", data[field], recorded_arms[field][arm])
    for field, value in stats.items():
        if field in recorded_stats:
            check(field, value, recorded_stats[field])
    return differences


def replay(case: dict, artifact: str, starts: dict, prefix: int | None) -> dict:
    law = Law.from_record(case["law"])
    seed = seed_for(case, law)
    s, x, y = case["s"], tuple(case["X"]), tuple(case["Y"])
    if case["reading"] != "form" or seed != case["seed"]:
        raise ValueError("The recorded case is not the requested form reading and seed", seed)
    history, reason = grow(initial_state(starts[case["start"]]), law, seed)
    states_by_round = {state.round: state for state in history}
    state = states_by_round[s]
    reading = roster(state)
    if (x, y) not in eligible_pairs(state, reading, seed, case["run"] == "R6"):
        raise ValueError("Regrowth did not yield the registered eligible pair", seed, s, x, y, reading.parts)
    target = Form.of(reading, y)
    x_matches_y = target.matches(reading, x)
    outcome = read_form(history[history.index(state):], x, y, target, x_matches_y)
    if outcome.form_after_meeting is None:
        raise ValueError("Regrowth did not meet the form reading after meeting", seed, outcome)
    record = {
        "source": artifact, "run": case["run"], "start": case["start"], "law": case["law"],
        "seed": seed, "pair_round": s, "X": x, "Y": y, "Y_loose_counts": target.counts,
        "base_growth": {**vars(outcome), "terminal_round": history[-1].round, "reason": reason},
    }
    first_trials = 300 if case["run"] == "R6" else 100
    plans = (("first_stage", KINDS[:3], 0, first_trials, Fraction(1, 100), "rates100"),
             ("confirmation", KINDS, 100, 1100, Fraction(1, 500 if artifact == "R3.json" else 1200), "rates1000"))
    for stage, kinds, first, end, level, recorded_key in plans:
        planned = end - first
        actual = min(prefix, planned) if prefix is not None else planned
        arms = {kind: read_arm(
            state, law, seed, x, y, target, x_matches_y,
            kind + ("3" if first_trials == 300 and stage == "first_stage" else ""), first, first + actual,
        ) for kind in kinds}
        stats = statistics(arms, level, stage == "confirmation") if actual == planned else None
        differences = compare(arms, stats, case[recorded_key], case[stage]) if stats is not None else None
        record[stage] = {
            "arms": arms, "registered_trials_per_arm": planned,
            "projected_seconds": {kind: round(arm["wall_seconds"] * planned / actual, 3) for kind, arm in arms.items()},
            "statistics": stats, "differences_from_record": differences,
        }
    return record


def selected_cases(selection: str):
    candidates = []
    for source in ("R3.json", "Rcond.json"):
        for case in json.loads((RECORDS / source).read_text())["cases"]:
            if case["family"] != "claimed" or not case["confirmation"]["confirmed"]:
                continue
            main_pick = source == "R3.json" and (
                case["made_questions"]["meeting through made knots"]
                or case["start"] in ("n5-g44-02333", "n5-g31-13122")
            )
            conditional_pick = case["confirmation"]["needs the meeting"]
            selected = {
                "main": main_pick,
                "six": main_pick or conditional_pick,
                "remaining": not (main_pick or conditional_pick),
                "all": True,
            }
            if selected[selection]:
                candidates.append((case, source))
    return sorted(candidates, key=lambda row: row[0]["run"] != "R6")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int, help="Replay only this many registered indices of each arm")
    option = parser.add_mutually_exclusive_group()
    option.add_argument("--include-needs", dest="selection", action="store_const", const="six",
                        help="Also replay both conditional cases needing the meeting")
    option.add_argument("--remaining-cases", dest="selection", action="store_const", const="remaining",
                        help="Replay the eleven other cases")
    option.add_argument("--all-cases", dest="selection", action="store_const", const="all",
                        help="Replay all seventeen confirmed cases of the claimed reading")
    parser.set_defaults(selection="main")
    args = parser.parse_args()
    if args.prefix is not None and args.prefix < 1:
        parser.error("--prefix must be positive")
    start = perf_counter()
    starts = {row["id"]: row for row in json.loads(CENSUS.read_text())["starts"]}
    rows = []
    for case, artifact in selected_cases(args.selection):
        row = replay(case, artifact, starts, args.prefix)
        rows.append(row)
        if args.prefix is None:
            differences = sum(len(row[stage]["differences_from_record"]) for stage in ("first_stage", "confirmation"))
            print(f"{row['run']} {row['start']} {row['law']} Y={row['Y']}: {differences} differing fields",
                  file=sys.stderr, flush=True)
    main_scope = "Both main cases with a made linking knot, another parity start, and the not-all-equal case"
    scopes = {
        "main": main_scope,
        "six": main_scope + ". Both conditional cases needing the meeting are included",
        "remaining": "Eleven confirmed cases beyond the initial six, starting with the two cases screened at 300",
        "all": "All seventeen confirmed cases, starting with the two cases screened at 300",
    }
    result = {
        "scope": scopes[args.selection],
        "source_records": str(RECORDS.relative_to(ROOT)), "starts": str(CENSUS.relative_to(ROOT)),
        "prefix_per_arm": args.prefix, "cases": rows,
        "total_continuations": sum(arm["trials"] for row in rows for stage in ("first_stage", "confirmation")
                                   for arm in row[stage]["arms"].values()),
        "wall_seconds": round(perf_counter() - start, 3), "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
