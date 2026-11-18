"""Shared-runner job for TREE-STEPS-20261118-001B-E001: one case per (shape, law-assignment block) at six knots, and per random
tree at seven knots."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import treelib as T  # noqa: E402

L = T.L


def cases():
    shapes6 = L.tree_shapes(6)
    for si in range(len(shapes6)):
        for block in range(4):
            yield f"six-{si}-{block}", {"kind": "six", "shape": si, "block": block}
    for i in range(80):
        yield f"rand7-{i}", {"kind": "rand", "seed": 7000 + i}


def run_base(knots, n, laws):
    kn = list(zip(laws, knots))
    B = L.Base(L.states_from_knots(n, kn), n)
    sp = L.steps_apart(knots, n)
    bad, badK, diff = [], [], 0
    for x in range(n):
        for y in range(x + 1, n):
            d = sp[x][y]
            v, vK = T.both(B, x, y, d + 2)
            if abs(v - d) > 1e-9:
                bad.append([x, y, d, v])
            if abs(vK - d) > 1e-9:
                badK.append([x, y, d, vK])
            diff += abs(v - vK) > 1e-9
    return {"laws": "".join(laws), "n": n, "pairs": n * (n - 1) // 2, "delta_off": bad, "deltaK_off": badK, "differ": diff}


def run(case_id, payload):
    import itertools
    if payload["kind"] == "six":
        knots, n = L.tree_shapes(6)[payload["shape"]]
        assigns = list(itertools.product("PN", repeat=6))[payload["block"] * 16:(payload["block"] + 1) * 16]
        return {"rows": [run_base(knots, n, a) for a in assigns]}
    rng = random.Random(payload["seed"])
    knots, n = T.random_tree(7, 3, rng)
    laws = tuple(rng.choice("PN") for _ in knots)
    return {"rows": [{"knots": knots, **run_base(knots, n, laws)}]}
