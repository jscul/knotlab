"""Independent literal-word and exact minimum-deficit audit of the disclosed spent signs."""

import argparse
from array import array
from collections import Counter, defaultdict, deque
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from math import gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EARLIER = {
    "mixed": ROOT / "research/SIBLING-CHANGE-ANNOUNCEMENTS-20261121-001A",
    "nine_z": ROOT / "research/SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001A",
}
FREEZE = HERE / "preregistration.md"
FREEZE_SHA256 = "d44b2b25d8d85d89bc074289763f49f2ad7a6927394d332deb91947e5e1c937e"
PHYSICAL_KEYS = {"mixed": "physical_input", "nine_z": "paid_and_loose_physical_evidence"}
LAWS = ("parity", "nae")
P = (0, 1, 2, 3)
X = (4, 5, 6)
R = tuple(range(7, 16))
FOCAL_WORDS = tuple(range(8))
H = tuple(range(16))
K = tuple(range(512))
COST_UNITS = 56
ZERO = ((0,) * 8,) * 8
CLASSES = ("deterministic", "randomized")


def _bin(word, names):
    return sum((word >> n & 1) << i for i, n in enumerate(reversed(names)))


def _int(bits):
    x = 0
    for b in bits:
        x = x * 2 + b
    return x


def _sign(n):
    return 1 - 2 * (n.bit_count() % 2)


def _admitted_bits(word, width, law):
    if law == "parity":
        return word.bit_count() % 2 == 0
    return word not in (0, (1 << width) - 1)


def _matrix(rows):
    return tuple(tuple(r) for r in rows)


def _scores(rows, c):
    expected = 7 * c
    return (sum(rows[7][a] for a in (3, 5, 6, 7)) - rows[0][expected]
            - sum(rows[s][a] for s in (1, 2, 4) for a in FOCAL_WORDS
                  if (s & a) and (a & (7 ^ s)) != (expected & (7 ^ s))))


def _normalized_moments(gram):
    w = sum(gram[i][i] for i in FOCAL_WORDS)
    rows = []
    for s in FOCAL_WORDS:
        moments = []
        for subset in FOCAL_WORDS:
            flip = subset & s
            diag = subset & (7 ^ s)
            moments.append(sum(_sign(diag & x) * gram[x][x ^ flip] for x in FOCAL_WORDS))
        line = tuple(F(sum(_sign(a & j) * moment for j, moment in enumerate(moments)), 8) for a in FOCAL_WORDS)
        assert sum(line) == w and min(line) >= 0
        rows.append(line)
    if w:
        for retained in range(1, 7):
            known = {}
            for s, row in enumerate(rows):
                marginal = tuple(sum(v for a, v in enumerate(row) if a & retained == seen)
                                 for seen in FOCAL_WORDS if seen & retained == seen)
                assert known.setdefault(s & retained, marginal) == marginal
    else:
        assert gram == ZERO
    return w, rows


def _deterministic_limit():
    verdict = [[], []]
    settings = list(product((0, 1), repeat=3))
    for six in product((0, 1), repeat=6):
        fixed = [_int(six[2 * i + mode] for i, mode in enumerate(s)) for s in settings]
        table = [[int(a == q) for a in FOCAL_WORDS] for q in fixed]
        for orientation in (0, 1):
            verdict[orientation].append(_scores(table, orientation))
    assert all(max(row) == 0 for row in verdict)
    return {"order": "each pair is Z then X, and the three pairs use focal name order", "scores": verdict, "bound": 0}


class _Tables:
    def __init__(self):
        self.ids = {}
        self.grams = []
        self.grades = []
        self.weights_and_integer_excess = []
        self.probabilities = []
        self.sums = {}

    def index(self, g):
        if g in self.ids:
            return self.ids[g]
        i = len(self.grams)
        self.ids[g] = i
        self.grams.append(g)
        w, raw = _normalized_moments(g)
        v0, v1 = (_scores(raw, c) for c in (0, 1))
        e0, e1 = (v - F(w, 28) for v in (v0, v1))
        assert all((e * COST_UNITS).denominator == 1 for e in (e0, e1))
        self.grades.append({"weight": w, "wI0": str(v0), "wI1": str(v1), "excess0": str(e0), "excess1": str(e1)})
        self.weights_and_integer_excess.append((w, int(e0 * COST_UNITS), int(e1 * COST_UNITS)))
        self.probabilities.append([[str(p / w) for p in line] for line in raw] if w else None)
        return i

    def rank_one(self, a):
        return self.index(tuple(tuple(x * y for y in a) for x in a))

    def pooled(self, ids):
        key = tuple(sorted(Counter(ids).items()))
        if key not in self.sums:
            cols = [(self.grams[i], n) for i, n in key]
            g = tuple(tuple(sum(n * m[a][b] for m, n in cols) for b in FOCAL_WORDS) for a in FOCAL_WORDS)
            self.sums[key] = self.index(g)
        return self.sums[key]


def _literal_input(law, old_mixed, old_z):
    named = ((0, 1, 2, 3), (0, 4, 5, 6), (1, 7, 8, 9), (2, 10, 11, 12), (3, 13, 14, 15))
    for case, rows in ((old_mixed, "ordinary_reached_rows"), (old_z["ordinary"], "reached")):
        assert _matrix(case[rows]) == named
    assert old_mixed["status"] == old_z["status"] == "funded_and_admitted"
    for i, event in enumerate(old_z["ordinary"]["births"]):
        paid, *fresh = named[i + 1]
        assert event["paid_names"] == [paid] and event["fresh_names"] == fresh and event["fresh_grant"] == 3
        assert old_z["ordinary"]["owners"][str(paid)] == [0, i + 1]
        assert all(old_z["ordinary"]["owners"][str(n)] == [i + 1] for n in fresh)
    masks = tuple(sum(1 << n for n in names) for names in named)
    if law == "parity":
        words = [w for w in range(1 << 16) if not any((w & q).bit_count() & 1 for q in masks)]
    else:
        words = [w for w in range(1 << 16) if all(0 < w & q < q for q in masks)]
    assert words == old_z["literal_complete_words_lsb_name_zero"]
    assert len(words) == old_mixed["verified_physical_words"] == old_mixed["N"] == old_z["N"]
    for names, retained in zip(named, old_z["reached_full_projections"], strict=True):
        allowed = sorted({_bin(w, names) for w in words})
        assert allowed == retained["allowed_projected_word_indices"]
        assert 0 < len(allowed) < 16 and all(retained[key] for key in ("K1", "K2", "K3", "canonical_check"))
        assert all(len({w & ~(1 << i) for w in allowed}) == 8 for i in range(4))
    regions = [[0] * 16 for _ in K]
    for raw in words:
        old, focal, loose = (_bin(raw, region) for region in (P, X, R))
        bit = 1 << focal
        assert not bit & regions[loose][old]
        regions[loose][old] |= bit
    return named, words, regions


@cache
def _indices(mask):
    return tuple(x for x in FOCAL_WORDS if mask >> x & 1)


def _vector_at_z(regions, h, r):
    a = [0] * 8
    for s, focal in enumerate(regions[r]):
        eps = _sign(h & s)
        for x in _indices(focal):
            a[x] += eps
    return tuple(a)


def _joined_views(regions, old_axes, tables):
    by_z, by_change = [], []
    vectors_z, vectors_change = [], []
    for h in H:
        z = tuple(_vector_at_z(regions, h, r) for r in K)
        # With name 15 changed, adjacent ordinary records are the two actual t values.
        changed = tuple(tuple(a + _sign(k & 1) * b for a, b in zip(z[k & ~1], z[k | 1], strict=True)) for k in K)
        vectors_z.append(z)
        vectors_change.append(changed)
        by_z.append(tuple(tables.rank_one(a) for a in z))
        by_change.append(tuple(tables.rank_one(a) for a in changed))
    for basis, outcome, amplitudes in (("nine_z", by_z, vectors_z), ("mixed", by_change, vectors_change)):
        previous = old_axes[basis]
        prior_ids, prior_probs = previous["root"]["gram_library"], previous["root"]["probability_library"]
        mapping = {}
        for h, ids in enumerate(outcome):
            for k, ident in enumerate(ids):
                old_id = previous["law"]["rows"][k]["character_grams"][h]
                if old_id not in mapping:
                    assert _matrix(prior_ids[old_id]) == tables.grams[ident]
                    assert prior_probs[old_id] == tables.probabilities[ident]
                    mapping[old_id] = ident
                assert mapping[old_id] == ident
                # Complement every ordinary bit. Fixed X signs keep their names in both views.
                q = k ^ (510 if basis == "mixed" else 511)
                phase = _sign(h) * (_sign(k & 1) if basis == "mixed" else 1)
                assert all(amplitudes[h][q][x ^ 7] == phase * amplitudes[h][k][x] for x in FOCAL_WORDS)
    return {"nine_z": by_z, "mixed": by_change}, {"nine_z": vectors_z, "mixed": vectors_change}


def _placement_checks(named, regions, amplitudes, archive):
    declared = {frozenset(row) for row in named}
    verified = {}
    for j in R:
        row = archive["physical_placements"][str(j)]
        image = row["name_image_by_old_name"]
        assert set(image) == set(range(16)) and image[15] == j
        assert {frozenset(image[n] for n in holder) for holder in named} == declared
        assert tuple(image[n] for n in X) == X
        owners = {n: holder[0] for holder in named[2:] for n in holder[1:]}
        assert image[owners[15]] == owners[j]
        ordinary = tuple(n for n in R if n != j)
        assert tuple(row["eight_ordinary_names"]) == ordinary and row["X_label_image"] == [0, 1]
        inverse = {v: n for n, v in enumerate(image)}
        def map_index(v, names, dest):
            word = sum((v >> (len(names) - 1 - i) & 1) << image[n] for i, n in enumerate(names))
            return _bin(word, dest)

        perm_s = tuple(map_index(s, P, P) for s in H)
        perm_r = tuple(map_index(r, R, R) for r in K)
        perm_k = tuple(2 * map_index(k >> 1, R[:-1], ordinary) + (k & 1) for k in K)
        assert list(perm_s) == row["spent_word_and_character_image_by_old_index"]
        assert tuple(R[:-1].index(inverse[n]) for n in ordinary) == tuple(row["ordinary_bit_image_sequence"])
        assert all(_sign(h & s) == _sign(perm_s[h] & perm_s[s]) for h in H for s in H)
        for r, after in enumerate(perm_r):
            assert all(regions[r][s] == regions[after][perm_s[s]] for s in H)
            # A transported mixed (u,b) refers to both distinct physical completions with unchanged t and b.
            assert perm_k[r] >> 1 == _bin(sum((after >> (8 - i) & 1) << n for i, n in enumerate(R)), ordinary)
            assert after >> (15 - j) & 1 == r & 1
        if j == R[0]:
            for h in H:
                z = tuple(_vector_at_z(regions, perm_s[h], r) for r in K)
                for k in K:
                    assert z[perm_r[k]] == amplitudes["nine_z"][h][k]
                    pair = (z[perm_r[k & ~1]], z[perm_r[k | 1]])
                    combined = tuple(a + _sign(k & 1) * b for a, b in zip(*pair, strict=True))
                    assert combined == amplitudes["mixed"][h][k]
        verified[str(j)] = {
            "physical_changed_name": j, "ordinary_sibling_names": ordinary,
            "physical_name_image": image, "paid_character_image": perm_s, "mixed_record_image": perm_k,
            "nine_z_record_image": perm_r, "completions_and_all_character_phases_verified": True,
            "signed_vector_recomputed_at_destination": j == R[0],
        }
    return verified


def _fractional(positive, deficits, credit):
    # Derive the dual breakpoint from entire ratio classes before constructing a witness.
    classes = defaultdict(list)
    for label, weight, cost in deficits:
        classes[F(weight, cost)].append((label, weight, cost))
    shadow = F(0)
    known_deficit = 0
    for ratio in sorted(classes, reverse=True):
        take_all_deficit = sum(cost for _label, _weight, cost in classes[ratio])
        if known_deficit + take_all_deficit >= credit:
            shadow = ratio
            break
        known_deficit += take_all_deficit
    mask = {lab: F(1) for lab, _weight, _d in positive}
    for ratio, rows in classes.items():
        if ratio > shadow:
            mask.update((label, F(1)) for label, _weight, _cost in rows)
    left = F(credit - known_deficit)
    for label, _weight, cost in classes.get(shadow, ()):
        if not left:
            break
        part = min(F(1), left / cost)
        mask[label] = part
        left -= part * cost
    upper = sum(w + shadow * d for _label, w, d in positive) + sum(
        max(0, w - shadow * cost) for _label, w, cost in deficits)
    chosen = sum(w for _label, w, _d in positive) + sum(mask.get(label, 0) * w for label, w, _cost in deficits)
    assert upper == chosen
    assert sum(mask.get(label, 0) * cost for label, _w, cost in deficits) <= credit
    return mask, upper, {"dual_multiplier": str(shadow * COST_UNITS), "equality_upper_raw_trace": str(upper),
                         "tied_deficit_ratio_labels": len(classes.get(shadow, ()))}


def _update_minimum_deficit(previous, stride, cost, copies, budget):
    """Minimum cost at each exact extra weight via a bounded residue recurrence."""
    cap = len(previous) - 1
    unknown = budget + 1
    next_min = [unknown] * (cap + 1)
    use = array("H", [0]) * (cap + 1)
    for residue in range(min(stride, cap + 1)):
        candidates = deque()
        for j, i in enumerate(range(residue, cap + 1, stride)):
            if previous[i] <= budget:
                shifted = previous[i] - j * cost
                # For a tie, use fewer copies of this numerical type.
                while candidates and candidates[-1][1] >= shifted:
                    candidates.pop()
                candidates.append((j, shifted))
            while candidates and candidates[0][0] < j - copies:
                candidates.popleft()
            if candidates:
                last, shifted = candidates[0]
                new_cost = shifted + j * cost
                if new_cost <= budget:
                    next_min[i] = new_cost
                    use[i] = j - last
    return next_min, use


def _integral(positive, deficits, credit, fractional_upper):
    # The recurrence prices exact extra weight rather than tabulating value by deficit.
    # A proved continuous upper and divisibility are safe bounds on this weight index.
    mandatory = sum(w for _label, w, _d in positive)
    price_groups = defaultdict(list)
    for label, w, cost in deficits:
        if cost <= credit:
            price_groups[(w, cost)].append(label)
    unit = gcd(*(w for w, _cost in price_groups)) or 1
    cap = int((fractional_upper - mandatory) // unit) if price_groups else 0
    before = [0] + [credit + 1] * cap
    stages = []
    for (w, cost), labels in sorted(price_groups.items()):
        assert labels == sorted(labels)
        stride = w // unit
        before, use = _update_minimum_deficit(before, stride, cost, len(labels), credit)
        stages.append((stride, cost, labels, use))
    optimum = max(i for i, cost in enumerate(before) if cost <= credit)
    chosen = {lab: F(1) for lab, _w, _d in positive}
    current = optimum
    additional_price = 0
    for stride, cost, labels, use in reversed(stages):
        count = use[current]
        chosen.update((lab, F(1)) for lab in labels[:count])
        current -= count * stride
        additional_price += cost * count
    assert current == 0 and before[optimum] == additional_price
    final = mandatory + optimum * unit
    dig = sha256(json.dumps(before, separators=(",", ":")).encode()).hexdigest()
    return chosen, final, {
        "method": "minimum total deficit by exact additional weight, grouping identical integer priced records",
        "positive_record_weight": mandatory, "max_extra_weight_units_from_fractional_bound": cap, "weight_unit": unit,
        "total_deficit_budget_in_1_over_56": credit, "actual_chosen_deficit_in_1_over_56": additional_price,
        "eligible_types_trace_cost_and_count": [(w, cost, len(labels)) for (w, cost), labels in sorted(price_groups.items())],
        "unreachable_weight_sentinel": credit + 1, "reachable_extra_weight_states": sum(cost <= credit for cost in before),
        "exact_terminal_minimum_deficit_digest": dig, "equality_upper_raw_trace": str(final),
    }


def _solve(table_axes, c, denominator, tables):
    priced_rows = {}
    total = 0
    for h, grades in table_axes:
        for k, ident in enumerate(grades):
            row = tables.weights_and_integer_excess[ident]
            trace, d = row[0], row[c + 1]
            if trace:
                priced_rows[h * 512 + k] = (trace, d)
            else:
                assert d == 0
            total += trace
    nonnegative = [(lab, w, d) for lab, (w, d) in priced_rows.items() if d >= 0]
    negative = [(lab, w, -d) for lab, (w, d) in priced_rows.items() if d < 0]
    credit = sum(d for _lab, _w, d in nonnegative)
    random_mask, random_bound, random_cert = _fractional(nonnegative, negative, credit)
    int_mask, int_bound, int_cert = _integral(nonnegative, negative, credit, random_bound)
    assert int_bound <= random_bound
    results = {}
    for label, mask, upper, cert in (("deterministic", int_mask, int_bound, int_cert),
                                      ("randomized", random_mask, random_bound, random_cert)):
        reach = sum(a * priced_rows[lab][0] for lab, a in mask.items())
        slack = sum(a * priced_rows[lab][1] for lab, a in mask.items()) / F(COST_UNITS)
        assert reach == upper and slack >= 0 and all(0 < f <= 1 for f in mask.values())
        score = slack + F(reach, 28)
        results[label] = {
            "raw_weight": str(reach), "per_launch_rate": str(F(reach, denominator)),
            "raw_weighted_score": str(score), "raw_surplus": str(slack),
            "I": str(score / reach) if reach else None, "decline_mass": str(F(total - reach, denominator)),
            "accepted_label_index_and_probability": [(lab, str(mask[lab])) for lab in sorted(mask)],
            "certificate": cert,
        }
    return results


def _transport_mask(mask, image):
    return sum(1 << (3 - image[j]) for j in range(4) if mask & (1 << (3 - j)))


def _subsets(full_ids, den, tables, placements):
    panels = {}
    for mask in H:
        available = [p for p in H if p & mask == p]
        subgroup = {p: tuple(h for h in H if h & mask == p) for p in available}
        assert all(len(group) == 1 << (4 - mask.bit_count()) for group in subgroup.values())
        by_seen = [(p, tuple(tables.pooled(full_ids[h][k] for h in hs) for k in K))
                   for p, hs in subgroup.items()]
        reachable = sum(bool(tables.weights_and_integer_excess[idx][0]) for _p, ids in by_seen for idx in ids)
        assert sum(tables.weights_and_integer_excess[idx][0] for _p, ids in by_seen for idx in ids) == den
        priced = {str(c): _solve(by_seen, c, den, tables) for c in (0, 1)}
        panels[str(mask)] = {"named_paid_subset": [n for n in P if mask & (1 << (3 - n))],
                             "seen_h_in_full_bit_positions": available,
                             "available_record_gram_ids": [ids for _p, ids in by_seen],
                             "reachable_records": reachable, "zero_records": len(by_seen) * 512 - reachable,
                             **priced}
    essential = {}
    for c in ("0", "1"):
        results = {}
        for klass in CLASSES:
            value = [F(panels[str(m)][c][klass]["raw_weight"]) for m in H]
            for a, b in product(H, repeat=2):
                if a & b == a:
                    assert value[a] <= value[b]
            full = [m for m in H if value[m] == value[15]]
            least = [m for m in full if not any(j != m and j & m == j for j in full)]
            assert least
            for host in placements.values():
                # These coordinate masks describe where the *same physically transported rule* reads.
                transported = [(_transport_mask(m, host["physical_name_image"]), m.bit_count()) for m in least]
                assert all(t.bit_count() == n for t, n in transported)
            results[klass] = {
                "all_sufficient_subset_masks": full, "inclusion_minimal_masks": least,
                "minimum_number_of_named_coordinates": min(m.bit_count() for m in least),
                "vacuous_on_zero_full_optimum": not bool(value[15]),
                "inclusion_minimal_masks_by_transported_changed_name": {
                    j: sorted(_transport_mask(m, host["physical_name_image"]) for m in least)
                    for j, host in placements.items()},
            }
        essential[c] = results
    return panels, essential


def _stricter(full_ids, den, tables, panels):
    result = {}
    for c in ("0", "1"):
        attempts = [_solve(((h, ids),), int(c), den, tables) for h, ids in enumerate(full_ids)]
        result[c] = {}
        for klass in CLASSES:
            view = [attempt[klass] for attempt in attempts]
            total = sum(F(item["raw_weight"]) for item in view)
            assert total <= F(panels["15"][c][klass]["raw_weight"])
            result[c][klass] = {"raw_weight": str(total), "per_launch_rate": str(total / den), "by_h": view}
    return result


def _same_matrix_up_to_scale(a, b, scale):
    return all(x == y * scale for row, other in zip(a, b, strict=True) for x, y in zip(row, other, strict=True))


def _parity_structure(regions, axes, amplitudes, tables):
    paid_word_by_r = []
    for r in K:
        (s,) = tuple(s for s, choices in enumerate(regions[r]) if choices)
        assert _indices(regions[r][s]) == tuple(x for x in FOCAL_WORDS if (x.bit_count() & 1) == (s >> 3))
        paid_word_by_r.append(s)
    grades_by_basis = {basis: set() for basis in axes}
    for h in H:
        for k in K:
            s0, s1 = (paid_word_by_r[r] for r in (k & ~1, k | 1))
            assert s1 == s0 ^ 9  # The focal payer and the payer of name 15.
            sign = (k & 1) ^ ((h & 9).bit_count() % 2)
            expected_x_product = tuple(_sign(h & s0) * _sign(sign * ((x.bit_count() & 1) ^ (s0 >> 3))) for x in FOCAL_WORDS)
            assert amplitudes["mixed"][h][k] == expected_x_product
            for basis in axes:
                g = tables.grades[axes[basis][h][k]]
                w = g["weight"]
                grade = tuple(F(g[f"wI{c}"]) / w for c in (0, 1))
                grades_by_basis[basis].add(grade)
    assert grades_by_basis["mixed"] == {(F(-1, 8),) * 2, (F(-11, 8),) * 2}
    assert grades_by_basis["nine_z"] == {(F(-7, 8), F(-5, 8)), (F(-5, 8), F(-7, 8))}
    return {
        "nine_Z_each_ordinary_sibling_record_determines_one_spent_word": True,
        "mixed_completion_changes_paid_names": (0, 3),
        "mixed_product_X_answer_bit_at_each_focal_name": "b XOR h_at_paid_0 XOR h_at_paid_3",
        "possible_fixed_score_pairs": {basis: [[str(r) for r in p] for p in sorted(options)]
                                       for basis, options in grades_by_basis.items()},
        "every_positive_joint_record_has_negative_score": True,
    }


def _zero_access_anchors(basis, old, launch, tables, subsets):
    panel = subsets["0"]
    ids = panel["available_record_gram_ids"][0]
    for k in K:
        former_id = old["law"]["rows"][k]["retained"]["gram"]
        g = tables.grams[ids[k]]
        archived = old["root"]["gram_library"][former_id]
        assert _same_matrix_up_to_scale(g, archived, 16)
        assert tables.probabilities[ids[k]] == old["root"]["probability_library"][former_id]
    for c in ("0", "1"):
        for klass in CLASSES:
            if basis == "mixed":
                expected = old["report"]["modes"]["retained"][c]["optima_and_controls"][klass]["per_launch_rate"]
            else:
                expected = old["report"]["modes"]["retained"]["primary_and_controls_rules"][f"full/{klass}"]["per_initial_launch_rate"]
            assert F(panel[c][klass]["per_launch_rate"]) == F(expected)
            assert F(panel[c][klass]["raw_weight"]) == F(expected) * launch
    return True


def _physical_writer(law, words, ancestor):
    valid = tuple(v for v in FOCAL_WORDS if _admitted_bits(v, 3, law))
    go, decline, ready = 0b101, 0b011, 0b110
    assert all(v in valid for v in (go, decline, ready))
    assert any(w not in valid for w in FOCAL_WORDS)
    assert all(len({v & ~(1 << i) for v in valid}) == 4 for i in range(3))
    shifts = ((16, 17, 18), (19, 20, 21))
    assert all(n not in range(16) for arr in shifts for n in arr)
    example = words[0]

    def insert(value, names):
        return sum((value >> (2 - i) & 1) << n for i, n in enumerate(names))

    def offer(full, names, target):
        mask = insert(ready ^ target, names)
        assert _bin(full, names) == ready and mask.bit_count() == 2 and (full & mask).bit_count() == 1
        result = full ^ mask
        assert _bin(result, names) == target
        return result

    events = {}
    for name, start, status, connected, due, prior in (
        ("resolved_go", ready, go, True, go, "addressed_yes"),
        ("resolved_decline", ready, go, True, decline, "addressed_no"),
        ("absent_source", ready, decline, True, None, "clean_or_source_refusal"),
        ("blocked_input_wire", ready, go, True, None, None),
        ("disconnected_writer", ready, go, False, go, "disconnected_public_writer"),
        ("occupied_old_go", go, go, True, go, "busy_old_yes"),
    ):
        before = example | insert(start, shifts[0]) | insert(ready, shifts[1])
        after = offer(before, shifts[1], status)
        written = connected and start == ready and due is not None
        if written:
            after = offer(after, shifts[0], due)
        assert after & 65535 == example
        v0, v1 = tuple(_bin(after, arr) for arr in shifts)
        assert v0 in valid and v1 == status
        assert (v0 == due if written else v0 == start)
        if prior:
            old = ancestor["keeper"]["events"][prior]
            assert (old["announcement_bank"], old["status_bank"], old["fresh_write"]) == (f"{v0:03b}", f"{v1:03b}", written)
        events[name] = {"initial_word_bit_n_is_name_n": before, "final_word_bit_n_is_name_n": after,
                        "announcement_bank": f"{v0:03b}", "source_status_bank": f"{v1:03b}",
                        "fresh_write": written, "public_go_delivered": written and due == go}
    assert events["resolved_go"]["public_go_delivered"]
    assert all(not row["public_go_delivered"] for key, row in events.items() if key != "resolved_go")
    return {"genuine_disjoint_ternary_names_announcement_then_status": shifts, "allowed": [f"{v:03b}" for v in valid],
            "whole_source_and_banks_allowed_word_count": len(words) * len(valid) ** 2, "K1_K2_K3": (True, True, True),
            "bank_events": events, "actual_source_admitted_and_all_16_spent_character_outcomes_eligible": True,
            "scope": "The addressed exchanges preserve the lawful separate bank supports and source word. Resolving and delivering the input signs, offering their controlled write, and broadcasting the resulting bit are supplied."}


def _fixed_older_rule(full_ids, den, earlier, tables, law):
    old = earlier["laws"][law]["modes"]["clean"]["0"]["optima_and_controls"]["deterministic"]
    mask = tuple(F(a) for a in old["mask"])
    assert len(mask) == 512 and all(m in (0, 1) for m in mask)
    picked = tuple(k for k in K if mask[k])
    if law == "nae":
        assert picked == (0, 7)
    prior = old["priced_transcript"]["diagnostic_same_mask_all_character_ports"]
    archived_tables = earlier["table_library"]
    attempts = []
    for h, ids in enumerate(full_ids):
        item = prior[h]
        assert item["h"] == f"{h:04b}"
        go = tables.pooled(ident for k, ident in enumerate(ids) if mask[k])
        decline = tables.pooled(ident for k, ident in enumerate(ids) if not mask[k])
        both = tables.pooled(ids)
        for ident, packet in ((go, item["normal_mask_go"]), (decline, item["normal_mask_decline"]), (both, item["entire_port"])):
            prior_gram = archived_tables[packet["table"]]["raw_gram"]
            assert tables.grams[ident] == tuple(tuple(F(v) for v in row) for row in prior_gram)
            assert F(tables.grades[ident]["weight"], den) == F(packet["launch_mass"])
            assert F(tables.grades[ident]["wI0"]) == F(packet["raw_witness"])
        other = tables.pooled(ids[k ^ 510] for k in picked)
        good = tables.weights_and_integer_excess[go]
        complement = tables.weights_and_integer_excess[other]
        assert (good[0], good[1]) == (complement[0], complement[2])
        attempts.append({"h": f"{h:04b}", "go_gram": go, "decline_gram": decline, "whole_port_gram": both,
                         "c1_complemented_mask_go_gram": other, "qualifies_at_fixed_c0": bool(good[0] and good[1] >= 0),
                         "go_mass": str(F(good[0], den))})
    good = [h for h, attempt in enumerate(attempts) if attempt["qualifies_at_fixed_c0"]]
    cost = sum((F(attempts[h]["go_mass"]) for h in good), F(0))
    if law == "nae":
        assert good == [0, 2, 4, 6, 8, 10, 12, 14] and cost == F(11, 19208)
    return {"old_fixed_c0_sibling_indices": picked, "c1_passively_complemented_indices": sorted(k ^ 510 for k in picked),
            "qualifying_spent_indices": good, "qualifying_fixed_rule_exact_lower_bound": str(cost), "attempts": attempts}


def _load_archives():
    assert sha256(FREEZE.read_bytes()).hexdigest() == FREEZE_SHA256
    paths = (Path(__file__).resolve(), FREEZE)
    canonical = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}
    variants = {}
    suites = {}
    for basis, path in EARLIER.items():
        receipt_path = path / "receipt.json"
        receipt = json.loads(receipt_path.read_bytes())
        blob_path = path / receipt["artifact"]
        blob = blob_path.read_bytes()
        assert sha256(blob).hexdigest() == receipt["sha256"]
        assert len(blob) == receipt.get("bytes", receipt.get("gzip_bytes"))
        suite = json.loads(gzip.decompress(blob))
        inherited = suite[PHYSICAL_KEYS[basis]]
        for public_path, digest in inherited["public_source_variants"].items():
            assert variants.setdefault(public_path, digest) == digest
        declared = {**receipt.get("source_bindings", receipt.get("project_files")), **inherited["source_sha256"]}
        for key, digest in declared.items():
            seen = sha256((ROOT / key).read_bytes()).hexdigest()
            assert seen == digest or seen == variants.get(key), key
            assert canonical.setdefault(key, digest) == digest
        for p in (receipt_path, blob_path):
            canonical[str(p.relative_to(ROOT))] = sha256(p.read_bytes()).hexdigest()
        suites[basis] = suite
    return suites, canonical, variants


def _case(law, source, tables):
    old = {
        k: {"root": library, "law": library["laws"][law], "report": suite["laws"][law]}
        for k, suite in source.items() for library in (suite[PHYSICAL_KEYS[k]],)
    }
    mixed_old, z_old = (old[basis]["law"] for basis in ("mixed", "nine_z"))
    named, words, regions = _literal_input(law, mixed_old, z_old)
    N, W = len(words), z_old["W"]
    assert W == mixed_old["W"]
    axes, amplitudes = _joined_views(regions, old, tables)
    placements = _placement_checks(named, regions, amplitudes, mixed_old)
    for h in H:
        for u in range(256):
            z = tables.pooled(axes["nine_z"][h][2 * u:2 * u + 2])
            mixed = tables.pooled(axes["mixed"][h][2 * u:2 * u + 2])
            assert _same_matrix_up_to_scale(tables.grams[mixed], tables.grams[z], 2)
    views = {}
    for basis in ("mixed", "nine_z"):
        order = axes[basis]
        denominator = N * (32 if basis == "mixed" else 16)
        char_totals = tuple(tables.pooled(row) for row in order)
        all_outcomes = tables.pooled(char_totals)
        totals = tuple(tables.grades[i]["weight"] for i in char_totals)
        assert sum(totals) == denominator and totals[0] == W * (2 if basis == "mixed" else 1)
        assert tables.grades[all_outcomes]["weight"] == denominator
        for h in H:
            for k in K:
                k_reversed = k ^ (510 if basis == "mixed" else 511)
                a, b = (tables.weights_and_integer_excess[order[h][x]] for x in (k, k_reversed))
                assert (a[0], a[1], a[2]) == (b[0], b[2], b[1])
        panels, essential = _subsets(order, denominator, tables, placements)
        stricter = _stricter(order, denominator, tables, panels)
        for p in panels.values():
            assert all(p["0"][cl]["raw_weight"] == p["1"][cl]["raw_weight"] for cl in CLASSES)
        assert all(stricter["0"][cl]["raw_weight"] == stricter["1"][cl]["raw_weight"] for cl in CLASSES)
        zero_access = _zero_access_anchors(basis, old[basis], denominator, tables, panels)
        views[basis] = {
            "launch_denominator": denominator,
            "gram_ids": order, "grades": order,
            "true_h_pooled_gram_ids": char_totals, "total_unconditioned_gram": all_outcomes,
            "true_h_port_masses": tuple(str(F(w, denominator)) for w in totals),
            "clean_only_port_mass": str(F(totals[0], denominator)),
            "h_hidden_matches_earlier_retained_price_and_all_record_matrices": zero_access,
            "subsets": panels, "minimal_coordinate_sets": essential, "per_true_h": stricter,
        }
    fixed = _fixed_older_rule(axes["mixed"], 32 * N, source["mixed"], tables, law)
    keeper = _physical_writer(law, words, mixed_old)
    return {
        "N": N, "W": W, "source_roster": named,
        "complete_original_support_bound_and_independently_enumerated": len(words),
        "changed_name_placements": placements, "keeper": keeper, "views": views,
        "fixed_older_mask_all_attempts": fixed,
        "parity_product_or_parity_support_check": _parity_structure(regions, axes, amplitudes, tables) if law == "parity" else None,
        "zero_lawful_support_or_failed_writer_receives_no_go": True,
        "phase_and_launch_checks": {"all_full_matrices_and_tables_match_archives": True,
                                    "two_X_outcomes_sum_to_same_eight_Z_marginal_at_each_true_h": True,
                                    "both_fixed_orientations_and_actual_character_signs_transport": True},
    }


def run():
    """Return the independent raw physical and exact finite optimization receipt as JSON-ready data."""
    old, paths, variants = _load_archives()
    tables = _Tables()
    laws = {law: _case(law, old, tables) for law in LAWS}
    return {
        "laws": laws, "gram_library": tables.grams, "probability_library": tables.probabilities,
        "grade_library": tables.grades, "source_sha256": paths, "public_source_variants": variants,
        "records": {"paid_names_in_lexicographic_h_order": P, "focal_names_in_setting_and_answer_order": X,
                    "sibling_names_in_order": R, "primary_change_name": 15,
                    "full_label_index": "512 * h + k; when withholding h bits, the integer h fills those positions with zero only for indexing",
                    "basis_k": {"mixed": "2 * u + b, plus is zero", "nine_z": "the ordinary nine-bit word"},
                    "focal_settings": "X=1, Z=0; first named focal distinction most significant",
                    "focal_answers": "plus=0; first named focal distinction most significant",
                    "grade_ids_address_the_same_library_index_as_grams": True,
                    "launch_cell_weight": "normalized table entry times integer raw trace over the corresponding launch denominator",
                    "launch_cell_joint_with_settings": "multiply by 1/8 for the three independent fair choices"},
        "focal_deterministic_limit": _deterministic_limit(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    obj = run()
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    if args.smoke:
        for law, program in obj["laws"].items():
            for basis, case in program["views"].items():
                pooled = case["subsets"]["15"]["0"]
                strict = case["per_true_h"]["0"]
                print(law, basis, *(pooled[cl]["per_launch_rate"] for cl in CLASSES), *(strict[cl]["per_launch_rate"] for cl in CLASSES))
        print(sha256(raw.encode()).hexdigest())
    else:
        print(raw)


if __name__ == "__main__":
    main()
