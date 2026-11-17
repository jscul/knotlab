"""Shared-runner job: finish SCALE-MEMORY-20261116-001A's n = 51200 stress cell for the scale-free arms only.

Disclosed deviation (coordinator, 2026-11-17 10:19 UTC): the full cell (test_job.py, phase "scale") was stopped with 4,855 of 6,250
runs finished, because its remaining runs were mostly the collapsed step-counted arms heading for the 2e9 cap. This job runs, for
the instances that cell had not finished, only the scale-free arms (L3s, L3sm, both seeds) and the comparators R needs (Novelty+
and sticky, training-tuned and re-tuned). The unfinished runs of the other arms are recorded as not finished. Same instances, run
seeds, caps and code paths as test_job.py.
Params: as test_job.py's phase "scale", plus done (the stopped cell's results.jsonl).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_job as T  # noqa: E402

KEEP = {"L3s_s0", "L3s_s1", "L3sm_s0", "L3sm_s1", "novelty_plus@train", "novelty_plus@cell", "sticky@train", "sticky@cell"}


def setup(params):
    T.setup({**params, "phase": "scale"})


def cases():
    done = set()
    for line in Path(T.P["done"]).read_text().splitlines():
        rec = json.loads(line)
        if rec.get("status") == "ok":
            done.add(rec["case"])
    for cid, payload in T.cases():
        if payload["n"] == 51200 and payload["arm"] in KEEP and cid not in done:
            yield cid, payload


run = T.run
