"""Replay selected ticket B runs from the frozen round rules."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json

from b_recount import STARTS, job_records, pairs_in_round, signature


def memberships(places, holders):
    met = [set() for knot in places]
    for owners in holders.values():
        if len(owners) > 1:
            for u in owners:
                met[u].update(owners - {u})
    return met


def roster(places, holders, barred):
    loose = {u: [] for u in range(len(places))}
    barred_count = Counter()
    for distinction, owners in holders.items():
        if len(owners) != 1:
            continue
        u = next(iter(owners))
        if distinction in barred:
            barred_count[u] += 1
        else:
            loose[u].append(distinction)
    return {u: sorted(ds) for u, ds in loose.items() if ds}, barred_count


def met_sets(members, met):
    m = set(members)
    sets = {frozenset(ms & m) for ms in met}
    return {s for s in sets if len(s) >= 2}


def joinability(members, sets):
    neighbours = {u: set() for u in members}
    for group in sets:
        for u in group:
            neighbours[u].update(group - {u})
    return neighbours


def maximal_groups(sets, neighbours):
    larger = []

    def search(group, available, used):
        if not available and not used:
            if len(group) >= 3 and not any(group <= met for met in sets):
                larger.append(tuple(sorted(group)))
            return
        pivot = max(available | used, key=lambda u: len(available & neighbours[u]))
        for u in sorted(available - neighbours[pivot]):
            search(group | {u}, available & neighbours[u], used & neighbours[u])
            available.remove(u)
            used.add(u)

    for part in parts(neighbours):
        if len(part) < 3 or frozenset(part) in sets:
            continue
        search(set(), part.copy(), set())
    covered = {pair for group in larger for pair in combinations(group, 2)}
    pairs = {(u, v) for u, ns in neighbours.items() for v in ns if u < v}
    return sorted(larger) + sorted(pairs - covered)


def parts(neighbours):
    unseen = set(neighbours)
    while unseen:
        frontier = [min(unseen)]
        seen = {frontier[0]}
        while frontier:
            u = frontier.pop()
            new = neighbours[u] - seen
            seen.update(new)
            frontier.extend(new)
        unseen -= seen
        yield seen


def add_place(holders, knot, distinction):
    holders.setdefault(distinction, set()).add(knot)


class Growth:
    def __init__(self, start, parity):
        labels = sorted({d for knot in start["stars"] for d in knot})
        numbering = {d: i for i, d in enumerate(labels)}
        self.places = [{numbering[d] for d in knot} for knot in start["stars"]]
        self.barred = {numbering[d] for d in start.get("barred", [])}
        self.marks = [0] * len(self.places)
        for u in start.get("X", []):
            self.marks[u] |= 1
        for u in start.get("Y", []):
            self.marks[u] |= 2
        self.parents = [()] * len(self.places)
        self.parity = parity
        self.holders = {}
        self.basis = {}
        for u, knot in enumerate(self.places):
            for distinction in knot:
                add_place(self.holders, u, distinction)
            if parity:
                self.add_equation(knot)
        self.next_distinction = len(labels)

    def reduce_equation(self, knot):
        row = sum(1 << d for d in knot)
        while row and (high := row.bit_length() - 1) in self.basis:
            row ^= self.basis[high]
        return row

    def add_equation(self, knot):
        if row := self.reduce_equation(knot):
            self.basis[row.bit_length() - 1] = row

    def bar_pattern(self, members):
        loose, _ = roster(self.places, self.holders, self.barred)
        for u in members:
            self.barred.update(loose.get(u, []))

    def make_round(self, ration, treatment, release, taking):
        loose, _ = roster(self.places, self.holders, self.barred)
        if not loose:
            return
        met = memberships(self.places, self.holders)
        sets = met_sets(loose, met)
        groups = maximal_groups(sets, joinability(loose, sets))
        owed = Counter(u for group in groups for u in group)
        short = {u for u in loose if owed[u] > len(loose[u])}
        kept_groups = [group for group in groups if not short.intersection(group)]
        paid = Counter(u for group in kept_groups for u in group)
        next_pay = Counter()
        births = []
        for group in kept_groups:
            inputs = {loose[u][next_pay[u]] for u in group}
            next_pay.update(group)
            births.append((group, inputs, None))
        for u, distinctions in loose.items():
            if u in short and treatment != "OFFSHOOT":
                if treatment == "RETIRE":
                    self.barred.update(distinctions)
                continue
            used = paid[u] if release or u in short else owed[u]
            births.extend(((u,), {d}, i) for i, d in enumerate(distinctions[used:]))
        if taking:
            self.take_shared(births, met, taking)
        implied = [self.parity and self.reduce_equation(inputs) == 0 for _, inputs, _ in births]
        demand = Counter()
        if ration == "CAP-3":
            provisional = list(self.places)
            new_holders = {d: set(us) for d, us in self.holders.items()}
            for _, inputs, _ in births:
                u = len(provisional)
                provisional.append(inputs)
                for d in inputs:
                    add_place(new_holders, u, d)
            members, _ = roster(provisional, new_holders, self.barred)
            members.update((u, []) for u in range(len(self.places), len(provisional)))
            demands_sets = met_sets(members, memberships(provisional, new_holders))
            later = maximal_groups(demands_sets, joinability(members, demands_sets))
            demand.update(u for group in later for u in group)
        for (parents, inputs, _), closed in zip(births, implied):
            u = len(self.places)
            used = len(parents) if ration == "FBP" else len(inputs)
            fresh = max(3 - used, 1)
            if ration == "CAP-3":
                fresh = min(max(demand[u], fresh), 3)
            if closed:
                fresh = 0
            distinctions = set(range(self.next_distinction, self.next_distinction + fresh))
            self.next_distinction += fresh
            knot = inputs | distinctions
            self.places.append(knot)
            self.parents.append(parents)
            mark = 0
            for parent in parents:
                mark |= self.marks[parent]
            self.marks.append(mark)
            for d in knot:
                add_place(self.holders, u, d)
            if self.parity:
                self.add_equation(knot)

    def take_shared(self, births, met, choice):
        shared = {d for d, owners in self.holders.items() if len(owners) > 1}
        for parents, inputs, order in births:
            met_by_all = set.intersection(*(met[p] for p in parents))
            usable = {d for u in met_by_all for d in self.places[u] if d in shared}
            from_parents = {d for u in parents for d in self.places[u]}
            candidates = sorted(usable - from_parents)
            if not candidates:
                continue
            chosen = 0
            if choice == "NEWEST":
                chosen = -1
            elif choice == "BY-COUNT":
                chosen = len(self.places[parents[0]]) % len(candidates)
            elif choice == "IN-TURN" and order is not None:
                chosen = order % len(candidates)
            inputs.add(candidates[chosen])

    def current_parts(self):
        members, barred_count = roster(self.places, self.holders, self.barred)
        sets = met_sets(members, memberships(self.places, self.holders))
        return members, barred_count, sets, parts(joinability(members, sets))

    def parts_forms(self, max_members=6, marked=False):
        members, barred_count, sets, pieces = self.current_parts()
        sets_by_member = defaultdict(set)
        for group in sets:
            sets_by_member[min(group)].add(group)
        for piece in pieces:
            if len(piece) > max_members:
                continue
            order = sorted(piece)
            index = {u: i for i, u in enumerate(order)}
            subgroups = {group for u in order for group in sets_by_member[u]}
            form = signature({
                "hk": [[len(members[u]), barred_count[u]] for u in order],
                "marks": [self.marks[u] for u in order] if marked else None,
                "maxsets": [[index[u] for u in group] for group in subgroups
                            if not any(group < other for other in subgroups)],
            })
            yield form, order

    def observe(self, target):
        result = Counter()
        for form, piece in self.parts_forms():
            if form != target:
                continue
            descents = {self.marks[u] for u in piece}
            result["Y form any"] += 1
            result["Y form from both"] += int(descents == {3})
            result["Y form mixed"] += int(len(descents) > 1)
            result["Y form with every knot made"] += int(all(self.parents[u] for u in piece))
        members, _ = roster(self.places, self.holders, self.barred)
        result["X only ended"] = not any(self.marks[u] == 1 for u in members)
        result["Y only ended"] = not any(self.marks[u] == 2 for u in members)
        return result


def law_parts(job):
    law = job["law"].split("/")
    ration = law[0] if "fresh-by-parents" not in law else "FBP"
    treatment = law[1].removeprefix("CANCEL-")
    choice = law[3][4:-1] if law[3].startswith("MET(") else None
    return (ration, treatment, law[2] == "RELEASE", choice)


def replay(start, job, rounds, target, bar=()):
    growth = Growth(start, job["law"].endswith("/parity"))
    growth.bar_pattern(bar)
    observations = []
    for t in range(1, rounds + 1):
        growth.make_round(*law_parts(job))
        observations.append(growth.observe(target))
    return observations, growth


CHECKED_FIELDS = (
    "X only ended", "Y only ended", "Y form any", "Y form from both", "Y form mixed",
)


def compare_start(inputs, job, key):
    run = job["starts"][key]
    start = inputs["starts"][key]
    y_kind = run["Y kind"]
    y_start = inputs["alone"][y_kind]["Y alone"]
    target, = (form for form, _ in Growth(y_start, False).parts_forms())
    assert target == signature(job["forms"][job["kind_forms"][y_kind]])
    results, _ = replay(start, job, len(run["per_round"]), target)
    for t, (observed, recorded) in enumerate(zip(results, run["per_round"]), 1):
        for field in CHECKED_FIELDS:
            assert observed[field] == recorded[field], (job["law"], key, t, field, observed, recorded)
    return results, target


def compare_controls(inputs, job, key, target):
    run = job["starts"][key]
    y_start = inputs["alone"][run["Y kind"]]["Y alone"]
    x_start = inputs["alone"][run["X kind"]]["X alone"]
    start = inputs["starts"][key]
    expected = {
        "Y alone": [c.get(str(job["kind_forms"][run["Y kind"]]), 0)
                    for c in job["alone"]["Y alone|" + run["Y kind"]]["counts"]],
        "X alone": [c.get(str(job["kind_forms"][run["Y kind"]]), 0)
                    for c in job["alone"]["X alone|" + run["X kind"]]["counts"]],
        "X barred": run["B_X"]["Y form"],
        "Y barred": run["B_i"]["Y form"],
    }
    for control, configuration, barred in (
        ("Y alone", y_start, ()), ("X alone", x_start, ()),
        ("X barred", start, start["X"]), ("Y barred", start, start["Y"]),
    ):
        rows, _ = replay(configuration, job, len(expected[control]), target, barred)
        observed = [row["Y form any"] for row in rows]
        assert observed == expected[control], (job["law"], key, control, observed)
    return expected


def initial_rosters(inputs):
    stored_path = STARTS.with_name("rosters_b.json")
    stored = json.loads(stored_path.read_text())
    comparisons = {False: defaultdict(set), True: defaultdict(set)}
    for key, start in inputs["starts"].items():
        if key.endswith("-other"):
            continue
        growth = Growth(start, False)
        for marked in (False, True):
            form = tuple(sorted(f for f, _ in growth.parts_forms(max_members=8, marked=marked)))
            comparisons[marked][form].add(key)
    report = {}
    for marked, field in ((False, "roster"), (True, "marked roster")):
        from_records = defaultdict(set)
        for key, value in stored["starts"].items():
            from_records[value[field]].add(key)
        exact = {frozenset(s) for s in comparisons[marked].values()}
        report[field] = {
            "classes": len(exact),
            "same partition as the record": exact == {frozenset(s) for s in from_records.values()},
        }
    return report


def three_sibling_replays(inputs, limit=None):
    kind = "three-222"
    target, = (form for form, _ in Growth(inputs["alone"][kind]["Y alone"], False).parts_forms())
    tally = Counter({"parts with a join among the members": 0, "parts with a made immediate parent": 0})
    witness = None
    for file in ("b1", "b2_hold"):
        for job in job_records(file, {}):
            if not job["law"].startswith("FLOOR1/"):
                continue
            target_code = str(job["kind_forms"][kind])
            for key, run in job["starts"].items():
                if not any(counts.get(target_code, 0) for counts in run["counts"]):
                    continue
                start = inputs["starts"][key]
                growth = Growth(start, job["law"].endswith("/parity"))
                n_start = len(growth.places)
                tally["replayed starts with form ever present"] += 1
                for t, row in enumerate(run["counts"], 1):
                    growth.make_round(*law_parts(job))
                    pieces = [piece for form, piece in growth.parts_forms() if form == target]
                    assert len(pieces) == row.get(target_code, 0), (job["law"], key, t)
                    for piece in pieces:
                        tally["all parts of form"] += 1
                        if not all(u >= n_start for u in piece):
                            continue
                        tally["parts of form with every member made"] += 1
                        families = {growth.parents[u] for u in piece}
                        if len(families) == 1:
                            parents, = families
                            if len(parents) == 1 and parents[0] < n_start:
                                tally["all three members are offshoots of one start knot"] += 1
                        if any(len(growth.parents[u]) != 1 for u in piece):
                            tally["parts with a join among the members"] += 1
                        if any(p >= n_start for u in piece for p in growth.parents[u]):
                            tally["parts with a made immediate parent"] += 1
                        if witness is None:
                            witness = {
                                "law": job["law"], "start": key, "round": t, "members": piece,
                                "parents": [growth.parents[u] for u in piece],
                                "marks": [growth.marks[u] for u in piece],
                            }
                if limit and tally["replayed starts with form ever present"] == limit:
                    return {"counts": tally, "example": witness}
    return {"counts": tally, "example": witness}


def form_specificity(inputs):
    """Check the reported counterexample to the frozen PB13 prediction."""
    law = "FLOOR1/CANCEL-RETIRE/RELEASE/parity"
    job = next(j for j in job_records("b1", {}) if j["law"] == law)
    target = signature({"hk": [[1, 0], [2, 0], [2, 0]], "maxsets": [[0, 1], [0, 2]], "marks": None})
    target_code, = (i for i, form in enumerate(job["forms"])
                    if sorted(form["hk"]) == [[1, 0], [2, 0], [2, 0]]
                    and signature(form) == target)
    results = {}
    for kind in inputs["alone"]:
        key = f"one-2 + {kind} / W3"
        run = job["starts"][key]
        observations, _ = replay(inputs["starts"][key], job, len(run["per_round"]), target)
        results[kind] = [row["Y form from both"] for row in observations]
        assert results[kind] == pairs_in_round(job, run, target_code)
    return {"law": law, "X": "one-2", "way": "W3", "parts per round by Y": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("probe", "selected"), default="selected")
    args = parser.parse_args()
    inputs = json.loads(STARTS.read_text())
    damage = {}
    records = {}
    timing_cases = {
        ("b1", "FLOOR1/CANCEL-OFFSHOOT/RELEASE/parity", "one-3 + two-22 / W3"),
        ("b1", "FLOOR1/CANCEL-RETIRE/RELEASE/nae", "one-2 + two-22 / W3"),
        ("b1", "FLOOR1/CANCEL-WAIT/RELEASE/nae", "two-33 + two-22 / W2"),
        ("b1", "CAP-3/CANCEL-WAIT/RELEASE/nae", "pairs-4 + two-23 / W4"),
        ("b2_hold", "FLOOR1/CANCEL-OFFSHOOT/HOLD/nae", "two-23 + one-2 / W2"),
        ("b2_other", "FLOOR1/CANCEL-OFFSHOOT/RELEASE/parity", "two-23 + one-2 / W3-other"),
        ("b3_small", "CAP-3/CANCEL-RETIRE/RELEASE/MET(OLDEST)/nae", "one-2 + one-2 / W1"),
        ("b3_small", "CAP-3/CANCEL-WAIT/RELEASE/MET(NEWEST)/nae", "three-222 + three-222 / W1"),
        ("b3_cut", "FLOOR1/CANCEL-RETIRE/RELEASE/MET(NEWEST)/fresh-by-parents/parity", "one-2 + two-22 / W1"),
        ("b3_cut2", "CAP-3/CANCEL-OFFSHOOT/RELEASE/MET(IN-TURN)/nae", "one-2 + one-2 / W1"),
    }
    for file in ("b1", "b2_hold", "b2_other", "b3_small", "b3_cut", "b3_cut2"):
        for job in job_records(file, damage):
            if "error" in job:
                continue
            law = job["law"]
            for key, run in job["starts"].items():
                chosen = (file, law, key) in timing_cases
                if args.mode != "probe" and file == "b1" and law.startswith("FLOOR1/"):
                    chosen |= (
                        key == "one-2 + two-22 / W3"
                        or key == "one-2 + one-3 / W1"
                        or run["first_two"] is not None
                        or ("RETIRE" in law and run["Y kind"] == "one-2")
                    )
                if not chosen:
                    continue
                results, target = compare_start(inputs, job, key)
                controls = compare_controls(inputs, job, key, target)
                records[f"{law}: {key}"] = {
                    "joint": [row["Y form from both"] for row in results],
                    "Y only ended": [row["Y only ended"] for row in results],
                    "Y form with every knot made": [row["Y form with every knot made"] for row in results],
                    "controls": controls,
                }
    report = {"replayed starts": len(records), "runs": records}
    report["PB5 three-222 replays"] = three_sibling_replays(
        inputs, limit=8 if args.mode == "probe" else None
    )
    if args.mode != "probe":
        report["roster counts"] = initial_rosters(inputs)
        report["PB13 example"] = form_specificity(inputs)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
