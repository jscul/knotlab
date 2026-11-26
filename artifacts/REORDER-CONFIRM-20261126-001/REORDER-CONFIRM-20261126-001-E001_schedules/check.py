"""Frozen confirmation of the reordering sign: the gate and predictions P1-P8 of
research/REORDER-CONFIRM-20261126-001/preregistration.md.

Run from the repository root:  .venv/bin/python -B <this folder>/check.py
Writes results.json beside this file. Everything is exact (integers and fractions) except the phase family of P6(b), which
is compared with a tolerance of 1e-9.
"""

import json
import math
import random
import sys
import time
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E  # noqa: E402

ROOT = HERE.parents[2]
SEED = 20261126
LETTERS = "abcdef"


def name(order):
    return "".join(LETTERS[i] for i in order)


def inversions(order):
    """Pairs (i, j), i < j as distinctions, that the sequence lists j before i."""
    pos = {v: k for k, v in enumerate(order)}
    return {(i, j) for i, j in combinations(sorted(order), 2) if pos[i] > pos[j]}


def differ(a, b):
    """Pairs ordered differently by two sequences."""
    pa = {v: k for k, v in enumerate(a)}
    pb = {v: k for k, v in enumerate(b)}
    return {(i, j) for i, j in combinations(sorted(a), 2) if (pa[i] < pa[j]) != (pb[i] < pb[j])}


def sgn(order):
    return (-1) ** len(inversions(order))


def even_words(n):
    return [w for w in product((0, 1), repeat=n) if sum(w) % 2 == 0]


def carrying(psi, readers):
    return E.full_contradiction(E.correlations(psi, readers))


def target_cache():
    cache = {}

    def get(n):
        if n not in cache:
            cache[n] = E.target_expectations(n)
        return cache[n]
    return get


TARGET = target_cache()
OUT = {}
TIMES = {}


def timed(label):
    def wrap(fn):
        def run(*a, **k):
            t = time.time()
            r = fn(*a, **k)
            TIMES[label] = round(time.time() - t, 2)
            print(f"{label}: {TIMES[label]} s", flush=True)
            return r
        return run
    return wrap


# ---------------------------------------------------------------- gate

@timed("G_a_replay")
def gate_replay():
    rec = json.loads((ROOT / "research/REORDER-SIGN-20261126-001/verify_fock.json").read_text())
    F = E.Modes(3)
    mismatches = []
    rows = 0
    for label, first in (("parents_created_c_b_a", (2, 1, 0)), ("parents_created_a_b_c", (0, 1, 2))):
        base = E.start(F, first)
        for kind in ("F1", "F2"):
            R = E.Readers(F, [kind] * 3)
            r = rec[f"{label}/{kind}"]
            grown, cs = {}, {}
            for order in permutations(range(3)):
                psi = E.grow(F, base, order)
                grown[order] = psi
                c = E.correlations(psi, R)
                cs[order] = c
                e = E.expectations(psi, R, ["ZZZ", "ZFF", "FZF", "FFZ"])
                win = Fraction(0)
                for s, w in (((0, 0, 0), "ZZZ"), ((0, 1, 1), "ZFF"), ((1, 0, 1), "FZF"), ((1, 1, 0), "FFZ")):
                    want = int(any(s))
                    win += (1 + (-1) ** want * e[w]) / 2
                win /= 4
                vals = [c[frozenset(t)] for t in ((), (0, 1), (0, 2), (1, 2))]
                p = vals[0] * vals[1] * vals[2] * vals[3]
                row = r["orders"][name(order)]
                rows += 1
                ok = (all(abs(float(v) - w) < 1e-9 for v, w in zip(vals, row["ZZZ_XXZ_XZX_ZXX"]))
                      and abs(float(p) - row["product_P"]) < 1e-9
                      and E.full_contradiction(c) == row["full_contradiction"]
                      and abs(float(win) - row["scored_win_fixed_labels"]) < 1e-9)
                if not ok:
                    mismatches.append([label, kind, name(order)])
            avg = {T: sum(cs[o][T] for o in cs) / len(cs) for T in cs[(0, 1, 2)]}
            best = max(abs(avg[frozenset()] - sum(avg[frozenset(pr)] * (-1) ** (u[pr[0]] + u[pr[1]])
                                                   for pr in ((0, 1), (0, 2), (1, 2))))
                       for u in product((0, 1), repeat=3))
            coh = E.add(*grown.values())
            words = sorted({"".join(str((b >> k) & 1) for k in range(3)) for b in coh[0]})
            ok = (abs(float(best) - r["order_blind_best_mermin_score"]) < 1e-9
                  and words == r["coherent_sum_old_words_present"])
            rows += 1
            if not ok:
                mismatches.append([label, kind, "order-blind / coherent"])
    return {"rows_compared": rows, "mismatches": mismatches, "held": not mismatches}


@timed("G_b_anticommutation")
def gate_car():
    out = {}
    rng = random.Random(SEED)
    for lname, listing in (("ascending", None), ("random", rng.sample(range(9), 9))):
        F = E.Modes(3, listing)
        bad = 0
        for b in range(512):
            v = E.state([b], [1])
            for m, k in product(range(9), repeat=2):
                ac = E.add(E.annihilate(F, m, E.create(F, k, v)), E.create(F, k, E.annihilate(F, m, v)))
                want = v if m == k else E.empty()
                if not same(ac, want):
                    bad += 1
                aa = E.add(E.annihilate(F, m, E.annihilate(F, k, v)), E.annihilate(F, k, E.annihilate(F, m, v)))
                cc = E.add(E.create(F, m, E.create(F, k, v)), E.create(F, k, E.create(F, m, v)))
                if len(aa[0]) or len(cc[0]):
                    bad += 1
        out[lname] = {"failures": bad}
    out["held"] = all(v["failures"] == 0 for v in out.values() if isinstance(v, dict))
    return out


def same(a, b):
    a, b = E.simplify(a), E.simplify(b)
    return len(a[0]) == len(b[0]) and np.array_equal(a[0], b[0]) and np.allclose(a[1], b[1], atol=1e-12)


# second code path: Jordan-Wigner matrices
def jw_ops(M):
    Zm = sp.diags([1.0, -1.0])
    I = sp.identity(2)
    low = sp.csr_matrix(np.array([[0.0, 1.0], [0.0, 0.0]]))
    cs = []
    for k in range(M):
        op = sp.identity(1)
        for m in range(M):
            op = sp.kron(op, Zm if m < k else (low if m == k else I), format="csr")
        cs.append(op)
    return cs


class JW:
    def __init__(self, n):
        self.n = n
        self.M = 3 * n
        self.c = jw_ops(self.M)
        self.cd = [c.T.tocsr() for c in self.c]
        self.num = [self.cd[k] @ self.c[k] for k in range(self.M)]
        self.one = sp.identity(2 ** self.M, format="csr")
        self.vac = np.zeros(2 ** self.M, dtype=complex)
        self.vac[0] = 1

    def birth(self, j):
        x, y, z = j, self.n + 2 * j, self.n + 2 * j + 1
        return (self.one - self.num[x]) @ (self.one + self.cd[y] @ self.cd[z]) + self.num[x] @ (self.cd[y] + self.cd[z])

    def start(self, first=None, signs=None):
        psi = np.zeros_like(self.vac)
        for w in even_words(self.n):
            v = self.vac.copy()
            if signs is None:
                for k in first:
                    if w[k]:
                        v = self.cd[k] @ v
            else:
                for k in sorted(range(self.n), reverse=True):
                    if w[k]:
                        v = self.cd[k] @ v
                v = signs[w] * v
            psi += v
        return psi

    def readers(self, kind="F1"):
        zs, fs = [], []
        for j in range(self.n):
            x, y = j, self.n + 2 * j
            g = lambda k: self.c[k] + self.cd[k]
            gp = lambda k: 1j * (self.cd[k] - self.c[k])
            fs.append(-1j * gp(x) @ g(y) if kind == "F1" else 1j * g(x) @ gp(y))
            zs.append(self.one - 2 * self.num[x])
        return zs, fs

    def expectations(self, psi, zs, fs):
        nrm = np.vdot(psi, psi).real
        out = {}
        for w in E.all_words(self.n):
            v = psi
            for j, letter in enumerate(w):
                if letter == "Z":
                    v = zs[j] @ v
                elif letter == "F":
                    v = fs[j] @ v
            val = np.vdot(psi, v) / nrm
            assert abs(val.imag) < 1e-9
            out[w] = Fraction(round(val.real * 2 ** (3 * self.n))) / 2 ** (3 * self.n)
        return out


@timed("G_c_second_path")
def gate_second_path():
    rng = random.Random(SEED + 1)
    compared, bad = 0, 0
    for n in (3, 4):
        J = JW(n)
        F = E.Modes(n)
        zs, fs = J.readers("F1")
        R = E.Readers(F, ["F1"] * n)
        words = E.all_words(n)
        sigmas = [tuple(range(n)), tuple(reversed(range(n))), tuple(rng.sample(range(n), n))]
        births = [J.birth(j) for j in range(n)]
        for sigma in sigmas:
            base_j = J.start(first=sigma)
            base_e = E.start(F, sigma)
            for pi in permutations(range(n)):
                v = base_j
                for j in pi:
                    v = births[j] @ v
                ej = J.expectations(v, zs, fs)
                ee = E.expectations(E.grow(F, base_e, pi), R, words)
                compared += 1
                bad += ej != ee
    # P5 at n = 3
    J, F = JW(3), E.Modes(3)
    zs, fs = J.readers("F1")
    R = E.Readers(F, ["F1"] * 3)
    births = [J.birth(j) for j in range(3)]
    for signs in sign_patterns(3):
        for pi in permutations(range(3)):
            v = J.start(signs=signs)
            for j in pi:
                v = births[j] @ v
            ej = J.expectations(v, zs, fs)
            ee = E.expectations(E.grow(F, E.start(F, None, signs), pi), R, E.all_words(3))
            compared += 1
            bad += ej != ee
    return {"tables_compared": compared, "disagreements": int(bad), "held": bad == 0}


def block_listing(n):
    return [m for j in range(n) for m in (j, n + 2 * j, n + 2 * j + 1)]


@timed("G_d_listing_gauge")
def gate_listing():
    rng = random.Random(SEED + 2)
    out = {}
    for n, sigmas, kinds in ((3, [(0, 1, 2), (2, 1, 0)], ("F1", "F2")), (4, [(0, 1, 2, 3)], ("F1",))):
        M = 3 * n
        listings = {"ascending": list(range(M)), "block": block_listing(n), "reversed": list(reversed(range(M)))}
        for k in range(20):
            listings[f"random_{k}"] = rng.sample(range(M), M)
        words = E.all_words(n)
        ref = None
        bad = 0
        tables = 0
        engines = {ln: E.Modes(n, l) for ln, l in listings.items()}
        for sigma in sigmas:
            for kind in kinds:
                for pi in permutations(range(n)):
                    ref = None
                    for ln, F in engines.items():
                        e = E.expectations(E.grow(F, E.start(F, sigma), pi), E.Readers(F, [kind] * n), words)
                        tables += 1
                        if ref is None:
                            ref = e
                        elif e != ref:
                            bad += 1
        out[f"n{n}"] = {"listings": len(listings), "tables": tables, "differing": bad}
    out["held"] = all(v["differing"] == 0 for v in out.values() if isinstance(v, dict))
    return out


# ---------------------------------------------------------------- P1: why P7 failed

@timed("P1")
def p1():
    F = E.Modes(3)
    bad = 0
    for b in range(1 << 9):
        v = E.state([b], [1])
        for i, j in permutations(range(3), 2):
            lhs = E.birth(F, i, E.birth(F, j, v))
            rhs = E.birth(F, j, E.birth(F, i, v))
            s = -1 if (b >> i) & 1 and (b >> j) & 1 else 1
            if not same(lhs, E.scale(rhs, s)):
                bad += 1
    identity = {"basis_states": 1 << 9, "failures": bad}
    orders_out = {}
    for n in (3, 4):
        F = E.Modes(n)
        base = E.start(F, tuple(range(n)))
        grown = {pi: E.simplify(E.grow(F, base, pi)) for pi in permutations(range(n))}
        bad = 0
        pairs = 0
        for a, b in combinations(grown, 2):
            pairs += 1
            A, B = grown[a], grown[b]
            if not np.array_equal(A[0], B[0]):
                bad += 1
                continue
            d = differ(a, b)
            for basis, va, vb in zip(A[0], A[1], B[1]):
                k = sum(1 for i, j in d if (basis >> i) & 1 and (basis >> j) & 1)
                if abs(va - (-1) ** k * vb) > 1e-12:
                    bad += 1
                    break
        orders_out[f"n{n}"] = {"pairs_of_orders": pairs, "failures": bad}
    held = identity["failures"] == 0 and all(v["failures"] == 0 for v in orders_out.values())
    return {"commutation_identity": identity, "reordering_sign": orders_out, "held": held}


# ---------------------------------------------------------------- P2: cyclic shifts

@timed("P2")
def p2():
    rng = random.Random(SEED + 3)
    out = {}
    held = True
    corr_store = {}
    for n in (3, 4, 5, 6):
        F = E.Modes(n)
        R = E.Readers(F, ["F1"] * n)
        words = E.all_words(n)
        tgt = TARGET(n)
        sigmas = {"ascending": tuple(range(n)), "descending": tuple(reversed(range(n))),
                  "random": tuple(rng.sample(range(n), n))}
        res = {}
        for sname, sigma in sigmas.items():
            base = E.start(F, sigma)
            carry = []
            cs = {}
            for pi in permutations(range(n)):
                psi = E.grow(F, base, pi)
                c = E.correlations(psi, R)
                cs[pi] = c
                if E.full_contradiction(c):
                    carry.append(pi)
            if sname == "ascending":
                corr_store[n] = cs
            shifts = E.cyclic_shifts(sigma)
            exact = {}
            for k, pi in enumerate(shifts):
                e = E.expectations(E.grow(F, base, pi), R, words)
                exact[name(pi)] = {
                    "fixed_labels": E.matches(e, tgt),
                    "after_relabelling_moved": E.matches(e, tgt, frozenset(sigma[:k])),
                }
            ok = (set(carry) == set(shifts) and exact[name(sigma)]["fixed_labels"]
                  and all(v["after_relabelling_moved"] for v in exact.values()))
            held &= ok
            res[sname] = {"sigma": name(sigma), "orders": math.factorial(n), "carrying": len(carry),
                          "carrying_orders": sorted(name(p) for p in carry), "shifts": exact, "held": ok}
        out[f"n{n}"] = res
    out["held"] = held
    return out, corr_store


# ---------------------------------------------------------------- P3 and P4: schedules

def schedule_class(rel, n):
    return {"F1": E.is_cut(rel ^ E.complete(n), n), "F3": E.is_cut(rel, n)}


@timed("P3")
def p3():
    rng = random.Random(SEED + 4)
    out = {}
    held = True
    for n, sample in ((3, None), (4, None), (5, 2000)):
        F = E.Modes(n)
        RF1 = E.Readers(F, ["F1"] * n)
        RF3 = E.Readers(F, ["F3"] * n)
        alls = E.schedules(n)
        todo = alls if sample is None else rng.sample(alls, sample)
        bad = {"F1": 0, "F3": 0}
        carry = {"F1": 0, "F3": 0}
        for s in todo:
            psi = E.scheduled(F, s)
            rel = E.crossing(s, n)
            want = schedule_class(rel, n)
            for kind, R in (("F1", RF1), ("F3", RF3)):
                got = carrying(psi, R)
                carry[kind] += got
                bad[kind] += got != want[kind]
        held &= bad["F1"] == 0 and bad["F3"] == 0
        out[f"n{n}"] = {"schedules": len(alls), "checked": len(todo), "disagreements": bad, "carrying_checked": carry}
    out["held"] = held
    return out


def count_schedule_classes(n):
    """Exact counts over every schedule of the crossing relation's class, by enumeration with the relation built as it goes."""
    counts = {"total": 0, "F1": 0, "F3": 0}
    comp = E.complete(n)
    cls_cache = {}

    def classify(rel):
        key = frozenset(rel)
        if key not in cls_cache:
            cls_cache[key] = schedule_class(set(key), n)
        return cls_cache[key]

    def rec(t, start, ended, rel):
        if len(ended) == n:
            c = classify(rel)
            counts["total"] += 1
            counts["F1"] += c["F1"]
            counts["F3"] += c["F3"]
            return
        for j in range(n):
            if j not in start:
                rec(t + 1, {**start, j: t}, ended, rel)
            elif j not in ended:
                add = set()
                for i in range(n):
                    if i == j or i not in start:
                        continue
                    ci = start[i]
                    inside_c = ci > start[j]
                    if inside_c and i not in ended:
                        add.add((min(i, j), max(i, j)))
                    elif not inside_c and i in ended and ended[i] > start[j]:
                        add.add((min(i, j), max(i, j)))
                rec(t + 1, start, {**ended, j: t}, rel | add)

    rec(0, {}, {}, frozenset())
    return counts


@timed("P3_shares")
def p3_shares():
    out = {}
    t5 = 0.0
    for n in (3, 4, 5):
        t = time.time()
        c = count_schedule_classes(n)
        t5 = time.time() - t
        assert c["total"] == math.factorial(2 * n) // 2 ** n
        out[f"n{n}"] = {**c, "share_F1": str(Fraction(c["F1"], c["total"])), "share_F3": str(Fraction(c["F3"], c["total"])),
                        "method": "every schedule"}
    total6 = math.factorial(12) // 2 ** 6
    estimate = t5 * total6 / (math.factorial(10) // 2 ** 5)
    if estimate < 600:
        c = count_schedule_classes(6)
        out["n6"] = {**c, "share_F1": str(Fraction(c["F1"], c["total"])), "share_F3": str(Fraction(c["F3"], c["total"])),
                     "method": f"every schedule (timed estimate {estimate:.0f} s)"}
    else:
        rng = random.Random(SEED + 6)
        f1 = f3 = 0
        m = 200000
        for _ in range(m):
            events = list(range(12))
            rng.shuffle(events)
            seen, sched = set(), []
            for e in events:
                j = e // 2
                sched.append(("b", j) if j in seen else ("c", j))
                seen.add(j)
            cls = schedule_class(E.crossing(sched, 6), 6)
            f1 += cls["F1"]
            f3 += cls["F3"]
        out["n6"] = {"total": total6, "sampled": m, "F1": f1, "F3": f3, "share_F1": f1 / m, "share_F3": f3 / m,
                     "method": f"seeded sample (timed estimate {estimate:.0f} s for every schedule)"}
    return out


@timed("P4")
def p4():
    out = {}
    held = True
    for n in (3, 4, 5):
        F = E.Modes(n)
        RF1 = E.Readers(F, ["F1"] * n)
        RF3 = E.Readers(F, ["F3"] * n)
        f1 = f3 = 0
        for sigma in permutations(range(n)):
            psi = E.scheduled(F, E.depth_first(sigma))
            f1 += carrying(psi, RF1)
            f3 += carrying(psi, RF3)
        ok = f1 == 0 and f3 == math.factorial(n)
        held &= ok
        out[f"n{n}"] = {"sigmas": math.factorial(n), "carrying_F1": f1, "carrying_F3": f3, "held": ok}
    out["held"] = held
    return out


# ---------------------------------------------------------------- P5: start signs

def sign_patterns(n):
    ws = even_words(n)
    rest = ws[1:]
    for bits in product((1, -1), repeat=len(rest)):
        yield {ws[0]: 1, **dict(zip(rest, bits))}


def polar(f, ws):
    zero = tuple([0] * len(ws[0]))
    add = lambda a, b: tuple(x ^ y for x, y in zip(a, b))
    return {(a, b): (f[add(a, b)] + f[a] + f[b] + f[zero]) % 2 for a in ws for b in ws}


def is_quadratic(f, ws):
    B = polar(f, ws)
    add = lambda a, b: tuple(x ^ y for x, y in zip(a, b))
    return all(B[(add(a, b), c)] == (B[(a, c)] + B[(b, c)]) % 2 for a in ws for b in ws for c in ws)


def predicted_start_signs(signs, n):
    """By the formula: logical sign h(x) (-1)^inv_pi(x), carrying iff quadratic with polar form the dot product."""
    ws = even_words(n)
    f = {w: 0 if signs[w] == 1 else 1 for w in ws}
    carry, exact = [], []
    dot = {(a, b): sum(x * y for x, y in zip(a, b)) % 2 for a in ws for b in ws}
    for pi in permutations(range(n)):
        inv = inversions(pi)
        q = {w: (f[w] + sum(w[i] * w[j] for i, j in inv)) % 2 for w in ws}
        if is_quadratic(q, ws) and polar(q, ws) == dot:
            carry.append(pi)
            if all(q[w] == (sum(w) * (sum(w) - 1) // 2) % 2 for w in ws):
                exact.append(pi)
    return carry, exact


@timed("P5")
def p5():
    out = {}
    # n = 3
    F = E.Modes(3)
    R = E.Readers(F, ["F1"] * 3)
    tgt = TARGET(3)
    rule_bad, with_exact = 0, 0
    anchor = None
    for signs in sign_patterns(3):
        has_exact = False
        for pi in permutations(range(3)):
            psi = E.grow(F, E.start(F, None, signs), pi)
            got = carrying(psi, R)
            want = signs[(1, 1, 0)] * signs[(1, 0, 1)] * signs[(0, 1, 1)] * sgn(pi) == -1
            rule_bad += got != want
            if got and E.matches(E.expectations(psi, R, E.all_words(3)), tgt):
                has_exact = True
            if [signs[w] for w in even_words(3)] == [1, -1, -1, -1] and pi == (0, 1, 2):
                anchor = {"carries": got, "exact": E.matches(E.expectations(psi, R, E.all_words(3)), tgt)}
        with_exact += has_exact
    out["n3"] = {"patterns": 8, "rule_failures": rule_bad, "patterns_with_exact_order": with_exact, "anchor": anchor,
                 "held": rule_bad == 0 and with_exact == 6 and anchor == {"carries": True, "exact": True}}
    # n = 4: prediction by the formula first, then the runs
    pats = list(sign_patterns(4))
    predicted = [predicted_start_signs(s, 4) for s in pats]
    F = E.Modes(4)
    R = E.Readers(F, ["F1"] * 4)
    tgt = TARGET(4)
    observed = []
    for signs in pats:
        base = E.start(F, None, signs)
        carry, exact = [], []
        for pi in permutations(range(4)):
            psi = E.grow(F, base, pi)
            if carrying(psi, R):
                carry.append(pi)
                if E.matches(E.expectations(psi, R, E.all_words(4)), tgt):
                    exact.append(pi)
        observed.append((carry, exact))
    with_carry = sum(1 for c, _ in observed if c)
    one_class = all((not c) or (len(c) == 4 and set(c) == set(E.cyclic_shifts(c[0]))) for c, _ in observed)
    with_exact = sum(1 for _, x in observed if x)
    same_as_formula = all(set(o[0]) == set(p[0]) and set(o[1]) == set(p[1]) for o, p in zip(observed, predicted))
    out["n4"] = {"patterns": len(pats), "with_carrying_orders": with_carry, "each_one_cyclic_class": one_class,
                 "with_exact_order": with_exact, "observed_equals_formula": same_as_formula,
                 "formula_with_carrying": sum(1 for c, _ in predicted if c),
                 "held": with_carry == 48 and one_class and with_exact == 24 and same_as_formula}
    out["held"] = out["n3"]["held"] and out["n4"]["held"]
    return out


# ---------------------------------------------------------------- P6: swap rules (listing model, one knot)

def qubit_correlations(amp, n):
    ws = list(amp)
    norm = sum(abs(a) ** 2 for a in amp.values())
    out = {}
    for T in E.even_sets(n):
        total = 0
        for w in ws:
            v = tuple(b ^ (1 if j in T else 0) for j, b in enumerate(w))
            ph = (-1) ** sum(w[j] for j in range(n) if j not in T)
            total += np.conj(amp.get(v, 0)) * ph * amp[w]
        out[T] = total / norm
    return out


def full_float(c, tol=1e-9):
    if not all(abs(abs(v) - 1) < tol and abs(complex(v).imag) < tol for v in c.values()):
        return False
    r = {T: round(complex(v).real) for T, v in c.items()}
    f = {T: r[T] * r[frozenset()] for T in r}
    return not all(f[T ^ U] == f[T] * f[U] for T in r for U in r)


@timed("P6")
def p6():
    out = {}
    held = True
    rules = list(product((1, -1), repeat=3))  # (c00, c01, c11)
    for n in (3, 4, 5, 6):
        ws = even_words(n)
        sets = {}
        for rule in rules:
            c00, c01, c11 = rule
            cost = {(0, 0): c00, (0, 1): c01, (1, 0): c01, (1, 1): c11}
            carry = []
            for L in permutations(range(n)):
                inv = inversions(L)
                amp = {w: math.prod(cost[(w[i], w[j])] for i, j in inv) for w in ws}
                c = qubit_correlations(amp, n)
                if full_float(c):
                    carry.append(L)
            sets[rule] = set(carry)
        fermion = sets[(1, 1, -1)]
        ok = all((sets[r] == fermion) if r[0] * r[2] == -1 else (not sets[r]) for r in rules)
        held &= ok and len(fermion) == n
        out[f"n{n}"] = {"fermion_rule_carrying": len(fermion), "rules": {f"c00={r[0]},c01={r[1]},c11={r[2]}": len(sets[r])
                                                                       for r in rules}, "held": ok}
    # phase family
    phase = {}
    for n in (3, 4, 5, 6):
        ws = even_words(n)
        hits = {}
        for k in range(24):
            s = complex(math.cos(k * math.pi / 12), math.sin(k * math.pi / 12))
            cnt = 0
            for L in permutations(range(n)):
                inv = inversions(L)
                amp = {w: s ** sum(w[i] * w[j] for i, j in inv) for w in ws}
                cnt += full_float(qubit_correlations(amp, n))
            hits[k] = cnt
        ok = all((hits[k] > 0) == (k == 12) for k in hits)
        held &= ok
        phase[f"n{n}"] = {"theta_k_pi_over_12_with_carrying_listings": {str(k): v for k, v in hits.items() if v},
                          "held": ok}
    mermin = {}
    ok3 = True
    for k in range(24):
        th = k * math.pi / 12
        s = complex(math.cos(th), math.sin(th))
        inv = inversions((2, 1, 0))
        amp = {w: s ** sum(w[i] * w[j] for i, j in inv) for w in even_words(3)}
        c = qubit_correlations(amp, 3)
        best = max(abs((c[frozenset()] - sum(c[frozenset(p)] * (-1) ** (u[p[0]] + u[p[1]])
                                             for p in ((0, 1), (0, 2), (1, 2)))).real)
                   for u in product((0, 1), repeat=3))
        want = 1 + 3 * (1 - math.cos(th)) / 2
        ok3 &= abs(best - want) < 1e-9 and ((best > 2 + 1e-12) == (math.cos(th) < 1 / 3 - 1e-12))
        mermin[str(k)] = round(best, 12)
    held &= ok3
    out["phase_family"] = phase
    out["reversal_best_mermin_n3"] = {"by_k": mermin, "formula_and_threshold_held": ok3}
    out["held"] = held
    return out


# ---------------------------------------------------------------- P7: weightings of orders

@timed("P7")
def p7(corr_store):
    out = {}
    held = True
    for n in (3, 4, 5, 6):
        F = E.Modes(n)
        cs = corr_store[n]
        carry = sum(1 for c in cs.values() if E.full_contradiction(c))
        avg = {T: sum(c[T] for c in cs.values()) / len(cs) for T in cs[tuple(range(n))]}
        sharp = all(abs(v) == 1 for v in avg.values())
        base = E.start(F, tuple(range(n)))
        coh = E.add(*[E.grow(F, base, pi) for pi in permutations(range(n))])
        old = sorted({tuple((b >> k) & 1 for k in range(n)) for b in coh[0]})
        ok = carry == n and not sharp and old == [tuple([0] * n)]
        held &= ok
        out[f"n{n}"] = {"carrying": carry, "orders": len(cs), "share": str(Fraction(carry, len(cs))),
                        "mixture_all_sharp": sharp, "coherent_sum_old_words": ["".join(map(str, w)) for w in old],
                        "held": ok}
    joint = {}
    for n in (3, 4):
        F = E.Modes(n)
        R = E.Readers(F, ["F1"] * n)
        cnt = 0
        for sigma in permutations(range(n)):
            base = E.start(F, sigma)
            for pi in permutations(range(n)):
                cnt += carrying(E.grow(F, base, pi), R)
        tot = math.factorial(n) ** 2
        ok = Fraction(cnt, tot) == Fraction(n, math.factorial(n))
        held &= ok
        joint[f"n{n}"] = {"pairs": tot, "carrying": cnt, "share": str(Fraction(cnt, tot)), "held": ok}
    out["joint_sigma_pi"] = joint
    out["held"] = held
    return out


# ---------------------------------------------------------------- P8: reader conventions

def left_creator(pair):
    return "y" if pair == "yz" else "z"


def is_matched(pair, record, kind):
    return (kind == "F1") == (record == left_creator(pair))


@timed("P8")
def p8():
    rng = random.Random(SEED + 5)
    out = {}
    held = True
    per_reader = list(product(("yz", "zy"), ("y", "z"), ("F1", "F2")))
    for n, sigmas, sample in ((3, [(0, 1, 2), (2, 1, 0)], None), (4, [(0, 1, 2, 3)], 256)):
        F = E.Modes(n)
        tgt = TARGET(n)
        words = E.all_words(n)
        assignments = list(product(per_reader, repeat=n))
        matched = [a for a in assignments if all(is_matched(*r) for r in a)]
        unmatched = [a for a in assignments if not all(is_matched(*r) for r in a)]
        if sample is not None:
            unmatched = rng.sample(unmatched, sample)
        todo = matched + unmatched
        fails = {"matched_carrying": 0, "unmatched_carrying": 0, "exact_rule": 0}
        exact_present = 0
        for sigma in sigmas:
            for a in todo:
                pairs = [r[0] for r in a]
                R = E.Readers(F, [r[2] for r in a], [r[1] for r in a])
                base = E.start(F, sigma)
                carry, exact = [], []
                for pi in permutations(range(n)):
                    psi = E.grow(F, base, pi, pairs)
                    if carrying(psi, R):
                        carry.append(pi)
                        if E.matches(E.expectations(psi, R, words), tgt):
                            exact.append(pi)
                if a in matched:
                    fails["matched_carrying"] += set(carry) != set(E.cyclic_shifts(sigma))
                    M = frozenset(j for j, r in enumerate(a) if r[2] == "F2")
                    comp = frozenset(range(n)) - M
                    want = [tuple(sigma[k:]) + tuple(sigma[:k]) for k in range(n)
                            if frozenset(sigma[:k]) in (M, comp)]
                    fails["exact_rule"] += set(exact) != set(want)
                    exact_present += bool(exact)
                else:
                    fails["unmatched_carrying"] += bool(carry)
        ok = all(v == 0 for v in fails.values())
        held &= ok
        out[f"n{n}"] = {"assignments_run": len(todo), "matched": len(matched), "sigmas": [name(s) for s in sigmas],
                        "failures": fails, "matched_runs_with_an_exact_order": exact_present, "held": ok}
    f3 = {}
    for n in (3, 4, 5, 6):
        F = E.Modes(n)
        R = E.Readers(F, ["F3"] * n)
        sigma = tuple(range(n))
        base = E.start(F, sigma)
        carry = [pi for pi in permutations(range(n)) if carrying(E.grow(F, base, pi), R)]
        ok = set(carry) == set(E.cyclic_shifts(tuple(reversed(sigma))))
        if n in (3, 4):
            held &= ok
        f3[f"n{n}"] = {"carrying": sorted(name(p) for p in carry), "held": ok, "registered": n in (3, 4)}
    out["F3_all_readers"] = f3
    out["held"] = held
    return out


def plain(o):
    return o.item() if hasattr(o, "item") else str(o)


def main():
    t0 = time.time()
    OUT["gate"] = {"a_replay": gate_replay(), "b_anticommutation": gate_car(), "c_second_path": gate_second_path(),
                   "d_listing_gauge": gate_listing()}
    OUT["gate"]["held"] = all(v["held"] for v in OUT["gate"].values())
    if not OUT["gate"]["held"]:
        print("GATE FAILED", json.dumps(OUT["gate"], indent=1))
    OUT["P1"] = p1()
    OUT["P2"], corr_store = p2()
    OUT["P3"] = p3()
    OUT["P3"]["shares_uniform_over_schedules"] = p3_shares()
    OUT["P4"] = p4()
    OUT["P5"] = p5()
    OUT["P6"] = p6()
    OUT["P7"] = p7(corr_store)
    OUT["P8"] = p8()
    OUT["timings_seconds"] = TIMES
    OUT["total_seconds"] = round(time.time() - t0, 1)
    (HERE / "results.json").write_text(json.dumps(OUT, indent=1, sort_keys=True, default=plain) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("held") if isinstance(v, dict) else v for k, v in OUT.items()}, indent=1, default=plain))


if __name__ == "__main__":
    main()
