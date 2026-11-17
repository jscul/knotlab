"""Referee R1 for SPEC-MERGE-20261117-001: gate D replicated in an independent engine (referee_gate.c), with more controls.

  .venv/bin/python -B referee_gate.py > referee_gate.json

The instances are the study's gate instances (seeds 8,700,000 + i, its generator, which is MEET-TRANSFER's; the planted state
is checked to satisfy every knot here). The search is the referee's own Novelty+ (0.7, 0.01) in epochs of n flips, from its own
initial states. The stability count is the referee's own: per co-knotted pair slot (three per knot), +1 when both members
flipped in the epoch and their relative value is what it was at the last epoch's end, 0 when it changed.

At epochs 4, 8 and 16, k = 1% of n pair slots are drawn five ways and read by agreement of the current relative value with the
planted one, and (on local) by the share an independent pair probe ties:
  top       the k most stable slots (stability >= 1; ties to the lower slot index), as the study's gate
  uniform   k slots uniformly among all slots, as the study's gate control
  active    k slots uniformly among slots whose two members both flipped in the last epoch (the test arms' control)
  stab1     k slots uniformly among slots with stability >= 1 (moved together at least once, relative value unchanged since)
  shuffled  the top slots' members re-paired at random (keeps how well each member agrees with the planted state, breaks the
            pairing): if top's agreement is no higher than this, the signal is about single distinctions, not pairs
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"))
from slow_loop import planted  # noqa: E402  (the study's generator only)

SO = Path(os.environ.get("TMPDIR", "/tmp")) / "referee_gate_spec.so"
subprocess.run(["cc", "-O2", "-shared", "-fPIC", "-o", str(SO), str(HERE / "referee_gate.c")], check=True)
L = ctypes.CDLL(str(SO))
L.g_new.restype = ctypes.c_void_p
L.g_new.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64]
L.g_run.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_int64, ctypes.c_void_p]
L.g_state.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
L.g_pair_probe.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
L.g_pair_probe.restype = ctypes.c_int
L.g_free.argtypes = [ctypes.c_void_p]

CELLS = {"rand-3200": ("rand", 2.1), "local-w10-3200": ("local", 4.0)}
N, SEED0, NI, CPS, BUDGET = 3200, 8_700_000, 30, (4, 8, 16), 4000
B = 10_000


def nae_ok(knots, x):
    s = x[knots].astype(np.int64).sum(axis=1)
    return bool(np.all((s == 1) | (s == 2)))


def one(cell, i):
    fam, a = CELLS[cell]
    inst = planted(fam, N, a, SEED0 + i, w=10)
    kv = np.ascontiguousarray(inst.knots, dtype=np.int32)
    hid = inst.hidden.astype(np.int64)
    assert nae_ok(kv, hid), "planted state must satisfy every knot"
    pa = kv[:, [0, 0, 1]].reshape(-1).astype(np.int64)
    pb = kv[:, [1, 2, 2]].reshape(-1).astype(np.int64)
    hrel = hid[pa] ^ hid[pb]
    rng = np.random.default_rng(1_000_003 * (i + 1) + (0 if fam == "rand" else 7))
    h = L.g_new(N, len(kv), kv.ctypes.data, ctypes.c_uint64(0xC0FFEE + 1000 * i + (0 if fam == "rand" else 1)))
    x = np.zeros(N, np.uint8)
    nf = np.zeros(N, np.int32)
    L.g_state(h, x.ctypes.data, nf.ctypes.data)
    rel = (x[pa] ^ x[pb]).astype(np.uint8)
    snap = nf.copy()
    stab = np.zeros(len(pa), np.int32)
    out = {"checkpoints": {}}
    o = np.zeros(3)
    for ep in range(1, max(CPS) + 1):
        L.g_run(h, 0.7, 0.01, N, o.ctypes.data)
        L.g_state(h, x.ctypes.data, nf.ctypes.data)
        sm = x[kv].astype(np.int64).sum(axis=1)
        assert int(np.sum((sm == 0) | (sm == 3))) == int(o[2]), "engine's violated count must match a recount"
        if o[1]:
            assert nae_ok(kv, x)
            out["solved_at_epoch"] = ep
            break
        r2 = (x[pa] ^ x[pb]).astype(np.uint8)
        both = (nf[pa] > snap[pa]) & (nf[pb] > snap[pb])
        stab = np.where(r2 != rel, 0, np.where(both, stab + 1, stab)).astype(np.int32)
        rel, snap = r2, nf.copy()
        if ep not in CPS:
            continue
        k = N // 100
        cand = np.nonzero(stab >= 1)[0]
        top = cand[np.lexsort((cand, -stab[cand]))][:k]
        act = np.nonzero(both)[0]
        sets = {"top": top, "uniform": rng.choice(len(pa), k, replace=False),
                "active": rng.choice(act, min(k, len(act)), replace=False),
                "stab1": rng.choice(cand, min(k, len(cand)), replace=False)}
        row = {"active_slots": int(len(act)), "stab1_slots": int(len(cand)), "top_median_stab": float(np.median(stab[top]))}
        for name, sel in sets.items():
            cur = rel[sel]
            d = {"agree": float(np.mean(cur == hrel[sel]))}
            if fam == "local":
                tied = 0
                for s_ in sel:
                    aa, bb = int(pa[s_]), int(pb[s_])
                    tied += bool(L.g_pair_probe(h, aa, bb, 0, BUDGET) or L.g_pair_probe(h, aa, bb, 1, BUDGET))
                d["tied"] = tied / len(sel)
            row[name] = d
        # shuffled: the top slots' members re-paired at random (members kept, pairing broken)
        a_, b_ = pa[top], rng.permutation(pb[top])
        ok = a_ != b_
        row["shuffled"] = {"agree": float(np.mean(((x[a_] ^ x[b_]) == (hid[a_] ^ hid[b_]))[ok]))}
        al = float(np.mean(x == hid))
        row["state_agree"] = max(al, 1 - al)
        out["checkpoints"][ep] = row
    L.g_free(h)
    return out


def summarize(res):
    rng = np.random.default_rng(99)
    s = {}
    for cell, rows in res.items():
        cs = {"instances": len(rows), "solved_before_16": sum("solved_at_epoch" in r for r in rows)}
        for cp in CPS:
            pts = [r["checkpoints"][cp] for r in rows if cp in r["checkpoints"]]
            row = {"n": len(pts)}
            for name in ("top", "uniform", "active", "stab1", "shuffled"):
                row[name] = round(float(np.mean([p[name]["agree"] for p in pts])), 4)
            for ctl in ("uniform", "active", "stab1", "shuffled"):
                d = np.array([p["top"]["agree"] - p[ctl]["agree"] for p in pts])
                m = d[rng.integers(0, len(d), (B, len(d)))].mean(axis=1)
                row[f"top-{ctl}"] = [round(float(d.mean()), 4)] + [round(float(q), 4) for q in np.quantile(m, [0.005, 0.995])]
            if "tied" in pts[0]["top"]:
                for name in ("top", "uniform", "active", "stab1"):
                    row[f"tied_{name}"] = round(float(np.mean([p[name]["tied"] for p in pts])), 4)
                for ctl in ("uniform", "active", "stab1"):
                    d = np.array([p["top"]["tied"] - p[ctl]["tied"] for p in pts])
                    m = d[rng.integers(0, len(d), (B, len(d)))].mean(axis=1)
                    row[f"tied top-{ctl}"] = [round(float(d.mean()), 4)] + [round(float(q), 4)
                                                                           for q in np.quantile(m, [0.005, 0.995])]
            row["state_agree"] = round(float(np.mean([p["state_agree"] for p in pts])), 4)
            row["active_slots_median"] = float(np.median([p["active_slots"] for p in pts]))
            cs[str(cp)] = row
        s[cell] = cs
    return s


if __name__ == "__main__":
    res = {cell: [one(cell, i) for i in range(NI)] for cell in CELLS}
    print(json.dumps({"summary": summarize(res), "per_instance": res}, indent=1, default=str))
