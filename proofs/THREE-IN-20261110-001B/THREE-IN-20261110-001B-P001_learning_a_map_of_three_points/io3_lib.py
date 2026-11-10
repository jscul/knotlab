"""Learning a map of three held points (research/THREE-IN-20261110-001/preregistration.md, ticket B, stage 1).

An interface is [input, input, input, output]; a target is the readings at the eight input patterns (index 4a + 2b + c). The learner is
CREDIT-PIN-20261110-001B's credit learner, unchanged, with STURDY-PROBE-20261110-001A's sturdier probe extended to three inputs: positive
checks one 4,000-step clamped walk from the current state; each negative check four 25,000-step walks, one from the current state and
three from fresh states. Maps are read by SAT only to score."""
import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe"))
sys.path.insert(0, str(ROOT / "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance"))
import probe_lib as P  # noqa: E402
import credit_lib as C  # noqa: E402

I, W, F = C.I, C.W, C.F
PATTERNS = list(itertools.product((0, 1), repeat=3))


def read_map3(K, s, ports):
    from pysat.solvers import Solver
    ins, o = ports[:3], ports[3]
    out = ""
    with Solver(name="cadical153", bootstrap_with=list(K.clauses(s))) as so:
        for x in PATTERNS:
            a = [(p + 1) if v else -(p + 1) for p, v in zip(ins, x)]
            v0, v1 = so.solve(assumptions=a + [-(o + 1)]), so.solve(assumptions=a + [o + 1])
            out += "x" if not (v0 or v1) else ("u" if v0 and v1 else ("1" if v1 else "0"))
    return out


def sturdy_probe3(E, ports, target, floor2, rng, tau):
    ins, o = ports[:3], ports[3]
    bad = 0
    for x, y in zip(PATTERNS, target):
        cl = dict(zip(ins, x))
        if y == "u":
            bad += not (P.reach_counted(E, {**cl, o: 0}, floor2, rng, tau) and P.reach_counted(E, {**cl, o: 1}, floor2, rng, tau))
        else:
            y = int(y)
            if not P.reach_counted(E, {**cl, o: y}, floor2, rng, tau):
                bad += 1
                continue
            wrong = {**cl, o: 1 - y}
            bad += any(P.reach_counted(E, wrong, floor2, rng, P.NEG_TAU, fresh=k > 0) for k in range(P.NEG_WALKS))
    return bad


def run_interface3(sp, ports, targets, seed):
    """the credit learner with the three-input sturdier probe; after each stop one random outermost-host point off the interface is
    flipped, M1 runs to the floor and the map is read again"""
    I.probe = sturdy_probe3
    rng = random.Random(seed)
    s, x = sp.start()
    E = W.Engine(sp.K, sp.O.S, s, x)
    W.m1(E, sp.floor2, rng)
    rows = []
    for tg in targets:
        steps, probes, r, stalls, credit = C.learn(E, sp.K, ports, tg, sp.floor2, rng, C.PARAMS)
        m = read_map3(sp.K, E.s, ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m,
               "acting": sp.acting(E.s)}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice([p for p in sp.upper if p not in ports]))
            w = W.m1(E, sp.floor2, rng)
            after = read_map3(sp.K, E.s, ports) if w == sp.floor2 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
