"""Compare the independently grown rounds with four archived studies.

Run from the repository root with .venv/bin/python -B. The replay uses the
archive's receiver and sender identities and its round and knot bounds. Its
birth reading includes parent-based names, fresh counts and total places.
The census archive retains the per-round counts and the results of comparing
the full readings. Both are checked. The archive supplies no growth input
beyond the starts, laws, bounds and mark positions.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import gzip
import json
from pathlib import Path
import random
import resource
import sys
from time import perf_counter

from growth import grow


HERE = Path(__file__).resolve().parent
SEED = 20261126
MEMORY_BYTES = 2_500_000_000
SECTIONS = ("census", "rule", "controls", "senders")
ARCHIVES = {
    "census": "receivers_runs.jsonl.gz",
    "rule": "rule_runs.jsonl.gz",
    "controls": "controls_runs.jsonl.gz",
    "senders": "senders_runs.jsonl.gz",
}
TWO_LOOSE = "g3:22@0"
SWITCH_RECEIVER = "g7:122@0"


def read_archive(section):
    with gzip.open(HERE.parent / ARCHIVES[section], "rt", encoding="utf-8") as source:
        return [json.loads(line) for line in source]


def first_difference(left, right):
    return next((i for i, (a, b) in enumerate(zip(left, right), 1) if a != b), None)


def leaves_first_way(births):
    return next((i for i, births_in_round in enumerate(births, 1) if births_in_round != i + 2), None)


def own_signature(rows):
    return [row.own_signature for row in rows]


@dataclass
class Replay:
    archive_rows: int = 0
    growth_runs: int = 0
    checks: Counter = field(default_factory=Counter)
    differences: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    differences_hidden_by_counts: list = field(default_factory=list)
    rounds_read: Counter = field(default_factory=Counter)
    unmarked: dict = field(default_factory=dict)

    def grow(self, *args, **kwargs):
        rows = grow(*args, **kwargs)
        self.growth_runs += 1
        self.rounds_read[len(rows)] += 1
        return rows

    def check(self, case, name, observed, recorded, *, per_round=False):
        self.checks[name] += min(len(observed), len(recorded)) if per_round else 1
        if observed != recorded:
            difference = {"case": case, "field": name}
            if per_round:
                index = first_difference(observed, recorded)
                if index is None:
                    difference.update({"rounds rebuilt": len(observed), "rounds archived": len(recorded)})
                else:
                    difference.update({"round": index, "rebuilt": observed[index - 1],
                                       "archived": recorded[index - 1]})
            else:
                difference.update({"rebuilt": observed, "archived": recorded})
            self.differences.append(difference)

    def check_trace(self, case, rows, archived):
        self.check(case, "rounds", len(rows), archived["rounds"])
        if "knots" in archived:
            self.check(case, "final knots", rows[-1].knots, archived["knots"])
        self.check(case, "own birth counts", [r.own_births for r in rows],
                   archived["own births"], per_round=True)
        self.check(case, "own short counts", [r.own_short for r in rows],
                   archived["A short"], per_round=True)

    def check_sender_classes(self, case, headline):
        a, d, law = case["A"], case["d"], case["law"]
        observed = {b: self.grow(a, b, d, law) for b in case["by sender"]}
        signatures = {b: own_signature(rows) for b, rows in observed.items()}
        shared_rounds = min(map(len, observed.values()))
        key = [a, d, law]
        self.check(key, "common rounds", shared_rounds, case["rounds compared"])
        by_reading = defaultdict(list)
        for b, archived in case["by sender"].items():
            self.check_trace([*key, b], observed[b], archived)
            by_reading[tuple(signatures[b][:shared_rounds])].append(b)
            self.check([*key, b], "first differs from stub",
                       first_difference(signatures[b], signatures["stub"]), archived["differs from the stub"])
            self.check([*key, b], "common rounds with stub",
                       min(len(observed[b]), len(observed["stub"])), archived["rounds with the stub"])
        classes = sorted(sorted(members) for members in by_reading.values())
        first = next((i for i, readings in enumerate(zip(*signatures.values()), 1)
                      if len(set(readings)) > 1), None)
        short_before = (any(row.own_short for rows in observed.values() for row in rows[:first - 1])
                        if first is not None else None)
        self.check(key, "sender classes", classes, sorted(sorted(group) for group in case["classes"]))
        self.check(key, "first difference among senders", first, case["first differs"])
        self.check(key, "own short before first difference", short_before, case["own short before"])
        first_count = next((i for i, readings in enumerate(zip(*observed.values()), 1)
                            if len({row.own_births for row in readings}) > 1), None)
        if first_count != first:
            self.differences_hidden_by_counts.append({"case": key, "birth reading": first, "counts": first_count})
        if headline or case.get("reading") == "classes":
            self.findings.append({"A": a, "d": d, "law": law, "rounds compared": shared_rounds,
                                  "first differs": first, "classes": classes, "own short before": short_before,
                                  "first by sender versus stub": {
                                      b: first_difference(reading, signatures["stub"])
                                      for b, reading in signatures.items()
                                  }})

    def check_mark(self, case, law):
        a, b, d, t = case["A"], case.get("B", TWO_LOOSE), 3, case["t0"]
        key = (a, b, law)
        if key not in self.unmarked:
            self.unmarked[key] = own_signature(self.grow(a, b, d, law))
        unchanged = self.unmarked[key]
        marked = own_signature(self.grow(a, b, d, law, mark_after=t))
        heard = first_difference(unchanged, marked)
        common = min(len(unchanged), len(marked))
        self.check([*key, t], "mark first heard", heard, case["heard"])
        self.check([*key, t], "mark common rounds", common, case["rounds"])

    def check_case(self, section, case, headline):
        self.archive_rows += 1
        reading = case.get("reading")
        if section == "census" or reading == "classes":
            self.check_sender_classes(case, section == "census" and case["A"] in headline and case["law"] == "CAP-3")
        elif reading == "swap":
            self.check_mark(case, f"CAP-{case['cap']}" if section == "rule" else "CAP-3")
        elif reading == "long":
            a, b = case["A"], case["B"]
            self.check_trace([a, b, "long"], self.grow(a, b, 3, "CAP-3", rounds=22, bound=6000), case)
        elif reading == "both":
            a = case["A"]
            rows = self.grow(a, a, 3, "CAP-3")
            for end, births in (("A", [r.own_births for r in rows]), ("B", [r.sender_births for r in rows])):
                self.check([a, "both", end], "both ends birth counts", births, case[f"own births {end}"], per_round=True)
                self.check([a, "both", end], "both ends leaves first way", leaves_first_way(births),
                           case[f"{end} leaves first way"])
        else:
            b, d, law = case["B"], case["d"], case["law"]
            rows = self.grow(SWITCH_RECEIVER, b, d, law)
            key = [SWITCH_RECEIVER, b, d, law]
            self.check_trace(key, rows, case)
            self.check(key, "leaves first way", leaves_first_way([r.own_births for r in rows]), case["leaves first way"])

    def summary(self, wall_seconds):
        return {"archive rows checked": self.archive_rows, "growth runs": self.growth_runs,
                "comparisons": dict(self.checks), "disagreements": self.differences,
                "findings": self.findings, "differences hidden by reading only birth counts": self.differences_hidden_by_counts,
                "run counts by completed rounds": dict(sorted(self.rounds_read.items())),
                "wall seconds": round(wall_seconds, 3)}


def sample_census(rows, headline):
    starts = sorted({r["A"] for r in rows})
    generator = random.Random(SEED)
    size_groups = {}
    for n in range(1, 5):
        eligible = [a for a in starts if a.startswith(f"n{n}:")]
        size_groups[n] = sorted(generator.sample(eligible, min(len(eligible), 5)))
    bench = [a for a in starts if not a.startswith("n")]
    selected = set(bench).union(*size_groups.values())
    sample = [r for r in rows if r["A"] in selected or (r["A"] in headline and r["law"] == "CAP-3")]
    detail = {"seed": SEED, "selection": "uniform without replacement among distinct archived sited starts by size",
              "starts by knot count": size_groups, "bench starts, all laws": bench,
              "reported cap-three switch receivers, cap three": sorted(headline),
              "unreplayed archive rows": len(rows) - len(sample)}
    return sample, detail


def pilot_cases(section, cases):
    if section == "census":
        law_sample = [next(r for r in cases if r["law"] == law and r["A"].startswith("n4:") and r["d"] == 5)
                      for law in sorted({r["law"] for r in cases})]
        known = next(r for r in cases if (r["A"], r["d"], r["law"]) == (f"n3:{SWITCH_RECEIVER}", 3, "CAP-3"))
        return [*law_sample, known]
    if section == "rule":
        high = [next(r for r in cases if r["reading"] == "classes" and r["cap"] == cap and r["d"] == 3)
                for cap in (6, 7, 8)]
        return [*high, next(r for r in cases if r["reading"] == "swap" and r["cap"] == 7 and r["t0"] == 3)]
    if section == "controls":
        return [next(r for r in cases if r["reading"] == "swap" and r["B"] == TWO_LOOSE and r["t0"] == 3),
                next(r for r in cases if r["reading"] == "long" and r["B"] == TWO_LOOSE),
                next(r for r in cases if r["reading"] == "both")]
    return [next(r for r in cases if r["law"] == law and r["d"] == d and r["B"] == TWO_LOOSE)
            for law in ("CAP-4", "CAP-5") for d in (2, 3)]


def run_section(section, cases, headline):
    run = Replay()
    longest = 0.0
    began = perf_counter()
    for case in cases:
        started = perf_counter()
        run.check_case(section, case, headline)
        longest = max(longest, perf_counter() - started)
    return run.summary(perf_counter() - began), longest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--write", action="store_true", help="save the completed replays to replay.json")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    started = perf_counter()
    archives = {section: read_archive(section) for section in SECTIONS}
    headline = {r["A"] for r in archives["controls"] if r["reading"] == "long"}
    archives["census"], selection = sample_census(archives["census"], headline)
    load_seconds = perf_counter() - started
    output = {"address-space limit bytes": MEMORY_BYTES, "worker processes": 1, "census selection": selection,
              "archive load seconds": round(load_seconds, 3), "pilot": {}, "replay": {}}

    for section in SECTIONS:
        pilot, longest = run_section(section, pilot_cases(section, archives[section]), headline)
        pilot["slowest seconds per archive row"] = round(longest, 3)
        pilot["projection at slowest observed pace, seconds"] = round(longest * len(archives[section]), 1)
        output["pilot"][section] = pilot
        print(f"{section} pilot: {pilot['archive rows checked']} rows, {pilot['wall seconds']} s; "
              f"full projection {pilot['projection at slowest observed pace, seconds']} s", file=sys.stderr, flush=True)
    if not args.pilot_only:
        for section in SECTIONS:
            result, _ = run_section(section, archives[section], headline)
            output["replay"][section] = result
            print(f"{section}: {result['growth runs']} growth runs, {len(result['disagreements'])} differences, "
                  f"{result['wall seconds']} s", file=sys.stderr, flush=True)

    output["peak resident kibibytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    output["total wall seconds"] = round(perf_counter() - started, 3)
    report = json.dumps(output, indent=2) + "\n"
    if args.write and not args.pilot_only:
        (HERE / "replay.json").write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return int(any(section["disagreements"] for section in output["replay"].values()))


if __name__ == "__main__":
    sys.exit(main())
