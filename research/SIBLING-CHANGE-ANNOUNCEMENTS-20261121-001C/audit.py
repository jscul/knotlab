"""Independent literal Gram and exact one-pair price checks."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
from struct import pack

try:
    import numpy as np
except ModuleNotFoundError as error:
    if error.name != "numpy":
        raise
    np = None


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "research/SIBLING-CHANGE-ANNOUNCEMENTS-20261121-001B"
FREEZE = HERE / "preregistration.md"
RECEIPT = PREVIOUS / "receipt.json"
SOURCE = PREVIOUS / "all_erasure_evidence.json.gz"
FREEZE_HASH = "0dfeb24dc28fbf14ec8a6bfcfaa42b04f00b3ae6170dad4c1644c175e3c80c09"
SOURCE_HASH = "bc93791c55734fe2a9f305cb77806b9eadb0653426ea2ea86e6b9129c8b90ae4"
RECEIPT_HASH = "c42a8bfde0d55be3a0ce468d22097490507732d09ea5643305f7fe53fa1779db"
SPENT = tuple(range(16))
RECORDS = tuple(range(512))
FOCAL = tuple(range(8))
CLASSES = ("deterministic", "randomized")
LAWS = ("parity", "nae")
ZERO = ((0,) * 8,) * 8


def _matrix(g):
    return tuple(tuple(row) for row in g)


def _plus(a, b):
    return tuple(tuple(x + y for x, y in zip(r, s, strict=True)) for r, s in zip(a, b, strict=True))


def _signed_setting_rows(g):
    rows = []
    for s in FOCAL:
        z = 7 ^ s
        row = []
        for a in FOCAL:
            support = [(x, (-1) ** (x & a & s).bit_count()) for x in FOCAL if x & z == a & z]
            numerator = sum(g[x][y] * p * q for x, p in support for y, q in support)
            row.append(F(numerator, 1 << s.bit_count()))
        assert min(row) >= 0
        rows.append(tuple(row))
    return tuple(rows)


def _weighted_score(table, c):
    required = 7 * c
    successes = sum(table[7][a] for a in (3, 5, 6, 7))
    penalties = table[0][required]
    for question in (1, 2, 4):
        not_chosen = 7 ^ question
        for a in FOCAL:
            if a & question and ((a ^ required) & not_chosen):
                penalties += table[question][a]
    return successes - penalties


@cache
def _grade(gram):
    weight = sum(gram[i][i] for i in FOCAL)
    table = _signed_setting_rows(gram)
    assert all(sum(row) == weight for row in table)
    d = tuple(28 * _weighted_score(table, c) - weight for c in (0, 1))
    assert all(x.denominator == 1 for x in d)
    return weight, int(d[0]), int(d[1])


def _combine(grades):
    return tuple(map(sum, zip(*grades, strict=True)))


class _Literal:
    def __init__(self, shared_archive, case):
        self.grams = tuple(_matrix(g) for g in shared_archive["gram_library"])
        former = shared_archive["grade_library"]
        self.ids = tuple(tuple(r) for r in case["gram_ids"])
        looked_at = set()
        grades = []
        for ids in self.ids:
            priced = []
            for i in ids:
                gram = self.grams[i]
                grade = _grade(gram)
                if i not in looked_at:
                    got = former[i]
                    w, d0, d1 = grade
                    assert (w, d0, d1) == (got["weight"], 28 * F(got["excess0"]), 28 * F(got["excess1"]))
                    probs = [[str(x / w) for x in r] for r in _signed_setting_rows(gram)] if w else None
                    assert probs == shared_archive["probability_library"][i]
                    if not w:
                        assert gram == ZERO
                    looked_at.add(i)
                priced.append(grade)
            grades.append(tuple(priced))
        self.grades = tuple(grades)
        assert len(grades) == 16 and all(len(row) == 512 for row in grades)
        self.denominator = case["launch_denominator"]
        assert sum(g[0] for row in grades for g in row) == self.denominator
        assert tuple(str(F(sum(w for w, _, _ in self.grades[h]), self.denominator)) for h in SPENT) == tuple(case["true_h_port_masses"])
        self.numerical_types = len(looked_at)
        self._pooling = {}

    def _pooled_grade(self, indices):
        order = tuple(sorted(indices))
        if order not in self._pooling:
            gram = _sum_grams((self.grams[i], 1) for i in order)
            literal = _grade(gram)
            assert literal == _combine(_grade(self.grams[i]) for i in order)
            self._pooling[order] = literal
        return self._pooling[order]

    def partition(self, blocks, orientation):
        bins = defaultdict(list)
        for symbol, paid in enumerate(blocks):
            assert paid
            for k in RECORDS:
                if len(paid) == 1:
                    p = self.grades[paid[0]][k]
                else:
                    p = self._pooled_grade(tuple(self.ids[h][k] for h in paid))
                w, d = p[0], p[1 + orientation]
                if w:
                    bins[w, d].append(512 * symbol + k)
                else:
                    assert d == 0
        assert sum(w * len(ids) for (w, _), ids in bins.items()) == self.denominator
        return bins


def _fractional(groups):
    fixed_weight = sum(w * len(labels) for (w, d), labels in groups.items() if d >= 0)
    credit = sum(d * len(labels) for (_w, d), labels in groups.items() if d > 0)
    by_ratio = defaultdict(list)
    for (w, d), labels in groups.items():
        if d < 0:
            by_ratio[F(-d, w)].append((w, -d, len(labels)))
    total = F(fixed_weight)
    left = F(credit)
    dual = F(0)
    for ratio, priced in sorted(by_ratio.items()):
        cost = sum(c * n for _, c, n in priced)
        if cost > left:
            total += left / ratio
            dual = 1 / ratio
            left = F(0)
            break
        total += sum(w * n for w, _, n in priced)
        left -= cost
    upper = sum(len(ids) * max(0, w + dual * d) for (w, d), ids in groups.items())
    assert upper == total
    return total, dual, credit, fixed_weight


def _add_integer_chunk(best, jump, charge, witness):
    if np is not None:
        # The proposal and improvement mask must both precede the destination write.
        proposal = best[:-jump] + charge
        target = best[jump:]
        better = proposal < target
        np.copyto(target, proposal, where=better)
        return np.packbits(better, bitorder="little") if witness else None

    # Descending destination indices leave each source state unchanged until it is read.
    proposals = len(best) - jump
    changed = bytearray((proposals + 7) // 8) if witness else None
    for source in range(proposals - 1, -1, -1):
        candidate = best[source] + charge
        target = source + jump
        if candidate < best[target]:
            best[target] = candidate
            if changed is not None:
                changed[source // 8] |= 1 << (source % 8)
    return changed


def _integer(groups, upper, credit, fixed_weight, witness):
    """Minimum deficit of each attainable extra trace, with bounded binary multiplicities."""
    deficit_items = [(w, -d, labels) for (w, d), labels in sorted(groups.items()) if -credit <= d < 0]
    unit = gcd(*(w for w, _cost, _labels in deficit_items)) or 1
    ceiling = int((upper - fixed_weight) // unit) if deficit_items else 0
    missing = credit + 1
    best = [missing] * (ceiling + 1) if np is None else np.full(ceiling + 1, missing, dtype=np.int64)
    best[0] = 0
    history = []
    chunks = 0
    for weight, cost, labels in deficit_items:
        stride = weight // unit
        left = min(len(labels), credit // cost, ceiling // stride)
        offset, size = 0, 1
        while left:
            qty = min(left, size)
            jump, charge = qty * stride, qty * cost
            changed = _add_integer_chunk(best, jump, charge, witness)
            if witness:
                history.append((jump, charge, labels[offset:offset + qty], changed))
            left -= qty
            offset += qty
            size *= 2
            chunks += 1
    chosen = index = next(i for i in range(ceiling, -1, -1) if best[i] <= credit)
    price = int(best[index])
    mask = {}
    if witness:
        used = 0
        for jump, charge, labels, bits in reversed(history):
            position = index - jump
            if position >= 0 and (int(bits[position // 8]) >> (position % 8)) & 1:
                mask.update(dict.fromkeys(labels, F(1)))
                index -= jump
                used += charge
        assert index == 0 and used == price
        # Equivalent labels have the same score. Keep the earliest concrete records in each type.
        for (w, d), labels in groups.items():
            count = len(labels) if d >= 0 else sum(label in mask for label in labels)
            if d < 0:
                for lab in labels:
                    mask.pop(lab, None)
            mask.update(dict.fromkeys(labels[:count], F(1)))
    state_bytes = pack(f"<{len(best)}q", *best) if np is None else best.astype("<i8").tobytes()
    cert = {"extra_weight_unit": unit, "extra_weight_capacity_units": ceiling,
            "deficit_budget": credit, "final_used_deficit": price, "binary_chunks": chunks,
            "final_state": chosen, "terminal_min_cost_states_sha256": sha256(state_bytes).hexdigest()}
    return fixed_weight + chosen * unit, mask, cert


def _fractional_mask(groups, dual, credit):
    mask = {}
    boundary = []
    for (w, d), labels in groups.items():
        price = w + dual * d
        if price > 0:
            mask.update(dict.fromkeys(labels, F(1)))
            if d < 0:
                credit += d * len(labels)
        if price == 0 and d < 0:
            boundary.extend((lab, -d) for lab in labels)
    assert credit >= 0
    left = F(credit)
    for i, d in sorted(boundary):
        if left <= 0:
            break
        amount = min(F(1), left / d)
        mask[i] = amount
        left -= amount * d
    return mask


def _price(groups, witness=False):
    upper, dual, credit, fixed = _fractional(groups)
    attained, integer_mask, dp = _integer(groups, upper, credit, fixed, witness)
    assert attained <= upper
    result = {"deterministic": attained, "randomized": upper}
    cert = {"integer": dp, "fractional_dual_multiplier_on_28_times_excess": str(dual)}
    masks = {"deterministic": integer_mask, "randomized": _fractional_mask(groups, dual, credit)} if witness else {}
    for kind, mask in masks.items():
        w, d = _score_mask(groups, mask)
        assert w == result[kind] and d >= 0
        if kind == "deterministic":
            assert all(val == 1 for val in mask.values())
    return result, masks, cert


def _score_mask(groups, mask):
    w = d = F(0)
    for (trace, excess), ids in groups.items():
        acceptance = sum(mask.get(k, 0) for k in ids)
        w += acceptance * trace
        d += acceptance * excess
    return w, d


def _pair_partition(a, b):
    return tuple((a, b) if h == a else (h,) for h in SPENT if h != b)


def _coordinate_partition(mask):
    return tuple(tuple(h for h in SPENT if h & mask == s) for s in SPENT if s & mask == s)


def _sum_grams(terms):
    total = [[0] * 8 for _ in FOCAL]
    for g, a in terms:
        for x in FOCAL:
            for y in FOCAL:
                total[x][y] += a * g[x][y]
    return _matrix(total)


def _matrix_packet(g, denominator, c):
    table = _signed_setting_rows(g)
    w = sum(g[x][x] for x in FOCAL)
    assert all(sum(r) == w for r in table)
    score = _weighted_score(table, c)
    return {
        "gram": tuple(tuple(str(v) for v in row) for row in g),
        "conditional_table": [[str(v / w) for v in row] for row in table] if w else None,
        "w": str(w), "28_times_raw_surplus": str(28 * score - w), "I": str(score / w) if w else None,
        "original_launch_probability": str(F(w, denominator)),
        "original_launch_denominator": denominator,
        "joint_with_uniform_setting_denominator": 8 * denominator,
        "probability_of_cell_with_setting": "conditional cell times original launch probability divided by eight",
    }


def _chosen_gram(literal, blocks, mask):
    weights = defaultdict(int)
    for index, a in mask.items():
        symbol, k = divmod(index, 512)
        for h in blocks[symbol]:
            weights[literal.ids[h][k]] += a
    return _sum_grams((literal.grams[ident], amount) for ident, amount in weights.items())


def _rule_receipt(literal, blocks, mask, c, total):
    go = _chosen_gram(literal, blocks, mask)
    no = tuple(tuple(F(a - b) for a, b in zip(u, v, strict=True)) for u, v in zip(total, go, strict=True))
    assert _plus(go, no) == total
    selected, declined = (_matrix_packet(g, literal.denominator, c) for g in (go, no))
    assert F(selected["original_launch_probability"]) + F(declined["original_launch_probability"]) == 1
    assert F(selected["28_times_raw_surplus"]) >= 0
    return {"encoder_classes_in_message_order": blocks,
            "acceptance_on_symbol_then_k": tuple((label, str(mask[label])) for label in sorted(mask)),
            "go": selected, "decline": declined, "source_refusal": "0"}


def _previous_rule(table, method, c):
    prev = table[str(c)][method]
    return {int(k): F(v) for k, v in prev["accepted_label_index_and_probability"]}


def _uniform_dual_pair(literal, field, denominator, paid_pair):
    a, b = paid_pair
    loss = 0
    sample = None
    collisions = 0
    for k, (s, t) in enumerate(zip(field[a], field[b], strict=True)):
        difference = max(s, 0) + max(t, 0) - max(s + t, 0)
        if difference:
            assert s * t < 0
            assert difference == min(abs(s), abs(t))
            assert literal.grades[a][k][0] and literal.grades[b][k][0]
            if sample is None:
                sample = {"sibling_record_index": k, "ordinary_word": f"{k // 2:08b}", "X_answer": k & 1,
                          "left_and_right_w_d_for_c0": [literal.grades[h][k][:2] for h in (a, b)],
                          "full_dual_values": (str(F(s, denominator)), str(F(t, denominator))),
                          "loss_from_forcing_shared_decision": str(F(difference, denominator))}
            collisions += 1
        loss += difference
    return F(loss, denominator), collisions, sample


def _prior_canonical_conflicts(literal, paid_pair, masks):
    a, b = paid_pair
    conflicts = {}
    for cls, rule in masks.items():
        rows = [k for k in RECORDS if literal.grades[a][k][0] and literal.grades[b][k][0]
                and rule.get(512 * a + k, 0) != rule.get(512 * b + k, 0)]
        conflicts[cls] = {"supported_disagreements": len(rows), "least_sibling_index": rows[0] if rows else None}
    return conflicts


def _projected_coordinate_control(literal, archived):
    rows = {}
    for mask in SPENT:
        enc = _coordinate_partition(mask)
        verified = {}
        for c in (0, 1):
            exact, _, _ = _price(literal.partition(enc, c))
            expectation = archived[str(mask)][str(c)]
            for cls in CLASSES:
                assert F(expectation[cls]["raw_weight"]) == exact[cls]
            verified[str(c)] = {kind: str(F(exact[kind], literal.denominator)) for kind in CLASSES}
        rows[f"{mask:04b}"] = verified
    return {
        "all_archived_named_coordinate_encoders_matched": rows,
        "hidden_mask": "0000", "example_true_three_coordinate_mask": "0111",
        "scope": "These coordinate prices check one specified family of encoders.",
    }


def _transport_complement(literal):
    for h in SPENT:
        for k in RECORDS:
            g = literal.grams[literal.ids[h][k]]
            complement = literal.grams[literal.ids[h][k ^ 510]]
            assert all(g[x][y] == complement[x ^ 7][y ^ 7] for x in FOCAL for y in FOCAL)
            w, d0, d1 = literal.grades[h][k]
            assert literal.grades[h][k ^ 510] == (w, d1, d0)


def _index(word, marks):
    value = 0
    for n in marks:
        value = (value << 1) | ((word >> n) & 1)
    return value


def _map_index(index, before_names, after_names, image):
    before = {image[n]: index >> (len(before_names) - 1 - j) & 1 for j, n in enumerate(before_names)}
    return sum(before[n] << j for j, n in enumerate(reversed(after_names)))


def _physically_transport_one(law, literal, inherited):
    tested = 7
    roster = inherited["source_roster"]
    placement = inherited["changed_name_placements"][str(tested)]
    actual_names = tuple(n for n in range(7, 16) if n != tested)
    payer_names = (0, 1, 2, 3)
    mapping = placement["physical_name_image"]
    assert mapping[15] == tested and mapping[3] == 1
    assert sorted(sorted(mapping[n] for n in row) for row in roster) == sorted(map(sorted, roster))
    assert [mapping[n] for n in (4, 5, 6)] == [4, 5, 6]
    h_images = tuple(_map_index(h, payer_names, payer_names, mapping) for h in SPENT)
    k_images = tuple(2 * _map_index(k >> 1, tuple(range(7, 15)), actual_names, mapping) + (k & 1) for k in RECORDS)
    assert list(h_images) == placement["paid_character_image"] and list(k_images) == placement["mixed_record_image"]
    allowed_masks = tuple(sum(1 << n for n in row) for row in roster)
    physical = [[[[0] * 8 for _s in SPENT] for _t in (0, 1)] for _u in range(256)]
    count = 0
    for ordinary_word in range(1 << 16):
        offsets = tuple(ordinary_word & mask for mask in allowed_masks)
        if law == "parity":
            legal = not any(n.bit_count() % 2 for n in offsets)
        else:
            legal = all(0 < a < b for a, b in zip(offsets, allowed_masks, strict=True))
        if legal:
            s = _index(ordinary_word, payer_names)
            u = _index(ordinary_word, actual_names)
            t = ordinary_word >> tested & 1
            x = _index(ordinary_word, (4, 5, 6))
            assert physical[u][t][s][x] == 0
            physical[u][t][s][x] = 1
            count += 1
    assert count * 32 == literal.denominator
    for h in SPENT:
        h_new = h_images[h]
        for k in RECORDS:
            u, b = divmod(k_images[k], 2)
            values = [0] * 8
            for t in (0, 1):
                for s in SPENT:
                    factor = (-1) ** ((s & h_new).bit_count() + b * t)
                    for x, allowed in enumerate(physical[u][t][s]):
                        values[x] += factor * allowed
            observed = tuple(tuple(x * y for y in values) for x in values)
            assert literal.grams[literal.ids[h][k]] == observed
    return {
        "changed_name": tested, "changed_paying_name": 1, "unchanged_focal_names": (4, 5, 6),
        "paid_sign_image": h_images, "sibling_record_image": k_images,
        "validated_relabelings_from_B": inherited["changed_name_placements"],
        "full_original_words_checked": count, "signed_matrices_recomputed_under_nonidentity_address": 8192,
    }


def _summarize_prices(prices, den):
    return {cls: {"raw_weight": str(prices[cls]), "per_launch_rate": str(F(prices[cls], den))}
            for cls in CLASSES}


def _case(law, archive):
    physical = archive["literal_physical_audit"]
    case = physical["laws"][law]
    predecessor = case["views"]["mixed"]
    literal = _Literal(physical, predecessor)
    assert literal.denominator == case["N"] * 32
    _transport_complement(literal)
    previous_full = predecessor["subsets"]["15"]
    block_identity = _coordinate_partition(15)
    full_by_orientation = {}
    for c in (0, 1):
        grp = literal.partition(block_identity, c)
        value, masks, cert = _price(grp, witness=True)
        for cls in CLASSES:
            old = _previous_rule(previous_full, cls, c)
            previous_w, previous_d = _score_mask(grp, old)
            assert value[cls] == previous_w == F(previous_full[str(c)][cls]["raw_weight"])
            assert previous_d >= 0
        full_by_orientation[c] = (value, masks, cert)
    full, full_masks, full_cert = full_by_orientation[0]
    assert full_by_orientation[1][0] == full
    raw_lambda = F(full_cert["fractional_dual_multiplier_on_28_times_excess"])
    assert raw_lambda == F(previous_full["0"]["randomized"]["certificate"]["dual_multiplier"]) / 28
    pp, qq = raw_lambda.numerator, raw_lambda.denominator
    scaled_dual_field = tuple(tuple(qq * w + pp * d for w, d, _other in row) for row in literal.grades)
    dual_full_scaled = sum(max(0, t) for row in scaled_dual_field for t in row)
    assert F(dual_full_scaled, qq) == full["randomized"]
    prev_masks = {cls: _previous_rule(previous_full, cls, 0) for cls in CLASSES}
    chronological_pairs = tuple(combinations(SPENT, 2))
    pair_rows, exact_values = {}, {}
    maximum_common_dual = F(0)
    for pair in chronological_pairs:
        a, b = pair
        blocks = _pair_partition(a, b)
        pool = literal.partition(blocks, 0)
        prices, _, bound = _price(pool)
        exact_values[pair] = prices
        loss, conflicts, sample = _uniform_dual_pair(literal, scaled_dual_field, qq, pair)
        common_upper = full["randomized"] - loss
        actual_pooled_dual = sum(max(0, qq * w + pp * d) * len(labels) for (w, d), labels in pool.items())
        assert F(actual_pooled_dual, qq) == common_upper
        assert prices["deterministic"] <= full["deterministic"]
        assert prices["deterministic"] <= prices["randomized"] <= common_upper
        maximum_common_dual = max(maximum_common_dual, common_upper)
        pair_rows[f"{a:04b}/{b:04b}"] = {
            "merging_labels": pair, "prices": _summarize_prices(prices, literal.denominator),
            "fractional_full_dual_loss": str(loss), "fractional_full_dual_upper": str(common_upper),
            "strict_opposite_dual_record_count": conflicts, "first_supported_strict_collision": sample,
            "archive_canonical_decision_conflicts": _prior_canonical_conflicts(literal, pair, prev_masks),
            "saturates_identity": {kind: prices[kind] == full[kind] for kind in CLASSES},
            "integer_minimum_deficit_certificate": bound["integer"],
            "refit_fractional_dual_multiplier": bound["fractional_dual_multiplier_on_28_times_excess"],
        }
    assert len(pair_rows) == 120
    control = _projected_coordinate_control(literal, predecessor["subsets"])
    transport = _physically_transport_one(law, literal, case)
    total = _sum_grams((literal.grams[i], n) for i, n in Counter(i for row in literal.ids for i in row).items())
    assert sum(total[i][i] for i in FOCAL) == literal.denominator
    tops = {}
    for cls in CLASSES:
        threshold = max(v[cls] for v in exact_values.values())
        ties = tuple(k for k, v in exact_values.items() if v[cls] == threshold)
        examples = []
        witnessed_pairs = ties if law != "parity" else ties[:1]
        for pair in witnessed_pairs:
            blocks = _pair_partition(*pair)
            values, opt, _ = _price(literal.partition(blocks, 0), witness=True)
            c0 = _rule_receipt(literal, blocks, opt[cls], 0, total)
            reversed_mask = {512 * (i // 512) + ((i % 512) ^ 510): p for i, p in opt[cls].items()}
            checked_c1, _, _ = _price(literal.partition(blocks, 1))
            assert checked_c1 == values
            c1 = _rule_receipt(literal, blocks, reversed_mask, 1, total)
            assert F(c0["go"]["w"]) == F(c1["go"]["w"]) == threshold == values[cls]
            for port in ("go", "decline"):
                for k in ("w", "I", "original_launch_probability", "28_times_raw_surplus"):
                    assert c0[port][k] == c1[port][k]
                tab0, tab1 = (r[port]["conditional_table"] for r in (c0, c1))
                if tab0:
                    assert all(tab0[s][a] == tab1[s][a ^ (7 ^ s)] for s in FOCAL for a in FOCAL)
                else:
                    assert tab1 is None
            # The independently recomputed nonidentity address uses the same amplitudes under a literal bijection.
            # Its transmitted class must move the named paid character, not just the sibling answer.
            h_to, k_to = transport["paid_sign_image"], transport["sibling_record_image"]
            target_blocks = tuple(sorted(tuple(sorted(h_to[h] for h in block)) for block in blocks))
            symbol_image = tuple(target_blocks.index(tuple(sorted(h_to[h] for h in block))) for block in blocks)
            accepted_at_transported_address = sorted((512 * symbol_image[i // 512] + k_to[i % 512], str(p))
                                                      for i, p in opt[cls].items())
            examples.append({"merge": pair, "c0": c0, "c1": c1,
                             "address_7_transported_blocks": target_blocks,
                             "address_7_transported_mask": accepted_at_transported_address})
        tops[cls] = {
            "best_proper_weight": str(threshold), "best_proper_per_launch": str(F(threshold, literal.denominator)),
            "full_gap_raw_weight": str(full[cls] - threshold), "maximizing_pairs": ties,
            "witnesses": examples,
            "unlisted_parity_ties_use_the_same_constant_decline_rule": law == "parity",
        }
    constructor = {cls: _rule_receipt(literal, block_identity, full_masks[cls], 0, total) for cls in CLASSES}
    return {
        "original_full_word_count": case["N"], "launch_denominator": literal.denominator,
        "literal_record_count": 8192, "distinct_regraded_archived_grams": literal.numerical_types,
        "per_true_h_original_launch_masses": predecessor["true_h_port_masses"],
        "identity": {"prices": _summarize_prices(full, literal.denominator), "attainment": constructor,
                     "both_orientations_independently_priced": True, "certificate": full_cert},
        "pair_prices": pair_rows, "best_proper": tops,
        "coordinate_control": control, "address_transports": transport,
        "orientation_transport": "Keep h and b fixed, complement the eight ordinary sibling values, and complement focal outputs only at their Z settings.",
        "uniform_dual": {
            "multiplier_on_28_times_surplus": str(raw_lambda), "maximum_pair_bound_raw_weight": str(maximum_common_dual),
            "strictly_below_full_integer_target": maximum_common_dual < full["deterministic"],
            "strictly_below_full_fractional_target": maximum_common_dual < full["randomized"],
            "pairs_priced": 120,
        },
    }


def _sources():
    read = SOURCE.read_bytes()
    raw_receipt = RECEIPT.read_bytes()
    assert sha256(FREEZE.read_bytes()).hexdigest() == FREEZE_HASH
    assert sha256(read).hexdigest() == SOURCE_HASH and sha256(raw_receipt).hexdigest() == RECEIPT_HASH
    receipt = json.loads(raw_receipt)
    assert receipt["sha256"] == SOURCE_HASH and receipt["bytes"] == len(read)
    assert receipt["artifact"] == SOURCE.name
    sources = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
               for p in (Path(__file__).resolve(), SOURCE, RECEIPT, FREEZE)}
    variants = receipt["physical_public_variants"]
    for loc, digest in receipt["source_bindings"].items():
        p = ROOT / loc
        observed = sha256(p.read_bytes()).hexdigest()
        assert observed in (digest, variants.get(loc)), loc
        sources[loc] = digest
    return json.loads(gzip.decompress(read)), sources, variants


def run():
    """Return a JSON-ready independent audit of full, paired, and coordinate encoders."""
    older, sources, variants = _sources()
    return {
        "source_sha256": sources, "public_source_variants": variants,
        "laws": {law: _case(law, older) for law in LAWS},
        "binary_order": {"spent": "h is the actual four paid signs, named 0 through 3 with oldest first",
                         "sibling": "k is 2*u+b, X plus is b=0, Z values listed by increasing physical names",
                         "mask": "index is 512*symbol + k, with symbol classes listed lexicographically by their least h"},
        "dynamic_program": "Minimum extra deficit for each additional accepted weight. Binary chunks describe every count of each numerical type, and the continuous dual caps the accepted-weight index. Original labels remain independently selectable.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = run()
    data = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if args.smoke:
        for law, item in result["laws"].items():
            for cls in CLASSES:
                proper = item["best_proper"][cls]
                print(law, cls, item["identity"]["prices"][cls]["raw_weight"], proper["best_proper_weight"],
                      len(proper["maximizing_pairs"]))
        print(sha256(data.encode()).hexdigest())
    else:
        print(data)


if __name__ == "__main__":
    main()
