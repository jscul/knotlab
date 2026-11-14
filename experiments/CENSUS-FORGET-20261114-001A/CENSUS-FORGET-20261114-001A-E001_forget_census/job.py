"""CENSUS-FORGET-20261114-001, the thread's shared-runner job: FREE-TARGET's exact forgetting test and independent audit (Codex's
code, imported unchanged) on every census family whose first-ray bond provably grows. One case per family."""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
FT = ROOT / "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex"
sys.path.insert(0, str(FT))
import inputs  # noqa: E402  (FREE-TARGET's)
import relations  # noqa: E402
import independent  # noqa: E402
from limits import LimitReached  # noqa: E402

CENSUS = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
_keys, _paths = None, None


def setup(params):
    global _keys, _paths
    _paths = inputs.load_paths()
    keys = []
    with gzip.open(CENSUS, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["class"] == "grows":
                keys.append(row["key"])
    _keys = sorted(keys)


def cases():
    for key in _keys:
        yield key, {}


def run(case_id, payload):
    t0 = time.monotonic()
    prep = _paths.Preparation(json.loads(case_id))
    S = prep.flat(prep.S)
    main = prep.flat(prep.main)
    c = sum(1 for callee, _ in S["calls"] if callee == prep.S)
    other = any(callee not in ("K", prep.S) for callee, _ in S["calls"]) or \
        any(callee not in ("K", prep.S) for callee, _ in main["calls"])
    entries = sum(1 for callee, _ in main["calls"] if callee == prep.S)
    chain = c == 1 and not other and (prep.main == prep.S or entries == 1)
    out = dict(c=c, chain=chain, n_defs=len(prep.u), other_holding_calls=other)
    calls = relations.per_call(prep)
    out["R_i"] = [x["hex"] for x in calls]
    out["empty_relation"] = any(x["relation"] == 0 for x in calls)
    try:
        sg = relations.semigroup([x["relation"] for x in calls])
        out["semigroup"] = {k: v for k, v in sg.items() if k not in ("P_r",)}
        out["r"] = sg.get("r")
        out["recurring_word"] = sg.get("recurring_word")
        if out["r"] is not None:
            audit = independent.audit(prep, calls, sg)
            out["audit_mismatches"] = audit.get("mismatches", audit) if isinstance(audit, dict) else audit
        out["verdict"] = "certified" if out["r"] is not None else (
            "non-forgetting" if out["recurring_word"] is not None else "capped")
    except LimitReached as exc:
        out["verdict"] = "capped"; out["cap"] = str(exc)
    out["seconds"] = round(time.monotonic() - t0, 4)
    return out
