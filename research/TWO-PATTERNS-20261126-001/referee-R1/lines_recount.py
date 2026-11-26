"""Regrow the two-, three-, and four-part starts without the study engine.

The round is the one in research/RING-IN-BALANCE-20261123-001/definitions.md
and research/PARTS-MEET-AGAIN-20261124-001/definitions.md, with nothing taken
beyond the parents' loose distinctions. No holder is removed.
Every new knot meets just its parents when made, so after constructing the
start we need only the meeting sets and each knot's loose count.
"""
import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import resource
import time


def maximal_cliques(candidates, excluded, neighbors, chosen=()):
    if not candidates and not excluded:
        yield tuple(sorted(chosen))
        return
    pivot = max(candidates | excluded, key=lambda v: len(candidates & neighbors[v]))
    for v in sorted(candidates - neighbors[pivot]):
        yield from maximal_cliques(
            candidates & neighbors[v], excluded & neighbors[v], neighbors, (*chosen, v)
        )
        candidates.remove(v)
        excluded.add(v)


def groups(meetings, members):
    met_sets = {frozenset(s & members) for s in meetings}
    pairs = {pair for s in met_sets for pair in combinations(sorted(s), 2)}
    joinable = {u: set() for pair in pairs for u in pair}
    for u, v in pairs:
        joinable[u].add(v)
        joinable[v].add(u)
    larger = [
        clique
        for clique in maximal_cliques(set(joinable), set(), joinable)
        if len(clique) >= 3 and not any(set(clique) <= met_set for met_set in met_sets)
    ]
    covered_pairs = {pair for clique in larger for pair in combinations(clique, 2)}
    return sorted(larger) + sorted(pairs - covered_pairs)


def make_start(count, join="share", mark=None):
    # Each part is two three-place knots sharing one distinction.
    stars = [[5 * part, 5 * part + a, 5 * part + b]
             for part in range(count) for a, b in ((1, 2), (3, 4))]
    roles = [part for part in range(count) for _ in range(2)]
    new = 5 * count
    if join == "share":
        for site in range(0, 2 * count, 2):
            stars[site].append(new)
        new += 1
    elif join == "meeting":
        assert count == 2
        # One spent knot of three places and one added loose distinction per site.
        stars[0].extend([new, new + 3])
        stars[2].extend([new + 1, new + 2, new + 4])
        stars.append([new, new + 1, new + 2])
        roles.append(-1)
        new += 5
    elif join != "apart":
        raise ValueError(join)
    if mark == "transfer":
        stars[0].remove(1)
        stars[1].append(1)
    elif mark == "extra sharing":
        stars[0].append(new)
        stars[1].append(new)
    elif mark is not None:
        stars[mark].append(new)
    return stars, roles


class Growth:
    def __init__(self, stars, roles, count, names):
        self.count = count
        self.names = names
        holders = defaultdict(list)
        for u, places in enumerate(stars):
            for distinction in places:
                holders[distinction].append(u)
        self.meetings = [set() for _ in stars]
        self.loose = [0 for _ in stars]
        for knots in holders.values():
            if len(knots) == 1:
                self.loose[knots[0]] += 1
            for u, v in combinations(knots, 2):
                self.meetings[u].add(v)
                self.meetings[v].add(u)
        self.ancestry = [{role} for role in roles]
        self.indices = [tuple(0 if role == part else -1 for part in range(count)) for role in roles]
        self.names_by_making = [self.intern(("start", u)) for u in range(len(stars))]
        self.birth_rounds = [0 for _ in stars]
        self.parents = [() for _ in stars]
        self.fresh = [0 for _ in stars]

    def intern(self, key):
        return self.names.setdefault(key, len(self.names))

    def step(self, rnd, ration, treatment):
        members = {u for u, loose in enumerate(self.loose) if loose}
        roster = groups(self.meetings, members)
        owing = Counter(u for group in roster for u in group)
        short = {u for u in members if owing[u] > self.loose[u]}
        kept = [group for group in roster if not short.intersection(group)]
        paying = Counter(u for group in kept for u in group)
        if treatment == "retire":
            for u in short:
                self.loose[u] = 0
        release = members if treatment == "offshoot" else members - short
        births = kept + [(u,) for u in sorted(release)
                         for _ in range(self.loose[u] - paying[u])]
        replacements = {}
        seen = Counter()
        for parents in births:
            u = len(self.parents)
            replacements[u] = parents
            self.parents.append(parents)
            self.meetings.append(set(parents))
            self.loose.append(0)
            for p in parents:
                self.loose[p] -= 1
                self.meetings[p].add(u)
            self.birth_rounds.append(rnd)
            ancestry = set().union(*(self.ancestry[p] for p in parents))
            self.ancestry.append(ancestry)
            self.indices.append(tuple(
                rnd if ancestry == {part} else max(self.indices[p][part] for p in parents)
                for part in range(self.count)
            ))
            parent_names = tuple(sorted(self.names_by_making[p] for p in parents))
            name = self.intern((parent_names, seen[parent_names]))
            seen[parent_names] += 1
            self.names_by_making.append(name)
        waiting = {u for u in short if self.loose[u]}
        demand_groups = groups(self.meetings, waiting | replacements.keys())
        demands = Counter(u for group in demand_groups for u in group)
        for u, parents in replacements.items():
            floor = max(3 - len(parents), 1)
            fresh = max(floor, demands[u])
            if ration == "CAP-3":
                fresh = min(fresh, 3)
            elif ration == "FLOOR1":
                fresh = floor
            else:
                assert ration == "ORD"
            self.loose[u] = fresh
            self.fresh.append(fresh)
        return replacements, short


def distances(meetings, origin, allowed=None):
    distance = {origin: 0}
    queue = [origin]
    for u in queue:
        for v in meetings[u]:
            if v not in distance and (allowed is None or v in allowed):
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance


def profile(growth, knots, rounds):
    middle = [u for u in knots if growth.birth_rounds[u] == 2 * rounds // 3]
    if not middle:
        return {}
    index = min((growth.indices[u] for u in middle),
                key=lambda x: (max(x) - min(x), tuple(-a for a in x)))
    centers = [u for u in middle if growth.indices[u] == index]
    ball_series = []
    for u in centers:
        shell = Counter(distances(growth.meetings, u).values())
        running = 0
        ball = []
        for r in range(min(rounds, max(shell) + 1)):
            running += shell[r]
            ball.append(running)
        ball_series.append(ball)
    return {"indices": index, "round": 2 * rounds // 3, "ball sizes at each center": ball_series}


def joint_components(growth, knots):
    unseen = set(knots)
    summary = []
    while unseen:
        component = set(distances(growth.meetings, min(unseen), unseen))
        unseen -= component
        indices = defaultdict(set)
        for u in component:
            indices[growth.indices[u]].add(u)
        expected = 0
        agreements = 0
        for a, knots_at_a in indices.items():
            for b in ((a[0] + 1, a[1]), (a[0], a[1] + 1)):
                knots_at_b = indices.get(b, set())
                expected += len(knots_at_a) * len(knots_at_b)
                agreements += sum(len(knots_at_b & growth.meetings[u]) for u in knots_at_a)
        actual = sum(len(growth.meetings[u] & component) for u in component) // 2
        summary.append({"knots": len(component), "indices": len(indices),
                        "pairs one index step apart": expected, "of them sharing": agreements,
                        "pairs sharing": actual})
    return summary


def run(count, rounds, names, join="share", ration="ORD", mark=None, treatment="wait"):
    start = time.perf_counter()
    growth = Growth(*make_start(count, join, mark), count, names)
    parent_profile = Counter()
    partial_parents = Counter()
    partial_at_zero = 0
    skipped_indices = Counter()
    table = defaultdict(list)
    own_signatures = [[] for _ in range(count)]
    rounds_profile = []
    joint = set()
    for rnd in range(1, rounds + 1):
        births, short = growth.step(rnd, ration, treatment)
        own = [[] for _ in range(count)]
        multiplicities = Counter()
        for u, parents in births.items():
            index = growth.indices[u]
            ancestry = growth.ancestry[u]
            fresh = growth.fresh[u]
            places = len(parents) + fresh
            if len(ancestry) == 1 and -1 not in ancestry:
                own[next(iter(ancestry))].append((growth.names_by_making[u], places, fresh))
            if -1 in index:
                continue
            joint.add(u)
            multiplicities[index] += 1
            table[index].append((places, fresh))
            for parent in parents:
                earlier = growth.indices[parent]
                if -1 in earlier:
                    parent_profile["a parent not of all parts"] += 1
                    partial_parents[tuple(p for p, a in enumerate(earlier) if a >= 0)] += 1
                    partial_at_zero += all(index[p] == 0 for p, a in enumerate(earlier) if a == -1)
                else:
                    delta = tuple(a - b for a, b in zip(index, earlier))
                    parent_profile[str(delta)] += 1
                    skipped_indices.update((a, b) for a, b in zip(index, earlier) if a - b > 1)
        for part, signature in enumerate(own):
            own_signatures[part].append(sorted(signature))
        rounds_profile.append({
            "round": rnd, "knots of all parts": sum(multiplicities.values()),
            "different places": len(multiplicities),
            "knots at one place (min, max)": [
                min(multiplicities.values(), default=0), max(multiplicities.values(), default=0)
            ],
            "places add up to": dict(Counter(str(sum(x)) for x in multiplicities)),
            "short": len(short), "knots": len(growth.parents),
        })
        if len(growth.parents) > 3000:
            break
    result = {
        "parts": count, "rounds": rounds_profile,
        "total knots of all parts": len(joint),
        "different indices over all rounds": len(table),
        "parents of a knot of all parts, by place steps back": dict(parent_profile),
        "parent index jumps greater than one (earlier to later)": {
            f"{b} to {a}": n for (a, b), n in skipped_indices.items()
        },
        "parents that represent only these parts (numbered from one)": {
            str(tuple(p + 1 for p in parts)): n for parts, n in partial_parents.items()
        },
        "links to a parent lacking parts whose indices at the child are zero": partial_at_zero,
        "balls by sharings": profile(growth, joint, len(rounds_profile)),
        "own births by round": [[len(s) for s in sequence] for sequence in own_signatures],
        "seconds": time.perf_counter() - start,
    }
    if count == 2:
        result["components on knots of both under sharings"] = joint_components(growth, joint)
    return result, {k: sorted(v) for k, v in table.items()}, own_signatures


def compare_mark(base, marked):
    profile0, table0, own0 = base
    profile1, table1, own1 = marked
    changed = sorted(k for k in table0.keys() | table1.keys() if table0.get(k) != table1.get(k))
    different_count = [k for k in changed if len(table0.get(k, ())) != len(table1.get(k, ()))]
    larger_same_count = [
        k for k in set(changed) - set(different_count)
        if all(size >= old_size and fresh >= old_fresh
               for (old_size, old_fresh), (size, fresh) in zip(table0[k], table1[k]))
    ]
    same_count_shifts = Counter(
        (tuple(table0[k]), tuple(table1[k])) for k in set(changed) - set(different_count)
    )
    return {
        "knots": profile1["rounds"][-1]["knots"],
        "short members, all rounds": sum(r["short"] for r in profile1["rounds"]),
        "the first part's own births by round": profile1["own births by round"][0],
        "unmarked": profile0["own births by round"][0],
        "the second part's own births by round": profile1["own births by round"][1],
        "places of the table that differ": len(changed),
        "of them with another number of knots": len(different_count),
        "same number of knots with some more places or fresh distinctions": len(larger_same_count),
        "changes when the number of knots is equal": [
            {"unmarked (places, fresh)": before, "marked (places, fresh)": after, "indices": n}
            for (before, after), n in sorted(same_count_shifts.items())
        ],
        "original places of the table that differ": sum(k in table0 for k in changed),
        "new places of the table": len(table1.keys() - table0.keys()),
        "places that differ, by place along the first line": dict(Counter(str(k[0]) for k in changed)),
        "places that differ, by place along the second line": dict(Counter(str(k[1]) for k in changed)),
        "places of the table in the marked growth": len(table1),
        "examples": [[list(k),
                      None if k not in table0 else [list(x) for x in table0[k]],
                      None if k not in table1 else [list(x) for x in table1[k]]]
                     for k in changed[:4]],
        "first difference in each part's own births by making": [
            next((r for r, (a, b) in enumerate(zip(s0, s1), 1) if a != b), None)
            for s0, s1 in zip(own0, own1)
        ],
        "seconds": profile1["seconds"],
    }


def record_agreement(configs, marks):
    bench = Path(__file__).resolve().parent.parent / "bench"
    result = {}
    for k in (2, 3):
        reference = json.loads((bench / f"table_check_{k}.json").read_text())
        actual = configs[f"{k} parts"][0]
        ball = actual["balls by sharings"]
        ball_key = f"ball around the knot at places {ball['indices']} made in round {ball['round']}, by sharings"
        selected = {key: actual[key] for key in reference if key in actual}
        selected[ball_key] = ball["ball sizes at each center"][0]
        result[f"table_check_{k}.json"] = sorted(
            key for key in reference.keys() | selected.keys() if reference.get(key) != selected.get(key)
        )
    reference = json.loads((bench / "table_mark.json").read_text())
    actual = marks["unmarked"]
    discrepancies = [key for key in reference["unmarked"] if reference["unmarked"][key] != actual[key]]
    if marks["rounds"] != reference["rounds"]:
        discrepancies.append("rounds")
    for label in ("mark at the first part's first knot (its site)", "mark at the first part's other knot"):
        discrepancies.extend(f"{label}: {key}" for key, value in reference[label].items()
                             if marks[label].get(key) != value)
    result["table_mark.json"] = discrepancies
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-rounds", type=int, default=12)
    args = parser.parse_args()
    if args.limit_rounds < 1:
        parser.error("--limit-rounds must be positive")
    start = time.perf_counter()
    rounds = min(12, args.limit_rounds)
    mark_rounds = min(10, args.limit_rounds)
    names = {}
    configs = {f"{k} parts": run(k, rounds, names) for k in (2, 3, 4)}
    controls = {f"two parts {join} {ration}": run(2, rounds, names, join=join, ration=ration)[0]
                for join, ration in (("meeting", "ORD"), ("apart", "ORD"),
                                     ("share", "CAP-3"), ("share", "FLOOR1"))}
    short_treatments = {
        f"{k} parts, short knots {treatment}": run(k, rounds, names, treatment=treatment)[0]
        for k in (3, 4) for treatment in ("retire", "offshoot")
    }
    base = run(2, mark_rounds, names)
    marks = {
        "rounds": mark_rounds,
        "unmarked": {
            "knots": base[0]["rounds"][-1]["knots"],
            "short members, all rounds": sum(row["short"] for row in base[0]["rounds"]),
            "places of the table": len(base[1]),
            "seconds": base[0]["seconds"],
        },
    }
    for mark, label in ((0, "mark at the first part's first knot (its site)"),
                        (1, "mark at the first part's other knot"),
                        ("transfer", "move a loose distinction from the site to the other knot"),
                        ("extra sharing", "add one distinction shared by the first part's two knots")):
        marks[label] = compare_mark(base, run(2, mark_rounds, names, mark=mark))
    result = {
        "shared distinction": {label: run[0] for label, run in configs.items()},
        "changes to join and ration": controls, "changes to treatment": short_treatments,
        "changes to the mark": marks,
        "discrepancies against committed tables": (
            record_agreement(configs, marks) if rounds == 12 and mark_rounds == 10 else None
        ),
        "seconds": time.perf_counter() - start,
        "maximum resident memory in KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
