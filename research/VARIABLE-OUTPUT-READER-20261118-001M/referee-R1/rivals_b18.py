"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001M (a copy of the referee's 001L rivals_l.py): every binary-third (001L) family member at width 18 (WIDTHS) against every
presentation the full law reaches at the same width (the referee's 001F census: one to three parents, two or three fresh, up to
isomorphism).  For each member, every rival of a different type whose table clipped through D = 4 (and, for comparison, through
D = 3) shares an invariant is tested for an exact isometry; for each isometric rival: does it carry the member's legal triples onto
the rival's, and its junction supports onto the rival's?  Same-type matches are the self-symmetries tested by family_l.py.

  WIDTHS=18,20,22,24 WORKERS=8 ../../../.venv/bin/python -B rivals_m.py > referee_m_rivals.json
"""
import json
import os
import pickle
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
import referee_f as F  # noqa: E402

WIDTHS = [int(w) for w in os.environ.get("WIDTHS", "18").split(",")]
WORKERS = int(os.environ.get("WORKERS", "10"))


def invs(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    return F.invariant(F.clip(K, 5)), F.invariant(F.clip(K, 4))


def check(args):
    T, rivals, L = args
    J, n = F.supports(T)
    K = F.bond_table(J, n)[0]
    C = F.clip(K, L)
    lt = {frozenset(t) for t in F.legal_triples(T, J)}
    stars = {frozenset(S) for S in J}
    G = F.graph(T)
    res = {"legal": len(lt), "candidates": len(rivals), "same type": 0, "isometric": 0, "menu not carried": 0, "supports not carried": 0,
           "examples": []}
    for R in rivals:
        if nx.is_isomorphic(G, F.graph(R), node_match=F.nm):
            res["same type"] += 1
            continue
        JR, _ = F.supports(R)
        p = F.isometric(C, F.clip(F.bond_table(JR, n)[0], L))
        if p is None:
            continue
        res["isometric"] += 1
        m = {frozenset(t) for t in F.legal_triples(R, JR)}
        bad_m = {frozenset(p[x] for x in t) for t in lt} != m
        bad_s = {frozenset(p[x] for x in S) for S in J} != {frozenset(S) for S in JR}
        res["menu not carried"] += bad_m
        res["supports not carried"] += bad_s
        if (bad_m or (lt and bad_s)) and len(res["examples"]) < 2:
            res["examples"].append({"source": [T[0], list(T[1]), list(T[2])], "rival": [R[0], list(R[1]), list(R[2])],
                                    "menus": [len(lt), len(m)], "map": p})
    return res


def main():
    levels = F.census(max(WIDTHS), workers=WORKERS)
    members = pickle.load(open(HERE / "../../VARIABLE-OUTPUT-READER-20261118-001L/referee-R1/family_members_32.pkl", "rb"))
    out = {}
    with Pool(WORKERS) as pool:
        for w in WIDTHS:
            riv = levels[w]
            iv = pool.map(invs, riv, chunksize=64)
            b5, b4 = defaultdict(list), defaultdict(list)
            for R, (i5, i4) in zip(riv, iv):
                b5[i5].append(R)
                b4[i4].append(R)
            mem = members[w]
            miv = pool.map(invs, mem, chunksize=4)
            res = {"full-law types at this width": len(riv), "family members": len(mem)}
            for L, b, j in ((5, b5, 0), (4, b4, 1)):
                rows = pool.map(check, [(T, b.get(mi[j], []), L) for T, mi in zip(mem, miv)], chunksize=1)
                for live in (True, False):
                    sel = [r for r in rows if (r["legal"] > 0) == live]
                    res[f"through D = {L - 1}, members {'with' if live else 'without'} a legal triple"] = {
                        "members": len(sel), "members found in the census (same type)": sum(r["same type"] > 0 for r in sel),
                        "isometric rivals of another type": sum(r["isometric"] for r in sel),
                        "... menu not carried": sum(r["menu not carried"] for r in sel),
                        "... supports not carried": sum(r["supports not carried"] for r in sel),
                        "examples": [e for r in sel for e in r["examples"]][:2]}
            out[f"width {w}"] = res
            print(w, json.dumps({k: v for k, v in res.items() if not isinstance(v, dict)}), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
