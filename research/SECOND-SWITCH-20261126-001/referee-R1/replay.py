"""Rebuild recorded marks and test signed controls with the independent growth."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import random
import resource
import time

from growth import State, roster_groups, start


HERE = Path(__file__).resolve().parent
SEED = 20261126
ROUNDS = 24
KNOT_LIMIT = 6000


def archived(file_name):
    with gzip.open(HERE.parent / file_name, "rt", encoding="utf-8") as source:
        return [json.loads(line) for line in source]


def key(item):
    return item["A"], item["B"], item["law"]


def sample_marks(rows, base_info, pilot=False):
    rng = random.Random(SEED)
    strata = defaultdict(list)
    for row in rows:
        reading = row["reading"]
        if reading == "change":
            stratum = reading, row["law"], row["sign"]
        elif reading == "waiting":
            stratum = reading, row["t0"], row["sign"]
        else:
            stratum = reading, row["law"], row["heard"] is not None
        strata[stratum].append(row)

    selected = []
    for stratum, group in sorted(strata.items()):
        count = 4 if stratum[0] != "horizon" else 3
        if pilot:
            count = 1
        for row in rng.sample(group, min(count, len(group))):
            selected.append((row, "stratified"))
    if pilot:
        return selected

    included = {id(row) for row, _ in selected}
    for row in rows:
        if row["reading"] != "horizon" or row["heard"] is None or id(row) in included:
            continue
        if row["sharings"] > 4 or row["heard"] == row["t0"] + row["sharings"]:
            selected.append((row, "hearing at the proposed bound or from over four sharings"))
            included.add(id(row))
    censored = [
        row for row in rows
        if row["reading"] == "change"
        and row["rounds"] < row["t0"] + row["sharings"]
        and id(row) not in included
    ]
    early_changed_stop = [row for row in censored if row["rounds"] < base_info[key(row)]["rounds"]]
    selected.extend((row, "shorter changed run") for row in early_changed_stop)
    other_censored = [row for row in censored if row["rounds"] == base_info[key(row)]["rounds"]]
    selected.extend((row, "short coverage") for row in rng.sample(other_censored, 4))
    return selected


def grow(state, own=(), sizes=(), snapshots=(), read_distance=False, round_limit=ROUNDS):
    own, sizes = list(own), list(sizes)
    nearest, saved = [], {}
    while state.r < round_limit and len(state.h) <= KNOT_LIMIT:
        state.step()
        own.append(state.own)
        sizes.append(len(state.h))
        if state.r in snapshots:
            saved[state.r] = state.copy()
        if read_distance:
            distance = state.distances()
            nearest.append(min(
                (distance[u] for u, h in enumerate(state.h)
                 if h and state.role[u] == 2 and u in distance),
                default=None,
            ))
    return own, sizes, nearest, saved


def check(issues, field, actual, expected):
    if actual != expected:
        issues[field] = {"replay": actual, "archive": expected}


def counts(per_round):
    return [len(births) for births in per_round]


def birth_places(births):
    return sorted((fresh, places) for _, fresh, places in births)


def receiver_locations(state):
    parts, direct, classes = state.partition()
    own = {u for u in parts if state.role[u] == 1}
    own_parts = {parts[u] for u in own}
    own_classes = {classes[u] for u in own}
    adjoining = {
        q if p in own_parts else p
        for p, q in direct
        if p in own_parts or q in own_parts
    }
    return {
        u: "same part" if p in own_parts else
        "directly linked part" if p in adjoining else
        "same class" if classes[u] in own_classes else
        "different class"
        for u, p in parts.items()
    }


def first_difference(a, b, t0):
    return next(
        (r for r, (x, y) in enumerate(zip(a[t0:], b[t0:]), t0 + 1) if x != y),
        None,
    )


def trajectory(snapshot, base_own, base_sizes, u, sign, round_limit=ROUNDS):
    t0 = snapshot.r
    branch = snapshot.copy()
    branch.mark(u, sign)
    changed_own, changed_sizes, _, _ = grow(
        branch, base_own[:t0], base_sizes[:t0], round_limit=round_limit
    )
    base_new = [b - a for a, b in zip(base_sizes[t0 - 1:], base_sizes[t0:])]
    changed_new = [b - a for a, b in zip(changed_sizes[t0 - 1:], changed_sizes[t0:])]
    overall_step = first_difference(base_new, changed_new, 0)
    return (
        {
            "common rounds": min(len(base_own), len(changed_own)),
            "changed rounds": len(changed_own),
            "changed final knots": changed_sizes[-1],
            "baseline final knots": base_sizes[-1],
            "heard": first_difference(base_own, changed_own, t0),
            "heard by fresh and places": first_difference(
                list(map(birth_places, base_own)), list(map(birth_places, changed_own)), t0
            ),
            "heard by count": first_difference(counts(base_own), counts(changed_own), t0),
            "first difference in all birth counts": None if overall_step is None else t0 + overall_step,
        },
        changed_own,
    )


def replay_mark(row, reason, snapshot, locations, base_own, base_sizes):
    u, t0 = row["knot"], row["t0"]
    sign = row.get("sign", "add")
    distance = snapshot.distances()
    evidence = {field: row[field] for field in ("reading", "A", "B", "law", "t0", "knot", "sharings")}
    evidence.update({"sign": sign, "sample": reason, "issues": {}})
    issues = evidence["issues"]
    check(issues, "sharing distance", distance.get(u), row["sharings"])
    if u < 0 or u >= len(snapshot.h) or not snapshot.h[u]:
        issues["eligible target"] = False
        return evidence
    role = snapshot.role[u]
    evidence["roster relation to receiver"] = locations[u]
    if row["reading"] == "horizon":
        reading = "A" if role == 1 else "B" if role == 2 else "joint" if role & 3 == 3 else "link"
        check(issues, "ancestry", reading, row["class"])
        candidates = [
            v for v, h in enumerate(snapshot.h)
            if h and snapshot.role[v] != 1 and distance.get(v) == row["sharings"]
        ][:3]
    else:
        check(issues, "strict far ancestry", role, 2)
        eligible = [v for v, h in enumerate(snapshot.h) if h and snapshot.role[v] == 2]
        if row["reading"] == "waiting":
            check(issues, "round made", snapshot.born[u], row["made"])
            eligible = [v for v in eligible if snapshot.born[v] < t0 and v in distance]
        candidates = sorted(eligible, key=lambda v: (distance.get(v, float("inf")), v))
        candidates = candidates[:1] if row["reading"] == "waiting" else candidates[:5]
    if u not in candidates:
        issues["target selection"] = {"replay": candidates, "archive": u}

    result, changed_own = trajectory(snapshot, base_own, base_sizes, u, sign)
    evidence.update(result)
    for field, value in (("heard", row["heard"]), ("common rounds", row["rounds"])):
        check(issues, field, result[field], value)
    if "own births" in row:
        check(issues, "baseline own births", counts(base_own), row["own births"])
    if "own births with" in row:
        check(issues, "changed own births", counts(changed_own), row["own births with"])
    return evidence


def ordinary_bars(ordinary_rows, pilot):
    """Swap the sign at the archived ordinary-count places for the next round."""
    grouped = defaultdict(list)
    for row in ordinary_rows:
        grouped[key(row)].append(row)
    trials = []
    for (a, b, law), group in sorted(grouped.items()):
        if pilot:
            group = group[:1]
        baseline_limit = max(row["t0"] + 1 for row in group)
        base_own, base_sizes, _, saved = grow(
            start(a, b, law), snapshots={x["t0"] for x in group}, round_limit=baseline_limit
        )
        for row in group:
            t0, u = row["t0"], row["knot"]
            snapshot = saved[t0]
            result, changed_own = trajectory(snapshot, base_own, base_sizes, u, "bar", t0 + 1)
            result.pop("first difference in all birth counts")
            record = {
                "A": a, "B": b, "law": law, "t0": t0, "knot": u,
                "sharings": snapshot.distances()[u], "usable before": snapshot.h[u],
                "heard for archived addition": row["heard"], **result,
            }
            if result["heard"] is not None:
                r = result["heard"]
                record["own births at hearing"] = [len(base_own[r - 1]), len(changed_own[r - 1])]
                if r == t0 + 1:
                    groups = [g for g in roster_groups(
                        snapshot.met, [i for i, count in enumerate(snapshot.h) if count]
                    ) if u in g]
                    record["next-round groups with target"] = groups
                    record["owes before"] = len(groups)
                    record["own members in those groups"] = sorted({
                        v for group in groups for v in group if snapshot.role[v] == 1
                    })
            trials.append(record)
    return trials


def speed_witness():
    # Three successive members leave in rounds 1 through 3. The last departure
    # leaves A (0) able to pay, while B (1) and the other member (2) still wait.
    # Each spent witness holds two different distinctions with each member it
    # meets. Even the member that owes just one starts with three places.
    witnesses = [(0, 1, 2), (0, 3), (3, 4), (4, 5)]
    h = [2, 1, 1, 1, 1, 1] + [0] * len(witnesses)
    roles = [1, 2] + [4] * (len(h) - 2)
    places = [[] for _ in h]
    met = [set() for _ in h]
    distinction = 0
    for w, witnessed in enumerate(witnesses, 6):
        for member in witnessed:
            met[w].add(member)
            met[member].add(w)
            for _ in range(2):
                places[w].append(distinction)
                places[member].append(distinction)
                distinction += 1
    for u, count in enumerate(h):
        places[u].extend(range(distinction, distinction + count))
        distinction += count
    assert all(len(held) >= 3 for held in places)
    state = State(h.copy(), met, roles.copy(), "CAP-3")
    initial_members = []
    for _ in range(3):
        state.step()
        initial_members.append([u for u in range(6) if state.h[u]])
    assert initial_members == [[0, 1, 2, 3, 4], [0, 1, 2, 3], [0, 1, 2]]
    distance = state.distances()[1]
    groups = roster_groups(state.met, [u for u, count in enumerate(state.h) if count])
    changed = state.copy()
    changed.mark(1, "add")
    state.step()
    changed.step()
    assert distance == 2 and len(state.own) == 2 and len(changed.own) == 1
    return {
        "law": "CAP-3", "t0": 3, "heard": 4, "sharings": distance, "sign": "add",
        "start places": places, "roles": roles, "target": 1, "groups at hearing": groups,
        "start members remaining after each round": initial_members,
        "short in round four without and with the mark": [sorted(state.short), sorted(changed.short)],
        "round-four own counts": [len(state.own), len(changed.own)],
    }


def horizon_ties(horizon_rows):
    """Choose the highest name outside the archive from sampled tied places."""
    by_cell = defaultdict(list)
    for row in horizon_rows:
        by_cell[key(row), row["t0"], row["sharings"]].append(row)
    by_sharings = defaultdict(list)
    for cell, rows in sorted(by_cell.items()):
        if len(rows) == 3:
            by_sharings[cell[2]].append((cell, rows))
    rng = random.Random(SEED)
    replacements = []
    for cells in by_sharings.values():
        rng.shuffle(cells)
        tried = 0
        for (setup, t0, sharings), rows in cells:
            snapshot = start(*setup)
            for _ in range(t0):
                snapshot.step()
            distance = snapshot.distances()
            old = {row["knot"] for row in rows}
            other = [u for u, h in enumerate(snapshot.h) if h and snapshot.role[u] != 1
                     and distance.get(u) == sharings and u not in old]
            if not other:
                continue
            u = max(other)
            end = t0 + sharings + 3
            base_own, base_sizes, _, saved = grow(
                start(*setup), snapshots={t0}, round_limit=end
            )
            result, _ = trajectory(saved[t0], base_own, base_sizes, u, "add", end)
            replacements.append({
                "A": setup[0], "B": setup[1], "law": setup[2], "t0": t0, "sharings": sharings,
                "knot": u, "archived knot and hearing": [[row["knot"], row["heard"]] for row in rows],
                **result,
            })
            tried += 1
            if tried == 3:
                break
    return replacements


def run(pilot, full):
    raw = archived("second_runs.jsonl.gz")
    waiting = [
        dict(row, reading="waiting", A="tri:122@0", law="CAP-3")
        for row in archived("waiting_far_runs.jsonl.gz")
    ]
    base_info = {key(row): row for row in raw if row["reading"] == "base"}
    archived_distance = {
        key(row): row["by round"] for row in raw if row["reading"] == "far end distance"
    }
    horizon = [row for row in raw if row["reading"] == "horizon"]
    marks = [row for row in raw if row["reading"] == "change"] + horizon + waiting
    groups = defaultdict(list)
    selected = sample_marks(marks, base_info, pilot)
    if full:
        included = {id(row) for row, _ in selected}
        selected += [(row, "remaining archive") for row in marks if id(row) not in included]
        unique = {
            (row["reading"], *key(row), row["t0"], row["knot"], row.get("sign", "add"))
            for row, _ in selected
        }
        assert len(selected) == len(unique) == 1140
    for row, reason in selected:
        groups[key(row)].append((row, reason))
    setups = sorted(set(groups) | set(base_info))
    stub = {(a, law): grow(start(a, "stub", law))[0] for a, law in {(x[0], x[2]) for x in base_info}}
    baseline, changed = [], []
    for i, (a, b, law) in enumerate(setups, 1):
        setup = a, b, law
        selected = groups[setup]
        base_own, base_sizes, nearest, saved = grow(
            start(*setup), snapshots={row["t0"] for row, _ in selected},
            read_distance=setup in base_info,
        )
        if setup in base_info:
            row = base_info[setup]
            record = {"A": a, "B": b, "law": law, "issues": {}}
            issues = record["issues"]
            check(issues, "rounds", len(base_own), row["rounds"])
            check(issues, "knots", base_sizes[-1], row["knots"])
            check(issues, "own births", counts(base_own), row["own births"])
            check(issues, "own births with a stub", counts(stub[a, law]), row["own births with a stub"])
            check(issues, "nearest far member by round", nearest, archived_distance[setup])
            record["first hearing against stub"] = first_difference(stub[a, law], base_own, 0)
            record["first count difference against stub"] = first_difference(
                counts(stub[a, law]), counts(base_own), 0
            )
            baseline.append(record)
        locations = {r: receiver_locations(snapshot) for r, snapshot in saved.items()}
        for row, reason in selected:
            t0 = row["t0"]
            changed.append(replay_mark(row, reason, saved[t0], locations[t0], base_own, base_sizes))
        if not pilot and (i % 10 == 0 or i == len(setups)):
            print(f"Rebuilt {i}/{len(setups)} preparations and {len(changed)} marks.", flush=True)

    ordinary = ordinary_bars([row for row in horizon if row["law"] == "ORD"], pilot)
    ties = [] if pilot else horizon_ties(horizon)
    shortened = [
        {
            **{k: row[k] for k in (
                "A", "B", "law", "t0", "knot", "sign", "sharings", "changed rounds",
                "changed final knots", "baseline final knots", "common rounds",
            )},
            "baseline rounds": base_info[key(row)]["rounds"],
        }
        for row in changed
        if row["reading"] == "change"
        and row.get("common rounds", float("inf")) < row["t0"] + row["sharings"]
        and row["common rounds"] < base_info[key(row)]["rounds"]
    ]
    return {
        "seed": SEED,
        "sampling": (
            "Four marks in each far law and sign stratum and waiting round and sign stratum, "
            "and three in each horizon law and archived hearing stratum, drawn without replacement. "
            "All recorded hearings at the proposed lower round bound and beyond four sharings "
            "included, plus the otherwise unselected shortened changed runs under the proposed bound "
            "and four further unselected far marks with short follow-up. "
            "The ordinary sign swap uses all its archived horizon places for the next round. "
            "The alternate numeric tie choice uses up to three sampled cells per sharing distance "
            "with a member outside the archive, choosing the highest name outside the original three "
            "and following the branch up to the proposed earliest hearing round plus three."
        ),
        "archive scope": "all" if full else "sample",
        "bounds": {"rounds": ROUNDS, "knots": KNOT_LIMIT},
        "summary": {
            "archived baseline cases": len(baseline),
            "baseline mismatches": sum(bool(row["issues"]) for row in baseline),
            "archived marks replayed": dict(Counter(row["reading"] for row in changed)),
            "marks in seeded and targeted sample": dict(Counter(
                row["reading"] for row in changed if row["sample"] != "remaining archive"
            )),
            "mark mismatches": sum(bool(row["issues"]) for row in changed),
            "heard by the recorded reading": dict(Counter(
                row["reading"] for row in changed if row.get("heard") is not None
            )),
            "heard by own count": dict(Counter(
                row["reading"] for row in changed if row.get("heard by count") is not None
            )),
            "horizon hearings by roster relation to receiver": dict(Counter(
                row["roster relation to receiver"] for row in changed
                if row["reading"] == "horizon" and row.get("heard") is not None
            )),
            "horizon hearings at the same round by count": sum(
                row["reading"] == "horizon" and row.get("heard") is not None
                and row["heard"] == row["heard by count"] for row in changed
            ),
            "ordinary horizon bars": len(ordinary),
            "ordinary horizon bars heard on next round": sum(row["heard"] is not None for row in ordinary),
            "alternate numeric tie choices": len(ties),
            "alternate numeric ties heard": sum(row["heard"] is not None for row in ties),
            "far marks with shorter changed coverage before the proposed lower bound": len(shortened),
            "of those, changed runs exceeding the knot bound": sum(
                row["changed final knots"] > KNOT_LIMIT for row in shortened
            ),
            "of those, baselines reaching the proposed lower bound": sum(
                row["baseline rounds"] >= row["t0"] + row["sharings"] for row in shortened
            ),
        },
        "baselines": baseline,
        "archived marks": changed,
        "ordinary horizon bars": ordinary,
        "alternate numeric tie choices": ties,
        "early changed-run stops": shortened,
        "speed witness outside archived panel": speed_witness(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--pilot", action="store_true")
    scope.add_argument("--all", action="store_true")
    args = parser.parse_args()
    before = time.perf_counter()
    result = run(args.pilot, args.all)
    print(json.dumps(result["summary"], indent=2))
    elapsed, peak = time.perf_counter() - before, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"{elapsed:.2f} seconds, {peak} KiB peak resident")
    result["elapsed seconds"] = round(elapsed, 2)
    result["peak resident KiB"] = peak
    if args.pilot:
        for reading in ("baselines", "archived marks"):
            for row in result[reading]:
                if row["issues"]:
                    print(json.dumps(row))
    else:
        (HERE / "replay.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
