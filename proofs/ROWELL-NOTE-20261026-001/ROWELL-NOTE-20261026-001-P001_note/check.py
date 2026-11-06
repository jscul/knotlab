"""Check for ROWELL-NOTE-20261026-001-P001, the note on #P-hard knot-group counting for solvable targets.

1. The replay: replay_result.json (written by replay.py) must show all ten cited checks rerun in a temporary copy,
   passing, and equal to their frozen results outside timing fields; links/links_result.json (written by
   links/run_all.py) must show every link check passing, and the logs must contain the end-to-end link reductions.
2. The numbers the note quotes from the cited proofs are found in the fresh replayed results.
3. The small facts the note derives itself are recomputed here: the 12-state gadget algebra, the Tutte points, the
   group orders and derived lengths, the smallest hard-pair groups, the twist-knot roots, and
   H_K(SL(2,3)) = 2 H_K(A4) on four knots.
4. The note compiles without errors or undefined references, and every quoted number occurs in its source.
5. Tampering controls.

Standard library only. Run: python3 -B check.py [--write]   (run replay.py --write first)
"""
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTE = HERE / "note" / "rowell_note.tex"
ROOT = HERE.parents[2]


# ---------- 1-2. the replay and the quoted numbers ----------

def load_replay():
    return json.loads((HERE / "replay_result.json").read_text())


def replay_ok(rep):
    rows = rep["rows"]
    return (rep["ok"] and len(rows) == 10
            and all(r["exit_code"] == 0 and r["matches_frozen_result"] and r["fresh_status"] == "Proved" for r in rows))


def fresh(rep, ticket, part):
    for r in rep["rows"]:
        if r["ticket"] == ticket:
            return r["fresh_checks"][part]
    raise KeyError(ticket)


def quoted_numbers(rep):
    out = {}
    e2e = fresh(rep, "CORRECTIONS-20261026-001D", "3_end_to_end")["rows"]
    out["F4 triangle N"] = sorted({v["N"] for k, v in e2e.items() if k.startswith("triangle") and v["ok"]})
    out["F4 digon N"] = sorted({v["N"] for k, v in e2e.items() if k.startswith("digon") and v["ok"]})
    e2e = fresh(rep, "COPRIME-CLASS2-20261026-001D", "3_end_to_end")["rows"]
    for pat in ("pattern 2", "pattern 3", "pattern 4"):
        out[f"odd p {pat} N"] = sorted({v["N"] for k, v in e2e.items() if pat in k and v["ok"] and v["N"] == v["gadget value"]})
    kg = fresh(rep, "CORRECTIONS-20261026-001D", "5_knot_groups")["rows"]
    out["knot group minus surgery"] = sorted({v["difference"] for v in kg.values() if v["ok"]})
    s4 = fresh(rep, "SL23-BOUNDED-20261025-001B", "2_knots")["rows"]
    out["S4 split 4+R+2T holds"] = all(v["|Hom(pi,S4)|"] == v["4 + R + 2T"] for v in s4.values())
    out["double covers twice S4"] = all(v["|Hom(pi,GL(2,3))|"] == 2 * v["|Hom(pi,S4)|"] == v["|Hom(pi,2O)|"] for v in s4.values())
    bf = fresh(rep, "CORRECTIONS-20261026-001A", "2_brute_force")["rows"]
    out["1+128 4^d N = brute force"] = all(v["1 + 128 4^d N"] == v["brute force"] for v in bf.values())
    return out


EXPECTED = {
    "F4 triangle N": [45162496], "F4 digon N": [326656],
    "odd p pattern 2 N": [3240625], "odd p pattern 3 N": [46101601], "odd p pattern 4 N": [25925],
    "knot group minus surgery": [63],
    "S4 split 4+R+2T holds": True, "double covers twice S4": True, "1+128 4^d N = brute force": True,
}


def link_facts():
    import re
    L = HERE / "links"
    res = json.loads((L / "links_result.json").read_text())
    logs = {f.stem: f.read_text() for f in (L / "logs").glob("*.log")}
    potts = re.findall(r"^(.*?): B_0 \(from link counts\) = (\d+)\s+9\^m Z\(Gamma;3,2\) = (\d+).*OK", logs["potts_reduction"], re.M)
    colour = re.findall(r"^(.*?): P\(Gamma,3\) recovered from link counts = (\d+), direct = (\d+) OK", logs["colouring_reduction_P3_K3"], re.M)
    dihedral = {p: re.findall(r"B_0 from link counts = (\d+), p\^\(2m\) Z\(Gamma;p,2\) = (\d+) OK", logs[f"dihedral_check_{p}"]) for p in (5, 7)}
    crossings = [(int(a), int(b)) for a, b in re.findall(r"crossings=(\d+) components=(\d+)", logs["potts_reduction"])]
    spot = re.findall(r"brute force (\d+), sector method (\d+), equal True", logs["independent_spot_check"])
    out = {
        "run_all ok": res["ok"] and all(r["exit_code"] == 0 for r in res["rows"]) and len(res["rows"]) == 10,
        "S3 Potts sector equals 9^m Z on five graphs": len(potts) == 5 and all(a == b for _, a, b in potts),
        "B_0 values": [int(a) for _, a, _ in potts],
        "3-colourings recovered": [(int(a), int(b)) for _, a, b in colour],
        "D5 and D7 graphs": {p: len(v) for p, v in dihedral.items()},
        "largest link (crossings, components)": max(crossings),
        "independent brute force": [(int(a), int(b)) for a, b in spot],
    }
    out["ok"] = (out["run_all ok"] and out["S3 Potts sector equals 9^m Z on five graphs"]
                 and out["B_0 values"] == [108, 3888, 48114, 669222, 1692738]
                 and out["3-colourings recovered"] == [(12, 12), (6, 6)]
                 and all(len(v) == 3 and all(a == b for a, b in v) for v in dihedral.values())
                 and out["largest link (crossings, components)"] == (2088, 12)
                 and out["independent brute force"] == [(228, 228), (1188, 1188)])
    return out


# ---------- 3. facts derived in the note ----------

def mat_ops():
    n = 12
    states = [(t, f, x) for t in range(2) for f in range(3) for x in range(2)]
    idx = {s: i for i, s in enumerate(states)}
    nu = [idx[(1 - t, f, 1 - x)] for (t, f, x) in states]
    J = [[Fr(1)] * n for _ in range(n)]
    I = [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
    N = [[Fr(int(nu[i] == j)) for j in range(n)] for i in range(n)]
    def lin(a, A, b, B, c=0, C=None):
        return [[a * A[i][j] + b * B[i][j] + (c * C[i][j] if C else 0) for j in range(n)] for i in range(n)]
    def mul(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    def had(A, B):
        return [[A[i][j] * B[i][j] for j in range(n)] for i in range(n)]
    def coords(A):
        """write A = a J + b I + g N; return (a, b, g) or None"""
        a = A[0][next(j for j in range(n) if j != 0 and j != nu[0])]
        b = A[0][0] - a
        g = A[0][nu[0]] - a
        ok = all(A[i][j] == a + b * (i == j) + g * (nu[i] == j) for i in range(n) for j in range(n))
        return (a, b, g) if ok else None
    M = lin(1, J, -2, N)
    half = Fr(1, 2)
    series = lambda A, B: [[half * v for v in row] for row in mul(A, B)]
    return J, I, N, M, series, had, coords, nu


def gadget_facts():
    J, I, N, M, series, had, coords, nu = mat_ops()
    see = series(M, M)
    out = {"S(e,e)": coords(see)}
    g1 = series(M, had(M, see))
    a, b, g = coords(g1)
    out["Gamma_1 = aJ + bI + gN"] = (a, b, g)
    out["Hadamard coordinates"] = (1 + b / a, 1 + g / a)
    # the J, I, N relations used in the note
    def eq(A, B): return all(A[i][j] == B[i][j] for i in range(12) for j in range(12))
    J2 = [[sum(J[i][k] * J[k][j] for k in range(12)) for j in range(12)] for i in range(12)]
    out["J^2 = 12J"] = eq(J2, [[12 * v for v in row] for row in J])
    out["N^2 = I"] = eq([[sum(N[i][k] * N[k][j] for k in range(12)) for j in range(12)] for i in range(12)], I)
    out["I o N = 0"] = all(I[i][j] * N[i][j] == 0 for i in range(12) for j in range(12))
    # spanning trees t and separating 2-forests f of Gamma_1 = S(e, P(e, S(e, e))): vertices s=0, m1=1, m2=2, t=3
    edges = [(0, 1), (1, 3), (1, 2), (2, 3)]
    def comps(es, nv=4):
        p = list(range(nv))
        def f(x):
            while p[x] != x:
                x = p[x]
            return x
        for u, v in es:
            p[f(u)] = f(v)
        return {f(x) for x in range(nv)}, f
    t = f2 = 0
    for k in range(len(edges) + 1):
        for S in itertools.combinations(edges, k):
            cs, find = comps(S)
            if len(S) == 3 and len(cs) == 1:
                t += 1
            if len(S) == 2 and len(cs) == 2 and find(0) != find(3):
                f2 += 1
    out["t, f of Gamma_1"] = (t, f2)
    # parallel powers: t_k = k t f^(k-1), f_k = f^k
    out["t_k, f_k odd for k = 1, 3, 5"] = all((k * t * f2 ** (k - 1)) % 2 == 1 and (f2 ** k) % 2 == 1 for k in (1, 3, 5))
    out["t_2 even (even power breaks the knot)"] = (2 * t * f2) % 2 == 0
    betas = {(i, j): (Fr(25, 17) ** i) * (Fr(15, 17) ** j) for i in range(8) for j in range(8 - i)}
    out["beta_ij distinct (i + j <= 7)"] = len(set(betas.values())) == len(betas)
    return out


def tutte_points():
    def point(Q, v):
        x, y = 1 + Fr(Q) / Fr(v), 1 + Fr(v)
        return x, y, (x - 1) * (y - 1)
    return {"Z(12,1/2)": point(12, Fr(1, 2)), "Z(64,15)": point(64, 15),
            "Z(p^3,p^2-1) p=5": point(125, 24), "Z(p^2,p-1) p=5": point(25, 4)}


# groups as multiplication tables

def table(elems, mul):
    ix = {e: i for i, e in enumerate(elems)}
    T = [[ix[mul(a, b)] for b in elems] for a in elems]
    e = next(i for i, a in enumerate(elems) if all(T[i][j] == j for j in range(len(elems))))
    inv = [next(j for j in range(len(elems)) if T[i][j] == e) for i in range(len(elems))]
    return T, e, inv


def generated(T, e, gens):
    S = {e} | set(gens)
    frontier = list(S)
    while frontier:
        new = []
        for a in frontier:
            for g in list(S):
                for c in (T[a][g], T[g][a]):
                    if c not in S:
                        S.add(c)
                        new.append(c)
        frontier = new
    return S


def derived_length(T, e, inv):
    H = set(range(len(T)))
    n = 0
    while len(H) > 1:
        comms = {T[T[a][b]][T[inv[a]][inv[b]]] for a in H for b in H}
        H2 = generated(T, e, comms)
        if H2 == H:
            return None  # not solvable
        H = H2
        n += 1
    return n


def perm_group(gens_deg):
    pass


def s4_elems():
    return [p for p in itertools.permutations(range(4))]


def pmul(a, b):  # (a*b)(i) = a(b(i))
    return tuple(a[b[i]] for i in range(len(b)))


def sign(p):
    s, seen = 1, set()
    for i in range(len(p)):
        if i in seen:
            continue
        j, L = i, 0
        while j not in seen:
            seen.add(j)
            j = p[j]
            L += 1
        s *= (-1) ** (L - 1)
    return s


def sl23_elems():
    return [(a, b, c, d) for a in range(3) for b in range(3) for c in range(3) for d in range(3) if (a * d - b * c) % 3 == 1]


def mmul3(x, y):
    a, b, c, d = x
    e, f, g, h = y
    return ((a * e + b * g) % 3, (a * f + b * h) % 3, (c * e + d * g) % 3, (c * f + d * h) % 3)


def heis(q_mul, q_add, F, al, be, r):
    """H(F) x| C_r with h.(x, y, z) = (al x, be y, al be z); al, be given as functions e -> multiplier"""
    els = [(x, y, z, k) for x in F for y in F for z in F for k in range(r)]
    def act(k, x, y, z):
        a, b = al(k), be(k)
        return q_mul(a, x), q_mul(b, y), q_mul(q_mul(a, b), z)
    def mul(g1, g2):
        x, y, z, k = g1
        u, v, t, l = g2
        u, v, t = act(k, u, v, t)
        return (q_add(x, u), q_add(y, v), q_add(q_add(z, t), q_mul(x, v)), (k + l) % r)
    return els, mul


def prime_heis(p, r, a, b):
    F = range(p)
    return heis(lambda s, t: s * t % p, lambda s, t: (s + t) % p, F, lambda k: pow(a, k, p), lambda k: pow(b, k, p), r)


def f4_mul(a, b):
    if a == 0 or b == 0:
        return 0
    lg = {1: 0, 2: 1, 3: 2}   # 2 = w, 3 = w^2 = w + 1
    return [1, 2, 3][(lg[a] + lg[b]) % 3]


def ut3f4():
    F = range(4)
    w2 = 3
    pw = lambda base, k: [1, base, f4_mul(base, base)][k % 3]
    return heis(f4_mul, lambda s, t: s ^ t, F, lambda k: pw(w2, k), lambda k: pw(w2, k), 3)


def group_facts():
    out = {}
    T, e, inv = table(s4_elems(), pmul)
    out["S4 order, derived length"] = (len(T), derived_length(T, e, inv))
    a4 = [p for p in s4_elems() if sign(p) == 1]
    T, e, inv = table(a4, pmul)
    out["A4 order, derived length"] = (len(T), derived_length(T, e, inv))
    T, e, inv = table(sl23_elems(), mmul3)
    out["SL(2,3) order, derived length"] = (len(T), derived_length(T, e, inv))
    els, mul = ut3f4()
    T, e, inv = table(els, mul)
    centre = [i for i in range(len(T)) if all(T[i][j] == T[j][i] for j in range(len(T)))]
    out["UT3(F4) x| C3 order, centre size, derived length"] = (len(T), len(centre), derived_length(T, e, inv))
    for (p, r, a, b) in [(5, 4, 2, 2), (5, 4, 2, 3), (5, 4, 1, 2), (7, 3, 2, 2), (7, 3, 2, 4)]:
        els, mul = prime_heis(p, r, a, b)
        T, e, inv = table(els, mul)
        out[f"G_({a},{b}) p={p} r={r}: order, derived length"] = (len(T), derived_length(T, e, inv))
    # smallest hard pairs: p odd prime, r | p - 1, a, b, ab all != 1 among r-th roots of unity
    best = []
    for p in (3, 5, 7, 11, 13):
        for r in range(2, p):
            if (p - 1) % r:
                continue
            roots = [x for x in range(1, p) if pow(x, r, p) == 1]
            hard = [(a, b) for a in roots for b in roots if a != 1 and b != 1 and a * b % p != 1]
            if hard:
                best.append((p ** 3 * r, p, r))
            if r == 2:
                out[f"hard pair with r = 2 at p = {p}"] = bool(hard)
    out["two smallest hard-pair orders"] = sorted(best)[:2]
    return out


# knot groups as fixed points of the Hurwitz action

KNOTS = {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "5_2": ([1, 1, 1, 2, -1, 2], 3),
         "6_1": ([1, 1, 2, -1, -3, 2, -3], 4)}


def hom_count(T, inv, word, b):
    n = len(T)
    count = 0
    for tup in itertools.product(range(n), repeat=b):
        x = list(tup)
        for s in word:
            i = abs(s) - 1
            if s > 0:
                x[i], x[i + 1] = T[T[x[i]][x[i + 1]]][inv[x[i]]], x[i]
            else:
                x[i], x[i + 1] = x[i + 1], T[T[inv[x[i + 1]]][x[i]]][x[i + 1]]
        if x == list(tup):
            count += 1
    return count


def sl23_vs_a4():
    T1, e1, inv1 = table(sl23_elems(), mmul3)
    a4 = [p for p in s4_elems() if sign(p) == 1]
    T2, e2, inv2 = table(a4, pmul)
    rows = {}
    for name, (w, b) in KNOTS.items():
        h1, h2 = hom_count(T1, inv1, w, b), hom_count(T2, inv2, w, b)
        rows[name] = {"H_K(SL(2,3))": h1, "H_K(A4)": h2, "ratio 2": h1 == 2 * h2}
    return rows


def twist_roots():
    rows = {}
    for p in (5, 7, 11, 13):
        roots61 = sorted(x for x in range(p) if (2 * x * x - 5 * x + 2) % p == 0)
        rows[f"6_1 roots mod {p}"] = roots61 == sorted({2, pow(2, p - 2, p)})
        for z in range(2, p):
            m = z * pow((z - 1) * (z - 1), p - 2, p) % p
            roots = {x for x in range(1, p) if (m * x * x - (2 * m + 1) * x + m) % p == 0}
            if not ({z, pow(z, p - 2, p)} <= roots):
                rows[f"m = zeta (zeta-1)^-2 fails at p={p}, zeta={z}"] = False
    return rows


# ---------- 4. the note ----------

QUOTED_IN_NOTE = ["45162496", "326656", "3240625", "46101601", "25925", "+63", "64-1", "192", "500", "1029",
                  "79/15,16", "(25,\\tfrac32)", "17J+8I-2N", "(25/17,15/17)", "$t=3$", "$f=5$", "894",
                  "3k\\cdot5^{k-1}", "5^k", "4+R(K)+2T(K)", "2H_K(A_4)", "2H_K(S_4)", "1+128\\cdot4^d",
                  "B_0=9^mZ_\\Gamma(3,1)", "$2088$", "$12$components", "($12$and$6$)", "$D_5$and$D_7$",
                  "n^{2m}Z_\\Gamma(n,1)", "64+128\\cdot4^{4m}Z_\\Gamma(64,15)"]


def compile_note(tex_path):
    with tempfile.TemporaryDirectory(prefix="rowell_tex_") as tmp:
        tmp = Path(tmp)
        shutil.copy(tex_path, tmp / "rowell_note.tex")
        logs = []
        for _ in range(2):
            run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "rowell_note.tex"],
                                 cwd=tmp, capture_output=True, text=True, timeout=300)
            logs.append(run.returncode)
        log = (tmp / "rowell_note.log").read_text(errors="replace")
        pdf = tmp / "rowell_note.pdf"
        pages = None
        if pdf.exists():
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
            pages = int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages")))
        return {"exit codes": logs, "undefined references": "undefined" in log.lower(),
                "errors": log.count("! "), "pages": pages}


def note_ties(text):
    flat = " ".join(text.split())
    missing = [s for s in QUOTED_IN_NOTE if s not in flat.replace(" ", "")]
    return missing


# ---------- 5. controls ----------

def controls(rep, text):
    out = {}
    out["tampered note number is caught"] = "45162496" in note_ties(text.replace("45162496", "45162497"))
    bad = json.loads(json.dumps(rep))
    bad["rows"][3]["matches_frozen_result"] = False
    out["a mismatching replay row is caught"] = not replay_ok(bad)
    J, I, N, M, series, had, coords, nu = mat_ops()
    wrong = series(M, series(M, M))       # S(e, S(e, e)), a path of three edges
    a, b, g = coords(wrong)
    out["a different gadget gives different coordinates"] = (1 + b / a, 1 + g / a) != (Fr(25, 17), Fr(15, 17))
    T1, e1, inv1 = table(sl23_elems(), mmul3)
    a4 = [p for p in s4_elems() if sign(p) == 1]
    T2, e2, inv2 = table(a4, pmul)
    out["SL(2,3) is not equal to A4 on 4_1 (factor 2 is real)"] = hom_count(T1, inv1, *KNOTS["4_1"]) != hom_count(T2, inv2, *KNOTS["4_1"])
    out["(a, b) = (2, 3) at p = 5 is not a hard pair"] = (2 * 3) % 5 == 1
    return out


def main():
    t0 = time.time()
    res = {}
    ok = True
    rep = load_replay()
    res["1_replay"] = {"replay ok": replay_ok(rep), "rows": len(rep["rows"]), "replay seconds": rep["seconds"]}
    ok &= res["1_replay"]["replay ok"]
    q = quoted_numbers(rep)
    res["2_quoted_numbers"] = {"found": q, "expected": EXPECTED, "ok": q == EXPECTED}
    ok &= res["2_quoted_numbers"]["ok"]
    lf = link_facts()
    res["2b_links"] = {k: str(v) for k, v in lf.items()} | {"ok": lf["ok"]}
    ok &= lf["ok"]
    review = (ROOT / "research/COPRIME-CLASS2-20261026-001A/review.md").read_text()
    res["2_quoted_numbers"]["894 steering configurations in review A"] = "894" in review
    ok &= "894" in review

    g = gadget_facts()
    gok = (g["S(e,e)"] == (4, 2, 0) and g["Gamma_1 = aJ + bI + gN"] == (17, 8, -2)
           and g["Hadamard coordinates"] == (Fr(25, 17), Fr(15, 17)) and g["t, f of Gamma_1"] == (3, 5)
           and g["J^2 = 12J"] and g["N^2 = I"] and g["I o N = 0"] and g["t_k, f_k odd for k = 1, 3, 5"]
           and g["t_2 even (even power breaks the knot)"] and g["beta_ij distinct (i + j <= 7)"])
    res["3a_gadget_algebra"] = {k: str(v) for k, v in g.items()} | {"ok": gok}
    tp = tutte_points()
    tok = (tp["Z(12,1/2)"] == (25, Fr(3, 2), 12) and tp["Z(64,15)"] == (Fr(79, 15), 16, 64)
           and tp["Z(p^3,p^2-1) p=5"][2] == 125 and tp["Z(p^2,p-1) p=5"][2] == 25)
    res["3b_tutte_points"] = {k: str(v) for k, v in tp.items()} | {"ok": tok}
    gf = group_facts()
    gfok = (gf["S4 order, derived length"] == (24, 3) and gf["A4 order, derived length"] == (12, 2)
            and gf["SL(2,3) order, derived length"] == (24, 3)
            and gf["UT3(F4) x| C3 order, centre size, derived length"] == (192, 1, 3)
            and gf["G_(2,2) p=5 r=4: order, derived length"] == (500, 3)
            and gf["G_(2,3) p=5 r=4: order, derived length"] == (500, 3)
            and gf["G_(1,2) p=5 r=4: order, derived length"] == (500, 2)
            and gf["G_(2,2) p=7 r=3: order, derived length"] == (1029, 3)
            and not any(v for k, v in gf.items() if k.startswith("hard pair with r = 2"))
            and gf["two smallest hard-pair orders"] == [(500, 5, 4), (1029, 7, 3)])
    res["3c_groups"] = {k: str(v) for k, v in gf.items()} | {"ok": gfok}
    sv = sl23_vs_a4()
    svok = all(r["ratio 2"] for r in sv.values())
    res["3d_sl23_is_twice_a4_on_knots"] = {"rows": sv, "ok": svok}
    tr = twist_roots()
    trok = all(tr.values())
    res["3e_twist_knot_roots"] = {"rows": tr, "ok": trok}
    ok &= gok and tok and gfok and svok and trok

    text = NOTE.read_text()
    comp = compile_note(NOTE)
    missing = note_ties(text)
    nok = comp["exit codes"] == [0, 0] and not comp["undefined references"] and comp["errors"] == 0 and not missing
    res["4_note"] = {"compile": comp, "quoted strings missing from the note": missing, "ok": nok}
    ok &= nok
    c = controls(rep, text)
    res["5_controls"] = {"rows": c, "ok": all(c.values())}
    ok &= all(c.values())

    res["ok"] = ok
    res["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "ROWELL-NOTE-20261026-001-P001",
              "status": "Proved" if ok else "Partial", "checks": res}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str)[:6000])
    print("ALL OK" if ok else "FAILURES", res["seconds"], "s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
