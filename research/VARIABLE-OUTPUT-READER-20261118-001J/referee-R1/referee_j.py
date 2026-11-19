"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001J (own code, on the referee's 001F-R1 machinery: shore-enumerated bond tables,
exact twin-quotient isometries, the census; histories are read from search.json and frontier.json as data; ring_tie.py is the
separate labelled cross-check of RING-READ's reader).

  ../../../.venv/bin/python -B referee_j.py <part> [args] > referee_j_<part>.json      (from this directory)

Parts:
  event21   the nine-junction seven-to-six event: both histories replayed under the referee's law, the legal triples before and
            after, the six loose distinctions as a bond; the reachable comparator with a real six-place junction on the same six:
            internal pair agreement, entries changed, and the cutoffs at which an isometry of the clipped tables exists.
  sharp25   the 25-distinction swap (19 20): family membership, agreement through each cutoff, the mark's two verdicts.
  family W  the all-size theorem exhaustively at widths 15..W: every type with a family history (ternary seed, the first two
            additions unary with three fresh, every later addition two- or three-parent with two fresh) against every reachable
            type of its width, clipped through K = 5 (the theorem) and K = 4 (one below).
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001G/referee-R1"))
import referee_f as F  # noqa: E402
import referee_g as RG  # noqa: E402

FAM = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six"


def table_of(J):
    n = 1 + max(max(S) for S in J)
    return F.bond_table(J, n)[0], n


def first_isometric_failure(K1, K2):
    out = {}
    for L in range(3, 12):
        out[L] = F.isometric(F.clip(K1, L), F.clip(K2, L)) is not None
    return out


def part_event21():
    ev = json.load(open(FAM / "search.json"))["events"][0]
    out = {}
    for side in ("before", "after"):
        steps = [h["support"] for h in ev[side]["history"]]
        J, legal, T, s = RG.replay(steps)
        K, n = table_of(J)
        loose = sorted(x for x in range(n) if sum(x in S for S in J) == 1)
        out[side] = {"width": n, "junctions": len(J), "history legal": legal, "legal triples": len(F.legal_triples(T, J)),
                     "loose distinctions": loose}
        if side == "after":
            w = sum(1 << x for x in loose)
            basis = {}
            for S in J:
                r = sum(1 << x for x in S)
                while r:
                    p = r.bit_length() - 1
                    if p not in basis:
                        basis[p] = r
                        break
                    r ^= basis[p]
            x = w
            while x:
                p = x.bit_length() - 1
                if p not in basis:
                    break
                x ^= basis[p]
            out[side]["the loose six are an equation"] = x == 0
            out[side]["their 15 pair minima K"] = sorted(int(K[a][b]) for a, b in itertools.combinations(loose, 2))
            K_after, J_after = K, J
    comp = ev["actual_boundary_as_six_site_comparator"]["actual_six_site"]
    steps = [h["support"] for h in comp["history"]]
    J2, legal2, T2, s2 = RG.replay(steps)
    K2, n2 = table_of(J2)
    six = ev["six_distinction_bond"]
    out["comparator"] = {"width": n2, "junctions": len(J2), "history legal": legal2, "has a junction on exactly the six": sorted(six) in [sorted(S) for S in J2],
                         "internal pairs equal on the same names": sum(int(K_after[a][b]) == int(K2[a][b]) for a, b in itertools.combinations(six, 2)),
                         "full entries changed on the same names": int(sum(K_after[a][b] != K2[a][b] for a in range(n2) for b in range(a + 1, n2))),
                         "an isometry of the clipped tables exists through K =": first_isometric_failure(K_after, K2),
                         "full tables isometric": F.isometric(K_after, K2) is not None}
    return out


def part_sharp25():
    d = json.load(open(FAM / "frontier.json"))["sharp_distance_four"]
    J, legal, T, s = RG.replay(d["junction_supports"])
    K, n = table_of(J)
    fresh = [sum(1 for x in S if all(x not in Q for Q in J[:k])) for k, S in enumerate(J)]
    parents = [len(S) - f for S, f in zip(J, fresh)]
    a, b = d["transposition"]
    p = list(range(n))
    p[a], p[b] = b, a
    K2 = K[p][:, p]
    lt = F.legal_triples(T, J)
    eq = {L: int(sum(F.clip(K, L)[x][y] == F.clip(K2, L)[x][y] for x in range(n) for y in range(x + 1, n))) for L in range(3, 8)}
    return {"width": n, "junctions": len(J), "history legal": legal,
            "in the family (seed; two unary three-fresh; then two- or three-parent two-fresh)":
                fresh[1:3] == [3, 3] and parents[1:3] == [1, 1] and all(f == 2 and q in (2, 3) for f, q in zip(fresh[3:], parents[3:])),
            "pairs": n * (n - 1) // 2, "pairs equal after the swap, clipped through K": eq,
            "legal triples": len(lt), "mark legal": frozenset(d["legal_mark"]) in lt,
            "image legal": frozenset(d["forbidden_image"]) in lt}


def family_history(T):
    n, adj, loose = T
    deg = [bin(x).count("1") for x in adj]
    ar = [deg[i] + loose[i] for i in range(n)]

    def go(order, placed, npar):
        if len(order) == n:
            return list(order)
        k = len(order)                     # this is the (k)th addition after the seed when k >= 1
        for i in range(n):
            if placed >> i & 1:
                continue
            P = [q for q in range(n) if placed >> q & 1 and adj[i] >> q & 1]
            f = ar[i] - len(P)
            if k <= 2:
                if not (len(P) == 1 and f == 3):
                    continue
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
            r = go(order + [i], placed | 1 << i, npar)
            del npar[i]
            if r:
                return r
        return None
    for s in range(n):
        if ar[s] == 3:
            r = go([s], 1 << s, {s: 0})
            if r:
                return r
    return None


def _prep(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    mem = n == 2 * T[0] + 3 and family_history(T) is not None
    return T, mem, {L: F.invariant(F.clip(K, L)) for L in (4, 5)}


def _check(args):
    T, rivals, L = args
    J, n = F.supports(T)
    C = F.clip(F.bond_table(J, n)[0], L)
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
    return {"keeps stars": F.keeps(gens, stars), "keeps triples": F.keeps(gens, lt) if lt else True, "iso": iso, "flips": flips,
            "legal": len(lt), "capped": capped}


def part_family(wmax=23, wmin=15):
    levels = F.census(wmax)
    out = {}
    with Pool(20) as pool:
        for w in range(wmin, wmax + 1):
            rows = pool.map(_prep, levels.get(w, []), chunksize=32)
            mem = [i for i, r in enumerate(rows) if r[1]]
            if not mem:
                continue
            res = {}
            for L in (5, 4):
                bucket = defaultdict(list)
                for i, r in enumerate(rows):
                    bucket[r[2][L]].append(i)
                jobs = [(rows[i][0], [rows[k][0] for k in bucket[rows[i][2][L]] if k != i], L) for i in mem]
                rs = pool.map(_check, jobs, chunksize=1)
                res[f"K through {L}"] = {"family sources": len(mem), "with a legal triple": sum(x["legal"] > 0 for x in rs),
                                         "a clipped symmetry moves a junction support": sum(not x["keeps stars"] for x in rs),
                                         "a clipped symmetry moves a legal triple": sum(not x["keeps triples"] for x in rs),
                                         "rivals with an isometric clipped table": sum(x["iso"] for x in rs),
                                         "... changing a triple verdict": sum(x["flips"] for x in rs), "searches capped": sum(x["capped"] for x in rs)}
            out[f"width {w}"] = res
            print(w, json.dumps(res), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    args = [int(a) for a in sys.argv[2:]]
    print(json.dumps({"event21": part_event21, "sharp25": part_sharp25, "family": part_family}[part](*args), indent=1, default=str))
