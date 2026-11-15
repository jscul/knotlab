"""Project the predecessor's actual pinned guarded axioms onto their source clauses."""

from collections import Counter
from functools import cache
import hashlib
import importlib.util
from itertools import chain, product
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
COMPILER = (ROOT / "proofs/TWO-RELAY-PADDING-20261115-001C"
            / "TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/check.py")
COMPILER_SHA256 = "28ec77fd9e0154378c7a1aefbe6d66f56df8b72e052b22961c6c29d9b743b6e4"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


@cache
def compiler():
    require(hashlib.sha256(COMPILER.read_bytes()).hexdigest() == COMPILER_SHA256,
            "the raw emitter differs from the declared predecessor")
    name = "route_parity_transfer_predecessor_c"
    spec = importlib.util.spec_from_file_location(name, COMPILER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def literal_image(lit, images):
    return images[lit] if lit > 0 else -images[-lit]


def clause_image(clause, images, true):
    """Return None for a tautology, () for false, or a signed source clause."""
    terms = {literal_image(lit, images) for lit in clause}
    if true in terms or any(-term in terms for term in terms):
        return None
    terms.discard(-true)
    return tuple(sorted(terms, key=abs))


class ProjectionTemplate:
    """Prepare the physical-variable images once, then apply any selector menu."""

    def __init__(self, n, clauses):
        self.clauses = tuple(tuple(clause) for clause in clauses)
        if type(n) is not int or n < 0:
            raise ValueError("source width must be a nonnegative integer")
        for clause in self.clauses:
            if (len(clause) != 3 or any(type(lit) is not int or not 1 <= abs(lit) <= n
                                        for lit in clause) or len(set(map(abs, clause))) != 3):
                raise ValueError("each source clause must name three distinct source variables")
        self.true = n + 1
        stages, starts = compiler().compile_stages(n, self.clauses)
        self.raw = compiler().StrictTemplate(stages, starts)
        used = {abs(lit) for clause in self.raw.cnf for lit in clause}
        self.base = dict.fromkeys(used, -self.true)
        specified = {}

        def put(key, value):
            variable = self.raw.var(key)
            require(variable in used, f"missing physical variable {key}")
            require(variable not in specified or specified[variable] == value,
                    f"two different images for {key}")
            specified[variable] = value

        def rail(v):
            if v == "source":
                return self.true
            if v == "sink":
                return -self.true
            return v

        heads, pad_images = [], []
        for x in range(1, n + 1):
            heads.extend([(x, -x), ("sink", "sink")])
            pad_images.extend([-x, x])
        for _, b, c in self.clauses:
            heads.append((b, c))
            pad_images.append(c)
        for row, ((first, second), pad) in enumerate(zip(heads, pad_images)):
            put(("shared_pad", row), pad)
            put(("middle", ("wire", row, 0)), rail(first))
            put(("middle", ("wire", row, 1)), rail(second))

        for v, start in starts.items():
            value = rail(v)
            put(("middle", ("feedback", v)), value)
            put(("boundary", start), value)
            stage = start
            while stages[stage][0][0][0] == "upper":
                put(("middle", stages[stage][0][0]), value)
                put(("boundary", stage + 1), value)
                stage += 1
        for end, stage, value in ((0, 0, self.true), (1, len(stages), -self.true)):
            put(("boundary", stage), value)
            put(("middle", ("endpoint", end)), value)
        self.base.update(specified)

    def pins(self, selected):
        if selected is None:
            selected = range(len(self.clauses))
        selected = frozenset(selected)
        if any(type(i) is not int or not 0 <= i < len(self.clauses) for i in selected):
            raise ValueError("selected position outside the input clause list")
        return self.raw.guards(selected)

    def substitution(self, pins, physical_overrides=None):
        images = self.base.copy()
        if physical_overrides:
            images.update(physical_overrides)
        require(len(pins) == len(self.raw.observable) and
                {abs(g) for g in pins} == set(self.raw.observable),
                "each visible switch must have exactly one pin")
        for pin in pins:
            images[abs(pin)] = self.true if pin > 0 else -self.true
        for i, guards in enumerate(self.raw.half_slots):
            witnesses = self.raw.cnf[4 * i]
            guard_values = [images[g] for g in guards]
            if -self.true in guard_values:
                off = guard_values.index(-self.true)
                for j, w in enumerate(witnesses):
                    images[w] = self.true if j == off else -self.true
            else:
                for j, (g, w) in enumerate(zip(guards, witnesses)):
                    row = self.raw.cnf[4 * i + j + 1]
                    require(row[:2] == [-g, -w], "unexpected guarded clause")
                    images[w] = literal_image(row[2], images)
        return images


def build_projection(n, clauses, selected=None):
    """Return (raw, pin_literals, images). Literal constants are ±(n+1).

    All listed occurrences are selected by default. A selector iterable gives
    the zero-based indices of its selected occurrences. The pinned CNF has
    raw.cnf followed by one unit clause for each signed pin literal.
    """
    template = ProjectionTemplate(n, clauses)
    pins = template.pins(selected)
    return template.raw, pins, template.substitution(pins)


def residual_multiset(raw, pins, images, true, extra_clauses=()):
    result = Counter()
    for clause in chain(raw.cnf, extra_clauses):
        image = clause_image(clause, images, true)
        if image is not None:
            result[image] += 1
    for pin in pins:
        require(clause_image([pin], images, true) is None, "nontrivial guard-pin image")
    return result


def validate_case(template, selected, totals):
    pins = template.pins(selected)
    images = template.substitution(pins)
    observed = residual_multiset(template.raw, pins, images, template.true)
    expected = Counter(tuple(sorted(template.clauses[i], key=abs)) for i in selected)
    require(observed == expected, f"raw axiom images do not equal the selected source: {observed}")
    totals["selector_or_listed_inputs_checked"] += 1
    totals["raw_and_unit_axiom_images_checked"] += len(template.raw.cnf) + len(pins)
    totals["surviving_source_clause_occurrences"] += sum(observed.values())
    return observed


def run_checks():
    totals = Counter()
    for n in (3, 4, 5):
        clauses = compiler().clauses_on(n)
        template = ProjectionTemplate(n, clauses)
        if n == 3:
            menus = [tuple(i for i in range(8) if mask >> i & 1) for mask in range(256)]
        else:
            menus = [(), (0,), (len(clauses) - 1,), tuple(range(1, len(clauses), 3)),
                     tuple(range(len(clauses)))]
        for selected in menus:
            validate_case(template, selected, totals)
        totals[f"fixed_width_{n}_menus"] = len(menus)

    for n in (0, 1, 2, 6):
        validate_case(ProjectionTemplate(n, []), (), totals)
    listed = [(5, -3, 1), (1, 5, -3), (-4, 2, 5), (5, -3, 1)]
    listed_images = validate_case(ProjectionTemplate(7, listed), range(len(listed)), totals)
    require(listed_images[(1, -3, 5)] == 3, "listed duplicate occurrences were lost")
    fixed_clauses = compiler().clauses_on(5)
    fixed_indices = {tuple(sorted(clause, key=abs)): i for i, clause in enumerate(fixed_clauses)}
    selected = {fixed_indices[tuple(sorted(clause, key=abs))] for clause in listed}
    fixed_images = validate_case(ProjectionTemplate(5, fixed_clauses), selected, totals)
    require(set(fixed_images) == set(listed_images) and max(fixed_images.values()) == 1,
            "fixed canonical slots must keep each distinct selected clause once")
    totals["listed_copies_of_reordered_clause"] = listed_images[(1, -3, 5)]
    totals["fixed_copies_of_reordered_clause"] = fixed_images[(1, -3, 5)]
    totals["empty_source_widths_checked"] = 4

    raw, pins, images = build_projection(3, [(1, 2, 3)])
    good = residual_multiset(raw, pins, images, 4)
    require(good == Counter({(1, 2, 3): 1}), "public API default did not select the listed clause")
    survivor = next(row for row in raw.cnf if clause_image(row, images, 4) is not None)
    doubled = residual_multiset(raw, pins, images, 4, extra_clauses=[survivor])
    require(doubled == Counter({(1, 2, 3): 2}), "raw clause clone lost its multiplicity")
    totals["raw_clone_projected_occurrences"] = doubled[(1, 2, 3)]
    template = ProjectionTemplate(3, [(1, 2, 3)])
    pins = template.pins(None)
    images = template.substitution(pins)
    bad_pad = template.raw.var(("shared_pad", 6))
    bad_images = template.substitution(pins, {bad_pad: -3})
    wrong = residual_multiset(template.raw, pins, bad_images, template.true)
    require(wrong == Counter({(1, 2, -3): 1, (3,): 1}) and wrong != good,
            "opposite data-pad substitution did not give the predicted foreign constraints")
    totals["wrong_data_pad_foreign_axioms"] = sum(wrong.values())

    # A partly switched-off padded slot is free even when its other guards are on.
    slot = next(i for i in range(len(template.raw.half_slots))
                if clause_image(template.raw.cnf[4 * i], images, template.true) == (1, 2, 3))
    gs = template.raw.half_slots[slot]
    other_pins = [g for g in pins if abs(g) not in gs]
    for mask in range(8):
        partial = other_pins + [g if mask >> j & 1 else -g for j, g in enumerate(gs)]
        mapping = template.substitution(partial)
        got = [clause_image(c, mapping, template.true)
               for c in template.raw.cnf[4 * slot:4 * slot + 4]]
        require(got == ([(1, 2, 3), None, None, None] if mask == 7 else [None] * 4),
                "an off guard failed to free its witness slot")
    totals["local_guard_patterns_checked"] = 8

    # Preserve both free source rails while adjoining a uniquely extensible auxiliary.
    empty_raw, empty_pins, empty_images = build_projection(2, [])
    require(not residual_multiset(empty_raw, empty_pins, empty_images, 3),
            "the empty input acquired a clause")
    x, y = empty_raw.signals[1], empty_raw.signals[2]
    z = max(empty_images) + 1
    xor_rows = [[-v if bit else v for v, bit in zip((x, y, z), bits)]
                for bits in product((0, 1), repeat=3) if sum(bits) % 2]
    for left, right in product((False, True), repeat=2):
        extensions = []
        for aux in (False, True):
            values = {x: left, y: right, z: aux}
            if all(any(values[abs(lit)] == (lit > 0) for lit in row) for row in xor_rows):
                extensions.append(aux)
        require(extensions == [left != right], "mutant lacks its unique XOR extension")
    rejected = 0
    for candidate in (1, -1, 2, -2, 3, -3):
        mapping = {**empty_images, z: candidate}
        if any(clause_image(row, mapping, 3) is not None for row in xor_rows):
            rejected += 1
    require(rejected == 6, "XOR extension unexpectedly admitted a faithful literal substitution")
    totals["xor_source_assignments_with_unique_extension"] = 4
    totals["xor_literal_or_constant_images_rejected"] = rejected
    return {"status": "passed", **totals}


if __name__ == "__main__":
    if importlib.util.find_spec("pysat") is None:
        local = ROOT / ".venv/bin/python"
        if not local.exists() or os.path.abspath(sys.executable) == os.path.abspath(local):
            raise RuntimeError("the predecessor's strict emitter requires python-sat")
        os.execv(local, [str(local), "-B", __file__])
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
