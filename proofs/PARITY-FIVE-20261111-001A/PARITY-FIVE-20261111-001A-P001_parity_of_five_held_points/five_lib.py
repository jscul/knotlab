"""Parity of more held points (research/PARITY-FIVE-20261111-001/preregistration.md).

Exact method. For a knot space and a class, the floor states (every line satisfied; a Kasteleyn law has no even face) are enumerated by SAT
with blocking clauses. Their parity checks are the vectors v over the points with v.x the same for every floor state x: the orthogonal
complement, over F2, of the span of the differences x - x0. A set T of k + 1 points carries a k-input parity map (any k of them held, the
last read) exactly when its indicator is such a check and the floor states' projection onto T has all 2^k patterns of k of its points.
By theorem D of IN-OUT-20261110-001 only even |T| can occur (flipping every point changes v.x by |T|)."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/UNATE-20261111-001A/UNATE-20261111-001A-P001_are_maps_of_held_points_unate"))
import unate_lib as U  # noqa: E402

SL = U.SL
MAX_N, STATE_CAP = 24, 200_000
EXTRA_N = 32


def tori(min_n=3, max_n=MAX_N):
    out = []
    for N in range(min_n, max_n + 1):
        for t in SL.hnf_sublattices(N):
            if SL.torus_kind(*t) == "degenerate":
                continue
            K = SL.KnotSpace(SL.torus(*t))
            if K.simple():
                out.append((t, N))
    return out


def floor_states(K, s, cap=STATE_CAP):
    from pysat.solvers import Solver
    out = []
    with Solver(name="cadical153", bootstrap_with=K.clauses(s)) as so:
        while so.solve():
            m = so.get_model()
            x = [int(m[p] > 0) for p in range(K.n)]
            out.append(sum(b << p for p, b in enumerate(x)))
            if len(out) > cap:
                return None
            so.add_clause([-(p + 1) if b else (p + 1) for p, b in enumerate(x)])
    return out


def echelon(vectors):
    basis = {}
    for v in vectors:
        for bit in sorted(basis, reverse=True):
            if (v >> bit) & 1:
                v ^= basis[bit]
        if v:
            basis[v.bit_length() - 1] = v
            for b2 in list(basis):
                if b2 != v.bit_length() - 1 and (basis[b2] >> (v.bit_length() - 1)) & 1:
                    basis[b2] ^= v
    return basis


def in_span(basis, v):
    for bit in sorted(basis, reverse=True):
        if (v >> bit) & 1:
            v ^= basis[bit]
    return v == 0


def parity_sets(states, n, size):
    """every set of `size` points whose indicator is a parity check of the floor states and whose projection is full"""
    if not states:
        return []
    x0 = states[0]
    span = echelon([x ^ x0 for x in states])
    found = []
    for T in itertools.combinations(range(n), size):
        v = sum(1 << p for p in T)
        # v is a check exactly when it is orthogonal to every difference, i.e. to the span's basis
        if any(bin(v & b).count("1") % 2 for b in span.values()):
            continue
        proj = {tuple((x >> p) & 1 for p in T[:-1]) for x in states}
        if len(proj) == 2 ** (size - 1):
            found.append((T, bin(v & x0).count("1") % 2))
    return found


# ---------------------------------------------------------------- stage 1c: two handles composed

def composed():
    """the knot sphere K_2 with the torus (2, 0, 4), less a point, grown as an atom at each of its two lines (nest_lib.grow_leaf): 30
    points, genus 2; the movable points for stage 2 are the host sphere's"""
    PL = _parity_lib()
    N, SP = PL.N, PL.SP
    Y = N.Nested(SP.SPH[2].S, SP.SPH[2].s0)
    for line in SP.lines_of(2):
        Y.grow_leaf(Y.where[line], N.A.Atom((2, 0, 4)))
    return Y


# ---------------------------------------------------------------- stage 2: learning, if a five-input parity space exists

def _parity_lib():
    sys.path.insert(0, str(ROOT / "proofs/LEARN-PARITY-20261111-001A/LEARN-PARITY-20261111-001A-P001_learning_parity"))
    import parity_lib
    return parity_lib


def read_map_k(K, s, ports):
    """scoring only: the map at the interface (inputs ports[:-1], output ports[-1]) by SAT, one reading per input pattern"""
    from pysat.solvers import Solver
    ins, o = ports[:-1], ports[-1]
    out = ""
    with Solver(name="cadical153", bootstrap_with=list(K.clauses(s))) as so:
        for x in itertools.product((0, 1), repeat=len(ins)):
            a = [(p + 1) if v else -(p + 1) for p, v in zip(ins, x)]
            v0, v1 = so.solve(assumptions=a + [-(o + 1)]), so.solve(assumptions=a + [o + 1])
            out += "x" if not (v0 or v1) else ("u" if v0 and v1 else ("1" if v1 else "0"))
    return out


def sturdy_probe_k(E, ports, target, floor2, rng, tau):
    """THREE-IN-20261110-001B's sturdy_probe3 over every input pattern of len(ports) - 1 held points, otherwise unchanged: a positive check
    is one tau-step clamped walk from the current state; a negative check passes only if none of four 25,000-step walks (the first from
    the current state, three from fresh states) reaches the floor with the wrong value held"""
    P = _parity_lib().L3.P
    ins, o = ports[:-1], ports[-1]
    bad = 0
    for x, y in zip(itertools.product((0, 1), repeat=len(ins)), target):
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


def parity_string(k, c=0):
    return "".join(str((sum(x) + c) % 2) for x in itertools.product((0, 1), repeat=k))


def space(found):
    """the space a stage-1 hit names, as LEARN-PARITY-20261111-001's Bare: a lattice torus, or the composed genus-2 space"""
    PL = _parity_lib()
    ports = list(found["set"])
    if found["space"] == "composed":
        Y = composed()
        sp = PL.Bare("composed genus 2", Y.S, ports)
        sp.movable = [p for p in range(sp.K.n) if Y.path[sp.K.points[p]] == () and p not in ports]
        return sp
    return PL.Bare("torus %s" % (tuple(found["space"]),), SL.torus(*found["space"]), ports)


def run(sp, targets, seed, budget=8_000_000):
    """LEARN-PARITY-20261111-001A's run with the probe and the scoring read over five held points: the credit learner, unchanged; after
    each stop one random movable point is flipped, M1 runs to the floor, and the map is read again by SAT"""
    import random
    PL = _parity_lib()
    C, I, W = PL.C, PL.I, PL.W
    I.probe = sturdy_probe_k
    params = dict(C.PARAMS, budget=budget)
    rng = random.Random(seed)
    s, x = sp.start()
    E = W.Engine(sp.K, sp.S, s, x)
    W.m1(E, sp.floor2, rng)
    rows = []
    for tg in targets:
        steps, probes, r, stalls, credit = C.learn(E, sp.K, sp.ports, tg, sp.floor2, rng, params)
        m = read_map_k(sp.K, E.s, sp.ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice(sp.movable))
            w = W.m1(E, sp.floor2, rng)
            after = read_map_k(sp.K, E.s, sp.ports) if w == sp.floor2 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows


def run_found(found, targets, seed):
    return run(space(found), targets, seed)
