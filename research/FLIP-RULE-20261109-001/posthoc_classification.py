"""Post-hoc classification of FLIP-RULE-20261109-001B-E001's exceptions (not part of its contract): for every persistent contact without a flip on
maps of 3 to 5 contacts, whether it sends and hears, and the smallest ring and face of its map. Run from the workspace root."""
import sys, collections, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "experiments/FLIP-RULE-20261109-001B/FLIP-RULE-20261109-001B-E001_small_maps"))
import run as R
from multiprocessing import Pool

def faces(sig):
    n = len(sig); seen = set(); sizes = []
    for d in range(n):
        if d in seen: continue
        k, x = 0, d
        while x not in seen:
            seen.add(x); k += 1; x = sig[x ^ 1]
        sizes.append(k)
    return sizes

def degrees(sig):
    n = len(sig); seen = set(); ds = []
    for s in range(n):
        if s in seen: continue
        k, x = 0, s
        while x not in seen:
            seen.add(x); k += 1; x = sig[x]
        ds.append(k)
    return ds

def classify(sig, c):
    n = len(sig); E = n // 2
    rows = [0] * E
    for d in range(n):
        rows[d >> 1] ^= 1 << (sig[d] >> 1)
    # does c ever influence anything? (its forward rows vanish)
    v = 1 << c; silent = True
    for k in range(E + 1):
        w, x = 0, v
        while x:
            low = x & -x; w ^= rows[low.bit_length() - 1]; x ^= low
        v = w
        if v: silent = False; break
    # does anything influence c? (backward)
    cols = [0] * E
    for e in range(E):
        x = rows[e]
        while x:
            low = x & -x; cols[low.bit_length() - 1] ^= 1 << e; x ^= low
    v = 1 << c; deaf = True
    for k in range(E + 1):
        w, x = 0, v
        while x:
            low = x & -x; w ^= cols[low.bit_length() - 1]; x ^= low
        v = w
        if v: deaf = False; break
    fs, ds = faces(sig), degrees(sig)
    return silent, deaf, min(fs), min(ds)

def chunk(args):
    E, first = args
    n = 2 * E
    cnt = collections.Counter(); ex = {}
    for tail in itertools.permutations([d for d in range(n) if d != first]):
        sig = (first,) + tail
        if not R.valid(sig): continue
        pers = R.persistent(sig)
        for c, p in enumerate(pers):
            if not p: continue
            flip, refl = R.symmetries(sig, c)
            if flip: continue
            silent, deaf, fmin, dmin = classify(sig, c)
            key = ("silent" if silent else "sends", "deaf" if deaf else "hears", "face>=3" if fmin >= 3 else "face<=2", "deg>=3" if dmin >= 3 else "deg<=2", "refl" if refl else "-")
            cnt[key] += 1
            if not silent and not deaf and fmin >= 3 and dmin >= 3:
                ex.setdefault(R.canonical(sig), (sig, c))
    return E, cnt, ex

if __name__ == "__main__":
    jobs = [(E, f) for E in range(3, 6) for f in range(2 * E)]
    with Pool(16) as pool:
        res = pool.map(chunk, jobs)
    tot = collections.defaultdict(collections.Counter); exs = collections.defaultdict(dict)
    for E, cnt, ex in res:
        tot[E].update(cnt); exs[E].update(ex)
    for E in sorted(tot):
        print("E", E)
        for k, v in sorted(tot[E].items()): print("   ", k, v)
        print("   non-degenerate distinct maps:", len(exs[E]))
        for code, (sig, c) in list(exs[E].items())[:5]:
            print("     sig", sig, "contact", c, "faces", sorted(faces(sig)), "degrees", sorted(degrees(sig)))
