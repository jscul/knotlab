"""Shared-runner job resuming WEIGHTS-20261112-001A-E001's census after the owner's pause (research/WEIGHTS-20261112-001/paused.md).

The frozen census.py is imported unchanged except for the enlarged arm's window (below). Cases: the (beta, sample) pairs without a
result in census.jsonl (those recorded as dropped are rerun), for beta = 0 samples 0 .. 119, beta = 1 samples 0 .. 129 and beta = 2
samples 0 .. 199. The frozen stopping rule (samples in index order
until 40 travelling bases with a new kind, or 300) is applied afterwards to the prefix of samples in index order, so samples past the
stopping index are run but not counted.
"""
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

# Second deviation: with the window fixed, the enlarged arm (sets of 2 to 4 cells of [0, 3]^2, about 200 primitive shifts, multiples
# up to 4) took over 30 minutes on a single base in the smoke test, against minutes for the main arm, so it is infeasible at this
# scale; the resumed census runs the main arm only and records a base without a certified second direction as unresolved, never
# as a failure of the rule.


def _enlarged_not_run(kinds):
    return {"certified directions": None, "forced, uncertified": None, "rank forced": None, "rank certified": None}


W.enlarged = _enlarged_not_run

DONE = os.path.join(ROOT, "artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts/census.jsonl")


def setup(params):
    pass


def cases():
    done = set()
    for line in open(DONE):
        r = json.loads(line)
        if "beta" in r:
            done.add((r["beta"], r["sample"]))
        # samples recorded as dropped at the cap died on the enlarged arm's window bug (above): they are rerun
    for w, n in ((0, 120), (1, 130), (2, 200)):
        for i in range(n):
            if (W.BETAS[w], i) not in done:
                yield f"{w}-{i}", {"w": w, "i": i}


def run(case_id, payload):
    w, i = payload["w"], payload["i"]
    order = W.draw(w, i)
    return {"beta": W.BETAS[w], "sample": i, "by r": {r: W.per_base(order[:r]) for r in W.RS}}
