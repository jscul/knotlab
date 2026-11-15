"""Check the forward summary and the public two-stage implementation of each tested implication."""

import importlib.util
import json
from math import comb
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
JOINED_CHECK = (ROOT / "proofs/UNSIGNED-ROUTE-JOINS-20261115-001B"
                / "UNSIGNED-ROUTE-JOINS-20261115-001B-P001_joined_reachability/check.py")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class Schedule:
    def __init__(self, k, reverse_seam=False):
        self.k = k
        self.s, self.t = k, k + 1
        self.stages = [self.s]
        before = [(i, j) for i in range(k) for j in range(k) if i != j]
        taps = [(self.s, i) for i in range(k)] + [(i, self.t) for i in range(k)]
        self.prefix = self.allocate(before + taps + [(self.s, self.t)])
        self.stages.append(self.s if reverse_seam else self.t)
        self.cut = len(self.stages)
        self.stages.append(self.t if reverse_seam else self.s)
        self.suffix = self.allocate(taps)
        self.stages.append(self.t)
        self.r = len(self.stages)
        require(self.r == 2 * k**2 + 6 * k + 6, "wrong fixed schedule length")
        self.links = (1 << 0) | (1 << (4 * (self.r - 1) + 1))
        self.early = (1 << (4 * self.cut)) - 1
        self.arcs = []
        for i, label in enumerate(self.stages):
            middle = self.name(label)
            self.arcs.extend([(i, middle), (middle, i + 1)] * 2)
        self.interface = []
        for i in range(self.r + 1):
            open_names = set(self.stages[:i]) & set(self.stages[i:])
            self.interface.append({0, i, self.r} | {self.name(v) for v in open_names})
        require(max(len(set(self.stages[:i]) & set(self.stages[i:])) for i in range(self.r + 1))
                == k + 2, "wrong open-middle width")

    def allocate(self, arcs):
        allocated = {}
        for u, v in arcs:
            first = len(self.stages)
            self.stages.extend([u, v])
            allocated[u, v] = (1 << (4 * first + 1)) | (1 << (4 * (first + 1)))
        return allocated

    def name(self, label):
        return self.r + 1 + label

    def pin(self, assignment):
        result = 0
        for i in range(self.k):
            arc = (self.s, i) if assignment >> i & 1 else (i, self.t)
            result |= self.suffix[arc]
        return result

    def graph(self, mask):
        adjacency = {}
        for edge in bits(mask):
            u, v = self.arcs[edge]
            adjacency.setdefault(u, []).append(v)
        return adjacency

    def feasible(self, mask):
        return self.r not in reachable(self.graph(mask), [0])

    def side_profile(self, mask, prefix):
        side = mask & self.early if prefix else mask & ~self.early
        adjacency = self.graph(side)
        profile = 0
        for x in range(1 << self.k):
            pos, neg = {self.name(self.s)}, {self.name(self.t)}
            if prefix:
                pos.add(0)
            else:
                neg.add(self.r)
            for i in range(self.k):
                (pos if x >> i & 1 else neg).add(self.name(i))
            if reachable(adjacency, pos).isdisjoint(neg):
                profile |= 1 << x
        return profile


def reachable(adjacency, sources):
    seen = set(sources)
    todo = list(sources)
    while todo:
        for v in adjacency.get(todo.pop(), ()):
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return seen


def frontier(arcs, interfaces, mask):
    stages = len(arcs) // 4
    relation = {(v, v) for v in interfaces[0]}
    for i in range(stages):
        current = arcs[4 * i:4 * i + 4]
        expanded = interfaces[i] | {v for arc in current for v in arc}
        relation.update((v, v) for v in expanded)
        for j in range(4 * i, 4 * i + 4):
            if mask >> j & 1:
                relation.add(arcs[j])
        for mid in expanded:
            starts = [u for u in expanded if (u, mid) in relation]
            ends = [v for v in expanded if (mid, v) in relation]
            relation.update((u, v) for u in starts for v in ends)
        keep = interfaces[i + 1]
        relation = {(u, v) for u, v in relation if u in keep and v in keep}
    return (0, stages) not in relation


def preorders(k):
    arcs = [(u, v) for u in range(k) for v in range(k) if u != v]
    count = 0
    for mask in range(1 << len(arcs)):
        relation = {(v, v) for v in range(k)} | {arcs[j] for j in bits(mask)}
        if all((u, z) in relation for u, v in relation for y, z in relation if v == y):
            count += 1
    return count


def closed(profile, k):
    if not 0 <= profile < (1 << (1 << k)):
        return False
    points = list(bits(profile))
    return all(profile >> (x & y) & 1 and profile >> (x | y) & 1 for x in points for y in points)


def abstract_prefix(arc_list, mask, k):
    selected = [arc_list[j] for j in bits(mask)]
    result = 0
    for x in range(1 << k):
        # Index k is true bus s, index k+1 is false bus t.
        valued = x | (1 << k)
        if all(not (valued >> u & 1) or (valued >> v & 1) for u, v in selected):
            result |= 1 << x
    return result


def check_profile_census():
    order_counts = [preorders(m) for m in range(5)]
    require(order_counts == [1, 1, 4, 29, 355], "labelled preorder census")
    counts = [1 + sum(comb(k, m) * 2**(k - m) * order_counts[m] for m in range(k + 1))
              for k in range(5)]
    require(counts == [2, 4, 13, 74, 732], "designed-cut profile formula")
    physical_probes = 0
    for k in range(4):
        sched = Schedule(k)
        arc_list = list(sched.prefix)
        profiles = set()
        physical_masks = [0] * (1 << len(arc_list))
        for m in range(len(physical_masks)):
            if m:
                bit = m & -m
                physical_masks[m] = physical_masks[m ^ bit] | sched.prefix[arc_list[bit.bit_length() - 1]]
            prefix = sched.links | physical_masks[m]
            expected = abstract_prefix(arc_list, m, k)
            observed = sum(int(sched.feasible(prefix | sched.pin(x))) << x for x in range(1 << k))
            require(expected == observed, "physical pairs changed the selected implication family")
            profiles.add(observed)
            physical_probes += 1 << k
        every_closed = {p for p in range(1 << (1 << k)) if closed(p, k)}
        require(profiles == every_closed and len(profiles) == counts[k], "incomplete cut profile family")
    all_four = sum(closed(p, 4) for p in range(1 << 16))
    require(all_four == counts[4], "independent four-variable subfamily census")
    return counts, physical_probes


def check_arbitrary_activations():
    rng = random.Random(802)
    checks = 0
    for k in (0, 1, 2, 4, 6):
        sched = Schedule(k)
        masks = [sched.links, (1 << (4 * sched.r)) - 1]
        masks += [sched.links | rng.getrandbits(4 * sched.r) for _ in range(28)]
        for m in masks:
            before = sched.side_profile(m, True)
            after = sched.side_profile(m, False)
            actual = sched.feasible(m)
            require(closed(before, k) and closed(after, k), "arbitrary masks lost closure")
            require(bool(before & after) == actual, "an unrestricted seam switch leaked")
            require(frontier(sched.arcs, sched.interface, m) == actual, "forgotten directed path")
            checks += 1

    bad = Schedule(0, reverse_seam=True)
    into_cut = 1 << (4 * (bad.cut - 1) + 1)
    out_of_cut = 1 << (4 * bad.cut)
    leaking = bad.links | into_cut | out_of_cut
    require(bad.side_profile(leaking, True) & bad.side_profile(leaking, False),
            "bad seam did not have individually feasible fragments")
    require(not bad.feasible(leaking) and bad.feasible(leaking ^ into_cut), "bad seam failed to leak")

    zero = Schedule(0)
    short = zero.links | zero.prefix[zero.s, zero.t]
    require(not zero.feasible(short) and zero.feasible(short ^ 1), "unfixed true bus control")
    return checks


def check_general_frontiers():
    rng = random.Random(1006)
    checked = 0
    for r in (1, 2, 3, 5, 8):
        labels = ([0, 1, 0, 2, 2, 1] if r == 3
                  else [rng.randrange(r + 1) for _ in range(2 * r)])
        arcs = []
        for j, middle in enumerate(labels):
            i, v = j // 2, r + 1 + middle
            arcs.extend([(i, v), (v, i + 1)])
        interfaces = []
        for i in range(r + 1):
            shared = set(labels[:2 * i]) & set(labels[2 * i:])
            interfaces.append({0, i, r} | {r + 1 + j for j in shared})
        masks = list(range(1 << (4 * r))) if r <= 2 else [rng.getrandbits(4 * r) for _ in range(64)]
        if r == 3:
            masks.append(sum(1 << j for j in (0, 3, 5, 6, 9, 10)))
        for mask in masks:
            adjacency = {}
            for j in bits(mask):
                u, v = arcs[j]
                adjacency.setdefault(u, []).append(v)
            expected = r not in reachable(adjacency, [0])
            require(frontier(arcs, interfaces, mask) == expected, "general open-name frontier")
            checked += 1
    return checked


def check_index(k):
    sched = Schedule(k)
    left = list(range(k // 2))
    right = list(range(k // 2, k))
    arcs = [(u, v) for u in left for v in right]
    outputs = set()
    for m in range(1 << len(arcs)):
        prefix = sched.links
        for j in bits(m):
            prefix |= sched.prefix[arcs[j]]
        reached = reachable(sched.graph(prefix & sched.early), [0])
        require(reached.isdisjoint(sched.name(i) for i in range(k)), "matrix prefix forced an internal name")
        observed = 0
        for j, (u, v) in enumerate(arcs):
            suffix = sched.suffix[sched.s, u] | sched.suffix[v, sched.t]
            if not sched.feasible(prefix | suffix):
                observed |= 1 << j
        require(observed == m, "INDEX query failed on the fixed schedule")
        outputs.add(observed)
    require(len(outputs) == 1 << (k**2 // 4), "matrix prefixes merged")
    return len(outputs)


def raw_replay():
    from pysat.solvers import Solver

    spec = importlib.util.spec_from_file_location("joined_strict_checks", JOINED_CHECK)
    joined = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(joined)
    old = joined.predecessor()
    count = 0
    counted_cuts = 0
    for k, reversed_seam in ((0, False), (1, False), (2, False), (4, False), (6, False), (0, True)):
        sched = Schedule(k, reverse_seam=reversed_seam)
        labels = tuple(x for x in sched.stages for _ in range(2))
        formula, groups, guards = joined.strict_instance(old, labels)
        require(len(groups) == 4 * sched.r + 2 and len(guards) == 24 * sched.r + 24,
                "strict template changed with switch input")
        with Solver(name="g3", bootstrap_with=formula) as solver:
            def compare(m, incomplete=None):
                nonlocal count
                active_groups = [True, True] + [bool(m >> e & 1) for e in range(4 * sched.r)]
                raw = 0
                for selected, group in zip(active_groups, groups):
                    if selected:
                        raw |= group
                if incomplete is not None:
                    raw ^= 1 << incomplete
                assumption = [v if raw >> i & 1 else -v for i, v in enumerate(guards)]
                result = solver.solve(assumptions=assumption)
                actual = sum(int(raw & g == g) << j for j, g in enumerate(groups[2:]))
                expected = (raw & groups[0] != groups[0] or raw & groups[1] != groups[1]
                            or sched.feasible(actual))
                require(result == expected, "actual switch CNF disagrees with the ordered reader")
                count += 1
                return result

            if reversed_seam:
                a = 1 << (4 * (sched.cut - 1) + 1)
                b = 1 << (4 * sched.cut)
                require(not compare(sched.links | a | b) and compare(sched.links | b),
                        "raw wrong-seam control")
                continue
            if k == 0:
                short = sched.links | sched.prefix[sched.s, sched.t]
                require(not compare(short) and compare(short ^ 1), "raw missing bus link")
            compare(sched.links)
            compare((1 << (4 * sched.r)) - 1)
            if k >= 2:
                u, v = 0, k - 1
                halves = sched.prefix[u, v]
                q = sched.suffix[sched.s, u] | sched.suffix[v, sched.t]
                only = sched.links | halves | q
                require(not compare(only) and compare(sched.links | q), "strict matrix entry")
                for e in bits(halves):
                    for b in bits(groups[e + 2]):
                        require(compare(only, b), "incomplete strict half still transmitted the bit")
            if k <= 2:
                arcs = list(sched.prefix)
                observed = set()
                for m in range(1 << len(arcs)):
                    prefix = sched.links
                    for j in bits(m):
                        prefix |= sched.prefix[arcs[j]]
                    observed.add(sum(int(compare(prefix | sched.pin(x))) << x for x in range(1 << k)))
                require(len(observed) == (2, 4, 13)[k], "raw cut profile count")
                counted_cuts += 1
    return {"strict_guard_vectors": count, "strict_profile_censuses": counted_cuts}


def installed_replay():
    if importlib.util.find_spec("pysat") is not None:
        return raw_replay()
    python = ROOT / ".venv/bin/python"
    test = "import importlib.util,sys; sys.exit(importlib.util.find_spec('pysat') is None)"
    if python.is_file() and subprocess.run([str(python), "-B", "-c", test]).returncode == 0:
        return json.loads(subprocess.check_output([str(python), "-B", __file__, "--raw"], text=True))
    return {"strict_guard_vectors": 0, "strict_profile_censuses": 0}


def main():
    counts, probes = check_profile_census()
    masks = check_arbitrary_activations()
    general = check_general_frontiers()
    matrices = check_index(6)
    return {
        "status": "passed",
        **{f"cut_profiles_k{k}": count for k, count in enumerate(counts)},
        "complete_pin_probes_on_physical_schedule": probes,
        "arbitrary_schedule_masks_checked": masks,
        "general_joined_schedule_masks_checked": general,
        "distinguished_bipartite_matrices_k6": matrices,
        "ordered_index_queries_k6": 9 * matrices,
        "fixed_schedule_stages_k6": Schedule(6).r,
        "reversed_boundary_counterexample": True,
        **installed_replay(),
    }


if __name__ == "__main__":
    data = raw_replay() if sys.argv[1:] == ["--raw"] else main()
    print(json.dumps(data, indent=2, sort_keys=True))
