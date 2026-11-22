"""Literal word replay of the reached source with a single changed sibling."""

import argparse
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "research/SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001A"
ARCHIVE = PREVIOUS / "announcement_evidence.json.gz"
RECEIPT = PREVIOUS / "receipt.json"
FREEZE = HERE / "preregistration.md"
FROZEN_SHA256 = "fa06f3a6c829b800d210ce1c85fc7b6cb437a72b566ef7536f977eb9b22824de"
LAWS = ("parity", "nae")
SPENT = (0, 1, 2, 3)
FOCAL = (4, 5, 6)
SIBLINGS = tuple(range(7, 16))
PRIMARY_CHANGE = SIBLINGS[-1]
ANNOUNCEMENT = (16, 17, 18)
STATUS = (19, 20, 21)
SETTINGS = range(8)
PAST_WORDS = range(16)
TARGET = F(1, 28)
SIGNS = (1, -1)


@cache
def _bits(n, width):
    return tuple(n >> i & 1 for i in reversed(range(width)))


def _lex(bits):
    out = 0
    for bit in bits:
        out = 2 * out + bit
    return out


def _read(raw, names):
    return _lex(raw >> n & 1 for n in names)


def _embed(value, names):
    return sum(bit << n for bit, n in zip(_bits(value, len(names)), names, strict=True))


def _parity_sign(i):
    return SIGNS[i.bit_count() % 2]


def _admitted(word, mask, law):
    value = word & mask
    if law == "parity":
        return value.bit_count() % 2 == 0
    return value not in (0, mask)


def _matrix(data):
    return tuple(tuple(x) for x in data)


def _outer(a, b):
    return tuple(tuple(x * y for y in b) for x in a)


def _zero():
    return ((0,) * 8,) * 8


def _sum(grams):
    totals = [[0] * 8 for _ in SETTINGS]
    for g in grams:
        for a, row in enumerate(g):
            for b, v in enumerate(row):
                totals[a][b] += v
    return _matrix(totals)


def _scaled(gram, factor):
    return tuple(tuple(v * factor for v in row) for row in gram)


def _trace(gram):
    return sum(row[i] for i, row in enumerate(gram))


def _weighted_score(table, c):
    target = 7 if c else 0
    reward = sum(table[7][answers] for answers in (3, 5, 6, 7))
    charge = table[0][target]
    for x_setting in (1, 2, 4):
        both_z = 7 ^ x_setting
        charge += sum(table[x_setting][answers] for answers in SETTINGS
                      if answers & x_setting and (answers & both_z) != (target & both_z))
    return reward - charge


def _projectors(gram):
    table = []
    for prompts in SETTINGS:
        z = 7 ^ prompts
        raw = []
        for answer in SETTINGS:
            support = tuple(x for x in SETTINGS if (x & z) == (answer & z))
            numerator = sum(_parity_sign((x ^ y) & answer & prompts) * gram[x][y] for x in support for y in support)
            raw.append(F(numerator, 1 << prompts.bit_count()))
        assert sum(raw) == _trace(gram) and min(raw) >= 0
        table.append(tuple(raw))
    return tuple(table)


def _local_marginals(table):
    for subset in range(1, 7):
        seen = {}
        for s, row in enumerate(table):
            marginal = tuple(sum(q for a, q in enumerate(row) if a & subset == ans)
                             for ans in SETTINGS if ans & subset == ans)
            assert seen.setdefault(s & subset, marginal) == marginal


class _Library:
    def __init__(self):
        self.indices = {}
        self.grams = []
        self.probabilities = []
        self.raw_tables = []
        self.w_scores = []

    def register(self, g):
        if g not in self.indices:
            i = len(self.grams)
            self.indices[g] = i
            self.grams.append(g)
            w = _trace(g)
            raw = _projectors(g)
            self.raw_tables.append(raw)
            self.w_scores.append(tuple(_weighted_score(raw, c) for c in (0, 1)))
            if w:
                _local_marginals(raw)
            else:
                assert g == _zero()
            self.probabilities.append([[str(v / w) for v in row] for row in raw] if w else None)
        return self.indices[g]

    def packet(self, g, launch, prepared):
        i = self.register(g)
        w = _trace(g)
        p, q = self.w_scores[i]
        return {
            "gram": i, "weight": w, "I0": str(p / w) if w else None, "I1": str(q / w) if w else None,
            "wI0": str(p), "wI1": str(q), "loss": str(w * TARGET - p), "excess": str(p - w * TARGET),
            "original_launch_denominator": launch, "original_launch_probability": str(F(w, launch)),
            "prepared_source_denominator": prepared, "prepared_source_probability": str(F(w, prepared)),
            "per_launch_joint_setting_denominator": 8 * launch,
        }


def _focal_bound():
    scores = {0: [], 1: []}
    for responses in product((0, 1), repeat=6):
        table = []
        for s in SETTINGS:
            a = _lex(responses[2 * i + b] for i, b in enumerate(_bits(s, 3)))
            table.append(tuple(int(x == a) for x in SETTINGS))
        for c in (0, 1):
            scores[c].append(_weighted_score(table, c))
    assert all(len(v) == 64 and max(v) == 0 for v in scores.values())
    return {"list_order": "Z1,X1,Z2,X2,Z3,X3 lexicographic", "upper_bound": 0, "values": scores}


def _actual_words(law, past):
    reached = tuple(tuple(row) for row in past["ordinary"]["reached"])
    original = tuple(tuple(row) for row in past["ordinary"]["original"])
    wanted = (SPENT, *((i, *range(4 + 3 * i, 7 + 3 * i)) for i in SPENT))
    if reached != wanted:
        return None, reached, "the paid birth's complete named support is missing"
    assert original == (SPENT,)
    assert past["ordinary"]["focal_paid_name"] == 0
    assert tuple(past["ordinary"]["focal_read_order"]) == FOCAL
    assert tuple(past["ordinary"]["sibling_read_order"]) == SIBLINGS
    events = past["ordinary"]["births"]
    assert past["ordinary"]["status"] == "funded" and len(events) == 4
    for i, event in enumerate(events):
        assert event["paid_names"] == [i] and event["holder"] == i + 1 and event["parent_holders"] == [0]
        assert event["lookahead_demand"] == event["fresh_grant"] == 3
        assert tuple(event["fresh_names"]) == wanted[i + 1][1:]
        assert past["ordinary"]["owners"][str(i)] == [0, i + 1]
        assert all(past["ordinary"]["owners"][str(k)] == [i + 1] for k in event["fresh_names"])
    clauses = tuple(sum(1 << n for n in row) for row in reached)
    words = [w for w in range(65536) if all(_admitted(w, row, law) for row in clauses)]
    if not words:
        return None, reached, "no lawful complete word at the named birth"
    assert words == past["literal_complete_words_lsb_name_zero"]
    assert len(words) == past["N"] and len(words) == len(set(words))
    for row, archived in zip(reached, past["reached_full_projections"], strict=True):
        projected = sorted({_read(w, row) for w in words})
        assert archived["names"] == list(row) and projected == archived["allowed_projected_word_indices"]
        assert all(archived[key] for key in ("K1", "K2", "K3", "canonical_check"))
        assert 0 < len(projected) < 16
        assert all(len({w & ~(1 << i) for w in projected}) == 8 for i in range(4))
    return words, reached, None


def _ordinary_masks(words):
    # An integer in each fibre is the bitset of legal focal words x at this actual (r,s).
    masks = [[0] * 16 for _ in range(512)]
    for raw in words:
        r = _read(raw, SIBLINGS)
        s = _read(raw, SPENT)
        x = _read(raw, FOCAL)
        assert not masks[r][s] & (1 << x)
        masks[r][s] |= 1 << x
    return masks


@cache
def _vector(mask):
    return tuple(mask >> i & 1 for i in SETTINGS)


def _walsh(sequence):
    rows = list(sequence)
    for width in (1, 2, 4, 8):
        for j in range(0, 16, 2 * width):
            for i in range(j, j + width):
                a, b = rows[i], rows[i + width]
                rows[i] = tuple(x + y for x, y in zip(a, b, strict=True))
                rows[i + width] = tuple(x - y for x, y in zip(a, b, strict=True))
    return tuple(rows)


def _raw(vectors):
    amplitudes = _walsh(vectors)
    return _sum(_outer(v, v) for v in vectors), tuple(_outer(n, n) for n in amplitudes), amplitudes


def _readiness_packet(law, words, archived):
    ready, yes, no = (int(s, 2) for s in ("110", "101", "011"))
    support = tuple(n for n in SETTINGS if _admitted(n, 7, law))
    assert all(n in support for n in (ready, yes, no))
    banks = (ANNOUNCEMENT, STATUS)
    assert len(set((*SPENT, *FOCAL, *SIBLINGS, *ANNOUNCEMENT, *STATUS))) == 22
    assert archived["keeper"]["complete_source_plus_two_banks_population"] == len(words) * len(support) ** 2
    for names, bank in zip(banks, archived["keeper"]["appended_banks"], strict=True):
        assert bank["names"] == list(names) and bank["allowed_projected_word_indices"] == list(support)
        assert 0 < len(support) < 8 and all(len({v & ~(1 << b) for v in support}) == 4 for b in range(3))

    def exchange(full, names, value):
        flipped = _embed(ready ^ value, names)
        assert flipped.bit_count() == 2 and (full & flipped).bit_count() == 1
        return full ^ flipped

    events = {}
    for label, admitted, desired, connected, start in (
        ("addressed_yes", True, True, True, ready),
        ("addressed_no", True, False, True, ready),
        ("clean_or_source_refusal", False, None, True, ready),
        ("disconnected_public_writer", True, True, False, ready),
        ("busy_old_yes", True, True, True, yes),
    ):
        initial = words[0] | _embed(start, ANNOUNCEMENT) | _embed(ready, STATUS)
        after_status = exchange(initial, STATUS, yes if admitted else no)
        writing = admitted and connected and start == ready
        final = exchange(after_status, ANNOUNCEMENT, yes if desired else no) if writing else after_status
        assert final & 65535 == words[0]
        written = _read(final, ANNOUNCEMENT)
        status = _read(final, STATUS)
        assert written in support and status in support
        events[label] = {
            "initial_complete_word_lsb_name_zero": initial, "output_complete_word_lsb_name_zero": final,
            "from_ready_or_busy": f"{start:03b}", "status_bank": f"{status:03b}",
            "announcement_bank": f"{written:03b}", "fresh_write": writing,
            "fresh_go": writing and desired,
        }
    assert events["addressed_yes"]["announcement_bank"] == "101" and events["addressed_yes"]["fresh_go"]
    assert events["addressed_no"]["announcement_bank"] == "011" and not events["addressed_no"]["fresh_go"]
    for key in ("clean_or_source_refusal", "disconnected_public_writer"):
        assert events[key]["announcement_bank"] == "110" and not events[key]["fresh_go"]
    assert events["busy_old_yes"]["announcement_bank"] == "101" and not events["busy_old_yes"]["fresh_go"]
    return {"named_banks_announcement_then_source_status": banks, "legal_words": tuple(f"{v:03b}" for v in support),
            "events": events, "retained_source_word_unchanged_by_bank_contacts": True,
            "keeper_supplied_scope": "A supplied control addresses the bank after the fine record or binary effect. Comparing a predicate in the evaluator does not connect the writer."}


def _ordinary_names(j):
    return tuple(n for n in SIBLINGS if n != j)


def _complete(u, t, j):
    before = list(_bits(u, 8))
    before.insert(SIBLINGS.index(j), t)
    return _lex(before)


def _one_change_vectors(left, right, b):
    return tuple(tuple(x + SIGNS[b] * y for x, y in zip(a, z, strict=True))
                 for a, z in zip(left, right, strict=True))


def _actual_mixed_rows(masks, N, W, library):
    ordinary = tuple(_raw(tuple(_vector(v) for v in at_r)) for at_r in masks)
    mixed, packets = [], []
    den_d, den_q = 2 * N, 32 * N
    for u in range(256):
        r0, r1 = (_complete(u, t, PRIMARY_CHANGE) for t in (0, 1))
        a, z = tuple(tuple(_vector(v) for v in masks[r]) for r in (r0, r1))
        no_cross_d = _sum(ordinary[r][0] for r in (r0, r1))
        no_cross_h = tuple(_sum(ordinary[r][1][h] for r in (r0, r1)) for h in PAST_WORDS)
        physical_legs = tuple(ordinary[r][2] for r in (r0, r1))
        same_past_cross = _sum(_outer(v0, v1) for v0, v1 in zip(a, z, strict=True))
        same_past_symmetric = _sum((same_past_cross, _matrix(zip(*same_past_cross))))
        for b in (0, 1):
            index = 2 * u + b
            vectors = _one_change_vectors(a, z, b)
            d, ports, n = _raw(vectors)
            assert _sum(ports) == _scaled(d, 16)
            assert d == _sum((no_cross_d, _scaled(same_past_symmetric, SIGNS[b])))
            for h, wh in enumerate(n):
                # Direct sign pairing from the ordinary-word sectors, with its sign intact.
                assert wh == tuple(x + SIGNS[b] * y for x, y in zip(physical_legs[0][h], physical_legs[1][h], strict=True))
                assert no_cross_h[h] == _sum(_outer(leg[h], leg[h]) for leg in physical_legs)
            # An explicit ordinary-basis phase operator at the changed name acts on the t=1 amplitudes.
            phase_legs = (a, tuple(tuple(-v for v in word) for word in z))
            phase_vectors = _one_change_vectors(*phase_legs, b)
            assert phase_vectors == _one_change_vectors(a, z, 1 - b)
            assert _walsh(phase_vectors) == _walsh(_one_change_vectors(a, z, 1 - b))
            mixed.append((d, ports, vectors, n))
            entry_d = library.packet(d, den_d, den_d)
            entry_q = library.packet(ports[0], den_q, 2 * W)
            tag_d = library.register(no_cross_d)
            tag_h = tuple(library.register(g) for g in no_cross_h)
            packets.append({
                "index": index, "u_index": u, "u": f"{u:08b}", "b": b,
                "ordinary_completion_indices": (r0, r1),
                "retained": entry_d, "clean": entry_q,
                "character_grams": tuple(library.register(g) for g in ports),
                "character_traces": tuple(_trace(g) for g in ports),
                "changed_value_tagged_retained_gram": tag_d,
                "changed_value_tagged_character_grams": tag_h,
                "spent_value_tagged_each_character_gram": entry_d["gram"],
                "both_value_tags_each_character_gram": tag_d,
                "phase_flipped_canonical_row": index ^ 1,
                "ordinary_focal_support_masks_at_each_completion_by_spent_word": (masks[r0], masks[r1]),
            })
        plus, minus = mixed[-2:]
        assert _sum((plus[0], minus[0])) == _scaled(no_cross_d, 2)
        assert all(_sum((a, z)) == _scaled(t, 2) for a, z, t in zip(plus[1], minus[1], no_cross_h, strict=True))
    total_d = _sum(row[0] for row in mixed)
    total_h = tuple(_sum(row[1][h] for row in mixed) for h in PAST_WORDS)
    assert _trace(total_d) == 2 * N
    assert _trace(total_h[0]) == 2 * W
    return ordinary, mixed, packets, total_d, total_h


def _checked_placements(masks, reached, mixed):
    fixed_blocks = tuple(tuple(b for b in row if b in SIBLINGS) for row in reached[2:])
    assert len(fixed_blocks) == 3 and tuple(n for block in fixed_blocks for n in block) == SIBLINGS
    incidence = {frozenset(row) for row in reached}
    checks = {}
    for j in SIBLINGS:
        k = (j - SIBLINGS[0]) // 3
        target_block = fixed_blocks[k]
        image = dict(enumerate(range(16)))
        source = (reached[4][0], *fixed_blocks[2])
        target = (reached[k + 2][0], *target_block)
        for a, b in zip(source, target, strict=True):
            image[a], image[b] = image[b], image[a]
        # Swap the image of the fixed change address with the desired named sibling.
        moved = target_block[-1]
        for n, v in tuple(image.items()):
            if v == moved:
                image[n] = j
            elif v == j:
                image[n] = moved
        assert set(image.values()) == set(image)
        assert {frozenset(image[n] for n in row) for row in reached} == incidence
        assert image[PRIMARY_CHANGE] == j and all(image[n] == n for n in FOCAL)
        inverse = {v: n for n, v in image.items()}
        target_names = _ordinary_names(j)
        old_u_names = _ordinary_names(PRIMARY_CHANGE)
        u_sequence = tuple(old_u_names.index(inverse[n]) for n in target_names)
        s_sequence = tuple(SPENT.index(inverse[s]) for s in SPENT)
        perm_s = tuple(_lex(_bits(s, 4)[i] for i in s_sequence) for s in PAST_WORDS)
        inverse_s = tuple(perm_s.index(s) for s in PAST_WORDS)
        perm_u = tuple(_lex(_bits(u, 8)[i] for i in u_sequence) for u in range(256))
        for u, new_u in enumerate(perm_u):
            old_words = tuple(masks[_complete(u, t, PRIMARY_CHANGE)] for t in (0, 1))
            new_words = tuple(masks[_complete(new_u, t, j)] for t in (0, 1))
            for old, new in zip(old_words, new_words, strict=True):
                assert all(old[s] == new[perm_s[s]] for s in PAST_WORDS)
            v0, v1 = tuple(tuple(_vector(mask) for mask in word) for word in new_words)
            for b in (0, 1):
                new_v = _one_change_vectors(v0, v1, b)
                old = mixed[2 * u + b]
                assert all(new_v[s] == old[2][inverse_s[s]] for s in PAST_WORDS)
                assert all(raw == old[3][inverse_s[h]] for h, raw in enumerate(_walsh(new_v)))
        checks[str(j)] = {
            "physical_changed_name": j, "eight_ordinary_names": target_names,
            "name_image_by_old_name": tuple(image[n] for n in range(16)),
            "ordinary_bit_image_sequence": u_sequence,
            "spent_word_and_character_image_by_old_index": perm_s,
            "X_label_image": (0, 1),
            "verified_matched_signed_vectors_and_zeros": 512 * 16,
        }
    return checks


def _checked_complement(masks, mixed, library):
    for r in range(512):
        for s in PAST_WORDS:
            opposite = sum(1 << (x ^ 7) for x in SETTINGS if masks[r][s] >> x & 1)
            assert masks[r ^ 511][s ^ 15] == opposite
    for u in range(256):
        for sign in (0, 1):
            a = mixed[2 * u + sign]
            b = mixed[2 * (u ^ 255) + sign]
            assert all(all(a[2][s][x] == SIGNS[sign] * b[2][s ^ 15][x ^ 7] for x in SETTINGS) for s in PAST_WORDS)
            for h, v in enumerate(a[3]):
                phase = _parity_sign(h) * SIGNS[sign]
                assert all(v[x] == phase * b[3][h][x ^ 7] for x in SETTINGS)
            for m, p in zip((a[0], *a[1]), (b[0], *b[1]), strict=True):
                assert all(m[x][y] == p[x ^ 7][y ^ 7] for x in SETTINGS for y in SETTINGS)
                i, j = library.register(m), library.register(p)
                q, q_opp = (library.raw_tables[k] for k in (i, j))
                assert all(q[s][z] == q_opp[s][z ^ (7 ^ s)] for s in SETTINGS for z in SETTINGS)
                assert library.w_scores[i][0] == library.w_scores[j][1]
    return {
        "complemented_ordinary_sibling_label": "u XOR 255", "change_sign_image": (0, 1),
        "retained_vector_phase_at_b": SIGNS, "spent_character_vector_phase": "(-1) ** (popcount(h)+b)",
        "focal_Z_answers_complement_and_X_answers_retain_labels": True,
        "all_lawful_words_all_signed_ports_and_both_fixed_statistics_checked": True,
    }


def _compare_old_packet(gram, den, packet):
    assert gram == tuple(tuple(F(v) for v in row) for row in packet["gram"])
    w = _trace(gram)
    raw = _projectors(gram)
    assert F(packet["raw_trace"]) == w and F(packet["launch_mass"]) == w / den
    if w:
        assert F(packet["conditional_I"]) == _weighted_score(raw, 0) / w
        assert tuple(tuple(F(v) for v in row) for row in packet["conditional_8by8"]) == _scaled(raw, F(1, w))
    else:
        assert packet["conditional_I"] is None and packet["conditional_8by8"] is None
    for k, d in (("per_launch_given_each_setting", den), ("per_launch_joint_settings_and_outcomes", 8 * den)):
        assert tuple(tuple(F(v) for v in row) for row in packet[k]) == _scaled(raw, F(1, d))


def _compare_ordinary_rates(mode, ordinary, den, prior, library):
    answers = {}
    for view in ("full", "eight"):
        grams = ordinary if view == "full" else tuple(_sum(ordinary[i:i + 2]) for i in range(0, 512, 2))
        weight = tuple(_trace(g) for g in grams)
        cost = tuple(w * TARGET - library.w_scores[library.register(g)][0] for w, g in zip(weight, grams, strict=True))
        credit = -sum(c for c in cost if c < 0)
        min_positive_cost = min(c for c, w in zip(cost, weight, strict=True) if c > 0 and w > 0)
        assert credit < min_positive_cost
        upper_integer = sum(w for w, c in zip(weight, cost, strict=True) if c <= 0)
        for class_name in ("deterministic", "randomized"):
            key = f"{view}/{class_name}"
            record = prior["modes"][mode]["primary_and_controls_rules"][key]
            mask = tuple(map(F, record["mask"]))
            assert len(mask) == 512
            if view == "eight":
                assert mask[::2] == mask[1::2]
                mask = mask[::2]
            assert all(0 <= f <= 1 for f in mask)
            value = sum(a * w for a, w in zip(mask, weight, strict=True))
            assert sum(a * c for a, c in zip(mask, cost, strict=True)) <= 0
            if class_name == "deterministic":
                assert all(a in (0, 1) for a in mask)
                bound = upper_integer
            else:
                multiplier = F(record["optimum_certificate"]["multiplier"])
                assert multiplier >= 0
                bound = sum(max(0, w - multiplier * c) for w, c in zip(weight, cost, strict=True))
            assert bound == value == F(record["attained_weight"])
            assert value / den == F(record["per_initial_launch_rate"])
            answers[key] = {"original_launch_rate": str(value / den), "attained_and_upper_weight": str(value)}
    return answers


def _archive_anchors(source, prior, old_grams, masks, ordinary, mixed, total_d, total_h, N, W, library):
    for row, mask, (d, chars, _n) in zip(source["rows"], masks, ordinary, strict=True):
        assert row["focal_masks_by_spent_word"] == mask
        assert old_grams[row["retained"]["gram"]] == d
        assert tuple(old_grams[j] for j in row["character_grams"]) == chars
        assert _trace(d) == row["literal_word_count"]
    assert _scaled(old_grams[source["unannounced_retained"]["gram"]], 2) == total_d
    assert tuple(_scaled(old_grams[record["gram"]], 2) for record in source["unannounced_character_ports"]) == total_h
    anchors = {}
    for mode, den, selected, total, norm in (
        ("retained", N, tuple(r[0] for r in ordinary), total_d, 2 * N),
        ("clean", 16 * N, tuple(r[1][0] for r in ordinary), total_h[0], 2 * W),
    ):
        baseline = prior["source_and_instrument_controls"][mode]["eight_ordinary_zero_plus_one_sibling_change"]
        a, b = (mixed[i][0] if mode == "retained" else mixed[i][1][0] for i in (0, 1))
        d_plus, d_minus = _scaled(a, F(1, 2)), _scaled(b, F(1, 2))
        null_cross = _scaled(_sum(selected[0:2]), F(1, 2))
        total_ordinary = _scaled(total, F(1, 2))
        outside = _sum((total_ordinary, _scaled(null_cross, -2)))
        cases = {"coherent_plus": d_plus, "coherent_minus": d_minus, "complementary_tuples_outside_pair": outside,
                 "diagonal_fair_accept": null_cross, "diagonal_fair_reject_inside": null_cross,
                 "diagonal_full_complement": _sum((null_cross, outside)),
                 "coherent_full_complement": _sum((d_minus, outside))}
        for key, g in cases.items():
            _compare_old_packet(g, den, baseline[key])
        assert baseline["sibling_words"] == ["000000000", "000000001"]
        assert F(baseline["coarse_or_logged_pair_read_price"]) == (_trace(a) + _trace(b)) / F(2 * den)
        anchors[mode] = {
            "ordinary_optima_directly_rechecked": _compare_ordinary_rates(mode, selected, den, prior, library),
            "matched_old_anchor_fields": tuple(cases), "matched_both_ports_earlier_replay": True,
            "eight_zero_plus": library.packet(a, 2 * den, norm),
            "eight_zero_minus": library.packet(b, 2 * den, norm),
        }
    return {
        "all_512_ordinary_words_retained_and_all_character_matrices_match": True,
        "all_16_unannounced_source_aggregate_matrices_match_after_scaling": True,
        "physical_ordinary_optima_and_eight_zero_probe": anchors,
    }


def _changed_support_boundary(words, reached, law):
    lawful = set(words)
    flips = 1 << PRIMARY_CHANGE
    one = next(w for w in words if w ^ flips not in lawful)
    unphysical = one ^ flips
    broken = tuple(row for row in reached if not _admitted(unphysical, sum(1 << k for k in row), law))
    assert len(broken) == 1 and PRIMARY_CHANGE in broken[0]
    # For this ordinary singleton, calibrated X+ and X- projectors each have squared norm 1/2.
    before = one >> PRIMARY_CHANGE & 1
    signs_before = tuple(SIGNS[b] ** before for b in (0, 1))
    after_phase = tuple(SIGNS[before] * signs_before[b] for b in (0, 1))
    assert after_phase == signs_before[::-1]
    return {
        "actual_ordinary_singleton": one,
        "unallowed_ordinary_word_reintroduced_in_a_kept_projected_target": unphysical,
        "violated_named_support": broken[0],
        "changed_input_t": before,
        "physical_X_sign_chances_on_singleton": ("1/2", "1/2"),
        "ordinary_word_integer_encoding": "bit n of the integer is the value at name n",
        "read_and_discard_scope": "X acts in a supplied two-value register. The record and the reduced focal state are evaluated after projection and discarding, without imposing the old relation on a post-projection ordinary word.",
    }


def _law_case(law, old_law, prior, old_grams, library):
    words, reached, reason = _actual_words(law, old_law)
    if reason:
        return {"status": "refused", "reason": reason, "ordinary_reached_rows": reached, "rows": []}
    N, W = len(words), old_law["W"]
    assert (N, W) == (prior["N"], prior["W"])
    masks = _ordinary_masks(words)
    ordinary, mixed, rows, total_d, total_h = _actual_mixed_rows(masks, N, W, library)
    launch_d, launch_q = 2 * N, 32 * N
    assert _sum(total_h) == _scaled(total_d, 16)
    clean_price = F(_trace(total_h[0]), launch_q)
    assert clean_price == F(W, 16 * N) == F(old_law["unannounced_clean"]["original_launch_probability"])
    assert sum(F(_trace(g), launch_q) for g in total_h) == 1
    spent_tag_packet = library.packet(total_d, launch_q, launch_d)
    assert spent_tag_packet["original_launch_probability"] == "1/16"
    bank = _readiness_packet(law, words, old_law)
    anchors = _archive_anchors(old_law, prior, old_grams, masks, ordinary, mixed, total_d, total_h, N, W, library)
    placements = _checked_placements(masks, reached, mixed)
    complement = _checked_complement(masks, mixed, library)
    refusal = _sum(total_h[1:])
    assert F(_trace(refusal), launch_q) + clean_price == 1
    zero = library.register(_zero())
    assert library.probabilities[zero] is None
    zeros_by_char = tuple(sum(row["character_traces"][h] == 0 for row in rows) for h in PAST_WORDS)
    zeros_retained = sum(r["retained"]["weight"] == 0 for r in rows)
    assert all((r["character_grams"][h] == zero) == (r["character_traces"][h] == 0) for r in rows for h in PAST_WORDS)
    return {
        "status": "funded_and_admitted", "N": N, "W": W, "clean_mixed_total_trace": 2 * W,
        "denominators": {"retained": launch_d, "clean_original_launch": launch_q, "clean_prepared_source": 2 * W},
        "rows": rows, "primary_changed_name": PRIMARY_CHANGE, "ordinary_reached_rows": reached,
        "verified_physical_words": len(words), "candidate_words_examined": 65536,
        "eight_ordinary_names": _ordinary_names(PRIMARY_CHANGE),
        "physical_placements": placements, "global_complement": complement,
        "eligible_source_probability": {"retained": "1", "clean": str(clean_price)},
        "clean_refusal_probability": str(1 - clean_price),
        "unannounced_readout": {
            "retained": library.packet(total_d, launch_d, launch_d),
            "clean": library.packet(total_h[0], launch_q, 2 * W),
            "characters": tuple(library.packet(g, launch_q, _trace(g) or launch_q) for g in total_h),
            "clean_source_refusal_pooled_nonzero_characters": library.packet(refusal, launch_q, launch_q),
            "spent_tag_present_each_character": spent_tag_packet,
            "spent_tag_present_refusal": library.packet(_scaled(total_d, 15), launch_q, launch_q),
        },
        "old_ordinary_anchor_and_both_ports": anchors, "keeper": bank,
        "zero_records": {"retained": zeros_retained, "character_ports_in_order": zeros_by_char,
                         "zero_gram_index": zero, "normalized_local_table_is_undefined": True,
                         "unobservable_record_does_not_write_a_keeper": True},
        "post_projection_source_relation_scope": _changed_support_boundary(words, reached, law),
        "checked_raw_identities": {"all_16_at_fixed_u_and_b_sum_to_16_retained": True,
                                   "both_signs_at_fixed_u_sum_to_twice_the_eight_name_ordinary_marginal": True,
                                   "ordinary_phase_flips_the_physically_recorded_X_sign_entrywise": True},
    }


def _input_bindings():
    frozen = sha256(FREEZE.read_bytes()).hexdigest()
    assert frozen == FROZEN_SHA256
    archive = ARCHIVE.read_bytes()
    receipt = json.loads(RECEIPT.read_bytes())
    assert receipt["sha256"] == sha256(archive).hexdigest() and receipt["gzip_bytes"] == len(archive)
    data = json.loads(gzip.decompress(archive))
    old_physical = data["paid_and_loose_physical_evidence"]
    direct = (Path(__file__).resolve(), FREEZE, ARCHIVE, RECEIPT)
    canonical = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in direct}
    variants = old_physical["public_source_variants"]
    inherited = {**old_physical["source_sha256"], **receipt["project_files"]}
    for key, historical in inherited.items():
        observed = sha256((ROOT / key).read_bytes()).hexdigest()
        assert observed == historical or observed == variants.get(key), key
        canonical[key] = historical
    return data, canonical, variants


def run():
    """Return raw Gram IDs, exact table libraries, and source-bound physical checks."""
    archive, digests, variants = _input_bindings()
    old = archive["paid_and_loose_physical_evidence"]
    old_grams = tuple(_matrix(gram) for gram in old["gram_library"])
    library = _Library()
    laws = {law: _law_case(law, old["laws"][law], archive["laws"][law], old_grams, library) for law in LAWS}
    return {
        "laws": laws, "gram_library": library.grams, "probability_library": library.probabilities,
        "source_sha256": digests, "public_source_variants": variants, "fixed_score": _focal_bound(),
        "focal_names": FOCAL, "spent_character_order_names": SPENT, "sibling_names": SIBLINGS,
        "primary_X_name": PRIMARY_CHANGE, "target": str(TARGET),
        "order": {
            "record": "index = 2*int(u,2)+b, first ordinary name most significant",
            "change_sign": "b=0 plus, b=1 minus",
            "settings_focal": "first focal physical name is the most significant, Z=0, X=1",
            "answer_and_gram_basis": "first focal physical name is the most significant, plus=0 for signs",
            "spent_characters": "in SPENT order, 0000 is all plus",
            "per_launch_cell": "probability_library[gram][setting][answer] times trace(gram) divided by the proper original launch denominator",
            "joint_per_launch_cell": "the per-launch cell times 1/8 for each independent fair setting",
            "tags": "changed-value and spent-value tags are different orthogonal records. A coherent return before the corresponding questions restores the untagged IDs.",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = run()
    raw = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if args.smoke:
        for law, values in result["laws"].items():
            print(law, values["N"], values["W"], len(values["rows"]), len(values["physical_placements"]),
                  values["zero_records"]["retained"], values["zero_records"]["character_ports_in_order"][0])
        print(sha256(raw.encode()).hexdigest())
    else:
        print(raw)


if __name__ == "__main__":
    main()
