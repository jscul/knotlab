#!/usr/bin/env python3
"""Independent check of KNOT-IMAGES-20261021-001A-E001. It imports no producer code.

- Each recorded square is checked to be a Latin square; the group-isotope test is recomputed with a loop isotope at a
  different base point; for the named groups the order, associativity, commutativity and number of involutions are
  checked against the name. The other laws are rebuilt here.
- Every failure is re-verified by brute-force enumeration of its system.
- Every collapse is re-verified: the witness relations are recomputed from their systems, each is checked to be
  reflexive and proper on the range, and their join is checked to be the total relation.
- Every operation table is re-verified as a polymorphism with its conditions, and every certificate is re-verified.
- For every law with neither, the hidden-circuit, tie and knot counts are replicated on fresh systems.
- The prediction and control flags are recomputed.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "KNOT-IMAGES-20261021-001A" / HERE.name


def latin(L):
    n = len(L)
    return all(sorted(r) == list(range(n)) for r in L) and all(sorted(c) == list(range(n)) for c in zip(*L))


def isotope_of_group(L):
    """Principal loop isotope based at the last row and column; associative exactly for group isotopes."""
    n = len(L)
    a, b = n - 1, n - 1
    R = {L[x][b]: x for x in range(n)}
    C = {L[a][y]: y for y in range(n)}
    op = lambda x, y: L[R[x]][C[y]]
    return all(op(op(x, y), z) == op(x, op(y, z)) for x in range(n) for y in range(n) for z in range(n))


def group_facts(L):
    n = len(L)
    assoc = all(L[L[x][y]][z] == L[x][L[y][z]] for x in range(n) for y in range(n) for z in range(n))
    ident = all(L[0][x] == x and L[x][0] == x for x in range(n))
    comm = all(L[x][y] == L[y][x] for x in range(n) for y in range(n))
    order = lambda x: next(k for k in range(1, n + 1) if pw(x, k) == 0)
    def pw(x, k):
        r = 0
        for _ in range(k):
            r = L[r][x]
        return r
    return {"group": assoc and ident, "abelian": comm, "involutions": sum(1 for x in range(1, n) if L[x][x] == 0),
            "exponent": max(order(x) for x in range(n)) if assoc and ident else None}


EXPECTED = {"Z2": (2, True, 1, 2), "Z3": (3, True, 0, 3), "Z4": (4, True, 1, 4), "Z2xZ2": (4, True, 3, 2),
            "Z5": (5, True, 0, 5), "Z6": (6, True, 1, 6), "S3": (6, False, 3, 3), "Z7": (7, True, 0, 7),
            "Z8": (8, True, 1, 8), "Z2xZ4": (8, True, 3, 4), "D4": (8, False, 5, 4), "Q8": (8, False, 1, 4)}


def rebuild(row):
    name = row["law"]
    if row["family"] == "3-net":
        L = row["square"]
        n = len(L)
        return [n, n, n], [((0, 1, 2), {(i, j, L[i][j]) for i in range(n) for j in range(n)})]
    if name.startswith("e=x+yH"):
        p = int(name.split("p=")[1].split()[0])
        H = [int(h) for h in name.split("H=")[1].split(",")]
        return [p, p, p], [((0, 1, 2), {(x, y, (x + y * h) % p) for x in range(p) for y in range(p) for h in H})]
    if name == "equality indicator":
        return [2, 3], [((0, 1, 1), {(int(a != b), a, b) for a in range(3) for b in range(3)})]
    if name == "parity":
        return [2], [((0, 0, 0), {t for t in product((0, 1), repeat=3) if t.count(1) % 2 == 0})]
    if name == "neither-knot":
        return [2], [((0, 0, 0), {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)})]
    raise KeyError(name)


def enumerate_system(sizes, rels, sorts, cons):
    return [a for a in product(*[range(sizes[s]) for s in sorts])
            if all(tuple(a[v] for v in vs) in rels[ri][1] for ri, vs in cons)]


def free_map(S, n, sizes=None):
    sz = sizes or [len({s[v] for s in S}) for v in range(n)]
    out = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            need = 1
            for v in Y:
                need *= sz[v]
            out[Y] = len({tuple(s[v] for v in Y) for s in S}) == need
    return out


def minimal(fr):
    return [Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)]


def join_blocks(values, rel):
    comp = {x: x for x in values}

    def root(x):
        while comp[x] != x:
            x = comp[x]
        return x
    for x, y in rel:
        comp[root(x)] = root(y)
    return len({root(x) for x in values})


def is_pol(tables, sizes, rels):
    for sig, R in rels:
        Rl = list(R)
        for t1 in Rl:
            for t2 in Rl:
                for t3 in Rl:
                    if tuple(tables[sig[i]][(t1[i], t2[i], t3[i])] for i in range(len(sig))) not in R:
                        return False
    return True


def tables_of(rec, sizes):
    return [dict(zip(product(range(sizes[s]), repeat=3), rec[s])) for s in range(len(sizes))]


def set_partitions(xs):
    if not xs:
        yield []
        return
    for p in set_partitions(xs[1:]):
        yield [[xs[0]]] + p
        for i in range(len(p)):
            yield p[:i] + [[xs[0]] + p[i]] + p[i + 1:]


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = {}
    for line in (ART / "raw_rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows[r["law"]] = r
    problems, report = [], {"squares": {}, "failures": {}, "collapses": {}, "survivors": {}}

    # squares
    for name, r in rows.items():
        if r["family"] != "3-net":
            continue
        L = r["square"]
        ok = latin(L) and isotope_of_group(L) == r["group_isotope"]
        label = name.split("3-net ")[1]
        if label in EXPECTED:
            f = group_facts(L)
            n, ab, inv, ex = EXPECTED[label]
            ok = ok and f["group"] and len(L) == n and f["abelian"] == ab and f["involutions"] == inv and f["exponent"] == ex
        elif label.startswith("non-group"):
            ok = ok and not r["group_isotope"]
        report["squares"][name] = ok
        if not ok:
            problems.append(f"{name}: square does not match its label")

    # failures and collapses
    for name, r in rows.items():
        sizes, rels = rebuild(r)
        if r["failure"]:
            f = r["failure"]
            sorts, cons = f["sorts"], [(ri, tuple(vs)) for ri, vs in f["constraints"]]
            S = enumerate_system(sizes, rels, sorts, cons)
            fr = free_map(S, len(sorts))
            a, b, e = tuple(f["circuits_and_shared"][0]), tuple(f["circuits_and_shared"][1]), f["circuits_and_shared"][2]
            cs = minimal(fr)
            ok = a in cs and b in cs and e in a and e in b and fr[tuple(sorted((set(a) | set(b)) - {e}))]
            report["failures"][name] = ok
            if not ok:
                problems.append(f"{name}: failure does not verify")
        elif r["collapse"]:
            w = r["collapse_witnesses"]
            srt, values = w["range"][0], w["range"][1]
            union, ok = set(), True
            for src in w["sources"]:
                sorts, cons = src["sorts"], [(ri, tuple(vs)) for ri, vs in src["constraints"]]
                S = enumerate_system(sizes, rels, sorts, cons)
                if "pair" in src:
                    u, v = src["pair"]
                    ok = ok and sorts[u] == sorts[v] == srt and sorted({s[u] for s in S}) == values == sorted({s[v] for s in S})
                    rel = {(s[u], s[v]) for s in S}
                    rel |= {(y, x) for x, y in rel}
                else:
                    C, e = src["circuit"], src["variable"]
                    fr = free_map(S, len(sorts))
                    ok = ok and tuple(C) in minimal(fr) and sorts[e] == srt and sorted({s[e] for s in S}) == values
                    fib = {}
                    for s in S:
                        fib.setdefault(tuple(s[v] for v in C if v != e), set()).add(s[e])
                    rel = {(x, y) for F in fib.values() for x in F for y in F}
                ok = ok and all((x, x) in rel for x in values) and len(rel) < len(values) ** 2
                union |= rel
            ok = ok and join_blocks(values, union) == 1
            report["collapses"][name] = ok
            if not ok:
                problems.append(f"{name}: collapse does not verify")

    # survivors
    for name, r in rows.items():
        if r["failure"] or r["collapse"]:
            continue
        sizes, rels = rebuild(r)
        tops = {}
        for k, blocks in r["tops"].items():
            s, vals = k.split(":")
            tops[(int(s), tuple(int(x) for x in vals.split(",")))] = blocks
        info = {}
        if r.get("table_knot_ranges"):
            T = tables_of(r["table_knot_ranges"], sizes)
            good = is_pol(T, sizes, rels)
            for k in r["knot_ranges"]:
                s, vals = k.split(":")
                B = (int(s), tuple(int(x) for x in vals.split(",")))
                cls = {x: i for i, b in enumerate(tops[B]) for x in b}
                good = good and all(cls[T[B[0]][(x, y, y)]] == cls[x] and cls[T[B[0]][(x, x, y)]] == cls[y]
                                    for x in B[1] for y in B[1])
            info["table"] = good
            if not good:
                problems.append(f"{name}: Mal'tsev table does not verify")
        pool = [tables_of(t, sizes) for t in r.get("pool", [])]
        pol_ok = {}
        for k, ok in r.get("certified", {}).items():
            if not ok:
                continue
            s, vals = k.split(":")
            B = (int(s), tuple(int(x) for x in vals.split(",")))
            blocks = tops[B]
            wit = {tuple(sorted(tuple(sorted(b)) for b in w["equivalence"])): w for w in r["certificates"][k]}
            for p in set_partitions(list(range(len(blocks)))):
                if not 1 < len(p) < len(blocks):
                    continue
                E = tuple(sorted(tuple(sorted(x for i in part for x in blocks[i])) for part in p))
                w = wit.get(E)
                if w is None:
                    problems.append(f"{name}: missing certificate on {k}")
                    continue
                i = w["pool_index"]
                if i not in pol_ok:
                    pol_ok[i] = is_pol(pool[i], sizes, rels)
                c = {x: j for j, b in enumerate(E) for x in b}
                (x1, y1), (x2, y2), (x3, y3) = w["pairs"]
                G = pool[i][B[0]]
                if not (pol_ok[i] and c[x1] == c[y1] and c[x2] == c[y2] and c[x3] == c[y3]
                        and c[G[(x1, x2, x3)]] != c[G[(y1, y2, y3)]]):
                    problems.append(f"{name}: certificate on {k} does not verify")
        # replication on fresh systems
        g = random.Random(f"check-{name}")
        st = dict.fromkeys(["systems", "hidden", "ties", "ties_bijective", "knots", "knots_functional", "elimination_failures"], 0)
        tries = 0
        nmax = 5 if max(sizes) <= 5 else 4
        while st["systems"] < 200 and tries < 3000:
            tries += 1
            sorts, cons = [], []
            for _ in range(g.randint(1, 4)):
                ri = g.randrange(len(rels))
                vs = []
                for s in rels[ri][0]:
                    have = [v for v in range(len(sorts)) if sorts[v] == s]
                    if not have or (len(sorts) < nmax and g.random() < 0.5):
                        sorts.append(s)
                        vs.append(len(sorts) - 1)
                    else:
                        vs.append(g.choice(have))
                cons.append((ri, tuple(vs)))
            S = enumerate_system(sizes, rels, sorts, cons)
            if not S:
                continue
            n = len(sorts)
            keyed = [(sorts[v], tuple(sorted({s[v] for s in S}))) for v in range(n)]
            if any(B not in tops for B in keyed):
                continue
            st["systems"] += 1
            fr = free_map(S, n)
            cs = minimal(fr)
            st["elimination_failures"] += any(fr[tuple(sorted((set(a) | set(b)) - {e}))]
                                              for a, b in combinations(cs, 2) for e in set(a) & set(b))
            cls = [{x: i for i, b in enumerate(tops[keyed[v]]) for x in b} for v in range(n)]
            ntop = [len(tops[keyed[v]]) for v in range(n)]
            T = {tuple(cls[v][s[v]] for v in range(n)) for s in S}
            st["hidden"] += free_map(list(T), n, ntop) != fr
            certified = lambda v: r["certified"].get(f"{keyed[v][0]}:" + ",".join(map(str, keyed[v][1])), True)
            for C in cs:
                img = {tuple(t[v] for v in C) for t in T}
                if len(C) == 2:
                    if certified(C[0]) and certified(C[1]):
                        st["ties"] += 1
                        u, v = C
                        st["ties_bijective"] += ntop[u] == ntop[v] == len(img) == len({p[0] for p in img}) == len({p[1] for p in img})
                else:
                    st["knots"] += 1
                    fun = True
                    for j in range(len(C)):
                        fib = {}
                        for t in img:
                            fib.setdefault(t[:j] + t[j + 1:], set()).add(t[j])
                        fun = fun and all(len(F) == 1 for F in fib.values())
                    st["knots_functional"] += fun
        info.update(st)
        report["survivors"][name] = info
        if st["systems"] < 50:
            problems.append(f"{name}: only {st['systems']} fresh systems replicated")

    # flags
    bad = lambda r: bool(r["failure"] or r["collapse"])
    nets = [r for r in rows.values() if r["family"] == "3-net"]
    surv = [n for n, r in rows.items() if not bad(r) and r["family"] != "control"]
    rep = report["survivors"]
    flags = {
        "H1": all(bad(r) for r in nets if not r["group_isotope"]),
        "H2": all(not bad(rows[f"3-net {g}"]) for g in ("Z2", "Z3", "Z4", "Z2xZ2", "Z5", "Z7", "Z8", "Z2xZ4")) and bad(rows["3-net Z6"]),
        "H2b": bad(rows["3-net S3"]) and bad(rows["3-net D4"]) and not bad(rows["3-net Q8"]),
        "H3": all(bad(r) for r in rows.values() if r["family"] == "overlapping"),
        "H4": all(rows[n]["knots_functional"] == rows[n]["knots"] and rep[n]["knots_functional"] == rep[n]["knots"] for n in surv),
        "H5": all(rows[n]["maltsev_knot_ranges"] == "found" and rep[n].get("table") for n in surv),
        "H6": all(rows[n]["hidden"] == 0 and rows[n]["ties_bijective"] == rows[n]["ties"] and rep[n]["hidden"] == 0
                  and rep[n]["ties_bijective"] == rep[n]["ties"] and rep[n]["elimination_failures"] == 0 for n in surv),
    }
    for h, v in flags.items():
        if v != result["predictions"][h]:
            problems.append(f"{h}: recorded {result['predictions'][h]}, recomputed {v}")
    g1 = rows["3-net non-group 5"]
    controls = {
        "C1_parity": not bad(rows["parity"]) and rows["parity"]["maltsev_knot_ranges"] == "found" and rep["parity"].get("table", False),
        "C2_neither_knot_fails": bool(rows["neither-knot"]["failure"]) and report["failures"].get("neither-knot", False),
        "C3_non_group_5_fails_on_the_shared_diagonal": bool(g1["failure"]) and g1["failure"]["source"] == "shared diagonal"
        and report["failures"].get("3-net non-group 5", False),
        "C4_Z6_collapses": bad(rows["3-net Z6"]) and (report["collapses"].get("3-net Z6", False) or report["failures"].get("3-net Z6", False)),
    }
    for c, v in controls.items():
        if v != result["controls"][c]:
            problems.append(f"{c}: recorded {result['controls'][c]}, recomputed {v}")
    report["flags"], report["controls"] = flags, controls
    status = "passed: every square, failure, collapse, table, certificate and flag agrees, and the replication agrees (V1, exploratory evidence only)" \
        if not problems else "failed"
    text = json.dumps(report, indent=1, sort_keys=True, default=str) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text[-2500:])
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
