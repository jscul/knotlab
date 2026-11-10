"""A sturdier probe for the example learner (research/STURDY-PROBE-20261110-001/preregistration.md).

The probe of IN-OUT-20261110-001 certifies only that an asked value is reachable; it reads a wrong value as unreachable when one 4,000-step
walk from the current state misses it. The sturdier probe keeps the positive checks as they were and makes each negative check four
walks of 25,000 steps: one from the current state and three from fresh random states of the free points. Nothing else changes.
Both probes count their walk steps in STEPS."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/IN-OUT-20261110-001A/IN-OUT-20261110-001A-P001_inputs_and_outputs"))
import io_lib as I  # noqa: E402

STEPS = [0]
NEG_WALKS, NEG_TAU = 4, 25000


def reach_counted(E, clamp, floor2, rng, tau, T=0.7, fresh=False):
    """io_lib.reach, step for step and draw for draw, with its steps counted; fresh=True first sets every free point at random"""
    snap = E.snapshot()
    free = [p for p in range(E.n) if p not in clamp]
    if fresh:
        for p in free:
            if rng.random() < 0.5:
                E.flip(p)
    for p, v in clamp.items():
        if E.x[p] != v:
            E.flip(p)
    ok = E.W == floor2
    t = 0
    while not ok and t < tau:
        p = rng.choice(free)
        sites = E.sites_of_point[p]
        d, nv, dag = E.delta(sites)
        if d <= 0 or rng.random() < math.exp(-d / T):
            E.x[p] ^= 1
            E.apply(sites, d, nv, dag)
            ok = E.W == floor2
        t += 1
    STEPS[0] += t
    E.restore(snap)
    return ok


def old_probe_counted(E, ports, target, floor2, rng, tau):
    """io_lib.probe exactly, with its walk steps counted"""
    ins, o = ports[:2], ports[2]
    bad = 0
    for x, y in zip(I.INPUTS, target):
        cl = dict(zip(ins, x))
        if y == "u":
            bad += not (reach_counted(E, {**cl, o: 0}, floor2, rng, tau) and reach_counted(E, {**cl, o: 1}, floor2, rng, tau))
        else:
            y = int(y)
            bad += not (reach_counted(E, {**cl, o: y}, floor2, rng, tau) and not reach_counted(E, {**cl, o: 1 - y}, floor2, rng, tau))
    return bad


def sturdy_probe(E, ports, target, floor2, rng, tau):
    """positive checks as io_lib.probe; a negative check passes only if none of NEG_WALKS walks of NEG_TAU steps (the first from the
    current state, the rest from fresh random states) reaches the floor with the wrong value held"""
    ins, o = ports[:2], ports[2]
    bad = 0
    for x, y in zip(I.INPUTS, target):
        cl = dict(zip(ins, x))
        if y == "u":
            bad += not (reach_counted(E, {**cl, o: 0}, floor2, rng, tau) and reach_counted(E, {**cl, o: 1}, floor2, rng, tau))
        else:
            y = int(y)
            if not reach_counted(E, {**cl, o: y}, floor2, rng, tau):
                bad += 1
                continue
            wrong = {**cl, o: 1 - y}
            bad += any(reach_counted(E, wrong, floor2, rng, NEG_TAU, fresh=k > 0) for k in range(NEG_WALKS))
    return bad
