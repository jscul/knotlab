"""Exact weights for the enrolled first ordinary growth rounds."""

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import prod
import os
from pathlib import Path
from random import Random
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREREG = HERE / "preregistration.md"
GROWTH = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py"
COUNTING = ROOT / "experiments/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/exact_counts.py"
ARCHIVE = ROOT / "artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json"
ENGINE_INPUTS = (
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/joinlib.py",
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py",
    "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py",
    "experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/freelib.py",
)
LAWS = ("parity", "nae")
CAP = 18
SEED = 25320261121


def _load(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@cache
def _ancestors():
    growth = _load("b253_literal_growth", GROWTH)
    old = growth.J
    for observed, expected in zip((old, old.fastlib, old.S, old.F), ENGINE_INPUTS, strict=True):
        assert Path(observed.__file__).resolve() == ROOT / expected
    return growth, _load("b253_exact_counts", COUNTING)


def _mask(names):
    return sum(1 << bit for bit in names)


def _width(supports):
    return max((max(row) + 1 for row in supports if row), default=0)


def _bit_word(physical_word, names):
    return "".join(str((physical_word >> j) & 1) for j in names)


def _ratio(a, b):
    return str(Fraction(a, b)) if b else None


def _tv(a, b):
    sa, sb = sum(a), sum(b)
    if not sa or not sb:
        return None
    return _ratio(sum(abs(x * sb - y * sa) for x, y in zip(a, b, strict=True)), 2 * sa * sb)


@dataclass(frozen=True)
class Source:
    name: str
    stratum: str
    supports: tuple
    marks: tuple
    provenance: dict


def _decode_prufer(word):
    degree = [1] * (len(word) + 2)
    for name in word:
        degree[name] += 1
    meetings = []
    for name in word:
        leaf = degree.index(1)
        meetings.append(tuple(sorted((leaf, name))))
        degree[leaf] = 0
        degree[name] -= 1
    meetings.append(tuple(i for i, count in enumerate(degree) if count == 1))
    return tuple(sorted(meetings))


def _stars(sizes, meetings):
    return tuple(map(tuple, _ancestors()[0].J.stars_from(sizes, meetings)))


def _fixed_sources():
    for name, sizes, meetings, marks in (
            ("single_ternary", (3,), (), (0, 1)),
            ("two_ternaries_one_shared_name", (3, 3), ((0, 1),), (1, 2)),
            ("three_ternaries_in_one_chain", (3, 3, 3), ((0, 1), (1, 2)), (0, 1))):
        yield Source(name, "fixed_small", _stars(sizes, meetings), marks,
                     {"draw": "specified fixed control", "sizes": sizes, "meetings_in_label_order": meetings})
    rng, joins = Random(SEED), _ancestors()[0].J
    for n in (3, 4, 5):
        for replicate in range(4):
            word = tuple(rng.randrange(n) for _ in range(n - 2))
            meetings = _decode_prufer(word)
            bare = tuple(joins.bare_sizes(n, meetings))
            for label, sizes in (("bare", bare), ("one_extra_at_0", (bare[0] + 1, *bare[1:]))):
                yield Source(f"prufer_{n}_{replicate}_{label}", "paired_labelled_tree", _stars(sizes, meetings), (0, 1),
                             {"size": n, "draw": replicate, "prufer_word": word, "sampling_with_replacement": True, "redraws": 0,
                              "uniform_generator_denominator": n ** (n - 2), "one_extra_at_holder_0": label != "bare",
                              "sizes": sizes, "meetings_in_label_order": meetings})
    old = json.loads(ARCHIVE.read_text())["named_archive_starts"]
    for label in ("start-03", "start-13"):
        row = old[label]
        sizes, meetings = tuple(row["sizes"]), tuple(map(tuple, row["meetings"]))
        supports = _stars(sizes, meetings)
        assert supports == tuple(map(tuple, row["gate"]["literal_supports"]))
        yield Source(label, "fixed_archived_stress", supports, supports[0][:2],
                     {"draw": "specified stress source by itself", "archive_cap_seven_label": row["identifier"],
                      "sizes": sizes, "meetings_in_label_order": meetings,
                      "historical_parity_birth_counts": row["round_junction_counts"],
                      "historical_note": {"start-03": "archived burst from 386 to 28065",
                                          "start-13": "archived proof of unbounded parity births"}[label]})


def _parallel_source(m, variant):
    chain = tuple((i, i + 1) for i in range(m + 1) for _ in range(2))
    end = m + 1
    if variant == "direct":
        meetings = (*chain, (0, end))
        sizes = (4, *((4,) * m), 4)
        witness = None
    else:
        witness = m + 2
        meetings = (*chain, (0, witness), (0, witness), (end, witness), (end, witness))
        sizes = (5, *((4,) * m), 5, 4)
    designated = len(meetings), len(meetings) + 1
    centre = m, m + 1
    supports = _stars(sizes, meetings)
    assert tuple(i for i, pair in enumerate(meetings) if pair == (m // 2, m // 2 + 1)) == centre
    assert designated[0] in supports[0] and designated[1] in supports[end]
    return Source(f"{variant}_{m}_parallel_chain", "fixed_parallel_chains", supports, centre,
                  {"m": m, "arrangement": variant, "sizes": sizes, "meetings_in_label_order": meetings,
                   "named_full_witness_holder": witness, "old_live_end_holders": (0, end), "designated_loose_names": designated,
                   "central_link_holders": (m // 2, m // 2 + 1)})


def _disconnected():
    active = _parallel_source(2, "witness")
    start = _width(active.supports)
    old_closed = (start, start + 1, start + 2)
    rows = active.supports + (old_closed, old_closed)
    return Source("witnessed_birth_with_disconnected_spent_companion", "fixed_disconnected", rows, old_closed[:2],
                  {"active_component_original_source": active.name, "mark_holders": (len(rows) - 2, len(rows) - 1),
                   "separately_spent_companion_holds_same_three_distinctions_twice": old_closed})


def _owners(rows):
    owners = {}
    for h, support in enumerate(rows):
        for bit in support:
            owners.setdefault(bit, []).append(h)
    assert all(len(h) in (1, 2) for h in owners.values()) and set(owners) == set(range(_width(rows)))
    return owners


def _round(old, law):
    growth, _ = _ancestors()
    instance = growth.S.from_junctions(old)
    live = tuple(i for i in instance.live if instance.loose(i))
    old_loose = {i: tuple(instance.loose(i)) for i in live}
    groups = growth.J.fastlib._orig(instance, live)
    assert groups == instance.groups_among(live)
    demand = Counter(i for group in groups for i in group)
    partners = [tuple(sorted(instance.nbr[i])) for i in range(len(old))]
    begin = {"old_live_holders_and_loose_names": old_loose, "old_direct_neighbor_holders": partners,
             "actual_common_neighbor_groups": [tuple(sorted(group)) for group in groups],
             "common_neighbors_for_each_group": [tuple(sorted(set.intersection(*(instance.nbr[i] for i in group)))) for group in groups],
             "fast_and_literal_group_methods_agree": True}
    bare_rule = growth.F.fewest
    actual_rule = growth.parity_rule(bare_rule) if law == "parity" else growth.nae_rule(bare_rule)
    observed = []

    def reviewed_rule(p, info, rng):
        grants = actual_rule(p, info, rng)
        for record, grant in zip(info, grants, strict=True):
            observed.append({**record, "grant": grant})
        return grants

    result = instance.step(reviewed_rule, None)
    rows = tuple(map(tuple, instance.bits_of))
    if result is None:
        assert rows == old and instance.rounds == 0
        return {**begin, "status": "stalled", "actual_rounds_performed": 0,
                "shortage_by_holder": {j: demand[j] - len(old_loose[j]) for j in live if demand[j] > len(old_loose[j])},
                "full_new_supports": old, "births": [], "new_names": ()}
    if result["new"] == 0:
        assert not live
        return {**begin, "status": "already_closed", "actual_rounds_performed": 0,
                "full_new_supports": old, "births": [], "new_names": ()}
    assert rows[:len(old)] == old and instance.rounds == 1
    old_width = _width(old)
    owners = _owners(old)
    after_owners = _owners(rows)
    births = []
    for stamp in observed:
        j, p, f = stamp["j"], stamp["p"], stamp["grant"]
        inputs, fresh = rows[j][:p], rows[j][p:]
        assert f == len(fresh) and f == instance.fresh[j]
        assert all(bit < old_width for bit in inputs) and all(bit >= old_width for bit in fresh)
        assert all(after_owners[bit] == [j] for bit in fresh)
        assert p and all(len(owners[bit]) == 1 for bit in inputs)
        assert instance.demand_at_birth[j] == stamp["d"]
        assert f == (stamp["d"] if stamp["implied"] else max(stamp["d"], 3 - p, 1))
        births.append({"holder": j, "parents_in_literal_input_order": tuple(owners[bit][0] for bit in inputs),
                       "consumed_old_names": inputs, "fresh_names": fresh, "fresh_grant": f,
                       "lookahead_demand": stamp["d"], "law_already_implied_before_fresh": stamp["implied"],
                       "new_support": rows[j]})
    assert len(births) == result["new"]
    assert Counter(b for row in old_loose.values() for b in row) == Counter(b for r in births for b in r["consumed_old_names"])
    assert sum(r["fresh_grant"] for r in births) == _width(rows) - old_width
    after_live = tuple(i for i in instance.live if instance.loose(i))
    return {**begin, "status": "grew" if after_live else "grew_and_closed", "actual_rounds_performed": 1,
            "full_new_supports": rows, "new_names": tuple(range(old_width, instance.nbits)), "births": births,
            "postround_live_holders": after_live, "all_old_rows_retained_verbatim": True,
            "all_old_loose_names_used_once": True, "every_distinction_has_at_most_two_holders": True}


def _allowed(word, scopes, law):
    if law == "parity":
        return all((word & scope).bit_count() % 2 == 0 for scope in scopes)
    return all(word & scope not in (0, scope) for scope in scopes)


@cache
def _literal_words(supports, law):
    n = _width(supports)
    if n > CAP:
        return None
    masks = tuple(map(_mask, supports))
    return tuple(word for word in range(1 << n) if _allowed(word, masks, law))


def _packed(word, marks):
    return sum(((word >> bit) & 1) << i for i, bit in enumerate(marks))


def _word_tokens(marks):
    return tuple("" if not marks else format(i, f"0{len(marks)}b") for i in range(1 << len(marks)))


def _literal_counts(words, marks):
    counts = Counter(_bit_word(word, marks) for word in words)
    return [counts[token] for token in _word_tokens(marks)]


@cache
def _canonical_cli(width, allowed):
    # Each excluded word contributes one clause over the anonymous whole projection.
    variables = [f"x{i}" for i in range(width)]
    forbidden = set(range(1 << width)) - set(allowed)
    clauses = [" ".join(("~" if word >> i & 1 else "") + v for i, v in enumerate(variables))
               for word in sorted(forbidden)]
    if not clauses:
        clauses = [f"{v} ~{v}" for v in variables]
    call = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
            "--loops", *variables[:-1], "--contact", variables[-1], "--json"]
    proc = subprocess.run(call, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                          capture_output=True, text=True)
    if width < 3:
        assert proc.returncode == 2 and "a knot binds at least two loops" in proc.stderr
        return {"canonical_knot": False, "status": "canonical_checker_refused_arity",
                "reason": proc.stderr.strip().removeprefix("error: ")}
    proc.check_returncode()
    row = json.loads(proc.stdout)
    assert set(row["allowed"]) == {_bit_word(value, range(width)) for value in allowed}
    return {"canonical_knot": bool(row["is_knot"]), "status": "whole_projection_replayed_by_canonical_checker"}


def _certificate_columns(supports, law):
    _, counts = _ancestors()
    literal = _literal_words(supports, law)
    if law == "parity":
        engine = counts.Parity(supports)
        tests = [engine.certificate(s) for s in supports]
    else:
        with counts.NotAllEqualSupport(supports) as engine:
            tests = [engine.certificate(s) for s in supports]
    rows = []
    for i, (scope, x) in enumerate(zip(supports, tests, strict=True)):
        width = len(scope)
        if law == "parity":
            masks = tuple(_packed(row, scope) for row in x["projected_equations"])
            allowed = tuple(p for p in range(1 << width) if _allowed(p, masks, law))
        else:
            allowed = tuple(x["projected_patterns"])
        if literal is not None:
            assert allowed == tuple(sorted({_packed(word, scope) for word in literal}))
        deleted_sizes = tuple(len({word & ~(1 << j) for word in allowed}) for j in range(width))
        k123 = 0 < len(allowed) < 1 << width and all(n == 1 << (width - 1) for n in deleted_sizes)
        assert k123 == (x["k1"] and x["k2"] and x["k3"])
        canonical = _canonical_cli(width, allowed)
        assert canonical["canonical_knot"] == (k123 and width >= 3)
        rows.append({"holder": i, "named_support": scope, "allowed_words_on_the_full_projection": allowed,
                     "physical_name_at_local_bit_zero": scope[0], "one_deleted_projection_sizes": deleted_sizes,
                     "K1": x["k1"], "K2": x["k2"], "K3": x["k3"], "relation_K1_K2_K3_without_arity_gate": k123,
                     "canonical_K1_K2_K3": canonical["canonical_knot"],
                     "full_declared_local_relation": x["full_law"], "previous_start_classifier_minimum_arity_three": x["eligible"],
                     "canonical_CNF_projection_check": canonical})
    return rows


def _schedule_width(scopes, names, marks):
    """Plan the inherited, deterministic minimum-scope elimination before making a table."""
    remaining = set(names) - set(marks)
    factors = [set(scope) for scope in scopes]
    order = []
    peak = max([len(marks), *(len(x) for x in factors)])
    while remaining and peak <= CAP:
        neighbors = {b: set() for b in remaining}
        for factor in factors:
            for b in factor.intersection(remaining):
                neighbors[b].update(factor)
        pivot = min(remaining, key=lambda v: (len(neighbors[v]), v))
        scope = neighbors[pivot]
        peak = max(peak, len(scope))
        remaining.remove(pivot)
        order.append(pivot)
        factors = [f for f in factors if pivot not in f] + [scope - {pivot}]
    return peak, order


@cache
def _ordinary_factor(scope):
    return _ancestors()[1].Factor.from_function(scope, lambda w: int("0" in w and "1" in w))


@cache
def _extension_factor(scope, fresh, exponent):
    return _ancestors()[1].Factor.from_function(scope, lambda w: ((1 << fresh) - int(all(b == w[0] for b in w))) ** exponent)


def _count_nae(old, marks, weighted_births=(), power=0):
    names = tuple(range(_width(old)))
    roots = tuple(tuple(sorted(r)) for r in old)
    factors = tuple((tuple(sorted(b["consumed_old_names"])), b["fresh_grant"]) for b in weighted_births)
    # A unary birth has the same multiplicity on both input values. Factor it out.
    constant = prod(((1 << f) - 1) ** power for s, f in factors if len(s) == 1) if power else 1
    nonconstant = tuple((s, f) for s, f in factors if len(s) > 1) if power else ()
    peak, order = _schedule_width((*roots, *(s for s, _ in nonconstant)), names, marks)
    tally = {"planned_live_boolean_peak": peak, "cap": CAP, "planned_elimination_prefix": order}
    if peak > CAP:
        return None, {**tally, "status": "omitted_without_allocating_over_cap", "omitted": "integer count and any probability using it"}
    old_factors = [_ordinary_factor(s) for s in roots]
    later = [_extension_factor(s, f, power) for s, f in nonconstant]
    histogram, actual = _ancestors()[1].eliminate(old_factors + later, names, marks)
    assert max(actual, len(marks)) == peak
    return [constant * c for c in histogram], {**tally, "status": "exact", "factorized_constant_multiplier": constant}


def _local_extension(birth, old_word, law):
    f = birth["fresh_grant"]
    if law == "parity":
        return 1 << max(0, f - 1)
    chosen = old_word & _mask(birth["consumed_old_names"])
    return (1 << f) - int(chosen in (0, _mask(birth["consumed_old_names"])))


def _extension_count(births, word, law):
    return prod(_local_extension(b, word, law) for b in births)


def _independent_child_example(old, new, births, word, law):
    enlarged = word
    for birth in births:
        scope, fresh = _mask(birth["consumed_old_names"]), birth["fresh_names"]
        if not fresh:
            continue
        paid = word & scope
        if (paid.bit_count() % 2 if law == "parity" else paid == 0):
            enlarged |= 1 << fresh[0]
    assert enlarged & ((1 << _width(old)) - 1) == word
    assert _allowed(word, tuple(map(_mask, old)), law)
    assert _allowed(enlarged, tuple(map(_mask, new)), law)
    return enlarged


def _known_extensions(old, new, births, law, exact_histogram, literal=None):
    count = lambda word: _extension_count(births, word, law)
    if law == "parity":
        candidates = (0,)
    elif literal:
        best, worst = max(literal, key=count), min(literal, key=count)
        candidates = (worst, best)
    else:
        _, c = _ancestors()
        with c.NotAllEqualSupport(old) as support:
            options = []
            schemes = [()]
            for birth in births:
                body = birth["consumed_old_names"]
                if len(body) > 1:
                    schemes.append(tuple(-(b + 1) for b in body))
                    schemes.extend((body[0] + 1, -(b + 1)) for b in body[1:])
            for pins in schemes:
                if support.solver.solve(assumptions=list(pins)):
                    options.append(_mask(v - 1 for v in support.solver.get_model() if v > 0))
        candidates = (min(options, key=count), max(options, key=count)) if options else ()
    seen = {}
    for word in dict.fromkeys(candidates):
        size = count(word)
        if size in seen:
            continue
        if exact_histogram is not None:
            assert exact_histogram[size] > 0
        seen[size] = {"physical_old_word": word, "physical_old_word_names_zero_up": _bit_word(word, range(_width(old))),
                      "total_extensions": size, "separate_birth_factors": [_local_extension(b, word, law) for b in births],
                      "one_complete_allowed_enlarged_word": _independent_child_example(old, new, births, word, law)}
    return list(seen.values())


def _histogram_fibres(old, births, law, old_total, raw):
    constant = prod(1 << max(0, b["fresh_grant"] - 1) for b in births) if law == "parity" else None
    if constant is not None:
        return Counter({constant: old_total}), {"status": "exact_by_affine_rank_and_private_fresh_names"}
    if raw is not None:
        return Counter(_extension_count(births, word, law) for word in raw), {"status": "direct_full_old_word_enumeration"}
    live = tuple(sorted({bit for b in births if len(b["consumed_old_names"]) > 1 for bit in b["consumed_old_names"]}))
    counts, meta = _count_nae(old, live)
    if counts is None and 0 < len(live) <= CAP and all(len(row) <= CAP for row in old):
        # Conditioning a retained distinction also preserves every other retained slot.
        # Choose the split by factor scopes alone, and verify the cap before materializing.
        names = tuple(range(_width(old)))
        for pinned in live:
            keep = tuple(bit for bit in live if bit != pinned)
            unpinned = tuple(bit for bit in names if bit != pinned)
            scopes = tuple(tuple(sorted(row)) for row in old)
            reduced = tuple(tuple(bit for bit in scope if bit != pinned) for scope in scopes)
            width, order = _schedule_width(reduced, unpinned, keep)
            if width > CAP:
                continue
            counter = _ancestors()[1]
            slices = []
            for bit_value in (0, 1):
                conditioned_factors = []
                for scope, after in zip(scopes, reduced, strict=True):
                    factor = _ordinary_factor(scope)
                    if scope != after:
                        factor = counter.Factor(after, factor.values.take(bit_value, axis=scope.index(pinned)))
                    conditioned_factors.append(factor)
                values, actual_width = counter.eliminate(conditioned_factors, unpinned, keep)
                assert max(actual_width, len(keep)) == width
                slices.append(values)
            stride = 1 << (len(live) - live.index(pinned) - 1)
            counts = [count for offset in range(0, len(slices[0]), stride)
                      for values in slices for count in values[offset:offset + stride]]
            meta = {"status": "exact_after_two_pinned_eliminations", "pinned_physical_name": pinned,
                    "unsplit_planned_boolean_peak": meta["planned_live_boolean_peak"], "planned_live_boolean_peak": width,
                    "cap": CAP, "pinned_elimination_order": order,
                    "branch_old_word_counts_for_zero_then_one": [sum(s) for s in slices]}
            break
    if counts is None:
        return None, meta
    fibres = Counter()
    for word, mass in zip(_word_tokens(live), counts, strict=True):
        if mass:
            physical = _mask(bit for bit, ch in zip(live, word, strict=True) if ch == "1")
            fibres[_extension_count(births, physical, law)] += mass
    return fibres, {**meta, "inputs_to_births_with_multiple_parents": live}


def _extension_bound(birth):
    f, p = birth["fresh_grant"], len(birth["consumed_old_names"])
    if not f:
        assert birth["law_already_implied_before_fresh"]
        return 1, 1
    return (1 << f) - 1, (1 << f) if p > 1 else (1 << f) - 1


def _constant_from_moments(n, first, second, witnesses):
    if n is not None and first is not None and second is not None:
        assert n * second >= first ** 2
        return n * second == first ** 2, n * second - first ** 2
    if len(witnesses) > 1:
        return False, None
    return None, None


def _histogram_comparison(marks, begin, after, transported):
    before_total = sum(begin) if begin is not None else None
    after_total = sum(after) if after is not None else None
    equal = (0, 3)
    one = (2, 3)
    def aggregate(values, subset):
        if values is None:
            return None
        count, denominator = sum(values[x] for x in subset), sum(values)
        return {"numerator": count, "denominator": denominator, "probability": _ratio(count, denominator)}

    return {"marks_in_printed_bit_order": marks, "printed_words": _word_tokens(marks),
            "before_raw": begin, "after_U_raw": after, "after_L_in_old_state_integer_units": transported,
            "before_denominator": before_total, "after_U_denominator": after_total,
            "marked_TV_U_grown_vs_U_initial": _tv(begin, after) if begin is not None and after is not None else None,
            "marked_TV_L_grown_vs_U_initial": _tv(begin, transported) if begin is not None and transported is not None else None,
            "equality_event": {"before_U": aggregate(begin, equal), "after_U": aggregate(after, equal), "after_L": aggregate(transported, equal)},
            "first_named_bit_is_one": {"before_U": aggregate(begin, one), "after_U": aggregate(after, one),
                                       "after_L": aggregate(transported, one)}}


def _full_count(source, law, turn):
    old, new = source.supports, turn["full_new_supports"]
    births, marks = turn["births"], source.marks
    literal_old, literal_new = _literal_words(old, law), _literal_words(new, law)
    measures, meta = {}, {}
    if law == "parity":
        parity = _ancestors()[1].Parity
        p, q = parity(old), parity(new)
        old_total, new_total = p.total, q.total
        c = _extension_count(births, 0, law)
        assert old_total * c == new_total
        projected, projected_rank = q.projected_rows(range(_width(old))), p.rank
        assert len(projected) == projected_rank  # The old rows already lie in this returned row space.
        basis = p._basis(0)
        for b in births:
            if not b["fresh_grant"]:
                assert b["law_already_implied_before_fresh"]
                residue = _mask(b["consumed_old_names"])
                while residue:
                    residue ^= basis[residue.bit_length() - 1]
        measures = {"N_old": old_total, "sum_c": new_total, "sum_c_squared": old_total * c ** 2}
        meta["old_projection_rank"] = {"old_original": projected_rank, "restrict_grown_to_old": len(projected)}
        begin, after = p.histogram(marks), q.histogram(marks)
        assert after == [v * c for v in begin]
        low, high = c, c
    else:
        with _ancestors()[1].NotAllEqualSupport(old) as support:
            for b in births:
                if not b["fresh_grant"]:
                    assert b["law_already_implied_before_fresh"]
                    inputs = b["consumed_old_names"]
                    assert all(not support.solver.solve(assumptions=[sign * (d + 1) for d in inputs]) for sign in (-1, 1))
        for label, power in (("N_old", 0), ("sum_c", 1), ("sum_c_squared", 2)):
            raw, meta[label] = _count_nae(old, (), births, power)
            measures[label] = None if raw is None else raw[0]
        old_total, new_total = measures["N_old"], measures["sum_c"]
        begin, meta["marked_before"] = _count_nae(old, marks)
        after, meta["marked_U_after"] = _count_nae(old, marks, births, 1)
        bounds = [_extension_bound(b) for b in births]
        low, high = prod(a for a, _ in bounds), prod(b for _, b in bounds)
    fibre, fibre_meta = _histogram_fibres(old, births, law, old_total, literal_old)
    witness = _known_extensions(old, new, births, law, fibre, literal_old)
    constant, moment_gap = _constant_from_moments(old_total, new_total, measures["sum_c_squared"], witness)
    if literal_old is not None:
        assert old_total == len(literal_old) and begin == _literal_counts(literal_old, marks)
        assert new_total == sum(_extension_count(births, word, law) for word in literal_old)
        assert measures["sum_c_squared"] == sum(_extension_count(births, word, law) ** 2 for word in literal_old)
    literal_fibre_comparison = None
    if literal_new is not None:
        assert new_total == len(literal_new) and after == _literal_counts(literal_new, marks)
        old_mask = (1 << _width(old)) - 1
        projected = Counter(w & old_mask for w in literal_new)
        assert literal_old is not None and set(projected) == set(literal_old)
        assert all(number == _extension_count(births, word, law) for word, number in projected.items())
        literal_fibre_comparison = "independent full enumeration of both relations and literal restriction"
    if fibre is not None:
        assert old_total == sum(fibre.values()) and new_total == sum(c * n for c, n in fibre.items())
        assert measures["sum_c_squared"] == sum(c ** 2 * n for c, n in fibre.items())
        assert constant == (len(fibre) == 1)
        tv_full = _ratio(sum(n * abs(old_total * c - new_total) for c, n in fibre.items()), 2 * old_total * new_total)
    else:
        tv_full = "0" if constant else None
    assert begin is None or sum(begin) == old_total or old_total is None
    assert after is None or sum(after) == new_total or new_total is None
    comparison = _histogram_comparison(marks, begin, after, begin)
    return {"extension_to_every_old_word": True,
            "extension_proof_scope": "Retained old rows, all consuming names old and separate fresh names, zero grants individually implied.",
            "moments_of_full_old_fibre": measures, "integer_variance_equality_gap": moment_gap,
            "constant_full_old_fibre": constant, "exact_fibre_histogram_size_to_number_of_old_words": fibre,
            "full_fibre_histogram_counting": fibre_meta,
            "a_priori_bounds_on_each_old_word_fibre": (low, high), "actual_old_word_and_complete_extension_witnesses": witness,
            "count_execution": meta, "literal_checks": {"old_word_enumeration": literal_old is not None, "new_word_enumeration": literal_new is not None,
                                                        "both_relation_comparison": literal_fibre_comparison},
            "TV_full_old_pushforward_vs_old_U": tv_full, "TV_full_enlarged_U_vs_L": tv_full,
            "equal_full_enlarged_and_old_weights_both_stages": constant, "marked_projection": comparison}


def _holder_distances(rows, births, marks):
    owners = _owners(rows)
    focal = tuple(sorted(set(h for bit in marks for h in owners[bit])))
    graph = {h: set() for h in range(len(rows))}
    for uses in owners.values():
        if len(uses) == 2:
            a, b = uses
            graph[a].add(b)
            graph[b].add(a)
    out = []
    for birth in births:
        holder = birth["holder"]
        distance, todo = {holder: 0}, deque((holder,))
        while todo:
            h = todo.popleft()
            for neighbor in sorted(graph[h]):
                if neighbor not in distance:
                    distance[neighbor] = distance[h] + 1
                    todo.append(neighbor)
        targets = {h: distance.get(h) for h in focal}
        out.append({"reached_birth": holder, "targets_holding_a_mark": targets,
                    "minimum_number_of_holder_meetings": min((v for v in targets.values() if v is not None), default=None)})
    return out


def _evaluate(source):
    report = {"cohort": source.stratum, "canonical_source_metadata": source.provenance, "original_named_rows": source.supports,
              "founding_owners_by_mark": _owners(source.supports), "marked_event": source.marks, "laws": {}}
    for law in LAWS:
        old_gate = _certificate_columns(source.supports, law)
        allowed = all(rec["canonical_K1_K2_K3"] and rec["full_declared_local_relation"] for rec in old_gate)
        if not allowed:
            report["laws"][law] = {"status": "ineligible_founder_actual_joint_projections", "old_projection_certificates": old_gate,
                                   "omitted_denominator": "no weighting attributed to a lawful growth start in this law"}
            continue
        turned = _round(source.supports, law)
        result = {**turned, "old_projection_certificates": old_gate}
        if turned["births"]:
            grown = turned["full_new_supports"]
            cert = _certificate_columns(grown, law)
            result.update({"new_projection_certificates": cert,
                           "failed_K_or_local_projection_holders": [r["holder"] for r in cert
                              if not r["canonical_K1_K2_K3"] or not r["full_declared_local_relation"]],
                           "actual_grown_owners_by_mark": _owners(grown),
                           "weights": _full_count(source, law, turned),
                           "holder_meetings_from_each_birth_to_the_mark": _holder_distances(grown, turned["births"], source.marks)})
        else:
            result["weights"] = None
            result["zero_growth_weighting_verdict"] = "no performed growth step"
        report["laws"][law] = result
    return report


LINK_PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))


def _local_values_allowed(values, law):
    return sum(values) % 2 == 0 if law == "parity" else 0 < sum(values) < len(values)


def _chain_transfer(source, law, actual):
    design, marks = source.provenance, source.marks
    m, variant = design["m"], design["arrangement"]
    terminal_names = design["designated_loose_names"]
    t = tuple(tuple(int(_local_values_allowed((*i, *j), law)) for j in LINK_PAIRS) for i in LINK_PAIRS)

    def propagate(start, k):
        message = start
        for _ in range(k):
            message = [sum(message[q] * t[q][x] for q in range(4)) for x in range(4)]
        return message

    if variant == "direct":
        fences = ((loose_left, loose_right, (d,), (d,))
                  for loose_left, loose_right, d in product((0, 1), repeat=3))
    else:
        fences = ((loose_left, loose_right, before, after)
                  for loose_left, loose_right, before, after in product((0, 1), (0, 1), LINK_PAIRS, LINK_PAIRS)
                  if _local_values_allowed((*before, *after), law))
    old_bins, new_bins, fibre, histories = [0] * 4, [0] * 4, Counter(), []
    for b0, b1, seam0, seam1 in fences:
        left = propagate([int(_local_values_allowed((*p, *seam0, b0), law)) for p in LINK_PAIRS], m // 2)
        right = propagate([int(_local_values_allowed((*p, *seam1, b1), law)) for p in LINK_PAIRS], m - m // 2)
        at_centre = [a * b for a, b in zip(left, right, strict=True)]
        if not any(at_centre):
            continuations = None
        else:
            # Read the actual birth's old named inputs and independently enumerate its fresh words.
            values = dict(zip(terminal_names, (b0, b1), strict=True))
            continuations = 1
            for event in actual["births"]:
                fixed = tuple(values[name] for name in event["consumed_old_names"])
                continuations *= sum(_local_values_allowed((*fixed, *fresh), law)
                                     for fresh in product((0, 1), repeat=event["fresh_grant"]))
            assert continuations > 0
            fibre[continuations] += sum(at_centre)
            for i, n in enumerate(at_centre):
                old_bins[i] += n
                new_bins[i] += continuations * n
        histories.append({"loose_values": (b0, b1), "seam_values_on_the_ends": (seam0, seam1),
                          "left_message": left, "right_message": right, "old_bins_in_central_word_order": at_centre,
                          "legal_fresh_allocations_per_old_word": continuations})
    primary = actual["weights"]["marked_projection"]
    assert primary["marks_in_printed_bit_order"] == marks and primary["before_raw"] == old_bins and primary["after_U_raw"] == new_bins
    assert primary["after_L_in_old_state_integer_units"] == old_bins
    if actual["weights"]["exact_fibre_histogram_size_to_number_of_old_words"] is not None:
        assert actual["weights"]["exact_fibre_histogram_size_to_number_of_old_words"] == fibre
    if law == "nae":
        for bins in (old_bins, new_bins):
            assert bins[0] == bins[3] and bins[1] == bins[2]
            assert 2 * (bins[2] + bins[3]) == sum(bins)
    return {"pair_state_order": LINK_PAIRS, "internal_four_place_transition": t,
            "finite_recurrence": "Start at a fixed endpoint bit and seam word. Sum each previous message against the old four-place relation. At the marked pair multiply the messages and sum over seam/endpoint choices.",
            "left_exponent": m // 2, "right_exponent": m - m // 2,
            "all_endpoint_and_seam_rows": histories, "old_central_counts": old_bins, "new_central_weighted_counts": new_bins,
            "transfer_histogram_of_full_old_fibres": fibre, "matches_named_mark_elimination_or_GF2": True,
            "global_NAE_complement_symmetry_certified_on_four_central_counts": law == "nae"}


def _parallel_pair(m):
    cases = {}
    for variant in ("direct", "witness"):
        source = _parallel_source(m, variant)
        report = _evaluate(source)
        for law in LAWS:
            actual = report["laws"][law]
            if not actual.get("births"):
                continue
            term = source.provenance["designated_loose_names"]
            awarded = len(actual["births"]) == 1 and set(actual["births"][0]["consumed_old_names"]) == set(term)
            actual.update({"one_birth_spends_both_designated_loose_names": awarded,
                           "old_sources_witnessed_direct_neighbor_holders": source.provenance["named_full_witness_holder"],
                           "independent_fixed_four_state_transfer": _chain_transfer(source, law, actual)})
            for row in actual["births"]:
                if law == "parity" and row["fresh_grant"] == 0:
                    projection = actual["new_projection_certificates"][row["holder"]]
                    row["binary_closing_arity_certificate"] = {
                        "physical_arity": len(row["new_support"]), "projected_words": projection["allowed_words_on_the_full_projection"],
                        "canonical_K1_K2_K3": projection["canonical_K1_K2_K3"],
                        "relation_K1_K2_K3_without_arity_gate": projection["relation_K1_K2_K3_without_arity_gate"],
                        "canonical_checker": projection["canonical_CNF_projection_check"],
                        "initial_arity_floor_test_is_separate": True}
        cases[variant] = report
    return cases


def growth_checks():
    """Replay physical growth and return counts, growth traces and exact dependencies."""
    fixed = {source.name: _evaluate(source) for source in _fixed_sources()}
    parallel = {str(m): _parallel_pair(m) for m in (2, 4, 6)}
    inactive_component = _evaluate(_disconnected())
    for law in LAWS:
        branch = inactive_component["laws"][law]
        if branch.get("weights"):
            assert branch["weights"]["marked_projection"]["marked_TV_U_grown_vs_U_initial"] == "0"
            assert all(row["minimum_number_of_holder_meetings"] is None
                       for row in branch["holder_meetings_from_each_birth_to_the_mark"])
    report = [*fixed.values(), *(r for pairs in parallel.values() for r in pairs.values()), inactive_component]
    inputs = (Path(__file__).resolve(), PREREG, GROWTH, COUNTING, ARCHIVE, *(ROOT / path for path in ENGINE_INPUTS))
    return {"registered_sources": fixed, "fixed_parallel_name_chains": parallel,
            "disconnected_closed_companion_control": inactive_component,
            "counts_by_law_and_status_all_physical_sources": {
                law: dict(Counter(r["laws"][law]["status"] for r in report)) for law in LAWS},
            "selection": {"fixed_small": 3, "draws_per_tree_size": 4, "labelled_tree_sizes": (3, 4, 5), "tree_rng_seed": SEED,
                          "paired_tree_sources_including_extra_controls": 24, "fixed_archive_stress": ("start-03", "start-13"),
                          "fixed_parallel_controls": 6, "fixed_disconnected_controls": 1,
                          "every_enrolled_physical_source": len(report), "same_named_supports_for_both_laws": True},
            "method": {"old_third_bit_order": "The first named distinction is the least significant bit for projected holder words. Histograms print names in their written order.",
                       "weights": "U gives one initial unit per complete allowed word. A grown word in L has weight 1/c(o) for its old restriction o.",
                       "fibre_moments": "O computes the number of old words. Sum c is the grown count. O times sum c² minus (sum c)² is zero exactly for a constant full old fibre.",
                       "distance": "Unweighted breadth-first count of actual holder meetings in the enlarged roster. Each shared distinction supplies one holder meeting without assigning a metric length.",
                       "cap": CAP, "conditional_growth_stage": "Exactly the first funded round, using the minimum-fresh engine and the registered labels."},
            "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs},
            "canonical_checker_code_sha256_after_guide_title_normalization": {
                str(p.relative_to(ROOT)): sha256(p.read_bytes().replace(b"docs/KNOT_INTUITION.md", b"INTUITIONS.md")).hexdigest()
                for p in sorted((ROOT / "tools/knotlab").glob("*.py"))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    options = parser.parse_args()
    if options.smoke:
        source = next(_fixed_sources())
        data = _evaluate(source)
        for law in LAWS:
            assert data["laws"][law]["weights"]["constant_full_old_fibre"] is True
        print("Both ordinary laws passed the single-ternary growth and complete-weight check.")
        return
    result = growth_checks()
    out = json.dumps(result, separators=(",", ":"), sort_keys=True).encode()
    print(f"{len(out)} canonical JSON bytes, SHA-256 {sha256(out).hexdigest()}")


if __name__ == "__main__":
    main()
