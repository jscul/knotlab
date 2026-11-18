"""Certify the bounded checks in the proof and run the anonymous reader under relabeling."""

import hashlib
import json
import os
import random
import subprocess
import sys
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path

from check_aligned import SOURCE, SOURCE_DIGEST, bits, projected_rows, short_supports
from read_frontier import read_frontier, sparse_rows, twin_classes

ROOT = Path(__file__).resolve().parents[3]


def source_groups(model):
    import importlib.util

    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_DIGEST
    spec = importlib.util.spec_from_file_location("original_growth_rule", SOURCE)
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    junctions = {v: tuple(bits(s)) for v, s in enumerate(model.stars)}
    users, neighbors = rules.incidence(junctions)
    loose = {v: tuple(sorted(ports)) for v, ports in rules.loose_ports(users).items()}
    groups, _ = rules.parent_groups(junctions)
    candidates = {tuple(sorted((loose[v], loose[w]))) for v, w in combinations(loose, 2)
                  if neighbors[v] & neighbors[w]}
    groups = tuple(sorted(tuple(sorted(loose[v] for v in group)) for group in groups))
    incoming = {g: set(junctions[v]) - set(g) for v, g in loose.items()}
    return incoming, candidates, groups


def permuted_rows(rows, perm):
    out = [{} for _ in rows]
    for i, row in enumerate(rows):
        out[perm[i]] = {perm[j]: val for j, val in row.items()}
    return out


def validate_reader(data, stage):
    rows = sparse_rows(len(data.model.wires), data.mixed)
    truth, pairs, groups = source_groups(data.model)
    for seed in (0, 113, 271):
        perm = list(range(len(rows)))
        if seed:
            random.Random(seed).shuffle(perm)
        result = read_frontier(permuted_rows(rows, perm))
        def rename(g):
            return tuple(sorted(perm[i] for i in g))
        assert {rename(g): {perm[i] for i in incoming} for g, incoming in truth.items()} == result["incoming"]
        expected_pairs = {tuple(sorted((rename(g), rename(h)))) for g, h in pairs}
        actual_pairs = {tuple(sorted((g, h))) for g, ns in result["adjacent"].items() for h in ns}
        assert actual_pairs == expected_pairs
        assert tuple(sorted(tuple(sorted(rename(g) for g in group)) for group in groups)) == result["groups"]
    counts = dict(sorted(Counter(map(len, groups)).items()))
    assert counts == {1: 3, 2: 3 * stage, 3: comb(stage, 2)}
    assert all(count == 3 for count in Counter(g for group in groups for g in group).values())
    assert len(set(groups)) == len(groups)
    return {"junctions": len(data.model.vertices), "distinctions": len(rows),
            "loose_triplets": len(truth), "candidate_parent_pairs": len(pairs),
            "required_joins_by_parent_count": counts, "permitted_full_allocations": str(6**len(truth)),
            "exact_under_permutations": [0, 113, 271]}


def knot_cli(model, names):
    indexes = [model.wires.index(wire) for wire in names]
    mask = sum(1 << i for i in indexes)
    positions = {wire: j for j, wire in enumerate(sorted(indexes))}
    labels = tuple(f"b{j}" for j in range(len(names)))
    allowed = {tuple((row >> positions[i]) & 1 for i in indexes) for row in projected_rows(model, mask)}
    forbidden = sorted(set(product(range(2), repeat=len(names))) - allowed)
    clauses = [" ".join(("~" if bit else "") + label for label, bit in zip(labels, row)) for row in forbidden]
    cnf = "; ".join(clauses) or f"{labels[0]} ~{labels[0]}"
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", *labels[:-1],
           "--contact", labels[-1], "--json"]
    report = json.loads(subprocess.check_output(cmd, env={**os.environ, "PYTHONPATH": str(ROOT/"tools")}))
    assert set(report["allowed"]) == {"".join(map(str, row)) for row in allowed}
    return {"arity": len(names), "allowed_rows": len(allowed), "knot": report["is_knot"]}



def audit_signatures():
    """Compare the potential obstruction with all eight literal rows on every subspace."""
    spaces = {frozenset({0}): ()}
    for v in range(1, 16):
        for space, basis in tuple(spaces.items()):
            if v not in space:
                larger = space | {w ^ v for w in space}
                spaces.setdefault(larger, (*basis, v))
    counts = Counter()
    tuples = [sign | cut for sign in (0, 8) for cut in (0, 1, 2, 4)]
    for space, basis in spaces.items():
        outputs = {tuple((row & v).bit_count() % 2 for v in basis) for row in tuples}
        onto = len(outputs) == 2**len(basis)
        even = {v for v in space if v < 8}
        bad = any({a, b, a^b} != {3,5,6} for a,b in combinations(even - {0}, 2))
        assert onto == (not bad)
        counts["full" if onto else "constrained"] += 1
    assert counts == {"full": 47, "constrained": 20}
    return dict(counts)

def main():
    stages = {}
    for t in range(4, 11):
        data = short_supports(t)
        stages[t] = validate_reader(data, t)
        if t == 4:
            # The old mixed counterexample reflected the horizontal ports
            # in the upper layer of the small template only.
            base = data.model
            original = sparse_rows(len(base.wires), data.mixed)
            flip = [base.wires.index(((y, x, z), 1 - axis)) if x < 2 and y < 2 and z == 1 and axis < 2 else i
                    for i, ((x,y,z),axis) in enumerate(base.wires)]
            rival = permuted_rows(original, flip)
            different_entries = sum(original[i].get(j) != rival[i].get(j)
                                    for i,j in combinations(range(len(flip)), 2))
            assert different_entries > 0
            recovered = read_frontier(original)
            inputs = recovered["incoming"]
            cross_counts = Counter(sum(j in original[i] for i in inputs[g] for j in inputs[h])
                                   for g, h in combinations(recovered["triplets"], 2))
            assert cross_counts == {0: 75, 1: 26, 2: 4}
            triple = [((0,0,0),2), ((1,0,0),2), ((1,1,0),2)]
            terminal_star = tuple(base.wires[i] for i in bits(base.stars[base.vertices.index((1,1,2))]))
            canonical = [knot_cli(base, q) for q in (triple, terminal_star, terminal_star[:-1])]
            assert [q["knot"] for q in canonical] == [True, True, False]
        if t == 7:
            rows = sparse_rows(len(data.model.wires), data.mixed)
            grades = [sum(point) for point,_ in data.model.wires]
            core = {i for i, grade in enumerate(grades) if grade <= 3}
            twins = twin_classes(rows)
            assert not any(core.intersection(g) for g in twins)
            assert all(any(j != i and data.model.wires[j][0] == data.model.wires[i][0] for j in rows[i])
                       for i in core)
            stabilization = {"stage": t, "core_distinctions": len(core),
                             "core_distinctions_with_a_twin": sum(len(core.intersection(g)) for g in twins),
                             "maximum_candidate_twin_grade": 5}
        if t == 9:
            new = data.mixed - data.ordinary
            missing = data.ordinary - data.mixed
            affected = {i for support in new | missing for i in bits(support)}
            maximum = max(sum(data.model.wires[i][0]) for i in affected)
            assert len(new)==479 and not missing and maximum==3
            # The true projected relations and every proper one-bit erasure
            # are checked by extending assignments via graph components.
            for support in new:
                assert 0 < len(projected_rows(data.model, support)) < 1 << support.bit_count()
                for i in bits(support):
                    smaller = support ^ (1 << i)
                    assert len(projected_rows(data.model, smaller)) == 1 << smaller.bit_count()
            classification = {"stage": t, "pure_short_supports": len(data.ordinary),
                              "mixed_short_supports": len(data.mixed), "added": len(new), "removed": len(missing),
                              "affected_distinctions": len(affected), "max_affected_grade": maximum,
                              "all_added_supports_and_deletions_checked": len(new)}
    return {"scalar_threshold": 5, "reader_stages": stages, "localization_certificate": classification,
            "twin_stability_certificate": stabilization, "signature_space_controls": audit_signatures(),
            "canonical_knot_cli": canonical,
            "upper_reflection_changed_threshold_entries_at_I4": different_entries,
            "I4_parent_pairs_by_short_cross_witness_count": dict(cross_counts)}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
