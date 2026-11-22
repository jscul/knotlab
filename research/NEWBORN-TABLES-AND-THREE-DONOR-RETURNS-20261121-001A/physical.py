"""Exact paid first rounds and complete three-reader character measurements."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EARLIER = ROOT / "research/SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001A/stage_observations.json.gz"
ORDINARY = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
ENGINE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py"
ENGINE_IMPORTS = (
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/joinlib.py",
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py",
    "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py",
    "experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/freelib.py",
)
LAWS = ("parity", "nae")
WIDTHS = (4, 5)


def _load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@cache
def _engine():
    native = _load("b298_old_growth", ENGINE)
    end = _load("b298_old_end", ORDINARY)
    source = native.J
    for observed, expected in zip((source, source.fastlib, source.S, source.F), ENGINE_IMPORTS, strict=True):
        assert Path(observed.__file__).resolve() == ROOT / expected
    return native, end


@cache
def _bits(n):
    return tuple(product((0, 1), repeat=n))


def _index(word):
    out = 0
    for bit in word:
        out = 2 * out + bit
    return out


def _pick(raw_word, names):
    return _index((raw_word >> b) & 1 for b in names)


def _sign(n):
    return (-1) ** n.bit_count()


def _allowed(law, values):
    k = sum(values)
    return k % 2 == 0 if law == "parity" else 0 < k < len(values)


def _owners(rows):
    owners = {}
    for k, row in enumerate(rows):
        assert tuple(sorted(set(row))) == row
        for v in row:
            owners.setdefault(v, []).append(k)
    assert all(0 < len(ks) <= 2 for ks in owners.values())
    return {v: tuple(owners[v]) for v in sorted(owners)}


def _actual_growth(width, law):
    native, end = _engine()
    source = (tuple(range(width)),)
    actual = native.S.from_junctions(source)
    original_owners = _owners(source)
    plan = end.step(end.from_stars(source), law)
    allocator = native.parity_rule(native.F.fewest) if law == "parity" else native.nae_rule(native.F.fewest)
    grants = []

    def inspect_rule(p, info, rng):
        fresh = allocator(p, info, rng)
        for entry, amount in zip(info, fresh, strict=True):
            grants.append({**entry, "issued_fresh": amount})
        return fresh

    result = actual.step(inspect_rule, None)
    if result is None:
        return {"ordinary_growth": {"outcome": "stalled", "original_rows": source, "funded_births": []},
                "occurrences": [], "launch": {"eligible": False, "quantum_read_called": False}}
    rows = tuple(tuple(row) for row in actual.bits_of)
    owners = _owners(rows)
    if not result["new"]:
        return {"ordinary_growth": {"outcome": "already_closed", "original_rows": source, "funded_births": []},
                "occurrences": [], "launch": {"eligible": False, "quantum_read_called": False}}
    assert actual.rounds == 1 and rows[:1] == source and plan.status == "extend"
    births = []
    for logged in grants:
        holder, p = logged["j"], logged["p"]
        paid = rows[holder][:p]
        fresh = rows[holder][p:]
        parents = tuple(original_owners[b][0] for b in paid)
        assert len(fresh) == logged["issued_fresh"] == actual.fresh[holder]
        assert all(owners[b] == (0, holder) for b in paid) and all(owners[b] == (holder,) for b in fresh)
        assert len(paid) == 1 and parents == (0,)
        births.append({"holder": holder, "parent_holders": parents, "paid_names": paid, "fresh_names": fresh,
                       "lookahead_demand": logged["d"], "fresh_grant": len(fresh), "full_named_support": rows[holder],
                       "zero_fresh_clause_of_the_law_invoked": logged["implied"] and not fresh})
    assert result["new"] == len(births) == width
    signature = Counter((e["parent_holders"], e["lookahead_demand"], e["fresh_grant"]) for e in births)
    assert signature == Counter(zip(plan.parents, plan.demand, plan.fresh, strict=True))
    assert sorted(b for e in births for b in e["paid_names"]) == list(source[0])
    fresh_names = tuple(b for b, h in owners.items() if len(h) == 1)
    spent_names = tuple(b for b, h in owners.items() if len(h) == 2)
    assert spent_names == source[0] and len(fresh_names) == sum(e["fresh_grant"] for e in births)
    assert all(len(e["fresh_names"]) == width - 1 for e in births)
    roster = {"outcome": "funded_first_complete_round", "original_rows": source, "reached_rows": rows,
              "actual_ordinary_rounds": actual.rounds, "funded_births": births, "holders_by_physical_name": owners,
              "all_spent_names_in_character_order": spent_names, "all_loose_names": fresh_names,
              "actual_stalled_or_closed_round": None, "all_original_loose_names_paid_once": True,
              "fresh_names_in_only_one_holder": True, "independent_complete_end_roster_agrees": True}
    return roster


def _full_old_and_local(roster, law):
    width = len(roster["all_spent_names_in_character_order"])
    roots = tuple(i for i, full in enumerate(_bits(width)) if _allowed(law, full))
    children = tuple(tuple(tuple(u for u in _bits(len(row["fresh_names"])) if _allowed(law, (s, *u))) for s in (0, 1))
                     for row in roster["funded_births"])
    parent_positions = tuple(roster["all_spent_names_in_character_order"].index(row["paid_names"][0])
                             for row in roster["funded_births"])
    words = {s: prod(len(child[_bits(width)[s][p]]) for p, child in zip(parent_positions, children, strict=True))
             for s in roots}
    assert all(words.values()) and len(children) == width
    return roots, children, parent_positions, words


@cache
def _canonical_check(width, allowed):
    variables = [f"x{i}" for i in range(width)]
    forbidden = [row for row in _bits(width) if _index(row) not in allowed]
    clauses = ";".join(" ".join(("~" if b else "") + v for b, v in zip(row, variables, strict=True)) for row in forbidden)
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", clauses,
           "--loops", *variables[:-1], "--contact", variables[-1], "--json"]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=ROOT, env={**os.environ, "PYTHONPATH":str(ROOT / "tools")})
    answer = json.loads(proc.stdout)
    assert {int(word, 2) for word in answer["allowed"]} == set(allowed)
    assert answer["is_knot"] and answer["binding"] and answer["loss_on_erasure"] and answer["coexistence"]
    return {k: answer[k] for k in ("is_knot", "binding", "loss_on_erasure", "coexistence")}


def _canonical_roster(roster, law, states, children, paid_positions):
    old = [{"holder": 0, "full_written_support": roster["original_rows"][0], "words_on_the_actual_projection": states}]
    grown = [dict(row) for row in old]
    for site, p, sides in zip(roster["funded_births"], paid_positions, children, strict=True):
        root_bits = set(_bits(len(paid_positions))[s][p] for s in states)
        words = tuple(sorted(_index((u, *fresh)) for u in root_bits for fresh in sides[u]))
        grown.append({"holder": site["holder"], "full_written_support": site["full_named_support"],
                      "words_on_the_actual_projection": words})
    for row in (*old, *grown):
        w = len(row["full_written_support"])
        included = row["words_on_the_actual_projection"]
        assert included == tuple(i for i, bits in enumerate(_bits(w)) if _allowed(law, bits))
        for clause in range(w):
            assert len({x & ~(1 << clause) for x in included}) == 1 << (w - 1)
        row["K1_K2_K3_and_actual_canonical_CNF_gate"] = _canonical_check(w, included)
    return {"before": old, "after": grown, "full_projected_written_rows_match_their_ordinary_law": True}


def _sat_projections(rows, expected, law):
    from pysat.solvers import Minisat22

    clauses = [tuple((-1 if bit else 1) * (mark + 1) for bit, mark in zip(word, physical, strict=True))
               for physical in rows for word in _bits(len(physical)) if not _allowed(law, word)]
    with Minisat22(bootstrap_with=clauses) as solver:
        for row, cert in zip(rows, expected, strict=True):
            fixed = tuple(i for i, test in enumerate(_bits(len(row))) if solver.solve(assumptions=[
                (-1 if not b else 1) * (mark + 1) for b, mark in zip(test, row, strict=True)]))
            assert fixed == cert["words_on_the_actual_projection"]
            cert["independent_CNF_model_feasibility_in_the_complete_named_relation"] = True


def _zeros():
    return [[0] * 8 for _ in range(8)]


def _sum_into(a, b, scale=1):
    for i in range(8):
        for j in range(8):
            a[i][j] += scale * b[i][j]


def _trace(g):
    return sum(g[i][i] for i in range(8))


def _rank_one(v):
    return [[a * b for b in v] for a in v]


def _cross(rows, cols):
    return [[sum(x * y for x, y in zip(a, b, strict=True)) for b in cols] for a in rows]


def _local_columns(fresh, marked, allowed):
    mark_pos = tuple(fresh.index(b) for b in marked)
    quiet = tuple(i for i in range(len(fresh)) if i not in mark_pos)
    c = [[0] * (1 << len(quiet)) for _ in range(8)]
    for value in allowed:
        x = _index(value[i] for i in mark_pos)
        r = _index(value[i] for i in quiet)
        c[x][r] = 1
    return c


def _pair_contraction(roster, roots, children, positions, site, marks):
    width = len(positions)
    basis = _bits(width)
    overlap = tuple(tuple(tuple(len(set(u) & set(v)) for v in child) for u in child) for child in children)
    columns = tuple(_local_columns(roster["funded_births"][site]["fresh_names"], marks, allow) for allow in children[site])
    local_grams = tuple(tuple(_cross(x, y) for y in columns) for x in columns)
    by_xor = [_zeros() for _ in basis]
    retained = _zeros()
    actual_tag_gram = [_zeros() for _ in basis]
    for s, t in product(roots, repeat=2):
        ss, tt = basis[s], basis[t]
        weights = prod(overlap[h][ss[slot]][tt[slot]] for h, slot in enumerate(positions) if h != site)
        block = local_grams[ss[positions[site]]][tt[positions[site]]]
        _sum_into(by_xor[s ^ t], block, weights)
        if s == t:
            _sum_into(retained, block, weights)
            _sum_into(actual_tag_gram[s], block, weights)
    assert retained == by_xor[0]
    char = []
    for h in range(len(basis)):
        mat = _zeros()
        for r, block in enumerate(by_xor):
            _sum_into(mat, block, _sign(h & r))
        char.append(mat)
    ignored = _zeros()
    for mat in char:
        _sum_into(ignored, mat)
    assert ignored == [[len(basis) * x for x in row] for row in retained]
    return {"retained": retained, "character_grams": char, "summed_character_grams": ignored,
            "per_spent_word_diagonal_tag_block": actual_tag_gram,
            "local_kept_spent_bit_versus_spent_bit_gram_blocks": local_grams,
            "complete_unread_peer_inner_products": overlap,
            "ordinary_independence_is_only_conditional_on_the_full_spent_word": True}


def _class_counts(law, width):
    cells = {}
    for row in _bits(width):
        count = sum(row)
        kind = (count % 2) if law == "parity" else 0 if not count else 1 if count == width else 2
        cells.setdefault(kind, []).append(row)
    return tuple((kind, table[0], len(table)) for kind, table in sorted(cells.items()))


def _end_population(roots, positions, law, roster):
    classes = tuple(_class_counts(law, row["fresh_grant"]) for row in roster["funded_births"])
    size = len(positions)
    actual = []
    hist = Counter()
    for end in product(*classes):
        n = sum(all(_allowed(law, (_bits(size)[s][p], *value))
                    for (_, value, _), p in zip(end, positions, strict=True)) for s in roots)
        multiplicity = prod(d[2] for d in end)
        hist[n] += multiplicity
        actual.append({"class_names_in_child_order": tuple(d[0] for d in end), "once_held_words_in_class": multiplicity,
                       "all_pasts_admitting_each_physical_loose_word_in_class": n})
    return {"class_rule": "0 even, 1 odd" if law == "parity" else "0 all zero, 1 all one, 2 mixed",
            "class_roster_of_each_child": classes, "complete_loose_count_by_named_class": actual,
            "histogram_of_past_fibre_sizes_including_zero": dict(sorted(hist.items())),
            "all_loose_words": sum(hist.values()), "allowed_loose_words": sum(hist.values()) - hist[0],
            "forbidden_loose_words": hist[0], "N": sum(k * v for k, v in hist.items()),
            "W": sum(k * k * v for k, v in hist.items())}


def _independent_class_transfer(roster, roots, positions, law, site, marked):
    size = len(positions)
    births = roster["funded_births"]
    selected = births[site]["fresh_names"]
    fixed_classes = tuple((h, _class_counts(law, e["fresh_grant"])) for h, e in enumerate(births) if h != site)
    ignored = tuple(b for b in selected if b not in marked)
    start, char = _zeros(), [_zeros() for _ in _bits(size)]
    for exterior in product(*(cells for h, cells in fixed_classes)):
        peers = [(_h, q) for (_h, cells), (kind, q, mass) in zip(fixed_classes, exterior, strict=True)]
        multiplicity = prod(t[2] for t in exterior)
        possible = [s for s in roots if all(_allowed(law, (_bits(size)[s][positions[h]], *q)) for h, q in peers)]
        for rest in _bits(len(ignored)):
            unmoved = dict(zip(ignored, rest, strict=True))
            local = {}
            for s in possible:
                choices = []
                for outcomes in _bits(3):
                    values = {**unmoved, **dict(zip(marked, outcomes, strict=True))}
                    choices.append(int(_allowed(law, (_bits(size)[s][positions[site]], *(values[b] for b in selected)))))
                local[s] = choices
                _sum_into(start, _rank_one(choices), multiplicity)
            for k, target in enumerate(char):
                coherent = [sum(_sign(s & k) * v[x] for s, v in local.items()) for x in range(8)]
                _sum_into(target, _rank_one(coherent), multiplicity)
    return start, char


def _literal_complete_words(roster, law):
    """Direct physical enumeration for the actual 16-name four-place result."""
    names, rows = roster["holders_by_physical_name"], roster["reached_rows"]
    assert len(names) == 16 and tuple(names) == tuple(range(16))
    masks = tuple(sum(1 << n for n in row) for row in rows)
    result = []
    for w in range(1 << len(names)):
        fills = tuple((mask & w).bit_count() for mask in masks)
        good = (all(v % 2 == 0 for v in fills) if law == "parity"
                else all(0 < v < len(r) for v, r in zip(fills, rows, strict=True)))
        if good:
            result.append(w)
    return result


def _literal_reduction(words, roster, marks):
    old = roster["all_spent_names_in_character_order"]
    remain = tuple(b for b in roster["all_loose_names"] if b not in marks)
    dim = 1 << len(old)
    contexts = {}
    for w in words:
        a, p, r = (_pick(w, names) for names in (marks, old, remain))
        if r not in contexts:
            contexts[r] = [[0] * 8 for _ in range(dim)]
        assert not contexts[r][p][a]
        contexts[r][p][a] = 1
    retained, chars = _zeros(), [_zeros() for _ in range(dim)]
    for r, contexts_matrix in contexts.items():
        for row in contexts_matrix:
            _sum_into(retained, _rank_one(row))
        values = [row[:] for row in contexts_matrix]
        half = 1
        while half < dim:
            for even in range(0, dim, half * 2):
                for j in range(even, even + half):
                    v, w = values[j], values[j + half]
                    values[j] = [x + y for x, y in zip(v, w, strict=True)]
                    values[j + half] = [x - y for x, y in zip(v, w, strict=True)]
            half *= 2
        for c, a in zip(chars, values, strict=True):
            _sum_into(c, _rank_one(a))
    return retained, chars


def _projected_probabilities(matrix, denom):
    """Direct real product bras. Retain the cross terms, even on signed ports."""
    rows = []
    for setting in range(8):
        fixed, variable = 7 ^ setting, setting
        total = (1 << variable.bit_count()) * denom
        line = []
        for outcome in range(8):
            selecting = [x for x in range(8) if x & fixed == outcome & fixed]
            coefficient = sum(matrix[x][y] * _sign((x ^ y) & outcome & variable) for x, y in product(selecting, repeat=2))
            line.append(Fraction(coefficient, total))
        assert min(line) >= 0
        assert sum(line) == Fraction(_trace(matrix), denom)
        rows.append(line)
    return rows


def _wald_check(matrix, probs):
    """Cross-check every product projector by its character expansion."""
    tr = _trace(matrix)
    for context, row in enumerate(probs):
        moments = []
        for selected in range(8):
            flips = context & selected
            seen = (~context & 7) & selected
            moments.append(sum(matrix[x][x ^ flips] * _sign(x & seen) for x in range(8)))
        assert row == [Fraction(sum(y * _sign(a & j) for j, y in enumerate(moments)), 8 * tr) for a in range(8)]


def _read_view(gram, original_launch_denominator=None):
    norm = _trace(gram)
    launch = original_launch_denominator if original_launch_denominator is not None else norm
    assert norm >= 0 and launch >= norm
    if norm:
        values = _projected_probabilities(gram, norm)
        _wald_check(gram, values)
        correlations = [sum(_sign(i) * q for i, q in enumerate(row)) for row in values]
        silent = None
        conditional = [[str(x) for x in row] for row in values]
        signed = str(correlations[7] - sum(correlations[i] for i in (1, 2, 4)))
        legacy = str(correlations[7] + sum(correlations[i] for i in (1, 2, 4)))
    else:
        assert not any(v for row in gram for v in row)
        values = [[0] * 8 for _ in range(8)]
        conditional, signed, legacy = None, None, None
        silent = "zero_probability_no_normalized_state_and_no_answer"
    mass = Fraction(norm, launch) if launch else Fraction(0)
    return {"gram": gram, "denominator": norm or None, "probabilities": conditional,
            "subnormalized_gram_denominator_per_initial_launch": launch or None, "launch_probability_of_this_branch": str(mass),
            "per_initial_launch_answer_masses_at_each_independent_setting": [[str(z * mass) for z in row] for row in values],
            "per_initial_launch_joint_setting_and_answer_masses_after_uniform_choices": [[str(z * mass / 8) for z in row] for row in values],
            "signed_M_XXX_minus_XZZ_ZXZ_ZZX": signed, "alternative_XXX_plus_XZZ_ZXZ_ZZX": legacy,
            "refusal_or_empty_branch": silent}


def _sum_matrices(mats):
    gram = _zeros()
    for g in mats:
        _sum_into(gram, g)
    return gram


def _readout(physical, total):
    all_chars = physical["character_grams"]
    count = len(all_chars)
    den = total * count
    retained, clean = physical["retained"], all_chars[0]
    assert _trace(retained) == total
    diag = [[clean[a][a] if a == b else 0 for b in range(8)] for a in range(8)]
    pooled = _sum_matrices(all_chars[1:])
    recovered = physical["summed_character_grams"]
    char_ports = {str(i): _read_view(gram, den) for i, gram in enumerate(all_chars)}
    assert sum(Fraction(x["launch_probability_of_this_branch"]) for x in char_ports.values()) == 1
    read = {
        "retained": _read_view(retained),
        "clean": char_ports["0"],
        "tag_present_clean": _read_view(retained, den),
        "tag_returned_clean": _read_view(clean, den),
        "diagonal": _read_view(diag, den),
        "diagonal_as_a_supplied_postulate_before_selection": _read_view(diag),
        "pure_counts_as_a_supplied_postulate_before_selection": _read_view(clean),
        "ignored_complete_character_instrument": _read_view(recovered, den),
        "complement_of_clean_herald": _read_view(pooled, den),
        "kept_tag_present_and_clean_herald_rejected": _read_view([[i * (count - 1) for i in r] for r in retained], den),
    }
    assert read["retained"]["probabilities"] == read["ignored_complete_character_instrument"]["probabilities"]
    assert read["retained"]["probabilities"] == read["tag_present_clean"]["probabilities"]
    assert read["clean"] == read["tag_returned_clean"]
    assert read["clean"]["probabilities"][0] == read["diagonal"]["probabilities"][0]
    assert read["diagonal"]["probabilities"][7] == ["1/8"] * 8
    assert Fraction(read["clean"]["launch_probability_of_this_branch"]) + Fraction(read["complement_of_clean_herald"]["launch_probability_of_this_branch"]) == 1
    tag_ports = {str(i): {"gram": g, "probability_of_port": str(Fraction(1, count))}
                 for i, g in enumerate([retained] * count)}
    return read, char_ports, {
        "tag_physically_held_but_value_not_delivered_to_reader": True,
        "all_character_ports_if_tag_is_still_physically_present": tag_ports,
        "conditional_Gram_denominator": total, "unconditional_Gram_denominator": den,
        "with_no_character_measurement_retained_tag_has_the_same_reduced_table": True,
        "projected_each_visible_orthogonal_tag_block_at_any_fixed_character": physical["per_spent_word_diagonal_tag_block"],
        "coherent_joint_tag_and_data_block_rule": ("For physically orthogonal spent strings s,t, the tag block on (s,t) at character j "
            "is (-1)^popcount(j&(s^t)) times the corresponding selected local Gram times the unread peer inner products. "
            "Its common per-launch denominator is the one given here."),
        "keeping_the_tag_removes_cross_terms_only_when_the_tag_is_ignored_or_resolved": True,
        "return_requires_a_supplied_controlled_inverse_before_character_measurement": True,
    }


def _reverse_bits(n, width):
    return _index((n >> j) & 1 for j in range(width))


def _archived_compare(stage, prior, *, actual_words):
    name, row = "single4/1/0", prior["structural_inventory"]["single4/1/0"][stage["law"]]
    now = stage["ordinary_growth"]
    actual = row["inventory_for_all_age_slots"][1]
    assert now["reached_rows"] == tuple(tuple(x) for x in actual["whole_named_rows"])
    raw = row["complete_round_roster_and_funding_replay"][0]["raw_outcome"]
    assert raw["status"] == "grown"
    for a, b in zip(now["funded_births"], raw["new"], strict=True):
        assert a["holder"] == b["holder"]
        assert a["fresh_grant"] == b["fresh"] and a["lookahead_demand"] == b["demand"]
        assert a["full_named_support"] == tuple(b["places"])
    hist = prior["built_histories"][name][stage["law"]]["bounded_numerical_stages"]["1"]
    old = hist["whole_current_weights"]
    assert old["N_complete_words"] == stage["end_fibres"]["N"] and old["W_sum_squared_past_counts"] == stage["end_fibres"]["W"]
    l = len(now["all_loose_names"])
    current_end = Counter(_pick(w, now["all_loose_names"]) for w in actual_words)
    for e in range(1 << l):
        assert current_end[e] == old["counts_by_current_word_int"][_reverse_bits(e, l)]
    compared = []
    for v, item in zip(hist["single_holder_results"], stage["occurrences"], strict=True):
        assert v["holder"] == item["holder"] and tuple(v["least_three_loose_names"]) == item["marked_names"]
        for original, new in (("unread_past_D", "retained"), ("pure_squared_count", "clean")):
            before = v["read"][original]
            after = stage["representative"][new]
            assert before["matrix_denominator"] == after["denominator"]
            assert after["gram"] == [[before["integer_matrix"][_reverse_bits(a, 3)][_reverse_bits(b, 3)] for b in range(8)]
                                     for a in range(8)]
            earlier = before["settings_and_scores"]
            assert Fraction(earlier["signed_M_XXX_minus_three_XZZ"]) == Fraction(after["signed_M_XXX_minus_XZZ_ZXZ_ZZX"])
            for s, x in enumerate(after["probabilities"]):
                code = "".join("XZ"[1 - b] for b in _bits(3)[s])
                p = earlier["every_joint_probability"][code]
                assert [Fraction(p["numerators"][_reverse_bits(j, 3)], p["denominator"]) for j in range(8)] == list(map(Fraction, x))
            compared.append({"holder": v["holder"], "marked_names": item["marked_names"], "preparation": new,
                             "score": after["signed_M_XXX_minus_XZZ_ZXZ_ZZX"], "all_sixty_four_cells_exactly_equal": True,
                             "raw_integer_Gram_exactly_matches": True})
    return {"case": name, "age": 1, "prior_bit_order": "Earlier integer table put first named reader in the least significant bit.",
            "explicit_answer_address_permutation": tuple(_reverse_bits(x, 3) for x in range(8)),
            "all_loose_fibres_checked_including_zero": 1 << l, "per_table": compared}


def _physical_permutation(roster, candidate, target_mark_order):
    births = roster["funded_births"]
    transported = tuple(candidate if i == 0 else 0 if i == candidate else i for i in range(len(births)))
    axes, holder_map = {}, {0: 0}
    for i, old in enumerate(births):
        new = births[transported[i]]
        holder_map[old["holder"]] = new["holder"]
        fresh = new["fresh_names"]
        if i == 0:
            fresh = (*target_mark_order, *(b for b in fresh if b not in target_mark_order))
        for x, y in zip((*old["paid_names"], *old["fresh_names"]), (*new["paid_names"], *fresh), strict=True):
            axes[x] = y
    assert set(axes) == set(axes.values()) == set(roster["holders_by_physical_name"])
    assert len(axes) == len(set(axes.values()))
    rows = roster["reached_rows"]
    assert all({axes[x] for x in row} == set(rows[holder_map[i]]) for i, row in enumerate(rows))
    assert tuple(axes[b] for b in births[0]["fresh_names"][:3]) == target_mark_order
    chars = []
    spent = roster["all_spent_names_in_character_order"]
    for incoming in _bits(len(spent)):
        send = dict(zip((axes[b] for b in spent), incoming, strict=True))
        chars.append(_index(send[b] for b in spent))
    return {"physical_name_renaming_from_representative": axes, "physical_holder_renaming": holder_map,
            "all_old_and_new_supports_preserved": True,
            "character_outcome_and_spent_tag_address_transport": tuple(chars)}


def _check_reader_permutation(readout, characters):
    results = {}
    for order in permutations(range(3)):
        axis = tuple(_index(word[i] for i in order) for word in _bits(3))
        for row in (*readout.values(), *characters.values()):
            gram, p = row["gram"], row["probabilities"]
            assert all(gram[a][b] == gram[axis[a]][axis[b]] for a, b in product(range(8), repeat=2))
            if p is not None:
                assert all(p[a][b] == p[axis[a]][axis[b]] for a, b in product(range(8), repeat=2))
        results["".join(map(str, order))] = axis
    return results


def _verify_literal_origins(words, roster, certificate, populations):
    for holder, scope in enumerate(roster["reached_rows"]):
        actual_projection = sorted({_pick(w, scope) for w in words})
        assert actual_projection == list(certificate["after"][holder]["words_on_the_actual_projection"])
    end_counts = Counter(_pick(w, roster["all_loose_names"]) for w in words)
    bins = Counter(end_counts.values())
    bins[0] = populations["all_loose_words"] - len(end_counts)
    assert dict(sorted(bins.items())) == populations["histogram_of_past_fibre_sizes_including_zero"]
    return [end_counts[x] for x in range(populations["all_loose_words"])]


def _site_addresses(roster, roots, children, positions, reference, axis_maps, direct_words):
    tested = []
    for site, birth in enumerate(roster["funded_births"]):
        for marked in combinations(birth["fresh_names"], 3):
            permutations_by_site = {}
            physical = _pair_contraction(roster, roots, children, positions, site, marked)
            assert physical["retained"] == reference["retained"]
            for order in permutations(range(3)):
                order_addr = "".join(map(str, order))
                targets = tuple(marked[i] for i in order)
                maps = _physical_permutation(roster, site, targets)
                transported = maps["character_outcome_and_spent_tag_address_transport"]
                for k, mapped in enumerate(transported):
                    assert reference["character_grams"][k] == physical["character_grams"][mapped]
                    assert reference["per_spent_word_diagonal_tag_block"][k] == physical["per_spent_word_diagonal_tag_block"][mapped]
                permutations_by_site[order_addr] = {"ordered_reader_names": targets, **maps,
                                                   "basis_setting_outcome_address_permutation_from_increasing_order": axis_maps[order_addr],
                                                   "all_port_integer_matrices_verified_via_relabeling": True}
            if direct_words is not None:
                direct_d, direct_ports = _literal_reduction(direct_words, roster, marked)
                assert direct_d == physical["retained"] and direct_ports == physical["character_grams"]
            tested.append({"holder": birth["holder"], "paid_name": birth["paid_names"][0], "marked_names": marked,
                           "unread_once_held_spectators": tuple(b for b in roster["all_loose_names"] if b not in marked),
                           "distinct_actual_loose_names_in_the_same_reached_holder": all(
                               roster["holders_by_physical_name"][b] == (birth["holder"],) for b in marked),
                           "reader_permutations": permutations_by_site, "representative_table_key": "representative",
                           "shown_by_literal_physical_enumeration_at_this_address": direct_words is not None,
                           "all_Grams_contracted_on_this_sorted_physical_subset": True})
    return tested


def _source_case(width, law, prior):
    roster = _actual_growth(width, law)
    if "ordinary_growth" in roster:
        return {"width": width, "law": law, **roster}
    states, children, positions, by_old = _full_old_and_local(roster, law)
    norms = _end_population(states, positions, law, roster)
    assert norms["N"] == sum(by_old.values())
    local_tests = _canonical_roster(roster, law, states, children, positions)
    _sat_projections(roster["original_rows"], local_tests["before"], law)
    _sat_projections(roster["reached_rows"], local_tests["after"], law)
    representative_marks = tuple(roster["funded_births"][0]["fresh_names"][:3])
    physical = _pair_contraction(roster, states, children, positions, 0, representative_marks)
    assert _trace(physical["character_grams"][0]) == norms["W"]
    contra_d, contra_ports = _independent_class_transfer(roster, states, positions, law, 0, representative_marks)
    assert contra_d == physical["retained"] and contra_ports == physical["character_grams"]
    readout, ports, retained_tag = _readout(physical, norms["N"])
    axes = _check_reader_permutation(readout, ports)
    direct_words = _literal_complete_words(roster, law) if width == 4 else None
    if direct_words is not None:
        assert len(direct_words) == norms["N"]
        direct_end = _verify_literal_origins(direct_words, roster, local_tests, norms)
    else:
        direct_end = None
    occurrence = _site_addresses(roster, states, children, positions, physical, axes, direct_words)
    assert len(occurrence) == {4: 4, 5: 20}[width]
    zero_ports = tuple(int(k) for k, row in ports.items() if row["denominator"] is None)
    full_complement = law == "nae" or all(len(row) % 2 == 0 for row in roster["reached_rows"])
    if full_complement:
        for matrix in (physical["retained"], *physical["character_grams"]):
            assert all(matrix[a ^ 7][b ^ 7] == matrix[a][b] for a, b in product(range(8), repeat=2))
        assert all(by_old[s] == by_old[s ^ ((1 << width) - 1)] for s in states)
    for raw in (physical["retained"], *physical["character_grams"]):
        assert min(raw[i][i] for i in range(8)) >= 0
    out = {
        "width": width, "law": law, "ordinary_growth": roster, "actual_full_local_projections": local_tests,
        "distinct_initial_source_words": states, "full_written_word_count_by_named_spent_word": by_old,
        "literal_fresh_word_numerators_for_width_four": direct_end, "end_fibres": norms,
        "representative_marked_names": representative_marks, "representative": readout, "occurrences": occurrence,
        "number_of_eligible_sorted_subsets": len(occurrence), "number_of_ordered_address_menus": 6 * len(occurrence),
        "character_ports": ports, "tag_before_and_after_filter": retained_tag,
        "independent_exact_checks": {"outside_pair_overlap_equals_class_transfer": True,
                                     "verified_every_actual_Gram_on_four_place_words_when_requested": width == 4,
                                     "whole_word_global_bit_complement_is_a_symmetry": full_complement,
                                     "checked_complement_on_every_Gram_cell_where_it_is_a_symmetry": full_complement},
        "factored_raw_state_data_after_the_funded_round": {
            "local_pair_gram_blocks_at_the_marked_child": physical["local_kept_spent_bit_versus_spent_bit_gram_blocks"],
            "other_fresh_output_spaces_are_fully_traced": physical["complete_unread_peer_inner_products"],
            "whole_preparation_uses_each_distinct_compatible_word_once": True},
        "launch": {"eligible": True, "origin_has_no_born_holder_at_age_zero": True,
                   "source_has_nonzero_written_support": bool(norms["N"]), "number_of_spent_names": width,
                   "initial_launch_mass": "1", "complete_measured_port_denominator": norms["N"] * (1 << width),
                   "W_clean_branch_integer_norm": norms["W"],
                   "all_clean_probability": readout["clean"]["launch_probability_of_this_branch"],
                   "all_other_character_ports_probability": readout["complement_of_clean_herald"]["launch_probability_of_this_branch"],
                   "clean_only_protocol_refusal_no_measurement_probability": readout["complement_of_clean_herald"]["launch_probability_of_this_branch"],
                   "all_character_ports_with_zero_probability": zero_ports,
                   "same_filter_on_an_unreturned_orthogonal_tag": readout["tag_present_clean"]["launch_probability_of_this_branch"],
                   "diagonal_eq_loose_collisions_across_two_independent_words": str(Fraction(norms["W"], norms["N"] ** 2)),
                   "number_of_refusal_trials_imputed_as_reader_answers": 0,
                   "settings_chosen_independently_after_the_port_is_observed": True,
                   "clean_only_refusal_reason": "A nonzero character outcome is an actual complementary port, retained in the launch ledger."}}
    if direct_words is not None:
        out["B252_four_place_verbatim_archive_comparison"] = _archived_compare(out, prior, actual_words=direct_words)
    return out


def run():
    """Return the four frozen physical cases as JSON-compatible data."""
    with gzip.open(EARLIER, "rt") as f:
        previous = json.load(f)
    sources = {str(width): {law: _source_case(width, law, previous) for law in LAWS} for width in WIDTHS}
    inputs = (Path(__file__).resolve(), HERE / "preregistration.md", EARLIER, ORDINARY, ENGINE,
              *(ROOT / rel for rel in ENGINE_IMPORTS))
    return {"sources": sources, "binary_labels": {"setting_digits_in_lexicographic_order": _bits(3),
              "answers_in_lexicographic_order": _bits(3), "character_slots_use_physical_spent_names_in_order": True,
              "first_named_reader_is_most_significant": True, "setting_zero_is_Z": True, "outcome_zero_is_plus_one": True},
            "actual_growth_and_supplied_measurement": ("The complete ordinary round pays old names and assigns fresh names. "
                "The real X projectors, all-character filter and orthogonal tag return are supplied operations on declared preparations."),
            "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs},
            "frozen_canonical_checker_hashes_normalized_for_public_guide_title": {
                str(p.relative_to(ROOT)): sha256(p.read_bytes().replace(b"docs/KNOT_INTUITION.md", b"INTUITIONS.md")).hexdigest()
                for p in sorted((ROOT / "tools/knotlab").glob("*.py"))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    opts = parser.parse_args()
    if opts.smoke:
        with gzip.open(EARLIER, "rt") as f:
            prior = json.load(f)
        a = _source_case(4, "nae", prior)
        print(json.dumps({"verified_eligible_children": a["number_of_eligible_sorted_subsets"],
                          "ordinary_N": a["end_fibres"]["N"], "clean_W": a["end_fibres"]["W"],
                          "printed_characters": len(a["character_ports"])}, sort_keys=True))
        return
    output = json.dumps(run(), sort_keys=True, separators=(",", ":")).encode()
    print(f"{len(output)} canonical JSON bytes, SHA-256 {sha256(output).hexdigest()}")


if __name__ == "__main__":
    main()
