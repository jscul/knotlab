"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001K (own code, on the referee's 001F-R1 machinery; histories read from cases.json
and high_check.json as data; no Codex code imported or run).

  ../../../.venv/bin/python -B referee_k.py <part> [args] > referee_k_<part>.json      (from this directory)

The family: a ternary seed; the first two additions unary with three fresh; exactly one further addition with three parents and
three fresh; every other addition two- or three-parent with two fresh (width 2n + 4 for n junctions).

Parts:
  sharp26   the width-26 swap (19 20): family membership, pairs equal through each cutoff, the named entries, the mark's verdicts.
  w28       the width-28 pair: both histories legal, their full tables on the same names, the allowed states that tell them apart,
            the swap (21 22) carrying one to the other, isomorphism as types, the triple menus, the table's symmetry group and
            whether it keeps the junction supports and the allowed states.
  family W  exhaustively at widths 12..W: every type with a family history against every reachable type of its width; through
            K = 6 (D = 5) and K = 5 (D = 4): rivals with isometric clipped tables, clipped symmetries that move a junction support
            or a legal triple, separately for sources with and without a legal triple; and full-table symmetries that move a
            junction support (the width-28 phenomenon) at every width.
"""
import itertools
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001G/referee-R1"))
import referee_f as F  # noqa: E402
import referee_g as RG  # noqa: E402

FAM = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001K/VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh"


def table_of(J):
    n = 1 + max(max(S) for S in J)
    return F.bond_table(J, n)[0], n


def profile(J):
    fresh = [sum(1 for x in S if all(x not in Q for Q in J[:k])) for k, S in enumerate(J)]
    parents = [len(S) - f for S, f in zip(J, fresh)]
    return fresh, parents


def in_family(J):
    fresh, parents = profile(J)
    if fresh[1:3] != [3, 3] or parents[1:3] != [1, 1]:
        return False
    rest = list(zip(fresh[3:], parents[3:]))
    three = [x for x in rest if x[0] == 3]
    return len(three) == 1 and three[0][1] == 3 and all(f == 2 and p in (2, 3) for f, p in rest if f != 3)


def span(rows):
    basis = {}
    for r in rows:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def allowed(J, ones):
    """Does the 0/1 assignment with exactly these one-bits satisfy every junction (even parity on each support)?"""
    return all(len(set(S) & set(ones)) % 2 == 0 for S in J)


def part_sharp26():
    u = json.load(open(FAM / "cases.json"))["live_arms"]["upgraded_late_cap"]
    tt = u["transposition_test"]
    J, legal, T, s = RG.replay([h["support"] for h in u["source"]["history"]])
    K, n = table_of(J)
    a, b = tt["swap"]
    p = list(range(n))
    p[a], p[b] = b, a
    K2 = K[p][:, p]
    eq = {L: int(sum(F.clip(K, L)[x][y] == F.clip(K2, L)[x][y] for x in range(n) for y in range(x + 1, n))) for L in range(3, 9)}
    lt = F.legal_triples(T, J)
    gens, nq, capped, q = F.generators(F.clip(K, 6))
    return {"width": n, "history legal": legal, "in the family": in_family(J), "pairs": n * (n - 1) // 2,
            "pairs equal after the swap, clipped through K": eq,
            "K(10, 19), K(10, 20)": [int(K[10][19]), int(K[10][20])],
            "legal triples": sorted(sorted(t) for t in lt), "mark legal": frozenset(tt["legal_mark"]) in lt,
            "image legal": frozenset(tt["forbidden_image"]) in lt,
            "every symmetry of the table through K = 6 keeps the menu": F.keeps(gens, lt),
            "every symmetry of the table through K = 6 keeps the junction supports": F.keeps(gens, {frozenset(S) for S in J})}


def part_w28():
    d = json.load(open(FAM / "high_check.json"))
    prefix = d["prefix_junctions"]
    out = {}
    sides = []
    for tr in d["transition"]:
        steps = prefix + [tr["cap_inputs"] + tr["cap_outputs"]]
        J, legal, T, s = RG.replay(steps)
        K, n = table_of(J)
        sides.append((J, T, K, n))
    (J1, T1, K1, n1), (J2, T2, K2, n2) = sides
    ones1, ones2 = d["one_state_per_side_given_by_its_one_bits"]
    sw = {21: 22, 22: 21}
    out["widths"] = [n1, n2]
    out["both histories legal and in the family"] = [in_family(J1), in_family(J2)]
    out["full tables equal on the same names (all pairs)"] = bool((K1 == K2).all())
    out["pairs"] = n1 * (n1 - 1) // 2
    out["state with ones at 11, 12, 14, 21: allowed in history 1 / 2"] = [allowed(J1, ones1), allowed(J2, ones1)]
    out["state with ones at 11, 12, 14, 22: allowed in history 1 / 2"] = [allowed(J1, ones2), allowed(J2, ones2)]
    out["parity-check spaces equal"] = sorted(span([sum(1 << x for x in S) for S in J1]).items()) == sorted(span([sum(1 << x for x in S) for S in J2]).items())
    out["the swap (21 22) carries history 1's supports onto history 2's"] = {frozenset(sw.get(x, x) for x in S) for S in J1} == {frozenset(S) for S in J2}
    out["isomorphic as types"] = nx.is_isomorphic(F.graph(T1), F.graph(T2), node_match=F.nm)
    out["legal triples (history 1, 2)"] = [len(F.legal_triples(T1, J1)), len(F.legal_triples(T2, J2))]
    gens, nq, capped, q = F.generators(K1)
    stars = {frozenset(S) for S in J1}
    out["full-table symmetries: generators keep the junction supports"] = F.keeps(gens, stars)
    moving = [g for g in gens if {frozenset(g[x] for x in S) for S in J1} != stars]
    out["a generator that moves a support"] = [[x, moving[0][x]] for x in range(n1) if moving[0][x] != x] if moving else None
    out["junction supports that differ between the histories"] = [sorted(S) for S in {frozenset(S) for S in J1} ^ {frozenset(S) for S in J2}]
    return out


def family_history(T):
    n, adj, loose = T
    deg = [bin(x).count("1") for x in adj]
    ar = [deg[i] + loose[i] for i in range(n)]

    def go(order, placed, npar, used3):
        if len(order) == n:
            return list(order) if used3 else None
        k = len(order)
        for i in range(n):
            if placed >> i & 1:
                continue
            P = [q for q in range(n) if placed >> q & 1 and adj[i] >> q & 1]
            f = ar[i] - len(P)
            u3 = used3
            if k <= 2:
                if not (len(P) == 1 and f == 3):
                    continue
            elif len(P) == 3 and f == 3 and not used3:
                u3 = True
            elif not (len(P) in (2, 3) and f == 2):
                continue
            if not all((bin(adj[q] & placed).count("1") - npar[q]) < ar[q] - npar[q] for q in P):
                continue
            A = [adj[q] & placed for q in P]
            if any(not (A[x] & A[y]) for x, y in itertools.combinations(range(len(P)), 2)):
                continue
            if len(P) == 3 and (A[0] & A[1] & A[2]):
                continue
            npar[i] = len(P)
            r = go(order + [i], placed | 1 << i, npar, u3)
            del npar[i]
            if r:
                return r
        return None
    for s in range(n):
        if ar[s] == 3:
            r = go([s], 1 << s, {s: 0}, False)
            if r:
                return r
    return None


def _prep(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    mem = n == 2 * T[0] + 4 and family_history(T) is not None
    return T, mem, {L: F.invariant(F.clip(K, L)) for L in (5, 6)}


def _check(args):
    T, rivals, L = args
    J, n = F.supports(T)
    K = F.bond_table(J, n)[0]
    C = F.clip(K, L)
    gens, nq, capped, q = F.generators(C)
    stars = {frozenset(S) for S in J}
    lt = F.legal_triples(T, J)
    iso = flips = 0
    for R in rivals:
        JR, _ = F.supports(R)
        pm = F.isometric(C, F.clip(F.bond_table(JR, n)[0], L))
        if pm is None:
            continue
        iso += 1
        flips += {frozenset(pm[x] for x in t) for t in lt} != F.legal_triples(R, JR)
    fg, _, _, _ = F.generators(K)
    return {"keeps stars": F.keeps(gens, stars), "keeps triples": F.keeps(gens, lt) if lt else True, "iso": iso, "flips": flips,
            "legal": len(lt), "capped": capped, "full symmetry moves a support": not F.keeps(fg, stars)}


def part_family(wmax=24, wmin=12):
    levels = F.census(wmax)
    out = {}
    with Pool(20) as pool:
        for w in range(wmin, wmax + 1):
            if w % 2:                     # the family's width is 2n + 4
                continue
            rows = pool.map(_prep, levels.get(w, []), chunksize=32)
            mem = [i for i, r in enumerate(rows) if r[1]]
            if not mem:
                continue
            res = {}
            for L in (6, 5):
                bucket = defaultdict(list)
                for i, r in enumerate(rows):
                    bucket[r[2][L]].append(i)
                jobs = [(rows[i][0], [rows[k][0] for k in bucket[rows[i][2][L]] if k != i], L) for i in mem]
                rs = pool.map(_check, jobs, chunksize=1)
                for live in (True, False):
                    sel = [x for x in rs if (x["legal"] > 0) == live]
                    res[f"K through {L}, sources {'with' if live else 'without'} a legal triple"] = {
                        "sources": len(sel),
                        "a clipped symmetry moves a junction support": sum(not x["keeps stars"] for x in sel),
                        "a clipped symmetry moves a legal triple": sum(not x["keeps triples"] for x in sel),
                        "rivals with an isometric clipped table": sum(x["iso"] for x in sel),
                        "... changing a triple verdict": sum(x["flips"] for x in sel),
                        "a full-table symmetry moves a junction support": sum(x["full symmetry moves a support"] for x in sel),
                        "searches capped": sum(x["capped"] for x in sel)}
            out[f"width {w}"] = res
            print(w, json.dumps(res), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    args = [int(a) for a in sys.argv[2:]]
    print(json.dumps({"sharp26": part_sharp26, "w28": part_w28, "family": part_family}[part](*args), indent=1, default=str))
