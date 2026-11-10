"""Checks for HOLE-SEP-20261110-001A: the ingredients of the reduction (R), on small instances.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run

1. tau([f_x = h]) = prod_t (sum_{z : z_t = h_t} X_x,z) reduces to X_x,h modulo Braun's unary ideal within degree l, for every pigeon x and
   hole h (n = 4, 8): its matching normal form, after the row-sum relations of degree <= l, equals X_x,h.
2. Hence tau(G(h)_j) = sum_x x_j tau([f_x = h]) reduces to gamma_h,j = sum_x x_j X_x,h (n = 4, 8).
3. The reduced decoder kills the inverse-counting identities kappa_{a,j} modulo the degree-1 ideal (n = 4, 8, 16, 32), and these
   (l + 1)^2 elements are independent."""
import hashlib
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
X = ROOT / "experiments/HOLE-SEP-20261110-001B/HOLE-SEP-20261110-001B-E001_decoder_kernel"
spec = importlib.util.spec_from_file_location("hole_sep_run", X / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["hole_sep_run"] = R
spec.loader.exec_module(R)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def normal_form(S, factors):
    """the matching normal form of a product of linear forms in the cells (each a list of cells): repeated rows or columns vanish,
    a repeated cell merges"""
    v = 0
    for cells in itertools.product(*factors):
        T = frozenset(cells)
        xs = [x for x, _ in T]
        hs = [h for _, h in T]
        if len(set(xs)) == len(xs) and len(set(hs)) == len(hs):
            v ^= 1 << S.index[T]
    return v


def reduces_to(S, v, w, basis):
    u = v ^ w
    while u:
        b = u.bit_length() - 1
        if b not in basis:
            return False
        u ^= basis[b]
    return True


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)
    ok1, ok2, cases = True, True, 0
    for n in (4, 8):
        S = R.Space(n, S_l := n.bit_length() - 1)
        basis = {}
        for v in S.relations():
            R.insert(basis, v)
        for x in range(S.m):
            for h in range(n):
                factors = [[(x, z) for z in range(n) if ((z >> t) & 1) == ((h >> t) & 1)] for t in range(S.l)]
                v = normal_form(S, factors)
                ok1 &= reduces_to(S, v, 1 << S.index[frozenset({(x, h)})], basis)
                cases += 1
        for h in range(n):
            for j in range(S.lg):
                v = 0
                for x in range(S.m):
                    if (x >> j) & 1:
                        v ^= normal_form(S, [[(x, z) for z in range(n) if ((z >> t) & 1) == ((h >> t) & 1)] for t in range(S.l)])
                ok2 &= reduces_to(S, v, S.image([("g", h, j)]), basis)
    check("1_indicator_decodes_to_a_cell", ok1, {"(n, x, h) cases": cases, "n": [4, 8]})
    check("2_hole_bits_decode_to_weighted_hole_sums", ok2, {"n": [4, 8]})
    ok3 = {}
    for n in (4, 8, 16, 32):
        S = R.Space(n, 1)
        ok, cnt = R.known_elements_check(S)
        ok3[n] = {"in K_1": ok, "count": cnt}
    check("3_inverse_counting_identities_in_the_kernel", all(v["in K_1"] for v in ok3.values()), ok3)
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "HOLE-SEP-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
