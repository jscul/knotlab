"""Exact local critical inequalities and independent finite count controls."""

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import combinations_with_replacement
import json
from math import comb
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEAD = ROOT / "proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead"
VERIFY = ROOT / "experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"
EXTEND = ROOT / "experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"
FAST = ROOT / "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins"
sys.path[:0] = [str(path) for path in (DEAD, VERIFY, EXTEND, FAST)]
import deadlib  # noqa: E402
import fastlib  # noqa: E402
from extend import C, grow1  # noqa: E402
from verify import Arrangement, round_replay, start_audit  # noqa: E402


def decimal(value):
    with localcontext() as c:
        c.prec = 55
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def discriminant(z):
    return 1 - 4*z*z*(1+z)


def bracket():
    low, high = Fraction(2, 5), Fraction(1, 2)
    assert discriminant(low) > 0 > discriminant(high)
    while high-low > Fraction(1, 10**62):
        middle = (high+low)/2
        if discriminant(middle) > 0:
            low = middle
        else:
            high = middle
    assert discriminant(low) > 0 > discriminant(high)
    return low, high


def multiply(a, b, cap=None):
    size = len(a)+len(b)-1
    if cap is not None:
        size = min(size, cap+1)
    row = [0]*size
    for i, x in enumerate(a):
        for j, y in enumerate(b[:max(0, size-i)]):
            row[i+j] += x*y
    return row


def add(a, b):
    width = max(len(a), len(b))
    return [x+y for x,y in zip(a + [0]*(width-len(a)), b + [0]*(width-len(b)), strict=True)]


def pendant(z, open_count, spare_count):
    if not spare_count:
        return Fraction(1), Fraction(1)
    if open_count == 1:
        assert spare_count == 1
        term, marked = 1 + z/(1-z)**2, z*(1+z)/(1-z)**3
    elif open_count == 2:
        term, marked = 1/(1-z), z/(1-z)**2
    else:
        term, marked = 1+z, z
    value = term**spare_count
    return value, value + spare_count*marked*term**(spare_count-1)


def local_certificate(low, high):
    # A = (1+zB)^2 identically for A=4(1+z)^2, zB=1+2z.
    # z(B-1-zA) = (1+z)(1-4z^2(1+z)) for that same pair.
    poly_a, poly_zb, poly_disc = [4,8,4], [1,2], [1,0,-4,-4]
    assert multiply(add([1], poly_zb), add([1], poly_zb)) == poly_a
    assert add([1,1], [0,0,*[-x for x in poly_a]]) == multiply([1,1], poly_disc)
    assert multiply([0,0,2], add([1], poly_zb)) == [0,0,4,4]
    a_low, a_high = 4*(1+low)**2, 4*(1+high)**2
    b_low, b_high = 2+1/high, 2+1/low
    profiles = [p for degree in (0,1,2) for p in combinations_with_replacement(range(2,6), degree) if sum(p) <= 5]
    assert set(profiles) == {(), (2,), (3,), (4,), (5,), (2,2), (2,3)}
    cases = []
    factor_cases = []
    for profile in profiles:
        required = sum(k-1 for k in profile)
        for slack in range(6-sum(profile)):
            o = required + slack
            if o < 1:
                continue
            e, e_marked = pendant(high, o, slack)
            kind = "no pendant" if slack == 0 else "two-ray" if o == 1 else "one-ray" if o == 2 else "spare"
            record = {"profile": profile, "open": o, "demand": required, "surplus": slack, "pendant_kind": kind,
                      "factor_upper_approx": decimal(e), "pointed_factor_upper_approx": decimal(e_marked), "incoming": []}
            for incoming in sorted(set(profile)):
                rest = list(profile)
                rest.remove(incoming)
                coupling = (b_high if rest[0] == 2 else a_high) if rest else 1
                if incoming <= 3:
                    exact = profile == (2,3)
                    if exact:
                        assert e == 1
                        gap = "0 (exact identity)"
                    else:
                        strict = (a_low if incoming == 2 else b_low) - e*coupling
                        assert strict > 0, (profile, o, incoming, strict)
                        gap = str(strict)
                    row = {"block": incoming, "needed_target": "A" if incoming == 2 else "B",
                           "strict_lower_gap": gap, "equality": exact}
                    if incoming == 3:
                        factor_cases.append((profile, o, exact))
                else:
                    assert len(profile) == 1 and kind in {"spare", "no pendant"}
                    row = {"block": incoming, "finite_polynomial_branch": True,
                           "upper_branch_at_r_approx": decimal((1+high*e)**(incoming-1))}
                record["incoming"].append(row)
            cases.append(record)
    assert len(cases) == 18
    pair_product_cases = [{"two_other_members": [a[:2], b[:2]], "strict": not(a[2] and b[2])}
                          for a,b in combinations_with_replacement(factor_cases, 2)]
    assert len(pair_product_cases) == 10 and sum(not e["strict"] for e in pair_product_cases) == 1
    assert high*(1+high) < 1
    return {"certified_radius_bracket": [str(low), str(high)], "radius_approx": decimal((low+high)/2),
            "certified_rate_bracket": [str(1/high), str(1/low)], "rate_approx": decimal(2/(low+high)),
            "critical_A_approx": decimal((a_low+a_high)/2), "critical_B_approx": decimal((b_low+b_high)/2),
            "theta_identities_checked_in_polynomials": True,
            "two_block_chain_normalized_derivative_upper": str(high*(1+high)),
            "point_profiles_and_surpluses": cases, "three_block_joint_profiles": pair_product_cases}


def divided_coefficients(poly, depth, index):
    out = []
    for age in range(depth+1):
        n = age+index
        coefficient = poly[n] if n < len(poly) else 0
        term, rem = divmod(coefficient, age+1)
        assert rem == 0, (age, coefficient)
        out.append(term)
    return out


def theta_coefficients(depth):
    # The square of the Catalan series has coefficient Catalan(k+1).
    # A(z)=(1+z)^2 C(z^2(1+z))^2, B(z)=1+z A(z).
    a = [0]*(depth+1)
    for k in range(depth//2+1):
        catalan = comb(2*k+2,k+1)//(k+2)
        for j in range(min(k+2, depth-2*k)+1):
            a[2*k+j] += catalan*comb(k+2,j)
    b = ([1]+a)[:depth+1]
    assert a == multiply(add([1], [0,*b]), add([1], [0,*b]), depth)
    core = divided_coefficients([6*x for x in multiply(a,b,depth)], depth, 0)
    counts = [11] + [core[t]+3*t for t in range(1, depth+1)]
    return counts, core, b


def five_cycle_counts(depth):
    fib = [0,1]
    while len(fib) <= depth+2:
        fib.append(fib[-1]+fib[-2])
    return [5*fib[t+2] for t in range(depth+1)]


def one_ray_one_spare_end_counts(depth):
    # Point 0 has one ray, point 2 has three spares. Expand their pointed
    # factors separately, then multiply each by the other side's branch.
    ray = [1]*(depth+1)
    pointed_ray = list(range(1, depth+2))
    spares = [1,3,3,1]
    pointed_spares = multiply([1,2,1], [1,4])
    roots = add(multiply(pointed_ray, [1,*spares], depth), multiply(pointed_spares, [1,*ray], depth))
    counts = divided_coefficients(roots, depth, 0)
    assert counts[0] == 2
    counts[0] += 1  # the closed middle row
    return counts


def isolated_block_counts(size, spares, depth):
    choices = [1, *[comb(spares,k) for k in range(spares+1)]]
    finite = [1]
    for _ in range(size):
        finite = multiply(finite, choices)
    return [size+1] + [finite[t+1] if t+1 < len(finite) else 0 for t in range(1, depth+1)]


def physical_fixture(sizes, meetings, expected, depth):
    assert max(sizes) <= 5
    a = deadlib.analyse(sizes, meetings)
    assert sum(a["open"]) >= 2 and all(a["open"][p] >= a["d"][p] for p in a["live"])
    assert all(len(a["nb"][p] & a["nb"][q]) <= 1 for p in a["live"] for q in a["live"] if p < q)
    assert all(a["nb"][p] & a["nb"][q] & a["nb"][r] for p in a["live"] for q in a["live"] for r in a["live"]
               if p < q < r and a["nb"][p] & a["nb"][q] and a["nb"][q] & a["nb"][r] and a["nb"][r] & a["nb"][p])
    assert deadlib.exact_counts(a,len(expected)-1) == expected
    stars = [[] for _ in sizes]
    for name,(u,v) in enumerate(meetings):
        stars[u].append(name)
        stars[v].append(name)
    after = len(meetings)
    for s, n in zip(stars, sizes, strict=True):
        fresh = n-len(s)
        s.extend(range(after, after+fresh))
        after += fresh
    stage = Arrangement.parse(stars)
    assert start_audit(stage)["census_open_legal"]
    actual = [len(stars)]
    fastlib.install(C.S.F)
    try:
        for _ in range(depth):
            raw = grow1(stage.stars)
            if raw is None:
                assert not stage.live
                actual.append(0)
                continue
            later = Arrangement.parse([sorted(s) for s in raw])
            actual.append(len(round_replay(stage, later)))
            stage = later
    finally:
        fastlib.uninstall(C.S.F)
    assert actual == expected[:depth+1]
    return {"starting_sizes": sizes, "meetings": meetings, "ranks": sorted(piece["rank"] for piece in a["pieces"]),
            "exact_counts": expected, "literal_growth_prefix": actual}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, default=HERE/"check_rate.json")
    args = cli.parse_args()
    low, high = bracket()
    report = local_certificate(low, high)
    depth = 25
    theta, core, b = theta_coefficients(depth)
    meetings = [(u,v) for i in range(3) for u,v in [(0,2+i),(1,5+i),(2+i,8+i),(5+i,8+i)]]
    assert theta[12:14] == [8910,18375]
    report["controls"] = {
        "theta": physical_fixture([3,3]+[5]*6+[3]*3, meetings, theta, 6) | {"main_piece_counts": core},
        "golden_ratio_five_cycle": physical_fixture([5]*5, [(0,1),(1,2),(2,3),(3,4),(0,4)], five_cycle_counts(depth), 7),
        "two_block_ray_and_three_spares": physical_fixture([4,3,5], [(0,1),(0,1),(1,2)], one_ray_one_spare_end_counts(depth), 10),
        "isolated_four_block_with_spares": physical_fixture([4]+[5]*4, [(0,j) for j in range(1,5)], isolated_block_counts(4,1,depth), 8),
        "isolated_five_block": physical_fixture([5]*6, [(0,j) for j in range(1,6)], isolated_block_counts(5,0,depth), 5),
    }
    actual = deadlib.analyse([4,3,5], [(0,1),(0,1),(1,2)])
    assert deadlib.profile(actual,2) == (2,) and actual["spares"][2] == 3
    larger = [1,1,3,3,1]  # 1 + z(1+z)^3, the branch through the three-spare end.
    assert larger[:2] == b[:2] and larger[2] > b[2]
    report["coefficientwise_dominance_negative_control"] = {
        "branch": "1 + z*(1+z)^3", "first_larger_degree": 2, "branch_coefficient": larger[2], "theta_B_coefficient": b[2]}
    history = json.loads((DEAD/"posthoc_rates.json").read_text())
    assert history["most_common"][0] == [2.382976, 133]
    report["historical_only"] = {"rounded_rate": 2.382976, "rounded_ties": 133,
                                 "role": "archived rounded rates, without an exact identity certificate"}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")


if __name__ == "__main__":
    main()
