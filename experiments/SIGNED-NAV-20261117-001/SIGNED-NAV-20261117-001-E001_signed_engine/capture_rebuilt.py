"""Capture signed patterns that the slow loop rebuilds, for gate (b) of SIGNED-NAV-20261117-001.

Imports the slow loop of SPEC-MERGE-20261117-001A read-only (its slow_loop.py and engine are not changed): wraps its
reduce_pattern to record each rebuilt pattern (tie-class roots renumbered 0..n-1, signed knots), runs its eager policy "GO"
with Novelty+ as the fast loop on a few local (window 10) and block patterns of 800 distinctions, and saves the last
rebuilt pattern of each run.

  capture_rebuilt.py OUT_DIR [--sequences]    (--sequences also saves every rebuild with its tie map)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SM = ROOT / "experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"
sys.path.insert(0, str(SM))
os.environ.setdefault("SLOW_LOOP_BUILD", str(Path.home() / ".cache" / "signed_nav_slow_build"))
import slow_loop as S  # noqa: E402

out = Path(sys.argv[1])
SEQ = len(sys.argv) > 2 and sys.argv[2] == "--sequences"
out.mkdir(parents=True, exist_ok=True)
POL = json.loads((ROOT / "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop/policies.json").read_text())["GO"]
NOV = (0.7, 0.01)
captured = []
orig_reduce = S.reduce_pattern


def recording_reduce(knots0, shadows, ties, new_ties):
    roots, kv, ks, w = orig_reduce(knots0, shadows, ties, new_ties)
    idx = np.full(ties.n, -1, dtype=np.int64)
    idx[roots] = np.arange(len(roots))
    captured.append((len(roots), idx[kv].astype(np.int32), ks.astype(np.uint8), len(shadows), roots.copy(),
                     ties.root.copy(), ties.rpar.copy()))
    return roots, kv, ks, w


S.reduce_pattern = recording_reduce
rows = []
for fam, alpha, w, count in (("local", 4.0, 10, 6), ("block", 2.5, 20, 4)):
    for i in range(count):
        seed = 5_500_000 + i
        inst = S.planted(fam, 800, alpha, seed, w=w)
        captured.clear()
        res = S.run_slow(inst, "novelty_plus", NOV, S.run_seed("signed-nav-capture", fam, seed), 10**7, POL)
        if not captured:
            rows.append({"family": fam, "seed": seed, "rebuilds": 0})
            continue
        n, kv, ks, nsh = captured[-1][:4]
        name = f"{fam}_w{w}_{seed}.npz"
        np.savez_compressed(out / name, n=n, kv=kv, ks=ks, n0=inst.n, m0=inst.m)
        if SEQ:  # every rebuild in order, with the tie map (for the handle's merge gate)
            seq = {"knots0": inst.knots}
            for j, (nj, kvj, ksj, _, rootsj, rootj, rparj) in enumerate(captured):
                seq.update({f"kv{j}": kvj, f"ks{j}": ksj, f"roots{j}": rootsj, f"root{j}": rootj, f"rpar{j}": rparj})
            np.savez_compressed(out / ("seq_" + name), count=len(captured), **seq)
        rows.append({"family": fam, "seed": seed, "file": name, "rebuilds": len(captured), "n": int(n), "m": int(len(kv)),
                     "n0": inst.n, "m0": inst.m, "signed_knots": int((ks.sum(axis=1) > 0).sum()), "shadows": int(nsh),
                     "slow_loop_solved": bool(res.get("solved"))})
        print(rows[-1], flush=True)
(out / "captured.json").write_text(json.dumps(rows, indent=1))
