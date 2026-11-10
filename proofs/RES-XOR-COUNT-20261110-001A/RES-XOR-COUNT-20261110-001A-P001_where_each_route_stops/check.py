"""Checks for RES-XOR-COUNT-20261110-001A: where each route of the frozen transfer statement stops for the sphere's count.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run

1. Lemma 1 (Braun's generic criterion is capped by the polynomial-calculus degree): over a grid of v, d <= 2v/3 and every admissible
   h, k, w with k(D + 1) < d, the criterion's right side C(v + k, k) / C(v - h(k + 1) - 1 + k, k) is at most exp(d^2 / (6v)), and its
   density exponent h k^2 / (v + k) at most d^2 / (36 v).
2. Lemma 3 (stifling gadgets are not affine): every Boolean function on at most 4 bits, and Maj_5; none is both affine and 1-stifled,
   Maj_3 is 1-stifled and Maj_5 is 2-stifled.
3. The degree ceiling on K_2: its resolution width (width-bounded saturation) is 4, and its polynomial-calculus degree (3,
   PC-COUNT-20261110-001B) is at most the width plus 1."""
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SA = next((ROOT / "proofs/COUNT-NOTE-20261107-001B").iterdir())
sys.path.insert(0, str(SA))
spec = importlib.util.spec_from_file_location("sa_lib", SA / "sa_lib.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def log_binom(a, b):
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def cap_grid():
    worst_ratio, worst_density, cases = 0.0, 0.0, 0
    for v in (60, 200, 1000, 5000):
        for d in sorted({4, 8, int(math.sqrt(v)), 2 * int(math.sqrt(v)), v // 10, v // 3, 2 * v // 3}):
            if d < 4 or d > 2 * v // 3:
                continue
            for h in range(1, d):
                for w in (3, 6, 12):
                    Dg = max(2 * h + w, 4 * h + 1)
                    for k in range(1, d):
                        if k * (Dg + 1) >= d or h * (k + 1) + 1 > v:
                            break
                        r = h * (k + 1) + 1
                        log_right = log_binom(v + k, k) - log_binom(v - r + k, k)
                        worst_ratio = max(worst_ratio, log_right / (d * d / (6 * v)))
                        worst_density = max(worst_density, (h * k * k / (v + k)) / (d * d / (36 * v)))
                        cases += 1
    return worst_ratio, worst_density, cases


def table(m):
    return [list(x) for x in itertools.product((0, 1), repeat=m)]


def is_affine(f, m):
    pts = table(m)
    for c in range(2):
        for T in range(1 << m):
            if all(f[i] == (c ^ (bin(T & int("".join(map(str, p)), 2)).count("1") & 1)) for i, p in enumerate(pts)):
                return True
    return False


def is_stifled(f, m, k):
    """for every k-set of positions and every b, some setting of the others makes f constantly b"""
    pts = table(m)
    idx = {tuple(p): i for i, p in enumerate(pts)}
    for Sset in itertools.combinations(range(m), k):
        rest = [i for i in range(m) if i not in Sset]
        for b in (0, 1):
            ok = False
            for fix in itertools.product((0, 1), repeat=len(rest)):
                good = True
                for free in itertools.product((0, 1), repeat=k):
                    p = [0] * m
                    for i, x in zip(rest, fix):
                        p[i] = x
                    for i, x in zip(Sset, free):
                        p[i] = x
                    if f[idx[tuple(p)]] != b:
                        good = False
                        break
                if good:
                    ok = True
                    break
            if not ok:
                return False
    return True


def resolution_refutes(cls, w):
    have = set(c for c in cls if len(c) <= w)
    by_lit = {}
    for c in have:
        for l in c:
            by_lit.setdefault(l, set()).add(c)
    queue = list(have)
    while queue:
        c = queue.pop()
        for l in c:
            for d in list(by_lit.get(-l, ())):
                r = (c | d) - {l, -l}
                if any(-x in r for x in r) or len(r) > w or r in have:
                    continue
                if not r:
                    return True
                have.add(r)
                queue.append(r)
                for x in r:
                    by_lit.setdefault(x, set()).add(r)
    return False


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    wr, wd, cases = cap_grid()
    check("1_braun_criterion_capped_by_degree", wr <= 1.0 and wd <= 1.0,
          {"admissible (v, d, h, w, k) read": cases, "largest log(right side) / (d^2 / 6v)": round(wr, 4),
           "largest density exponent / (d^2 / 36v)": round(wd, 4)})

    both, n_f, n_aff = 0, 0, 0
    for m in range(1, 5):
        for code in range(1 << (1 << m)):
            f = [(code >> i) & 1 for i in range(1 << m)]
            a = is_affine(f, m)
            n_f += 1
            n_aff += a
            if a and is_stifled(f, m, 1):
                both += 1
    maj = lambda m: [int(sum(p) > m // 2) for p in table(m)]
    ok = both == 0 and is_stifled(maj(3), 3, 1) and is_stifled(maj(5), 5, 2) and not is_affine(maj(3), 3)
    check("2_stifling_gadgets_are_not_affine", ok, {"functions on 1 to 4 bits": n_f, "affine among them": n_aff,
                                                    "affine and 1-stifled": both, "Maj_3 1-stifled, Maj_5 2-stifled": True})

    cls = [frozenset((v + 1) * (1 if val == 0 else -1) for v, val in f) for f in S.falsifiers(2)]
    widths = {w: resolution_refutes(cls, w) for w in (3, 4)}
    pc = json.loads((ROOT / "artifacts/PC-COUNT-20261110-001B/PC-COUNT-20261110-001B-E001_small_sphere_degrees/run/result.json").read_text())
    d2 = pc["readings"]["K_2 count pc"]["degree"]
    check("3_degree_at_most_width_plus_1_on_K_2", widths == {3: False, 4: True} and d2 <= 4 + 1,
          {"K_2 resolution width": 4, "refuted at width": widths, "K_2 polynomial-calculus degree": d2})

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "RES-XOR-COUNT-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
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
