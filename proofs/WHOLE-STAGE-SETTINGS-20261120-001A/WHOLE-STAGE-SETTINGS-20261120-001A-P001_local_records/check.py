"""Exact finite tests of the probability statements in proof.md, independent of the growth code."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B = (0, 1)
CELLS = tuple(product(B, repeat=2))


def tv(left, right):
    """Total variation between two positive finite measures after normalization."""
    a, b = sum(left.values()), sum(right.values())
    return sum(abs(Fraction(left[k], a) - Fraction(right[k], b)) for k in left.keys() | right.keys()) / 2


def push(distribution, read):
    marginal = Counter()
    for event, mass in distribution.items():
        marginal[read(event)] += mass
    return marginal


def test_visibility():
    cases = ordered = concealed = 0
    for weights in [(1, 1, 1, 1), (1, 2, 4, 8)]:
        total = sum(weights)
        for flags0 in product(B, repeat=4):
            for flags1 in product(B, repeat=4):
                records = [Counter(), Counter()]
                up, down = Counter(), Counter()
                for i, (a, b, w) in enumerate(zip(flags0, flags1, weights)):
                    info = i % 2
                    records[0][info, a] += w
                    records[1][info, b] += w
                    up[info] += w * (a > b)
                    down[info] += w * (b > a)
                pivot = Fraction(sum(up.values()) + sum(down.values()), total)
                hidden = Fraction(2 * sum(min(up[i], down[i]) for i in B), total)
                direct = tv(*records)
                assert direct == pivot - hidden
                if hidden == 0:
                    assert direct == pivot
                    ordered += 1
                if direct == 0 and pivot:
                    concealed += 1
                cases += 1
    assert concealed > 0
    return dict(comparisons=cases, locally_ordered=ordered,
                zero_visible_TV_despite_pivotal_mass=concealed)


def test_policy_optimum():
    # Four pairs of labels, with a correlated, nonuniform common source.
    joint = {(0, 0): 2, (0, 1): 1, (1, 0): 3, (1, 1): 8}
    total = sum(joint.values())
    profiles = tuple(product(B, repeat=2))
    cases = 0
    for f, g0, g1 in product(profiles, repeat=3):
        readiness = (g0, g1)
        fund = lambda rule: sum(w * f[u] * readiness[rule[v]][v] for (u, v), w in joint.items())
        best = tuple(int(g1[v] > g0[v]) for v in B)
        worst = tuple(int(g1[v] < g0[v]) for v in B)
        masses = [fund(rule) for rule in profiles]
        pivot = sum(w for (u, v), w in joint.items() if f[u] and g0[v] != g1[v])
        assert fund(best) - fund(worst) == max(masses) - min(masses) == pivot
        assert tv(Counter({1: fund(best), 0: total - fund(best)}),
                  Counter({1: fund(worst), 0: total - fund(worst)})) == Fraction(pivot, total)
        cases += 1
    responsive = 0
    for fa, gb in product(profiles, repeat=2):
        by_context = [fa[x] * gb[y] for x, y in CELLS]
        sender_can_change = any(fa) and gb[0] != gb[1]
        receiver_can_change = any(gb) and fa[0] != fa[1]
        assert (len(set(by_context)) > 1) == (sender_can_change or receiver_can_change)
        responsive += len(set(by_context)) > 1
    return dict(readiness_profiles=cases, sender_policies_per_profile=len(profiles),
                two_way_pure_profiles=16, responsive_two_way_profiles=responsive,
                source_mass=[joint[key] for key in CELLS])


def test_visible_product():
    # The class label c is part of both records. Each party has four local input values.
    local = range(4)
    classes = ((2, ((1, 0, 0, 0), (0, 0, 1, 0)), ((1, 1, 1, 0), (0, 1, 1, 1))),
               (3, ((1, 1, 0, 0), (0, 1, 0, 1)), ((0, 1, 0, 1), (1, 0, 1, 0))),
               (1, ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (1, 1, 1, 0))))
    observations = {cell: Counter() for cell in CELLS}
    model = {cell: Counter() for cell in CELLS}
    for c, (weight, f, g) in enumerate(classes):
        for (x, y), u, v in product(CELLS, local, local):
            observations[x, y][c, u, v, f[x][u] * g[y][v]] += Fraction(weight, 16)
        if not any(f[0]) and not any(f[1]):
            # Never funded. One pre-sampled constant response per side suffices.
            for u, v in product(local, repeat=2):
                for cell in CELLS:
                    model[cell][c, u, v, 0] += Fraction(weight, 16)
            continue
        for a, b in CELLS:
            ua = [tuple(i for i in local if f[x][i] == a) for x in B]
            vb = [tuple(i for i in local if g[y][i] == b) for y in B]
            mass = Fraction(weight * len(ua[0]) * len(vb[0]), 16)
            choices = list(product(*ua, *vb))
            for u0, u1, v0, v1 in choices:
                for x, y in CELLS:
                    model[x, y][c, (u0, u1)[x], (v0, v1)[y], a * b] += mass / len(choices)
    assert observations == model
    return dict(visible_classes=len(classes), contexts_reconstructed=len(model),
                full_events_per_context=[len(model[cell]) for cell in CELLS])


def test_matched_local_model():
    direct = {cell: Counter() for cell in CELLS}
    prospective = {cell: Counter() for cell in CELLS}
    for i, j, l, k in product(B, repeat=4):
        ar = ((l, k), (k, l ^ k))
        br = ((l ^ k, l), (k, l))
        for x, y in CELLS:
            direct[x, y][i, ar[i], j, br[j], int(x == i and y == j)] += 1
            u, v = x ^ i, y ^ j
            prospective[x, y][u, ar[u], v, br[v], int(i == 0 and j == 0)] += 1
    assert direct == prospective
    return dict(contexts_reconstructed=4, common_latent_states=16)


def test_piece_counts():
    checks = {}
    for law in ("parity", "not_all_equal"):
        def accepts(bits):
            return sum(bits) % 2 == 0 if law == "parity" else 0 < sum(bits) < len(bits)

        matrix = [[sum(accepts((a, s, t)) and accepts((b, s, t)) for s, t in CELLS)
                   for b in B] for a in B]
        assert matrix == ([[2, 0], [0, 2]] if law == "parity" else [[3, 2], [2, 3]])
        counts = [[1, 0], [0, 1]]
        correlations = []
        for length in range(1, 6):
            counts = [[sum(row[k] * matrix[k][b] for k in B) for b in B] for row in counts]
            corr = Fraction(counts[0][0] - counts[0][1], sum(counts[0]))
            assert corr == (1 if law == "parity" else Fraction(1, 5 ** length))
            correlations.append(str(corr))
        checks[law] = dict(single_piece=matrix, isolated_correlations=correlations)
    return checks


def swapped(word, left, right, enabled):
    values = list(word)
    if enabled:
        values[left], values[right] = values[right], values[left]
    return tuple(values)


def trials(x, y, *, weights=(1, 1), public=False, bracket=False, commuting=False,
           own_only=False, always_fund=False, fixed_type=None, message=None, both_adapt=False):
    outcomes = Counter()
    sides = [Counter(), Counter()]
    flags = [Counter(), Counter()]
    for u, v in CELLS:
        if fixed_type is not None and (u, v) != fixed_type:
            continue
        ax = u if both_adapt else x
        by = (v if message else 1 - v) if message is not None else y
        ready_a, ready_b = (ax == u), (by == v)
        activate = ready_a and ready_b
        fund_a = True if always_fund else (ready_a if own_only else activate)
        fund_b = True if always_fund else (ready_b if own_only else activate)
        for start in product(B, repeat=3):
            indices = (0, 1) if commuting else (1, 2)
            mid1 = swapped(start, 0, 1, u)
            mid2 = swapped(mid1, *indices, v)
            mid3 = swapped(mid2, 0, 1, u)
            end = swapped(mid3, *indices, v)
            a = (ax, u, start, int(fund_a))
            b = (by, v, end, int(fund_b))
            if public:
                a += (v,)
                b += (u,)
            if bracket:
                a += (mid1, mid2)
                b += (mid2, mid3)
            w = weights[v]
            outcomes[int(fund_a) * start[0], int(fund_b) * end[0]] += w
            sides[0][a] += w
            sides[1][b] += w
            flags[0][int(fund_a)] += w
            flags[1][int(fund_b)] += w
    return outcomes, sides, flags


def analyze(**settings):
    arms = {cell: trials(*cell, **settings) for cell in CELLS}
    counts = [[arms[cell][0][outcome] for outcome in CELLS] for cell in CELLS]
    corr = [Fraction(a + d - b - c, a + b + c + d) for a, b, c, d in counts]
    chsh = [sum(i * e for i, e in zip(signs, corr)) for signs in product((-1, 1), repeat=4)
            if signs.count(-1) % 2]
    full = [[], []]
    bits = [[], []]
    for side, own in CELLS:
        pair = [(own, far) if side == 0 else (far, own) for far in B]
        full[side].append(tv(*(arms[cell][1][side] for cell in pair)))
        bits[side].append(tv(*(push(arms[cell][0], lambda ab: ab[side]) for cell in pair)))
    return dict(counts=counts, denominators=[sum(row) for row in counts], correlators=corr,
                signed=sum(corr[:3]) - corr[3], maximum=max(chsh), bit_TV=bits,
                full_endpoint_core_TV=full)


def test_routing():
    equal = [28, 0, 0, 4]
    primary = analyze()
    assert primary["counts"] == [equal, equal, equal, [26, 2, 2, 2]]
    assert primary["signed"] == primary["maximum"] == Fraction(9, 4)
    assert primary["bit_TV"] == primary["full_endpoint_core_TV"] == [[0, 0], [0, 0]]
    public, bracket, biased = analyze(public=True), analyze(bracket=True), analyze(weights=(1, 3))
    assert public["full_endpoint_core_TV"] == [[Fraction(1, 2)] * 2] * 2
    assert bracket["full_endpoint_core_TV"] == [[Fraction(1, 4)] * 2] * 2
    assert biased["full_endpoint_core_TV"] == [[Fraction(1, 4)] * 2, [0, 0]]
    assert biased["bit_TV"] == [[Fraction(1, 8)] * 2, [0, 0]]
    pref = {}
    for u, v in CELLS:
        by_type = analyze(fixed_type=(u, v))
        assert by_type["full_endpoint_core_TV"] == [[int(x == u) for x in B], [int(y == v) for y in B]]
        pref[f"{u}{v}"] = by_type
    pregrowth, commuting, own_only = analyze(always_fund=True), analyze(commuting=True), analyze(own_only=True)
    assert pregrowth["correlators"] == [Fraction(3, 4)] * 4
    assert pregrowth["signed"] == Fraction(3, 2)
    assert commuting["signed"] == 2
    assert own_only["signed"] == Fraction(5, 4)
    policies = {}
    for own_adapts in (False, True):
        for x in B:
            off, on = [trials(x, 0, message=m, both_adapt=own_adapts) for m in B]
            full_tv = tv(off[1][0], on[1][0])
            flag_tv = tv(off[2][0], on[2][0])
            bit_tv = tv(push(off[0], lambda ab: ab[0]), push(on[0], lambda ab: ab[0]))
            assert full_tv == flag_tv == (1 if own_adapts else Fraction(1, 2))
            assert bit_tv == (Fraction(1, 2) if own_adapts else Fraction(1, 4))
            key = "own_deficient_address" if own_adapts else f"fixed_own_{x}"
            policies[key] = dict(full_endpoint_TV=full_tv, flag_TV=flag_tv, selected_bit_TV=bit_tv)
    return dict(primary=primary, disclosed_type=public, bracketed_switch=bracket,
                biased_B_preference=biased, individual_preparations=pref,
                always_read_old_terminals=pregrowth, commuting_correspondences=commuting,
                separately_funded_ends=own_only, message_policies=policies)


def build_result():
    protocol = ROOT / "research/WHOLE-STAGE-SETTINGS-20261120-001/preregistration.md"
    paths = (protocol, HERE / "proof.md", Path(__file__).resolve())
    digests = {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in paths}
    assert digests[str(protocol.relative_to(ROOT))] == "44e0640d4119a981c4c5f9e8095817d7144e9669c608fad0a57b727b41e0352d"
    return dict(proof="WHOLE-STAGE-SETTINGS-20261120-001A-P001",
                ticket="WHOLE-STAGE-SETTINGS-20261120-001A", status="Proved", referee="pending",
                claim="Exact visibility of a shared binary funding or closure event and its ordered-mixture and matched-setting special cases. Product/common-part locality, classification by complete prepared payloads, and free-message policy signalling.",
                validation="V1 standalone exact finite checks of the proof's probability reductions. The incidence and full guarded native endpoints are validated in the construction lane. The referee is pending.",
                source_sha256=digests, proof_sha256=digests[str((HERE / "proof.md").relative_to(ROOT))],
                checks=dict(general_visibility=test_visibility(), optimal_message=test_policy_optimum(),
                            visible_product_reconstruction=test_visible_product(),
                            matched_reconstruction=test_matched_local_model(), relay_counts=test_piece_counts(),
                            parity_terminal_source=test_routing()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the entire reproducible result")
    args = parser.parse_args()
    result = build_result()
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        saved = json.loads((HERE / "result.json").read_text())
        assert json.loads(json.dumps(result, default=str)) == saved
        print("Passed all local-record checks and reproduced result.json from its bound sources.")
