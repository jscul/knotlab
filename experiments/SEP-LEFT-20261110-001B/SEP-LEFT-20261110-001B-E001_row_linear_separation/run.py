"""SEP-LEFT-20261110-001B-E001: row-linear separation in bit PHP and bit LeftPigeon at small sizes (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/SEP-LEFT-20261110-001B/SEP-LEFT-20261110-001B-E001_row_linear_separation/run/result.json

pcsep.c (compiled into the artifact folder) computes the F2 polynomial-calculus closure at degree B (standard rule) and, for each
probe set of monomials, how many are independent modulo it: a set's span meets the closure in dimension (size - new), so the
largest subspace of its span separated at degree B (meeting the closure only in zero) has dimension new.

Instances, for n = 2, 4, 8 holes, l = log2 n, m = n + 1 pigeons:
- BPHP_n, Braun's compact base: bit rows b_i (l bits, pigeon i), axioms E_ii' = prod_t (1 + b_it + b_i't) for i < i' ("rows i and i'
  encode the same hole").
- LP_n, the binary left-pigeon principle: pigeon rows f_x (l bits, the hole of pigeon x) and hole rows g_h (l + 1 bits, a pigeon's
  code; codes of m or more name no pigeon), axioms [f_x = h] * [g_h,j != x_j] for every pigeon x, hole h and bit j ("if pigeon x sits
  in hole h, then g(h) = x"), of degree l + 1.
Probe sets: the row-linear monomials (at most one bit from each row) of degree at most k, k = 1, 2, over the pigeon rows only and over
all rows (for BPHP the two coincide)."""
import itertools
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "SEP-LEFT-20261110-001B" / "SEP-LEFT-20261110-001B-E001_row_linear_separation" / "run"
SIZES = (2, 4, 8)
MEM_MIB = 15000


def mul(P, Q):
    out = set()
    for a in P:
        for b in Q:
            out ^= {a | b}
    return out


def bphp(n):
    l = n.bit_length() - 1
    m = n + 1
    rows = [[i * l + t for t in range(l)] for i in range(m)]
    axioms = []
    for i, j in itertools.combinations(range(m), 2):
        P = {0}
        for t in range(l):
            P = mul(P, {0, 1 << rows[i][t], 1 << rows[j][t]})
        axioms.append(P)
    return m * l, axioms, rows, rows


def left_pigeon(n):
    l = n.bit_length() - 1
    m = n + 1
    lg = (m - 1).bit_length()
    f = [[x * l + t for t in range(l)] for x in range(m)]
    g = [[m * l + h * lg + j for j in range(lg)] for h in range(n)]
    axioms = []
    for x in range(m):
        for h in range(n):
            sits = {0}
            for t in range(l):
                lit = {1 << f[x][t]} if (h >> t) & 1 else {0, 1 << f[x][t]}
                sits = mul(sits, lit)
            for j in range(lg):
                differs = {1 << g[h][j]} ^ ({0} if (x >> j) & 1 else set())
                axioms.append(mul(sits, differs))
    return m * l + n * lg, axioms, f, f + g


def row_linear(rows, k):
    out = [0]
    for d in range(1, k + 1):
        for chosen in itertools.combinations(range(len(rows)), d):
            for bits in itertools.product(*[rows[r] for r in chosen]):
                out.append(sum(1 << b for b in bits))
    return out


def run(binary, B, v, axioms, probes):
    inp = "%d %d\n" % (v, len(axioms)) + "".join("%d %s\n" % (len(a), " ".join(map(str, sorted(a)))) for a in axioms)
    inp += "%d\n" % len(probes) + "".join("%d\n%s\n" % (len(p), " ".join(map(str, p))) for p in probes)
    return json.loads(subprocess.run([str(binary), str(B), str(MEM_MIB)], input=inp, capture_output=True, text=True,
                                     check=True).stdout.splitlines()[0])


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    binary = OUT / "pcsep"
    subprocess.run(["gcc", "-O3", "-march=native", "-o", str(binary), str(HERE / "pcsep.c")], check=True)
    log = open(OUT / "progress.txt", "w")
    readings = {}
    for name, build in (("BPHP", bphp), ("LP", left_pigeon)):
        for n in SIZES:
            v, axioms, prow, arow = build(n)
            sets = {"L1 pigeon rows": row_linear(prow, 1), "L1 all rows": row_linear(arow, 1),
                    "L2 pigeon rows": row_linear(prow, 2), "L2 all rows": row_linear(arow, 2)}
            key = "%s_%d" % (name, n)
            readings[key] = {"variables": v, "axioms": len(axioms), "set sizes": {s: len(p) for s, p in sets.items()}, "by degree": {}}
            for B in range(1, v + 1):
                use = [s for s in sets if int(s[1]) <= B]
                r = run(binary, B, v, axioms, [sets[s] for s in use])
                print(key, B, json.dumps(r), round(time.time() - t0), file=log, flush=True)
                if "skipped" in r:
                    readings[key]["by degree"][B] = {"undecided": r["skipped"]}
                    break
                readings[key]["by degree"][B] = {"refuted": r["refuted"], "rank": r["rank"],
                                                 "separated": {s: p[1] for s, p in zip(use, r["probes"])}}
                if r["refuted"]:
                    break
    def horizon(key, s):
        h = 0
        for B, rd in sorted(readings[key]["by degree"].items()):
            if "separated" not in rd or s not in rd["separated"] or rd["separated"][s] < readings[key]["set sizes"][s]:
                break
            h = B
        return h
    hz = {key: {s: horizon(key, s) for s in readings[key]["set sizes"]} for key in readings}
    braun = {4: (1, 2), 8: (2, 4)}                     # n: (largest k with 4(k - 1) < n, largest B with 2B - 1 <= n)
    def sep_through(key, s, Bmax):
        rows = readings[key]["by degree"]
        return all(B in rows and "separated" in rows[B] and rows[B]["separated"].get(s) == readings[key]["set sizes"][s]
                   for B in range(int(s[1]), Bmax + 1))
    h1 = all(sep_through("BPHP_%d" % n, "L%d all rows" % k, Bm) for n, (km, Bm) in braun.items() for k in range(1, km + 1))
    h2 = {"n=%d k=%d" % (n, k): hz["LP_%d" % n]["L%d all rows" % k] >= hz["BPHP_%d" % n]["L%d all rows" % k] for n in (4, 8) for k in (1, 2)}
    h3 = {"n=%d k=%d" % (n, k): hz["LP_%d" % n]["L%d pigeon rows" % k] >= hz["BPHP_%d" % n]["L%d all rows" % k] for n in (4, 8) for k in (1, 2)}
    inside = all(sep_through("LP_8", "L%d all rows" % k, 4) for k in (1, 2))
    grows = all(hz["LP_8"]["L%d all rows" % k] > hz["LP_4"]["L%d all rows" % k] for k in (1, 2))
    verdict = ("density that grows" if all(h2.values()) and grows else
               "none" if not inside else "intermediate")
    result = {"experiment": "SEP-LEFT-20261110-001B-E001", "readings": readings, "horizons (largest B with the set fully separated)": hz,
              "H1 BPHP's row-linear spaces are separated through Braun's range (n = 4, 8)": h1,
              "H2 LP's row-linear spaces over all rows are separated as far as BPHP's": h2,
              "H3 LP's row-linear spaces over the pigeon rows are separated as far as BPHP's": h3,
              "LP_8 separated through B = 4 for k = 1, 2 (Braun's range)": inside,
              "LP's horizon grows from n = 4 to n = 8 (all rows, k = 1, 2)": grows,
              "verdict": verdict, "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "readings"}, indent=1))


if __name__ == "__main__":
    main()
