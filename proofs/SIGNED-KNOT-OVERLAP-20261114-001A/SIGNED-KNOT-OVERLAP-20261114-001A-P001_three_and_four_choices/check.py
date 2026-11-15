#!/usr/bin/env python3
"""Check projections of the unpinned prefix by full truth tables, local elimination and knotlab."""

import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Prefix:
    def __init__(self, slots):
        self.slots = slots
        self.public = 1 + max(x for slot in slots for x in slot)
        self.names = ["x" + str(i) for i in range(self.public)]
        for s, slot in enumerate(slots):
            require(len(slot) == len(set(slot)) == 3, "a slot needs three distinct public variables")
            self.names.extend(f"{role}{s}_{i}" for role in ("w", "e") for i in range(3))

    def w(self, s, i):
        return self.public + 6 * s + i

    def e(self, s, i):
        return self.w(s, i) + 3

    def clauses(self, signs):
        # Each literal is (zero-based variable, value that satisfies it).
        result = []
        for s, slot in enumerate(self.slots):
            result.append(tuple((self.w(s, i), 1) for i in range(3)))
            for i, x in enumerate(slot):
                literal_true = 1 - ((signs[s] >> i) & 1)
                result.append(((self.e(s, i), 0), (self.w(s, i), 0), (x, literal_true)))
        return result


def displayed(clauses):
    out = {}
    for clause in clauses:
        ordered = sorted(clause)
        scope = tuple(i for i, _ in ordered)
        omitted = sum((1 - value) << j for j, (_, value) in enumerate(ordered))
        out[scope] = 255 ^ (1 << omitted)
    return out


def boolean_columns(n):
    full = (1 << (1 << n)) - 1
    cols = []
    for i in range(n):
        run = 1 << i
        ones = (full // ((1 << run) + 1)) << run
        cols.append((full ^ ones, ones))
    return full, cols


def cnf_states(full, cols, clauses):
    states = full
    for clause in clauses:
        clause_states = 0
        for var, value in clause:
            clause_states |= cols[var][value]
        states &= clause_states
    return states


def pin_cells(full, cols, scope):
    cells = [full]
    for var in scope:
        cells = [cell & cols[var][value] for value in (0, 1) for cell in cells]
    return cells


def project(states, cells):
    return sum(1 << i for i, cell in enumerate(cells) if states & cell)


def three_scope_census(prefix, scenarios, project_many):
    totals = Counter()
    n = len(prefix.names)
    for size in range(4):
        all_rows = (1 << (1 << size)) - 1
        for scope in combinations(range(n), size):
            for (_, clause_scopes), actual in zip(scenarios, project_many(scope), strict=True):
                expected = clause_scopes.get(scope, all_rows)
                require(actual == expected, f"projection differs at {scope}")
                totals[str(size) + ("_free" if actual == all_rows else "_constrained")] += 1
    return dict(sorted(totals.items()))


def quartets(prefix, signs, read):
    counts = Counter()
    for s, u in combinations(range(len(prefix.slots)), 2):
        for i, j in product(range(3), repeat=2):
            same_x = prefix.slots[s][i] == prefix.slots[u][j]
            opposed = ((signs[s] >> i) ^ (signs[u] >> j)) & 1
            kind = "different_public" if not same_x else ("opposed" if opposed else "aligned")
            scope = (prefix.e(s, i), prefix.w(s, i), prefix.e(u, j), prefix.w(u, j))
            actual = read(scope)
            require(actual == (32767 if kind == "opposed" else 65535), f"bad quartet {scope}, {kind}")
            counts[kind] += 1
    return dict(sorted(counts.items()))


def full_table_fixture(slots):
    prefix = Prefix(slots)
    full, cols = boolean_columns(len(prefix.names))
    scenarios, states = [], []
    for signs in product(range(8), repeat=len(slots)):
        clauses = prefix.clauses(signs)
        scenarios.append((signs, displayed(clauses)))
        states.append(cnf_states(full, cols, clauses))

    audit_signs = tuple(range(len(slots)))
    audit_idx = next(i for i, (signs, _) in enumerate(scenarios) if signs == audit_signs)
    audit = Eliminator(prefix, audit_signs)

    def read_all(scope):
        cells = pin_cells(full, cols, scope)
        answers = [project(state_set, cells) for state_set in states]
        require(answers[audit_idx] == audit.relation(scope), "independent slot elimination disagrees")
        return answers

    census = three_scope_census(prefix, scenarios, read_all)
    four = Counter()
    for (signs, _), state_set in zip(scenarios, states):
        four.update(quartets(prefix, signs, lambda scope: project(state_set, pin_cells(full, cols, scope))))
    return {"bits": len(prefix.names), "signings": len(scenarios), "small_projections": census,
            "private_quartets": dict(sorted(four.items()))}


class Eliminator:
    """For each public assignment, enumerate every local six-bit private state."""
    def __init__(self, prefix, signs):
        self.prefix = prefix
        self.public_states = list(range(1 << prefix.public))
        self.full = (1 << len(self.public_states)) - 1
        self.public_masks = [[sum(1 << p for p in self.public_states if (p >> i) & 1 == val)
                              for val in (0, 1)] for i in range(prefix.public)]
        self.local = []
        for s, slot in enumerate(prefix.slots):
            conditions = []
            for p in self.public_states:
                allowed = []
                for private in range(64):
                    witnesses, switches = private & 7, private >> 3
                    if witnesses and all(not (witnesses & switches & (1 << i))
                                         or (((p >> x) ^ (signs[s] >> i)) & 1)
                                         for i, x in enumerate(slot)):
                        allowed.append(private)
                require(allowed, "an untouched slot cannot extend a public assignment")
                conditions.append(allowed)
            self.local.append(conditions)

    @lru_cache(maxsize=None)
    def local_public(self, slot, mask, value):
        return sum(1 << p for p in self.public_states
                   if any((private & mask) == value for private in self.local[slot][p]))

    def relation(self, scope):
        result = 0
        for bits in range(1 << len(scope)):
            possible = self.full
            private_masks = {}
            for j, var in enumerate(scope):
                val = (bits >> j) & 1
                if var < self.prefix.public:
                    possible &= self.public_masks[var][val]
                else:
                    slot, pos = divmod(var - self.prefix.public, 6)
                    mask, value = private_masks.get(slot, (0, 0))
                    private_masks[slot] = mask | (1 << pos), value | (val << pos)
            for slot, (mask, value) in private_masks.items():
                possible &= self.local_public(slot, mask, value)
            if possible:
                result |= 1 << bits
        return result


def large_fixture():
    prefix = Prefix(((0, 1, 2),) * 8)
    signs = tuple(range(8))
    oracle = Eliminator(prefix, signs)
    census = three_scope_census(prefix, [(signs, displayed(prefix.clauses(signs)))],
                                lambda scope: [oracle.relation(scope)])
    counts = quartets(prefix, signs, oracle.relation)
    by_x = defaultdict(list)
    for s, slot in enumerate(prefix.slots):
        for i, x in enumerate(slot):
            by_x[x].append((s, i))
    comparisons = 0
    for group in by_x.values():
        s, i = group[0]
        anchor_sign = (signs[s] >> i) & 1
        for u, j in group[1:]:
            scope = (prefix.e(s, i), prefix.w(s, i), prefix.e(u, j), prefix.w(u, j))
            relative = not (oracle.relation(scope) & (1 << 15))
            require(relative == (anchor_sign ^ ((signs[u] >> j) & 1)), "anchor reconstruction failed")
            comparisons += 1
    return {"bits": len(prefix.names), "slots": len(signs), "small_projections": census,
            "private_quartets": counts, "relative_sign_comparisons": comparisons}


def actual_knotlab():
    prefix = Prefix(((0, 1, 2), (0, 1, 2)))
    clauses = prefix.clauses((0, 1))
    cnf = "; ".join(" ".join(("" if val else "~") + prefix.names[x] for x, val in clause)
                    for clause in clauses)
    all_states, cols = boolean_columns(len(prefix.names))
    states = cnf_states(all_states, cols, clauses)
    tests = {
        "core": tuple(prefix.w(0, i) for i in range(3)),
        "positive_gate": (prefix.e(0, 0), prefix.w(0, 0), 0),
        "negative_gate": (prefix.e(1, 0), prefix.w(1, 0), 0),
        "nondisplayed": (0, 1, 2),
        "opposed": (prefix.e(0, 0), prefix.w(0, 0), prefix.e(1, 0), prefix.w(1, 0)),
        "aligned": (prefix.e(0, 1), prefix.w(0, 1), prefix.e(1, 1), prefix.w(1, 1)),
    }
    reports = {}
    for kind, scope in tests.items():
        visible = [prefix.names[i] for i in scope]
        hidden = [var for var in prefix.names if var not in visible]
        args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
                "--loops", *visible[:-1], "--contact", visible[-1], "--witnesses", *hidden, "--json"]
        env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
        report = json.loads(subprocess.run(args, check=True, capture_output=True, text=True, env=env).stdout)
        cells = pin_cells(all_states, cols, scope)
        allowed = {"".join(str((i >> j) & 1) for j in range(len(scope)))
                   for i, cell in enumerate(cells) if states & cell}
        require(set(report["allowed"]) == allowed, "knotlab and full CNF disagree")
        knot = kind not in ("nondisplayed", "aligned")
        require(report["is_knot"] == report["binding"] == knot and report["coexistence"]
                and report["loss_on_erasure"], f"unexpected K1–K3 verdict for {kind}")
        omitted = sorted({"".join(p) for p in product("01", repeat=len(scope))} - allowed)
        if knot:
            require(len(omitted) == 1, "expected one forbidden tuple")
            hole = omitted[0]
            neighbours = [hole[:j] + str(1 - int(hole[j])) + hole[j + 1:] for j in range(3)]
            majority = "".join(str(int(sum(int(r[j]) for r in neighbours) >= 2)) for j in range(len(scope)))
            require(set(neighbours) <= allowed and majority == hole and not report["pairwise_definable"],
                    "majority or two-clause obstruction failed")
        reports[kind] = {"variables": visible, "count": len(allowed), "omitted": omitted,
                         "K1": report["binding"], "K2": report["loss_on_erasure"],
                         "K3": report["coexistence"], "is_knot": report["is_knot"]}
    # Deleting the actual second implication on x0 should permit the previous conflict.
    opposed_cells = pin_cells(all_states, cols, tests["opposed"])
    removed_gate = ((prefix.e(1, 0), 0), (prefix.w(1, 0), 0), (0, 0))
    require(clauses.count(removed_gate) == 1, "deletion control lost its target")
    altered_states = cnf_states(all_states, cols, [c for c in clauses if c != removed_gate])
    require(project(altered_states, opposed_cells) == 65535,
            "opposed quartet stayed constrained after dropping its gate")
    return reports


def main():
    result = {"one_slot": full_table_fixture(((0, 1, 2),)),
              "two_repeated_slots": full_table_fixture(((0, 1, 2), (0, 1, 2))),
              "two_distinct_slots": full_table_fixture(((0, 1, 2), (0, 2, 3))),
              "eight_slots": large_fixture(), "knotlab": actual_knotlab()}
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2))
        return
    require(len(sys.argv) == 1, "expected no arguments, or --emit")
    require(result == json.loads(Path(__file__).with_name("projections.json").read_text()),
            "recomputed certificate differs from saved projection data")
    print(json.dumps({"status": "passed", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
