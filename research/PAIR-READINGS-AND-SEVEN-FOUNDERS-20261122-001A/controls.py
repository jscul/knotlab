"""Independent exact replay of the frozen positive and deletion controls."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from math import lcm, prod
from pathlib import Path
from random import Random
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "artifacts/NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A/NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A-E001_newest_knots"
OPERATOR = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
HASHES = {
    HERE / "preregistration.md": "c509b1eb23c72d8985605d7e1b15de56f101ccc098c6a608f334f1428a04a47c",
    HERE / "design_candidate_v2.md": "639423697f11005143b9047d98eb90a65191baf58b896d69cd7dba6aedfc275b",
    OPERATOR: "cffce06049dee59029790d1668e34aa6efef0cd34cb34997379d0b9cbd4c3ece",
    ARCHIVE / "reference.json": "163919ab8b4a7b8ed04b5458cb28e56dca5b5010aa8843827d2ee03b9b651de4",
    ARCHIVE / "target_uniform.json": "6760b421bc687edb762b8e6b352f96bd783d9de1c9bd774f41f6c1974f4c3686",
    ARCHIVE / "target_inherited.json": "e778fcb5ddbf4058090c151e5d88fb40191017bd733a70bcf55ef8f0f92377b1",
    ARCHIVE / "control_target.json": "36b5925b3f38c7a75debcfb0d07bcf1529279f0988510786f6708713f98cea5b",
    ARCHIVE / "control_references.json": "9c0f6722c71bece582c0c6ac234af6d21b7b00a555450a433b98ae7559da8179",
}


@dataclass(frozen=True)
class Birth:
    holder: int
    parents: tuple
    paid: tuple
    fresh: tuple
    demand: int
    support: tuple

    def record(self):
        return vars(self)


def owners(stars):
    assert len(set(map(frozenset, stars))) == len(stars)
    seen = defaultdict(list)
    for holder, support in enumerate(stars):
        assert len(set(support)) == len(support) >= 3
        for name in support:
            seen[name].append(holder)
    assert all(len(group) in (1, 2) for group in seen.values())
    return seen


def loose(stars):
    return tuple(sorted(name for name, support in owners(stars).items() if len(support) == 1))


def paid_cut(stars, law, engine, name_at_rank=None):
    held = owners(stars)
    rank = ({name: i for i, name in enumerate(name_at_rank)} if name_at_rank is not None
            else {name: name for name in range(len(held) + 4096)})
    assert {rank[name] for name in held} == set(range(len(held)))
    queues = defaultdict(list)
    for name in sorted(held, key=rank.__getitem__):
        if len(held[name]) == 1:
            queues[held[name][0]].append(name)
    result = engine.step(engine.from_stars(stars), law, max_births=128)
    assert result.status == "extend" and not result.implied and not result.shortages
    assert Counter(p for ps in result.parents for p in ps) == {
        payer: len(names) for payer, names in queues.items()}
    pools = {payer: iter(names) for payer, names in queues.items()}
    next_rank = len(held)
    births = []
    for parents, grant, demand in zip(result.parents, result.fresh, result.demand, strict=True):
        assert grant == max(1, 3 - len(parents), demand)
        paid = tuple(next(pools[payer]) for payer in parents)
        new_ranks = range(next_rank, next_rank + grant)
        fresh = tuple(name_at_rank[k] if name_at_rank is not None else k for k in new_ranks)
        support = tuple(sorted((*paid, *fresh), key=rank.__getitem__))
        births.append(Birth(len(stars) + len(births), parents, paid, fresh, demand, support))
        next_rank += grant
    reached = stars + tuple(row.support for row in births)
    incidence = owners(reached)
    for row in births:
        for p, x in zip(row.parents, row.paid, strict=True):
            assert held[x] == [p] and incidence[x] == [p, row.holder]
        for x in row.fresh:
            assert x not in held and incidence[x] == [row.holder]
    assert {x for x, group in incidence.items() if len(group) == 1} == {
        x for row in births for x in row.fresh}
    return reached, tuple(births)


def fixed_history(source, law, engine, horizon, name_at_rank=None):
    stages, ledger = [source], []
    for _ in range(horizon):
        reached, births = paid_cut(stages[-1], law, engine, name_at_rank)
        stages.append(reached)
        ledger.append(births)
    return stages, ledger


def relabeling(size):
    labels = list(range(100, 100 + size))
    Random(60571).shuffle(labels)
    return tuple(labels)


def replay_renamed(stages, ledger, law, engine, mapping):
    renamed = tuple(tuple(mapping[x] for x in row) for row in stages[0])
    replay, births = fixed_history(renamed, law, engine, len(ledger), mapping)
    remap = {x: i for i, x in enumerate(mapping)}
    assert stages == [tuple(tuple(remap[x] for x in row) for row in stage) for stage in replay]
    for native, moved in zip(ledger, births, strict=True):
        for a, b in zip(native, moved, strict=True):
            assert (a.holder, a.parents, a.demand) == (b.holder, b.parents, b.demand)
            assert (a.paid, a.fresh, a.support) == tuple(
                tuple(remap[x] for x in names) for names in (b.paid, b.fresh, b.support))
    return replay, births


def legal(law, width, positives):
    return positives % 2 == 0 if law == "parity" else 0 < positives < width


def masks(stars, names):
    rank = {x: i for i, x in enumerate(names)}
    return tuple(sum(1 << rank[x] for x in row) for row in stars)


def literal_words(stars, names, law):
    support = masks(stars, names)
    return tuple(word for word in range(1 << len(names))
                 if all(legal(law, m.bit_count(), (word & m).bit_count()) for m in support))


def digits(word, indices):
    return tuple(word >> idx & 1 for idx in indices)


def word_label(word, width):
    return "".join(map(str, digits(word, range(width))))


def source_certificate(stars, law):
    names = tuple(sorted(owners(stars)))
    words = literal_words(stars, names, law)
    masks_by_holder = masks(stars, names)
    projections, essential = [], []
    for i, row_mask in enumerate(masks_by_holder):
        width = row_mask.bit_count()
        allowed = {mask for mask in range(1 << width) if legal(law, width, mask.bit_count())}
        indices = tuple(j for j in range(len(names)) if row_mask >> j & 1)
        local = {sum((word >> j & 1) << k for k, j in enumerate(indices)) for word in words}
        assert local == allowed and 0 < len(local) < 1 << width
        assert all(len({(w & ((1 << k) - 1)) | ((w >> (k + 1)) << k)
                        for w in local}) == 1 << (width - 1) for k in range(width))
        others = masks_by_holder[:i] + masks_by_holder[i + 1:]
        witness = next(word for word in range(1 << len(names))
                       if not legal(law, row_mask.bit_count(), (word & row_mask).bit_count())
                       and all(legal(law, m.bit_count(), (word & m).bit_count()) for m in others))
        projections.append(len(local))
        essential.append(word_label(witness, len(names)))
    return words, {"name_order": names, "allowed_words": len(words),
                   "lawful_patterns_on_each_holder": projections,
                   "constraint_deletion_witness_for_each_holder": essential}


def child_moments(birth, law):
    """Exact first and second sign numerators for each paid-input count."""
    width = len(birth.fresh)
    result = []
    for paid_ones in range(len(birth.paid) + 1):
        fresh = [bits for bits in range(1 << width)
                 if legal(law, width + len(birth.paid), paid_ones + bits.bit_count())]
        assert fresh
        first = sum(1 - 2 * (bits & 1) for bits in fresh)
        same_birth = sum(1 - 2 * ((bits ^ (bits >> 1)) & 1) for bits in fresh) if width > 1 else 0
        result.append((len(fresh), first, same_birth))
    return tuple(result)


def pair(x, y):
    return (x, y) if x < y else (y, x)


def reached_tables(source, births, law, words=None):
    """Integrate the one-cut fresh banks against every allowable founder word."""
    old = tuple(sorted(owners(source)))
    if words is None:
        words = literal_words(source, old, law)
    assert words
    indexes = {x: j for j, x in enumerate(old)}
    root_bits = (np.asarray(words, dtype=np.int64)[:, None] >> np.arange(len(old))) & 1
    kernels = [child_moments(birth, law) for birth in births]
    scale = lcm(*(count for child in kernels for count, _, _ in child))
    maximum = prod(max(entry[0] for entry in child) for child in kernels)
    assert len(words) * maximum * scale ** 2 < 1 << 63
    first = [(1 - 2 * root_bits[:, j]) * scale for j in range(len(old))]
    second, counts = [], np.ones(len(words), dtype=np.int64)
    for birth, kernel in zip(births, kernels, strict=True):
        paid_ones = root_bits[:, [indexes[x] for x in birth.paid]].sum(axis=1)
        k_count, k_first, k_second = np.asarray(kernel, dtype=np.int64).T
        multiplicity = k_count[paid_ones]
        unit = scale // multiplicity
        first.append(unit * k_first[paid_ones])
        second.append(unit * scale * k_second[paid_ones])
        counts *= multiplicity
        for x in birth.fresh:
            indexes[x] = len(first) - 1
    columns = np.asarray(first)
    all_pairs = tuple(combinations(sorted(indexes), 2))
    tables = {}
    next_words = int(counts.sum())
    for weighting, weight in (("uniform", counts), ("inherited", np.ones_like(counts))):
        moment = columns @ (columns * weight).T
        sibling_moments = [int(row @ weight) for row in second]
        denominator = int(weight.sum()) * scale ** 2
        table = {}
        for x, y in all_pairs:
            a, b = indexes[x], indexes[y]
            numerator = sibling_moments[a - len(old)] if a == b else int(moment[a, b])
            table[x, y] = Fraction(denominator - numerator, 2 * denominator)
        tables[weighting] = table
    return next_words, tables


def profile(stars, births):
    return Counter((tuple(sorted(tuple(sorted(stars[p])) for p in birth.parents)), len(birth.fresh))
                   for birth in births)


def archived_profile(raw):
    return Counter((tuple(sorted(tuple(x) for x in parents)), n) for parents, n in raw)


def compare_history(source, history, stages, ledger):
    assert source == tuple(map(tuple, history["source_rows"]))
    for saved, reached, births, next_births in zip(
            history["stages"], stages[1:3], ledger[:2], ledger[1:3], strict=True):
        assert reached == tuple(map(tuple, saved["rows"]))
        assert [(row.parents, len(row.fresh)) for row in births] == [
            (tuple(p), n) for p, n in saved["births"]]
        assert len(next_births) == saved["next_count"]
        assert profile(reached, next_births) == archived_profile(saved["profile"])


def json_table(table):
    return {" ".join(map(str, key)): str(value) for key, value in table.items()}


def correlation(table, x, y):
    return Fraction(1) if x == y else 1 - 2 * table[pair(x, y)]


def unary_identity(pre, post, old, x, new):
    a, b = new
    assert all(post[key] == value for key, value in pre.items())
    assert correlation(post, a, b) == Fraction(-1, 3)
    for z in old:
        for u in new:
            assert correlation(post, u, z) == -correlation(pre, x, z) / 3
    assert len(post) == len(pre) + 1 + 2 * len(old)
    return len(post)


def main_control(engine):
    ref = json.loads((ARCHIVE / "reference.json").read_bytes())
    archive = json.loads((ARCHIVE / "control_target.json").read_bytes())
    source = tuple(map(tuple, ref["source"]))
    words, gate = source_certificate(source, "nae")
    stages, births = fixed_history(source, "nae", engine, 3)
    compare_history(source, archive["native_history"], stages, births)
    assert stages[1] == tuple(map(tuple, ref["stage"]))
    assert profile(stages[1], births[1]) == archived_profile(ref["profile"])
    assert tuple(ref["loose"]) == loose(stages[1]) and len(births[1]) == 7
    assert all(len(row.parents) == 2 for row in births[1])
    assert Counter(len(row.fresh) for row in births[1]) == {2: 4, 3: 3}
    assert len(owners(stages[0])) == 17 and len(owners(stages[1])) == 31
    total, tables = reached_tables(source, births[0], "nae", words)
    assert total == 601181310
    for weighting, table in tables.items():
        file = ARCHIVE / f"target_{weighting}.json"
        assert HASHES[file] == ref["table_sha256"][weighting]
        assert tuple(table) == tuple(combinations(range(31), 2))
        assert list(table.values()) == list(map(Fraction, json.loads(file.read_bytes())))
    uniform, inherited = tables["uniform"], tables["inherited"]
    _, source_table = reached_tables(source, (), "nae", words)
    source_table = source_table["uniform"]
    assert all(inherited[p] == value for p, value in source_table.items())
    assert all(uniform[p] != value for p, value in source_table.items())
    delta = {p: abs(uniform[p] - inherited[p]) for p in uniform}
    maximum = max(delta.values())
    assert sum(bool(d) for d in delta.values()) == 462
    assert maximum == Fraction(59350418148, 832175208679)
    assert [p for p in delta if delta[p] == maximum] == [(0, 9), (12, 15)]
    assert all((rate * total).denominator == 1 for rate in uniform.values())

    mapping = relabeling(len(owners(stages[-1])))
    renamed, renamed_births = replay_renamed(stages, births, "nae", engine, mapping)
    renamed_total, renamed_tables = reached_tables(renamed[0], renamed_births[0], "nae")
    assert renamed_total == total
    for weighting, table in tables.items():
        assert all(renamed_tables[weighting][pair(mapping[x], mapping[y])] == value
                   for (x, y), value in table.items())

    parity_words, parity_gate = source_certificate(source, "parity")
    parity_stages, parity_ledger = fixed_history(source, "parity", engine, 3)
    compare_history(source, archive["lawful_parity_from_same_founder"]["history"],
                    parity_stages, parity_ledger)
    assert parity_stages == stages and parity_ledger == births
    parity_total, parity_tables = reached_tables(source, parity_ledger[0], "parity", parity_words)
    assert parity_total == 1048576
    for mode, table in parity_tables.items():
        assert all(value == Fraction(1, 2) != tables[mode][key] for key, value in table.items())

    assert births[0][-1].support == (8, 29, 30)
    deleted_rows = stages[1][:-1]
    old_count, deleted = reached_tables(source, births[0][:-1], "nae", words)
    assert old_count == 200393770 and old_count * 3 == total
    old_loose = loose(deleted_rows)
    assert old_loose == (8, *range(17, 29))
    old_pairs = unary_identity(deleted["uniform"], uniform, range(29), 8, (29, 30))
    assert old_pairs == 465 and len(deleted["uniform"]) == 406
    return {
        "source_rows": source, "source_certificate": gate, "ordinary_cuts": [
            [row.record() for row in cut] for cut in births],
        "age_one_rows": stages[1], "age_one_loose": loose(stages[1]),
        "allowed_31_name_words": total, "all_465_pair_readings": {
            key: json_table(value) for key, value in tables.items()},
        "uniform_disagreement_counts": json_table({key: int(total * value) for key, value in uniform.items()}),
        "weighting_change": {"pair_rates_changed": 462, "inherited_old_rates_preserved": 136,
                             "uniform_old_rates_changed": 136, "maximum": str(maximum),
                             "maximum_pairs": [(0, 9), (12, 15)]},
        "lawful_same_founder_parity": {"source_certificate": parity_gate, "allowed_31_name_words": parity_total,
                                       "pairs_at_one_half_each_weighting": 465,
                                       "pairs_changed_from_nae_each_weighting": 465,
                                       "same_literal_cuts": True},
        "coherent_relabeling": {"name_at_original_rank": mapping, "same_literal_cuts": 3,
                               "matched_pair_rates_over_two_weightings": 930},
        "drop_latest_unary": {"removed": (8, 29, 30), "retained_rows": deleted_rows,
                              "allowed_29_name_words": old_count, "old_pairs_equal": 406,
                              "whole_unary_lift_equations_verified": old_pairs,
                              "uniform_rates": json_table(deleted["uniform"]), "loose": old_loose,
                              "other_loose_besides_8": old_loose[1:],
                              "satisfies_one_loose_premise": False},
    }


def pattern_counts(words, positions):
    return Counter(digits(word, positions) for word in words)


def triple_probability(signs, entries):
    return (1 + sum(signs[i] * signs[j] * rate
                    for (i, j), rate in zip(combinations(range(3), 2), entries, strict=True))) / 8


def literal_tables(words, names):
    assert {word ^ ((1 << len(names)) - 1) for word in words} == set(words)
    index = {x: i for i, x in enumerate(names)}
    pairs, triples = {}, {}
    for labels in combinations(names, 2):
        counts = pattern_counts(words, [index[x] for x in labels])
        rate = Fraction(counts[0, 1] + counts[1, 0], len(words))
        for a, b in product((0, 1), repeat=2):
            assert counts[a, b] == len(words) * (rate if a != b else 1 - rate) / 2
        pairs[labels] = rate
    for labels in combinations(names, 3):
        counts = pattern_counts(words, [index[x] for x in labels])
        moments = [1 - 2 * pairs[key] for key in combinations(labels, 2)]
        expected = {}
        for bits in product((0, 1), repeat=3):
            p = triple_probability(tuple(1 - 2 * b for b in bits), moments)
            assert p * len(words) == counts[bits] and p >= 0
            expected["".join(map(str, bits))] = counts[bits]
        triples[labels] = expected
    return pairs, triples


def small_counts(stages, births, x):
    original = stages[0]
    assert loose(original) == (x,)
    erased_holder, = (row for row in original if x in row)
    companions = tuple(y for y in erased_holder if y != x)
    residual = tuple(row for row in original if row != erased_holder)
    residual_names = tuple(sorted(owners(residual)))
    assert loose(residual) == tuple(sorted(companions))
    original_words, certificate = source_certificate(original, "nae")
    names, words = [certificate["name_order"]], [original_words]
    for stage in stages[1:]:
        visible = tuple(sorted(owners(stage)))
        names.append(visible)
        words.append(literal_words(stage, visible, "nae"))
    residual_words = literal_words(residual, residual_names, "nae")
    positions = {label: i for i, label in enumerate(names[0])}
    residual_positions = dict((z, i) for i, z in enumerate(residual_names))
    ext = Counter(digits(word, [positions[y] for y in residual_names]) for word in original_words)
    event_counts = Counter()
    for word in residual_words:
        constant = len(set(digits(word, [residual_positions[z] for z in companions]))) == 1
        assert ext[digits(word, range(len(residual_names)))] == (1 if constant else 2)
        event_counts["constant" if constant else "mixed"] += 1
    assert len(ext) == len(residual_words)
    q = Fraction(event_counts["constant"], len(original_words))
    assert Fraction(len(original_words)) * (1 + q) / 2 == len(residual_words)
    tables = [literal_tables(w, n) for w, n in zip(words, names, strict=True)]
    residual_pairs, residual_triples = literal_tables(residual_words, residual_names)
    corrected = {}
    for y in companions:
        for z in residual_names:
            estimate = (correlation(tables[0][0], y, z) - correlation(tables[0][0], x, z)) / (1 + q)
            assert estimate == correlation(residual_pairs, y, z)
            if y != z:
                corrected[pair(y, z)] = estimate
    checked_patterns = {}
    for labels, counts in residual_triples.items():
        factors = tuple(combinations(labels, 2))
        if all(key in corrected for key in factors):
            for bits, count in counts.items():
                estimate = triple_probability(tuple(1 - 2 * int(b) for b in bits),
                                              [corrected[key] for key in factors])
                assert estimate * len(residual_words) == count
            checked_patterns[labels] = counts

    one, two = births
    assert len(one) == 1 and len(two) == 2
    unary, = one
    assert unary.paid == (x,) and len(unary.fresh) == 2
    assert {item.parents for item in two} == {(unary.holder,)}
    assert {item.paid[0] for item in two} == set(unary.fresh) and all(len(row.fresh) == 2 for row in two)
    assert len(words[1]) == len(words[0]) * 3 and len(words[2]) == len(words[1]) * 9
    for age, multiplicity in ((1, 3), (2, 9)):
        indices = tuple(names[age].index(z) for z in names[age - 1])
        old_patterns = set(digits(word, range(len(indices))) for word in words[age - 1])
        projected = pattern_counts(words[age], indices)
        assert set(projected) == old_patterns and set(projected.values()) == {multiplicity}
        assert all(tables[age][0][key] == value for key, value in tables[age - 1][0].items())
    assert unary_identity(tables[0][0], tables[1][0], names[0], x, unary.fresh) == len(tables[1][0])
    return {
        "source_certificate": certificate, "erased_holder": erased_holder, "erased_loose": x,
        "residual_rows": residual, "names": [*names, residual_names],
        "word_counts": [*map(len, words), len(residual_words)],
        "complete_words_for_erasure": {
            "original": [word_label(w, len(names[0])) for w in words[0]],
            "residual": [word_label(w, len(residual_names)) for w in residual_words],
        },
        "residual_companion_event_counts": dict(event_counts),
        "constant_companion_probability_before_erasure": str(q),
        "pair_rates_source_cut_one_cut_two_residual": [
            *(json_table(table[0]) for table in tables), json_table(residual_pairs)],
        "corrected_pair_correlations": json_table(corrected),
        "identifiable_residual_three_name_patterns": {
            " ".join(map(str, labels)): row for labels, row in checked_patterns.items()},
        "all_literal_signed_three_name_patterns_checked": {
            "source": len(tables[0][1]) * 8, "cut_one": len(tables[1][1]) * 8,
            "cut_two": len(tables[2][1]) * 8, "residual": len(residual_triples) * 8},
    }


def lawful_one_loose(engine):
    source = ((0, 1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 5, 6))
    stages, births = fixed_history(source, "nae", engine, 2)
    data = small_counts(stages, births, 0)
    mapping = relabeling(len(owners(stages[-1])))
    renamed, ledger = replay_renamed(stages, births, "nae", engine, mapping)
    other = small_counts(renamed, ledger, mapping[0])
    assert other["word_counts"] == data["word_counts"]
    for original_rows, renamed_rows in zip(data["pair_rates_source_cut_one_cut_two_residual"],
                                          other["pair_rates_source_cut_one_cut_two_residual"], strict=True):
        moved = {" ".join(map(str, pair(*(mapping[int(x)] for x in k.split())))): v
                 for k, v in original_rows.items()}
        assert moved == renamed_rows
    for which, i in (("original", 0), ("residual", 3)):
        alphabet = [mapping[x] for x in data["names"][i]]
        transport = [alphabet.index(x) for x in other["names"][i]]
        assert {"".join(w[k] for k in transport) for w in data["complete_words_for_erasure"][which]
                } == set(other["complete_words_for_erasure"][which])
    data["source_rows"] = source
    data["ordinary_cuts"] = [[b.record() for b in cut] for cut in births]
    data["coherent_relabeling"] = {"name_at_original_rank": mapping, "matched_full_word_sets_and_pair_rates": True}
    return data


def parity_reduce(mask, basis):
    for top in sorted(basis, reverse=True):
        if mask >> top & 1:
            mask ^= basis[top]
    return mask


def parity_controls(engine):
    archive = json.loads((ARCHIVE / "control_references.json").read_bytes())["parity_obstructions"]
    outcome = {}
    for name, rows in archive.items():
        checked = []
        for case in rows:
            _, gate = source_certificate(tuple(map(tuple, case["source"])), "parity")
            stages, births = fixed_history(tuple(map(tuple, case["source"])), "parity", engine, case["age"] + 1)
            mapping = case["current_to_common"]
            stars = sorted(tuple(sorted(mapping[x] for x in row)) for row in stages[-2])
            assert stars == list(map(tuple, case["common_rows"]))
            assert len(births[-1]) == case["next_count"]
            basis = {}
            for mask in masks(stars, range(len(mapping))):
                remaining = parity_reduce(mask, basis)
                if remaining:
                    basis[remaining.bit_length() - 1] = remaining
            rates = [Fraction(1, 2) if parity_reduce((1 << x) | (1 << y), basis) else Fraction(0)
                     for x, y in combinations(range(len(mapping)), 2)]
            for values in case["weights"].values():
                assert rates == [Fraction(count, values["total"]) for count in values["disagreement_counts"]]
            checked.append((len(births[-1]), rates, basis, gate))
        a, b = checked
        assert a[1] == b[1] and a[0] != b[0]
        same = len(a[2]) == len(b[2]) and all(not parity_reduce(row, b[2]) for row in a[2].values())
        assert same == (name == "same_states_different_births")
        outcome[name] = {"pairs_equal": len(a[1]), "next_births": [a[0], b[0]], "same_complete_word_set": same}
    return outcome


def run(check=False):
    for path, wanted in HASHES.items():
        assert sha256(path.read_bytes()).hexdigest() == wanted, path
    spec = spec_from_file_location("ordinary_operator_for_pair_controls", OPERATOR)
    engine = module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    data = {"input_sha256": {str(path.relative_to(ROOT)): value for path, value in HASHES.items()},
            "independent_positive": main_control(engine), "one_loose_nae_control": lawful_one_loose(engine),
            "archived_parity_obstructions": parity_controls(engine)}
    content = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    path = HERE / "controls.json"
    if check:
        assert path.read_bytes() == content
    else:
        with path.open("xb") as out:
            out.write(content)
    print(sha256(content).hexdigest(), path.name)


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["--check"])
    run("--check" in sys.argv)
