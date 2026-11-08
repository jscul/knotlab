#!/usr/bin/env python3
"""What the persistent closed loops of LOOP-RINGS-20261108-001A-E001 are (exploratory, post hoc; a few minutes).

    .venv/bin/python3 -B research/LOOP-RINGS-20261108-001/characterise.py   writes characterise.json
- Control (the contract's, run here after the census): every persistent loop at size 4 rechecked on its full state space.
- Laws: which law patterns occur among persistent loops, by size.
- Families: a loop family fixes the laws and, for each ring, whether its second contact sits at cell 2 or cell s - 2; which families
  persist at every size from 4 to 10, and one size past, at 11 to 16.
- Round the loop: in persistent loops, does each contact need the ring it does not touch (three rings: the third one) at some lag of
  its eventual cycle, or at every lag from some lag on?"""
import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops"))
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import run as LR  # noqa: E402
import net_lib as N  # noqa: E402
import numpy as np  # noqa: E402

LOOPS = ROOT / "artifacts/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops/run/loops.json"


def full_persists(args):
    s, ks, laws = args
    net = LR.loop_net(s, ks, [tuple(l) for l in laws])
    nxt, Nn, blocks = N.state_map(*net)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen = set()
    for T in range(1, 4097):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            return True
        seen.add(key)
        for c, (ra, pa, rb, pb, law) in enumerate(net[2]):
            F = ((cur >> c) & 1).astype(np.uint8)
            if F.min() == F.max() or any(N.PL.C.decides_outside(F, *blocks[x], Nn) for x in (ra, rb)):
                return False
    return None


def family_key(s, ks, laws):
    return (tuple(0 if k == 2 else 1 for k in ks), tuple(tuple(l) for l in laws))


def family_sizes(fam):
    v, laws = fam
    out = {}
    for s in range(4, 17):
        ks = tuple(2 if x == 0 else s - 2 for x in v)
        out[s] = LR.verdict(s, ks, laws)[0]
    return out


def round_the_loop(args):
    s, ks, laws = args
    net = LR.loop_net(s, ks, [tuple(l) for l in laws])
    rows, Nn, blocks = N.matrix(*net)
    r = len(ks)
    res = []
    for c in range(r):
        far = [x for x in range(r) if x not in (c, (c + 1) % r)]
        o = N.orbit(rows, 1 << c)
        if o is None:
            return None
        seq, T1, p = o
        cyc = [seq[T1 - 1 + j] for j in range(p)]
        some = all(any(row & N.mask(blocks, x) for row in cyc) for x in far)
        every = all(all(row & N.mask(blocks, x) for row in cyc) for x in far)
        res.append((some, every))
    return res


def main():
    t0 = time.time()
    rows = json.loads(LOOPS.read_text())["rows"]
    pers = [r for r in rows if r[3] == "persistent"]
    small = [(r[0], tuple(r[1]), r[2]) for r in pers if r[0] == 4]
    with Pool(16) as pool:
        fullv = pool.map(full_persists, small, chunksize=4)
        fams = sorted({family_key(r[0], r[1], r[2]) for r in pers if all(k in (2, r[0] - 2) for k in r[1])})
        profiles = pool.map(family_sizes, fams, chunksize=4)
        rl = pool.map(round_the_loop, [(r[0], tuple(r[1]), r[2]) for r in pers], chunksize=8)
    every_size = [(f, p) for f, p in zip(fams, profiles) if all(p[s] == "persistent" for s in range(4, 11))]
    past = [(f, p) for f, p in every_size if all(p[s] == "persistent" for s in range(11, 17))]
    laws_by_size = defaultdict(Counter)
    for r in pers:
        laws_by_size[r[0]][json.dumps([l for l in r[2]])] += 1
    rl_counts = Counter()
    for x in rl:
        if x is None:
            rl_counts["undecided"] += 1
        else:
            rl_counts[("every contact needs the far rings at some lag of its cycle", all(a for a, b in x))] += 1
            rl_counts[("every contact needs the far rings at every lag of its cycle", all(b for a, b in x))] += 1
    out = {"persistent loops": len(pers), "by rings": dict(Counter(len(r[1]) for r in pers)), "by size": dict(Counter(r[0] for r in pers)),
           "control: persistent loops at size 4 on their full state spaces (agree, of)": [sum(1 for v in fullv if v is True), len(fullv)],
           "laws among persistent loops (top 12)": Counter(json.dumps(r[2]) for r in pers).most_common(12),
           "loop families with contacts two apart": len(fams),
           "families persistent at every size 4 to 10": len(every_size),
           "of those, persistent at every size 11 to 16 too": len(past),
           "examples (positions as 0 = cell 2, 1 = cell s - 2; laws)": [[list(f[0]), [list(l) for l in f[1]]] for f, p in past[:12]],
           "round the loop": {str(k): v for k, v in rl_counts.items()},
           "seconds": round(time.time() - t0, 1)}
    (HERE / "characterise.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1)[:5000])


if __name__ == "__main__":
    main()
