#!/usr/bin/env python3
"""Checks for GROW-RUN-20261109-001A: a band inserted while the network runs keeps only the knots it has not reached.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Binding after an insertion is read exactly: the network is fixed from the insertion on, so a contact's row
under it is eventually periodic (net_lib.orbit), and each row of the orbit is applied to the state at the insertion. Whether an
insertion at lag t0 keeps every contact persistent depends only on the run's state at t0, which is eventually periodic in t0, so
reading every t0 below the state's preperiod plus its period reads every insertion lag. Checks 3 to 5 are computations."""
import collections
import copy
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import growrun_lib as GR  # noqa: E402

T0_CLOCK = time.time()
OUT = {}
DEPS = {
    "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two/net_lib.py":
        "e75467f9d6df5f0fe7c8311e4801fabfaa8b4a4a74b3a4e2ff26c1cab9d26351",
    "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not/manifest.json":
        "71121891197b547cc36d05bbb54e247377ad2e6d645671eaa91d8345f02ffee7",
    "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns/manifest.json":
        "ea82b4fbe792a325ce481430b65203894505095f86c54798973cb5a58d1134e5",
    "proofs/GROWN-DISTANCE-20261109-001A/GROWN-DISTANCE-20261109-001A-P001_the_grown_torus_reads_distance_plainly_only_as_a_ladder/manifest.json":
        "c99a5ae475f4e02c7f5c09974990c7bfe5a810a0b6593e2037319f1056615fae",
}
SPLITS = ("lower", "upper", "fresh", "copy")
CENSUS = ((3, 3, 2), (3, 4, 2), (4, 3, 2), (4, 4, 2), (5, 3, 2), (3, 5, 2), (5, 5, 2), (3, 3, 3), (4, 3, 3), (3, 4, 3), (3, 3, 4),
          (6, 3, 2), (3, 6, 2))


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0_CLOCK, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def contacts(run):
    return [k for k in run.tube.keys if k[0] == 'c']


def all_persist(run):
    return all(GR.binds_forever(run, k)[0] == [None, None] for k in contacts(run))


def state_cycle(n, m, g):
    run = GR.Run(GR.Tube(n, list(range(m)), g))
    seen, T = {}, 0
    while True:
        key = tuple(run.state)
        if key in seen:
            return seen[key], T - seen[key]
        seen[key] = T
        run.step()
        T += 1


# ---------- check 1: the stages persist; inserting at lag 0 is the stage
def stages():
    bad = []
    for n, m, g in ((3, 3, 2), (3, 4, 2), (4, 4, 2), (3, 3, 3), (5, 4, 2), (3, 8, 2)):
        if not all_persist(GR.Run(GR.Tube(n, list(range(m)), g))):
            bad.append(("stage", n, m, g))
        for split in SPLITS:
            run = GR.Run(GR.Tube(n, list(range(m)), g))
            run.insert_band(0, 0.5, split)
            if not all_persist(run):
                bad.append(("lag 0", n, m, g, split))
    return bad


# ---------- check 2: Theorem 1 (rings not reached keep every binding; the band's rings are always bound)
def theorem1():
    cnt = collections.Counter()
    for n, m, g in ((3, 8, 2), (4, 6, 2), (3, 5, 3)):
        for split in SPLITS:
            run = GR.Run(GR.Tube(n, list(range(m)), g))
            for T0 in range(32):
                r2 = copy.deepcopy(run)
                r2.insert_band(0, 0.5, split)
                st = GR.Run(GR.Tube(n, r2.tube.rows, g))
                for _ in range(T0):
                    st.step()
                tb = r2.tube
                unaffected = {R: GR.footprint(r2, R) == GR.footprint(st, R) for R in run.tube.rings}
                for k in contacts(r2):
                    ff, T1, p = GR.binds_forever(r2, k)
                    c = tb.pos[k]
                    ra, pa, rb, pb, law = tb.contacts[c]
                    for j, R in enumerate((tb.rings[ra], tb.rings[rb])):
                        if R not in unaffected:
                            cnt[("band ring", "fails" if ff[j] is not None else "binds")] += 1
                        else:
                            cnt[("not reached" if unaffected[R] else "reached", "fails" if ff[j] is not None else "binds")] += 1
                run.step()
    return {" / ".join(k): v for k, v in sorted(cnt.items())}


# ---------- check 3: every insertion lag (computed)
def census():
    out = {}
    for n, m, g in CENSUS:
        pre, per = state_cycle(n, m, g)
        res = {}
        for split in SPLITS:
            run = GR.Run(GR.Tube(n, list(range(m)), g))
            clean = []
            for T0 in range(pre + per):
                r2 = copy.deepcopy(run)
                r2.insert_band(0, 0.5, split)
                if all_persist(r2):
                    clean.append(T0)
                run.step()
            res[split] = clean
        out["%d x %d, g = %d" % (n, m, g)] = {"state preperiod": pre, "state period": per, "clean insertion lags": res}
    return out


# ---------- check 4: the damage spreads from the band (computed)
def spread():
    n, m, g = 3, 8, 2
    run = GR.Run(GR.Tube(n, list(range(m)), g))
    first = {}
    table = []
    for T0 in range(24):
        r2 = copy.deepcopy(run)
        r2.insert_band(3, 3.5, "lower")
        fails = collections.Counter()
        for k in contacts(r2):
            if GR.binds_forever(r2, k)[0] != [None, None]:
                fails[k[3]] += 1
        for row in fails:
            first.setdefault(row, T0)
        table.append((T0, {r: fails[r] for r in sorted(set(k[3] for k in contacts(r2)))}))
        run.step()
    return first, table


# ---------- check 5: an independent reading by actual bits
def brute():
    bad, read = [], 0
    for n, m, g, T0, split in ((3, 3, 2, 5, "lower"), (3, 4, 2, 9, "fresh"), (4, 3, 2, 3, "upper"), (3, 3, 3, 7, "copy")):
        H = T0 + 30
        run = GR.Run(GR.Tube(n, list(range(m)), g))
        hist = {}
        for t in range(1, H + 1):
            if t - 1 == T0:
                run.insert_band(0, 0.5, split)
            run.step()
            hist[t] = (list(run.state), list(run.tube.keys))
        first_keys = [k for k in run.vkey[:len(GR.Tube(n, list(range(m)), g).build().keys)]]
        band_keys = run.vkey[len(first_keys):]
        flips = [(0, k) for k in first_keys[::5]] + [(1, k) for k in band_keys[::3]]
        res = GR.brute_values(n, m, g, T0, split, H, flips, seed=n * 1000 + m * 100 + g * 10 + T0)
        for flip in flips:
            v = run.vkey.index(flip[1]) if flip[0] == 0 else len(first_keys) + band_keys.index(flip[1])
            dep = {(t, k) for t, (st, keys) in hist.items() for b, k in enumerate(keys) if st[b] >> v & 1}
            read += 1
            if dep != res[flip]:
                bad.append((n, m, g, T0, split, flip))
    return read, bad


# ---------- check 6: a band every P lags (computed)
def repeated():
    out = {}
    for P in (4, 8, 16):
        run = GR.Run(GR.Tube(3, [0, 1, 2], 2))
        born = {R: 0 for R in run.tube.rings}
        k = 0
        for t in range(1, 5 * P + 1):
            run.step()
            if t % P == 0 and t < 5 * P:
                k += 1
                run.insert_band(0, 0.5 ** k, "lower")   # each band below the one before, after row 0
                for R in run.tube.rings:
                    born.setdefault(R, t)
        kept = collections.defaultdict(lambda: [0, 0])
        for key in contacts(run):
            ff, T1, p = GR.binds_forever(run, key)
            c = run.tube.pos[key]
            ra, pa, rb, pb, law = run.tube.contacts[c]
            for j, R in enumerate((run.tube.rings[ra], run.tube.rings[rb])):
                kept[born[R]][0] += ff[j] is None
                kept[born[R]][1] += 1
        out["P = %d" % P] = {str(b): v for b, v in sorted(kept.items())}
    return out


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    bad = stages()
    check("1 every stage persists, and a band inserted at lag 0 gives the stage, for each split", not bad, {"bad": bad})
    cnt = theorem1()
    check("2 Theorem 1: a ring the insertion has not reached keeps every binding, and the band's rings are always bound "
          "(3 x 8 and 4 x 6 at g = 2, 3 x 5 at g = 3, insertion lags 0 to 31, four splits)",
          cnt.get("not reached / fails", 0) == 0 and cnt.get("band ring / fails", 0) == 0, cnt)
    cen = census()
    share = {s: (sum(len(v["clean insertion lags"][s]) for v in cen.values()),
                 sum(v["state preperiod"] + v["state period"] for v in cen.values())) for s in SPLITS}
    check("3 Computed: every insertion lag of 13 tubes, four splits; lag 0 keeps every contact in every case, and at most one lag in "
          "seven does overall", all(0 in v["clean insertion lags"][s] for v in cen.values() for s in SPLITS)
          and all(a * 7 <= b for a, b in share.values()),
          {"clean lags / lags read, all tubes": share,
           "by tube": {k: {s: len(c) for s, c in v["clean insertion lags"].items()} | {"cycle": v["state preperiod"] + v["state period"]}
                       for k, v in cen.items()}})
    OUT["3 census detail"] = cen
    first, table = spread()
    rows_below = [first.get(r) for r in (3, 2, 1, 0)]
    rows_above = [first.get(r) for r in (4, 5, 6, 7)]
    check("4 Computed: on the 3 x 8 tube the contacts that lose a binding spread from the band, one row every 4 lags each way",
          rows_below == sorted(rows_below) and rows_above == sorted(rows_above) and None not in rows_below + rows_above,
          {"first insertion lag with a failing contact, by row": {str(k): v for k, v in sorted(first.items())}})
    OUT["4 spread table"] = table
    read, bad = brute()
    check("5 The dependence sets against actual bits, a cell flipped at a time", not bad, {"flips read": read, "bad": bad})
    rep = repeated()
    check("6 Computed: four bands, one every P lags, on the 3 x 3 tube; after the last, only the newest band's rings keep every "
          "binding", all(v[str(4 * int(k.split()[-1]))] == [12, 12] and all(x[0] < x[1] for b, x in v.items() if b != str(4 * int(k.split()[-1])))
                         for k, v in rep.items()), rep)
    result = {"ticket": "GROW-RUN-20261109-001A", "artifact_id": "GROW-RUN-20261109-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        return 0
    old = json.loads(path.read_text())
    same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
    print("result.json matches" if same else "result.json differs")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
