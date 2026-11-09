"""FLIP-RULE-20261109-001B-E001: persistence without a flip, a search of small maps (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/FLIP-RULE-20261109-001B/FLIP-RULE-20261109-001B-E001_small_maps/run/result.json

A map on E contacts is a permutation sigma of the darts 0 .. 2E - 1 (the next dart counterclockwise at a ring), with alpha(d) = d xor 1
and contact(d) = d >> 1; rings are the cycles of sigma. A map is kept when <sigma, alpha> is transitive (connected) and no contact has
both darts in one cycle (no contact joins a ring to itself). As a network of equally spaced rule-60 rings with law (12, 12) contacts,
the contact graph has an arc from contact(d) to contact(sigma(d)) for every dart d (loopnet_lib.corners), and a contact c persists exactly
when every count of closed walks c -> c of length k >= 1 is even (LOOP-NET-20261108-001A, Theorem 2 (a), at equal spacing), decided at
k = 1 .. E + 1 since the counts satisfy a recurrence of order at most E. A flip at c is an automorphism phi (phi sigma = sigma phi,
phi alpha = alpha phi) with phi(2c) = 2c + 1; a reflection at c is an anti-automorphism psi (psi sigma = sigma^-1 psi, psi alpha =
alpha psi) with psi(2c) in {2c, 2c + 1}."""
import collections
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "FLIP-RULE-20261109-001B" / "FLIP-RULE-20261109-001B-E001_small_maps" / "run"
EXHAUSTIVE = range(1, 6)
SAMPLED = {6: 400000, 7: 400000}
SEED = 20261109


def valid(sig):
    n = len(sig)
    seen = [False] * n
    cyc = [0] * n
    k = 0
    for s in range(n):
        if not seen[s]:
            x = s
            while not seen[x]:
                seen[x] = True
                cyc[x] = k
                x = sig[x]
            k += 1
    for e in range(n // 2):
        if cyc[2 * e] == cyc[2 * e + 1]:
            return False
    reach, stack = {0}, [0]
    while stack:
        x = stack.pop()
        for y in (sig[x], x ^ 1):
            if y not in reach:
                reach.add(y)
                stack.append(y)
    return len(reach) == n


def persistent(sig):
    n = len(sig)
    E = n // 2
    rows = [0] * E
    for d in range(n):
        rows[d >> 1] ^= 1 << (sig[d] >> 1)
    out = []
    for c in range(E):
        v, ok = 1 << c, True
        for k in range(1, E + 2):
            w, x = 0, v
            while x:
                low = x & -x
                w ^= rows[low.bit_length() - 1]
                x ^= low
            v = w
            if v >> c & 1:
                ok = False
                break
        out.append(ok)
    return out


def build(sig, inv, start, image, reverse):
    n = len(sig)
    phi = {start: image}
    stack = [start]
    while stack:
        d = stack.pop()
        pairs = [(sig[d], inv[phi[d]] if reverse else sig[phi[d]]), (d ^ 1, phi[d] ^ 1)]
        for a, b in pairs:
            if a in phi:
                if phi[a] != b:
                    return False
            else:
                phi[a] = b
                stack.append(a)
    return len(phi) == n and len(set(phi.values())) == n


def symmetries(sig, c):
    inv = [0] * len(sig)
    for d, s in enumerate(sig):
        inv[s] = d
    flip = build(sig, inv, 2 * c, 2 * c + 1, False)
    refl = build(sig, inv, 2 * c, 2 * c, True) or build(sig, inv, 2 * c, 2 * c + 1, True)
    return flip, refl


def canonical(sig):
    """the least BFS code over roots: an orientation-preserving isomorphism invariant"""
    n = len(sig)
    best = None
    for r in range(n):
        lab, order = {r: 0}, [r]
        i = 0
        while i < len(order):
            x = order[i]
            for y in (sig[x], x ^ 1):
                if y not in lab:
                    lab[y] = len(order)
                    order.append(y)
            i += 1
        code = tuple((lab[sig[x]], lab[x ^ 1]) for x in order)
        if best is None or code < best:
            best = code
    return best


def examine(sig, acc, exceptions):
    if not valid(sig):
        return
    acc["maps"] += 1
    pers = persistent(sig)
    for c, p in enumerate(pers):
        flip, refl = symmetries(sig, c)
        acc["contacts"] += 1
        acc["persistent"] += p
        acc["with a flip"] += flip
        if p and not flip:
            acc["persistent without a flip"] += 1
            acc["of those, with a reflection"] += refl
            exceptions.add((canonical(sig), c, refl))
        if flip and not p:
            acc["flip but not persistent"] += 1


def exhaustive_chunk(args):
    E, first = args
    n = 2 * E
    acc, exc = collections.Counter(), set()
    rest = [d for d in range(n) if d != first]
    for tail in itertools.permutations(rest):
        sig = (first,) + tail
        examine(sig, acc, exc)
    return E, acc, exc


def sampled_chunk(args):
    E, count, seed = args
    rng = random.Random(seed)
    n = 2 * E
    acc, exc = collections.Counter(), set()
    for _ in range(count):
        p = list(range(n))
        rng.shuffle(p)
        examine(tuple(p), acc, exc)
    return E, acc, exc


def main():
    t0 = time.time()
    jobs = [(E, f) for E in EXHAUSTIVE for f in range(2 * E)]
    sjobs = [(E, cnt // 16, SEED * 100 + E * 16 + i) for E, cnt in SAMPLED.items() for i in range(16)]
    with Pool(16) as pool:
        res = pool.map(exhaustive_chunk, jobs, chunksize=1)
        sres = pool.map(sampled_chunk, sjobs, chunksize=1)
    out = {}
    for label, rs in (("exhaustive", res), ("sampled", sres)):
        by = collections.defaultdict(collections.Counter)
        exc = collections.defaultdict(set)
        for E, acc, ex in rs:
            by[E].update(acc)
            exc[E] |= ex
        for E in sorted(by):
            maps_exc = {code for code, c, refl in exc[E]}
            out["%s, E = %d" % (label, E)] = {**dict(by[E]), "distinct maps with a persistent contact without a flip": len(maps_exc),
                                             "examples (canonical codes, contact, reflection)": [[list(map(list, code)), c, refl] for code, c, refl in sorted(exc[E])[:20]]}
    result = {"experiment": "FLIP-RULE-20261109-001B-E001", "readings": out,
              "H1 every persistent contact has a flip (exhaustive, E <= 5)": all(v.get("persistent without a flip", 0) == 0 for k, v in out.items() if k.startswith("exhaustive")),
              "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if not kk.startswith("examples")} if isinstance(v, dict) else v)
                      for k, v in result["readings"].items()}, indent=1))
    print("H1:", result["H1 every persistent contact has a flip (exhaustive, E <= 5)"], result["seconds"], "s")


if __name__ == "__main__":
    main()
