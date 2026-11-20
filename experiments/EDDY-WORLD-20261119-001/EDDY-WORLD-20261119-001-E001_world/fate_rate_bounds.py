"""Certify rational bounds on the two double-ring growth rates."""

from collections import deque
from fractions import Fraction
from itertools import combinations
import json

from fate_series import DATA, HERE, Source


GRID = 10**10


def equations(source):
    ports = [(p, b) for b, block in enumerate(source.blocks) for p in block]
    index = {port: i for i, port in enumerate(ports)}
    deps = [[index[q, c] for c, row in enumerate(source.blocks)
             if c != b and p in row for q in row if q != p] for p, b in ports]
    reverse = [[] for _ in ports]
    for i, row in enumerate(deps):
        for j in row:
            reverse[j].append(i)
    choices = []
    for i, row in enumerate(deps):
        distances = {i: 0}
        queue = deque([i])
        while queue:
            j = queue.popleft()
            for x in reverse[j]:
                if x not in distances:
                    distances[x] = distances[j] + 1
                    queue.append(x)
        for j, k in combinations((v for v in row if v in distances), 2):
            choices.append((1 + distances[j] + distances[k], i, j, k))
    return ports, deps, min(choices)


def prove(source, system, x):
    ports, deps, witness = system
    h, i, j, k = witness
    z = 1 / x
    factors = []
    for (p, _), row in zip(ports, deps):
        rays = max(0, 3 - source.opens[p])
        e = (1 + z / (1 - z)**rays)**source.spares[p]
        # Integer input/output messages represent GRID times their value.
        factors.append(z * e * GRID / GRID**len(row))
    numerators = [v.numerator for v in factors]
    denominators = [v.denominator for v in factors]
    limit = GRID / z**h
    cap = limit.numerator // limit.denominator + 2
    old_lo, old_hi = [GRID] * len(ports), [GRID] * len(ports)
    for iteration in range(1, 20001):
        lo, hi = [], []
        for n, d, row in zip(numerators, denominators, deps):
            lower = upper = n
            for q in row:
                lower *= old_lo[q]
                upper *= old_hi[q]
            lo.append(min(cap, GRID + lower // d))
            hi.append(min(cap, GRID + (upper + d - 1) // d))
        if lo[i] > limit:
            return {"side": "lower", "x": str(x), "iterations": iteration,
                    "ports": [list(ports[v]) for v in (i, j, k)], "power": h,
                    "lower_ordinate_scaled": lo[i]}
        if hi == old_hi and max(hi) < cap:
            return {"side": "upper", "x": str(x), "iterations": iteration,
                    "positive_supersolution_scaled_in_port_order": hi}
        old_lo, old_hi = lo, hi
    raise ArithmeticError(f"undecided exact comparison at {x}")


def certify(case):
    source = Source(case)
    system = equations(source)
    low, high = 2000, 3000
    low_proof = prove(source, system, Fraction(low, 1000))
    high_proof = prove(source, system, Fraction(high, 1000))
    assert low_proof["side"] == "lower" and high_proof["side"] == "upper"
    while high - low > 1:
        mid = (low + high) // 2
        proof = prove(source, system, Fraction(mid, 1000))
        if proof["side"] == "lower":
            low, low_proof = mid, proof
        else:
            high, high_proof = mid, proof
    return {"rate_interval_per_thousand": [low, high],
            "lower_certificate": low_proof, "upper_certificate": high_proof}


def main():
    inputs = json.loads((HERE / "inputs.json").read_text())["cases"]
    result = {case["id"]: certify(case) for case in inputs if case["id"] in {"T4", "T8"}}
    assert result["T8"]["rate_interval_per_thousand"][1] < result["T4"]["rate_interval_per_thousand"][0]
    (DATA / "fate_rate_bounds.json").write_text(json.dumps({"scale": GRID, "cases": result}, indent=2) + "\n")


if __name__ == "__main__":
    main()
