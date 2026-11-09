#!/usr/bin/env python3
"""Run BIRTH-RULE-20261109-001A-E001 (frozen contract beside this file): birth rules for the doubling law, a frozen test of A44.

    .venv/bin/python3 -B run.py
On GROW-CHOOSE-20261109-001A-E001's choose_lib (every born cell a variable; persistence through a full cycle of the state, Brent's
method). A doubling puts a band at every cut both ways (choose_lib's insert with the fresh split), then sets every cell it bears (every
contact, and every cell of a new ring) by the birth rule: "open" keeps the new distinction choose_lib gave it (A44); "copy" gives it the
value, before the doubling, of the cell it splits from (the same cell of the ring at the lower column and row label, or the cut contact
itself); "zero" gives it 0; "open plus copy" adds the two. 8 worker processes, one per (rule, P). Writes
artifacts/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run/result.json."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth"))
import choose_lib as C  # noqa: E402

RULES = ("open", "copy", "zero", "open plus copy")
PS = (1, 2, 3, 4)
MAX_RINGS = 600
CAP = 300000
OUT = ROOT / "artifacts/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run/result.json"


def parent_label(label, old_labels):
    return label if label in old_labels else max(a for a in old_labels if a < label) if any(a < label for a in old_labels) else max(old_labels)


def double(run, t, rule):
    old_cols, old_rows = list(run.tube.cols), list(run.tube.rows)
    old_val = {k: run.state[b] for b, k in enumerate(run.tube.keys)}
    old_rings = set(run.tube.rings)
    cuts = [('row', x) for x in old_rows] + [('col', x) for x in old_cols]
    for k, (kind, x) in enumerate(cuts):
        run.insert(kind, x, (t, k), 'fresh')
    # labels: integers before the first doubling, tuples (lag, k) after; order the new labels by position, as choose_lib does
    order_c = {lab: j for j, lab in enumerate(run.tube.cols)}
    order_r = {lab: j for j, lab in enumerate(run.tube.rows)}

    def parent(lab, old, order):
        if lab in old:
            return lab
        j = order[lab]
        seq = run.tube.cols if order is order_c else run.tube.rows
        while seq[j] not in old:
            j -= 1
        return seq[j]
    for b, key in enumerate(run.tube.keys):
        if key[0] == 'o':
            R = key[1]
            if R in old_rings:
                continue
            pkey = ('o', (parent(R[0], old_cols, order_c), parent(R[1], old_rows, order_r)), key[2])
        else:
            pkey = ('c', key[1], parent(key[2], old_cols, order_c), parent(key[3], old_rows, order_r))
        if rule == "open":
            continue
        inherited = old_val.get(pkey, 0)
        if rule == "copy":
            run.state[b] = inherited
        elif rule == "zero":
            run.state[b] = 0
        else:
            run.state[b] ^= inherited
    return old_rings


def readings(run, old_rings):
    tb = run.tube
    masks, pairs_all, pairs_old = {}, [], []
    for c, (ra, pa, rb, pb, law) in enumerate(tb.contacts):
        for R in (tb.rings[ra], tb.rings[rb]):
            if R not in masks:
                masks[R] = run.ringmask(R)
        pairs_all.append((c, masks[tb.rings[ra]], masks[tb.rings[rb]]))
        for R in (tb.rings[ra], tb.rings[rb]):
            if R in old_rings:
                pairs_old.append((c, masks[R]))
    s = list(run.state)
    saved, power, lam = list(s), 1, 0
    all_ok, old_ok, done = True, True, None
    for _ in range(CAP):
        new = []
        for row in tb.M:
            v, x = 0, row
            while x:
                low = x & -x
                v ^= s[low.bit_length() - 1]
                x ^= low
            new.append(v)
        s = new
        if all_ok and any(not (s[c] & ma) or not (s[c] & mb) for c, ma, mb in pairs_all):
            all_ok = False
        if old_ok and any(not (s[c] & m) for c, m in pairs_old):
            old_ok = False
        if not all_ok and not old_ok:
            done = True
            break
        if s == saved:
            done = True
            break
        lam += 1
        if lam == power:
            saved, power, lam = list(s), power * 2, 0
    if not done:
        return None, None
    return all_ok, old_ok


def hearing(run):
    owner = {}
    for v, k in enumerate(run.vkey):
        if k[0] == 'o':
            owner[v] = k[1]
    bad = 0
    for b, k in enumerate(run.tube.keys):
        if k[0] != 'o':
            continue
        s = run.state[b]
        while s:
            low = s & -s
            v = low.bit_length() - 1
            if v in owner and owner[v] != k[1]:
                bad += 1
                break
            s ^= low
    return bad


def one(job):
    rule, P = job
    t0 = time.time()
    run = C.Run2(C.Tube2([0, 1, 2], [0, 1, 2], 2))
    t, rows = 0, []
    while len(run.tube.rings) * 4 <= MAX_RINGS or t % P:
        if t % P == 0:
            old = double(run, t, rule)
            bal, old_bound = readings(run, old)
            rows.append({"lag": t, "side": len(run.tube.cols), "every stage balanced": bal, "old rings bound": old_bound,
                         "own cells hearing another ring": hearing(run)})
        run.step()
        t += 1
    return {"rule": rule, "P": P, "doublings": rows, "seconds": round(time.time() - t0, 1)}


def main():
    jobs = [(r, P) for r in RULES for P in PS]
    with Pool(8) as pool:
        res = pool.map(one, jobs, chunksize=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"experiment_id": "BIRTH-RULE-20261109-001A-E001", "runs": res}, indent=1) + "\n")
    for r in res:
        print(r["rule"], "P =", r["P"], [(d["lag"], d["side"], d["every stage balanced"], d["old rings bound"], d["own cells hearing another ring"])
                                         for d in r["doublings"]], r["seconds"], "s")


if __name__ == "__main__":
    main()
