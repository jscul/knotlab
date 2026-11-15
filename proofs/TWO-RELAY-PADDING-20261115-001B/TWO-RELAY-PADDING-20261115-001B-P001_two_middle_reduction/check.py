"""Compile the fixed two-relay selector family and test its physical guarded clauses."""

from collections import Counter, defaultdict
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
BASE = (ROOT / "proofs/SIGNED-KNOT-OVERLAP-20261114-001C"
        / "SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/check.py")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def base_module():
    spec = importlib.util.spec_from_file_location("guarded_routes", BASE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def holds(lit, assignment):
    return bool((assignment >> (abs(lit) - 1)) & 1) == (lit > 0)


class Template:
    def __init__(self, n):
        require(n >= 3, "the fixed three-variable-clause family starts at n=3")
        self.n = n
        self.clauses = [tuple(i * s for i, s in zip(triple, signs))
                        for triple in combinations(range(1, n + 1), 3)
                        for signs in product((1, -1), repeat=3)]
        self.m = len(self.clauses)
        self.copy_source = []
        self.by_variable = [[] for _ in range(n)]
        self.tests = []
        for clause in self.clauses:
            row = []
            for lit in clause:
                self.copy_source.append(abs(lit))
                copy_id = len(self.copy_source)
                self.by_variable[abs(lit) - 1].append(copy_id)
                row.append(copy_id if lit > 0 else -copy_id)
            self.tests.append(tuple(row))
        for ring in self.by_variable:
            self.tests.extend((-u, v) for u, v in zip(ring, ring[1:] + ring[:1]))

        self.r = 3 * len(self.tests) + 2
        self.mids = list(range(self.r + 2, 3 * self.r + 2))
        self.j, self.k = self.mids[0], self.mids[-2]
        self.copy_on_edge = [None] * (4 * self.r)
        self.baseline = bytearray(24 * self.r + 24)
        self.baseline[:24] = bytes([1]) * 24
        self.corridors = []
        self.selectors = []
        self.selector_edges = set()
        self.hooks = (0, 4 * (self.r - 1) + 1)
        for e in self.hooks:
            self.set_edge(e, 3)
        for i, test in enumerate(self.tests):
            stage = 1 + 3 * i
            self.mids[2 * stage] = self.j
            self.mids[2 * (stage + 2)] = self.k
            edges = (4 * stage + 1, 4 * (stage + 1), 4 * (stage + 1) + 1, 4 * (stage + 2))
            self.corridors.append(edges)
            for e, lit in zip(edges, test):
                self.copy_on_edge[e] = abs(lit)
                self.set_edge(e, 2 if lit > 0 else 1)
            if i < self.m:
                e = edges[-1]
                self.set_edge(e, 3)
                index = 24 + 6 * e + 2
                self.baseline[index] = 0
                self.selectors.append(index)
                self.selector_edges.add(e)
            else:
                for e in edges[2:]:
                    self.set_edge(e, 3)
        self.arcs = []
        for position, middle in enumerate(self.mids):
            i = position // 2
            self.arcs.extend([(i + 1, middle), (middle, i + 2)])
        self.audit_wiring()

    def set_edge(self, e, slots):
        start = 24 + 6 * e
        self.baseline[start:start + 6] = bytes([slots & 1] * 3 + [(slots >> 1) & 1] * 3)

    def audit_wiring(self):
        require(self.r == 12 * self.m + 2 and len(self.baseline) == 288 * self.m + 72,
                "stage or public input count")
        uses = Counter(p for p in self.copy_on_edge if p is not None)
        require(len(uses) == 3 * self.m and set(uses.values()) == {3}, "copy pad placement cap")
        middle_uses = Counter(self.mids)
        require({m for m, count in middle_uses.items() if count > 1} == {self.j, self.k},
                "third shared middle")
        require(middle_uses[self.j] == middle_uses[self.k] == 4 * self.m + 1, "relay count")
        available = self.raw((1 << self.m) - 1)
        potential = {e for e in range(4 * self.r)
                     if any(self.fully_on(available, e))}
        intended = set(self.hooks) | {e for path in self.corridors for e in path}
        require(potential == intended, "unintended occurrence can carry a path")
        inside = set()
        for corridor in self.corridors:
            chain = [self.arcs[e] for e in corridor]
            require(chain[0][0] == self.j and chain[-1][1] == self.k and
                    all(left[1] == right[0] for left, right in zip(chain, chain[1:])),
                    "four arcs are not one J-to-K path")
            private = {v for _, v in chain[:-1]}
            require(len(private) == 3 and private.isdisjoint(inside | {self.j, self.k}),
                    "separate corridors share an internal source vertex")
            inside |= private

    def raw(self, chosen):
        raw = self.baseline.copy()
        for i, selector in enumerate(self.selectors):
            raw[selector] = (chosen >> i) & 1
        return raw

    @staticmethod
    def fully_on(raw, e):
        start = 24 + 6 * e
        return all(raw[start:start + 3]), all(raw[start + 3:start + 6])

    def copies(self, x):
        return [0] + [(x >> (var - 1)) & 1 for var in self.copy_source]

    def pads(self, copies):
        return [copies[c] if c is not None else int(e in self.selector_edges)
                for e, c in enumerate(self.copy_on_edge)]

    def reached(self, raw, pad_values):
        adjacency = defaultdict(list)
        for e, ((u, v), p) in enumerate(zip(self.arcs, pad_values)):
            neg, pos = self.fully_on(raw, e)
            enforced = neg if p else pos
            if enforced:
                adjacency[u].append(v)
        seen, todo = {1}, [1]
        while todo:
            for v in adjacency[todo.pop()]:
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
        return seen

    def source_models(self, chosen):
        return [x for x in range(1 << self.n)
                if all(not (chosen >> j & 1) or any(holds(lit, x) for lit in clause)
                       for j, clause in enumerate(self.clauses))]


class RawCNF:
    def __init__(self, template, old):
        self.template = template
        r = template.r
        groups = old.strict_groups(old.source(r))
        original, _, self.guards = old.guarded_formula(groups)
        rename = {r + 2 + j: v for j, v in enumerate(template.mids)}
        self.copy_vars = {}
        self.pad_vars = []
        for e, copy in enumerate(template.copy_on_edge):
            raw_id = abs(groups[e + 2][0][-1])
            if copy is not None:
                rename[raw_id] = self.copy_vars.setdefault(copy, raw_id)
            self.pad_vars.append(rename.get(raw_id, raw_id))

        def recode(clause):
            return tuple((1 if v > 0 else -1) * rename.get(abs(v), abs(v)) for v in clause)

        self.clauses = [recode(c) for c in original]
        self.padded = [recode(c) for group in groups for c in group]
        self.endpoint_pads = [abs(v) for group in groups[:2] for v in group[0][1:]]
        counts = Counter(lit for c in self.clauses for lit in c)
        require(len(self.clauses) == 32 * r + 32 and all(len(set(map(abs, c))) == 3 for c in self.clauses),
                "raw clauses are not distinct-variable strict ternaries")
        require(all(counts[v] == counts[-v] == 3 for v in self.copy_vars.values()),
                "raw pad polarity occurrence count")
        require(len(set(self.pad_vars)) == 42 * template.m + 8, "a private pad leaked between edges")

    def witness(self, raw, copies):
        template = self.template
        pads = template.pads(copies)
        reached = template.reached(raw, pads)
        require(template.r + 1 not in reached, "candidate hidden pads leave an intact path")
        env = {v: int(v in reached) for e in template.arcs for v in e}
        for var, value in zip(self.pad_vars, pads):
            require(var not in env or env[var] == value, "inconsistent raw pad copies")
            env[var] = value
        env.update((v, 0) for v in self.endpoint_pads)
        env.update(zip(self.guards, raw))

        def value(lit):
            return bool(env[abs(lit)]) == (lit > 0)

        for i, padded in enumerate(self.padded):
            chosen = next((j for j, lit in enumerate(padded) if not raw[3 * i + j] or value(lit)), None)
            require(chosen is not None, "active padded clause has no satisfying witness")
            env.update((w, int(j == chosen)) for j, w in enumerate(self.clauses[4 * i]))
        require(all(all(abs(lit) in env for lit in c) and any(value(lit) for lit in c) for c in self.clauses),
                "complete assignment disagrees with the actual raw CNF")
        return env


def small_complete(old):
    template = Template(3)
    physical = RawCNF(template, old)
    duplicate = Template(3)
    require((template.arcs, template.copy_on_edge, template.baseline) ==
            (duplicate.arcs, duplicate.copy_on_edge, duplicate.baseline), "schedule depends on selector input")
    decisions = projected = witnesses = 0
    single_switch_changes = []
    for y in range(256):
        raw = template.raw(y)
        different = {i for i, (a, b) in enumerate(zip(raw, template.baseline)) if a != b}
        require(different == {v for j, v in enumerate(template.selectors) if y >> j & 1},
                "a selector changed an unrelated switch")
        if y.bit_count() == 1:
            single_switch_changes.append(len(different))
        expected = template.source_models(y)
        observed = []
        for x in range(8):
            pads = template.pads(template.copies(x))
            if template.r + 1 not in template.reached(raw, pads):
                observed.append(x)
            projected += 1
        require(expected == observed, "source assignment changed after fixed wiring")
        if observed:
            physical.witness(raw, template.copies(observed[0]))
            witnesses += 1
        decisions += bool(observed)
    require(decisions == 255 and single_switch_changes == [1] * 8, "three-variable selectors")
    return decisions, projected, witnesses


def counterexamples(old):
    template = Template(3)
    cnf = RawCNF(template, old)
    all_on = template.raw(255)
    one_missing = template.raw(254)
    require(template.source_models(254) == [0], "missing positive clause no longer isolates 000")
    copies = template.copies(0)
    pads = template.pads(copies)
    selector_pad_edge = template.corridors[0][-1]
    require(template.r + 1 not in template.reached(one_missing, pads), "missing clause failed to switch off")
    pads[selector_pad_edge] = 0
    require(template.r + 1 in template.reached(one_missing, pads), "private-selector-pad control")

    first = template.by_variable[0][0]
    following = template.by_variable[0][1]
    ring_number = template.tests.index((-first, following))
    e = template.corridors[ring_number][0]
    damaged = bytearray(all_on)
    damaged[24 + 6 * e] = 0
    copies[first] = 1
    require(template.r + 1 in template.reached(all_on, template.pads(copies)), "intact ring allowed a split")
    cnf.witness(damaged, copies)
    return 2


def raw_oracle():
    from pysat.solvers import Solver

    old = base_module()
    rng = random.Random(111)
    count = positive = negative = 0
    for n in (3, 4, 5):
        template = Template(n)
        cnf = RawCNF(template, old)
        # The first eight lexicographic slots always range over one original triple.
        masks = list(range(256)) if n == 3 else [0, 1, 127, 255, (1 << template.m) - 1]
        if n > 3:
            masks.extend(rng.getrandbits(template.m) for _ in range(20))
        with Solver(name="g3", bootstrap_with=cnf.clauses) as solver:
            def assumptions(raw):
                return [v if bit else -v for v, bit in zip(cnf.guards, raw)]

            for chosen in masks:
                raw = template.raw(chosen)
                expected = template.source_models(chosen)
                answer = solver.solve(assumptions=assumptions(raw))
                require(answer == bool(expected), "raw SAT disagrees with strict source")
                if answer:
                    actual = set(solver.get_model())
                    values = []
                    for ring in template.by_variable:
                        bits_in_ring = {cnf.copy_vars[c] in actual for c in ring}
                        require(len(bits_in_ring) == 1, "actual strict model violates occurrence equality")
                        values.append(bits_in_ring.pop())
                    recovered = sum(int(b) << j for j, b in enumerate(values))
                    require(recovered in expected, "actual model fails source formula")
                    if n > 3:
                        cnf.witness(raw, template.copies(recovered))
                    positive += 1
                else:
                    negative += 1
                count += 1
            if n == 3:
                first, following = template.by_variable[0][:2]
                ring = template.tests.index((-first, following))
                damaged = template.raw(255)
                damaged[24 + 6 * template.corridors[ring][0]] = 0
                require(solver.solve(assumptions=assumptions(damaged)), "damaged equality remained UNSAT")
                e = template.corridors[0][-1]
                inactive = assumptions(template.raw(254))
                require(solver.solve(assumptions=inactive + [cnf.pad_vars[e]]) and
                        not solver.solve(assumptions=inactive + [-cnf.pad_vars[e]]),
                        "single-switch selector lost dependence on its private pad")
                count += 3
    return {"raw_sat_replays": count, "raw_valid_menu_sat": positive, "raw_valid_menu_unsat": negative}


def installed_oracle():
    if importlib.util.find_spec("pysat") is not None:
        return raw_oracle()
    python = ROOT / ".venv/bin/python"
    probe = "import importlib.util,sys; sys.exit(importlib.util.find_spec('pysat') is None)"
    if python.is_file() and subprocess.run([str(python), "-B", "-c", probe]).returncode == 0:
        return json.loads(subprocess.check_output([str(python), "-B", __file__, "--raw"], text=True))
    return {"raw_sat_replays": 0, "raw_valid_menu_sat": 0, "raw_valid_menu_unsat": 0}


def main():
    old = base_module()
    decisions, projections, assignments = small_complete(old)
    controls = counterexamples(old)
    larger = Template(5)
    return {
        "status": "passed",
        "three_variable_selector_inputs": 256,
        "three_variable_sat_inputs": decisions,
        "source_assignments_checked_n3": projections,
        "full_raw_witnesses_constructed_n3": assignments,
        "data_slots_n5": larger.m,
        "mandatory_binary_tests_n5": len(larger.tests) - larger.m,
        "stages_n5": larger.r,
        "varying_raw_bits_per_data_slot": 1,
        "maximum_binary_padding_placements_per_name": max(Counter(c for c in larger.copy_on_edge
                                                                  if c is not None).values()),
        "structural_controls": controls,
        **installed_oracle(),
    }


if __name__ == "__main__":
    report = raw_oracle() if sys.argv[1:] == ["--raw"] else main()
    print(json.dumps(report, indent=2, sort_keys=True))
