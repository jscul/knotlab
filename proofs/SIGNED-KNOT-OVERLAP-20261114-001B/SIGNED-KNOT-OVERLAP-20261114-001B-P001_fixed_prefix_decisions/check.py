"""Check fixed switch queries, full small projections, and the affine control."""

import json
import os
from itertools import combinations, product
from pathlib import Path
import subprocess
import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def slots(n):
    return [tuple(i * sign for i, sign in zip(triple, signs))
            for triple in combinations(range(1, n + 1), 3)
            for signs in product((1, -1), repeat=3)]


def literal_value(lit, assignment):
    value = (assignment >> (abs(lit) - 1)) & 1
    return bool(value) == (lit > 0)


def clause_holds(clause, assignment):
    return any(literal_value(lit, assignment) for lit in clause)


def rules(n, clauses):
    result = []
    for s, clause in enumerate(clauses):
        ws = tuple(n + 6 * s + j + 1 for j in range(3))
        result.append(ws)
        result.extend((-(w + 3), -w, lit) for w, lit in zip(ws, clause))
    return result


def support(clause):
    return tuple(sorted(abs(x) - 1 for x in clause))


def support_mask(clause):
    return sum(1 << i for i in support(clause))


def guard_models(n, clause, e):
    """Existentially try the seven witnesses satisfying the actual local core."""
    result = 0
    for x in range(1 << n):
        for w in range(1, 8):
            if all(not ((e >> j) & (w >> j) & 1) or literal_value(lit, x)
                   for j, lit in enumerate(clause)):
                result |= 1 << x
                break
    return result


def solve_xor(rows, pins):
    """Ordinary GF(2) elimination with a constant bit kept separately."""
    pivots = {}
    equations = [(row, 0) for row in rows] + [(1 << i, value) for i, value in pins]
    for mask, value in equations:
        while mask:
            i = mask.bit_length() - 1
            if i not in pivots:
                pivots[i] = mask, value
                break
            known, rhs = pivots[i]
            mask ^= known
            value ^= rhs
        else:
            if value:
                return False
    return True


def fixed_queries():
    n = 3
    signed = slots(n)
    aligned = [tuple(map(abs, c)) for c in signed]
    rows = [support_mask(c) for c in rules(n, signed)]
    signed_slot = [[guard_models(n, c, e) for e in range(8)] for c in signed]
    aligned_slot = [[guard_models(n, c, e) for e in range(8)] for c in aligned]
    for c, models in zip(signed, signed_slot):
        true_x = sum(1 << x for x in range(8) if clause_holds(c, x))
        require(models == [255] * 7 + [true_x], "local slot extension differs from clause activation")
    restrictions = {}
    for pin in product((None, 0, 1), repeat=n):
        compatible = [x for x in range(8) if all(v is None or ((x >> j) & 1) == v
                                                 for j, v in enumerate(pin))]
        maximizer = sum((v != 0) << j for j, v in enumerate(pin))
        restrictions[pin] = (sum(1 << x for x in compatible), maximizer)
    yes_signed, yes_aligned, yes_xor = set(), set(), set()
    signed_raw_count = affine_raw_count = 0
    partial_queries = 0
    for y in range(256):
        selected = [s for s in range(8) if y >> s & 1]
        signed_models = aligned_models = 255
        pins = []
        for s in range(8):
            on = (y >> s) & 1
            signed_models &= signed_slot[s][7 * on]
            aligned_models &= aligned_slot[s][7 * on]
            pins.extend((n + 6 * s + j + 3, on) for j in range(3))
        source_models = sum(1 << x for x in range(8)
                            if all(clause_holds(signed[s], x) for s in selected))
        require(signed_models == source_models, "the fixed-prefix reduction changed a public model")
        if signed_models:
            yes_signed.add(y)
            signed_raw_count += 7 ** (8 - len(selected))
        if aligned_models:
            yes_aligned.add(y)
        if solve_xor(rows, pins):
            yes_xor.add(y)
        # Solve one representative of each tuple of eight switch parities.
        parity_sample = [(n + 6 * s + 3 + j, ((y >> s) & 1) if j == 0 else 0)
                         for s in range(8) for j in range(3)]
        if solve_xor(rows, parity_sample):
            affine_raw_count += 4**8
        for allowed, maximizer in restrictions.values():
            require(bool(aligned_models & allowed) == bool(aligned_models & (1 << maximizer)),
                    "aligned monotone extension disagrees with existential completion")
            require(bool(signed_models & allowed) == bool(source_models & allowed), "public pins")
            partial_queries += 1
    require(yes_signed == set(range(255)), "signed eight-clause MUS")
    require(yes_aligned == set(range(256)), "aligned all-switch control")
    require(yes_xor == {0, 255}, "affine grouped control")
    require(signed_raw_count == 2**24 - 1, "independent guard count")
    for e, x in product(range(8), repeat=2):
        local_witnesses = [w for w in range(8) if w.bit_count() % 2 == 0 and w ^ e ^ x == 0]
        require(bool(local_witnesses) == (e.bit_count() % 2 == x.bit_count() % 2),
                "actual affine guard triple does not reduce to switch parity")
    require(affine_raw_count == 2**17, "affine independent guard count")
    # A single equation detects inconsistent pins, including a witness pin.
    require(not solve_xor(rows, [(n, 1), (n + 1, 0), (n + 2, 0)]),
            "Gaussian elimination missed a pinned non-even core")
    return yes_signed, len(yes_aligned), len(yes_xor), signed_raw_count, affine_raw_count, partial_queries


def ternary_projections(n, clauses, affine=False):
    local = rules(n, clauses)
    var_count = n + 6 * len(clauses)
    rule_by_support = {support(c): c for c in local}
    require(len(rule_by_support) == len(local), "two rules share a ternary support")
    masks = [support_mask(c) for c in local]
    if affine:
        models = [v for v in range(1 << var_count)
                  if all((v & row).bit_count() % 2 == 0 for row in masks)]
    else:
        models = [v for v in range(1 << var_count) if all(clause_holds(c, v) for c in local)]
    columns = [sum(1 << v for v, assignment in enumerate(models) if assignment >> j & 1)
               for j in range(var_count)]
    full = (1 << len(models)) - 1
    projections = {}
    for width in range(1, 4):
        for coordinates in combinations(range(var_count), width):
            projected = set()
            expected = set()
            row = rule_by_support.get(coordinates)
            for values in product((0, 1), repeat=width):
                remaining = full
                for j, value in zip(coordinates, values):
                    remaining &= columns[j] if value else ~columns[j]
                if remaining:
                    projected.add(values)
                represented = sum(v << j for j, v in zip(coordinates, values))
                if row is None or (sum(values) % 2 == 0 if affine else clause_holds(row, represented)):
                    expected.add(values)
            require(projected == expected, "global projection disagrees with declared rule")
            if width == 3:
                projections[coordinates] = projected
    return projections


def full_affine_short_rows():
    local = rules(3, slots(3))
    cores = [support_mask(c) for i, c in enumerate(local) if i % 4 == 0]
    guards = [support_mask(c) for i, c in enumerate(local) if i % 4]
    core_sums = {0}
    for c in cores:
        core_sums |= {m ^ c for m in core_sums}
    short = set()
    combinations_tested = 0
    for r in range(4):
        for group in combinations(guards, r):
            total = 0
            for c in group:
                total ^= c
            for core_sum in core_sums:
                value = total ^ core_sum
                combinations_tested += 1
                if 0 < value.bit_count() <= 3:
                    short.add(value)
    require(short == set(guards + cores), "an extra low-weight affine consequence appeared")
    return len(short), combinations_tested


def full_three_variable_prefix(clauses):
    """Reconstruct all 51-choice prefix triples from enumerated slot models."""
    n = 3
    # Table keys are (mask for pinned choices, their assigned values).
    tables = {-1: {(mask, x & mask): sum(1 << y for y in range(8) if y & mask == x & mask)
                   for mask in range(8) for x in range(8)}}
    private_masks = [mask for mask in range(64) if mask.bit_count() <= 3]
    for i, clause in enumerate(clauses):
        table = {}
        local = rules(n, [clause])
        for model in range(512):
            if all(clause_holds(c, model) for c in local):
                for mask in private_masks:
                    key = mask, (model >> n) & mask
                    table[key] = table.get(key, 0) | (1 << (model & 7))
        require(table[0, 0] == 255, "an untouched slot already constrains public choices")
        tables[i] = table
    by_support = {support(c): c for c in rules(n, clauses)}
    checked = 0
    for coordinates in combinations(range(n + 6 * len(clauses)), 3):
        parts = [(-1, i) if i < n else divmod(i - n, 6) for i in coordinates]
        masks = {part: 0 for part, _ in parts}
        for part, j in parts:
            masks[part] |= 1 << j
        rule = by_support.get(coordinates)
        for values in product((0, 1), repeat=3):
            pins = dict.fromkeys(masks, 0)
            for (part, j), bit in zip(parts, values):
                pins[part] |= bit << j
            common_public = 255
            for part, mask in masks.items():
                common_public &= tables[part].get((mask, pins[part]), 0)
            x = sum(v << j for j, v in zip(coordinates, values))
            require(bool(common_public) == (rule is None or clause_holds(rule, x)),
                    "universal prefix has an unexpected projected assignment")
        checked += 1
    return checked


def minimal_unsatisfiable(clauses, n):
    necessary = set()
    for x in range(1 << n):
        failed = [j for j, c in enumerate(clauses) if not clause_holds(c, x)]
        if not failed:
            return False
        if len(failed) == 1:
            necessary.add(failed[0])
    return len(necessary) == len(clauses)


def check_replacements():
    clauses = slots(3)
    n = 3
    for step in range(4):
        require(len(clauses) == 8 + 2 * step and all(len(support(c)) == len(set(support(c))) == 3
                for c in clauses), "replacement is not a strict three-variable MUS candidate")
        require(minimal_unsatisfiable(clauses, n), "replacement lost a critical deletion")
        if step < 3:
            a, b, c = clauses.pop(0)
            t, u = n + 1, n + 2
            clauses.extend([(a, b, t), (-t, c, u), (-t, c, -u)])
            n += 2
    return len(clauses)


def canonical_knot(projected, width, expected_knot):
    names = [f"v{i}" for i in range(width)]
    excluded = set(product((0, 1), repeat=width)) - projected
    clauses = [" ".join(("~" if bit else "") + name for name, bit in zip(names, values))
               for values in sorted(excluded)]
    if not clauses:
        clauses = [f"{name} ~{name}" for name in names]
    root = Path(__file__).resolve().parents[3]
    env = {**os.environ, "PYTHONPATH": str(root / "tools")}
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", *names[:-1], "--contact", names[-1], "--json"]
    data = json.loads(subprocess.check_output(command, cwd=root, env=env, text=True))
    observed = {tuple(map(int, row)) for row in data["allowed"]}
    require(observed == projected and data["is_knot"] == expected_knot, "canonical knot test")
    return data["minimum_width"]


def main():
    grouped, aligned, affine, raw, raw_affine, partial_count = fixed_queries()
    clauses = [slots(3)[0], slots(3)[-1]]
    signed_proj = ternary_projections(3, clauses)
    aligned_proj = ternary_projections(3, [tuple(map(abs, c)) for c in clauses])
    xor_proj = ternary_projections(3, clauses, affine=True)
    supports = {s for s in signed_proj if len(signed_proj[s]) < 8}
    require(supports == {s for s in aligned_proj if len(aligned_proj[s]) < 8}
            == {s for s in xor_proj if len(xor_proj[s]) < 8}, "different ternary support sets")
    require(any(signed_proj[s] != aligned_proj[s] for s in supports), "signed rows lost their signs")
    require(all(len(signed_proj[s]) == 7 and len(xor_proj[s]) == 4 for s in supports),
            "seven- and four-assignment controls")
    local_relations = {frozenset(p[s]) for p in (signed_proj, aligned_proj, xor_proj)
                       for s in supports}
    for relation in local_relations:
        require(canonical_knot(relation, 3, True) == 3, "ternary relation lost width")
    require(canonical_knot(signed_proj[(0, 1, 2)], 3, False) == 0, "public triple is constrained")
    grouped_relation = {tuple((y >> j) & 1 for j in range(8)) for y in grouped}
    require(canonical_knot(grouped_relation, 8, True) == 8, "grouped MUS lost a switch")
    short, row_sums = full_affine_short_rows()
    signed_full = full_three_variable_prefix(slots(3))
    aligned_full = full_three_variable_prefix([tuple(map(abs, c)) for c in slots(3)])
    require(signed_full == aligned_full == 20825, "some full-prefix triples were omitted")
    largest_mus = check_replacements()
    return {
        "status": "passed",
        "grouped_signed_yes_n3": len(grouped),
        "grouped_aligned_yes_n3": aligned,
        "grouped_affine_yes_n3": affine,
        "independent_signed_guard_vectors_n3": raw,
        "independent_affine_guard_vectors_n3": raw_affine,
        "grouped_inputs_with_partial_public_pins_checked": partial_count,
        "two_slot_triples_per_control": len(signed_proj),
        "two_slot_ternary_knot_supports_per_control": len(supports),
        "distinct_ternary_relations_verified_by_knotlab": len(local_relations),
        "grouped_guard_knot_width_checked_by_knotlab": 8,
        "full_n3_affine_short_rows": short,
        "full_n3_triples_per_signed_or_aligned_control": signed_full,
        "full_n3_affine_row_sums_with_at_most_three_guards": row_sums,
        "largest_strict_mus_checked_by_all_deletions": largest_mus,
        "named_guards_in_largest_mus_checked": 3 * largest_mus,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
