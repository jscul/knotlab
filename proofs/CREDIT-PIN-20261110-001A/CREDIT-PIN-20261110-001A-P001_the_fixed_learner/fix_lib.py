"""The example learner of IN-OUT-20261110-001 with its defect fixed (research/CREDIT-PIN-20261110-001/preregistration.md, ticket A).

The frozen learner probes only at the floor and widens its attention only after failed probes, so a learner left above its floor with
dissonance outside its attention never probes again. The fix: a run of `widen` probe slots in a row that pass above the floor counts as
one failed probe for widening. Nothing else changes."""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/IN-OUT-20261110-001A/IN-OUT-20261110-001A-P001_inputs_and_outputs"))
import io_lib as I  # noqa: E402

W = I.W
PARAMS = dict(I.PARAMS)


def learn(E, K, ports, target, floor2, rng, params=PARAMS):
    """io_lib.learn with the stall rule; returns (steps, probes, radius, stalls)"""
    r, att, fails, probes, above, stalls = 0, I.near_lines(K, ports, 0), 0, 0, 0, 0
    for t in range(params["budget"]):
        if t % params["probe_every"] == 0:
            if E.W == floor2:
                above = 0
                probes += 1
                if I.probe(E, ports, target, floor2, rng, params["tau"]) == 0:
                    return t, probes, r, stalls
                fails += 1
                if fails % params["widen"] == 0 and r < params["rmax"]:
                    r += 1
                    att = I.near_lines(K, ports, r)
            else:
                above += 1
                if above % params["widen"] == 0:
                    stalls += 1
                    if r < params["rmax"]:
                        r += 1
                        att = I.near_lines(K, ports, r)
        if rng.random() < 0.5:
            p = rng.randrange(E.n)
            sites, mv = E.sites_of_point[p], ("flip", p)
            hot = any(i in att for (i, _) in sites)
        else:
            ls = [st for st in E.learn_sites() if st[0] in att]
            if not ls:
                continue
            st = rng.choice(ls)
            sites, mv, hot = [st], ("learn",) + st, True
        T = params["T_hot"] if hot else params["T_cold"]
        d, nv, dag = E.delta(sites)
        if E.W + d > floor2 + params["envelope"]:
            continue
        if d <= 0 or rng.random() < math.exp(-d / T):
            if mv[0] == "flip":
                E.x[mv[1]] ^= 1
            else:
                E.s[3 * mv[1] + mv[2]] ^= 1
            E.apply(sites, d, nv, dag)
    return None, probes, r, stalls


def run_interface(sp, ports, targets, seed, params=PARAMS, learner=None):
    """io_lib.run_interface with the fixed learner (or another learner with the same signature)"""
    learner = learner or learn
    rng = random.Random(seed)
    s, x = sp.start()
    E = W.Engine(sp.K, sp.O.S, s, x)
    W.m1(E, sp.floor2, rng)
    rows = []
    for tg in targets:
        out = learner(E, sp.K, ports, tg, sp.floor2, rng, params)
        steps, probes, r, stalls = out[:4]
        m = I.read_map(sp.K, E.s, ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "stalls": stalls,
               "map at the stop": m, "acting": sp.acting(E.s)}
        if len(out) > 4:
            row["credit"] = out[4]
        if steps is None:
            row["outcome"] = "not stopped, never reached (map uuuu)" if m == "uuuu" else "not stopped, other map"
        else:
            E.flip(rng.choice([p for p in sp.upper if p not in ports]))
            w = W.m1(E, sp.floor2, rng)
            after = I.read_map(sp.K, E.s, ports) if w == sp.floor2 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
