"""Referee R1 for CENSUS-READ-20261118-001 (own growth, tables and symmetry test; the study's exact_table_v2 is the object under test
and is run read-only as such; pass 5's per-stage records are read from runs/census-exact5 as data).

  ../../../.venv/bin/python -B referee_census.py <part> > referee_census_<part>.json      (from this directory)

Stages: every census arrangement grown by the referee's own engine (FRESH-COUNT-R1 / FIRST-KNOT-R1: the fewest counts, GF(2)
implied parity), round 0 and every later round to 8, stopping at a stall, at closing (the closed stage is kept) or past JMAX
junctions.  Each stage is matched to pass 5's record of the same arrangement and round (junctions, largest junction, loose count,
least distance).

Parts:
  tables   on every stage of at most 16 junctions (all arrangements, or a sample with SAMPLE): the referee's exact table by its own
           shore enumeration, written for closed stages too (no loose distinction: both sides connected among the junctions), and
           on stages of at most 14 distinctions also by brute force over the allowed states' minimal non-free sets; against
           exact_table_v2 at the study's horizon (largest + 2, pooled above).
  sym      at every stage where junctions meet at most once and there are at most SYMJ junctions: does any symmetry of the exact
           table move a junction?  Exact, by the twin quotient of the referee's 001F code (no cap reached is reported); against
           pass 5's recorded symmetry verdict ('moves', 'fixes', 'unknown', 'not_checked').
  large    a sample of stages of 17 to 40 junctions (SAMPLE arrangements): the referee's exact all-sides bond search from its
           RING-READ report (search_root: include/exclude growth with a max-flow cut) where a distinction is loose, its shore
           enumeration on closed stages of at most 20 junctions; against exact_table_v2.
  amend5   pass 3 (before Amendment 5) against pass 5 on the 1,925 arrangements both read: every stage whose R3n or R3 verdict
           changed, by cause (closed stage; R3n's dependent-candidate flag; other).
"""
import itertools
import json
import os
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/NAE-GROWTH-20261119-001/referee-R1"))
import referee_f as F  # noqa: E402
import referee_first as RFK  # noqa: E402

EXP = ROOT / "experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census"
INF = F.INF


def stars_of(key):
    """The start's stars: shared distinctions pair by pair in order, then each knot's loose ones (the census's convention)."""
    sizes, flat = key
    n = len(sizes)
    st = [[] for _ in range(n)]
    b = 0
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        for _ in range(m):
            st[i].append(b)
            st[j].append(b)
            b += 1
    for i in range(n):
        while len(st[i]) < sizes[i]:
            st[i].append(b)
            b += 1
    return st


def stages_of(key, jmax):
    G = RFK.Start(stars_of(key))
    out = [[list(s) for s in G.bits]]
    for _ in range(8):
        if len(G.bits) > jmax:
            break
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            break
        out.append([list(s) for s in G.bits])
    return [s for s in out if len(s) <= jmax]


def shore_table(stars):
    """K matrix over every bond (both sides connected), closed stages included: with no loose distinction the outside vertex is
    absent and both sides must be connected sets of junctions."""
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    J = [[idx[b] for b in s] for s in stars]
    n, nb = len(J), len(labels)
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    star = [sum(1 << x for x in S) for S in J]
    adj = [0] * n
    haslo = 0
    for x, ks in owner.items():
        if len(ks) == 2:
            adj[ks[0]] |= 1 << ks[1]
            adj[ks[1]] |= 1 << ks[0]
        else:
            haslo |= 1 << ks[0]
    full = (1 << n) - 1

    def grow(seed, U):
        comp = seed
        while True:
            new = comp
            m = comp
            while m:
                low = m & -m
                new |= adj[low.bit_length() - 1] & U
                m ^= low
            if new == comp:
                return comp
            comp = new
    K = np.full((nb, nb), INF, dtype=np.int64)
    np.fill_diagonal(K, 0)
    word = [0] * (1 << n)
    for U in range(1, 1 << n):
        low = U & -U
        word[U] = word[U ^ low] ^ star[low.bit_length() - 1]
        if grow(low, U) != U:
            continue
        O = full & ~U
        if haslo:
            if grow(O & haslo, O) != O:
                continue
        else:
            if not O or grow(O & -O, O) != O:
                continue
        w = word[U]
        ids = [x for x in range(nb) if w >> x & 1]
        s = len(ids)
        sub = K[np.ix_(ids, ids)]
        np.minimum(sub, s, out=sub)
        K[np.ix_(ids, ids)] = sub
    np.fill_diagonal(K, 0)
    return K, labels


def brute_table(stars):
    import referee_nae as RN
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    st = [[idx[b] for b in s] for s in stars]
    return RN.nae_table(len(labels), RN.parity_states(len(labels), st)), labels


def theirs(stars, H):
    sys.path.insert(0, str(EXP))
    import exact_table_v2 as X      # the object under test, read-only
    return X.exact_table([frozenset(s) for s in stars], H)


def records():
    rec = {}
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok" or not r["case"].startswith("census"):
            continue
        for a in r["result"]["arrangements"]:
            rec[a["index"]] = a
    return rec


def _tables(args):
    idx, key, recst = args
    out = Counter()
    bad = []
    for r, stars in enumerate(stages_of(tuple(map(tuple, key)), 16)):
        if r >= len(recst):
            out["stage not in the record"] += 1
            continue
        R = recst[r]
        K, labels = shore_table(stars)
        Kmax = max(len(s) for s in stars)
        H = Kmax + 2
        own = Counter(b for s in stars for b in s)
        closed = not any(c == 1 for c in own.values())
        same_stage = R["junctions"] == len(stars) and R["largest"] == Kmax and R["loose"] == sum(c == 1 for c in own.values())
        out["stages"] += 1
        out["closed stages"] += closed
        out["stage summary equals the record"] += same_stage
        T = theirs(stars, H)
        pos = {b: i for i, b in enumerate(labels)}
        agree = all(min(int(K[pos[a]][pos[b]]) - 1, H + 1) == d for (a, b), d in T.items())
        out["exact_table_v2 equals the referee's shore table (through the horizon)"] += agree
        out["... on closed stages"] += agree and closed
        mind = min(min(int(K[i][j]) - 1 for i in range(len(labels)) for j in range(i + 1, len(labels))), H + 1)
        out["least distance equals the record"] += mind == R["min_distance"]
        if len(labels) <= 14:
            Kb, _ = brute_table(stars)
            out["brute force checked"] += 1
            out["brute force equals the shore table"] += bool((Kb == K).all())
        if not agree and len(bad) < 3:
            bad.append({"index": idx, "round": r, "closed": closed})
    return out, bad


def part_tables():
    rec = records()
    keys = sorted(rec)
    s = int(os.environ.get("SAMPLE", "0"))
    if s:
        keys = sorted(random.Random(31).sample(keys, s))
    jobs = [(i, rec[i]["key"], rec[i]["stages"]) for i in keys]
    tot = Counter()
    bads = []
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        for c, b in pool.imap_unordered(_tables, jobs, chunksize=20):
            tot.update(c)
            bads += b
    return {"arrangements": len(jobs), **dict(tot), "disagreements (first)": bads[:10]}


def _sym(args):
    idx, key, recst, symj = args
    rows = []
    for r, stars in enumerate(stages_of(tuple(map(tuple, key)), symj)):
        if r >= len(recst):
            continue
        own = defaultdict(list)
        for j, s in enumerate(stars):
            for b in s:
                own[b].append(j)
        shared = Counter(tuple(sorted(js)) for js in own.values() if len(js) == 2)
        if shared and max(shared.values()) >= 2:
            continue
        K, labels = shore_table(stars)
        pos = {b: i for i, b in enumerate(labels)}
        S = {frozenset(pos[b] for b in s) for s in stars}
        gens, nq, capped, q = F.generators(K)
        moves = not F.keeps(gens, S)
        rows.append({"index": idx, "round": r, "junctions": len(stars), "mine": "moves" if moves else "fixes", "capped": capped,
                     "theirs": recst[r].get("symmetry", {}).get("search"), "r3n": recst[r].get("r3n")})
    return rows


def part_sym():
    rec = records()
    symj = int(os.environ.get("SYMJ", "14"))
    jobs = [(i, rec[i]["key"], rec[i]["stages"], symj) for i in sorted(rec)]
    rows = []
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        for rs in pool.imap_unordered(_sym, jobs, chunksize=20):
            rows += rs
    out = {"meet-once stages classified": len(rows), "searches capped": sum(r["capped"] for r in rows)}
    for lo, hi in ((1, 10), (11, symj)):
        sel = [r for r in rows if lo <= r["junctions"] <= hi]
        out[f"{lo} to {hi} junctions"] = {"stages": len(sel), "mine x theirs": {f"{a} / {b}": c for (a, b), c in sorted(Counter((r["mine"], r["theirs"]) for r in sel).items())},
                                         "R3n verdicts where mine is 'fixes'": dict(Counter(r["r3n"] for r in sel if r["mine"] == "fixes"))}
    return out


def _large(args):
    idx, key = args
    sys.path.insert(0, str(ROOT / "research/RING-READ-20261118-001/referee-R1"))
    import referee_ringread as RR
    out = Counter()
    for stars in stages_of(tuple(map(tuple, key)), 40):
        n = len(stars)
        if n <= 16:
            continue
        own = defaultdict(list)
        for j, st in enumerate(stars):
            for b in st:
                own[b].append(j)
        closed = not any(len(js) == 1 for js in own.values())
        Kmax = max(len(st) for st in stars)
        H = Kmax + 2
        L = H + 1
        if closed:
            if n > 20:
                out["closed, over 20 junctions: skipped"] += 1
                continue
            K, labels = shore_table(stars)
            mine = {(a, b): min(int(K[i][j]) - 1, H + 1) for i, a in enumerate(labels) for j, b in enumerate(labels) if a < b}
        else:
            adj = defaultdict(dict)
            for b, js in own.items():
                u, v = (js[0], js[1]) if len(js) == 2 else (js[0], n)
                adj[u][v] = adj[u].get(v, 0) + 1
                adj[v][u] = adj[v].get(u, 0) + 1
            masks = [sum(1 << b for b in st) for st in stars]
            best = {}
            for r in range(n):
                _, _, _, keep = RR.search_root((adj, n, r, L, 10 ** 9, L, masks))
                for side, w in keep:
                    bits = [b for b in range(w.bit_length()) if w >> b & 1]
                    for p in itertools.combinations(bits, 2):
                        if best.get(p, 99) > len(bits):
                            best[p] = len(bits)
            labels = sorted(own)
            mine = {p: min(best.get(p, 99) - 1, H + 1) for p in itertools.combinations(labels, 2)}
        T = theirs(stars, H)
        out["stages"] += 1
        out["closed"] += closed
        out["equal"] += T == mine
    return out


def part_large():
    rec = records()
    keys = sorted(random.Random(37).sample(sorted(rec), int(os.environ.get("SAMPLE", "600"))))
    tot = Counter()
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        for c in pool.imap_unordered(_large, [(i, rec[i]["key"]) for i in keys], chunksize=4):
            tot.update(c)
    return {"arrangements sampled": len(keys), **dict(tot)}


def part_amend5():
    p3 = {}
    for line in open(ROOT / "runs/census-exact/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok" or not r["case"].startswith("census"):
            continue
        for a in r["result"]["arrangements"]:
            p3[json.dumps(a["key"])] = a
    p5 = {json.dumps(a["key"]): a for a in records().values()}
    common = sorted(set(p3) & set(p5))
    ch = Counter()
    ex = []
    for i in common:
        s3, s5 = p3[i]["stages"], p5[i]["stages"]
        for r in range(min(len(s3), len(s5))):
            a, b = s3[r], s5[r]
            ch["stages compared"] += 1
            closed = b.get("loose", 1) == 0
            flag = bool(b.get("r3n_flags", {}).get("dependent")) or any("depend" in k for k in b.get("r3n_flags", {}))
            for name in ("r3", "r3n"):
                if a.get(name) != b.get(name):
                    cause = "closed stage" if closed else ("dependent-candidate flag" if flag else "other")
                    ch[f"{name} changed: {a.get(name)} -> {b.get(name)} ({cause})"] += 1
                    if cause == "other" and len(ex) < 5:
                        ex.append({"index": i, "round": r, "reader": name, "pass 3": a.get(name), "pass 5": b.get(name),
                                   "flags 5": b.get("r3n_flags"), "junctions": b.get("junctions")})
    return {"arrangements in both passes": len(common), **dict(sorted(ch.items())), "examples of 'other'": ex}


if __name__ == "__main__":
    print(json.dumps({"tables": part_tables, "sym": part_sym, "amend5": part_amend5, "large": part_large}[sys.argv[1]](), indent=1, default=str))
