"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001N (the referee's 001M family_m.py with the family changed): the four-addition
family, grown by its own moves and deduplicated up to isomorphism of the site graph with loose counts: a ternary seed (the only
three-place site); the first two additions unary with three fresh; exactly two further three-fresh additions, each with one, two or
three parents, at any later time and any legal holders; every other addition two- or three-parent with two fresh.  Its width is
2n + 5 (odd).  Tables are tested through D = 3, 4 and 5 and in full.

  WMAX=29 WORKERS=10 ../../../.venv/bin/python -B family_n.py gen        > referee_n_family_counts.json
  WMAX=29 WORKERS=10 ../../../.venv/bin/python -B family_n.py examine W  (streams one JSON line per member to family_four_W.jsonl)
  ../../../.venv/bin/python -B family_n.py cross W                       > referee_n_cross_W.json
"""
import json
import os
import pickle
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
import referee_f as F  # noqa: E402

WMAX = int(os.environ.get("WMAX", "29"))
FAMILY = "four"
WORKERS = int(os.environ.get("WORKERS", "10"))
CAP = 20000
LOOSE0 = 0                                  # (shrinks are not tracked for this family; the field reads minus the loose count)


def children(state):
    """state: (presentation, additions made, three-fresh additions after the first two (0, 1 or 2))."""
    T, k, used = state
    out = []
    for P in F.moves(T):
        if k < 2:
            if len(P) == 1:
                out.append((F.add(T, P, 3), k + 1, used))
            continue
        if len(P) in (2, 3):
            out.append((F.add(T, P, 2), k + 1, used))
        if used < 2:
            out.append((F.add(T, P, 3), k + 1, used + 1))
    return [s for s in out if F.width(s[0]) <= WMAX]


def key(state):
    T, k, used = state
    return (F.wl(T), used, min(k, 2))


def dedup(bucket):
    reps = []
    for s in bucket:
        G = F.graph(s[0])
        if not any(nx.is_isomorphic(G, H, node_match=F.nm) for H, _ in reps):
            reps.append((G, s))
    return [s for _, s in reps]


def part_gen():
    level = [(F.seed(), 0, False)]
    members = defaultdict(list)
    with Pool(WORKERS) as pool:
        while level:
            kids = [c for r in pool.map(children, level, chunksize=64) for c in r]
            buckets = defaultdict(list)
            for c in kids:
                buckets[key(c)].append(c)
            level = [s for r in pool.map(dedup, list(buckets.values()), chunksize=64) for s in r]
            for s in level:
                if s[2] == 2:
                    members[F.width(s[0])].append(s[0])
            print(len(level), file=sys.stderr, flush=True)
    pickle.dump(dict(members), open(HERE / f"family_{FAMILY}_members_{WMAX}.pkl", "wb"))
    return {f"width {w}": {"members": len(v), "by shrinks": dict(sorted(Counter(LOOSE0 - sum(T[2]) for T in v).items()))}
            for w, v in sorted(members.items())}


def examine(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    stars = {frozenset(S) for S in J}
    lt = F.legal_triples(T, J)
    row = {"T": T, "width": n, "shrinks": LOOSE0 - sum(T[2]), "legal": len(lt)}
    for name, C in (("D3", F.clip(K, 4)), ("D4", F.clip(K, 5)), ("D5", F.clip(K, 6)), ("full", K)):
        gens, nq, capped, q = F.generators(C, cap=CAP)
        row[name] = [F.keeps(gens, stars), F.keeps(gens, lt) if lt else True, capped]
        if name != "D3":
            row[f"inv {name}"] = F.invariant(C)
    return row


def part_examine(w):
    members = pickle.load(open(HERE / f"family_{FAMILY}_members_{WMAX}.pkl", "rb"))[w]
    path = HERE / f"family_{FAMILY}_{w}.jsonl"
    done = set()
    if path.exists():
        done = {json.loads(line)["i"] for line in open(path)}
    todo = [(i, T) for i, T in enumerate(members) if i not in done]
    with Pool(WORKERS) as pool, open(path, "a") as fh:
        for i, row in pool.imap_unordered(_ex, todo, chunksize=4):
            row["i"] = i
            row["T"] = [row["T"][0], list(row["T"][1]), list(row["T"][2])]
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    return summarize(w)


def _ex(arg):
    i, T = arg
    return i, examine(T)


def summarize(w):
    rows = [json.loads(l) for l in open(HERE / f"family_{FAMILY}_{w}.jsonl")]
    live = [r for r in rows if r["legal"]]
    dead = [r for r in rows if not r["legal"]]
    out = {"members examined": len(rows), "with a legal triple": len(live),
           "by shrinks (members, live)": {t: [sum(r["shrinks"] == t for r in rows), sum(r["shrinks"] == t for r in live)]
                                          for t in sorted({r["shrinks"] for r in rows})}}
    for name in ("D3", "D4", "D5", "full"):
        out[f"live: a symmetry through {name} moves a support / a legal triple"] = [sum(not r[name][0] for r in live), sum(not r[name][1] for r in live)]
        out[f"empty menu: a symmetry through {name} moves a support"] = sum(not r[name][0] for r in dead)
        out[f"searches capped through {name}"] = sum(r[name][2] for r in rows)
    out["first live member whose D3 symmetries move a triple (shrinks)"] = sorted({r["shrinks"] for r in live if not r["D3"][1]})
    out["empty-menu members whose full symmetries move a support, by shrinks"] = dict(Counter(r["shrinks"] for r in dead if not r["full"][0]))
    return out


def _pair(args):
    a, b, name = args
    out = []
    Ts = []
    for r in (a, b):
        T = (r["T"][0], tuple(r["T"][1]), tuple(r["T"][2]))
        J, n = F.supports(T)
        K, _ = F.bond_table(J, n)
        Ts.append((T, J, K if name == "full" else F.clip(K, 5)))
    (T1, J1, C1), (T2, J2, C2) = Ts
    p = F.isometric(C1, C2)
    if p is None:
        return None
    m1 = {frozenset(p[x] for x in t) for t in F.legal_triples(T1, J1)}
    m2 = {frozenset(t) for t in F.legal_triples(T2, J2)}
    s1 = {frozenset(p[x] for x in S) for S in J1}
    s2 = {frozenset(S) for S in J2}
    return {"pair": [a["i"], b["i"]], "legal": [a["legal"], b["legal"]], "menus carried": m1 == m2, "supports carried": s1 == s2}


def part_cross(w):
    rows = [json.loads(l) for l in open(HERE / f"family_{FAMILY}_{w}.jsonl")]
    out = {}
    with Pool(WORKERS) as pool:
        for name in ("D4", "full"):
            b = defaultdict(list)
            for r in rows:
                b[r[f"inv {name}"]].append(r)
            jobs = [(g[i], g[j], name) for g in b.values() if len(g) > 1 for i in range(len(g)) for j in range(i + 1, len(g))]
            res = [x for x in pool.map(_pair, jobs, chunksize=1) if x]
            out[f"through {name}"] = {"members": len(rows), "invariant buckets with two or more": sum(len(g) > 1 for g in b.values()),
                                      "pairs tested": len(jobs), "isometric pairs of distinct types": len(res),
                                      "... with a legal triple on either side": sum(1 for x in res if max(x["legal"]) > 0),
                                      "... menus not carried": sum(1 for x in res if not x["menus carried"]),
                                      "... supports not carried, with a legal triple": sum(1 for x in res if max(x["legal"]) > 0 and not x["supports carried"]),
                                      "examples": res[:5]}
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    if part == "gen":
        print(json.dumps(part_gen(), indent=1))
    elif part == "examine":
        print(json.dumps(part_examine(int(sys.argv[2])), indent=1))
    elif part == "summary":
        print(json.dumps(summarize(int(sys.argv[2])), indent=1))
    else:
        print(json.dumps(part_cross(int(sys.argv[2])), indent=1))
