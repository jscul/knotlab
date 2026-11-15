#!/usr/bin/env python3
"""Verify the two-use pad criterion, its minimal clause sets and actual guarded stages."""

import argparse
import json
import runpy
import subprocess
import sys
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations_with_replacement, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = (ROOT / "proofs/SIGNED-KNOT-OVERLAP-20261114-001C"
        / "SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/check.py")


def require(test, message):
    if not test:
        raise ValueError(message)


def normalize(track):
    # Bit 0 activates the negative pad half, bit 1 the positive pad half.
    literals = set()
    for p, halves in track:
        if halves == 0:
            return None  # Always a permissible drop here.
        if halves != 3:
            lit = p if halves == 2 else -p
            if -lit in literals:
                return None
            literals.add(lit)
    return tuple(literals)


def accepts(rows, values):
    return all(row is None or any(values[abs(lit)] == (lit > 0) for lit in row) for row in rows)


def orient(rows):
    """Return a satisfying assignment or every inclusion-minimal failed clause set."""
    uses = defaultdict(list)
    active = []
    for i, row in enumerate(rows):
        if row is not None:
            active.append(i)
            for lit in row:
                uses[abs(lit)].append((i, lit))
    marked, values = set(), {}
    graph = [[] for _ in rows]
    for p, items in uses.items():
        require(len(items) <= 2, "normalized pad degree exceeds two")
        if len(items) == 1 or items[0][1] == items[1][1]:
            values[p] = items[0][1] > 0
            marked.update(v for v, _ in items)
        else:
            (a, lit_a), (b, lit_b) = items
            require(a != b, "opposite literals in one surviving clause")
            graph[a].append((b, lit_b))
            graph[b].append((a, lit_a))

    visited, examined, cores = set(), set(), []
    forest = [[] for _ in rows]
    for first in active:
        if first in visited:
            continue
        vertices, stack = [], [first]
        visited.add(first)
        spare = root = None
        while stack:
            v = stack.pop()
            vertices.append(v)
            if v in marked:
                root = v
            for other, lit in graph[v]:
                if abs(lit) in examined:
                    continue
                examined.add(abs(lit))
                if other in visited:
                    spare = (other, lit)
                else:
                    visited.add(other)
                    stack.append(other)
                    forest[v].append((other, lit))
                    forest[other].append((v, -lit))
        if root is None and spare is None:
            cores.append(frozenset(vertices))
            continue
        if root is None:
            root, lit = spare
            values[abs(lit)] = lit > 0
        stack = [(root, None)]
        while stack:
            v, parent = stack.pop()
            for other, lit in forest[v]:
                if other != parent:
                    values[abs(lit)] = lit > 0
                    stack.append((other, v))
    for p in uses:
        values.setdefault(p, False)
    if cores:
        return None, set(cores)
    require(accepts(rows, values), "constructed orientation did not satisfy the literal clauses")
    return values, set()


@cache
def clause_models(w, row):
    return sum(1 << bits for bits in range(1 << w)
               if row is None or any(bool(bits & (1 << (abs(lit) - 1))) == (lit > 0) for lit in row))


def literal_cores(w, rows):
    """Truth-table all subsets of labelled clause occurrences, retaining duplicate rows."""
    models = [(1 << (1 << w)) - 1]
    masks = [clause_models(w, row) for row in rows]
    minimal = set()
    for subset in range(1, 1 << len(rows)):
        bit = subset & -subset
        models.append(models[subset ^ bit] & masks[bit.bit_length() - 1])
        indices = [j for j in range(len(rows)) if subset & (1 << j)]
        if not models[-1] and all(models[subset ^ (1 << j)] for j in indices):
            minimal.add(frozenset(indices))
    return minimal


def exhaustive(w, limit):
    clauses = [tuple((i + 1) * value for i, value in enumerate(signs) if value)
               for signs in product((-1, 0, 1), repeat=w)]
    counts = Counter()
    for k in range(limit + 1):
        for rows in combinations_with_replacement(clauses, k):
            if any(d > 2 for d in Counter(abs(lit) for row in rows for lit in row).values()):
                continue
            values, cores = orient(rows)
            require(cores == literal_cores(w, rows), "literal subset enumeration contradicts a claimed core")
            counts["formulas"] += 1
            counts["clause_subsets"] += 1 << k
            counts["unsatisfiable" if values is None else "satisfiable"] += 1
            counts["minimal_cores"] += len(cores)
    return dict(sorted(counts.items()))


def degree_controls():
    n = 2048
    tree = [(1,), *((-i, i + 1) for i in range(1, n)), (-n,)]
    require(orient(tree)[1] == {frozenset(range(n + 1))}, "larger path did not have its unique full core")
    cycle = [(1, -n - 1), *tree[1:-1], (-n, n + 1)]
    require(orient(cycle)[0] is not None and orient([*tree[:-1], (-n, n + 1)])[0] is not None,
            "an extra mixed pad or pure pad failed to cover the tree")
    # Four triples each omit one of four pads. Every pad occurs exactly three times.
    triples = [tuple(j for j in range(1, 5) if j != i) for i in range(1, 5)]
    hall = 0
    for signs in product(range(8), repeat=4):
        rows = [tuple(p if s & (1 << k) else -p for k, p in enumerate(triple))
                for s, triple in zip(signs, triples)]
        common = (1 << 16) - 1
        for row in rows:
            common &= clause_models(4, row)
        require(common, "a signed width-three degree-three Hall instance had no assignment")
        hall += 1
    return {"larger_tree_clauses": n + 1, "larger_tree_cores": 1,
            "pure_mark_repair_satisfiable": True, "extra_edge_repair_satisfiable": True,
            "Hall_sign_patterns_satisfiable": hall}


def partitions(n, prefix=(1,)):
    if len(prefix) == n:
        yield prefix
    else:
        for p in range(1, max(prefix) + 2):
            yield from partitions(n, prefix + (p,))


class StageSchedule:
    """Embed disjoint even-length tracks in the original guarded two-branch stages."""

    def __init__(self, base, tracks):
        require(all(len(t) >= 2 and not len(t) % 2 for t in tracks) and tracks, "physical track length")
        self.tracks = tracks
        self.r = sum(len(t) // 2 + 1 for t in tracks)
        source = base["source"](self.r)
        groups = base["strict_groups"](source)
        raw, _, self.guards = base["guarded_formula"](groups)
        self.pad_vars, rename, self.positions = {}, {}, []
        start = 0
        j_var = source[2][1]
        k_var = source[2 + 4 * (len(tracks[0]) // 2)][1]
        self.relays = (j_var, k_var)
        for track in tracks:
            end = start + len(track) // 2
            rename[source[2 + 4 * start][1]] = j_var
            rename[source[2 + 4 * end][1]] = k_var
            slots = [4 * start + 1]
            for s in range(start + 1, end):
                slots.extend((4 * s, 4 * s + 1))
            slots.append(4 * end)
            for e, p in zip(slots, track):
                old_pad = abs(groups[2 + e][0][-1])
                rename[old_pad] = self.pad_vars.setdefault(p, old_pad)
            self.positions.append(slots)
            start = end + 1
        self.caps = (0, 4 * (self.r - 1) + 1)
        self.formula = [tuple((1 if lit > 0 else -1) * rename.get(abs(lit), abs(lit)) for lit in clause)
                        for clause in raw]
        self.variables = {abs(v) for row in self.formula for v in row}
        self.names = []
        for slots in self.positions:
            pairs = [(-source[2 + e][0], source[2 + e][1]) for e in slots]
            route = [rename.get(pairs[0][0], pairs[0][0])]
            for u, v in pairs:
                require(rename.get(u, u) == route[-1], "the raw physical corridor is not a chain")
                route.append(rename.get(v, v))
            require((route[0], route[-1]) == self.relays, "the raw chain connects different relay names")
            self.names.append(route)
        require(all(len({abs(v) for v in row}) == 3 for row in self.formula), "non-strict raw clause")

    def assumptions(self, states, almost=False):
        edge_states = [0] * (4 * self.r)
        for cap in self.caps:
            edge_states[cap] = 3
        for slots, track in zip(self.positions, states):
            for slot, code in zip(slots, track):
                edge_states[slot] = code
        on = [True] * 24
        for e, code in enumerate(edge_states):
            for half in (0, 1):
                active = bool(code & (1 << half))
                on.extend(active or (almost and i != (e + half) % 3) for i in range(3))
        require(len(on) == len(self.guards), "wrong raw switch count")
        return [v if live else -v for v, live in zip(self.guards, on)]

    def literal_witness(self, states, switches, pad_values):
        values = dict.fromkeys(self.variables, False)
        values.update({abs(lit): lit > 0 for lit in switches})
        values.update({v: pad_values.get(p, False) for p, v in self.pad_vars.items()})
        values[1] = True  # Positive endpoint x_0. The final endpoint already has value 0.
        for path, names, halves in zip(self.names, self.tracks, states):
            drop = next((i for i, (p, h) in enumerate(zip(names, halves))
                         if h == 0 or (h != 3 and values[self.pad_vars[p]] == (h == 2))), None)
            require(drop is not None, "the oriented pad assignment permits no actual corridor drop")
            for k, v in enumerate(path):
                values[v] = k <= drop
        for start in range(0, len(self.formula), 4):
            for negative_guard, negative_witness, lit in self.formula[start + 1:start + 4]:
                if not values[-negative_guard] or values[abs(lit)] == (lit > 0):
                    values[-negative_witness] = True
                    break
            else:
                raise ValueError("no witness for a raw strict slot")
        require(all(any(values[abs(lit)] == (lit > 0) for lit in row) for row in self.formula),
                "a clause of the literal guarded formula rejected the constructed assignment")
        return values


def tracks_for(rows):
    """Realize each listed pad clause, padding a zero or odd length with unconditional positions."""
    fresh = 1 + max((abs(lit) for row in rows for lit in row), default=0)
    pads, states = [], []
    for row in rows:
        names, halves = [abs(lit) for lit in row], [2 if lit > 0 else 1 for lit in row]
        while len(names) < 2 or len(names) % 2:
            names.append(fresh)
            fresh += 1
            halves.append(3)
        pads.append(names)
        states.append(halves)
    return pads, states


def clone_example():
    # All eight forbidden rows on three variables, with one copy per occurrence.
    triples = [tuple((1 if mask & (1 << j) else -1) * (8 * j + mask + 1) for j in range(3))
               for mask in range(8)]
    binaries = [(-(8 * j + i + 1), 8 * j + ((i + 1) % 8) + 1) for j in range(3) for i in range(8)]
    rows = triples + binaries
    require(set(Counter(abs(lit) for row in rows for lit in row).values()) == {3}, "bad copy cycle degree")
    return rows


def raw_checks():
    from pysat.solvers import Solver

    base = runpy.run_path(str(BASE))
    data = Counter()
    for labels in partitions(4):
        paths = (labels[:2], labels[2:])
        schedule = StageSchedule(base, paths)
        with Solver(name="g3", bootstrap_with=schedule.formula) as solver:
            for codes in product(range(4), repeat=4):
                halves = (codes[:2], codes[2:])
                rows = tuple(normalize(zip(pads, active)) for pads, active in zip(paths, halves))
                witness, _ = orient(rows)
                for almost in (False, True):
                    raw = schedule.assumptions(halves, almost)
                    require(solver.solve(assumptions=raw) == (witness is not None), "raw corridor SAT mismatch")
                    data["complete_guard_vectors"] += 1
                for values in product((False, True), repeat=max(labels)):
                    assignment = dict(enumerate(values, 1))
                    pad_pins = [v if assignment[p] else -v for p, v in schedule.pad_vars.items()]
                    require(solver.solve(assumptions=raw + pad_pins) == accepts(rows, assignment),
                            "raw existential projection disagrees with a normalized pad clause")
                    data["pad_assignments_on_raw_vectors"] += 1
                if witness is not None:
                    pins = [v if witness.get(p, False) else -v for p, v in schedule.pad_vars.items()]
                    require(solver.solve(assumptions=raw + pins), "oriented pad witness did not lift to strict CNF")
                    schedule.literal_witness(halves, raw, witness)
                    data["lifted_pad_witnesses"] += 1
                data["track_settings"] += 1
    examples = {
        "opposed_units": ([(1,), (-1,)], False), "parallel_mixed": ([(1, 2), (-1, -2)], True),
        "marked_tree": ([(1,), (-1, 2)], True), "empty_clause": ([()], False),
        "duplicate_empty": ([(), ()], False), "same_signed_twice": ([(1,), (1,)], True),
        "adjacent_repetitions": ([(1, 1, 1), (-1,)], False),
        "tautological_track": ([(1, -1), (1,)], True),
        "separate_cores": ([(1,), (-1,), (), (2, 3), (-2, -3)], False),
        "mixed_degree_three": (clone_example(), False), "one_source_row_deleted": (clone_example()[1:], True)}
    decisions = {}
    for name, (rows, expected) in examples.items():
        paths, states = tracks_for(rows)
        schedule = StageSchedule(base, paths)
        with Solver(name="g3", bootstrap_with=schedule.formula) as solver:
            raw = schedule.assumptions(states)
            outcome = solver.solve(assumptions=raw)
            require(outcome == expected, "raw guarded named control failed")
            if name == "parallel_mixed":
                require(not solver.solve(assumptions=raw + [-schedule.relays[0]])
                        and not solver.solve(assumptions=raw + [schedule.relays[1]]), "two cap forces failed")
            decisions[name] = outcome
    return {"two_tracks_of_length_two": dict(sorted(data.items())), "named_raw_decisions": decisions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("checks.json"))
    args = parser.parse_args()
    if args.raw:
        print(json.dumps(raw_checks()))
        return
    corpus = {f"{w}_pads_up_to_{k}_clauses": exhaustive(w, k) for w, k in ((3, 4), (4, 3))}
    boundary = degree_controls()
    raw = subprocess.run([str(ROOT / ".venv/bin/python"), "-B", str(Path(__file__).resolve()), "--raw"],
                         capture_output=True, text=True, check=True)
    result = {"exhaustive_degree_two": corpus, "degree_controls": boundary, "raw_cnf": json.loads(raw.stdout)}
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        require(json.loads(args.expected.read_text()) == result, "reference counts disagree with recomputation")
        print(json.dumps({"status": "passed", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
