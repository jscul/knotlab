#!/usr/bin/env python3
"""Checks for SEPARATE-20261108-001A: a cut separates a path; a cycle of rings needs two.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes."""
import hashlib
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import net_lib as N  # noqa: E402

PL = N.PL
T0 = time.time()
OUT = {}
H = 300


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def odd(n, k):
    return n >= 0 and (n & k) == k


def lucas(d, e, h=H):
    return [T for T in range(1, h + 1) if odd(T - d, e)]


def path_net(n, s, ks):
    contacts = [(0, 0, 1, 0, (10, 10))] + [(i - 1, ks[i - 2], i, 0, (6, 10)) for i in range(2, n)]
    return (s,) * n, (60,) * n, contacts


def cycle_net(s, k0, k1, k2, k3, around=False):
    if around:      # every contact reads both neighbours on the ring before it and its partner on the next
        contacts = [(0, 0, 1, 0, (10, 10)), (1, k1, 2, 0, (6, 10)), (2, k2, 3, 0, (6, 10)), (3, k3, 0, k0, (6, 10))]
    else:           # two routes from R0 to R2
        contacts = [(0, 0, 1, 0, (10, 10)), (0, k0, 3, 0, (10, 10)), (1, k1, 2, 0, (6, 10)), (3, k3, 2, k2, (6, 10))]
    return (s,) * 4, (60,) * 4, contacts


def persists(net, c, cut=()):
    sizes, rules, contacts = net
    rows, Nn, blocks = N.matrix(sizes, rules, contacts, cut)
    o = N.orbit(rows, 1 << c)
    ra, rb = contacts[c][0], contacts[c][2]
    return all(N.row_at(o, T) & N.mask(blocks, ra) and N.row_at(o, T) & N.mask(blocks, rb) for T in range(1, o[1] + o[2] + 8))


def mirrored(net, rng):
    sizes, rules, contacts = net
    for ring in range(len(sizes)):
        if rng.random() < 0.5:
            sizes, rules, contacts = N.mirror(sizes, rules, contacts, ring)
    return sizes, rules, contacts


def theorem1(args):
    n, s, ks, seed = args
    net = path_net(n, s, ks)
    if seed is not None:
        net = mirrored(net, random.Random(seed))
    e = sum(k - 1 for k in ks)
    bad = int(N.needs(*net, n - 2, 0, H) != lucas(n - 1, e))
    for i in range(n - 1):
        bad += N.needs(*net, n - 2, 0, H, cut=(i,)) != []
        bad += not all(persists(net, c, cut=(i,)) for c in range(n - 1) if c != i)
    return bad


def theorem2(args):
    s, ks, seed = args
    k0, k1, k2, k3 = ks
    net = cycle_net(s, k0, k1, k2, k3)
    if seed is not None:
        net = mirrored(net, random.Random(seed))
    S1, S3 = lucas(2, k1 - 1), lucas(2, k3 - 1)
    ok = all(persists(net, c) for c in range(4))
    ok &= N.needs(*net, 2, 0, H) == S1 and N.needs(*net, 3, 0, H) == S3
    ok &= N.needs(*net, 2, 0, H, cut=(0,)) == [] and N.needs(*net, 3, 0, H, cut=(0,)) == S3
    ok &= N.needs(*net, 2, 0, H, cut=(1,)) == S1 and N.needs(*net, 3, 0, H, cut=(1,)) == []
    ok &= N.needs(*net, 2, 0, H, cut=(0, 1)) == [] and N.needs(*net, 3, 0, H, cut=(0, 1)) == []
    ok &= all(persists(net, c, cut=(0,)) for c in (1, 2, 3)) and all(persists(net, c, cut=(1,)) for c in (0, 2, 3))
    return ok


def remark(args):
    s, ks = args
    net = cycle_net(s, *ks, around=True)
    S1 = lucas(2, ks[1] - 1)
    pre = N.needs(*net, 1, 0, H) == S1 and bool(N.needs(*net, 2, 0, H))
    post = N.needs(*net, 1, 0, H, cut=(0,)) == [] and N.needs(*net, 2, 0, H, cut=(0,)) == []
    return pre and post and all(persists(net, c) for c in range(4))


def full(args):
    net, contact, ring, cut, horizon = args
    return N.needs(*net, contact, ring, horizon, cut) == N.needs_full(*net, contact, ring, horizon, cut)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith("manifest.json")}
    check("0 dependency artifacts bound by hash; upstream statuses", not bad and all(s_ == "Proved" for s_ in status.values()),
          {"mismatched": bad, "statuses": status})

    rng = random.Random(20261108)
    mism = 0
    for _ in range(500):
        n = rng.randint(3, 5)
        sizes = tuple(rng.randint(3, 6) for _ in range(n))
        ks = [rng.randint(1, sizes[i] - 1) for i in range(1, n - 1)]
        rules = tuple(rng.choice(sorted(PL.LIN)) for _ in range(n))
        laws = tuple(("self-blind", rng.choice((12, 10, 6)), rng.choice((12, 10, 6))) for _ in range(n - 1))
        contacts = [(i - 1, 0 if i == 1 else ks[i - 2], i, 0, laws[i - 1][1:]) for i in range(1, n)]
        rows, Nn, blocks = N.matrix(sizes, rules, contacts)
        prow, PN, pblocks = PL.linear_matrix(rules, sizes, ks, laws)
        for c in range(n - 1):
            o1, o2 = N.orbit(rows, 1 << c), N.orbit(prow, 1 << c)
            for T in range(1, 60):
                for i in range(n):
                    mism += bool(N.row_at(o1, T) & N.mask(blocks, i)) != bool(N.row_at(o2, T) & PL.mask(pblocks, f"R{i}"))
    small = [(cycle_net(4, 2, 2, 2, 2), c, 0, cut, 24) for c in (2, 3) for cut in ((), (0,), (1,), (0, 1))]
    with Pool(8) as pool:
        fs = pool.map(full, small)
    check("1 net_lib agrees with path_lib on 500 random linear paths, and its full-state-space reading with its row sequences on a small cycle",
          mism == 0 and all(fs), {"paths": 500, "mismatched verdicts": mism, "small-cycle readings agreeing": sum(fs)})

    jobs = [(n, s, ks, None) for n in range(3, 9) for s in range(4, 15) for ks in itertools.product((2, s - 2), repeat=n - 2)]
    jobs += [(rng.randint(3, 7), None, None, k) for k in range(300)]
    jobs = [(n, s if s else rng.randint(4, 12), list(ks) if ks else None, seed) for (n, s, ks, seed) in jobs]
    jobs = [(n, s, ks if ks is not None else [rng.choice((2, s - 2)) for _ in range(n - 2)], seed) for (n, s, ks, seed) in jobs]
    with Pool(16) as pool:
        res = pool.map(theorem1, jobs, chunksize=4)
    check("2 Theorem 1 for 3 to 8 rings at ring sizes 4 to 14, every choice of positions, each contact cut, and on 300 random mirrored paths",
          sum(res) == 0, {"paths": len(jobs), "failures": sum(res)})

    jobs = [(s, ks, None) for s in range(4, 25) for ks in itertools.product((2, s - 2), repeat=4)]
    jobs += [(s, [rng.choice((2, s - 2)) for _ in range(4)], k) for k, s in enumerate(rng.randint(4, 14) for _ in range(300))]
    with Pool(16) as pool:
        res = pool.map(theorem2, jobs, chunksize=4)
    check("3 Theorem 2 at ring sizes 4 to 24, all 16 choices of positions, every cut of one or both route contacts, and on 300 random "
          "mirrored cycles", all(res), {"cycles": len(jobs), "failures": sum(1 for r in res if not r)})

    jobs = [(s, ks) for s in range(4, 17) for ks in itertools.product((2, s - 2), repeat=4)]
    with Pool(16) as pool:
        res = pool.map(remark, jobs, chunksize=4)
    check("4 the remark: with the contacts oriented round the cycle, R2 needs R0 only through c01 and cutting c01 separates, sizes 4 to 16",
          all(res), {"cycles": len(jobs), "failures": sum(1 for r in res if not r)})

    jobs = [(path_net(3, s, [k]), 1, 0, cut, 32) for s in (4, 5) for k in (2, s - 2) for cut in ((), (0,), (1,))]
    jobs += [(path_net(4, 4, [2, 2]), 2, 0, cut, 32) for cut in ((), (0,), (1,), (2,))]
    jobs += [(cycle_net(s, *ks), c, 0, cut, 24) for s in (4, 5) for ks in itertools.product((2, s - 2), repeat=4)
             for c in (2, 3) for cut in ((), (0,), (1,), (0, 1))]
    with Pool(16) as pool:
        res = pool.map(full, jobs, chunksize=1)
    check("5 full state spaces: Theorem 1 for three rings at sizes 4 and 5 and four rings at size 4, and Theorem 2 at sizes 4 and 5, every cut",
          all(res), {"readings": len(jobs), "agree": sum(res)})

    out = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
