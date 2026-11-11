"""A learned memory that computes parity (research/LEARN-PARITY-20261111-001/preregistration.md).

Two spaces: T1, the bare 8-point lattice torus (2,0,4); T2, a memory host, the knot sphere K_2 with the torus (2,0,4) less a point grown
as an atom at its first line (nest_lib.grow_leaf), 23 points, genus 1. The learner is CREDIT-PIN-20261110-001B's credit learner with
THREE-IN-20261110-001B's three-input sturdier probe, both unchanged; only the harness around them is new (a space without an outermost
nested host). Maps are read by SAT afterwards, exactly."""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/THREE-IN-20261110-001B/THREE-IN-20261110-001B-P001_learning_a_map_of_three_points"))
import io3_lib as L3  # noqa: E402

C, I, W, F, P = L3.C, L3.I, L3.W, L3.F, L3.P
SP = W.SP
N = SP.N
BUDGET = 8_000_000


class Bare:
    """a knot space given by its surface; the start is the base Kasteleyn law (no class added) at the solver's first satisfying state"""

    def __init__(self, name, S, interface, movable=None):
        self.name, self.S = name, S
        self.K = N.SL.KnotSpace(S)
        self.floor2 = abs(self.K.chi)
        self.ports = list(interface)
        self.movable = [p for p in (movable if movable is not None else range(self.K.n)) if p not in self.ports]

    def start(self):
        s = self.K.signing()
        ok, model = self.K.sat(s)
        assert ok
        return s, [int(model[p] > 0) for p in range(self.K.n)]


def t1():
    return Bare("T1 torus (2,0,4)", N.SL.torus(2, 0, 4), [0, 1, 4, 5])


def t2():
    Y = N.Nested(SP.SPH[2].S, SP.SPH[2].s0)
    Y.grow_leaf(Y.where[SP.lines_of(2)[0]], N.A.Atom((2, 0, 4)))
    sp = Bare("T2 K_2 with the torus (2,0,4) grown at a line", Y.S, [16, 19, 20, 0])
    sp.movable = [p for p in range(sp.K.n) if Y.path[sp.K.points[p]] == () and p not in sp.ports]
    sp.nested = Y
    return sp


def run(sp, targets, seed, budget=BUDGET):
    """the credit learner with the three-input sturdier probe; after each stop one random movable point is flipped, M1 runs to the
    floor, and the map is read again by SAT"""
    I.probe = L3.sturdy_probe3
    params = dict(C.PARAMS, budget=budget)
    rng = random.Random(seed)
    s, x = sp.start()
    E = W.Engine(sp.K, sp.S, s, x)
    W.m1(E, sp.floor2, rng)
    rows = []
    for tg in targets:
        steps, probes, r, stalls, credit = C.learn(E, sp.K, sp.ports, tg, sp.floor2, rng, params)
        m = L3.read_map3(sp.K, E.s, sp.ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice(sp.movable))
            w = W.m1(E, sp.floor2, rng)
            after = L3.read_map3(sp.K, E.s, sp.ports) if w == sp.floor2 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
