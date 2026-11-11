"""The frozen census of KNOTS-ALONE-20261111-001A-E001 (contract.json beside this file).

Run from the repository root:
    .venv/bin/python -B experiments/KNOTS-ALONE-20261111-001A/KNOTS-ALONE-20261111-001A-E001_knots_alone_census/census.py
Output: artifacts/KNOTS-ALONE-20261111-001A/KNOTS-ALONE-20261111-001A-E001_knots_alone_census/census.json and census_log.txt.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import knots_alone as ka  # noqa: E402

CONTROL = "--control" in sys.argv
OUT = os.path.join(ROOT, "artifacts", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census")
if CONTROL:
    OUT = sys.argv[sys.argv.index("--control") + 1]
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, "census_log.txt"), "w")

# Frozen parameters (contract.json, "definitions")
POS_V = range(4, 13)              # d = 3, 4, 5: complete for every V by double counting (chi <= 2)
FLAT_SAT_V = range(7, 17)         # d = 6, exhaustive SAT: tori and Klein bottles
FLAT_LATTICE_V = range(17, 49)    # d = 6, lattice tori (Altshuler: all tori)
NEG_V, NEG_BUDGET = 12, 600       # d = 7, a sample: what the SAT search finds within 600 s
H_DV = [(d, V) for d in range(3, 8) for V in range(6, 13) if (d * V) % 3 == 0 and d <= V - 1]
H_N, H_SEED = 60, 20261111        # per (d, V), seeded, biased sample for existence only
SMALL_V = 20                      # OR and NOL read by SAT up to here; brute force cross-check up to BRUTE_V
BRUTE_V = 16
BOND_V = range(12, 25)            # P5: lattice tori 12..24 under NAE, bonds of size <= KMAX through distinction 0
KMAX = 6
CTRL_BOND_V = range(12, 17)       # lemma controls for bond distance: OR, NOL, PAR


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def describe(V, T, family):
    deg = ka.degrees(V, T)
    rec = {"family": family, "V": V, "knots": len(T), "d": deg[0] if len(set(deg)) == 1 else None, "T": [list(t) for t in T]}
    surf = ka.is_surface(V, T)
    rec["surface"] = surf
    if surf:
        rec["chi"] = ka.euler(V, T)
        rec["orientable"] = ka.orientable(T)
        rec["nonfacial_triangle"] = ka.has_nonfacial_triangle(V, T)
        rec["three_colourable"] = ka.three_colouring(V, T) is not None
    return rec


def control_worlds():
    """Worlds outside the frozen family: not regular, or regular at a size the census does not sample."""
    bip = [tuple(sorted((5, i, (i + 1) % 5))) for i in range(5)] + [tuple(sorted((6, i, (i + 1) % 5))) for i in range(5)]
    out = [describe(3, [(0, 1, 2)], "control"), describe(4, [(0, 1, 2), (1, 2, 3)], "control"), describe(7, bip, "control")]
    for T in ka.random_regular_worlds_sat(15, 6, 3, seed=7):
        out.append(describe(15, T, "regular d=6"))
    return out


def main():
    t0 = time.time()
    worlds = []
    if CONTROL:
        return run_laws(control_worlds(), {}, t0, control=True)
    # ---- surface worlds
    for d in (3, 4, 5):
        for V in POS_V:
            reps, n = ka.surface_worlds_sat(V, d)
            for T in reps:
                worlds.append(describe(V, T, f"surface d={d}"))
    flat_sat_tori = {}
    for V in FLAT_SAT_V:
        reps, n = ka.surface_worlds_sat(V, 6)
        flat_sat_tori[V] = [T for T in reps if ka.orientable(T)]
        for T in reps:
            worlds.append(describe(V, T, "surface d=6"))
    # control: the lattice tori are exactly the orientable flat worlds found by SAT
    lattice_check = {}
    for V in FLAT_SAT_V:
        lat = ka.lattice_tori(V)
        a = sorted(min(ka.canon_codes_surface(T)) for T in lat)
        b = sorted(min(ka.canon_codes_surface(T)) for T in flat_sat_tori[V])
        lattice_check[V] = a == b
    log("lattice tori agree with the SAT tori at every V in 7..16:", all(lattice_check.values()), lattice_check)
    for V in FLAT_LATTICE_V:
        for T in ka.lattice_tori(V):
            worlds.append(describe(V, T, "surface d=6 lattice"))
    reps, n, complete = ka.surface_worlds_sat(NEG_V, 7, budget=NEG_BUDGET)
    log("d=7, V=12 sample:", len(reps), "classes, complete:", complete)
    for T in reps:
        worlds.append(describe(NEG_V, T, "surface d=7 sample"))
    # ---- non-surface regular worlds (sample)
    for d, V in H_DV:
        sample = ka.random_regular_worlds_sat(V, d, H_N, seed=H_SEED + 100 * d + V)
        for T in sample:
            if not ka.is_surface(V, T):
                worlds.append(describe(V, T, f"regular d={d}"))
    log("worlds:", len(worlds), Counter(w["family"] for w in worlds), round(time.time() - t0, 1), "s")
    return run_laws(worlds, lattice_check, t0)


def run_laws(worlds, lattice_check, t0, control=False):

    # ---- laws
    mismatches = []
    for i, w in enumerate(worlds):
        V, T = w["V"], [tuple(t) for t in w["T"]]
        w["NAE"] = ka.read_law_sat(V, T, ka.LAWS["NAE"])
        w["PAR"] = ka.read_parity_gf2(V, T)
        if V <= SMALL_V:
            w["OR"] = ka.read_law_sat(V, T, ka.LAWS["OR"])
            w["NOL"] = ka.read_law_sat(V, T, ka.LAWS["NOL"])
            par_sat = ka.read_law_sat(V, T, ka.LAWS["PAR"])
            if any(par_sat.get(k) != w["PAR"].get(k) for k in par_sat):
                mismatches.append(("PAR sat vs gf2", i))
        if V <= BRUTE_V:
            for law in ("NAE", "PAR", "OR", "NOL"):
                b = ka.read_law_brute(V, T, ka.LAWS[law])
                if any(b.get(k) != w[law].get(k) for k in w[law] if k != "states"):
                    mismatches.append((law + " brute", i))
                w[law]["states"] = b.get("states", 0)
            if V <= 12:
                for law, comp in (("PAR", frozenset({0, 2})), ("OR", frozenset({0, 1, 2})), ("NOL", frozenset({0, 1, 3}))):
                    c = ka.read_law_brute(V, T, comp)
                    if any(c.get(k) != w[law].get(k) for k in w[law]):
                        mismatches.append((law + " complement", i))
    log("independent paths and complements disagree on:", mismatches)

    # ---- lemma controls D4, D5, D6 (computed; each can fail)
    d4 = [i for i, w in enumerate(worlds) if "OR" in w and not w["OR"].get("faithful")]
    d5 = []
    d6 = []
    for i, w in enumerate(worlds):
        if not w["surface"]:
            continue
        V, T = w["V"], [tuple(t) for t in w["T"]]
        p = w["PAR"]
        if w["three_colourable"]:
            col = ka.three_colouring(V, T)
            transversal = sum(1 for t in itertools.combinations(range(V), 3) if len({col[v] for v in t}) == 3)
            if not (p["allowed"] and p["native"] and p["states"] == 4 and p["bonds3"] == transversal and (V == 3 or not p["faithful"])):
                d5.append(i)
        elif p.get("native"):
            d5.append(i)
        if "NOL" in w:
            q = w["NOL"]
            adjacent = set()
            for t in T:
                adjacent.update(itertools.combinations(t, 2))
            with_edge = sum(1 for t in itertools.combinations(range(V), 3)
                            if any(e in adjacent for e in itertools.combinations(t, 2)))
            if not (q["allowed"] and q["native"] and q["bonds3"] == with_edge):
                d6.append(i)
    log("lemma failures D4 (OR):", d4, "D5 (PAR on surfaces):", d5, "D6 (NOL on surfaces):", d6)

    # ---- bond distance (P5) and its lemma controls
    bonds = []
    bond_worlds = [(V, T) for V in BOND_V for T in ka.lattice_tori(V)] if not control else [(7, [tuple(t) for t in worlds[2]["T"]])]
    for V, T in bond_worlds:
        if True:
            rec = {"V": V, "T": [list(t) for t in T]}
            idx = next(i for i, w in enumerate(worlds) if w["V"] == V
                       and sorted(map(tuple, w["T"])) == sorted(map(tuple, T)))
            rec["world"] = idx
            delta = ka.graph_distance(V, T, 0)
            laws = ["NAE"] + (["OR", "NOL", "PAR"] if V in CTRL_BOND_V or control else [])
            for law in laws:
                st = ka.all_states(V, T, ka.LAWS[law])
                if len(st) == 0:
                    rec[law] = None
                    continue
                beta = ka.bond_distances_from(V, T, st, 0, KMAX)
                table = Counter((delta[v], beta[v]) for v in beta)
                rec[law] = sorted([[dl, b, n] for (dl, b), n in table.items()], key=lambda r: (r[0], -1 if r[1] is None else r[1]))
            bonds.append(rec)
            log("bonds V", V, {k: rec[k] for k in rec if k in ("NAE", "OR", "NOL", "PAR")}, "faithful NAE:",
                worlds[idx]["NAE"].get("faithful"), round(time.time() - t0, 1), "s")

    bond_lemma = []
    for rec in bonds:
        V, T = rec["V"], [tuple(t) for t in rec["T"]]
        delta = ka.graph_distance(V, T, 0)
        if rec.get("OR") is not None and any((dl == 1) != (b == 2) or (b not in (2, None)) for dl, b, n in rec["OR"]):
            bond_lemma.append(("OR", V))
        if rec.get("NOL") is not None and any(b != 2 for dl, b, n in rec["NOL"]):
            bond_lemma.append(("NOL", V))
    log("bond-distance lemma failures (OR: 2 exactly between co-knotted, NOL: 2 everywhere):", bond_lemma)

    # ---- knotlab cross-check on the smallest bond-distance torus: 3-bonds and least bonds, by the canonical checker
    from knotlab.relations import Relation
    from knotlab import space
    kl = {}
    first = bonds[0]
    V, T = first["V"], [tuple(t) for t in first["T"]]
    st = ka.all_states(V, T, ka.LAWS["NAE"])
    names = tuple(f"x{v}" for v in range(V))
    rel = Relation(names, frozenset(tuple(bool((int(x) >> v) & 1) for v in range(V)) for x in st))
    kl_bonds3 = sorted(tuple(sorted(int(n[1:]) for n in b)) for b in space.bonds(rel) if len(b) == 3)
    mine = ka.read_law_sat(V, T, ka.LAWS["NAE"])
    kl["bonds3_agree"] = len(kl_bonds3) == mine.get("bonds3")
    beta = ka.bond_distances_from(V, T, st, 0, KMAX)
    agree = True
    for v in range(1, V):
        sb = space.smallest_bond(rel, "x0", f"x{v}")
        kb = None if sb is None or sb > KMAX else sb - 1
        if kb != beta[v]:
            agree = False
    kl["bond_distance_agree"] = agree
    log("knotlab cross-check on V =", V, kl)

    # ---- predictions, computed
    pos = {(w["family"], w["V"], w["orientable"]): w for w in worlds if w["family"] in ("surface d=3", "surface d=4", "surface d=5")}
    tet = pos.get(("surface d=3", 4, True))
    octa = pos.get(("surface d=4", 6, True))
    ico = pos.get(("surface d=5", 12, True))
    hemi = pos.get(("surface d=5", 6, False))
    P1 = {
        "positive worlds": sorted([[k[0], k[1], k[2]] for k in pos]),
        "tetrahedron NAE faithful": bool(tet and tet["NAE"].get("faithful")),
        "octahedron NAE faithful": bool(octa and octa["NAE"].get("faithful")),
        "icosahedron NAE faithful": bool(ico and ico["NAE"].get("faithful")),
        "hemi-icosahedron NAE not allowed": bool(hemi and not hemi["NAE"]["allowed"]),
    }
    P1["holds"] = len(pos) == 4 and all(v for k, v in P1.items() if k != "positive worlds")
    flat = [w for w in worlds if w["surface"] and w.get("d") == 6]
    flat_no_nft = [w for w in flat if not w["nonfacial_triangle"]]
    fails2 = [[w["V"], w["orientable"], w["NAE"]] for w in flat_no_nft if not w["NAE"].get("faithful")]
    k7 = [w for w in flat if w["V"] == 7]
    P2 = {"flat worlds": len(flat), "without nonfacial triangle": len(flat_no_nft), "failures": fails2,
          "K7 NAE not allowed": bool(k7) and all(not w["NAE"]["allowed"] for w in k7)}
    P2["holds"] = not fails2 and P2["K7 NAE not allowed"]
    P2["with nonfacial triangle"] = Counter(
        ("faithful" if w["NAE"].get("faithful") else "native" if w["NAE"].get("native") else "allowed" if w["NAE"]["allowed"] else "no state")
        for w in flat if w["nonfacial_triangle"])
    P3 = {}
    for d in range(3, 8):
        hs = [w for w in worlds if w["family"] == f"regular d={d}"]
        entry = {"sampled": len(hs)}
        for law in ("NAE", "PAR", "OR", "NOL"):
            entry[law + " native"] = sum(1 for w in hs if law in w and w[law].get("native"))
        entry["NAE faithful"] = sum(1 for w in hs if w["NAE"].get("faithful"))
        P3[d] = entry
    P3["holds"] = all(P3[d]["sampled"] and all(P3[d][law + " native"] > 0 for law in ("NAE", "PAR", "OR", "NOL"))
                      and P3[d]["NAE faithful"] > 0 for d in range(3, 8))
    klein = [w for w in flat if not w["orientable"]]
    tori = [w for w in flat if w["orientable"]]
    P4 = {"Klein bottles": len(klein), "Klein NAE allowed": sum(1 for w in klein if w["NAE"]["allowed"]),
          "tori NAE allowed": sum(1 for w in tori if w["NAE"]["allowed"]),
          "Klein PAR native (3-colourable)": sum(1 for w in klein if w["PAR"].get("native")),
          "tori PAR native (3-colourable)": sum(1 for w in tori if w["PAR"].get("native")), "tori": len(tori)}
    P4["holds"] = P4["Klein NAE allowed"] > 0 and P4["tori NAE allowed"] > 0
    viol = []
    measured = 0
    for rec in bonds:
        if not worlds[rec["world"]]["NAE"].get("faithful") or rec["NAE"] is None:
            continue
        measured += 1
        for dl, b, n in rec["NAE"]:
            if dl in (1, 2, 3) and b != dl + 1:
                viol.append([rec["V"], dl, b, n])
    P5 = {"tori measured": measured, "violations": viol}
    P5["holds"] = measured > 0 and not viol
    neg = [w for w in worlds if w["family"] == "surface d=7 sample"]
    extra = {"d=7 sample": {"classes": len(neg), "NAE allowed": sum(1 for w in neg if w["NAE"]["allowed"]),
                             "NAE faithful": sum(1 for w in neg if w["NAE"].get("faithful")),
                             "PAR native": sum(1 for w in neg if w["PAR"].get("native"))}}
    summary = {"P1": P1, "P2": P2, "P3": P3, "P4": P4, "P5": P5, "extra": extra,
               "controls": {"lattice tori = SAT tori (7..16)": all(lattice_check.values()) if lattice_check else None,
                            "mismatches": mismatches, "lemma failures": {"D4": d4, "D5": d5, "D6": d6},
                            "bond lemma failures": bond_lemma, "knotlab": kl},
               "seconds": round(time.time() - t0, 1)}
    log(json.dumps(summary, indent=1, default=str))
    with open(os.path.join(OUT, "census.json"), "w") as f:
        json.dump({"summary": summary, "worlds": worlds, "bonds": bonds}, f, default=str)


if __name__ == "__main__":
    main()
