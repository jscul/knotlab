"""Shared-runner job for FREE-READ-20261118-001B-E001."""
import itertools
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import freelib as F  # noqa: E402

L, T = F.L, F.T


def cases():
    for si in range(19):
        for block in range(8):
            yield f"six-{si}-{block}", {"kind": "six", "shape": si, "block": block}
    for i in range(80):
        yield f"rand7-{i}", {"kind": "rand", "seed": 9000 + i}
    yield "cycles", {"kind": "cycles"}


def tree_rows(knots, n, laws):
    st = L.states_from_knots(n, list(zip(laws, knots)))
    sup = F.Supports(st, n)
    sp = L.steps_apart(knots, n)
    off = []
    for x, y in itertools.combinations(range(n), 2):
        b = sup.bond_distance(x, y, sp[x][y] + 2)
        if b is None or b != sp[x][y] + 1:
            off.append([x, y, sp[x][y], b])
    return {"laws": "".join(laws), "n": n, "pairs": n * (n - 1) // 2, "off": off}


def fin(v):
    """JSON has no infinity: write an infinite reading (no binding set) as null; merge.py reads it back as infinity."""
    return None if v == math.inf else v


def cycles():
    """Rings of m = 3..6 knots under pure parity, pure NAE and alternating laws, and the mixed cycle (an NAE path of k = 2..5 from
    x to y closed by a parity knot (x, y, z)): bond distance, steps apart, tau, delta and delta_K for every pair."""
    out = []
    configs = []
    for m in range(3, 7):
        for name, laws in (("P", "P" * m), ("N", "N" * m), ("alt", ("PN" * m)[:m])):
            knots = [(laws[i], (2 * i, 2 * i + 1, (2 * i + 2) % (2 * m))) for i in range(m)]
            configs.append((f"ring{m}-{name}", knots, 2 * m))
    for k in range(2, 6):
        knots = [("N", (2 * j, 2 * j + 1, 2 * j + 2)) for j in range(k)]
        n = 2 * k + 1
        knots.append(("P", (0, 2 * k, n)))
        configs.append((f"closed{k}", knots, n + 1))
    for name, knots, n in configs:
        st = L.states_from_knots(n, knots)
        sup = F.Supports(st, n)
        B = L.Base(st, n)
        sp = L.steps_apart([k for _, k in knots], n)
        rows = []
        for x, y in itertools.combinations(range(n), 2):
            d = sp[x][y]
            b = sup.bond_distance(x, y, d + 3)
            v, vK = T.both(B, x, y, d + 3)
            rows.append({"x": x, "y": y, "steps": d, "bond_minus_1": None if b is None else b - 1,
                         "tau": fin(L.tau(B.correlation(x, y))), "delta": fin(v), "delta_K": fin(vK)})
        out.append({"name": name, "n": n, "N": len(st), "rows": rows})
    # negative control: the clause law "not all ones" (K1 and K2 hold) on chains of 2 to 4 knots; bonds holding the ends
    for k in range(2, 5):
        n = 2 * k + 1
        knots = [(2 * j, 2 * j + 1, 2 * j + 2) for j in range(k)]
        st = [s for s in range(1 << n) if all(not all((s >> v) & 1 for v in kn) for kn in knots)]
        sup = F.Supports(st, n)
        out.append({"name": f"clause-chain{k}", "n": n, "N": len(st),
                    "rows": [{"x": 0, "y": n - 1, "steps": k, "bond_minus_1": (lambda b: None if b is None else b - 1)(sup.bond_distance(0, n - 1, n))}]})
    return out


def run(case_id, payload):
    if payload["kind"] == "six":
        knots, n = L.tree_shapes(6)[payload["shape"]]
        assigns = list(itertools.product("PN", repeat=6))[payload["block"] * 8:(payload["block"] + 1) * 8]
        return {"rows": [tree_rows(knots, n, a) for a in assigns]}
    if payload["kind"] == "rand":
        rng = random.Random(payload["seed"])
        knots, n = T.random_tree(7, 3, rng)
        laws = tuple(rng.choice("PN") for _ in knots)
        return {"rows": [tree_rows(knots, n, laws)]}
    return {"cycles": cycles()}
