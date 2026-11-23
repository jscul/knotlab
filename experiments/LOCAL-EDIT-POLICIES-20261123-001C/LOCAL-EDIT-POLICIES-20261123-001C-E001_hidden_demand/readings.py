"""Exact all-trial readings from prepared integer counts; no simulated trials."""

from collections import Counter
from fractions import Fraction
from itertools import product
import json

from kernels import ARTIFACTS, BITS, PAIRS, WORDS, hidden, power, correspondence


def total_variation(first, second):
    keys = first.keys() | second.keys()
    return sum(abs(first[k] - second[k]) for k in keys) / 2


def numerator_table(kernels, x, y, weights, commuting=False):
    result = Counter()
    for (u, v), weight in zip(PAIRS, weights, strict=True):
        table = kernels["00" if commuting else f"{u}{v}"]
        funded = u == x and v == y
        for a, row in zip(WORDS, table, strict=True):
            for b, count in zip(WORDS, row, strict=True):
                result[a[0] * funded, b[0] * funded] += weight * count
    return [result[outcome] for outcome in PAIRS]


def fixed_tables(data, weights=(1, 1, 1, 1), commuting=False):
    denom = sum(weights) * data["source_total_each"]
    cells, correlations = {}, []
    for x, y in PAIRS:
        counts = numerator_table(data["pair_kernels"]["terminal_terminal"], x, y, weights, commuting)
        assert sum(counts) == denom
        e = Fraction(counts[0] + counts[3] - counts[1] - counts[2], denom)
        correlations.append(e)
        cells[f"{x}{y}"] = dict(counts=counts, denominator=denom, correlation=str(e),
                                  probabilities=[str(Fraction(c, denom)) for c in counts])
    sign_scores = [sum(s * e for s, e in zip(signs, correlations, strict=True))
                   for signs in product((-1, 1), repeat=4) if signs.count(-1) % 2]
    return dict(cells=cells, signed_CHSH=str(sum(correlations[:3]) - correlations[3]),
                max_CHSH=str(max(sign_scores)))


def edit(policy, old_word, hidden_label):
    if policy == "mark":
        return old_word[0]
    if policy == "opposite_mark":
        return 1 - old_word[0]
    if policy == "repair_revealed":
        return hidden_label
    if policy == "miss_revealed":
        return 1 - hidden_label
    return policy  # 0 or 1 names an address; None withholds the spare.


def receiver_law(data, side, receiver_edit, sender_policy, receiver_cut, sender_cut,
                 weights=(1, 1, 1, 1), commuting=False):
    """Read one or three old bits and the actual common gain, keeping all old states."""
    left, right = ((receiver_cut, sender_cut) if side == "Alice" else (sender_cut, receiver_cut))
    kernels = data["pair_kernels"][f"{left}_{right}"]
    totals = {k: Counter() for k in ("word_gain", "mark_gain", "mark_and_gain", "gain")}
    denominator = sum(weights) * data["source_total_each"]
    for (u, v), w in zip(PAIRS, weights, strict=True):
        table = kernels["00" if commuting else f"{u}{v}"]
        for a, row in zip(WORDS, table, strict=True):
            for b, n in zip(WORDS, row, strict=True):
                i, j, r, s = (a, b, u, v) if side == "Alice" else (b, a, v, u)
                x = edit(receiver_edit, i, r)
                y = edit(sender_policy, j, s)
                gain = int(r == x and s == y)
                mass = Fraction(n * w, denominator)
                totals["word_gain"][i, gain] += mass
                totals["mark_gain"][i[0], gain] += mass
                totals["mark_and_gain"][i[0] * gain] += mass
                totals["gain"][gain] += mass
    assert all(sum(counter.values()) == 1 for counter in totals.values())
    return totals


def policy_comparison(data, side, receiver_edit, policies, weights=(1, 1, 1, 1), commuting=False):
    denominator = sum(weights) * data["source_total_each"]
    result = {"old_assignment_denominator_for_each_policy": denominator}
    for receiver_cut in ("terminal", "guard"):
        laws = [receiver_law(data, side, receiver_edit, policy, receiver_cut, "terminal", weights, commuting)
                for policy in policies]
        result[receiver_cut] = {k: str(total_variation(laws[0][k], laws[1][k])) for k in laws[0]}
        result[receiver_cut]["gain_probabilities"] = [str(d["gain"][1]) for d in laws]
        result[receiver_cut]["selected_probabilities"] = [str(d["mark_and_gain"][1]) for d in laws]
        result[receiver_cut]["old_mark_and_gain_joint"] = [
            [str(d["mark_gain"][a, f]) for a, f in PAIRS] for d in laws
        ]
        raw_counts = [[d["mark_gain"][a, f] * denominator for a, f in PAIRS] for d in laws]
        assert all(c.denominator == 1 for counts in raw_counts for c in counts)
        result[receiver_cut]["old_mark_and_gain_counts"] = [list(map(int, counts)) for counts in raw_counts]
    result["full_post_TV"] = result["guard"]["word_gain"]
    return result


def all_scenarios(data):
    scenarios = {
        "fixed_sender_addresses": ((0, 1), (1, 1, 1, 1), False),
        "sender_old_mark_or_opposite": (("mark", "opposite_mark"), (1, 1, 1, 1), False),
        "commuting_sender_old_mark_or_opposite": (("mark", "opposite_mark"), (1, 1, 1, 1), True),
        "sender_idle_or_address0": ((None, 0), (1, 1, 1, 1), False),
        "revealed_sender_repair_or_miss": (("repair_revealed", "miss_revealed"), (1, 1, 1, 1), False),
        "biased_Bob_type_fixed_sender_addresses": ((0, 1), (1, 3, 1, 3), False),
    }
    report = {}
    for name, (policies, weights, commuting) in scenarios.items():
        report[name] = {
            side: {f"fixed_{x}": policy_comparison(data, side, x, policies, weights, commuting)
                   for x in BITS} for side in ("Alice", "Bob")
        }
    report["revealed_both_repair_receiver"] = {
        side: policy_comparison(data, side, "repair_revealed", ("repair_revealed", "miss_revealed"))
        for side in ("Alice", "Bob")
    }
    return report


def joint_boundary_check(law, data):
    """Check the factor for every full past atom and every possible newly visible H state.

    Once a local old assignment is specified, its unsummed hidden multiplicity
    is exactly H(c), where c is its two W-H bits. All other outside factors depend
    only on z. On funded cuts the actual local edit identifies the active H.
    """
    one = data["one_piece"]
    weights = data["local_weights_at_terminal"]
    forward = data["pair_kernels"]["guard_guard"]
    backward = {k: list(zip(*v, strict=True)) for k, v in forward.items()}
    summaries = {}
    for side, matrices in (("Alice", forward), ("Bob", backward)):
        scores = {}
        for own in BITS:
            # Divide out the complete local term, leaving the integer outside
            # factor common to every assignment with these three outer bits.
            outside = {}
            for r, s in PAIRS:
                type_key = f"{r}{s}" if side == "Alice" else f"{s}{r}"
                outside[r, s] = []
                for z, row in enumerate(matrices[type_key]):
                    q, rem = divmod(sum(row), data["local_weights_at_guard"][z])
                    assert rem == 0
                    outside[r, s].append(q)
            assert len({tuple(col) for col in outside.values()}) == 1
            states_examined = 0
            for z in range(len(WORDS)):
                for c in PAIRS:
                    trials = []
                    for far in BITS:
                        atoms = Counter()
                        for r, s in PAIRS:
                            rest = outside[r, s][z]
                            for middle, openings in hidden(law, r, c):
                                if r == own and s == far:
                                    atoms[True, middle, openings] += rest
                                else:
                                    atoms[False] += rest
                        trials.append(atoms)
                    assert trials[0] == trials[1]
                    states_examined += len(trials[0])
            scores[f"own_{own}"] = states_examined
        summaries[side] = scores
    # Direct 7-segment contraction of the tail, independent of the two-cut cancellation check.
    tail = power(one, 7)
    for zindex, z in enumerate(WORDS):
        right_mass = sum(w * correspondence(tail, z, b) for w, b in zip(weights, WORDS, strict=True))
        assert right_mass * data["local_weights_at_guard"][zindex] == sum(forward["00"][zindex])
    return summaries


def replay_physical(law, data, reports, physical):
    """Score actual gained marks from the independent ordinary implementation."""
    checks = 0
    for mode in ("primary", "commuting"):
        records = physical["modes"][mode]
        sums = {f"{x}{y}": Counter() for x, y in PAIRS}
        for type_key, record in records.items():
            source = record["laws"][law]
            old = source["old_counts"]
            expected_type = type_key if mode == "primary" else "00"
            matrix = data["pair_kernels"]["terminal_terminal"][expected_type]
            assert matrix == old["terminal_counts"]
            assert data["source_total_each"] == old["old_assignments"]
            for name, counts in sums.items():
                trial = source["trials"][name]
                actual = [len(trial["mark_holders"][side]) - 1 for side in "AB"]
                for a, row in zip(WORDS, matrix, strict=True):
                    for b, n in zip(WORDS, row, strict=True):
                        counts[a[0] * actual[0], b[0] * actual[1]] += n
                checks += 1
        expected = reports["fixed" if mode == "primary" else "commuting"]["cells"]
        for key, counts in sums.items():
            assert [counts[ab] for ab in PAIRS] == expected[key]["counts"]
    for side in ("Alice", "Bob"):
        for address in BITS:
            for message in BITS:
                joint = Counter()
                for source in physical["modes"]["primary"].values():
                    item = source["laws"][law]
                    for a, row in zip(WORDS, item["old_counts"]["terminal_counts"], strict=True):
                        for b, n in zip(WORDS, row, strict=True):
                            if side == "Alice":
                                key, mark, end = f"{address}{b[0] ^ message}", a[0], "A"
                            else:
                                key, mark, end = f"{a[0] ^ message}{address}", b[0], "B"
                            gained = len(item["trials"][key]["mark_holders"][end]) - 1
                            joint[mark, gained] += n
                actual = [str(Fraction(joint[ab], 4 * data["source_total_each"])) for ab in PAIRS]
                agreed = reports["policies"]["sender_old_mark_or_opposite"][side][f"fixed_{address}"]
                assert actual == agreed["terminal"]["old_mark_and_gain_joint"][message]
    return dict(fixed_type_context_checks=checks, real_mark_policy_comparisons=8)


def main():
    kernels = json.loads((ARTIFACTS / "kernels.json").read_text())["laws"]
    physical = json.loads((ARTIFACTS / "physical.json").read_text())
    report = {
        "unit": "Uniform old assignment within one of four equally likely preparations unless explicitly reweighted.",
        "old_mark_and_gain_joint_order": ["old0 gain0", "old0 gain1", "old1 gain0", "old1 gain1"],
        "record": "Full record TV is exactly the outer guard triple with the gain in the fixed-receiver comparisons. If own type is revealed to the deciding receiver, it still attains the same displayed extremes zero or one in its repair/miss comparison.",
        "laws": {},
    }
    for law, data in kernels.items():
        report["laws"][law] = dict(
            fixed=fixed_tables(data),
            commuting=fixed_tables(data, commuting=True),
            biased=fixed_tables(data, (1, 3, 1, 3)),
            fixed_type={f"{u}{v}": fixed_tables(data, tuple(int((u, v) == k) for k in PAIRS))
                        for u, v in PAIRS},
            policies=all_scenarios(data),
            full_local_trajectory_check=joint_boundary_check(law, data),
        )
        report["laws"][law]["literal_replay"] = replay_physical(law, data, report["laws"][law], physical)
    (ARTIFACTS / "readings.json").write_text(json.dumps(report, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
