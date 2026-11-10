"""REACH-HALVES-20261110-001B checks (--write rewrites result.json).

0 the dependency bound by hash; 1 Proposition 5's criterion computed at sides 3 to 26 (which sides have a contact with a cyclic basis
vector in every ring, which have none at all), with full reach read at every side; 2 the census B2 (research/REACH-HALVES-20261110-001/
census.json, run by run_census.py as REACH-HALVES-B2), bound by hash, against its frozen prediction, with the failing sets recomputed
from its ring lists: the quarter-turn orbit of (X, X + 1), X = n + 2, n + 6, ..., 2n - 6, each missing one corner ring and its two
neighbours."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/REACH-HALVES-20261110-001A/REACH-HALVES-20261110-001A-P001_the_failure_at_every_power_of_two"))
from halves_lib import box  # noqa: E402

DEP = "proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two/manifest.json"
WANT = "affc32533a4d960bd72b879ef5870513fe8ffaad5614bf296900aa27d5d618d0"
checks = {}


def rec(name, ok, info=None):
    checks[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, flush=True)


def krylov(B, x):
    """dimension of the cyclic space of x and the union of its supports"""
    basis, row, union = {}, x, 0
    while True:
        union |= row
        y = row
        while y:
            t = y.bit_length() - 1
            if t not in basis:
                break
            y ^= basis[t]
        if not y:
            return len(basis), union
        basis[y.bit_length() - 1] = y
        row = B.step(row)


def check1():
    meets, full, info = [], {}, {}
    for n in range(3, 27):
        B = box(n)
        M = len(B.contacts)
        dims, unions = {}, {}
        for c in B.contacts:
            dims[c], unions[c] = krylov(B, 1 << B.idx(*c))
        rings = [[q for q in [(2*i+1, 2*j), (2*i-1, 2*j), (2*i, 2*j+1), (2*i, 2*j-1)] if B.inside(*q)] for i in range(n) for j in range(n)]
        crit = all(any(dims[c] == M for c in r) for r in rings)
        allc = sum(1 << B.idx(*c) for c in B.contacts)
        fr = all(any(unions[c] >> B.idx(*d) & 1 for d in r) for c in B.contacts for r in rings)
        info[str(n)] = {"cyclic contacts": sum(1 for c in B.contacts if dims[c] == M), "every ring has one": crit, "full reach": fr}
        info[str(n)]["no cyclic contact"] = info[str(n)]["cyclic contacts"] == 0
        if crit:
            meets.append(n)
        full[n] = fr
    none = [n for n in range(3, 27) if info[str(n)]["no cyclic contact"]]
    ok = (all(full[n] for n in meets) and meets == [3, 5, 7, 9, 11, 13, 18, 19, 21, 23, 25] and none == [4, 8, 14, 16, 20, 24]
          and [n for n in range(3, 27) if not full[n]] == [8, 16])
    rec("1 Proposition 5's criterion at sides 3 to 26: met exactly at 3, 5, 7, 9, 11, 13, 18, 19, 21, 23, 25; no cyclic contact at 4, 8, 14, 16, 20, 24; full reach everywhere but 8 and 16", ok, info)


def check2():
    p = ROOT / "research/REACH-HALVES-20261110-001/census.json"
    if not p.exists():
        rec("2 the census B2 (pending: census.json not written yet)", False)
        return
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    c = json.loads(p.read_text())
    pred = c["failing-set predictions at the powers of two"]
    ok = c["prediction (fails exactly at 8, 16, 32, 64, 128)"] and all(all(v.values()) for v in pred.values())
    ok &= [int(n) for n, r in c["by side"].items() if not r["full_reach"]] == [8, 16, 32, 64, 128]
    ok &= all(c["by side"][str(n)]["full_reach"] and c["by side"][str(n)].get("certified_at_step") for n in range(3, 131)
              if n not in (4, 8, 16, 32, 64, 128))
    # recompute the failing sets from the stored ring lists
    for n in (8, 16, 32, 64, 128):
        N = 2 * n - 2
        rot = lambda p: (p[1], N - p[0])
        base = [(X, X + 1) for X in range(n + 2, 2 * n - 5, 4)]
        orbit = set()
        for q in base:
            for _ in range(4):
                orbit.add(q)
                q = rot(q)
        rows = c["by side"][str(n)]["contacts_missing_rings"]
        got = {(int(a), int(b)) for a, b, k, _ in rows}
        ok &= got == orbit
        corners = [{(0, 0), (0, 1), (1, 0)}, {(n - 1, 0), (n - 2, 0), (n - 1, 1)}, {(0, n - 1), (1, n - 1), (0, n - 2)},
                   {(n - 1, n - 1), (n - 2, n - 1), (n - 1, n - 2)}]
        for a, b, k, ringtext in rows:
            rings = {tuple(map(int, r.strip("()").split(","))) for r in ringtext.split()}
            ok &= int(k) == 3 and rings in corners
    rec("2 the census B2, sides 3 to 130 (census.json bound by hash): full reach fails exactly at 8, 16, 32, 64, 128; there the failing set is the quarter-turn orbit of (X, X + 1), X = n + 2, n + 6, ..., 2n - 6, each contact missing one corner ring and its two neighbours, recomputed from the ring lists", ok,
        {"census.json sha256": digest, "failing sides": c["sides failing full reach"], "predictions": pred, "seconds": c["seconds"]})


def main():
    got = hashlib.sha256((ROOT / DEP).read_bytes()).hexdigest()
    rec("0 the dependency (FULL-REACH-PROOF-20261108-001A's manifest) bound by hash", got == WANT, got)
    check1()
    check2()
    allpass = all(v["pass"] for v in checks.values())
    print("ALL PASS" if allpass else "SOME FAIL")
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact": "REACH-HALVES-20261110-001B-P001", "checks": checks,
                                                     "status": "passed" if allpass else "failed"}, indent=1) + "\n")


if __name__ == "__main__":
    main()
