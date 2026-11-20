"""Exact bond minima on a wired parity presentation by separator partitions."""

from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "certify.json"
PREVIOUS = "STATE-FEEDS-GROWTH-20261119-001"
GROWTH = ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_feedback")
EDDY = "EDDY-WORLD-20261119-001"
SOURCES = ROOT / "experiments" / EDDY / (EDDY + "-E001_world") / "inputs.json"
FOCUS = ((0, 2), (0, 8), (0, 15), (2, 5), (3, 4), (6, 12), (10, 15))


class Wired:
    def __init__(self, stars):
        self.stars = tuple(map(frozenset, stars))
        self.outside = len(self.stars)
        self.all_knots = set(range(self.outside + 1))
        held = defaultdict(list)
        for j, row in enumerate(self.stars):
            for bit in row:
                held[bit].append(j)
        assert all(1 <= len(row) <= 2 for row in held.values())
        self.ends = {bit: tuple(row) if len(row) == 2 else (row[0], self.outside)
                     for bit, row in held.items()}
        self.near = [defaultdict(int) for _ in range(self.outside + 1)]
        for a, b in self.ends.values():
            self.near[a][b] += 1
            self.near[b][a] += 1
        assert self.connected(self.all_knots)

    def connected(self, shore):
        if not shore:
            return False
        queue = [min(shore)]
        seen = set(queue)
        for j in queue:
            onward = (self.near[j].keys() & shore) - seen
            seen.update(onward)
            queue.extend(onward)
        return seen == shore

    def witness(self, mask):
        inside = {j for j in self.all_knots if mask & (1 << j)}
        assert self.outside not in inside
        assert self.connected(inside) and self.connected(self.all_knots - inside)
        boundary = sorted(bit for bit, (a, b) in self.ends.items() if (a in inside) != (b in inside))
        return {"shore": sorted(inside), "crossing_distinctions": boundary, "cost": len(boundary)}


@dataclass(frozen=True)
class Child:
    at: int
    positions: tuple[int, ...]


@dataclass(frozen=True)
class Bag:
    names: tuple[int, ...]
    children: tuple[Child, ...]
    edges: tuple[tuple[int, int], ...]


def min_fill(graph):
    """Only the filled graph sets the bags. Its extra links never carry a cost."""
    neighbors = [set(row) for row in graph.near]
    outside = graph.outside
    for j in range(outside):
        neighbors[j].add(outside)
        neighbors[outside].add(j)
    waiting = set(range(outside))
    records = []
    while waiting:
        def score(v):
            return (sum(b not in neighbors[a] for a, b in combinations(neighbors[v], 2)),
                    len(neighbors[v]), v)
        j = min(waiting, key=score)
        later = tuple(sorted(neighbors[j]))
        records.append((j, later))
        waiting.remove(j)
        for a, b in combinations(later, 2):
            neighbors[a].add(b)
            neighbors[b].add(a)
        for v in later:
            neighbors[v].remove(j)
    order = {j: i for i, (j, _) in enumerate(records)}
    order[outside] = len(order)
    child_lists = defaultdict(list)
    for i, (_, later) in enumerate(records):
        child_lists[min(order[j] for j in later)].append(i)
    records.append((outside, ()))
    result = []
    for i, (j, later) in enumerate(records):
        names = (j, *later)
        where = {v: index for index, v in enumerate(names)}
        links = tuple((where[v], graph.near[j][v]) for v in later if v in graph.near[j])
        children = tuple(Child(k, tuple(where[v] for v in records[k][1])) for k in child_lists[i])
        result.append(Bag(names, children, links))
    return result


def join_classes(reps, links):
    result = list(reps)
    for a, b in links:
        if result[a] != result[b]:
            keep, replace = sorted((result[a], result[b]))
            result = [keep if part == replace else part for part in result]
    return tuple(result)


def forget_front(colors, reps, closed):
    """Every finished component needs the live exterior or the unique inside flag."""
    if reps[0] not in reps[1:]:
        if not colors[0] or 1 in colors[1:] or closed:
            return None
        closed = True
    first = {}
    remaining = tuple(first.setdefault(rep, i) for i, rep in enumerate(reps[1:]))
    return remaining, closed


def improve(table, key, record):
    if key not in table or record < table[key]:
        table[key] = record


@dataclass
class Work:
    budget: int
    operations: int = 0
    max_factor_states: int = 0

    def charge(self, steps=1):
        self.operations += steps
        if self.operations > self.budget:
            raise OverflowError("separator-state transition limit")


def solve_pins(graph, decomposition, pins, work_budget):
    """Minimize conditional on literal colors of the four marked endpoints."""
    work = Work(work_budget)
    # A factor groups equal boundary colors. Within each group retain the
    # cheapest realization of each exact partition and sealed-inside flag.
    factors = {}
    completed = decomposition[-1]
    for index, bag in enumerate(decomposition[:-1]):
        v = bag.names[0]
        child_factors = [(child.positions, factors.pop(child.at)) for child in bag.children]
        domains = [(pins[k],) if k in pins else (0, 1) for k in bag.names]
        table = defaultdict(dict)
        for colors in product(*domains):
            work.charge()
            same = tuple((0, j) for j, _ in bag.edges if colors[j] == colors[0])
            paid = sum(weight for j, weight in bag.edges if colors[j] != colors[0])
            partial = {(join_classes(range(len(colors)), same), False): (paid, (1 << v) if colors[0] else 0)}
            for positions, factor in child_factors:
                matching = factor.get(tuple(colors[i] for i in positions), {})
                following = {}
                for (classes, closed), (cost, mask) in partial.items():
                    for (peer, child_closed), (other_cost, other_mask) in matching.items():
                        work.charge()
                        if child_closed and (closed or 1 in colors):
                            continue
                        links = tuple((positions[i], positions[rep]) for i, rep in enumerate(peer) if i != rep)
                        key = join_classes(classes, links), closed or child_closed
                        improve(following, key, (cost + other_cost, mask | other_mask))
                partial = following
            for (reps, closed), record in partial.items():
                boundary = forget_front(colors, reps, closed)
                if boundary is not None:
                    improve(table[colors[1:]], boundary, record)
        work.max_factor_states = max(work.max_factor_states, sum(map(len, table.values())))
        factors[index] = table

    # The exterior is the only root member. Exactly one retired inside
    # component is required. Outside components were kept alive by the root.
    filled = None
    empty = (0, 0)
    for child in completed.children:
        assert child.positions == (0,)
        records = factors.pop(child.at).get((0,), {})
        zero, one = (records.get(((0,), flag)) for flag in (False, True))
        choices = []
        if empty is not None and one is not None:
            choices.append((empty[0] + one[0], empty[1] | one[1]))
        if filled is not None and zero is not None:
            choices.append((filled[0] + zero[0], filled[1] | zero[1]))
        filled = min(choices) if choices else None
        empty = ((empty[0] + zero[0], empty[1] | zero[1])
                 if empty is not None and zero is not None else None)
    assert not factors
    return filled, work


def orientations(graph, first, second):
    for directions in product((0, 1), repeat=2):
        pins = {graph.outside: 0}
        for bit, color in zip((first, second), directions, strict=True):
            a, b = graph.ends[bit]
            if pins.get(a, color) != color or pins.get(b, 1 - color) != 1 - color:
                break
            pins[a], pins[b] = color, 1 - color
        else:
            yield pins


def pair(graph, decomposition, first, second, work_budget):
    outcomes = []
    for pins in orientations(graph, first, second):
        outcome = {"pins": sorted(pins.items())}
        try:
            answer, effort = solve_pins(graph, decomposition, pins, work_budget)
        except OverflowError:
            outcome.update(status="capped", work_budget=work_budget)
        else:
            outcome.update(status="infeasible", work=effort.operations,
                           max_factor_states=effort.max_factor_states)
            if answer is not None:
                cost, mask = answer
                witness = graph.witness(mask)
                assert witness["cost"] == cost
                assert {first, second} <= set(witness["crossing_distinctions"])
                assert all(bool(mask & (1 << j)) == color for j, color in pins.items())
                outcome.update(status="exact", **witness)
        outcomes.append(outcome)
    return finish_pair(first, second, outcomes)


def finish_pair(first, second, outcomes):
    feasible = [row for row in outcomes if row["status"] == "exact"]
    best = min(feasible, key=lambda row: row["cost"]) if feasible else None
    if any(row["status"] == "capped" for row in outcomes):
        status = "capped"
    else:
        status = "exact" if best else "infinite"
    return {"marks": [first, second], "status": status,
            "bond_distance": best["cost"] - 1 if status == "exact" else None,
            "upper_bound": best["cost"] - 1 if best else None, "orientations": outcomes}


def native_pairs(graph, decomposition, requested, state_budget, binary, known=None):
    known = known or {}
    tie_order = sorted(requested, key=lambda key: -known.get(key, len(graph.ends)))
    requests = [(a, b, pins, known.get((a, b), len(graph.ends)))
                for a, b in tie_order for pins in orientations(graph, a, b)]
    links = [(a, b, w) for a, near in enumerate(graph.near) for b, w in near.items() if a < b]
    wire = [[len(graph.all_knots), len(links), len(requests), state_budget],
            *links, [bag.names[0] for bag in decomposition]]
    wire.extend([len(pins), ceiling, *(entry for link in sorted(pins.items()) for entry in link)]
                for _, _, pins, ceiling in requests)
    run = subprocess.run([binary], input="\n".join(" ".join(map(str, row)) for row in wire) + "\n",
                         text=True, capture_output=True, check=True)
    outcomes = defaultdict(list)
    for (a, b, pins, ceiling), response in zip(requests, run.stdout.splitlines(), strict=True):
        status, *receipt = response.split()
        cost, *mask_words, work, stored = map(int, receipt)
        assert status in ("exact", "infeasible", "capped") and len(mask_words) == 4
        row = {"pins": sorted(pins.items()), "status": status,
               "uncached_partition_merges": work, "max_new_factor_states": stored}
        if status == "infeasible" and ceiling < len(graph.ends):
            row.update(status="above_verified_ceiling", lower_bound_cost=ceiling + 1)
        if status == "exact":
            mask = sum(word << (64 * j) for j, word in enumerate(mask_words))
            assert all(bool(mask & (1 << j)) == color for j, color in pins.items())
            witness = graph.witness(mask)
            assert cost == witness["cost"] <= ceiling and {a, b} <= set(witness["crossing_distinctions"])
            row.update(witness)
        outcomes[a, b].append(row)
    return {key: finish_pair(*key, outcomes[key]) for key in requested}


def direct_words(stars):
    """Read the minimal nonzero parity equations without assuming the bond theorem."""
    span = {frozenset()}
    for row in stars:
        span.update(word ^ row for word in tuple(span))
    span.remove(frozenset())
    minimal = []
    for row in sorted(span, key=lambda word: (len(word), sorted(word))):
        if not any(previous <= row for previous in minimal):
            minimal.append(row)
    return minimal


def synthetic_controls(binary=None):
    plain = tuple(frozenset(e for e in (j - 1, j, 6 + 2*j, 7 + 2*j) if 0 <= e < 5 or e >= 6)
                  for j in range(6))
    lobes = tuple(map(frozenset, ((0, 1, 2), (0, 3, 4), (5, 6, 7), (5, 8, 9))))
    weighted = tuple(map(frozenset, ((0, 1, 4), (0, 1, 2, 3), (2, 3, 5), (5, 6, 7))))
    rows = {}
    for label, stars in (("short_path", plain), ("separate_wired_lobes", lobes), ("parallel_links", weighted)):
        graph = Wired(stars)
        bags = min_fill(graph)
        words = direct_words(stars)
        tally = defaultdict(int)
        pairs = list(combinations(sorted(graph.ends), 2))
        native = native_pairs(graph, bags, pairs, 100000, binary) if binary else None
        for first, second in pairs:
            expected = min((len(row) - 1 for row in words if {first, second} <= row), default=None)
            answer = pair(graph, bags, first, second, 100000)
            assert answer["status"] != "capped" and answer["bond_distance"] == expected
            if native:
                comparison = native[first, second]
                assert comparison["status"] == answer["status"] and comparison["bond_distance"] == expected
                assert [row.get("cost") for row in comparison["orientations"]] == [
                    row.get("cost") for row in answer["orientations"]
                ]
            tally[answer["status"]] += 1
        rows[label] = dict(tally)
    graph = Wired(plain)
    relaxed = float("inf")
    one_shore = float("inf")
    for colors in product((0, 1), repeat=graph.outside):
        inside = {j for j, color in enumerate(colors) if color}
        crossing = {bit for bit, (a, b) in graph.ends.items() if (a in inside) != (b in inside)}
        if {0, 4} <= crossing:
            relaxed = min(relaxed, len(crossing))
            if graph.connected(inside):
                one_shore = min(one_shore, len(crossing))
    exact = pair(graph, min_fill(graph), 0, 4, 100000)
    assert relaxed == 6 < one_shore == exact["bond_distance"] + 1 == 10
    rows["relaxation_gap"] = {"marks": [0, 4], "unrestricted_cost": relaxed, "bond_cost": 10}
    return rows


def frozen_source():
    sys.path.insert(0, str(GROWTH))
    from growth import predecessor, step

    contents = SOURCES.read_bytes()
    spec, = [row for row in json.loads(contents)["cases"] if row["id"] == "J1"]
    raw = tuple(map(tuple, predecessor().source_stars(spec)))
    path = spec["roles"]["anchors"]
    ring, = spec["roles"]["ring_edges"]
    assert len(path) == 16 and len(ring) == 5
    for marked in (set(), set(ring)):
        assert all(len(marked.intersection(row)) % 2 == 0 for row in raw)
    return raw, path, ring, sha256(contents).hexdigest(), step


def stage_result(stars, marks, queries, budget, binary, previous=None):
    graph = Wired(stars)
    decomposition = min_fill(graph)
    largest = max(len(bag.names) for bag in decomposition)
    packed = binary is not None and len(graph.all_knots) <= 256 and largest <= 15
    if packed:
        inherited = {}
        for key in queries:
            if previous is None or key not in previous or previous[key]["upper_bound"] is None:
                continue
            witnesses = [v for v in previous[key]["orientations"] if v["status"] == "exact"]
            best = min(witnesses, key=lambda row: row["cost"])
            carried = graph.witness(sum(1 << j for j in best["shore"]))
            assert carried == {k: best[k] for k in ("shore", "crossing_distinctions", "cost")}
            inherited[marks[key[0]], marks[key[1]]] = carried["cost"]
        direct = native_pairs(graph, decomposition, [(marks[a], marks[b]) for a, b in queries],
                              budget, binary, inherited)
        # A separate implementation verifies a priority entry on every small literal stage.
        if largest <= 6:
            for a, b in queries:
                if (a, b) in FOCUS:
                    grade = pair(graph, decomposition, marks[a], marks[b], budget)
                    assert direct[marks[a], marks[b]]["bond_distance"] == grade["bond_distance"]
        values = {(a, b): direct[marks[a], marks[b]] for a, b in queries}
        assert all(values[a, b]["status"] != "infinite" for a, b in queries
                   if (marks[a], marks[b]) in inherited)
    else:
        values = {(a, b): pair(graph, decomposition, marks[a], marks[b], budget) for a, b in queries}
        inherited = {}
    return {
        "ordinary_knots": graph.outside, "distinctions": len(graph.ends),
        "literal_stars_sha256": sha256(json.dumps(stars, separators=(",", ":")).encode()).hexdigest(),
        "largest_bag_including_exterior": largest, "packed_evaluation": packed,
        "verified_older_ceilings": len(inherited),
        "elimination_order": [bag.names[0] for bag in decomposition],
    }, values


def comparison(quiet, loaded):
    result = []
    for (i, j), before in quiet.items():
        after = loaded[i, j]
        if any(row["status"] == "capped" for row in (before, after)):
            grade, delta = "unresolved", None
        elif any(row["status"] == "infinite" for row in (before, after)):
            grade = "equal" if before["status"] == after["status"] else "different_infinity"
            delta = None
        else:
            delta = after["bond_distance"] - before["bond_distance"]
            grade = "longer" if delta > 0 else "shorter" if delta < 0 else "equal"
        result.append({"path_positions": [i, j], "quiet": before, "loaded": after,
                       "delta": delta, "verdict": grade})
    return result


def run(through, endpoint_only, budget, binary=None):
    old, path, ring, source_hash, step = frozen_source()
    current = {"quiet": (old, ()), "loaded": (old, ring)}
    result = {"source": "J1", "parity_source_sha256": source_hash, "action_table": ["P", "V"],
              "old_path_marks": path, "work_limit_per_orientation": budget,
              "controls": synthetic_controls(binary), "ages": {}, "missing": []}
    caps = {"junctions": 6000, "distinctions": 32000}
    previous = {}
    for age in range(through + 1):
        queries = (((0, 15), (2, 5), (3, 4)) if endpoint_only
                   else tuple(combinations(range(16), 2)) if age in (1, 2) else FOCUS)
        if len(current) == 2:
            records, values = {}, {}
            for arm, (stars, _) in current.items():
                records[arm], values[arm] = stage_result(stars, path, queries, budget, binary,
                                                         previous.get(arm))
            rows = comparison(values["quiet"], values["loaded"])
            counts = defaultdict(int)
            for row in rows:
                counts[row["verdict"]] += 1
            result["ages"][age] = {"stages": records, "counts": dict(counts), "pairs": rows}
            previous = values
            print(age, {k: r["largest_bag_including_exterior"] for k, r in records.items()},
                  dict(counts), flush=True)
        if age == through:
            break
        for arm, (stars, values) in tuple(current.items()):
            next_stage = step(stars, values, ("P", "V"), caps=caps)
            if next_stage["status"] == "extend":
                current[arm] = (next_stage["stars"], next_stage["occupied"])
            else:
                result["missing"].append({"arm": arm, "age": age + 1, "status": next_stage["status"]})
                del current[arm]
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, choices=range(7), default=2)
    parser.add_argument("--work-limit", type=int, default=500000)
    parser.add_argument("--endpoint-only", action="store_true")
    parser.add_argument("--native", action="store_true",
                        help="compile and use the packed separator engine on supported stages")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.native:
        with TemporaryDirectory(prefix="old-mark-separators-") as build:
            binary = Path(build) / "certify"
            subprocess.run(["g++", "-std=c++20", "-O3", HERE / "certify_native.cpp", "-o", binary], check=True)
            data = run(args.through, args.endpoint_only, args.work_limit, binary)
    else:
        data = run(args.through, args.endpoint_only, args.work_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
