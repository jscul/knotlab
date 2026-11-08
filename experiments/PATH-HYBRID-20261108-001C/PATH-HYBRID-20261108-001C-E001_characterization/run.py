"""PATH-HYBRID-20261108-001C-E001: what makes a hybrid middle ring work (exploratory; see contract.json).

    .venv/bin/python3 -B run.py   writes artifacts/PATH-HYBRID-20261108-001C/PATH-HYBRID-20261108-001C-E001_characterization/run/result.json
Measures on ticket B's 1,120 native paths, exact by the row-sequence reduction, and a canonical check of the smallest."""
from __future__ import annotations

import itertools
import json
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PATH-HYBRID-20261108-001B/PATH-HYBRID-20261108-001B-E001_hybrid_middles"))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import hybrid_lib as H  # noqa: E402
import growth_law_lib as G  # noqa: E402

PL, W = H.PL, H.W
OUT = ROOT / "artifacts" / "PATH-HYBRID-20261108-001C" / "PATH-HYBRID-20261108-001C-E001_characterization" / "run"
PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001B/PATH-HYBRID-20261108-001B-E001_hybrid_middles/run/paths.json"
LIN = sorted(H.LIN)


def native(rules, sizes, ks, laws):
    try:
        a = H.analyze(rules, sizes, ks, laws)
    except AssertionError:
        return False
    return a["all persist"] and a["ends at the last contact"]


def insert_cell(rule_list, at, rule):
    out = list(rule_list)
    out.insert(at, rule)
    return out


def measures(x):
    rules = [x[0][0], x[0][1], list(x[0][2]), x[0][3]]
    sizes, ks, laws = list(x[1]), list(x[2]), tuple(tuple(l) for l in x[3])
    rC, mC, kC = rules[2], sizes[2], ks[1]
    # (1) uniform second middle rings
    uniform_native = [r for r in LIN if native((rules[0], rules[1], r, rules[3]), tuple(sizes), ks, laws)]
    # (2) transport: one more cell in ring C on the far side (between c3 and c2), with the rule of either neighbour; one more end-ring cell
    far = [j for j in range(kC + 1, mC)]
    grown_C = []
    for j in far + [mC]:
        for rule in {rC[j - 1] if j - 1 not in (0, kC) else 204, rC[j % mC] if j % mC not in (0, kC) else 204}:
            r2 = insert_cell(rC, j, rule)
            grown_C.append(native((rules[0], rules[1], r2, rules[3]), (sizes[0], sizes[1], mC + 1, sizes[3]), ks, laws))
    grown_A = native(tuple(rules), (sizes[0] + 1, sizes[1], sizes[2], sizes[3]), ks, laws)
    grown_D = native(tuple(rules), (sizes[0], sizes[1], sizes[2], sizes[3] + 1), ks, laws)
    # (3) roles: which ring-C cells stay in c3's eventual support, and through which side ring A's influence arrives at c3
    rows, N, blocks = H.linear_matrix(tuple(rules), tuple(sizes), ks, laws)
    rings, _, _ = PL.layout(tuple(sizes), ks)
    s3, T1, p = W.row_orbit(rows, 1 << 2)
    RC = rings[2]
    kept = sorted({j for j in range(mC) if j not in (0, kC) and any(r >> RC[j] & 1 for r in s3[T1 - 1:T1 + p - 1])})
    return {"uniform rings that stay native": uniform_native, "grown ring C native": grown_C, "grown A native": grown_A,
            "grown D native": grown_D, "ring-C cells in c3's eventual support": kept}


def canonical(x):
    rules = (x[0][0], x[0][1], list(x[0][2]), x[0][3])
    sizes, ks, laws = tuple(x[1]), list(x[2]), tuple(tuple(l) for l in x[3])
    nxt, N, blocks = H.mixed_state_map(rules, sizes, ks, laws)
    L = PL.light_cone(sizes, ks)
    masks = [PL.mask(blocks, f"R{i}") for i in range(4)]
    cur = np.arange(len(nxt), dtype=np.int64)
    lags = []
    for T in range(1, L + 6):
        cur = nxt[cur]
        if T < L:
            continue
        F = ((cur >> 2) & 1).astype(np.uint8)
        R = G.Rel([f"v{j}" for j in range(N)] + ["c3"], [u | (int(F[u]) << N) for u in range(1 << N)])
        kn = [S for S in G.knots(R) if S >> N & 1]
        lags.append({"T": T, "knots through c3(T)": len(kn), "each meets all four rings": bool(kn) and all(all(S & m for m in masks) for S in kn),
                     "sizes": sorted({bin(S).count("1") for S in kn})})
    rows, N, blocks = H.linear_matrix(rules, sizes, ks, laws)
    s3, T1, p = W.row_orbit(rows, 1 << 2)
    support = [j for j in range(N) if s3[-1] >> j & 1]
    names = [f"x{j}" for j in support]
    cnf = [" ".join((f"~{n}" if v else n) for n, v in zip(names + ["c"], vals))
           for vals in itertools.product((0, 1), repeat=len(names) + 1) if sum(vals) % 2 == 1]
    env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
    kl = json.loads(subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(cnf), "--loops", *names, "--contact",
                                    "c", "--json"], capture_output=True, text=True, env=env, cwd=ROOT, check=True).stdout)
    return {"path": x[:4], "light cone": L, "generic enumerator at lags L..L+5": lags,
            "eventual support of c3 per ring": [sum(1 for j in support if masks[i] >> j & 1) for i in range(4)],
            "knotlab check of the parity relation on that support": {k: kl[k] for k in ("is_knot", "binding", "loss_on_erasure", "invisible_in_parts")}}


def main():
    t0 = time.time()
    rows = json.loads(PATHS.read_text())["rows"]
    nat = [r for r in rows if r[4]]
    with Pool(16) as pool:
        res = pool.map(measures, nat, chunksize=8)
    hybrid_needed = sum(1 for m in res if not m["uniform rings that stay native"])
    uni = Counter(r for m in res for r in m["uniform rings that stay native"])
    grownC = Counter((sum(m["grown ring C native"]), len(m["grown ring C native"])) for m in res)
    kept = Counter(len(m["ring-C cells in c3's eventual support"]) for m in res)
    nat.sort(key=lambda x: (sum(x[1]), x[1], x[2], json.dumps(x[0])))
    can = canonical(nat[0])
    result = {"experiment": "PATH-HYBRID-20261108-001C-E001", "native paths characterized": len(nat),
              "hybridness necessary (no uniform ring C with one of the eight linear rules stays native)": hybrid_needed,
              "uniform ring-C rules that keep some path native": dict(uni),
              "one more ring-C cell: (native variants, variants tried) per path": [[list(k), v] for k, v in grownC.most_common(8)],
              "paths still native with one more ring-A cell": sum(m["grown A native"] for m in res),
              "paths still native with one more ring-D cell": sum(m["grown D native"] for m in res),
              "number of ring-C cells in c3's eventual support (paths)": dict(sorted(kept.items())),
              "canonical check of the smallest": can, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1)[:6000])


if __name__ == "__main__":
    main()
