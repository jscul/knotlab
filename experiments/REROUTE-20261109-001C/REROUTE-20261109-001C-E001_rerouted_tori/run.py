"""REROUTE-20261109-001C-E001: re-routed lattice tori, a census (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/REROUTE-20261109-001C/REROUTE-20261109-001C-E001_rerouted_tori/run/result.json

Each network is a square, triangular or honeycomb n x n torus re-routed at a random set of contacts (REROUTE-20261109-001B's reroute_lib):
starting from the empty set (the torus) or from the line network's set (one direction class on the square and triangular tori, two on
the honeycomb), 4 n^2 times a face of the torus is drawn and its contacts toggled in the set, the toggle kept when the result is still a
network (no contact joining a ring to itself). Persistence is read through REROUTE-20261109-001B, Theorem 1 (the contact graph is checked
unchanged) and directly where the network has at most 300 contacts; flips as in FLIP-RULE-20261109-001B-E001; the plain first need of
every ring for every target by shortest routes."""
import collections
import importlib.util
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/REROUTE-20261109-001B/REROUTE-20261109-001B-P001_rerouting_keeps_persistence"))
import reroute_lib as RR  # noqa: E402

spec = importlib.util.spec_from_file_location("run_e001", ROOT / "experiments/FLIP-RULE-20261109-001B/FLIP-RULE-20261109-001B-E001_small_maps/run.py")
R1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R1)
OUT = ROOT / "artifacts" / "REROUTE-20261109-001C" / "REROUTE-20261109-001C-E001_rerouted_tori" / "run"
KINDS = ("square", "triangular", "honeycomb")
SIZES = (6, 8, 10, 12, 16)
SEEDS = (1, 2, 3, 4)
STARTS = ("torus", "lines")
LINE_CLASSES = {"square": (1,), "triangular": (0,), "honeycomb": (0, 1)}
SMALL = 12
SEED = 20261112


def sends_hears_all(sig):
    E = len(sig) // 2
    out = [[sig[2 * c] >> 1, sig[2 * c + 1] >> 1] for c in range(E)]
    inn = [[] for _ in range(E)]
    for a in range(E):
        for b in out[a]:
            inn[b].append(a)
    # in a strongly connected contact graph whose rows and columns mod 2 are not all zero every contact sends and hears; read directly
    rows = [0] * E
    for d in range(len(sig)):
        rows[d >> 1] ^= 1 << (sig[d] >> 1)
    cols = [0] * E
    for a in range(E):
        x = rows[a]
        while x:
            low = x & -x
            cols[low.bit_length() - 1] ^= 1 << a
            x ^= low

    def nonzero(mat, c):
        v = 1 << c
        for _ in range(E + 1):
            w, x = 0, v
            while x:
                low = x & -x
                w ^= mat[low.bit_length() - 1]
                x ^= low
            v = w
            if v:
                return True
        return False
    return all(nonzero(rows, c) and nonzero(cols, c) for c in range(E))


def network(args):
    kind, n, start, seed = args
    rng = random.Random(SEED + 1000 * KINDS.index(kind) + 100 * n + 10 * STARTS.index(start) + seed)
    sig, rot, edges, B = RR.lattice(kind, n)
    cl = RR.classes(kind, rot)
    S = set() if start == "torus" else set().union(*[cl[k] for k in LINE_CLASSES[kind]])
    F = RR.face_moves(sig)
    kept = 0
    for _ in range(4 * n * n):
        T = S.symmetric_difference(rng.choice(F))
        if RR.is_network(RR.reroute(sig, T)):
            S, kept = T, kept + 1
    s = RR.reroute(sig, S)
    E = len(s) // 2
    rs = RR.rings(s)
    fs = RR.faces(s)
    doubled = sum(1 for c in range(E) if s[2 * c] >> 1 == s[2 * c + 1] >> 1)
    pers = R1.persistent(s) if E <= 300 else None
    flips = sum(R1.symmetries(s, c)[0] for c in range(E))
    late_rings, late = set(), 0
    for t in range(E):
        dist, par, low = RR.routes_to(s, t)
        for i, cs in enumerate(rs):
            m = min(dist[e] for e in cs)
            if not any(par[e] for e in cs if dist[e] == m):
                late += 1
                late_rings.add(i)
    single = RR.late_pairs(s, single=True)
    small = [i for i, cs in enumerate(rs) if len(cs) <= SMALL]
    roots = rng.sample(range(len(rs)), min(4, len(rs)))
    balls = RR.ring_graph_balls(s, 8, roots=roots)
    return {"lattice": kind, "n": n, "start": start, "seed": seed, "contacts": E, "toggles kept": kept, "re-routed contacts": len(S),
            "rings": len(rs), "ring sizes": [min(map(len, rs)), max(map(len, rs)), round(2 * E / len(rs), 2)],
            "smallest face": min(map(len, fs)), "genus": RR.genus(s), "doubled pairs": doubled,
            "contact graph unchanged": RR.arcs(s) == RR.arcs(sig), "every contact persists (direct)": None if pers is None else all(pers),
            "contacts with a flip": flips, "late (ring, target) pairs": late, "of": len(rs) * E, "rings late for some target": len(late_rings),
            "pairs with no single fastest way": single, "rings of at most %d contacts" % SMALL: len(small),
            "of those, late for some target": sum(1 for i in small if i in late_rings),
            "ring balls, radius 0 to 8, mean of four roots": [round(sum(b[r] for b in balls) / len(balls), 2) for r in range(9)]}


def main():
    t0 = time.time()
    jobs = [(k, n, st, sd) for k in KINDS for n in SIZES for st in STARTS for sd in SEEDS]
    with Pool(16) as pool:
        rows = pool.map(network, sorted(jobs, key=lambda j: -j[1]), chunksize=1)
    rows.sort(key=lambda r: (KINDS.index(r["lattice"]), r["n"], r["start"], r["seed"]))
    base_sh = {k: sends_hears_all(RR.lattice(k, 8)[0]) for k in KINDS}
    nondeg = [r for r in rows if r["ring sizes"][0] >= 3 and r["smallest face"] >= 3 and r["doubled pairs"] == 0]
    h1 = all(r["contact graph unchanged"] and r["every contact persists (direct)"] in (True, None) and r["contacts with a flip"] == 0 for r in rows)
    h2 = all(r["late (ring, target) pairs"] > 0 for r in rows)
    big = [r for r in rows if r["n"] >= 12]
    h3 = all(r["of those, late for some target"] == r["rings of at most %d contacts" % SMALL] for r in big)
    summary = {"networks": len(rows), "non-degenerate (rings and faces of at least 3, no doubled pair)": len(nondeg),
               "every contact sends and hears on the 8 x 8 tori (a property of the contact graph)": base_sh,
               "with no flip at any contact": sum(r["contacts with a flip"] == 0 for r in rows),
               "on time": sum(r["late (ring, target) pairs"] == 0 for r in rows),
               "rings of at most %d contacts on tori of n >= 12, late for some target / all" % SMALL:
                   [sum(r["of those, late for some target"] for r in big), sum(r["rings of at most %d contacts" % SMALL] for r in big)]}
    result = {"experiment": "REROUTE-20261109-001C-E001", "summary": summary,
              "H1 every random re-routing keeps every contact persistent and has no flip": h1,
              "H2 no random re-routing reads its distance plainly": h2,
              "H3 on tori of n >= 12 every ring of at most 12 contacts is late for some target": h3,
              "networks": rows, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "networks"}, indent=1))


if __name__ == "__main__":
    main()
