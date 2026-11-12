"""The drawing's two jobs, apart (research/LAW-RIGIDITY-20261112-001/preregistration.md).

On one copy of the drawn knot pattern (2, 0, 4) (J1), the learner with the drawing's faces feels W = 2 x violated knots + the sum of a
face term over faces (graded: each face's agreeing corners beyond one, and an even count, cost more). Two variants replace the graded face
term:

- R, the rest set without the grade: W = 2 x violated knots + 2 x [some face does not have exactly one agreeing corner]. The floor is the
  same as with faces (no violated knot, and the law a Kasteleyn law, in the literature's term), so the learner can rest only where the
  faces allow; leaving that set costs a flat 2, however many faces it disturbs. Sign changes are proposed at the same places as with faces.
- RS: R, and after each stop the repair flips distinctions only (a rule we supply): the learned law cannot change during the repair.

The learner, its probe, budgets and harness are UNDRAWN-LEARN-20261111-001's (SHARED-COUNT-20261111-001's), unchanged but for the engine
and, in RS, the repair."""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/UNDRAWN-LEARN-20261111-001A/UNDRAWN-LEARN-20261111-001A-P001_learning_without_a_drawing"))
import undrawn_lib as UL  # noqa: E402

J, F, PL, W, C, I = UL.J, UL.F, UL.PL, UL.W, UL.C, UL.I


class RestEngine(W.Engine):
    """the drawn engine's bookkeeping, with W = 2 x violated + 2 x [nbad > 0], nbad the faces whose agreeing corners are not exactly one"""

    def __init__(self, K, S, s, x):
        super().__init__(K, S, s, x)
        self.nbad = sum(a != 1 for a in self.ag)
        self.W = 2 * sum(self.viol) + 2 * (self.nbad > 0)

    def delta(self, sites):
        _, nv, dag = W.Engine.delta(self, sites)
        dv = sum(b - self.viol[i] for i, b in nv.items())
        db = sum((self.ag[v] + x != 1) - (self.ag[v] != 1) for v, x in dag.items())
        return 2 * dv + 2 * ((self.nbad + db > 0) - (self.nbad > 0)), nv, dag

    def apply(self, sites, d, nv, dag):
        self.nbad += sum((self.ag[v] + x != 1) - (self.ag[v] != 1) for v, x in dag.items())
        W.Engine.apply(self, sites, d, nv, dag)

    def snapshot(self):
        return W.Engine.snapshot(self) + (self.nbad,)

    def restore(self, snap):
        W.Engine.restore(self, snap[:-1])
        self.nbad = snap[-1]


def m1_states(E, floor2, rng, rounds=2000):
    """W.m1 with state flips only: a random flip lowering W, else one keeping it, until the floor"""
    for _ in range(rounds):
        if E.W == floor2:
            break
        moves = [(E.delta(E.sites_of_point[p]), p, E.sites_of_point[p]) for p in range(E.n)]
        pick = [m for m in moves if m[0][0] < 0] or [m for m in moves if m[0][0] == 0]
        if not pick:
            break
        (d, nv, dag), p, sites = rng.choice(pick)
        E.x[p] ^= 1
        E.apply(sites, d, nv, dag)
    return E.W


def run(variant, targets, seed, budget=8_000_000):
    """UNDRAWN-LEARN-20261111-001's run on J1 with RestEngine; in RS the repair after each stop flips distinctions only"""
    sp = J.Space(1)
    I.probe = F.sturdy_probe_k
    params = dict(C.PARAMS, budget=budget)
    rng = random.Random(seed)
    s, x = sp.start()
    E = RestEngine(sp.K, sp.S, s, x)
    W.m1(E, 0, rng)
    repair = m1_states if variant == "RS" else W.m1
    rows = []
    for tg in targets:
        steps, probes, r, stalls, credit = C.learn(E, sp.K, sp.ports, tg, 0, rng, params)
        m = F.read_map_k(sp.K, E.s, sp.ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice(sp.movable))
            w = repair(E, 0, rng)
            after = F.read_map_k(sp.K, E.s, sp.ports) if w == 0 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
