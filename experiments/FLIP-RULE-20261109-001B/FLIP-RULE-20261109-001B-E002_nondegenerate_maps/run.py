"""FLIP-RULE-20261109-001B-E002: persistence without a flip on non-degenerate maps (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/FLIP-RULE-20261109-001B/FLIP-RULE-20261109-001B-E002_nondegenerate_maps/run/result.json

E001's readings (maps, persistence, flips) on random maps of E = 6 to 9 contacts, conditioned by rejection on being connected, with no
contact joining a ring to itself, every ring of at least 3 contacts and every face of at least 3 (non-degenerate). Every contact is read;
a persistent contact without a flip is listed, with whether it sends (some walk from it has an odd count) and hears (some walk into it
has an odd count)."""
import collections
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/FLIP-RULE-20261109-001B/FLIP-RULE-20261109-001B-E001_small_maps"))
import run as R1  # noqa: E402

OUT = ROOT / "artifacts" / "FLIP-RULE-20261109-001B" / "FLIP-RULE-20261109-001B-E002_nondegenerate_maps" / "run"
DRAWS = {6: 4000000, 7: 4000000, 8: 4000000, 9: 4000000}
SEED = 20261110


def cycles(perm):
    n, seen, out = len(perm), set(), []
    for s in range(n):
        if s in seen:
            continue
        k, x = 0, s
        while x not in seen:
            seen.add(x)
            k += 1
            x = perm[x]
        out.append(k)
    return out


def nondegenerate(sig):
    if min(cycles(sig)) < 3:
        return False
    face = [sig[d ^ 1] for d in range(len(sig))]
    return min(cycles(face)) >= 3


def sends_hears(sig, c):
    n = len(sig)
    E = n // 2
    rows = [0] * E
    for d in range(n):
        rows[d >> 1] ^= 1 << (sig[d] >> 1)
    cols = [0] * E
    for e in range(E):
        x = rows[e]
        while x:
            low = x & -x
            cols[low.bit_length() - 1] ^= 1 << e
            x ^= low

    def nonzero(mat):
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
    return nonzero(rows), nonzero(cols)


def chunk(args):
    E, count, seed = args
    rng = random.Random(seed)
    n = 2 * E
    acc, exc = collections.Counter(), {}
    for _ in range(count):
        p = list(range(n))
        rng.shuffle(p)
        sig = tuple(p)
        if not nondegenerate(sig) or not R1.valid(sig):
            continue
        acc["maps"] += 1
        pers = R1.persistent(sig)
        for c, ok in enumerate(pers):
            flip, refl = R1.symmetries(sig, c)
            acc["contacts"] += 1
            acc["persistent"] += ok
            acc["with a flip"] += flip
            if flip and not ok:
                acc["flip but not persistent"] += 1
            if ok and not flip:
                s, h = sends_hears(sig, c)
                acc["persistent without a flip"] += 1
                acc["of those, sending and hearing"] += s and h
                acc["of those, with a reflection"] += refl
                exc.setdefault(R1.canonical(sig), [list(sig), c, s, h, refl])
    return E, acc, exc


def main():
    t0 = time.time()
    jobs = [(E, cnt // 16, SEED * 100 + E * 16 + i) for E, cnt in DRAWS.items() for i in range(16)]
    with Pool(16) as pool:
        res = pool.map(chunk, jobs, chunksize=1)
    by, exc = collections.defaultdict(collections.Counter), collections.defaultdict(dict)
    for E, acc, ex in res:
        by[E].update(acc)
        exc[E].update(ex)
    readings = {"E = %d" % E: {**dict(by[E]), "distinct maps with a persistent contact without a flip": len(exc[E]),
                               "examples": list(exc[E].values())[:20]} for E in sorted(by)}
    result = {"experiment": "FLIP-RULE-20261109-001B-E002", "readings": readings,
              "H1' every persistent contact of a non-degenerate map has a flip": all(v.get("persistent without a flip", 0) == 0 for v in readings.values()),
              "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "examples"} for k, v in readings.items()}, indent=1))
    print("H1':", result["H1' every persistent contact of a non-degenerate map has a flip"], result["seconds"], "s")


if __name__ == "__main__":
    main()
