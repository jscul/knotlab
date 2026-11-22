"""Exact counts and original/current reader replays on the frozen growth archive."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from math import gcd, prod
import os
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEDOM = "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A"
FAMILY = FREEDOM + "-E001_freedom"
ARCHIVE = ROOT / "artifacts" / FREEDOM / FAMILY / "histories.json.gz"
REGISTRATION = HERE / "preregistration.md"
ENGINE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py"
END = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
ANCESTOR_PATHS = (
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/joinlib.py",
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py",
    "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py",
    "experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/freelib.py",
)
CAP = 18
SPLIT_CAP = 4
LOOSE_DENSE = 14
REPORTED_LOOSE_CAP = 65536
LAWS = ("parity", "nae")
SETTINGS = tuple("".join(s) for s in product("ZX", repeat=3))
TERMS = ("XXX", "XZZ", "ZXZ", "ZZX")
PRIVATE_WAYS_SHA = "4bd90354c38e35fc242f4340c59687ec6ebc2bb560543a36086e91e00389febc"


def _load(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@cache
def _engine():
    mod = _load("spent_pasts_growth", ENGINE)
    j = mod.J
    for observed, rel in zip((j, j.fastlib, j.S, j.F), ANCESTOR_PATHS, strict=True):
        assert Path(observed.__file__).resolve() == ROOT / rel
    return mod, _load("spent_pasts_end", END)


def _mask(names):
    return sum(1 << b for b in names)


def _extract(word, names):
    return sum(((word >> b) & 1) << i for i, b in enumerate(names))


def _bits(word, names):
    return "".join(str((word >> b) & 1) for b in names)


def _sign(word):
    return -1 if word.bit_count() % 2 else 1


def _prob(n, d):
    return str(F(n, d)) if d else None


def _owners(rows):
    found = {}
    for h, row in enumerate(rows):
        assert len(row) == len(set(row))
        for b in row:
            found.setdefault(b, []).append(h)
    assert all(1 <= len(holds) <= 2 for holds in found.values())
    return {b: tuple(found[b]) for b in sorted(found)}


def _sorted_rows(rows):
    return tuple(tuple(r) for r in rows)


def _valid(word, masks, law):
    if law == "parity":
        return all((word & m).bit_count() % 2 == 0 for m in masks)
    return all(word & m not in (0, m) for m in masks)


def _parity_count(rows, names, fixed):
    pinned = _mask(fixed)
    values = _mask(b for b in fixed if fixed[b])
    basis = {}
    for row in rows:
        rhs = (row & values).bit_count() % 2
        rem = row & ~pinned
        while rem:
            pivot = rem.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = rem, rhs
                break
            old, shift = basis[pivot]
            rem, rhs = rem ^ old, rhs ^ shift
        if not rem and rhs:
            return 0
    return 1 << (len(names) - len(fixed) - len(basis))


@dataclass(frozen=True)
class LocalFactor:
    branch_terms: tuple
    free_once_held: int = 0

    @property
    def scope(self):
        return tuple(sorted({v for names, _ in self.branch_terms for v in names}))

    def values(self, pins):
        terms = tuple((tuple(x for x in names if x not in pins),
                       seen | sum({1 << pins[x] for x in names if x in pins}))
                      for names, seen in self.branch_terms)
        return _materialize_factor(terms, self.free_once_held)


@cache
def _materialize_factor(terms, free):
    scope = tuple(sorted({v for names, _ in terms for v in names}))
    assert len(scope) <= CAP
    # The final numpy axis is the least significant position in the encoded row.
    grid = np.arange(1 << len(scope), dtype=np.uint32)
    banned0, banned1 = np.zeros(len(grid), dtype=bool), np.zeros(len(grid), dtype=bool)
    for names, fixed in terms:
        flags = np.full(len(grid), fixed, dtype=np.uint8)
        for name in names:
            flags |= 1 << ((grid >> (len(scope) - 1 - scope.index(name))) & 1)
        banned0 |= flags < 2
        banned1 |= (flags & 1) == 0
    if free:
        dtype = np.int64 if free < 63 else object
        values = np.full(len(grid), 1 << free, dtype=dtype) - banned0 - banned1
    else:
        values = np.asarray(~(banned0 | banned1), dtype=np.int64)
    return scope, values.reshape((2,) * len(scope))


@cache
def _elimination_plan(scopes, keep):
    graph = {v: set() for scope in scopes for v in scope}
    for scope in scopes:
        for b in scope:
            graph[b].update(v for v in scope if v != b)
    preserved = set(keep)
    assert preserved <= set(graph)
    order = []
    peak = max([len(keep), *(len(s) for s in scopes)])
    peak_scope = max((scopes + (keep,)), key=len)
    remaining = set(graph) - preserved
    while remaining:
        p = min(remaining, key=lambda v: (len(graph[v]), v))
        linked = graph.pop(p)
        if 1 + len(linked) > peak:
            peak = 1 + len(linked)
            peak_scope = tuple(sorted({p, *linked}))
        for n in linked:
            graph[n].remove(p)
            graph[n].update(linked - {n})
        remaining.remove(p)
        order.append(p)
    return peak, tuple(order), peak_scope


@cache
def _bounded_plan(scopes, keep):
    untouched = _elimination_plan(scopes, keep)
    selected = []
    current = scopes
    plan = untouched
    while plan[0] > CAP and len(selected) < SPLIT_CAP:
        candidates = set(plan[2]) - set(keep)
        if not candidates:
            break
        def trial(v):
            drop = tuple(tuple(t for t in row if t != v) for row in current)
            alt = _elimination_plan(drop, keep)
            return alt[0], -sum(v in row for row in current), v, alt, drop

        _, _, pin, plan, current = min(trial(v) for v in candidates)
        selected.append(pin)
    return untouched[0], tuple(selected), plan


def _contract(factors, scope, sum_terms_bound=1):
    assert len(scope) <= CAP
    # Bound the wide multiplication in Python integers before allocating its tensor.
    ceiling = prod(int(a.max()) for _, a in factors) * sum_terms_bound
    dtype = np.int64 if ceiling < 1 << 63 and all(a.dtype != object for _, a in factors) else object
    val = np.ones((2,) * len(scope), dtype=dtype)
    for names, a in factors:
        val *= a.reshape(tuple(2 if b in names else 1 for b in scope))
    return val


class CountLimit(Exception):
    def __init__(self, meta):
        self.record = meta


def _count_factors(factors, keep=()):
    scopes = tuple(f.scope for f in factors)
    first, split, plan = _bounded_plan(scopes, keep)
    width, order, obstruction = plan
    receipt = {"unpartitioned_elimination_peak": first, "split_binary_indices": split,
               "simultaneous_binary_peak": width, "conditional_branch_count": 1 << len(split)}
    if width > CAP:
        raise CountLimit({**receipt, "obstructing_indices": obstruction, "fixed_binary_limit": CAP})
    answer = None
    for bits in product((0, 1), repeat=len(split)):
        pins = dict(zip(split, bits, strict=True))
        table = [f.values(pins) for f in factors]
        for v in order:
            involved = [f for f in table if v in f[0]]
            table = [f for f in table if v not in f[0]]
            joined = tuple(sorted({name for sources, _ in involved for name in sources}))
            reduced = _contract(involved, joined, sum_terms_bound=2).sum(axis=joined.index(v))
            table.append((tuple(x for x in joined if x != v), np.asarray(reduced)))
        sorted_keep = tuple(sorted(keep))
        next_answer = _contract(table, sorted_keep).transpose(tuple(sorted_keep.index(v) for v in keep)).astype(object)
        answer = next_answer if answer is None else answer + next_answer
    # For requested names, reverse the axes to print name zero as the least significant bit.
    return tuple(int(v) for v in np.asarray(answer, dtype=object).transpose().flat), receipt


@dataclass
class Stage:
    rows: tuple
    law: str

    def __post_init__(self):
        self.owners = _owners(self.rows)
        self.names = tuple(self.owners)
        self.spent = tuple(n for n, h in self.owners.items() if len(h) == 2)
        self.loose = tuple(n for n, h in self.owners.items() if len(h) == 1)
        self.shared = set(self.spent)
        self.loose_set = set(self.loose)
        self.namemask = _mask(self.names)
        self.masks = tuple(map(_mask, self.rows))
        self.offset = max(self.names, default=-1) + 1
        self.measurements = {}

    def local_factors(self, fixed_maps, duplicate_spent=False, retained=()):
        fixed_names = fixed_maps[0].keys()
        assert all(p.keys() == fixed_names for p in fixed_maps)
        assert not set(retained).intersection(fixed_names)
        free_loose = self.loose_set - set(retained) - set(fixed_names)
        pieces = []
        for row in self.rows:
            free = len(free_loose.intersection(row))
            terms = []
            for branch, pins in enumerate(fixed_maps):
                selected = []
                seen = 0
                for n in row:
                    if n in pins:
                        seen |= 1 << pins[n]
                    elif n not in free_loose:
                        selected.append(n + (self.offset if branch and duplicate_spent and n in self.shared else 0))
                terms.append((tuple(selected), seen))
            pieces.append(LocalFactor(tuple(terms), free))
        return tuple(pieces)

    def finite_words(self, width=CAP):
        if len(self.names) > width or self.names != tuple(range(len(self.names))):
            return None
        return _literal_words(self.rows, self.law)

    def parity_end(self):
        adjacent = {h: set() for h in range(len(self.rows))}
        for n in self.spent:
            a, b = self.owners[n]
            adjacent[a].add(b)
            adjacent[b].add(a)
        components = []
        unread = set(adjacent)
        while unread:
            first = min(unread)
            found, queue = {first}, [first]
            while queue:
                nxt = adjacent[queue.pop()] - found
                found.update(nxt)
                queue.extend(sorted(nxt))
            unread -= found
            spent = tuple(b for b in self.spent if self.owners[b][0] in found)
            loose = tuple(b for b in self.loose if self.owners[b][0] in found)
            rank = len(found) - 1
            components.append({"holders": sorted(found), "exact_shared_names": spent, "exact_loose_names": loose,
                               "rank_of_shared_name_incidence": rank,
                               "past_fibre_size_if_this_component_loose_parity_is_even": 1 << (len(spent) - rank),
                               "allowed_loose_words": 1 << max(0, len(loose) - 1)})
        return components

    def total_and_collision(self):
        if self.law == "parity":
            components = self.parity_end()
            c = prod(p["past_fibre_size_if_this_component_loose_parity_is_even"] for p in components)
            support_count = prod(p["allowed_loose_words"] for p in components)
            total, square = support_count * c, support_count * c * c
            assert total == _parity_count(self.masks, self.names, {})
            return total, square, {"rank_by_component": components}
        counts, trace = {}, {}
        for repeated, name in ((False, "ordinary"), (True, "squared")):
            try:
                parts = self.local_factors(({}, {}) if repeated else ({},), duplicate_spent=repeated)
                (counts[name],), trace[name] = _count_factors(parts)
            except CountLimit as failure:
                counts[name] = None
                trace[name] = {"count_censored": failure.record}
        return counts["ordinary"], counts["squared"], trace


@cache
def _literal_words(rows, law):
    names = tuple(_owners(rows))
    assert len(names) <= CAP and names == tuple(range(len(names)))
    masks = tuple(map(_mask, rows))
    return tuple(word for word in range(1 << len(names)) if _valid(word, masks, law))


def _point_count(stage, fixed):
    if stage.law == "parity":
        return _parity_count(stage.masks, stage.names, fixed)
    (num,), _ = _count_factors(stage.local_factors((fixed,)))
    return num


def _parity_loose_counts(stage):
    components = stage.parity_end()
    coeff = prod(part["past_fibre_size_if_this_component_loose_parity_is_even"] for part in components)
    masks = tuple(_extract(_mask(part["exact_loose_names"]), stage.loose) for part in components)
    return tuple(coeff if all(_sign(e & row) == 1 for row in masks) else 0 for e in range(1 << len(stage.loose)))


def _per_holder_loose(stage):
    return tuple((h, tuple(b for b in row if b in stage.loose_set))
                 for h, row in enumerate(stage.rows) if stage.loose_set.intersection(row))


def _coarse_counts(stage):
    groups = _per_holder_loose(stage)
    schemes = tuple((0, 1, 2) if len(bits) > 1 else (0, 1) for h, bits in groups)
    counts = {}
    for assignment in product(*schemes):
        fixed = {}
        for (_, scope), kind in zip(groups, assignment, strict=True):
            fixed.update({n: int(kind == 1 or (kind == 2 and j == 0)) for j, n in enumerate(scope)})
        counts[assignment] = _point_count(stage, fixed)
    converted = tuple(_extract(_mask(b), stage.loose) for h, b in groups)
    def arrangement(e):
        return tuple(0 if e & mask == 0 else 1 if e & mask == mask else 2 for mask in converted)
    return tuple(counts[arrangement(e)] for e in range(1 << len(stage.loose))), len(counts)


def _unequal_witnesses(stage, average):
    groups = _per_holder_loose(stage)
    chosen = {0, (1 << len(stage.loose)) - 1}
    mixed = _extract(_mask(b[0] for _, b in groups), stage.loose)
    chosen.add(mixed)
    for j, (_, group) in enumerate(groups):
        chosen.add(mixed ^ _extract(_mask(group), stage.loose))
        chosen.add(_extract(_mask(group), stage.loose))
    observed = {}
    for w in sorted(chosen):
        try:
            n = _point_count(stage, {q: (w >> j) & 1 for j, q in enumerate(stage.loose)})
        except CountLimit:
            continue
        if n > 0 and n not in observed:
            observed[n] = w
        if len(observed) > 1 or (n > 0 and average is not None and n != average):
            break
    return [{"word": w, "positive_past_count": n} for n, w in sorted(observed.items())]


def _support_from_a_shared_assignment(stage, total, square):
    from pysat.solvers import Minisat22
    shared = [tuple(n for n in r if n in stage.shared) for r in stage.rows]
    tails = {i: s[0] for i, s in enumerate(shared) if len(s) == 1}
    named_tail = set(tails.values())
    core = {i: tuple(b for b in r if b not in named_tail) for i, r in enumerate(shared)
            if len(r) > 1}
    isolated = tuple(i for i, row in enumerate(shared) if not row)
    enough = (len(named_tail) == len(tails) and all(len(s) >= 2 for s in core.values())
              and all(len(stage.rows[h]) > 1 for h in tails))
    bound = 1 << len(stage.loose)
    if enough:
        clauses = [tuple(sign * (name + 1) for name in r) for r in core.values() for sign in (-1, 1)]
        with Minisat22(bootstrap_with=clauses) as solver:
            if solver.solve():
                word = _mask(v - 1 for v in solver.get_model() if v > 0)
                masks = tuple(_mask(row) for row in core.values())
                assert _valid(word, masks, "nae")
                num = bound
                for h in isolated:
                    possible = 1 << len(stage.rows[h])
                    num = (num // possible) * (possible - 2)
                return {"ordinary_support_count": num, "forbidden_loose_word_count": bound - num,
                        "exact_support_certificate": {"shared_witness_word": word,
                            "all_shared_conditions_on_internal_holders": core, "independent_leaf_input_at_each_tail": tails,
                            "entirely_loose_isolated_holders_with_their_own_local_constraint": isolated}}
    lower = (total + (1 << len(stage.spent)) - 1) >> len(stage.spent) if total is not None else 0
    if total is not None and square:
        lower = max(lower, (total * total + square - 1) // square)
    return {"ordinary_support_count": None, "forbidden_loose_word_count": None,
            "ordinary_support_count_bounds": (lower, bound), "forbidden_loose_word_count_bounds": (0, bound - lower),
            "all_word_counts_still_specified_by_integer_factorization": True}


def _loose_weights(stage):
    total, square, solver = stage.total_and_collision()
    literal = stage.finite_words(width=16)
    peek = None
    dense = None
    if len(stage.loose) <= LOOSE_DENSE:
        if stage.law == "parity":
            dense = _parity_loose_counts(stage)
            peek = {"rank_computation": True}
        else:
            try:
                dense, peek = _count_factors(stage.local_factors(({},), retained=stage.loose), stage.loose)
            except CountLimit as failure:
                dense, classes = _coarse_counts(stage)
                peek = {"exact_from_all_loose_holder_permutation_classes": classes, "dense_plan_obstruction": failure.record}
        both = sum(dense), sum(x * x for x in dense)
        assert total is None or total == both[0]
        assert square is None or square == both[1]
        total, square = both
        if literal is not None:
            raw = Counter(_extract(w, stage.loose) for w in literal)
            assert dense == tuple(raw[i] for i in range(len(dense)))
    status = {}
    if dense is not None:
        fibres = Counter(dense)
        support_count = len(dense) - fibres.get(0, 0)
        equal = len(set(fibres) - {0}) == 1 if total else None
        distance = _prob(sum(mass * abs(n * square - n * n * total) for n, mass in fibres.items()), 2 * total * square)
        status = {"representation": "literal_count_for_each_current_word", "counts_by_current_word_int": dense,
                  "squared_counts_by_current_word_int": tuple(n * n for n in dense),
                  "fibre_size_including_zero_to_number_of_loose_words": dict(fibres),
                  "ordinary_support_count": support_count, "forbidden_loose_word_count": len(dense) - support_count,
                  "full_total_variation_U_vs_squared_weights": distance, "positive_fibre_is_flat": equal,
                  "dense_count_execution": peek, "reported_loose_count_cells": len(dense)}
    elif stage.law == "parity":
        count = prod(s["allowed_loose_words"] for s in solver["rank_by_component"])
        status = {"representation": "connected_component_parity_and_constant_fibre_formula",
                  "ordinary_support_count": count, "forbidden_loose_word_count": (1 << len(stage.loose)) - count,
                  "full_total_variation_U_vs_squared_weights": "0", "positive_fibre_is_flat": True,
                  "reported_loose_count_cells": 0}
    else:
        average = F(square, total) if total and square is not None else None
        witness = _unequal_witnesses(stage, average)
        unequal = len(witness) > 1 or any(average is not None and w["positive_past_count"] != average for w in witness)
        status = {"representation": "factored_integer_count_for_every_loose_word",
                  "evaluate_a_count": "Fix the written values of once-held names and sum the product of the stored NAE row indicators over all twice-held names.",
                  "holder_symmetry": [{"holder": h, "once_held_names": ns,
                                      "multiplicities_for_all_zero_all_one_mixed": (1, 1, (1 << len(ns)) - 2)}
                                     for h, ns in _per_holder_loose(stage)],
                  "total_current_word_cells_described_by_factorization": 1 << len(stage.loose),
                  "certified_unequal_by_positive_counts_or_size_biased_mean": unequal,
                  "exact_positive_fibre_witnesses": witness, "positive_fibre_is_flat": False if unequal else None,
                  "size_biased_mean_past_count": str(average) if average is not None else None,
                  "full_total_variation_U_vs_squared_weights": None, "reported_loose_count_cells": 0,
                  **_support_from_a_shared_assignment(stage, total, square)}
    chance = {"N_complete_words": total, "W_sum_squared_past_counts": square,
              "all_plus_erasure_probability": _prob(square, (1 << len(stage.spent)) * total)
              if total and square is not None else None,
              "collision_two_independent_ordinary_words_accept": _prob(square, total ** 2)
              if total and square is not None else None}
    for label, source in (("all_other_character_ports_total", "all_plus_erasure_probability"),
                          ("collision_mismatched_loose_words", "collision_two_independent_ordinary_words_accept")):
        chance[label] = str(1 - F(chance[source])) if chance[source] is not None else None
    if total and square is None:
        low = max(total, (total * total + (1 << len(stage.loose)) - 1) >> len(stage.loose))
        high = min(total ** 2, total * (1 << len(stage.spent)))
        chance["unknown_W_proved_integer_bounds"] = (low, high)
        chance["clean_chance_bounds"] = tuple(_prob(x, (1 << len(stage.spent)) * total) for x in (low, high))
        chance["collision_accept_chance_bounds"] = tuple(_prob(x, total * total) for x in (low, high))
    symmetry = stage.law == "nae" or all(len(row) % 2 == 0 for row in stage.rows)
    if dense is not None and symmetry:
        assert dense == dense[::-1]
    return {**status, **chance, "normalizer_execution": solver,
            "ordinary_word_rule": "n(e)/N; squared count: n(e)^2/W; matrix amplitudes require an additional preparation.",
            "whole_physical_word_complement_preserves_every_local_relation": symmetry,
            "checked_complement_on_all_materialized_loose_count_pairs": bool(dense is not None and symmetry),
            "complete_law_has_no_probability_if_total_is_zero": total == 0,
            "empty_loose_string_present_when_closed_if_N_is_positive": bool(total) and not stage.loose}, dense


def _corank_gram(stage, marks, coherent):
    if coherent:
        assert set(marks) <= stage.loose_set
        units = stage.loose
        info = stage.parity_end()
        rows = tuple(_mask(c["exact_loose_names"]) for c in info)
        volume = prod(c["past_fibre_size_if_this_component_loose_parity_is_even"] for c in info) ** 2
    else:
        units, rows, volume = stage.names, stage.masks, 1
    values = [[] for _ in range(1 << len(marks))]
    offsets = [_mask(b for j, b in enumerate(marks) if bit >> j & 1) for bit in range(len(values))]
    for i, x in enumerate(offsets):
        fixed = {b: int(bool(x & (1 << b))) for b in marks}
        n = _parity_count(rows, units, fixed) * volume
        values[i] = [n if all(_sign((x ^ y) & row) == 1 for row in rows) else 0 for y in offsets]
    return tuple(tuple(r) for r in values)


def _outer_gram(groups, dim):
    out = [[0] * dim for _ in range(dim)]
    for vector in groups.values():
        nz = [(i, int(v)) for i, v in enumerate(vector) if v]
        for i, a in nz:
            for j, b in nz:
                out[i][j] += a * b
    return tuple(tuple(r) for r in out)


def _direct_full_gram(stage, marks, literal):
    # Preserve every other physical mark, including the actual past for the unread trace.
    outside = stage.namemask ^ _mask(marks)
    size = 1 << len(marks)
    groups = defaultdict(lambda: [0] * size)
    for w in literal:
        groups[w & outside][_extract(w, marks)] += 1
    return _outer_gram(groups, size)


def _loose_gram(stage, marks, counts):
    packed = tuple(stage.loose.index(b) for b in marks)
    outside = ((1 << len(stage.loose)) - 1) ^ _mask(packed)
    size = 1 << len(marks)
    groups = defaultdict(lambda: [0] * size)
    for w, count in enumerate(counts):
        if count:
            groups[w & outside][_extract(w, packed)] += int(count)
    return _outer_gram(groups, size)


def _counted_gram(stage, marks, coherent):
    if stage.law == "parity":
        return _corank_gram(stage, marks, coherent), {"method": "binary rank and translation"}
    dim, work, note = 1 << len(marks), [], None
    sites = tuple(sorted({h for n in marks for h in stage.owners[n]}))
    fixed = dict.fromkeys(marks, 0)
    initial = stage.local_factors((fixed, fixed), duplicate_spent=coherent)
    keep = tuple(sorted({v for h in sites for v in initial[h].scope}))
    unmarked = tuple(f for h, f in enumerate(initial) if h not in sites)
    already = {v for f in unmarked for v in f.scope}
    # A physically shared variable can have both holders in the marked group.
    # Its integration still needs both values even if the outside factors omit it.
    units = tuple(LocalFactor((((v,), 3),)) for v in keep if v not in already)
    try:
        environment, env_meta = _count_factors(unmarked + units, keep)
        env_tensor = np.asarray(environment, dtype=np.int64 if max(environment) < 1 << 63 else object).reshape((2,) * len(keep)).transpose()
    except CountLimit as exc:
        env_tensor, env_meta = None, {"retained_environment_too_wide": exc.record}
    values = [[0] * dim for _ in range(dim)]
    scalar_cache = {}
    for x in range(dim):
        for y in range(x, dim):
            px, py = ({k: (word >> i) & 1 for i, k in enumerate(marks)} for word in (x, y))
            factors = stage.local_factors((px, py), duplicate_spent=coherent)
            try:
                selected = tuple(factors[h] for h in sites)
                if selected not in scalar_cache:
                    if env_tensor is None:
                        (score,), note = _count_factors(factors)
                    else:
                        child = tuple(f.values({}) for f in selected)
                        score = int(_contract(((keep, env_tensor), *child), keep,
                                              sum_terms_bound=1 << len(keep)).sum())
                    scalar_cache[selected] = score
                weight = scalar_cache[selected]
            except CountLimit as limit:
                return None, {"first_impossible_matrix_cell": (x, y), "count_censored": limit.record,
                              "circuit": "Actual row products, pinned marked bits, same unmarked loose bits; repeat spent names iff clean.",
                              "already_counted_cells": len(work)}
            values[x][y] = values[y][x] = weight
            work.append(weight)
    return tuple(tuple(r) for r in values), {
        "method": "exact integer elimination", **(note if note is not None else env_meta),
        "reused_outside_contraction": env_tensor is not None, "counted_upper_triangle": len(work),
        "distinct_marked_local_factor_patterns": len(scalar_cache)}


def _gram_pair(stage, marks, dense):
    retained, dmeta = _counted_gram(stage, marks, False)
    literal = stage.finite_words(width=16)
    if retained is not None and literal is not None:
        assert retained == _direct_full_gram(stage, marks, literal)
        dmeta["independent_literal_exterior_slices"] = True
    if dense is not None:
        erased = _loose_gram(stage, marks, dense)
        cmeta = {"method": "sum the exterior slices of the full n(e) amplitude table"}
        if literal is not None:
            # The second method contracts two separately named copies of the actual spent bits.
            checked, raw = _counted_gram(stage, marks, True)
            assert erased == checked
            cmeta["independent_duplicate_past_contraction"] = raw
    else:
        erased, cmeta = _counted_gram(stage, marks, True)
    return (retained, dmeta), (erased, cmeta)


def _clean_instrument(stage, stats):
    literal = stage.finite_words(width=16)
    num = stats["N_complete_words"]
    k = len(stage.spent)
    expected = stats["W_sum_squared_past_counts"]
    summary = {"spent_bits_in_character_order": stage.spent, "current_name_order": stage.loose,
               "clean_probability": stats["all_plus_erasure_probability"], "other_ports_total": stats["all_other_character_ports_total"],
               "fully_retained_orthogonal_past_tag_each_port_probability": _prob(1, 1 << k) if num else None,
               "returns_every_tag_coherently": "A true inverse returning the entire path tag makes the clean formula applicable.",
               "no_choice_of_character_is_an_ordinary_growth_event": True}
    if literal is None or num is None:
        return {**summary, "representation": "exact_character_formula",
                "all_ports": "a_r(e)=sum_s(-1)^(r·s) A(s,e); P(r)=sum_e a_r(e)^2/(2^k N). Zero has no normalized state.",
                "orthogonal_partial_tag_formula": "Partition s by the physically held tag g; retain one signed a_(r,g) vector per tag. Ignore the tag by summing their projectors.",
                "ignore_all_ports": "Orthogonality of the 2^k characters returns the unread state D."}
    depth, side = 1 << k, 1 << len(stage.loose)
    grid = np.zeros((depth, side), dtype=np.int64)
    for w in literal:
        grid[_extract(w, stage.spent), _extract(w, stage.loose)] = 1
    rows = grid.copy()
    for step in range(k):
        half = 1 << step
        blocks = rows.reshape(-1, 2 * half, side)
        a, b = blocks[:, :half, :].copy(), blocks[:, half:, :].copy()
        blocks[:, :half, :] = a + b
        blocks[:, half:, :] = a - b
    norms = [int(val) for val in (rows * rows).sum(axis=1)]
    assert sum(norms) == depth * num and norms[0] == expected
    plain = []
    for r, w in enumerate(norms):
        # A signed amplitude vector is recorded before normalizing, and its null case is preserved.
        nonzero = [(int(e), int(rows[r, e])) for e in np.flatnonzero(rows[r])]
        plain.append({"character": r, "probability_num": w, "signed_open_amplitudes": nonzero,
                      "normalizing_square_for_conditional_state": w or None})
    partial = None
    if k:
        parts = grid.reshape(-1, 2, side).sum(axis=0)
        component_norms = [int(v) for v in (parts * parts).sum(axis=1)]
        assert num <= sum(component_norms) <= expected
        partial = {"one_retained_tag_name": stage.spent[0], "clean_norm_per_tag_value": component_norms,
                   "clean_probability_when_tag_ignored": _prob(sum(component_norms), depth * num),
                   "zero_then_one_tag_clean_integer_vectors": [tuple(map(int, part)) for part in parts]}
    return {**summary, "representation": "complete_signed_character_instrument_on_this_anchor",
            "every_signed_character_port": plain, "all_ports_probability_common_denominator": depth * num,
            "one_spent_bit_tag_control": partial}


def _setting_table(matrix):
    dim = len(matrix)
    assert dim == 8
    den = sum(matrix[i][i] for i in range(dim))
    if not den:
        return None
    rows, correlations = {}, {}
    for setting in SETTINGS:
        changed = _mask(i for i, q in enumerate(setting) if q == "X")
        moments = []
        for enable in range(8):
            x, z = enable & changed, enable & ~changed
            moments.append(sum(_sign(w & z) * matrix[w][w ^ x] for w in range(8)))
        values = [sum(_sign(answer & active) * moment for active, moment in enumerate(moments)) for answer in range(8)]
        assert sum(values) == 8 * den and min(values) >= 0
        divisor = gcd(8 * den, *values)
        rows[setting] = {"numerators": [v // divisor for v in values], "denominator": 8 * den // divisor}
        correlations[setting] = F(moments[7], den)
    score = correlations[TERMS[0]] - sum(correlations[t] for t in TERMS[1:])
    legacy = {sign: correlations[TERMS[0]] + sign * sum(correlations[t] for t in TERMS[1:]) for sign in (-1, 1)}
    return {"every_joint_probability": rows, "expectations": {q: str(v) for q, v in correlations.items()},
            "signed_M_XXX_minus_three_XZZ": str(score), "absolute_signed_M": str(abs(score)),
            "signed_M_exceeds_local_bound_two": abs(score) > 2,
            "private_common_sign_alternatives": {str(s): str(v) for s, v in legacy.items()},
            "private_maximum_absolute_value": str(max(map(abs, legacy.values())))}


def _matrix_record(matrix, meta, expected):
    if matrix is None:
        return {"status": "count_censored", "execution": meta}
    norm = sum(matrix[i][i] for i in range(len(matrix)))
    assert expected is None or expected == norm
    result = {"status": "exact" if norm else "empty_support", "integer_matrix": matrix, "matrix_denominator": norm or None,
              "execution": meta, "settings_and_scores": _setting_table(matrix)}
    if norm:
        diag = tuple(tuple(matrix[i][i] if i == j else 0 for j in range(len(matrix))) for i in range(len(matrix)))
        diagonal_questions = _setting_table(diag)
        assert diagonal_questions["every_joint_probability"]["XXX"] == {"numerators": [1] * 8, "denominator": 8}
        result["diagonal_control_with_same_ordinary_weights"] = {
            "ordinary_ZZZ": diagonal_questions["every_joint_probability"]["ZZZ"],
            "XXX": diagonal_questions["every_joint_probability"]["XXX"],
            "local_X_plus_marginal_each": ["1/2"] * 3, "signed_M": diagonal_questions["signed_M_XXX_minus_three_XZZ"],
            "specified_classical_joint_measurement": "sample the Z triple once and independently sample each X answer fairly"}
    return result


def _read_triple(stage, marks, stats, dense):
    if marks in stage.measurements:
        return stage.measurements[marks]
    assert len(marks) == 3 and len(set(marks)) == 3 and set(marks) <= stage.loose_set
    d, c = _gram_pair(stage, marks, dense)
    retained = _matrix_record(*d, stats["N_complete_words"])
    erased = _matrix_record(*c, stats["W_sum_squared_past_counts"])
    if stats["whole_physical_word_complement_preserves_every_local_relation"]:
        for model in (retained, erased):
            if "integer_matrix" in model:
                m = model["integer_matrix"]
                assert all(m[i][j] == m[i ^ 7][j ^ 7] for i in range(8) for j in range(8))
                model["full_matrix_commutes_with_complementing_all_three_named_marks"] = True
    comparisons = {}
    if retained["status"] == erased["status"] == "exact":
        dr, cr = (r["settings_and_scores"]["every_joint_probability"] for r in (retained, erased))
        for setting in SETTINGS:
            a, b = dr[setting], cr[setting]
            tv = sum(abs(F(x, a["denominator"]) - F(y, b["denominator"]))
                     for x, y in zip(a["numerators"], b["numerators"], strict=True)) / 2
            comparisons[setting] = str(tv)
        support = [i for i, value in enumerate(retained["integer_matrix"]) if value[i]]
        assert support == [i for i, value in enumerate(erased["integer_matrix"]) if value[i]]
        status = "exact"
    else:
        support = None
        status = "incomplete"
    report = {"physical_triple_in_bit_order": marks, "status": status, "unread_past_D": retained, "pure_squared_count": erased,
              "projected_possible_Z_words": support, "TV_D_vs_pure_count_each_offered_context": comparisons,
              "max_TV_only_over_this_triple_contexts": str(max(map(F, comparisons.values()))) if comparisons else None}
    stage.measurements[marks] = report
    return report


@cache
def _strategies():
    table = []
    for s in range(64):
        outcomes = tuple(sum(((s >> (2 * i + int(q == "X"))) & 1) << i for i, q in enumerate(setting)) for setting in SETTINGS)
        table.append(outcomes)
    design = tuple(tuple(int(assignment[k] == o) for assignment in table) for k in range(8) for o in range(8))
    return tuple(table), design


def _signed_classical_bounds():
    strategies, _ = _strategies()
    cuts = {}
    columns = tuple(SETTINGS.index(s) for s in TERMS)
    for signs in product((-1, 1), repeat=3):
        scores = [sum(w * _sign(row[k]) for w, k in zip((1, *signs), columns, strict=True)) for row in strategies]
        bound = max(map(abs, scores))
        cuts["".join("+" if v > 0 else "-" for v in signs)] = {"full_correlation_bound_absolute": bound,
            "one_deterministic_strategy_attaining_the_bound": max(range(64), key=lambda r: abs(scores[r])),
            "number_of_checked_strategies": len(scores)}
    return cuts


def _exact_linear_solution(design, target, selected):
    values = [[F(row[c]) for c in selected] + [y] for row, y in zip(design, target, strict=True)]
    pivots, rank = {}, 0
    for c in range(len(selected)):
        r = next((i for i in range(rank, len(values)) if values[i][c]), None)
        if r is None:
            continue
        values[r], values[rank] = values[rank], values[r]
        factor = values[rank][c]
        values[rank] = [v / factor for v in values[rank]]
        for i, a in enumerate(values):
            if i != rank and a[c]:
                values[i] = [x - a[c] * y for x, y in zip(a, values[rank], strict=True)]
        pivots[c] = rank
        rank += 1
    if any(not any(row[:-1]) and row[-1] for row in values):
        return None
    exact = {sel: values[pivots[j]][-1] for j, sel in enumerate(selected) if j in pivots and values[pivots[j]][-1]}
    wanted = [sum(exact[c] * row[c] for c in exact) for row in design]
    return exact if all(v >= 0 for v in exact.values()) and wanted == target else None


def _common_certificate(rows):
    from scipy.optimize import linprog
    _, design = _strategies()
    target = [F(v, rows[s]["denominator"]) for s in SETTINGS for v in rows[s]["numerators"]]
    values = np.array(design, dtype=float)
    result = linprog(np.zeros(64), A_eq=values, b_eq=[float(v) for v in target], bounds=(0, None), method="highs")
    if result.success:
        eligible = tuple(i for i, w in enumerate(result.x) if w > 1e-11)
        rational = _exact_linear_solution(design, target, eligible)
        if rational is not None:
            assert sum(rational.values()) == 1
            return {"full_common_joint_exists": True, "checked_rows": 64,
                    "weights_by_local_strategy_id": {i: str(v) for i, v in rational.items()}}
    dual = linprog([float(v) for v in target], A_ub=-values.T, b_ub=np.zeros(64), bounds=(-1, 1), method="highs")
    assert dual.success and dual.fun < 0, "floating search gave no recheckable certificate"
    r = [F(float(v)).limit_denominator(100000) for v in dual.x]
    columns = tuple(zip(*design, strict=True))
    cube = [sum(x * y for x, y in zip(col, r, strict=True)) for col in columns]
    shift = max(F(0), -min(cube))
    if shift:
        for k in range(8):
            r[k] += shift
    checked = [sum(x * y for x, y in zip(col, r, strict=True)) for col in columns]
    score = sum(x * y for x, y in zip(target, r, strict=True))
    assert min(checked) >= 0 and score < 0
    return {"full_common_joint_exists": False, "min_over_all_sixty_four_strategies": str(min(checked)),
            "signed_witness_value_on_actual_table": str(score),
            "coefficients_by_setting_and_answer_mask": {s: [str(v) for v in r[i * 8:(i + 1) * 8]]
                                                         for i, s in enumerate(SETTINGS)}}


def _isolated_single_distinction_fixture(law):
    rows = ((0, 1, 2),)
    allowed = _literal_words(rows, law)
    sectors = defaultdict(list)
    for word in allowed:
        sectors[_extract(word, (1, 2))].append(word & 1)
    den = 2 * len(allowed)
    outcomes = {}
    for sign, encoded in (("plus", 0), ("minus", 1)):
        amplitudes = {e: sum(_sign(encoded & b) for b in bits) for e, bits in sorted(sectors.items())}
        numerator = sum(x ** 2 for x in amplitudes.values())
        outcomes[sign] = {"probability": _prob(numerator, den), "conditional_signed_amplitudes_by_remaining_named_word": amplitudes,
                          "conditional_normalization_square": numerator or None}
    assert sum(F(row["probability"]) for row in outcomes.values()) == 1
    return {"erased_name": 0, "readable_names": (1, 2), "both_actual_supplied_character_outcomes": outcomes,
            "this_is_a_supplied_control_with_ordinary_growth_turned_off": True}


def _source_fixture(case_by_key):
    comparisons = {}
    for law in LAWS:
        case = case_by_key[("single3/1/0", law)]
        reached = case["outcomes"][0]["new"]
        assert [row["places"][0] for row in reached] == [0, 1, 2] and all(row["fresh"] == 2 for row in reached)
        marks, spectators = (tuple(row["places"][i] for row in reached) for i in (1, 2))
        s = Stage(_sorted_rows(case["stages"][1]), law)
        stats, dense = _loose_weights(s)
        table = _read_triple(s, marks, stats, dense)
        for method in ("unread_past_D", "pure_squared_count"):
            row = table[method]
            row["exact_common_joint"] = _common_certificate(row["settings_and_scores"]["every_joint_probability"])
        erasure = _clean_instrument(s, stats)
        ignored = [[0] * 8 for _ in range(8)]
        for port in erasure["every_signed_character_port"]:
            signed = dict(port["signed_open_amplitudes"])
            reduced = _loose_gram(s, marks, [signed.get(e, 0) for e in range(1 << len(s.loose))])
            for i in range(8):
                for j in range(8):
                    ignored[i][j] += reduced[i][j]
        raw_d = table["unread_past_D"]["integer_matrix"]
        assert all(ignored[i][j] == (1 << len(s.spent)) * raw_d[i][j] for i in range(8) for j in range(8))
        rename = dict(zip(s.names, reversed(s.names), strict=True))
        renamed = Stage(tuple(tuple(rename[b] for b in row) for row in s.rows), law)
        alternate_stats, alternate_dense = _loose_weights(renamed)
        for i, n in enumerate(dense):
            mapped = _mask(renamed.loose.index(rename[b]) for bit, b in enumerate(s.loose) if i >> bit & 1)
            assert alternate_dense[mapped] == n
        alternate = _read_triple(renamed, tuple(rename[b] for b in marks), alternate_stats, alternate_dense)
        for which in ("unread_past_D", "pure_squared_count"):
            assert table[which]["integer_matrix"] == alternate[which]["integer_matrix"]
        comparisons[law] = {"defined_by_paid_children": reached, "distinct_measured_holders": tuple(r["holder"] for r in reached),
                            "read_marks": marks, "unread_once_held_spectator_marks": spectators,
                            "true_stage_roster": s.rows, "complete_loose_counts": stats, "three_reader_results": table,
                            "complete_character_and_tag_outcomes": erasure,
                            "all_ports_ignored_integer_matrix": ignored,
                            "complete_character_mixture_recovers_unread_D_on_every_matrix_cell": True,
                            "reversed_physical_name_order_transport_and_both_reductions_verified": rename,
                            "private_script_one_mark_supplied_erasure": _isolated_single_distinction_fixture(law)}
    return {"same_least_loose_bit_per_named_child_choice": True, "cases_by_law": comparisons,
            "literal_private_script_first_three_raw_spent_names": (0, 1, 2),
            "private_common_sign_formula": "max(abs(E(XXX)+(E(XZZ)+E(ZXZ)+E(ZZX))), abs(E(XXX)-(E(XZZ)+E(ZXZ)+E(ZZX))))",
            "classical_bound_of_every_choice_of_the_three_relative_signs": _signed_classical_bounds(),
            "strategy_address": "strategy bit 2*i is Z outcome; bit 2*i+1 is X outcome, with 0 denoting +1",
            "private_source_identification_sha256": PRIVATE_WAYS_SHA}


def _roster_inventories(rows, origin, old_marks):
    owners = _owners(rows)
    loose, spent = (tuple(n for n, sites in owners.items() if len(sites) == cardinality) for cardinality in (1, 2))
    loose_mask = set(loose)
    holds = tuple((i, tuple(sorted(loose_mask.intersection(support)))) for i, support in enumerate(rows))
    live = tuple(item for item in holds if item[1])
    eligible = []
    for i, owned in holds:
        if len(owned) >= 3:
            eligible.append({"holder": i, "actual_support": rows[i], "holder_width": len(rows[i]),
                             "once_held_names_in_holder": owned, "least_three_loose_names": owned[:3],
                             "marks_of_original_holder_zero": i == 0, "holder_first_exists_after_source": i >= len(origin),
                             "source_holder_other_than_zero": 0 < i < len(origin)})
    address = tuple({"holder": h, "least_loose_name": names[0]} for h, names in live[:3])
    fate = tuple({"name": m, "holders": owners.get(m, ()),
                  "ordinary_status": "still_loose" if m in loose_mask else "retained_but_twice_held" if m in owners else "missing"}
                 for m in old_marks)
    return {"whole_named_rows": rows, "total_holdings": len(rows), "number_of_physically_written_names": len(owners),
            "loose_names_in_order": loose, "spent_names_in_order": spent,
            "live_holders_and_their_loose_names_in_order": live, "all_single_holder_three_loose_choices": eligible,
            "one_three_holder_choice": address if len(address) == 3 else None,
            "three_holder_status": "present" if len(address) == 3 else "fewer_than_three_actual_live_holders",
            "original_choice_of_holder_zero": old_marks,
            "literal_original_three_can_be_read": len(old_marks) == 3 and all(m in loose_mask and m in rows[0] for m in old_marks),
            "original_physical_mark_fates": fate}


def _validate_outcomes(case, *, independent=False):
    stages = tuple(map(_sorted_rows, case["stages"]))
    validations = []
    for i, outcome in enumerate(case["outcomes"]):
        old = stages[i]
        owners = _owners(old)
        dealt = set(n for n, h in owners.items() if len(h) == 1)
        if outcome["status"] in ("grown", "closed"):
            new = stages[i + 1]
            assert new[:len(old)] == old
            assert len(new) - len(old) == outcome["births"] == len(outcome["new"])
            actual = _owners(new)
            paid = []
            for entry in outcome["new"]:
                h, p, f = entry["holder"], entry["parents"], entry["fresh"]
                names = tuple(entry["places"])
                assert new[h] == names and len(names) == p + f
                spent = tuple(b for b in names if b in owners)
                fresh = tuple(b for b in names if b not in owners)
                assert len(spent) == p and len(fresh) == f and set(spent) <= dealt
                assert all(actual[b] == (h,) for b in fresh)
                assert sorted(owners[b][0] for b in spent) == entry["parent_names"]
                paid.extend(spent)
            assert Counter(paid) == Counter(dealt)
            assert not (dealt & {b for b, h in actual.items() if len(h) == 1})
            validations.append({"age_from": i, "age_to": i + 1, "all_old_rows_retained": True,
                                "all_old_loose_names_paid_in_this_ordinary_round": sorted(paid), "raw_outcome": outcome})
        else:
            assert i == len(stages) - 1
            validations.append({"age_from": i, "age_to": None, "raw_outcome": outcome})
        if independent:
            engine, end = _engine()
            # This loop only replays the small built histories. It never probes an archived explosive cap.
            state = engine.S.from_junctions(old)
            law = case["law"]
            rule = engine.parity_rule(engine.F.fewest) if law == "parity" else engine.nae_rule(engine.F.fewest)
            planned = end.step(end.from_stars(old), law, 48)
            result = state.step(rule, None)
            if outcome["status"] == "stall":
                assert result is None and planned.status == "stall"
            elif outcome["status"] == "already closed":
                assert planned.status == "closed" and result["new"] == 0
            else:
                assert _sorted_rows(state.bits_of) == stages[i + 1]
                assert planned.status == "extend" and result["new"] == outcome["births"]
                assert Counter((tuple(r["parent_names"]), r["fresh"], r["demand"]) for r in outcome["new"]) == +                    Counter((parents, fresh, demand) for parents, fresh, demand in zip(planned.parents, planned.fresh, planned.demand, strict=True))
            validations[-1]["matched_actual_paid_growth_engine_and_its_independent_end_operator"] = True
    if case["stop"] == "already closed":
        assert not any(len(h) == 1 for h in _owners(stages[-1]).values())
    return validations


def _vote_index(archive):
    result = defaultdict(list)
    for vote in archive["votes"]:
        result[vote["case"], vote["law"]].append(vote)
    return result


def _audit_original(stage, marks, record, table):
    avail = set(marks) <= stage.loose_set
    if "table" not in record:
        return {"status": "previous_auditor_count_censored", "earlier_evaluator": record, "marks": marks,
                "admitted_by_loose_only_observer": avail}
    expected = tuple(tuple(table["gram"][i * 8 + j] * record["physical_unit"] for j in range(8)) for i in range(8))
    actual, proof = _counted_gram(stage, marks, False)
    if actual is not None:
        assert expected == actual
    data = _setting_table(expected)
    assert data["signed_M_XXX_minus_three_XZZ"] == str(F(table["M"]))
    for old in table["rows"]:
        label = "".join("XZ"[q] for q in old["settings"])
        values = data["every_joint_probability"][label]
        assert [F(x, old["denominator"]) for x in old["numerators"]] == [F(y, values["denominator"]) for y in values["numerators"]]
    return {"status": "exact_archived_score", "admitted_by_loose_only_observer": avail, "original_marks": marks,
            "archived_normalized_integer_gram_and_physical_unit": record,
            "original_score": table["M"], "original_common_joint_exists": table["common"],
            "independent_replay_execution": proof, "physically_counted_gram_independently_matched": actual is not None,
            "every_archived_probability_and_the_signed_score_compared_exactly": True}


@cache
def _canonical_verdict(width, words):
    variables = tuple(f"x{i}" for i in range(width))
    denied = sorted(set(range(1 << width)) - set(words))
    clauses = [" ".join(("~" if i >> j & 1 else "") + v for j, v in enumerate(variables)) for i in denied]
    if not clauses:
        clauses = [v + " ~" + v for v in variables]
    invocation = (sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
                  "--loops", *variables[:-1], "--contact", variables[-1], "--json")
    proc = subprocess.run(invocation, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}, capture_output=True, text=True)
    if width < 3:
        assert proc.returncode == 2 and "at least two loops" in proc.stderr
        return False
    proc.check_returncode()
    verdict = json.loads(proc.stdout)
    assert set(verdict["allowed"]) == {_bits(w, range(width)) for w in words}
    return verdict["is_knot"]


def _holder_projection(stage, holder, verify_with_cli=False):
    support = stage.rows[holder]
    if stage.law == "parity":
        included = [w for w in range(1 << len(support)) if _parity_count(
            stage.masks, stage.names, {b: (w >> i) & 1 for i, b in enumerate(support)})]
    else:
        from pysat.solvers import Minisat22
        clauses = [tuple(sign * (b + 1) for b in row) for row in stage.rows for sign in (-1, 1)]
        with Minisat22(bootstrap_with=clauses) as solver:
            included = [w for w in range(1 << len(support)) if solver.solve(
                assumptions=[(1 if w >> i & 1 else -1) * (b + 1) for i, b in enumerate(support)])]
    removed = [len({w & ~(1 << i) for w in included}) for i in range(len(support))]
    k1, k2, k3 = len(included) < 1 << len(support), all(x == 1 << (len(support) - 1) for x in removed), bool(included)
    target = [w for w in range(1 << len(support)) if _valid(w, ((1 << len(support)) - 1,), stage.law)]
    gate = len(support) >= 3 and k1 and k2 and k3
    if verify_with_cli:
        assert _canonical_verdict(len(support), tuple(included)) == gate
    return {"named_holder": holder, "full_support_marks_in_order": support, "full_projected_word_list": included,
            "one_deleted_projection_sizes": removed, "full_written_law_realized_on_projection": included == target,
            "K1": k1, "K2": k2, "K3": k3, "enrolled_knot_gate_with_arity_at_least_three": gate,
            "independent_canonical_CNF_projection_replay": verify_with_cli}


def _symmetry_check(stage, site, marks, known, dense):
    owner = stage.owners[marks[0]]
    assert all(stage.owners[m] == owner == (site["holder"],) for m in site["once_held_names_in_holder"])
    # Swapping any two of these named variables preserves their only row and fixes every other row.
    for x, y in combinations(site["once_held_names_in_holder"], 2):
        assert all((x in row) == (y in row) for row in stage.rows)
    evidence = {"all_triples_permuted_within_the_exact_written_holder": True,
                "number_of_different_three_loose_subsets": len(tuple(combinations(site["once_held_names_in_holder"], 3)))}
    if dense is not None and len(site["once_held_names_in_holder"]) > 3:
        other = (*marks[:-1], site["once_held_names_in_holder"][-1])
        s = _read_triple(stage, other, known, dense)
        j = stage.measurements[marks]
        for which in ("unread_past_D", "pure_squared_count"):
            assert s[which]["integer_matrix"] == j[which]["integer_matrix"]
        evidence["explicit_alternative_triple_identical_on_both_reduced_matrices"] = other
    return evidence


def _quantitative_stage(roster, law, votes, tables, age, *, core=False):
    stage = Stage(roster["whole_named_rows"], law)
    weight, dense = _loose_weights(stage)
    report = {"whole_current_weights": weight, "same_roster_normalized_erasure_and_collision": _clean_instrument(stage, weight),
              "single_holder_results": [], "three_holder_result": None, "auditor_original_and_other_fixed_marks": []}
    projected = {i: _holder_projection(stage, i, verify_with_cli=True) for i in range(len(stage.rows))} if core else {}
    if core:
        report["all_whole_holder_projections"] = projected
    for site in roster["all_single_holder_three_loose_choices"]:
        marks = site["least_three_loose_names"]
        read = _read_triple(stage, marks, weight, dense)
        symmetry = _symmetry_check(stage, site, marks, weight, dense)
        holder = site["holder"]
        projection = projected[holder] if holder in projected else _holder_projection(stage, holder)
        report["single_holder_results"].append({**site, "projected_full_holder_feasibility": projection,
                                                "read": read, "within_holder_mark_symmetry": symmetry})
    address = roster["one_three_holder_choice"]
    if address:
        read = _read_triple(stage, tuple(x["least_loose_name"] for x in address), weight, dense)
        report["three_holder_result"] = {"distinct_reader_addresses": address, "read": read}
    else:
        report["three_holder_result"] = {"status": "ineligible", "explanation": roster["three_holder_status"]}
    for v in votes:
        if v.get("ineligible"):
            report["auditor_original_and_other_fixed_marks"].append({"role": v["role"], "trial": v["trial"], "status": "ineligible"})
            continue
        j = age - v["anchor_age"]
        if j < 0 or j >= len(v["records"]):
            continue
        record = v["records"][j]
        saved = tables[record["table"]] if "table" in record else None
        if core:
            audit = _audit_original(stage, tuple(v["marks"]), record, saved)
        else:
            audit = {"status": "exact_archived_score" if saved else "previous_auditor_count_censored",
                     "earlier_evaluator": record, "original_score": saved["M"] if saved else None,
                     "original_common_joint_exists": saved["common"] if saved else None,
                     "admitted_by_loose_only_observer": set(v["marks"]) <= stage.loose_set}
        report["auditor_original_and_other_fixed_marks"].append({"role": v["role"], "trial": v["trial"], "holder": v["holder"],
                                                               "original_or_fixed_marks": v["marks"], **audit})
    addressed = [r["read"] for r in report["single_holder_results"]]
    if "read" in report["three_holder_result"]:
        addressed.append(report["three_holder_result"]["read"])
    measured = [F(r["TV_D_vs_pure_count_each_offered_context"]["ZZZ"]) for r in addressed if r["status"] == "exact"]
    report["largest_ordinary_ZZZ_TV_for_these_named_projections_only"] = str(max(measured)) if measured else None
    report["addressed_triples_and_entire_contexts_compared"] = {"operative_triples": len(addressed), "exact_both_weights": len(measured),
                                                              "omitted_because_of_count_cap": len(addressed) - len(measured)}
    return report


def _summarize_structural_row(out, case, ages):
    for age, stage in enumerate(ages):
        key = f'{case["label"]}/{case["n"]}/{case["law"]}/{age}'
        current = out.setdefault(key, Counter())
        current["sources_in_this_stratum"] += 1
        if not stage.get("reached"):
            current[stage["status"]] += 1
            continue
        current["reached"] += 1
        sites = stage["all_single_holder_three_loose_choices"]
        current["reached_sources_with_a_single_holder_choice"] += bool(sites)
        current["number_of_single_holder_triples"] += len(sites)
        current["reached_with_three_holder_choice"] += bool(stage["one_three_holder_choice"])
        current["original_holder_zero_three_names_still_loose"] += stage["literal_original_three_can_be_read"]


def _bound_fixed_panel(chosen):
    summary = {}
    for case, laws in chosen.items():
        row = {}
        for law, report in laws.items():
            cases = {}
            for age, result in report["bounded_numerical_stages"].items():
                if "whole_current_weights" not in result:
                    cases[age] = {"status": result["status"], "actual_stage_denominator": 0}
                    continue
                r = [t["read"] for t in result["single_holder_results"]]
                third = result["three_holder_result"]
                combined = r + ([third["read"]] if "read" in third else [])
                versions = {}
                for state in ("unread_past_D", "pure_squared_count"):
                    positive, exact = 0, 0
                    for c in combined:
                        if c[state]["status"] == "exact":
                            positive += c[state]["settings_and_scores"]["signed_M_exceeds_local_bound_two"]
                            exact += 1
                    versions[state] = {"exact_addressed_triples": exact,
                                       "censored_addressed_triples": len(combined) - exact,
                                       "bounds_on_number_above_two_in_this_fixed_set_of_operable_readers":
                                           [positive, positive + len(combined) - exact]}
                cases[age] = {"denominator_addressed_triples_in_both_modes": len(combined), "exact_denominator_by_weight": versions}
            row[law] = cases
        summary[case] = row
    return summary


def _archive_runs(archive):
    votes = _vote_index(archive)
    built, roster_inventory, panel, denominators = {}, {}, {}, {}
    core_cases = tuple(c for c in archive["cases"] if c["mode"] == "built")
    if not all(len(c["stages"]) <= 7 for c in archive["cases"]):
        raise ValueError("unexpected stored stage beyond age six")
    for c in archive["cases"]:
        cid, law = c["id"], c["law"]
        core = c["mode"] == "built"
        quantitative = core or c["mode"] == "host" or (c["mode"] == "draw" and c["n"] in (4, 5) and c["index"] == 0)
        old = _sorted_rows(c["stages"][0])
        names = tuple(sorted(old[0])[:3])
        all_ages = []
        for age in range(7):
            if age < len(c["stages"]):
                all_ages.append({"age": age, "reached": True, "status": "actual_archived_stage",
                                 **_roster_inventories(_sorted_rows(c["stages"][age]), old, names)})
            else:
                all_ages.append({"age": age, "reached": False, "status": "no_stage_because_" + c["stop"].replace(" ", "_")})
        checked = _validate_outcomes(c, independent=core)
        audit_votes = votes[cid, law]
        structural = {"archive_case_id": cid, "source_mode": c["mode"], "source_kind": c["label"], "source_size": c["n"],
                      "archived_draw": c["index"], "original_source_and_draw": c["origin"], "source_law": law,
                      "original_archived_placements_and_earlier_count_status": audit_votes,
                      "archived_terminal_status": c["stop"], "stored_ages": len(c["stages"]), "inventory_for_all_age_slots": all_ages,
                      "complete_round_roster_and_funding_replay": checked,
                      "first_age_the_original_three_are_not_all_loose":
                          next((a["age"] for a in all_ages if a["reached"] and not a["literal_original_three_can_be_read"]), None)}
        roster_inventory.setdefault(cid, {})[law] = structural
        if not core:
            _summarize_structural_row(denominators, c, all_ages)
        if not quantitative:
            continue
        stages = {}
        for age in (range(len(c["stages"])) if core else (0, 1)):
            a = all_ages[age]
            if a["reached"]:
                stages[str(age)] = _quantitative_stage(a, law, audit_votes, archive["tables"], age, core=core)
            else:
                stages[str(age)] = {"status": a["status"]}
        envelope = {"archived_identity": (cid, law), "source_mode": c["mode"], "source_size": c["n"], "source_origin": c["origin"],
                    "bounded_numerical_stages": stages, "prior_stop": c["stop"],
                    "ages_outside_bounded_comparison_kept_structurally": tuple(
                        a["age"] for a in all_ages if a["reached"] and str(a["age"]) not in stages)}
        (built if core else panel).setdefault(cid, {})[law] = envelope
    assert len(core_cases) == 8 and len(built) == 4 and len(panel) == 6
    assert sum(c["mode"] == "draw" for c in archive["cases"]) == 240
    assert sum(c["mode"] == "host" for c in archive["cases"]) == 4
    return built, roster_inventory, panel, {k: dict(v) for k, v in denominators.items()}


def _product_control(cases):
    out = {}
    for law in LAWS:
        old = _sorted_rows(cases[("single3/1/0", law)]["stages"][1])
        piece = Stage(old, law)
        stats, dense = _loose_weights(piece)
        width = piece.offset
        independent = old + tuple(tuple(n + width for n in r) for r in old)
        made = Stage(independent, law)
        prod_stats, both = _loose_weights(made)
        n, w = stats["N_complete_words"], stats["W_sum_squared_past_counts"]
        assert prod_stats["N_complete_words"] == n ** 2 and prod_stats["W_sum_squared_past_counts"] == w ** 2
        assert tuple(a * b for a in dense for b in dense) == both
        marks = (3, 5, 7)
        pair, q = _gram_pair(piece, marks, dense), _gram_pair(made, marks, both)
        assert tuple(tuple(v * n for v in r) for r in pair[0][0]) == q[0][0]
        assert tuple(tuple(v * w for v in r) for r in pair[1][0]) == q[1][0]
        out[law] = {"two_independent_relabelled_rosters": independent, "ordinary_denominator": n ** 2, "clean_denominator": w ** 2,
                    "original_triple_in_first_component": marks, "entire_current_count_weights_factor": True,
                    "both_reduced_triple_matrices_before_and_after_ignoring_the_other_copy_agree_normalized": True,
                    "independent_clean_launch": prod_stats["all_plus_erasure_probability"],
                    "independent_collision_launch": prod_stats["collision_two_independent_ordinary_words_accept"]}
    return out


def _single_interface_auditor_cases(archive):
    proofs = {}
    for c in archive["cases"]:
        if c["mode"] != "built" or c["law"] != "nae":
            continue
        stages = tuple(map(_sorted_rows, c["stages"]))
        criterion = [(i, tuple(b for b, holders in _owners(s).items() if len(holders) == 1)) for i, s in enumerate(stages)]
        eligible = next(((i, open_names[0]) for i, open_names in criterion if len(open_names) == 1), None)
        if eligible is None:
            continue
        [vote] = [v for v in archive["votes"] if v["case"] == c["id"] and v["law"] == "nae" and v["role"] == "built"]
        begin, bridge = eligible
        frozen = stages[begin]
        old_names = set(_owners(frozen))
        assert bridge not in vote["marks"]
        freeze_count = Stage(frozen, "nae").total_and_collision()[0]
        base = vote["records"][begin]
        substitutions = []
        for age, stage in enumerate(stages[begin + 1:], begin + 1):
            exterior = stage[len(frozen):]
            assert old_names.intersection(_owners(exterior)) == {bridge}
            rest = Stage(exterior, "nae")
            num0, num1 = (_point_count(rest, {bridge: b}) for b in (0, 1))
            assert num0 == num1 and num0 > 0
            now = vote["records"][age]
            assert now["table"] == base["table"] and now["physical_unit"] == num0 * base["physical_unit"]
            assert Stage(stage, "nae").total_and_collision()[0] == num0 * freeze_count
            substitutions.append({"actual_age": age, "sole_old_name_in_new_rows": bridge,
                                  "actual_new_rows_beyond_the_frozen_age": exterior,
                                  "complete_exterior_words_at_zero_then_one": (num0, num1),
                                  "archived_unread_full_table_multiplier": num0,
                                  "normalization_cancels_and_matches_every_archived_answer_probability": True})
        proofs[c["id"]] = {"first_one_loose_age": begin, "sole_possible_future_shared_name": bridge,
                           "old_full_auditor_physical_marks": vote["marks"], "audit_table_id_at_the_cut": base["table"],
                           "all_direct_later_checks": substitutions,
                           "scope": ("The fixed auditor asks on the original names. Future rows meet the frozen written system only "
                                     "at one unread name. Complementing the other part pairs the two joining sectors under NAE.")}
    return proofs


def run():
    """Return the complete registered archive replay without writing a file."""
    with gzip.open(ARCHIVE, "rt") as f:
        archive = json.load(f)
    case_index = {(c["id"], c["law"]): c for c in archive["cases"]}
    assert len(case_index) == len(archive["cases"])
    built, structural, panel, denominators = _archive_runs(archive)
    fixture = _source_fixture(case_index)
    dense_cells = sum(s["whole_current_weights"]["reported_loose_count_cells"]
                      for roster in (built, panel) for by_law in roster.values() for c in by_law.values()
                      for s in c["bounded_numerical_stages"].values() if "whole_current_weights" in s)
    dense_cells += sum(p["complete_loose_counts"]["reported_loose_count_cells"] for p in fixture["cases_by_law"].values())
    assert dense_cells <= REPORTED_LOOSE_CAP
    experiment = ROOT / "experiments" / FREEDOM / FAMILY
    exact_files = (Path(__file__).resolve(), REGISTRATION, ARCHIVE, ENGINE, END,
                   *(ROOT / p for p in ANCESTOR_PATHS),
                   experiment / "histories.py", experiment / "ordinary.py", experiment / "contract.json")
    return {"built_histories": built, "source_fixture": fixture, "structural_inventory": structural,
            "archived_original_reader_integer_tables_by_id": archive["tables"],
            "quantitative_panel": panel, "bound_on_excesses_in_this_fixed_panel": _bound_fixed_panel(panel),
            "age_and_stratum_denominators_for_all_archive_non_core_sources": denominators,
            "independent_product_control": _product_control(case_index),
            "exact_single_interface_frozen_original_auditor": _single_interface_auditor_cases(archive),
            "caps_and_coverage": {"dense_loose_word_width": LOOSE_DENSE, "binary_factor_index_limit": CAP,
                                  "optional_conditioning_of_up_to_this_many_named_binary_indices": SPLIT_CAP,
                                  "max_reported_loose_words": REPORTED_LOOSE_CAP, "actual_reported_loose_words": dense_cells,
                                  "source_coverage": {"four_built_both_laws": len(built), "labelled_random_draws_held_in_archive": 120,
                                                      "two_fixed_explosive_cases_both_laws": 2, "cases_with_law_separate": len(case_index)},
                                  "retrospective_selected_draw_cases": 4, "quantitative_ages_in_non_core_cases": (0, 1)},
            "settings": {"answer_order": "answer mask bit i denotes outcome minus at named mark i",
                         "ordinary_setting": "Z reads the named value; X reads the real sum/difference.",
                         "normalizers": "ordinary full count N, square count W, character division 2^k N, collision division N^2.",
                         "physical_access": "The strongest original-record audit reads the same named distinctions after they are spent. The loose-only tests retain every other loose name as a spectator."},
            "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in exact_files},
            "same_canonical_checker_source_hashes_with_the_public_guide_title": {
                str(p.relative_to(ROOT)): sha256(p.read_bytes().replace(b"docs/KNOT_INTUITION.md", b"INTUITIONS.md")).hexdigest()
                for p in sorted((ROOT / "tools/knotlab").glob("*.py"))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    option = parser.parse_args()
    if option.smoke:
        with gzip.open(ARCHIVE, "rt") as f:
            data = json.load(f)
        cohort = {(c["id"], c["law"]): c for c in data["cases"]}
        print(json.dumps(_source_fixture(cohort)["classical_bound_of_every_choice_of_the_three_relative_signs"], sort_keys=True))
    else:
        out = json.dumps(run(), sort_keys=True, separators=(",", ":")).encode()
        print(f"{len(out)} canonical JSON bytes SHA-256 {sha256(out).hexdigest()}")


if __name__ == "__main__":
    main()
