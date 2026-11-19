"""Referee R1 for UNIQUE-TABLE-20261119-001: an independent count of the same-equation rivals, against the study's Whitney
enumeration (`same_code_rivals` in runs/unique-table*, read as data).

A rival with the same equation space has every junction star a bond of its own wired graph, and bonds are the minimal nonzero
words of the common space, so every rival star is a minimal word of the truth's space.  So: list every minimal word of size three
or more (the referee's closed-aware shore enumeration over the truth's junctions), and search, including or excluding each in turn, for every collection
of at most n of them with every distinction in one or two, no two sharing two distinctions, the same span as the truth, and every
junction's star a bond (no cut vertex but the outside); the truth itself excluded.  The truth's stages are regrown by the
referee's own engine from each record's start and round.

  ../../../.venv/bin/python -B samecode.py > referee_unique_samecode.json
"""
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import referee_unique as RU  # noqa: E402

RC = RU.RC


def minimal_words(stars):
    """Every bond's word (both sides connected; closed-aware), as bitmasks."""
    n = len(stars)
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    star = [sum(1 << x for x in s) for s in stars]
    adj = [0] * n
    haslo = 0
    for x, ks in own.items():
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
    words = set()
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
        elif not O or grow(O & -O, O) != O:
            continue
        words.add(word[U])
    return words


def rivals(stars, cap=3000000):
    n = len(stars)
    nb = 1 + max(max(s) for s in stars)
    truth = frozenset(sum(1 << x for x in s) for s in stars)
    code = RU.span(stars)
    cands = sorted(w for w in minimal_words(stars) if bin(w).count("1") >= 3)
    by_bit = defaultdict(list)
    for w in cands:
        for x in range(nb):
            if w >> x & 1:
                by_bit[x].append(w)
    found = []
    cov = [0] * nb
    chosen = []
    steps = [0]
    last_index = {x: max((i for i, w in enumerate(cands) if w >> x & 1), default=-1) for x in range(nb)}

    def go(i):
        """Include or exclude candidate i (in order), keeping every distinction in at most two chosen words, no two chosen words
        sharing two, at most n chosen; every distinction still uncovered must have a later candidate."""
        steps[0] += 1
        if steps[0] > cap:
            return
        if any(cov[x] == 0 and last_index[x] < i for x in range(nb)):
            return
        if i == len(cands):
            S = [[y for y in range(nb) if w >> y & 1] for w in chosen]
            if frozenset(chosen) != truth and RU.span(S) == code and RU.legal_static(S)[0]:
                found.append(frozenset(chosen))
            return
        w = cands[i]
        if len(chosen) < n and all(cov[x] < 2 for x in range(nb) if w >> x & 1) and \
                not any(bin(w & c).count("1") >= 2 for c in chosen):
            chosen.append(w)
            for y in range(nb):
                if w >> y & 1:
                    cov[y] += 1
            go(i + 1)
            chosen.pop()
            for y in range(nb):
                if w >> y & 1:
                    cov[y] -= 1
        go(i + 1)
    go(0)
    return len(set(found)), steps[0] > cap


def records():
    rec = {}
    for run in ("unique-table", "unique-table-amend", "unique-table-amend2"):
        p = ROOT / "runs" / run / "results.jsonl"
        if not p.exists():
            continue
        for line in open(p):
            r = json.loads(line)
            if r.get("status") != "ok":
                continue
            x = r["result"]
            if "same_code_rivals" in x:
                rec[(json.dumps(x["key"]), x["round"])] = x
    return rec


def one(args):
    key, rnd, theirs, capped_theirs = args
    G = RU.RFK.Start(RC.stars_of(tuple(map(tuple, key))))
    for _ in range(rnd):
        if G.step(RU.RFK.fewest, None, None) != "ok":
            return None
    stars = [sorted(s) for s in G.bits]
    mine, capped = rivals(stars)
    return {"key": key, "round": rnd, "junctions": len(stars), "mine": mine, "theirs": theirs, "capped": capped or capped_theirs}


if __name__ == "__main__":
    rec = records()
    jobs = [(json.loads(k[0]), k[1], v["same_code_rivals"], v.get("same_code_capped", False)) for k, v in rec.items()]
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        rows = [r for r in pool.map(one, jobs, chunksize=4) if r]
    agree = [r for r in rows if not r["capped"]]
    print(json.dumps({"stages compared": len(rows), "capped (either side)": sum(r["capped"] for r in rows),
                      "same count": sum(r["mine"] == r["theirs"] for r in agree),
                      "same verdict (a same-equation rival exists or not)": sum((r["mine"] > 0) == (r["theirs"] > 0) for r in agree),
                      "stages with a same-equation rival (mine, theirs)": [sum(r["mine"] > 0 for r in agree), sum(r["theirs"] > 0 for r in agree)],
                      "disagreements": [r for r in agree if (r["mine"] > 0) != (r["theirs"] > 0)][:10],
                      "count differences (first)": [r for r in agree if r["mine"] != r["theirs"]][:10]}, indent=1))
