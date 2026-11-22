"""Literal paid newborn words, disclosed siblings, and lawful announcement banks."""

import argparse
from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import lcm
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "research/NEWBORN-TABLES-AND-THREE-DONOR-RETURNS-20261121-001A"
OLD_ARTIFACT = PREVIOUS / "newborn_evidence.json.gz"
ENGINE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py"
END = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
LATCH = ROOT / "research/TWO-KNOTS-ONE-DECISION-20261121-001/measurement.py"
ENGINE_IMPORTS = (
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/joinlib.py",
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py",
    "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py",
    "experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/freelib.py",
)
LAWS = ("parity", "nae")
TARGET = F(1, 28)
ROOT_SUPPORT = ((0, 1, 2, 3),)


def _module(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@cache
def _ancestors():
    old = _module("b300_growth", ENGINE)
    independent = _module("b300_end", END)
    modules = (old.J, old.J.fastlib, old.J.S, old.F)
    for actual, needed in zip(modules, ENGINE_IMPORTS, strict=True):
        assert Path(actual.__file__).resolve() == ROOT / needed
    return old, independent


@cache
def _bits(width):
    return tuple(product((0, 1), repeat=width))


def _word(bits):
    n = 0
    for b in bits:
        n = 2 * n + b
    return n


def _pick(raw, names):
    return _word((raw >> b) & 1 for b in names)


def _embed(value, names):
    b = _bits(len(names))[value]
    return sum(x << n for x, n in zip(b, names, strict=True))


def _name_owners(rows):
    owners = {}
    for h, row in enumerate(rows):
        assert len(set(row)) == len(row)
        for n in row:
            owners.setdefault(n, []).append(h)
    assert all(len(h) in (1, 2) for h in owners.values())
    return {n: tuple(owners[n]) for n in sorted(owners)}


def _allowed(bits, law):
    return sum(bits) % 2 == 0 if law == "parity" else min(bits) != max(bits)


def _grow(rows, law):
    old, _ = _ancestors()
    presentation = old.S.from_junctions(rows)
    first = _name_owners(rows)
    raw_rule = old.parity_rule(old.F.fewest) if law == "parity" else old.nae_rule(old.F.fewest)
    each_grant = []

    def rule(state, proposed, rng):
        grants = raw_rule(state, proposed, rng)
        each_grant.extend({**entry, "grant": g} for entry, g in zip(proposed, grants, strict=True))
        return grants

    result = presentation.step(rule, None)
    after = tuple(tuple(row) for row in presentation.bits_of)
    second = _name_owners(after)
    events = []
    for step in each_grant:
        knot, p = step["j"], step["p"]
        paid, fresh = after[knot][:p], after[knot][p:]
        assert all(len(first[x]) == 1 and second[x] == (*first[x], knot) for x in paid)
        assert all(x not in first and second[x] == (knot,) for x in fresh)
        assert len(fresh) == step["grant"] == presentation.fresh[knot]
        events.append({"holder": knot, "parent_holders": tuple(first[v][0] for v in paid),
                       "paid_names": paid, "fresh_names": fresh, "lookahead_demand": step["d"],
                       "fresh_grant": step["grant"], "used_implication_exception": not fresh and step["implied"]})
    if events:
        assert result["new"] == len(events) and presentation.rounds == 1
        assert after[:len(rows)] == rows
        assert Counter(b for event in events for b in event["paid_names"]) == Counter(v for v, h in first.items() if len(h) == 1)
    status = "stalled" if result is None else "funded" if result["new"] else "closed"
    return result, {"status": status, "original": rows, "reached": after, "births": events}


@cache
def _canonical(width, allowed):
    names = tuple(f"x{i}" for i in range(width))
    clauses = [" ".join(("~" if bit else "") + m for bit, m in zip(values, names, strict=True))
               for i, values in enumerate(_bits(width)) if i not in allowed]
    args = (sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
            "--loops", *names[:-1], "--contact", names[-1], "--json")
    verified = subprocess.check_output(args, text=True, cwd=ROOT, env={**os.environ, "PYTHONPATH":str(ROOT / "tools")})
    row = json.loads(verified)
    assert {int(w, 2) for w in row["allowed"]} == set(allowed)
    assert row["binding"] and row["loss_on_erasure"] and row["coexistence"] and row["is_knot"]
    return {"K1": row["binding"], "K2": row["loss_on_erasure"], "K3": row["coexistence"], "canonical_check": True}


def _projection(words, names, law):
    actual = tuple(sorted({_pick(w, names) for w in words}))
    oracle = tuple(value for value, val in enumerate(_bits(len(names))) if _allowed(val, law))
    assert oracle == actual
    return {"names": names, "allowed_projected_word_indices": actual,
            "loss_of_constraint_on_each_named_erasure": tuple(len({w & ~(1 << j) for w in actual}) for j in range(len(names))),
            **_canonical(len(names), actual)}


def _ordinary_roster(law, before):
    result, raw = _grow(ROOT_SUPPORT, law)
    if len(raw["births"]) != 4:
        return dict(raw, source_refusal="missing birth in the complete first round")
    if any(len(b["paid_names"]) != 1 or len(b["fresh_names"]) != 3 for b in raw["births"]):
        return dict(raw, source_refusal="missing paid or fresh name in a funded birth")
    prior = before["ordinary_growth"]
    assert raw["reached"] == tuple(tuple(r) for r in prior["reached_rows"])
    assert len(raw["births"]) == result["new"] == 4
    for a, b in zip(raw["births"], prior["funded_births"], strict=True):
        for names in ("paid_names", "parent_holders", "fresh_names"):
            assert a[names] == tuple(b[names])
        assert all(a[x] == b[x] for x in ("holder", "fresh_grant", "lookahead_demand"))
    _, end = _ancestors()
    plan = end.step(end.from_stars(ROOT_SUPPORT), law)
    assert plan.status == "extend" and Counter(zip(plan.parents, plan.demand, plan.fresh, strict=True)) == Counter(
        (r["parent_holders"], r["lookahead_demand"], r["fresh_grant"]) for r in raw["births"])
    owners = _name_owners(raw["reached"])
    spent = tuple(v for v, hs in owners.items() if len(hs) == 2)
    loose = tuple(v for v, hs in owners.items() if len(hs) == 1)
    assert spent == ROOT_SUPPORT[0] and len(loose) == 12
    assert tuple(owners) == tuple(range(16))
    ordered = tuple(sorted(raw["births"], key=lambda r: r["paid_names"]))
    focal = ordered[0]
    local = tuple(sorted(focal["fresh_names"]))
    sibling = tuple(n for h in ordered[1:] for n in sorted(h["fresh_names"]))
    assert len(local) == 3 and len(sibling) == 9 and set(sibling).union(local) == set(loose)
    return {**raw, "ordered_births": ordered, "paid_names": spent, "focal_holder": focal["holder"],
            "focal_read_order": local, "sibling_read_order": sibling, "owners": owners,
            "focal_paid_name": focal["paid_names"][0], "exact_archive_and_independent_end_operator_rosters_checked": True}


def _physical_words(rows, law):
    masks = tuple(sum(1 << p for p in support) for support in rows)
    assert len(_name_owners(rows)) == 16
    words = []
    for w in range(65536):
        if law == "parity":
            okay = all((w & mask).bit_count() % 2 == 0 for mask in masks)
        else:
            okay = all(w & mask not in (0, mask) for mask in masks)
        if okay:
            words.append(w)
    return words


def _word_fibres(words, roster):
    bank = [[0] * 16 for _ in range(512)]
    for w in words:
        s, x, r = (_pick(w, roster[k]) for k in ("paid_names", "focal_read_order", "sibling_read_order"))
        assert not (bank[r][s] >> x & 1)
        bank[r][s] |= 1 << x
    return bank


def _conditional_supports(roster, law):
    inputs = tuple(roster["paid_names"].index(k["paid_names"][0]) for k in roster["ordered_births"])
    original = tuple(s for s, bits in enumerate(_bits(4)) if _allowed(bits, law))
    pupil = tuple(tuple(x for x, v in enumerate(_bits(3)) if _allowed((s, *v), law)) for s in (0, 1))
    bins = []
    for r in _bits(9):
        allowed_each_sibling = tuple(tuple(s for s in (0, 1) if _allowed((s, *r[3 * j:3 * j + 3]), law)) for j in range(3))
        possible = tuple(s for s in original if all(_bits(4)[s][i] in hit
                         for i, hit in zip(inputs[1:], allowed_each_sibling, strict=True)))
        s0 = tuple(s for s in possible if not _bits(4)[s][inputs[0]])
        s1 = tuple(s for s in possible if _bits(4)[s][inputs[0]])
        block = [0] * 16
        for bit, target in enumerate((s0, s1)):
            for s in target:
                block[s] = sum(1 << x for x in pupil[bit])
        bins.append((block, (s0, s1), pupil, allowed_each_sibling))
    return bins


def _zero():
    return tuple((0,) * 8 for _ in range(8))


def _outer(values):
    return tuple(tuple(u * v for v in values) for u in values)


def _add(a, b):
    return tuple(tuple(u + v for u, v in zip(x, y, strict=True)) for x, y in zip(a, b, strict=True))


def _scale(a, v):
    return tuple(tuple(t * v for t in row) for row in a)


def _trace(a):
    return sum(a[i][i] for i in range(8))


def _matsum(seq):
    result = _zero()
    for matrix in seq:
        result = _add(result, matrix)
    return result


def _walsh(xs):
    rows = [tuple(x) for x in xs]
    width = 1
    assert len(rows) == 16
    while width <= 8:
        for k in range(0, 16, 2 * width):
            for i in range(k, k + width):
                a, b = rows[i], rows[i + width]
                rows[i] = tuple(x + y for x, y in zip(a, b, strict=True))
                rows[i + width] = tuple(x - y for x, y in zip(a, b, strict=True))
        width *= 2
    return rows


def _grams_of_word_fibre(masks):
    vectors = [tuple((p >> x) & 1 for x in range(8)) for p in masks]
    past_read = tuple(_outer(row) for row in vectors)
    char_columns = _walsh(vectors)
    return _matsum(past_read), tuple(_outer(v) for v in char_columns), past_read, tuple(char_columns)


def _compare_class_contraction(block, claim):
    # Count the two focal-parent values independently, after testing actual sibling rows.
    masks, spent_lists, local, _ = block
    v0, v1 = (tuple(int(x in values) for x in range(8)) for values in local)
    raw, chars, _, amps = claim
    predicted = _add(_scale(_outer(v0), len(spent_lists[0])), _scale(_outer(v1), len(spent_lists[1])))
    assert raw == predicted
    for k in range(16):
        m0, m1 = (sum((-1) ** (s & k).bit_count() for s in seen) for seen in spent_lists)
        v = tuple(m0 * a + m1 * b for a, b in zip(v0, v1, strict=True))
        assert v == amps[k] and chars[k] == _outer(v)


def _signed_table(gram):
    # Explicit product projectors in the ordinary basis, prior to division by the trace.
    by_setting = []
    for setting in range(8):
        context = []
        z = 7 ^ setting
        denom = 1 << setting.bit_count()
        for output in range(8):
            vectors = tuple((i, (-1) ** (i & output & setting).bit_count())
                            for i in range(8) if (i & z) == (output & z))
            numerator = sum(sign_x * sign_y * gram[x][y] for x, sign_x in vectors for y, sign_y in vectors)
            context.append(F(numerator, denom))
        by_setting.append(tuple(context))
    return tuple(by_setting)


def _check_projectors(gram, table):
    # Reconstruct each entry from its eight signed product moments.
    for setting, row in enumerate(table):
        moments = tuple(sum((-1) ** (x & mask & (7 ^ setting)).bit_count() * gram[x][x ^ (mask & setting)]
                            for x in range(8)) for mask in range(8))
        assert all(8 * value == sum((-1) ** (mask & a).bit_count() * m for mask, m in enumerate(moments))
                   for a, value in enumerate(row))
        assert sum(row) == _trace(gram) and min(row) >= 0


def _score(table, c):
    demand = 7 if c else 0
    reward = sum(table[7][a] for a in (3, 5, 6, 7))
    charged = sum(table[setting][a] for setting in (1, 2, 4) for a in range(8)
                  if a & setting and (a & (7 ^ setting)) != (demand & (7 ^ setting)))
    return reward - table[0][demand] - charged


def _strategies():
    scores = {}
    for c in (0, 1):
        values = []
        for choices in _bits(6):
            row = [[0] * 8 for _ in range(8)]
            for setting, bits in enumerate(_bits(3)):
                answer = _word(choices[2 * i + b] for i, b in enumerate(bits))
                row[setting][answer] = 1
            values.append(_score(row, c))
        assert max(values) == 0
        scores[str(c)] = {"maximum": max(values), "minimum": min(values), "values": values}
    return {"list_order": "lexicographic Z1,X1,Z2,X2,Z3,X3", "scores": scores}


def _encode_table(table, denominator):
    return [[str(q / denominator) for q in row] for row in table] if denominator else None


class _Grams:
    def __init__(self):
        self.ids = {}
        self.matrices = []
        self.tables = []
        self.probabilities = []
        self.scores = []

    def index(self, gram):
        if gram not in self.ids:
            i = len(self.matrices)
            self.ids[gram] = i
            self.matrices.append(gram)
            table = _signed_table(gram)
            _check_projectors(gram, table)
            self.tables.append(table)
            self.probabilities.append(_encode_table(table, _trace(gram)))
            self.scores.append(tuple(_score(table, c) for c in (0, 1)))
        return self.ids[gram]

    def packet(self, gram, launch_den, prepared_den=None):
        i = self.index(gram)
        weight = _trace(gram)
        claim, reverse = self.scores[i]
        assert weight or (gram == _zero() and claim == 0 == reverse)
        loss = weight * TARGET - claim
        return {"gram": i, "weight": weight, "I0": str(claim / weight) if weight else None,
                "I1": str(reverse / weight) if weight else None, "wI0": str(claim), "wI1": str(reverse),
                "loss": str(loss), "excess": str(-loss), "original_launch_denominator": launch_den,
                "original_launch_probability": str(F(weight, launch_den)),
                "prepared_source_denominator": prepared_den or launch_den,
                "prepared_source_probability": str(F(weight, prepared_den or launch_den))}


def _diagonal(gram):
    return tuple(tuple(v if y == x else 0 for y, v in enumerate(row)) for x, row in enumerate(gram))


def _archive_port(gram, actual, den, library):
    i = library.index(gram)
    w = _trace(gram)
    assert gram == tuple(tuple(q) for q in actual["gram"])
    assert w == actual["denominator"]
    assert den == actual["subnormalized_gram_denominator_per_initial_launch"]
    assert F(w, den) == F(actual["launch_probability_of_this_branch"])
    assert library.probabilities[i] == actual["probabilities"]
    assert _encode_table(library.tables[i], den) == actual["per_initial_launch_answer_masses_at_each_independent_setting"]
    assert _encode_table(library.tables[i], 8 * den) == actual["per_initial_launch_joint_setting_and_answer_masses_after_uniform_choices"]


def _archive_table(gram, actual, library):
    assert gram == tuple(tuple(q) for q in actual["gram"])
    assert _trace(gram) == actual["denominator"]
    assert library.probabilities[library.index(gram)] == actual["settings"]


def _relabelling(roster, words, actual, claims, library):
    word_set = set(words)
    assert all((w ^ 65535) in word_set for w in words)
    for r, (d, chars, _, _) in enumerate(claims):
        opposite = r ^ 511
        all_opposite = actual[opposite]
        for s in range(16):
            assert all_opposite[s ^ 15] == sum(1 << (x ^ 7) for x in range(8) if (actual[r][s] >> x) & 1)
        target = claims[opposite]
        for i, (gram, complemented) in enumerate(zip((d, *chars), (target[0], *target[1]), strict=True)):
            assert all(gram[x][y] == complemented[x ^ 7][y ^ 7] for x in range(8) for y in range(8))
            j, k = library.index(gram), library.index(complemented)
            assert library.scores[j][0] == library.scores[k][1]
            if i:
                phase = (-1) ** (i - 1).bit_count()
                assert all(claims[r][3][i - 1][x] == phase * target[3][i - 1][x ^ 7] for x in range(8))
    direct = []
    births = roster["ordered_births"]
    banks = tuple(tuple(sorted(h["fresh_names"])) for h in births)
    donors = roster["paid_names"]
    reached = {frozenset(row) for row in roster["reached"]}
    for focus in range(4):
        new_order = dict(roster, focal_read_order=banks[focus],
                         sibling_read_order=tuple(n for k, bank in enumerate(banks) if k != focus for n in bank))
        map_name = list(range(16))
        first, second = (donors[0], *banks[0]), (donors[focus], *banks[focus])
        for a, b in zip(first, second, strict=True):
            map_name[a], map_name[b] = map_name[b], map_name[a]
        assert {frozenset(map_name[b] for b in row) for row in reached} == reached
        assert tuple(map_name[n] for n in roster["focal_read_order"]) == new_order["focal_read_order"]
        fresh_basis = tuple(roster["sibling_read_order"].index(map_name[n]) for n in new_order["sibling_read_order"])
        past_basis = tuple(donors.index(map_name[n]) for n in donors)
        new_exterior = tuple(_word(bits[i] for i in fresh_basis) for bits in _bits(9))
        new_past = tuple(_word(bits[i] for i in past_basis) for bits in _bits(4))
        observed = actual if not focus else _word_fibres(words, new_order)
        for r, q in enumerate(new_exterior):
            assert observed[q] == [actual[r][p] for p in new_past]
        direct.append({"focal_holder": births[focus]["holder"], "after_paid_name": donors[focus],
                       "focal_read_order": new_order["focal_read_order"], "sibling_read_order": new_order["sibling_read_order"],
                       "physical_name_image_by_index": map_name, "spent_word_and_character_image": new_past,
                       "sibling_bit_image": fresh_basis, "matched_literal_full_fibres": True})
    return {"all_physical_complements_legal": True, "opposite_orientation_table_and_all_characters_match": True,
            "focal_birth_transports": direct}


def _archive_reconciliation(prior, reconstruction, natural, words, source_roster, rows, library):
    retained, chars, paid_rows = natural
    clean = chars[0]
    N, W = len(words), _trace(clean)
    assert (N, W) == tuple(prior["end_fibres"][k] for k in ("N", "W"))
    assert sum(_trace(g) for g in chars) == 16 * N
    assert _matsum(chars) == _scale(retained, 16)
    assert list(source_roster["focal_read_order"]) == prior["representative_marked_names"]
    all_pasts = Counter(_pick(raw, source_roster["paid_names"]) for raw in words)
    assert {str(s): n for s, n in all_pasts.items()} == prior["full_written_word_count_by_named_spent_word"]
    loose = source_roster["focal_read_order"] + source_roster["sibling_read_order"]
    loose_fibres = Counter(_pick(w, loose) for w in words)
    assert [loose_fibres[x] for x in range(4096)] == prior["literal_fresh_word_numerators_for_width_four"]
    launch = 16 * N
    recheck = {}
    for h, gram in enumerate(chars):
        a = prior["character_ports"][str(h)]
        b = reconstruction["character_ports"][f"{h:04b}"]
        _archive_port(gram, a, launch, library)
        assert F(b["launch"]) == F(_trace(gram), launch)
        _archive_table(gram, b["table"], library)
        held = prior["tag_before_and_after_filter"]["all_character_ports_if_tag_is_still_physically_present"][str(h)]
        assert retained == tuple(tuple(q) for q in held["gram"])
        assert F(held["probability_of_port"]) == F(1, 16)
    cases = reconstruction["cases"]
    for name, matrix in {"retained": retained, "clean": clean}.items():
        _archive_table(matrix, cases[name], library)
    for c, matrix in enumerate(paid_rows):
        name = f"retained_disclosed_paid_{c}"
        _archive_table(matrix, cases[name], library)
        assert F(_trace(matrix), N) == F(cases[name]["selection_probability"])
        recheck[name] = library.packet(matrix, N)
    representative = {
        "retained": (retained, N),
        "clean": (clean, launch),
        "complement_of_clean_herald": (_matsum(chars[1:]), launch),
        "tag_present_clean": (retained, launch),
        "tag_returned_clean": (clean, launch),
        "diagonal": (_diagonal(clean), launch),
        "ignored_complete_character_instrument": (_matsum(chars), launch),
        "kept_tag_present_and_clean_herald_rejected": (_scale(retained, 15), launch),
        "diagonal_as_a_supplied_postulate_before_selection": (_diagonal(clean), W),
        "pure_counts_as_a_supplied_postulate_before_selection": (clean, W),
    }
    assert representative.keys() == prior["representative"].keys()
    for name, (gram, den) in representative.items():
        _archive_port(gram, prior["representative"][name], den, library)
        recheck[name] = library.packet(gram, den)
    previous = reconstruction["actual_exterior_conditioning"]
    exteriors = {}
    for c, r in ((0, 0), (1, 511)):
        old = previous[str(c)]
        a, b = rows[r]["retained"], rows[r]["clean"]
        assert rows[r]["r"] == old["values_of_the_nine_unread_fresh"]
        assert sorted(rows[r]["compatible_spent_by_focal_paid"][0] + rows[r]["compatible_spent_by_focal_paid"][1]) == sorted(
            _word(s) for s in old["compatible_past_words"])
        assert a["original_launch_probability"] == old["retained_exterior_probability"]
        assert b["prepared_source_probability"] == old["exterior_probability_given_clean"]
        assert b["original_launch_probability"] == old["joint_clean_and_exterior_launch"]
        for mode, data in (("retained", a), ("clean", b)):
            _archive_table(library.matrices[data["gram"]], old[f"{mode}_table"], library)
            if "simple_separator" in old:
                assert F(data[f"I{c}"]) == F(old["simple_separator"]["gap"])
        exteriors[str(c)] = {"r": r, "matched_orientation": c,
                             "retained": a, "clean": b}
    for mode, den, prepared in (("retained", N, N), ("clean", launch, W)):
        both = _add(*(library.matrices[rows[r][mode]["gram"]] for r in (0, 511)))
        _archive_table(both, previous[f"accept_both_orientations_without_identifying_them_{mode}"], library)
        exteriors[f"undisclosed_union_{mode}"] = library.packet(both, den, prepared)
    return {"all_16_character_ports_matched_archived_tables_and_original_launch_masses": True,
            "all_reconstruction_comparisons": recheck, "actual_exterior_comparisons": exteriors}


def _law_source(law, prior, archived, library):
    roster = _ordinary_roster(law, prior)
    if "source_refusal" in roster:
        return {"status": "source_refusal", "reason": roster["source_refusal"], "ordinary": roster}
    words = _physical_words(roster["reached"], law)
    if not words:
        return {"status": "source_refusal", "reason": "empty ordinary source support", "ordinary": roster}
    places = tuple(_projection(words, names, law) for names in roster["reached"])
    for geometry, old in zip(places, prior["actual_full_local_projections"]["after"], strict=True):
        assert list(geometry["names"]) == old["full_written_support"]
    actual = _word_fibres(words, roster)
    contracted = _conditional_supports(roster, law)
    claims = []
    for masks, block in zip(actual, contracted, strict=True):
        assert masks == block[0]
        g = _grams_of_word_fibre(masks)
        _compare_class_contraction(block, g)
        assert _matsum(g[1]) == _scale(g[0], 16)
        claims.append(g)
    retained = _matsum(g[0] for g in claims)
    chars = tuple(_matsum(g[1][h] for g in claims) for h in range(16))
    N, W = len(words), _trace(chars[0])
    assert _trace(retained) == N and W
    launch_den = 16 * N
    rows = []
    for r, ((_masks, past, focal, sibling), (d, port, _tag, amp)) in enumerate(zip(contracted, claims, strict=True)):
        w_plain, w_herald = _trace(d), _trace(port[0])
        assert w_plain == sum(p.bit_count() for p in actual[r])
        assert w_plain == sum(len(s) * len(f) for s, f in zip(past, focal, strict=True))
        assert w_herald == sum(v * v for v in amp[0])
        rows.append({
            "r": f"{r:09b}", "r_index": r, "literal_word_count": w_plain, "empty": w_plain == 0,
            "compatible_spent_by_focal_paid": past, "true_parent_support_counts": tuple(map(len, past)),
            "focal_masks_by_spent_word": actual[r], "allowed_paid_input_by_sibling_block": sibling,
            "retained": library.packet(d, N, N), "clean": library.packet(port[0], launch_den, W),
            "character_grams": [library.index(one) for one in port],
            "character_traces": [_trace(one) for one in port],
        })
    paid = tuple(_matsum(g[2][s] for g in claims for s in range(16) if s >> 3 == c) for c in (0, 1))
    assert _add(*paid) == retained
    compare = _archive_reconciliation(prior, archived, (retained, chars, paid), words, roster, rows, library)
    relabel = _relabelling(roster, words, actual, claims, library)
    controls = {}
    for mode, table, launch, prepared in (("retained", retained, N, N), ("clean", chars[0], launch_den, W)):
        all_read = library.packet(table, launch, prepared)
        absent = library.packet(_zero(), launch, prepared)
        controls[mode] = {"all": {"go": all_read, "no": absent}, "none": {"go": absent, "no": all_read}}
    no_bank = _bank_controls(law, roster, words)
    rates = {mode: _independent_rates(rows, mode, launch, prepared)
             for mode, launch, prepared in (("retained", N, N), ("clean", launch_den, W))}
    same_decision = _coarse_same_flag(actual, claims, roster, N, W, library)
    return {
        "status": "funded_and_admitted", "N": N, "W": W, "source_refusal": {"retained": "0", "clean": str(1 - F(W, launch_den))},
        "ordinary": roster, "reached_full_projections": places, "transport": relabel,
        "literal_complete_words_lsb_name_zero": words,
        "number_of_complete_words_examined": 65536,
        "number_of_impossible_sibling_words": sum(row["empty"] for row in rows),
        "rows": rows, "declined_announcement_controls": controls,
        "launch_character_denominator": launch_den,
        "unannounced_character_ports": [library.packet(g, launch_den) for g in chars],
        "unannounced_retained": library.packet(retained, N),
        "unannounced_clean": library.packet(chars[0], launch_den, W),
        "archive": compare, "keeper": no_bank, "coarse_same_flag": same_decision, "independent_primary_rates": rates,
        "all_literal_fibres_and_characters_match_the_independent_contraction": True,
        "every_mask_summed_over_all_16_spent_ports_recovers_retained": True,
    }


def _bank_controls(law, roster, words):
    announcement = (16, 17, 18)
    status = (19, 20, 21)
    source_rows = roster["reached"]
    attached = (*source_rows, announcement, status)
    permitted = tuple(n for n, values in enumerate(_bits(3)) if _allowed(values, law))
    ready, yes, no = (int(word, 2) for word in ("110", "101", "011"))
    names = _name_owners(attached)
    assert all(len(names[b]) == 1 for b in (*announcement, *status))
    assert not (set(announcement) & set(status) or set(announcement + status) & set(roster["owners"]))
    # The two separate complete factors have explicit extensions over every lawful source word.
    a_ext, b_ext = (_embed(ready, h) for h in (announcement, status))
    projections = tuple(_projection(tuple(words[0] | _embed(i, bank) | other for i in permitted), bank, law)
                        for bank, other in ((announcement, b_ext), (status, a_ext)))
    assert all(_pick(w | a_ext | b_ext, tuple(range(16))) == _pick(w, tuple(range(16))) for w in words)
    source_projection_by_holder = [
        _projection(tuple(w | a_ext | b_ext for w in words), holding, law) for holding in source_rows
    ]
    fixed_effects = (
        ("source_admitted_and_go", True, True, True, ready),
        ("source_admitted_and_declines", True, False, True, ready),
        ("source_refused", False, True, True, ready),
        ("public_writer_disconnected_predicate_true", True, True, False, ready),
        ("announcement_bank_already_holds_yes", True, True, True, yes),
    )

    def exchange(w, bank, first, second):
        a, b = bank[first], bank[second]
        assert (w >> a & 1) != (w >> b & 1)
        image = w ^ (1 << a) ^ (1 << b)
        assert _pick(image, bank) in permitted
        return image, (a, b)

    def valuation(w, enabled, passed, connected, initial):
        first = w | _embed(initial, announcement) | _embed(ready, status)
        after_source, source_swap = exchange(first, status, *((1, 2) if enabled else (0, 2)))
        did_write = enabled and connected and (initial == ready)
        if did_write:
            final, announcement_swap = exchange(after_source, announcement, *((1, 2) if passed else (0, 2)))
        else:
            final, announcement_swap = after_source, ()
        expected = (yes if passed else no) if did_write else initial
        assert _pick(final, announcement) == expected
        assert _pick(final, status) == (yes if enabled else no)
        assert final & 65535 == w
        return first, final, source_swap, announcement_swap, did_write

    effects = {}
    for label, enabled, passed, connected, initial in fixed_effects:
        first, final, source_swap, announcement_swap, did_write = valuation(words[0], enabled, passed, connected, initial)
        all_images = (valuation(w, enabled, passed, connected, initial)[1] for w in words)
        assert sum(1 for w, image in zip(words, all_images, strict=True) if image & 65535 == w) == len(words)
        _, after = _grow(attached, law)
        effects[label] = {
            "example_complete_initial_word_lsb_first_name": first, "example_complete_final_word_lsb_first_name": final,
            "initial_source_status": "110", "initial_announcement": f"{initial:03b}",
            "final_source_status": f"{_pick(final, status):03b}", "final_announcement": f"{_pick(final, announcement):03b}",
            "source_status_exchange_named_distinctions": source_swap, "announcement_exchange_named_distinctions": announcement_swap,
            "passed_supplied_predicate": passed, "source_admitted": enabled, "public_writer_connected": connected,
            "actual_announcement_write": did_write, "fresh_public_go_delivered": did_write and passed,
            "ordinary_rows_after_fixed_offered_growth": after["reached"], "fresh_birth_count": len(after["births"]),
            "all_literal_source_valuations_left_lawful": len(words),
        }
    ordinary = effects["source_admitted_and_go"]["ordinary_rows_after_fixed_offered_growth"]
    assert all(row["ordinary_rows_after_fixed_offered_growth"] == ordinary for row in effects.values())
    return {
        "appended_banks": projections, "full_sources_after_appending_disjoint_banks": source_projection_by_holder,
        "source_extension_count_of_each_fixed_written_word": len(permitted) ** 2,
        "complete_source_plus_two_banks_population": len(words) * len(permitted) ** 2,
        "legal_bank_words": tuple(f"{i:03b}" for i in permitted),
        "guarded_write_cases": effects, "ordinary_offered_growth_uses_same_incidence_for_every_written_value": True,
        "writer_changes_no_incidence": True,
    }


def _coarse_same_flag(actual, claims, roster, N, W, library):
    pair = (2, 4)
    r, t = pair
    common_s, common_x = next((s, x) for s in range(16) for x in range(8) if (actual[r][s] & actual[t][s]) >> x & 1)
    named_common = _embed(common_s, roster["paid_names"]) | _embed(common_x, roster["focal_read_order"])
    complete = [named_common | _embed(i, roster["sibling_read_order"]) for i in pair]
    vectors = tuple(tuple(tuple((m >> x) & 1 for x in range(8)) for m in actual[i]) for i in pair)
    a, b = vectors
    cross_retained = tuple(tuple(sum(a[s][x] * b[s][y] for s in range(16)) for y in range(8)) for x in range(8))
    cross_clean = tuple(tuple(claims[r][3][0][x] * claims[t][3][0][y] for y in range(8)) for x in range(8))
    observed = {}
    for mode, matrices, cross, launch, prepared in (
        ("retained", (claims[r][0], claims[t][0]), cross_retained, N, N),
        ("clean", (claims[r][1][0], claims[t][1][0]), cross_clean, 16 * N, W),
    ):
        both = _add(*matrices)
        shared_test = cross[common_x][common_x]
        assert shared_test > 0
        log = library.packet(both, launch, prepared)
        sym = _add(cross, tuple(zip(*cross)))
        plus = _add(both, sym)
        minus = _add(both, _scale(sym, -1))
        assert _add(plus, minus) == _scale(both, 2)
        observed[mode] = {
            "common_focal_packet_after_ignoring_siblings": log,
            "cross_block_for_coarse_flag": cross, "cross_block_after_logging_fine_word": _zero(),
            "selected_joint_off_diagonal_before_logging_per_launch": str(F(shared_test, launch)),
            "selected_joint_off_diagonal_before_logging_conditioned_on_pair": str(F(shared_test, _trace(both))),
            "separate_plus_projection_after_coarse_flag": library.packet(plus, 2 * launch, 2 * prepared),
            "separate_minus_projection_after_coarse_flag": library.packet(minus, 2 * launch, 2 * prepared),
            "separate_plus_projection_after_fine_word_logging": library.packet(both, 2 * launch, 2 * prepared),
        }
    return {"same_flag_selected_pair": tuple(f"{i:09b}" for i in pair), "complete_words_lsb_name_zero": complete,
            "common_spent_word": f"{common_s:04b}", "common_focal_word": f"{common_x:03b}", "modes": observed}


def _independent_rates(rows, mode, launch, prepared):
    fields = tuple((i, F(row[mode]["loss"]), row[mode]["weight"]) for i, row in enumerate(rows) if row[mode]["weight"])
    include = tuple((i, loss, w) for i, loss, w in fields if loss <= 0)
    items = tuple((i, loss, w) for i, loss, w in fields if loss > 0)
    base = sum(row[2] for row in include)
    credit = -sum((row[1] for row in include), F(0))

    # Finite exact integer programs on the literal records. State remembers the largest
    # reachable acceptance at a given exact cost, after processing each offered word once.
    scale = lcm(credit.denominator, *(loss.denominator for _, loss, _ in items))
    cap = int(scale * credit)
    dp = {0: 0}
    for _, loss, w in items:
        cost = int(scale * loss)
        for before, value in tuple(dp.items()):
            if before + cost <= cap:
                dp[before + cost] = max(dp.get(before + cost, 0), value + w)
    deterministic = base + max(dp.values())

    # A separate fractional price bound, witnessed by filling in descending value per cost.
    remaining = credit
    randomized = F(base)
    filling = []
    for index, cost, w in sorted(items, key=lambda q: (q[1] / q[2], q[0])):
        if remaining == 0:
            break
        fraction = min(F(1), remaining / cost)
        filling.append((f"{index:09b}", str(fraction)))
        randomized += fraction * w
        remaining -= fraction * cost
    if not items or remaining > 0:
        multiplier = F(0)
    elif filling:
        boundary = int(filling[-1][0], 2)
        multiplier = next(w / cost for index, cost, w in items if index == boundary)
    else:
        multiplier = max(w / cost for _, cost, w in items)
    bound = sum(max(F(0), w - multiplier * cost) for _, cost, w in fields)
    assert randomized == bound and deterministic <= randomized

    def price(weight):
        return {"raw_accepted_weight": str(weight), "original_launch_acceptance": str(F(weight, launch)),
                "prepared_source_acceptance": str(F(weight, prepared))}

    return {"deterministic": price(deterministic), "randomized": price(randomized),
            "all_nonpositive_cost_words": tuple(f"{i:09b}" for i, _, _ in include),
            "fractional_fill_above_base": filling, "credit": str(credit), "price_multiplier": str(multiplier),
            "integer_budget": cap, "integer_unit": str(F(1, scale)), "exact_integer_dp": sorted(dp.items())}


def _source_digests():
    paths = [HERE / "physical.py", HERE / "preregistration.md", PREVIOUS / "physical.py", PREVIOUS / "replay.py",
             OLD_ARTIFACT, ENGINE, END, LATCH, *(ROOT / p for p in ENGINE_IMPORTS)]
    paths.extend(sorted((ROOT / "tools/knotlab").glob("*.py")))
    canonical, public = {}, {}
    for path in paths:
        key = str(path.relative_to(ROOT))
        body = path.read_bytes()
        # These four mirrored modules substitute the public guide filename in explanatory text.
        if key in ("tools/knotlab/__init__.py", "tools/knotlab/cli.py", "tools/knotlab/competition.py", "tools/knotlab/knots.py"):
            if b"docs/KNOT_INTUITION.md" in body:
                private, mirror = body, body.replace(b"docs/KNOT_INTUITION.md", b"INTUITIONS.md")
            else:
                private, mirror = body.replace(b"INTUITIONS.md", b"docs/KNOT_INTUITION.md"), body
            canonical[key], public[key] = sha256(private).hexdigest(), sha256(mirror).hexdigest()
        else:
            canonical[key] = sha256(body).hexdigest()
    return canonical, public


def run():
    """Represent each exact raw Gram once. Row gram IDs address the two top-level libraries."""
    prior = json.loads(gzip.decompress(OLD_ARTIFACT.read_bytes()))
    library = _Grams()
    cases = {law: _law_source(law, prior["physical_words"]["sources"]["4"][law], prior["reconstruction"][f"4/{law}"], library)
             for law in LAWS}
    digests, variants = _source_digests()
    return {
        "source_sha256": digests, "public_source_variants": variants,
        "order": {
            "exterior": "binary lexicographic with first named sibling most significant",
            "settings": "binary lexicographic Z=0, X=1, first focal mark most significant",
            "answers_and_gram_indices": "binary lexicographic plus=0, first focal mark most significant",
            "spent_characters": "binary lexicographic all-plus first, in named spent order",
        },
        "laws": cases, "gram_library": library.matrices, "probability_library": library.probabilities,
        "target": str(TARGET), "six_sign_deterministic_bound": _strategies(),
        "apparatus_scope": "The paid roster and legal word support use the ordinary law. Signed projectors, reading r, and the controlled keeper record are supplied.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="print exact populations, acceptances, and evidence digest")
    opts = parser.parse_args()
    evidence = run()
    serialized = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    if opts.smoke:
        digest = sha256(serialized.encode()).hexdigest()
        for law, case in evidence["laws"].items():
            for mode, rates in case["independent_primary_rates"].items():
                print(law, mode, case["N"], case["W"], len(case["rows"]),
                      *(rates[k]["original_launch_acceptance"] for k in ("deterministic", "randomized")))
        print(digest)
    else:
        print(serialized)


if __name__ == "__main__":
    main()
