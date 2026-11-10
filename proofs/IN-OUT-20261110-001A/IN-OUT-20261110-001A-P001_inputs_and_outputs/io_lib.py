"""Inputs and outputs (research/IN-OUT-20261110-001/preregistration.md): the interface, the example learner and the readouts.

The world holds two points of an interface (the three outer points of an atom or a composite, on the line it replaced) at an input
pattern, and the third is read as the output. At the floor (W = |chi|, every line satisfied and no even face) the output is decided at
an input pattern when every floor state with those inputs gives it the same value, undecided ("u") when both values occur, and the
pattern is excluded ("x") when no floor state has those inputs. A map is the string of the four readings at inputs 00, 01, 10, 11.

The example learner sees its own dissonance, the floor, the interface points and the examples: the world holds the inputs and, as a
teacher, the output it asks for. It never reads a role, a class, an address, a solver's answer or a target signing. Maps are read by SAT
only to score the run afterwards."""
import itertools
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-WRITE-20261110-001A/NATIVE-WRITE-20261110-001A-P001_native_writing"))
import write_lib as W  # noqa: E402

INPUTS = list(itertools.product((0, 1), repeat=2))


def interfaces(sp):
    """every leaf's sides and every top-level composite's sides, as (name, [input, input, output])"""
    out = [("leaf %d" % j, list(sp.role_parts[j][1])) for j in sorted(sp.role_parts)]
    tops = sorted({q[:1] for q in sp.leaves if len(q) > 1})
    out += [("composite %d" % t[0], list(sp.O.group_parts(sp.K, t)[1])) for t in tops]
    return out


def read_map(K, s, ports):
    """scoring only: the map at the interface, by SAT over floor states (every line satisfied; a Kasteleyn law has no even face)"""
    from pysat.solvers import Solver
    ins, o = ports[:2], ports[2]
    out = ""
    with Solver(name="cadical153", bootstrap_with=list(K.clauses(s))) as so:
        for x in INPUTS:
            a = [(p + 1) if v else -(p + 1) for p, v in zip(ins, x)]
            v0, v1 = so.solve(assumptions=a + [-(o + 1)]), so.solve(assumptions=a + [o + 1])
            out += "x" if not (v0 or v1) else ("u" if v0 and v1 else ("1" if v1 else "0"))
    return out


def no_even_face(E):
    return all(a % 2 == 1 for a in E.ag)


# ---------------------------------------------------------------- the learner's own walks

def _hold(E, p, v):
    if E.x[p] != v:
        E.flip(p)


def reach(E, clamp, floor2, rng, tau, T=0.7):
    """on a copy: hold the clamped points, then a state-only Metropolis walk at temperature T on the other points for tau steps;
    True if the floor is reached"""
    snap = E.snapshot()
    for p, v in clamp.items():
        _hold(E, p, v)
    free = [p for p in range(E.n) if p not in clamp]
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
    E.restore(snap)
    return ok


def probe(E, ports, target, floor2, rng, tau):
    """The learner's test of the examples. For an example asking value y at inputs x: the floor must be reached with (x, y) held and
    not with (x, 1 - y). For an example asking "u": the floor must be reached with both. Returns the number of failing examples."""
    ins, o = ports[:2], ports[2]
    bad = 0
    for x, y in zip(INPUTS, target):
        cl = dict(zip(ins, x))
        if y == "u":
            bad += not (reach(E, {**cl, o: 0}, floor2, rng, tau) and reach(E, {**cl, o: 1}, floor2, rng, tau))
        else:
            y = int(y)
            bad += not (reach(E, {**cl, o: y}, floor2, rng, tau) and not reach(E, {**cl, o: 1 - y}, floor2, rng, tau))
    return bad


def near_lines(K, pts, r):
    """lines through the points, widened r times to the lines through any of their points"""
    pts = set(pts)
    lines = {i for i in range(K.n) if any(K.pt[i][k] in pts for k in range(3))}
    for _ in range(r):
        P = {K.pt[i][k] for i in lines for k in range(3)}
        lines = {i for i in range(K.n) if any(K.pt[i][k] in P for k in range(3))}
    return lines


PARAMS = dict(T_hot=2.0, T_cold=0.7, probe_every=200, tau=4000, envelope=4, widen=40, rmax=4, budget=4_000_000)


def learn(E, K, ports, target, floor2, rng, params=PARAMS):
    """Learning from examples with attention at the interface. Moves are proposed at random: a state flip of a random point
    (probability 1/2) or a sign change at a random A21 site on an attention line. Accepted by the Metropolis rule on W at temperature
    T_hot when the move touches an attention line and T_cold otherwise, never above floor + envelope. Attention starts at the lines
    through the interface points and widens by one step after every `widen` failed probes, up to rmax. Every probe_every steps at the
    floor the learner runs its probe and stops when no example fails. Returns (steps, probes, radius), steps None if the budget ran out."""
    r, att, fails, probes = 0, near_lines(K, ports, 0), 0, 0
    for t in range(params["budget"]):
        if t % params["probe_every"] == 0 and E.W == floor2:
            probes += 1
            if probe(E, ports, target, floor2, rng, params["tau"]) == 0:
                return t, probes, r
            fails += 1
            if fails % params["widen"] == 0 and r < params["rmax"]:
                r += 1
                att = near_lines(K, ports, r)
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
    return None, probes, r


def run_interface(sp, ports, targets, seed, params=PARAMS):
    """learn each target in turn from the start; after each stop flip one random outermost-host point off the interface, run M1, and
    read the map again"""
    rng = random.Random(seed)
    s, x = sp.start()
    E = W.Engine(sp.K, sp.O.S, s, x)
    W.m1(E, sp.floor2, rng)
    rows = []
    for tg in targets:
        steps, probes, r = learn(E, sp.K, ports, tg, sp.floor2, rng, params)
        m = read_map(sp.K, E.s, ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m,
               "acting": sp.acting(E.s)}
        if steps is None:
            row["outcome"] = "not stopped, never reached (map uuuu)" if m == "uuuu" else "not stopped, other map"
        else:
            E.flip(rng.choice([p for p in sp.upper if p not in ports]))
            w = W.m1(E, sp.floor2, rng)
            after = read_map(sp.K, E.s, ports) if w == sp.floor2 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
