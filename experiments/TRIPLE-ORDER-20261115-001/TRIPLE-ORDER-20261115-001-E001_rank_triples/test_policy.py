"""Synthetic, independent checks for the public-table ordering policy."""

from itertools import combinations
import json
import random

import policy


def planted_example(n, group, byte, rng):
    outside = tuple(i for i in range(n) if i not in group)
    blocks = tuple(tuple(rng.getrandbits(1 << len(outside)) for _ in range(2)) for _ in range(2))
    outputs = [0, 0]
    for row in range(1 << n):
        local = sum(((row >> axis) & 1) << j for j, axis in enumerate(group))
        z = sum(((row >> axis) & 1) << j for j, axis in enumerate(outside))
        h = (byte >> local) & 1
        for o in range(2):
            outputs[o] |= ((blocks[o][h] >> z) & 1) << row
    return tuple(outputs)


def true_grade(n, outputs):
    common = tuple(i for i in range(n) if all(
        any(((t >> r) ^ (t >> (r ^ (1 << i)))) & 1 for r in range(1 << n)) for t in outputs))
    eligible = tuple(combinations(common, 3))
    widths = []
    for group in eligible:
        outside = [i for i in range(n) if i not in group]
        values = set()
        for local in range(8):
            offset = sum(((local >> j) & 1) << axis for j, axis in enumerate(group))
            rows = [offset | sum(((c >> j) & 1) << axis for j, axis in enumerate(outside))
                    for c in range(1 << len(outside))]
            values.add(tuple(tuple((t >> r) & 1 for r in rows) for t in outputs))
        widths.append((len(values) - 1).bit_length())
    if not widths:
        return eligible, {"width": None, "minimizers": []}
    return eligible, {"width": min(widths), "minimizers": [g for g, w in zip(eligible, widths) if w == min(widths)]}


def relabel(outputs, mapping):
    renamed = [0, 0]
    for row in range(1 << len(mapping)):
        new_row = sum(((row >> i) & 1) << axis for i, axis in enumerate(mapping))
        for j, t in enumerate(outputs):
            renamed[j] |= ((t >> row) & 1) << new_row
    return tuple(renamed)


def check():
    rng = random.Random(530114)
    rows, grades, geometry = [], {}, {}
    for i in range(12):
        n = 7
        group = tuple(sorted(rng.sample(range(1, n), 3)))
        # Majority and odd parity provide independent local operations.
        byte = 0xE8 if i % 2 == 0 else 0x96
        tables = planted_example(n, group, byte, rng)
        eligible, grade = true_grade(n, tables)
        assert grade["width"] == 1 and group in grade["minimizers"]
        for mode in policy.CHANNELS:
            ranker = policy.Ranker(n, policy._model(mode, 4))
            context = ranker._features(tables, tuple(range(n)))
            assert any(set(group) <= {axis for axis, _ in bucket} for bucket in context.buckets)
        rows.append({"id": str(i), "n": n, "outputs": tables})
        grades[str(i)], geometry[str(i)] = grade, eligible

    for i in range(3):
        n = 6
        pair = (rng.getrandbits(1 << n), rng.getrandbits(1 << n))
        eligible, grade = true_grade(n, pair)
        key = f"u{i}"
        rows.append({"id": key, "n": n, "outputs": pair})
        grades[key], geometry[key] = grade, eligible

    model, receipt = policy.fit(rows, grades)
    assert model["channel"] != "lexical" and receipt["fit_score"]["objective_units"] > 0
    assert policy.fit(reversed(rows), grades)[0] == model
    assert json.loads(json.dumps(model)) == model
    assert policy.model_hash(model) == receipt["model_sha256"]
    assert policy.fit([], {})[0] == policy.zero_model()
    assert policy.fit(rows[-3:], {r["id"]: grades[r["id"]] for r in rows[-3:]})[0] == policy.zero_model()

    # Check the fit objective against end-to-end deployment ordering. Every
    # tied true minimizer is eligible to terminate this rank calculation.
    savings = units = unique_relabelings = 0
    for row in rows:
        n, x, key = row["n"], row["outputs"], row["id"]
        eligible, grade = geometry[key], grades[key]
        eng = policy.Ranker(n, model)
        order = eng.full_ranking(x, eligible)
        assert len(set(order)) == len(eligible) and set(order) == set(eligible)
        units += eng.work_counters()["estimated_feature_units"]
        if grade["width"] == 1:
            good = set(grade["minimizers"])
            savings += next(i for i, g in enumerate(eligible) if g in good)
            savings -= next(i for i, g in enumerate(order) if g in good)
        for variant in (policy.fixed_model(), policy._model("transitions", 4, ((1, 1, 1), (1, 1, 2)))):
            ranker = policy.Ranker(n, variant)
            sub = eligible[::2]
            full_order = ranker.full_ranking(x, eligible)
            assert full_order == ranker.full_ranking(x[::-1], eligible)
            mask = (1 << (1 << n)) - 1
            assert full_order == ranker.full_ranking((x[0] ^ mask, x[1]), eligible)
            part = ranker.full_ranking(x, sub)
            assert sorted(part) == list(sub)
            if set(sub) != set(eligible):
                context = ranker._features(x, ranker._layout(eligible).axes)
                full = policy.Ranker._choose(context, ranker._layout(eligible), eligible, ranker.shapes)[0]
                brute = policy.Ranker._choose(context, policy._Layout(ranker._layout(eligible).axes, False),
                                             eligible, ranker.shapes)[0]
                assert full == brute
            assert ranker.full_ranking(x, ()) == []
        fixed = policy.Ranker(n, policy.fixed_model())
        buckets = fixed._features(x, fixed._layout(eligible).axes).buckets
        if len([b for b in buckets if len(b) == 3]) == 1:
            winner = next(fixed.order(x, eligible))
            mapping = tuple(reversed(range(n)))
            renamed = relabel(x, mapping)
            new_eligible = tuple(sorted(tuple(sorted(mapping[i] for i in g)) for g in eligible))
            assert next(fixed.order(renamed, new_eligible)) == tuple(sorted(mapping[i] for i in winner))
            unique_relabelings += 1
    assert unique_relabelings > 0
    assert receipt["fit_score"]["objective_units"] == policy.PROBE_UNITS * savings - units
    assert receipt["minimum_triple_labels"] == sum(len(grade["minimizers"]) for grade in grades.values())
    return len(rows)


if __name__ == "__main__":
    print(f"Passed synthetic order, symmetry, label, fallback and objective checks on {check()} table pairs.")
