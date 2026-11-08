#!/usr/bin/env python3
"""Checks for RECUR-PROOF-20261108-001A: one-sided additive paths compose at recurring lags at every ring size.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes. References: NATIVE-PATH-20261108-001A's path_lib (the path
layout and the row-sequence reduction), RECUR-PATH-20261108-001A-E002's recur_lib and its full-state-space reading."""
import hashlib
import importlib.util
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E2 = ROOT / "experiments/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed"
FAMS = ROOT / "artifacts/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed/run/families.json"
sys.path.insert(0, str(E2))
spec = importlib.util.spec_from_file_location("recur_run", E2 / "run.py")
RUN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RUN)
R, G, PL = RUN.R, RUN.G, RUN.PL
T0 = time.time()
OUT = {}
SIZES = range(4, 41)


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def side(rule):
    """the contact's partner on a ring: its right neighbour (law 10) under rule 60, its left neighbour (law 12) under rule 102"""
    return 10 if rule == 60 else 12


def family(rules, v):
    laws = (("self-blind", side(rules[0]), side(rules[1])), ("self-blind", 6, side(rules[2])), ("self-blind", 6, side(rules[3])))
    return tuple(rules), laws, tuple(v)


THEOREM = [family(r, v) for r in itertools.product((60, 102), repeat=4) for v in itertools.product((0, 1), repeat=2)]


def m_of(rules, ks, s):
    kp = [k if r == 60 else s - k for k, r in zip(ks, rules[1:3])]
    return kp[0] + kp[1] - 2


def odd(n, k):
    return n >= 0 and (n & k) == k


def mirror(path, ring):
    """Lemma 2: mirror one ring of a path (rule 60 <-> 102, its contacts' left and right reads swapped, position k <-> s - k)"""
    rules, sizes, ks, laws = path
    rules, ks, laws = list(rules), list(ks), [list(l) for l in laws]
    swap = {10: 12, 12: 10, 6: 6}
    rules[ring] = {60: 102, 102: 60}[rules[ring]]
    if ring in (1, 2):
        ks[ring - 1] = sizes[ring] - ks[ring - 1]
    if ring >= 1:
        laws[ring - 1][2] = swap[laws[ring - 1][2]]       # the contact before the ring reads it as its second ring
    if ring <= 2:
        laws[ring][1] = swap[laws[ring][1]]               # the contact after the ring reads it as its first ring
    return tuple(rules), sizes, ks, tuple(tuple(l) for l in laws)


def predictions(fam):
    """parts 1 and 2 of the theorem at every lag through the eventual cycle, and the composing share, at every size"""
    rules3, laws3, v = fam
    bad = lags = 0
    shares = []
    for s in SIZES:
        rules, sizes, ks, laws = G.path("two apart", s, rules3, laws3, v)
        m = m_of(rules, ks, s)
        rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
        msk = [PL.mask(blocks, f"R{i}") for i in range(4)]
        orbs = [R.orbit(rows, 1 << c, 10 ** 6) for c in range(3)]
        H = max(o[1] + o[2] for o in orbs) + 64
        for T in range(1, H):
            rw = [R.row_at(o, T) for o in orbs]
            lags += 1
            pers = all(rw[c] & msk[c] and rw[c] & msk[c + 1] for c in range(3))
            bad += (not pers) or (not rw[2] & msk[3]) or (bool(rw[2] & msk[0]) != odd(T - 3, m))
        seq, T1, p = orbs[2]
        cyc = [seq[T1 - 1 + j] for j in range(p)]
        share = sum(1 for r in cyc if r & msk[0] and r & msk[3]) / p
        shares.append(share == 2.0 ** (-bin(m).count("1")))
    return bad, lags, all(shares)


def mirror_job(fam):
    """Lemma 2 on this family: mirroring every rule-102 ring gives the rule-60 family with the same three readings at sizes 4 to 12"""
    rules3, laws3, v = fam
    same = True
    for s in range(4, 13):
        p = G.path("two apart", s, rules3, laws3, v)
        q = p
        for ring in range(4):
            if q[0][ring] == 102:
                q = mirror(q, ring)
        target_v = tuple(0 if k == 2 else 1 for k in q[2])
        t = G.path("two apart", s, (60, 60, 60, 60), family((60, 60, 60, 60), target_v)[1], target_v)
        same &= (q[0], q[1], list(q[2]), q[3]) == (t[0], t[1], list(t[2]), t[3])
        same &= RUN.triple(R.analyze(*p)) == RUN.triple(R.analyze(*q))
    return same


def full_job(args):
    fam, s = args
    return RUN.brute(*G.path("two apart", s, *fam))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(("manifest.json", "contract.json"))}
    check("0 dependency artifacts bound by hash; upstream statuses", not bad and all(s_ in ("Proved", "passed", "Frozen") for s_ in status.values()),
          {"mismatched": bad, "statuses": status})

    rows = json.loads(FAMS.read_text())["rows"]
    found = {(tuple(p[1]), tuple(tuple(l) for l in p[2]), tuple(p[3])) for p in rows
             if p[0] == "two apart" and all(str(s) in p[4] and p[4][str(s)][1] is True for s in G.SIZES["two apart"])}
    with Pool(16) as pool:
        mir = pool.map(mirror_job, THEOREM)
    check("1 the 64 families are the mirror images of the four rule-60 families, with the stated laws, and are exactly E002's 64 distinct "
          "two-apart families with every contact persistent at every size", set(THEOREM) == found and len(found) == 64 and all(mir),
          {"theorem's families": len(THEOREM), "E002's": len(found), "equal": set(THEOREM) == found, "mirror checks": sum(mir)})

    rng = random.Random(20261108)
    okl = 0
    for _ in range(2000):
        n1, n2, c = rng.randint(0, 1), rng.randint(0, 1), rng.randint(0, 1)
        n10, n20 = n1, n2
        us = [rng.randint(0, 1) for _ in range(40)]
        good = True
        for T in range(40):
            n1, n2, c = n1 ^ c, n2 ^ c, n1 ^ n2 ^ us[T]
            good &= c == (n10 ^ n20 ^ us[T])
        okl += good
    check("2 Lemma 1 on 2,000 random three-cell loops with random inputs: c(T) = n(0) + n'(0) + u(T - 1)", okl == 2000, {"loops": 2000, "agree": okl})

    with Pool(16) as pool:
        pr = pool.map(predictions, THEOREM)
    check("3 the theorem's predictions (every contact binds both rings, c3 binds D at every lag and A exactly when C(T - 3, m) is odd) at "
          "every lag through the eventual cycle, all 64 families, ring sizes 4 to 40",
          sum(b for b, l, s_ in pr) == 0, {"lags": sum(l for b, l, s_ in pr), "mismatches": sum(b for b, l, s_ in pr)})
    check("4 the last contact's composing share equals 2^(-w), w the number of ones in m, all 64 families, sizes 4 to 40",
          all(s_ for b, l, s_ in pr), {"families": len(pr), "agree": sum(1 for b, l, s_ in pr if s_)})

    with Pool(16) as pool:
        fs = pool.map(full_job, [(f, s) for f in THEOREM for s in (4, 5)], chunksize=1)
    check("5 full state spaces at ring sizes 4 and 5 (13 and 17 bits), all 64 families: every lag no, recurring with every contact "
          "persistent yes, binding there yes", all(b == [False, True, True] for b in fs), {"paths": len(fs), "agree": sum(1 for b in fs if b == [False, True, True])})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
