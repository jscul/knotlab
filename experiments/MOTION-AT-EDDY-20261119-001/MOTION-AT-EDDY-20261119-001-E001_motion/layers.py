"""Anonymous parent-link test, two-landmark readings, and exact source-map comparison."""

from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
import sys

from motion_stage import HERE, INPUTS, ROOT, anonymous_owners, load_case_record


OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "layers.json"


def distances(neighbors, start):
    queue = deque(start)
    found = {v: 0 for v in queue}
    while queue:
        v = queue.popleft()
        for w in neighbors[v]:
            if w not in found:
                found[w] = found[v] + 1
                queue.append(w)
    return found


class Stage:
    def __init__(self, stars):
        self.owners = anonymous_owners(stars)
        self.nbr = [set() for _ in stars]
        self.shared = {}
        live = set()
        for bit, row in self.owners.items():
            if len(row) == 1:
                live.add(row[0])
            else:
                u, v = row
                self.nbr[u].add(v)
                self.nbr[v].add(u)
                assert (u, v) not in self.shared
                self.shared[u, v] = self.shared[v, u] = bit
        depth = distances(self.nbr, live)
        self.last = max(depth.values())
        self.age = [self.last - depth[v] for v in range(len(stars))]
        self.parents = [{u for u in row if self.age[u] + 1 == self.age[v]} for v, row in enumerate(self.nbr)]
        self.children = [{u for u in row if self.age[u] == self.age[v] + 1} for v, row in enumerate(self.nbr)]

    def choices(self, p, c):
        siblings = self.children[p] - {c}
        return {d for d in self.children[c] if self.parents[d].isdisjoint(siblings)}

    def square(self, p, q, r, s):
        bits = {self.shared[p, q], self.shared[q, r], self.shared[r, s], self.shared[s, p]}
        assert len(bits) == 4 and all(len(self.owners[bit]) == 2 for bit in bits)
        counts = Counter(v for bit in bits for v in self.owners[bit])
        assert set(counts.values()) == {2}
        return bits


class Map:
    def __init__(self, case):
        self.nbr = [set() for _ in case["sizes"]]
        for u, v in case["meetings"]:
            self.nbr[u].add(v)
            self.nbr[v].add(u)
        self.opens = [size - len(row) for size, row in zip(case["sizes"], self.nbr)]
        self.demand = [sum(len(self.nbr[w]) - 1 for w in row) for row in self.nbr]
        self.left = [x - y for x, y in zip(self.opens, self.demand)]
        assert min(self.left) >= 0 and min(self.opens) >= 2
        common = {(u, v): self.nbr[u] & self.nbr[v] for u, v in combinations(range(len(self.nbr)), 2)}
        assert all(len(ws) <= 1 for ws in common.values())
        for u, v, w in combinations(range(len(self.nbr)), 3):
            if common[u, v] and common[u, w] and common[v, w]:
                assert common[u, v] == common[u, w] == common[v, w]

    def onward(self, port):
        kind, p, incoming = port
        if kind != "point":
            return [("ray", p, -1)] if self.opens[p] == 2 else []
        return ([("point", q, w) for w in sorted(self.nbr[p] - {incoming})
                 for q in sorted(self.nbr[w] - {p})]
                + [("pendant", p, -1)] * self.left[p])

    def fate(self, port):
        seen = {}
        t = 1
        while port not in seen:
            seen[port] = t
            offered = self.onward(port)
            if len(offered) != 1:
                return {"outcome": "tie" if offered else "stop", "decision_age": t,
                        "map_alternatives": offered}
            port, = offered
            t += 1
        return {"outcome": "ray" if port[0] == "ray" else "periodic_map",
                "first_repeated_type_age": t, "period": t - seen[port]}


def infer_ports(stage, model, born):
    ports = {}
    roots = {}
    source_quads = set()
    pulse_ports = set()
    for t in range(1, stage.last + 1):
        for c in born[t]:
            par = stage.parents[c]
            for p in par:
                if t == 1 and len(par) == 2:
                    q, = par - {p}
                    w, = model.nbr[p] & model.nbr[q]
                    port = ("point", q, w)
                    source_quads.add(tuple(sorted(stage.square(p, w, q, c))))
                elif t == 1:
                    assert len(par) == 1
                    port = ("pendant", p, -1)
                elif len(par) == 1:
                    grandparent, = stage.parents[p]
                    old_kind, owner, _ = ports[grandparent, p]
                    assert old_kind in {"pendant", "ray"} and model.opens[owner] == 2
                    port = ("ray", owner, -1)
                else:
                    # Opposite edges of a two-deletion square add the same point
                    # through the same block. Compare all possible older squares.
                    values = {ports[g, q] for q in par - {p} for g in stage.parents[p] & stage.parents[q]}
                    assert len(values) == 1, (t, p, c, values)
                    port, = values
                ports[p, c] = port
                if t == 1:
                    roots[p, c] = model.fate(port)
    for quad in source_quads:
        pulse_ports.update(quad)
    assert all(max(stage.age[v] for v in stage.owners[bit]) <= 1 for bit in pulse_ports)
    return ports, roots, source_quads


def trace(stage, p, c, endpoint_distances):
    rows, square_rows = [], []
    last_square = None
    while True:
        t = stage.age[c]
        rows.append([t, p, c, *[ds[c] for ds in endpoint_distances]])
        if t == stage.last:
            return rows, square_rows, None
        choices = stage.choices(p, c)
        if len(choices) != 1:
            return rows, square_rows, sorted(choices)
        d, = choices
        others = stage.children[p] - {c}
        if len(others) == 1:
            s, = others
            shared_children = stage.children[c] & stage.children[s]
            if len(shared_children) == 1:
                m, = shared_children
                quad = stage.square(p, c, m, s)
                if last_square is not None:
                    assert len(quad & last_square) == 1 and len(quad ^ last_square) == 6
                last_square = quad
                square_rows.append([t, sorted(quad), *[min(ds[x] for x in (p, c, m, s))
                                                     for ds in endpoint_distances]])
            else:
                last_square = None
        else:
            last_square = None
        p, c = c, d


def analyze(case):
    name = case["id"]
    record = load_case_record(name)
    assert record["qualification"]["canonical"] and record["qualification"]["DOUBLE_IDENT"]["in_class"]
    snapshots = sorted(record["stages"].values(), key=lambda s: s["age"])
    stage = Stage(snapshots[-1]["stars"])
    assert stage.last + 1 == len(snapshots)
    born = [s["born"] for s in snapshots]
    ages = {}
    for t, s in enumerate(snapshots):
        if t:
            old = snapshots[t - 1]
            assert s["stars"][:len(old["stars"])] == old["stars"] and s["old_states_preserved"]
        for v in born[t]:
            ages[v] = t
            assert stage.age[v] == t and stage.parents[v] == set(s["parent_sets"].get(str(v), []))
    assert len(ages) == len(stage.age)
    model = Map(case)
    ports, roots, quads = infer_ports(stage, model, born)
    rng = Random(710004)
    node_rename = rng.sample(range(len(stage.age)), len(stage.age))
    all_bits = sorted(stage.owners)
    bit_rename = dict(zip(all_bits, rng.sample(all_bits, len(all_bits))))
    renamed_stars = [None] * len(stage.age)
    for v, row in enumerate(snapshots[-1]["stars"]):
        renamed_stars[node_rename[v]] = [bit_rename[b] for b in reversed(row)]
    renamed = Stage(renamed_stars)
    for v in range(len(stage.age)):
        assert renamed.age[node_rename[v]] == stage.age[v]
        assert renamed.parents[node_rename[v]] == {node_rename[u] for u in stage.parents[v]}
    ties = []
    scores = Counter()
    by_age = {}
    for t in range(1, stage.last):
        histogram = Counter()
        for c in born[t]:
            for p in sorted(stage.parents[c]):
                ds = stage.choices(p, c)
                predicted = model.onward(ports[p, c])
                assert Counter(ports[c, d] for d in ds) == Counter(predicted), (name, p, c, ds, predicted)
                assert {node_rename[d] for d in ds} == renamed.choices(node_rename[p], node_rename[c])
                histogram[len(ds)] += 1
                if len(ds) > 1:
                    ties.append([p, c, sorted(ds)])
        scores.update(histogram)
        by_age[t] = dict(sorted(histogram.items()))
    launches = []
    for (p, c), outcome in sorted(roots.items()):
        a, b = p, c
        while stage.age[b] < stage.last:
            ds = stage.choices(a, b)
            if len(ds) != 1:
                assert outcome["decision_age"] == stage.age[b]
                break
            a, b = b, next(iter(ds))
        launches.append({"p": p, "c": c, "port": ports[p, c], **outcome})
    states = {ports[key] for key in roots}
    pending = list(states)
    map_options = {}
    while pending:
        port = pending.pop()
        ds = model.onward(port)
        map_options[port] = ds
        for other in ds:
            if other not in states:
                states.add(other)
                pending.append(other)
    cases = {"age_max": stage.last, "all_ages_match_anonymous_depth": True,
             "junction_and_distinction_renaming_checked": True,
             "canonical_and_funded": True, "candidate_links_by_number_of_choices": dict(sorted(scores.items())),
             "per_age": by_age, "literal_ties_p_c_all_children": ties,
             "reachable_map_ports_and_all_exits": [[q, map_options[q]] for q in sorted(states)],
             "all_source_launches": launches, "fate_counts": dict(sorted(Counter(x["outcome"] for x in launches).items())),
             "A0_zero_extended_source_four_changes": len(quads)}
    if name == "J1":
        prior = ROOT / "artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/adjacent_changes.json"
        pulse = json.loads(prior.read_text())["four_distinction_states"]
        for bits in pulse:
            assert tuple(sorted(bits)) in quads
            for snapshot in snapshots[1:]:
                assert all(len(set(row).intersection(bits)) % 2 == 0 for row in snapshot["stars"])
        cases["A0_retained_EddyWorld_pulses"] = pulse
    path = case["roles"]["background"]
    if path:
        endpoints = path[0], path[-1]
        probes = [distances(stage.nbr, [v]) for v in endpoints]
        assert probes[0][endpoints[1]] == len(path) - 1
        data = {}
        for i, p in enumerate(endpoints):
            for mode, size in (("inward", 2), ("outward", 1)):
                c, = [v for v in stage.children[p] if len(stage.parents[v]) == size]
                ordered_ds = [probes[i], probes[1 - i]]
                rows, squares, stop = trace(stage, p, c, ordered_ds)
                D = len(path) - 1
                for t, _, _, near, far in rows:
                    assert near == t
                    assert far == (max(t, D - t) if mode == "inward" else D + t)
                if mode == "inward" and name in {"B", "B81"}:
                    for t, bits, near, far in squares:
                        assert [near, far] == [t - 1, max(t - 1, D - t)]
                        holders = {v for bit in bits for v in stage.owners[bit]}
                        arities = sorted(len(snapshots[-1]["stars"][v]) for v in holders)
                        assert arities == ([3, 3, 4, 4] if t == 1 else [4, 4, 4, 4])
                data[f"{p}_{mode}"] = {"trace_age_previous_current_near_far": rows,
                                       "square_at_age_t_plus_one": squares,
                                       "literal_terminal_alternatives": stop, "all_size": roots[p, c]}
        cases["endpoint_launches"] = data
    return cases


def main():
    inputs = json.loads(INPUTS.read_text())
    assert sha256((ROOT / inputs["source_archive"]).read_bytes()).hexdigest() == inputs["archive_sha256"]
    report = {case["id"]: analyze(case) for case in inputs["cases"]}
    old_names = [case["id"] for case in inputs["cases"] if case["id"] not in inputs["additional_cases"]]
    assert len(old_names) == 10 and sum(report[k]["age_max"] for k in old_names) == 150
    # Reuse the terminal predecessor's exact positive-series bounds on the new spacing.
    sys.path.insert(0, str(ROOT / "experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world"))
    from fate_rate_bounds import certify
    double = next(c for c in inputs["cases"] if c["id"] == "T81")
    rate_certificate = certify(double)
    OUTPUT.write_text(json.dumps({"old_adjacent_stage_comparisons": 150,
                                  "T81_total_growth_certificate": rate_certificate, "cases": report},
                                 separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
