"""Shared-runner job resuming WEIGHTS-20261112-001A-E001's calibration (the enlarged arm on COMMON-FOLD's travelling bases with one
certified direction in SHIFT-COUNT) after the owner's pause; census.py imported unchanged; cases are the items not yet in
calibration.jsonl."""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
spec = importlib.util.spec_from_file_location("wcensus", os.path.join(HERE, "census.py"))
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)

# Deviation, recorded in the decision note: the frozen enlarged arm searches shifts up to 8 with multiples up to 4 (up to 32 cells
# away) inside SHIFT-COUNT's window of -30 .. 30, so a translate can fall outside it (KeyError); the frozen run's worker then died and
# the sample was recorded as dropped at the cap. The enlarged arm here uses the window -42 .. 42 instead; the main arm is unchanged.
_orig_window = W.S.C.window


def _enlarged_fixed(kinds):
    W.S.C.window = lambda k, w: _orig_window(k, (-42, 42, -42, 42))
    try:
        return W._frozen_enlarged(kinds)
    finally:
        W.S.C.window = _orig_window


W._frozen_enlarged = W.enlarged
W.enlarged = _enlarged_fixed

DONE = os.path.join(ROOT, "artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts/calibration.jsonl")


def setup(params):
    pass


def cases():
    done = {(r["item"]["sample"], r["item"]["r"]) for r in map(json.loads, open(DONE))}
    sc = [r for r in map(json.loads, open(W.SC_ROWS)) if "rank certified" in r and r["rank certified"] < 2 and r["sample"] != "base16"]
    sms = {(x["sample"], x["r"]): x for x in W.T.samples()}
    for r in sc:
        if (r["sample"], r["r"]) not in done:
            yield f"{r['sample']}-{r['r']}", {"sample": r["sample"], "r": r["r"], "kinds": sms[(r["sample"], r["r"])]["kinds"]}


def run(case_id, payload):
    e = W.enlarged(payload["kinds"])
    return {"sample": payload["sample"], "r": payload["r"], "enlarged": {k: v for k, v in e.items() if k != "certificates"}}
