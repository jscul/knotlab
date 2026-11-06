#!/usr/bin/env python3
"""Checks for CYCLE-TOPS-20261021-001B-P001. The statements are in proof.md.

Laws: the surviving laws of census CYCLE-TOPS-20261021-001A-E001 (five block removals of the Z3 lift, two lifts of K6,
two disjoint unions, parity and the Z3 law), rebuilt here; their tops are read from the census and re-certified.

Checks:
- Tops. Every certificate recorded by the census is re-verified: each coarser proper equivalence of a recorded top is
  broken by a recorded table, and that table is re-verified as a polymorphism.
- Lemma 1. On 300 random systems per law, every reflexive two-variable projection between variables with one range,
  and every fibre-sharing relation of a circuit, is the total relation or lies inside the top.
- Theorem 2. On the same systems, the blur by the tops has the system's free sets, and so does the blur by proper
  reflexive relations collected from earlier systems. On small systems the doubled system T is built: each {v, v'} is a
  circuit, each circuit's copy is a circuit, and T satisfies elimination.
- Corollaries 3 and 4. Tie top images are bijections; knot top images are functional or overlapping at each variable.
- Proposition 5. For both unions, an explicit binary polymorphism (first projection inside each part) breaks every
  equivalence on the whole domain other than equality; J and K4 are not rectangular; no elimination failure appears.
- Proposition 6. Knot ranges of the unions lie in one part; the operation combined from the parts is a polymorphism
  and is Mal'tsev modulo the tops on the knot ranges.

Controls, each of which must be rejected:
- 'reflexive relations lie below the top without composing like cycles' (Z6: x = y mod 2 and mod 3 join to everything);
- 'the top lemma holds without composing like cycles' (Z6: blurring by mod 2 frees the tie x = y mod 3);
- 'tie images are bijections modulo any proper equivalence' (K6 modulo equality, which is finer than its top);
- 'every law that composes like cycles is Mal'tsev on its tops' (parity beside J).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts" / "CYCLE-TOPS-20261021-001A" / "CYCLE-TOPS-20261021-001A-E001_tops_census"
Z3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
G = (0, 1, 2, 2)
LIFT = {t for t in product(range(4), repeat=3) if tuple(G[x] for x in t) in Z3}
NOT_TWO = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in Z3 for w in NOT_TWO}
PAR = {t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0}
J = {(2, 2), (3, 3), (3, 4), (4, 3)}


def laws():
    out = {}
    for name, X in (("L-{}", ()), ("L-{222}", ((2, 2, 2),)), ("L-{223}", ((2, 2, 3),)),
                    ("L-{223,232}", ((2, 2, 3), (2, 3, 2))), ("L-{223,232,322}", ((2, 2, 3), (2, 3, 2), (3, 2, 2)))):
        out[name] = (4, [LIFT - set(X)])
    for a in (0, 1):
        g7 = list(range(6)) + [a]
        out[f"K6 lift at {a}"] = (7, [{t for t in product(range(7), repeat=3) if tuple(g7[x] for x in t) in K6} - {(a, a, a)}])
    out["parity + J"] = (5, [PAR, J])
    out["K4 + Z3"] = (7, [LIFT - {(2, 2, 2)}, {tuple(x + 4 for x in t) for t in Z3}])
    out["parity"] = (2, [PAR])
    out["Z3"] = (3, [Z3])
    return out


def solve(D, rels, n, cons):
    return [a for a in product(range(D), repeat=n) if all(tuple(a[v] for v in vs) in rels[ri] for ri, vs in cons)]


def free_sets(S, n, sizes):
    fr = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            need = 1
            for v in Y:
                need *= sizes[v]
            fr[Y] = len({tuple(s[v] for v in Y) for s in S}) == need
    return fr


def circuits(fr):
    return [Y for Y, f in fr.items() if len(Y) > 1 and not f and all(fr[tuple(x for x in Y if x != w)] for w in Y)]


def elimination_holds(fr):
    cs = circuits(fr)
    return all(not fr[tuple(sorted((set(a) | set(b)) - {e}))] for a, b in combinations(cs, 2) for e in set(a) & set(b))


def is_pol(F, rels, ar=3):
    for R in rels:
        Rl = sorted(R)
        k = len(Rl[0])
        for ts in product(Rl, repeat=ar):
            if tuple(F[tuple(t[i] for t in ts)] for i in range(k)) not in R:
                return False
    return True


def partitions(xs):
    if not xs:
        yield []
        return
    for p in partitions(xs[1:]):
        yield [[xs[0]]] + p
        for i in range(len(p)):
            yield p[:i] + [[xs[0]] + p[i]] + p[i + 1:]


def blur_free(S, n, ranges, rho):
    """Free sets of the blur of S by the relations rho[v] (sets of pairs), relative to the ranges."""
    fr = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            cur = {tuple(s[v] for v in Y) for s in S}
            for i, v in enumerate(Y):
                nbr = {}
                for x, y in rho[v]:
                    nbr.setdefault(x, set()).add(y)
                cur = {t[:i] + (y,) + t[i + 1:] for t in cur for y in nbr[t[i]]}
            need = 1
            for v in Y:
                need *= len(ranges[v])
            fr[Y] = len(cur) == need
    return fr


def run():
    checks, controls, failures = {}, {}, []
    rows = {}
    for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows[r["law"]] = r
    L = laws()

    # tops: re-certify
    tops, cert_ok = {}, {}
    for name, (D, rels) in L.items():
        r = rows[name]
        args = list(product(range(D), repeat=3))
        pool = [dict(zip(args, t)) for t in r["pool"]]
        pol_cache = {}
        tops[name] = {}
        good = True
        for key, blocks in r["tops"].items():
            B = tuple(int(x) for x in key.split(","))
            tops[name][B] = [list(b) for b in blocks]
            if len(B) < 2:
                continue
            if not r["certified"][key]:
                good = False
                continue
            wit = {tuple(sorted(tuple(sorted(b)) for b in w["equivalence"])): w for w in r["certificates"][key]}
            for p in partitions(list(range(len(blocks)))):
                if not 1 < len(p) < len(blocks):
                    continue
                E = tuple(sorted(tuple(sorted(x for i in part for x in blocks[i])) for part in p))
                w = wit.get(E)
                if w is None:
                    good = False
                    continue
                i = w["pool_index"]
                if i not in pol_cache:
                    pol_cache[i] = is_pol(pool[i], rels)
                c = {x: j for j, b in enumerate(E) for x in b}
                (x1, y1), (x2, y2), (x3, y3) = w["pairs"]
                good = good and pol_cache[i] and c[x1] == c[y1] and c[x2] == c[y2] and c[x3] == c[y3] \
                    and c[pool[i][(x1, x2, x3)]] != c[pool[i][(y1, y2, y3)]]
        cert_ok[name] = good
    checks["tops_certified"] = cert_ok
    if not all(cert_ok.values()):
        failures.append("tops")

    # Lemma 1, Theorem 2, Corollaries 3 and 4 on random systems
    stats = {}
    for name, (D, rels) in L.items():
        rng = random.Random(f"B-{name}")
        cls = {B: {x: i for i, b in enumerate(bl) for x in b} for B, bl in tops[name].items()}
        mu = {B: {(x, y) for b in bl for x in b for y in b} for B, bl in tops[name].items()}
        observed = {}
        s = dict.fromkeys(["systems", "lemma1_relations", "lemma1_violations", "blur_tops_mismatch", "blur_random",
                           "blur_random_mismatch", "doubled", "doubled_bad", "ties", "ties_bijective", "knots",
                           "knots_functional", "knots_overlapping", "knots_neither", "elimination_failures"], 0)
        nmax = 5 if D <= 5 else 4
        tries = 0
        while s["systems"] < 300 and tries < 3000:
            tries += 1
            n = rng.randint(2, nmax)
            cons = []
            for _ in range(rng.randint(1, 4)):
                ri = rng.randrange(len(rels))
                cons.append((ri, tuple(rng.randrange(n) for _ in range(len(next(iter(rels[ri])))))))
            S = solve(D, rels, n, cons)
            if not S:
                continue
            ranges = [tuple(sorted({a[v] for a in S})) for v in range(n)]
            if any(B not in tops[name] for B in ranges):
                continue
            s["systems"] += 1
            fr = free_sets(S, n, [len(B) for B in ranges])
            s["elimination_failures"] += not elimination_holds(fr)
            cs = circuits(fr)
            # Lemma 1
            for u, v in combinations(range(n), 2):
                B = ranges[u]
                if B == ranges[v] and len(B) > 1:
                    P = {(a[u], a[v]) for a in S}
                    if all((x, x) in P for x in B):
                        s["lemma1_relations"] += 1
                        if len(P) < len(B) ** 2:
                            observed.setdefault(B, []).append(P)
                            s["lemma1_violations"] += not P <= mu[B]
            for C in cs:
                for i, e in enumerate(C):
                    fib = {}
                    for a in S:
                        fib.setdefault(tuple(a[v] for v in C if v != e), set()).add(a[e])
                    lam = {(x, y) for F in fib.values() for x in F for y in F}
                    B = ranges[e]
                    s["lemma1_relations"] += 1
                    if len(lam) < len(B) ** 2:
                        observed.setdefault(B, []).append(lam)
                        s["lemma1_violations"] += not lam <= mu[B]
            # Theorem 2: blur by the tops, and by observed proper reflexive relations
            s["blur_tops_mismatch"] += blur_free(S, n, ranges, [mu[B] for B in ranges]) != fr
            rho = []
            for B in ranges:
                opts = observed.get(B, [])
                rho.append(rng.choice(opts) if opts and len(B) > 1 else {(x, x) for x in B})
            s["blur_random"] += 1
            s["blur_random_mismatch"] += blur_free(S, n, ranges, rho) != fr
            # the doubled system T on small systems
            if n <= 3 and s["doubled"] < 40:
                s["doubled"] += 1
                T = [a + b for a in S for b in product(*[[y for y in B if (a[v], y) in mu[B]] for v, B in enumerate(ranges)])]
                frT = free_sets(T, 2 * n, [len(B) for B in ranges] * 2)
                csT = set(circuits(frT))
                ok = elimination_holds(frT)
                ok = ok and all((v, v + n) in csT for v in range(n) if len(ranges[v]) > 1 and len(tops[name][ranges[v]]) > 1)
                ok = ok and all(tuple(v + n for v in C) in csT for C in cs)
                s["doubled_bad"] += not ok
            # Corollaries 3 and 4
            T = {tuple(cls[ranges[v]][a[v]] for v in range(n)) for a in S}
            for C in cs:
                img = {tuple(t[v] for v in C) for t in T}
                sizes = [len(tops[name][ranges[v]]) for v in C]
                if len(C) == 2:
                    s["ties"] += 1
                    s["ties_bijective"] += sizes[0] == sizes[1] == len(img) == len({p[0] for p in img}) == len({p[1] for p in img})
                else:
                    s["knots"] += 1
                    kinds = []
                    for i in range(len(C)):
                        fib = {}
                        for t in img:
                            fib.setdefault(t[:i] + t[i + 1:], set()).add(t[i])
                        lam = {(x, y) for F in fib.values() for x in F for y in F}
                        kinds.append("functional" if all(len(F) == 1 for F in fib.values())
                                     else "overlapping" if len(lam) == sizes[i] ** 2 else "neither")
                    s["knots_functional"] += all(k == "functional" for k in kinds)
                    s["knots_overlapping"] += "overlapping" in kinds
                    s["knots_neither"] += "neither" in kinds
        stats[name] = s
    checks["systems"] = stats
    if any(s["systems"] < 150 or s["elimination_failures"] for s in stats.values()):
        failures.append("sampling")
    if any(s["lemma1_violations"] for s in stats.values()):
        failures.append("Lemma 1")
    if any(s["blur_tops_mismatch"] or s["blur_random_mismatch"] or s["doubled_bad"] for s in stats.values()) \
            or not all(s["doubled"] for s in stats.values()):
        failures.append("Theorem 2")
    if any(s["ties_bijective"] != s["ties"] for s in stats.values()):
        failures.append("Corollary 3")
    if any(s["knots_neither"] for s in stats.values()):
        failures.append("Corollary 4")
    checks["knot_images_all_functional"] = all(s["knots_functional"] == s["knots"] for s in stats.values())

    # Proposition 5
    prop5 = {}
    for name, parts in (("parity + J", [(0, 1), (2, 3, 4)]), ("K4 + Z3", [(0, 1, 2, 3), (4, 5, 6)])):
        D, rels = L[name]
        part = {x: i for i, p in enumerate(parts) for x in p}
        broken = total = 0
        for p in partitions(list(range(D))):
            if len(p) in (1, D):
                continue
            total += 1
            c = {x: i for i, b in enumerate(p) for x in b}
            a, b = next((x, y) for blk in p for x in blk for y in blk if x != y)
            f = {(x, y): x for x in range(D) for y in range(D)}
            if part[a] == part[b]:
                cc = parts[1 - part[a]][0]
                u = a
                v = next(z for z in range(D) if c[z] != c[u])
                f[(a, cc)], f[(b, cc)] = u, v
                img = (f[(a, cc)], f[(b, cc)])
            else:
                u = next(z for z in range(D) if c[z] != c[a])
                f[(b, a)] = u
                img = (f[(b, a)], f[(a, a)])
            pol = all(tuple(f[(s1[i], s2[i])] for i in range(len(s1))) in R for R in rels for s1 in R for s2 in R)
            broken += pol and c[img[0]] != c[img[1]]
        nonrect = []
        for R in rels:
            k = len(next(iter(R)))
            bad = False
            for e in range(k):
                fib = {}
                for t in R:
                    fib.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
                fs = list(fib.values())
                bad = bad or any(x != y and x & y for x in fs for y in fs)
            nonrect.append(bad)
        prop5[name] = {"equivalences": total, "broken_by_mixed_polymorphisms": broken, "relations_not_rectangular": nonrect,
                       "census_all_ranges": rows[name]["maltsev_all_ranges"]}
    checks["proposition_5"] = prop5
    if not all(v["broken_by_mixed_polymorphisms"] == v["equivalences"] and any(v["relations_not_rectangular"])
               for v in prop5.values()):
        failures.append("Proposition 5")

    # Proposition 6
    prop6 = {}
    for name, parts, pieces in (("parity + J", [(0, 1), (2, 3, 4)], ["parity", None]),
                                ("K4 + Z3", [(0, 1, 2, 3), (4, 5, 6)], ["L-{222}", "Z3"])):
        D, rels = L[name]
        r = rows[name]
        knot_ranges = [tuple(B) for B in r["knot_ranges"]]
        inside = all(any(set(B) <= set(p) for p in parts) for B in knot_ranges)
        F = {(x, y, z): x for x in range(D) for y in range(D) for z in range(D)}
        for p, piece in zip(parts, pieces):
            if piece is None:
                continue
            Dp = len(p)
            tab = dict(zip(product(range(Dp), repeat=3), rows[piece]["table_knot_ranges"]))
            for (x, y, z), w in tab.items():
                F[(p[x], p[y], p[z])] = p[w]
        cls = {B: {x: i for i, b in enumerate(bl) for x in b} for B, bl in tops[name].items()}
        maltsev = all(cls[B][F[(x, y, y)]] == cls[B][x] and cls[B][F[(x, x, y)]] == cls[B][y]
                      for B in knot_ranges for x in B for y in B)
        same_tops = True
        for B in knot_ranges:
            for p, piece in zip(parts, pieces):
                if piece and set(B) <= set(p):
                    key = ",".join(str(p.index(x)) for x in B)
                    same_tops = same_tops and sorted(sorted(p.index(x) for x in b) for b in tops[name][B]) == \
                        sorted(sorted(b) for b in rows[piece]["tops"][key])
        prop6[name] = {"knot_ranges": knot_ranges, "inside_one_part": inside, "tops_agree_with_part": same_tops,
                       "combined_is_polymorphism": is_pol(F, rels), "combined_maltsev_on_knot_tops": maltsev}
    checks["proposition_6"] = prop6
    if not all(v["inside_one_part"] and v["tops_agree_with_part"] and v["combined_is_polymorphism"]
               and v["combined_maltsev_on_knot_tops"] for v in prop6.values()):
        failures.append("Proposition 6")

    # controls
    Z6 = [{t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}]
    mod3 = {(a[0], a[1]) for a in solve(6, Z6, 3, [(0, (0, 0, 2)), (0, (1, 1, 2))])}
    mod2 = {(a[0], a[1]) for a in solve(6, Z6, 3, [(0, (2, 2, 2)), (0, (0, 1, 2))])}
    parent = list(range(6))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for x, y in mod2 | mod3:
        parent[find(x)] = find(y)
    controls["reflexive_below_top_without_cycles"] = {
        "mod2_and_mod3_proper_reflexive": len(mod2) < 36 and len(mod3) < 36 and all((x, x) in mod2 and (x, x) in mod3 for x in range(6)),
        "join_total": len({find(x) for x in range(6)}) == 1}
    controls["reflexive_below_top_without_cycles"]["rejected"] = all(controls["reflexive_below_top_without_cycles"].values())
    blurred = {(a, b) for x, y in mod3 for a in range(6) for b in range(6) if (a - x) % 2 == 0 and (b - y) % 2 == 0}
    controls["top_lemma_without_cycles"] = {"tie_constrained": len(mod3) < 36, "blur_free": len(blurred) == 36}
    controls["top_lemma_without_cycles"]["rejected"] = all(controls["top_lemma_without_cycles"].values())
    tie = {(a[0], a[1]) for a in solve(6, [K6], 2, [(0, (0, 0, 1))])}
    controls["bijection_modulo_any_equivalence"] = {
        "K6_tie_image_modulo_equality_is_bijection": len(tie) == 6 and len({x for x, _ in tie}) == len({y for _, y in tie}) == 6,
        "K6_tie_image_modulo_first_component_is_bijection": len({(x // 2, y // 2) for x, y in tie}) == 3}
    controls["bijection_modulo_any_equivalence"]["rejected"] = \
        not controls["bijection_modulo_any_equivalence"]["K6_tie_image_modulo_equality_is_bijection"] \
        and controls["bijection_modulo_any_equivalence"]["K6_tie_image_modulo_first_component_is_bijection"]
    controls["every_law_maltsev_on_its_tops"] = {
        "parity_J_whole_domain_top_is_equality": prop5["parity + J"]["broken_by_mixed_polymorphisms"] == prop5["parity + J"]["equivalences"],
        "J_not_rectangular": prop5["parity + J"]["relations_not_rectangular"][1]}
    controls["every_law_maltsev_on_its_tops"]["rejected"] = all(controls["every_law_maltsev_on_its_tops"].values())
    for k, v in controls.items():
        if not v["rejected"]:
            failures.append(f"control not rejected: {k}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
