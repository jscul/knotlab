"""Replay a deterministic stratified sample of the records as closed.

Run 'plan', 'pilot', 'full', 'controls-pilot', 'controls' in that order
from the repository root. Both pilots use the corresponding full settings.
The controls check a changed mark, a changed stub and a no-cancellation
counterexample.
"""

import argparse
import gzip
import hashlib
import json
import math
import random
import resource
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path

from regrow_engine import Growth, WorkLimit, joined, pattern


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.relative_to(ROOT)
CLOSURE = "9b6dad2e0c"
SEED = 20261126
ARCHIVES = {
    "bench": "bench/bench_runs.jsonl.gz",
    "bench take with marks": "bench/bench_take_marks.jsonl.gz",
    "bench owing": "bench/bench_owing.jsonl.gz",
    "census": "census/census_runs.jsonl.gz",
}
READER = {"A": "B", "B": "A"}


def select():
    rng = random.Random(SEED)
    samples = []
    frames = {}
    directed = []
    for source, path in ARCHIVES.items():
        blob = subprocess.check_output(["git", "show", f"{CLOSURE}:{STUDY / path}"], cwd=ROOT)
        rows = [json.loads(line) for line in gzip.decompress(blob).splitlines()]
        frame = defaultdict(list)
        for i, row in enumerate(rows):
            if "knots" not in row:
                continue
            candidate = (source, i + 1, row)
            if source == "census":
                stratum = (row["join"], *row["law"])
                if row["law"] == ["ORD", "CANCEL-WAIT"]:
                    if (row["i"], row["j"]) == (0, 1):
                        directed.append(candidate)
                    if any(m[0] == 6 for side in row["reads"].values() for m in side["marks"]):
                        directed.append(candidate)
            elif source == "bench take with marks":
                stratum = (row["join"], row["law"][0])
                if any(m["own making first differs"] == 6 for side in row["reads"].values()
                       for m in side["mark at a start knot of the other"].values()):
                    directed.append(candidate)
            else:
                stratum = (row["law"][0], row["law"][2])
                if (source == "bench" and row["A"] == "ring" and row["B"] == "source"
                        and row["steps"] == 1 and row["join"] == "meeting"
                        and row["law"] == ["ORD", "CANCEL-WAIT", None]):
                    directed.append(candidate)
            if row["knots"] <= 2500 and row["seconds"] <= 2:
                frame[stratum].append(candidate)
        frames[source] = {"closed_rows": len(rows), "completed": sum("knots" in r for r in rows),
                          "eligible": sum(map(len, frame.values())),
                          "weighting_within_stratum": "one uniform draw without replacement",
                          "strata": {repr(key): len(values) for key, values in frame.items()},
                          "compressed_sha256": hashlib.sha256(blob).hexdigest()}
        for stratum in sorted(frame, key=repr):
            samples.append(rng.choice(frame[stratum]))
    return samples, directed, frames


def key_of(case):
    source, line, r = case
    return {"archive": source, "line": line, "A": r["A"], "B": r["B"], "join": r["join"],
            "steps": r.get("steps", 1), "law": r["law"]}


def make_rows(state, limit, bound, retirement=None):
    rows = []
    retired = None
    for rnd in range(1, limit + 1):
        step = state.step()
        ancestry = state.ancestry
        signatures = {"A": [], "B": [], "both": []}
        for child in step["births"]:
            tags = ancestry[child]
            origin = next(iter(tags)) if len(tags) == 1 else ("both" if {"A", "B"} <= tags else None)
            if origin in signatures:
                signatures[origin].append((state.tokens[child], step["fresh"][child], len(state.places[child])))
        for births in signatures.values():
            births.sort()
        counts = {}
        for x, y in READER.items():
            own = frozenset([x])
            cross = [group for group in step["groups"] if any(ancestry[k] == own for k in group)
                     and any(ancestry[k] != own for k in group)]
            counts[x] = {"members": sum(ancestry[k] == own for k in step["members"]),
                         "joined": len(cross),
                         "kept": sum(step["short"].isdisjoint(group) for group in cross),
                         "joined to the other": sum(any(y in ancestry[k] for k in group) for group in cross)}
        rows.append({"knots": len(state.places), "short": len(step["short"]), "takes": step["takes"],
                     "made members": sum(bool(state.parents[k]) for k in step["members"]),
                     "made short": sum(bool(state.parents[k]) for k in step["short"]),
                     "cancelled": sum(not step["short"].isdisjoint(group) for group in step["groups"]),
                     "counts": counts, "signatures": signatures})
        if retirement is not None and rnd == retirement[0]:
            retired = state.retire(retirement[1])
        if len(state.places) > bound:
            break
    return rows, retired


def first(rows, other, tag, after=0, count_only=False):
    common = min(len(rows), len(other))
    for i in range(after, common):
        a = rows[i]["signatures"][tag]
        b = other[i]["signatures"][tag]
        left, right = (len(a), len(b)) if count_only else (a, b)
        if left != right:
            return i + 1
    return None


class Reading:
    def __init__(self, case):
        source, self.line, self.row = case
        self.census = source == "census"
        self.rounds = 10 if self.census else 12
        self.bound = 1500 if self.census else 3000
        self.ration, self.treatment, *take = self.row["law"]
        self.take = take[0] if take else None
        self.marks_asked = source != "bench" or self.take is None
        self.names = {}
        self.full = (self.row["A"], self.row["B"])
        self.totals = Counter()
        self.grow_calls = 0
        self.grow_rounds = 0
        self.horizons = defaultdict(Counter)
        self.count_only_examples = {}

    def grow(self, pair, mark=None, stub_extra=0, bar=None, retire=None, limit=None):
        s, roles = joined(*pair, self.row.get("steps", 1), self.row["join"], mark, stub_extra)
        state = Growth(s, roles, self.ration, self.treatment, self.take, name_table=self.names)
        if bar is not None:
            tag, knot = bar
            i = [j for j, role in enumerate(roles) if role == tag][knot]
            if i not in state.active:
                return None, None
            state.active[i] = state.active[i][1:]
            if not state.active[i]:
                del state.active[i]
        rows, retired = make_rows(state, self.rounds if limit is None else limit, self.bound, retire)
        self.grow_calls += 1
        self.grow_rounds += len(rows)
        return rows, retired

    def difference(self, base, other, tag, kind, after=0):
        exact = first(base, other, tag, after)
        counts = first(base, other, tag, after, count_only=True)
        self.horizons[kind][min(len(base), len(other))] += 1
        if counts != exact and kind not in self.count_only_examples:
            self.count_only_examples[kind] = {"receiver": tag, "exact_first": exact,
                                              "count_only_first": counts}
        self.totals[kind + " comparisons"] += 1
        self.totals[kind + " exact positive"] += exact is not None
        self.totals[kind + " exact differs before (or without) a birth-count difference"] += counts != exact
        return exact

    def regenerate(self):
        r = self.row
        base, _ = self.grow(self.full)
        n = len(base)
        stop = "knots" if base[-1]["knots"] > self.bound else "rounds"
        short = [s["short"] for s in base]
        joint = [len(s["signatures"]["both"]) for s in base]
        self.totals["rounds checked in the unmarked, joined growth"] = n
        self.totals["short members born after the start in unmarked ordinary rounds"] = (
            sum(s["made short"] for s in base) if self.ration == "ORD" else 0)
        self.totals["made member appearances in unmarked ordinary rounds"] = (
            sum(s["made members"] for s in base) if self.ration == "ORD" else 0)
        rebuilt = {"A": r["A"], "B": r["B"], "join": r["join"], "law": r["law"],
                   "knots": base[-1]["knots"], "reads": {}}
        if self.census:
            rebuilt.update({"rounds": n, "ended": stop, "short": short, "joint": joint})
        else:
            rebuilt.update({"rounds read": n, "ended by": stop, "steps": r["steps"],
                            "births that took": sum(s["takes"] for s in base),
                            "short members by round": short, "joint descent, births by round": joint})
        for x, y in READER.items():
            stub_pair = (r["A"], "stub") if x == "A" else ("stub", r["B"])
            stub, _ = self.grow(stub_pair, limit=n)
            d = self.difference(base, stub, x, "stub")
            births = [len(s["signatures"][x]) for s in base]
            kept = [s["counts"][x]["kept"] for s in base]
            joined_counts = [s["counts"][x]["joined"] for s in base]
            if self.census:
                reading = {"last kept": max((i for i, c in enumerate(kept, 1) if c), default=0),
                           "last joined": max((i for i, c in enumerate(joined_counts, 1) if c), default=0),
                           "stub": d, "own births": births, "marks": []}
            else:
                bare, _ = self.grow((r[x], None), limit=n)
                bare_common = min(n, len(bare))
                bare_prefix = next((i for i in range(bare_common)
                                    if births[i] != len(bare[i]["signatures"]["A"])
                                    or base[i]["counts"][x]["members"] != bare[i]["counts"]["A"]["members"]),
                                   bare_common)
                reading = {"pattern": r[x], "own members by round": [s["counts"][x]["members"] for s in base],
                           "own births by round": births, "joined by round": joined_counts, "kept by round": kept,
                           "joined to the other by round": [s["counts"][x]["joined to the other"] for s in base],
                           "own series is the bare pattern's through": bare_prefix,
                           "own making differs from with a stub, first round": d,
                           "rounds compared with the stub": min(n, len(stub)), "other retired after round": {}}
                for c in (2, 4, 6, 8):
                    if c > n:
                        break
                    changed, retired = self.grow(self.full, retire=(c, y), limit=n)
                    reading["other retired after round"][str(c)] = {
                        "members retired": retired, "own making first differs":
                        self.difference(base, changed, x, "retiring", after=c),
                        "rounds compared": min(n, len(changed))}
            if self.marks_asked:
                if not self.census:
                    reading["mark at a start knot of the other"] = {}
                for i in range(len(pattern(r[y])[0])):
                    other, _ = self.grow(self.full, mark=(y, i, 1), limit=n)
                    own = self.difference(base, other, x, "own mark")
                    both = self.difference(base, other, "both", "joint mark")
                    if self.census:
                        reading["marks"].append([own, both])
                    else:
                        reading["mark at a start knot of the other"][str(i)] = {
                            "own making first differs": own, "joint descent first differs": both,
                            "rounds compared": min(n, len(other))}
            rebuilt["reads"][x] = reading
        return rebuilt


def compare(got, saved):
    """Compare every saved scientific value; census i,j are archive labels."""
    exclude = {"seconds", "i", "j"}
    expected = {k: v for k, v in saved.items() if k not in exclude}
    misses = []
    checks = Counter()

    def descend(x, y, path):
        if isinstance(x, dict) and isinstance(y, dict) and x.keys() == y.keys():
            for key in x:
                descend(x[key], y[key], path + (key,))
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            for i, (got_item, saved_item) in enumerate(zip(x, y)):
                descend(got_item, saved_item, path + (i,))
        else:
            checks["saved_leaf_values_compared"] += 1
            is_input = path[0] in ("A", "B", "join", "law", "steps") or path[-1] == "pattern"
            checks["input_labels" if is_input else "saved_growth_values_compared"] += 1
            if x != y:
                misses.append({"path": path, "rebuilt": x, "saved": y})
    descend(got, expected, ())
    return checks, misses


def one(case, selection):
    t0 = time.monotonic()
    reading = Reading(case)
    result = {**key_of(case), "selection": selection}
    try:
        got = reading.regenerate()
        checks, misses = compare(got, case[2])
        checks.update(reading.totals)
        result.update({"comparisons": dict(checks), "mismatches": misses,
                       "common_rounds_by_comparison": dict(reading.horizons),
                       "examples_where_counts_alone_change_first_difference": reading.count_only_examples})
    except WorkLimit as error:
        result["referee limit"] = str(error)
    result.update({"seconds": round(time.monotonic()-t0, 4), "growths": reading.grow_calls,
                   "all_growth_rounds": reading.grow_rounds})
    return result


def controls(cases, pilot):
    """Compare marks and stubs on fixed inputs admitted by the tests."""
    targets = [c for c in cases if c[0] == "census" and (c[2]["i"], c[2]["j"]) in ((0, 1), (27, 28))]
    # The three-knot start with each knot at its least loose count gives a
    # positive control for a supplied meeting: the site's two joins exhaust
    # its two loose distinctions, so barring one can cancel the external join.
    path = ARCHIVES["census"]
    blob = subprocess.check_output(["git", "show", f"{CLOSURE}:{STUDY / path}"], cwd=ROOT)
    for i, line in enumerate(gzip.decompress(blob).splitlines(), 1):
        r = json.loads(line)
        if (r.get("A") == "g1:3@0" and r.get("B") == "g7:111@0" and
                r.get("join") == "meeting" and r.get("law") == ["ORD", "CANCEL-WAIT"]):
            targets.append(("census", i, r))
            break
    assert len(targets) == 4
    output = []
    if pilot:
        # The marked late-hearing case was the dearest by archived time.
        targets = [max(targets, key=lambda c: c[2]["seconds"])]
    for case in targets:
        t0 = time.monotonic()
        r = Reading(case)
        base, _ = r.grow(r.full)
        item = {**key_of(case), "rounds": len(base), "sides": {}}
        for x, y in READER.items():
            pair = (r.full[0], "stub") if x == "A" else ("stub", r.full[1])
            small, _ = r.grow(pair)
            larger, _ = r.grow(pair, stub_extra=1)
            side = {"own_births_round_1": [len(t[0]["signatures"][x]) for t in (base, small, larger)],
                    "short_by_round_whole_and_standard_stub": [[q["short"] for q in t] for t in (base, small)],
                    "cancelled_by_round_whole_and_standard_stub": [[q["cancelled"] for q in t] for t in (base, small)],
                    "first_own_difference_with_standard_or_larger_stub": [first(base, t, x) for t in (small, larger)],
                    "common_rounds_with_standard_or_larger_stub": [min(len(base), len(t)) for t in (small, larger)],
                    "marks": []}
            for i in range(len(pattern(r.row[y])[0])):
                added, _ = r.grow(r.full, mark=(y, i, 1))
                barred, _ = r.grow(r.full, bar=(y, i))
                for label, t in (("one extra loose distinction", added), ("bar one existing loose distinction", barred)):
                    value = {"site": i, "mark": label}
                    if t is None:
                        value["not run"] = "there is no usable loose distinction at the named knot"
                    else:
                        value.update({"own": first(base, t, x), "joint": first(base, t, "both"),
                                      "common_rounds": min(len(base), len(t))})
                    side["marks"].append(value)
            item["sides"][x] = side
        item["seconds"] = round(time.monotonic()-t0, 4)
        output.append(item)
    return output


def save(kind, data):
    path = HERE / ("regrow_" + kind + ".json")
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("plan", "pilot", "full", "controls-pilot", "controls"))
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    samples, directed, frames = select()
    jobs = [(v, "planned uniform draw in stratum") for v in samples]
    have = {(c[0], c[1]) for c in samples}
    jobs.extend((v, "directed check") for v in directed if (v[0], v[1]) not in have)
    # First in the selected order for each archive, except the main bench:
    # there the more expensive named ordinary meeting is the pilot's case.
    pilot = [next((c, sel) for c, sel in jobs if c[0] == name and
                  (name != "bench" or c[2]["A"] == "ring" and c[2]["B"] == "source" and
                   c[2]["join"] == "meeting" and c[2]["law"] == ["ORD", "CANCEL-WAIT", None]))
             for name in ARCHIVES]
    target_keys = [key_of(v) for v, _ in jobs]
    if args.stage == "plan":
        save("plan", {"seed": SEED, "closure": CLOSURE, "frames": frames,
                      "sample_frame_cut": "completed rows with saved unmarked knots <= 2500 and saved seconds <= 2",
                      "directed_additions": "singleton/copier both joins, four census sixth-round cases, the bench sixth-round case, and ring/source one-step ordinary meeting",
                      "jobs": target_keys, "pilot": [key_of(v) for v, _ in pilot],
                      "case_limits": "full documented round and knot bounds, one process, 3 GiB address space; independent per-roster work ceilings in regrow_engine.py"})
        print("selected", len(samples), "stratified jobs and", len(jobs)-len(samples), "added directed jobs")
        return
    if args.stage.startswith("controls"):
        pilot_control = args.stage == "controls-pilot"
        if not pilot_control:
            prior = json.loads((HERE / "regrow_controls-pilot.json").read_text())
            assert prior["expected_full_seconds_at_pilot_rate"] < 3600
        data = controls(directed, pilot_control)
        result = {"controls": data, "stub": "one extra loose distinction on the replacement knot",
                  "mark": "bar the least numbered usable loose distinction at the marked start knot",
                  "base": "each control grows independently to its recorded bounds"}
        if pilot_control:
            result["expected_full_seconds_at_pilot_rate"] = 4 * data[0]["seconds"]
        save(args.stage, result)
        print("controls", len(data))
        return
    piloted = args.stage == "pilot"
    if not piloted:
        plan = json.loads((HERE / "regrow_plan.json").read_text())
        assert plan["jobs"] == target_keys
        prior = json.loads((HERE / "regrow_pilot.json").read_text())
        assert prior["expected_full_seconds_at_pilot_rates"] < 3600
    out = []
    for case, selection in (pilot if piloted else jobs):
        out.append(one(case, selection))
    totals = Counter()
    for row in out:
        totals.update(row.get("comparisons", {}))
    result = {"seed": SEED, "closure": CLOSURE, "results": out, "totals": dict(totals),
              "cases": len(out), "growths": sum(z["growths"] for z in out),
              "all_growth_rounds": sum(z["all_growth_rounds"] for z in out),
              "wall_seconds_for_growths": round(sum(z["seconds"] for z in out), 3),
              "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "cases_with_mismatches": sum(bool(z.get("mismatches")) for z in out),
              "referee_limits_reached": sum("referee limit" in z for z in out)}
    if piloted:
        rates = {z["archive"]: z["seconds"] for z in out}
        result["projected_seconds_by_archive"] = {
            name: round(rates[name] * sum(c[0] == name for c, sel in jobs), 2) for name in rates}
        result["expected_full_seconds_at_pilot_rates"] = math.ceil(sum(result["projected_seconds_by_archive"].values()))
    save(args.stage, result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("results", "totals")}, indent=2))


if __name__ == "__main__":
    main()
