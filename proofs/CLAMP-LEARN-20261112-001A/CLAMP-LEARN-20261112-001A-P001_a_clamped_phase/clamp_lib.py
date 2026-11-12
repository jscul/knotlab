"""Let the examples shape the dissonance the learner feels (research/CLAMP-LEARN-20261112-001/preregistration.md).

On one copy of (2, 0, 4) with NATIVE-GRADE-20261112-001's graded value-free engine (64 laws at rest; setting GE of STEER-LEARN-20261112-001):

- C, a clamped phase: while it learns, the world holds one example (its three inputs and its output) at a time, cycling through the eight
  examples, K = 200 steps each; the learner's state and sign moves feel the dissonance under that clamp. After each cycle the clamp is
  released, and if the learner is at rest it runs the sturdier probe.
- CA, contrastive acceptance (the advisor model's suggestion, after Boltzmann machine learning): as C, and a second copy of the state is
  relaxed under the wrong output for the same inputs (100 state-only steps at each switch of example); a proposed sign change is accepted
  by the Metropolis rule on (its change of dissonance under the correct clamp) minus (its change under the wrong clamp).
- Biased walk (B169's cheap part): the unchanged learner (STEER-LEARN's B) taught an impossible map, so it never stops; at each probe the
  map of its law is read (scoring only).

Every step is counted: learning moves (state and sign apart), the wrong copy's relaxation steps, and the probe's walk steps."""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/STEER-LEARN-20261112-001A/STEER-LEARN-20261112-001A-P001_steering_rules"))
import steer_lib as S  # noqa: E402

J, F, W, C, I, P, G = S.J, S.F, S.W, S.C, S.I, S.P, S.G
K_STEPS, K_WRONG = 200, 100
IMPOSSIBLE = "00000001"   # the AND of three held inputs: not self-dual, so no law computes it (theorem D)


def clamp_to(E, clamp):
    for p, v in clamp.items():
        if E.x[p] != v:
            E.flip(p)


def relax_states(E, free, floor2, rng, tau, cnt, T=0.7):
    t = 0
    while E.W != floor2 and t < tau:
        p = rng.choice(free)
        sites = E.sites_of_point[p]
        d, nv, dag = E.delta(sites)
        if d <= 0 or rng.random() < math.exp(-d / T):
            E.x[p] ^= 1
            E.apply(sites, d, nv, dag)
        t += 1
    cnt["wrong copy steps"] += t


def learn_clamped(E, K, ports, target, floor2, rng, rule, cnt, params=None):
    params = params or dict(C.PARAMS, budget=2_000_000)
    ins, o = ports[:-1], ports[-1]
    att = I.near_lines(K, ports, params["rmax"])
    free_all = [p for p in range(E.n)]
    free_unclamped = [p for p in range(E.n) if p not in ports]
    mem = {"plus": [], "minus": [], "fail_viol": []}
    Ew = None
    t = 0
    while t < params["budget"]:
        for e, (x, y) in enumerate(zip(S.PATTERNS, target)):
            yv = rng.randrange(2) if y == "u" else int(y)
            clamp = {**dict(zip(ins, x)), o: yv}
            clamp_to(E, clamp)
            if rule == "CA":
                Ew = E.__class__(K, E.S if hasattr(E, "S") else None, E.s, E.x) if False else _copy(E)
                clamp_to(Ew, {**dict(zip(ins, x)), o: 1 - yv})
                relax_states(Ew, free_unclamped, floor2, rng, K_WRONG, cnt)
            for _ in range(K_STEPS):
                t += 1
                if rng.random() < 0.5:
                    p = rng.choice(free_unclamped)
                    sites, mv = E.sites_of_point[p], ("flip", p)
                else:
                    ls = [st for st in E.learn_sites() if st[0] in att]
                    if not ls:
                        continue
                    st = rng.choice(ls)
                    sites, mv = [st], ("learn",) + st
                d, nv, dag = E.delta(sites)
                if E.W + d > floor2 + params["envelope"]:
                    continue
                dd = d
                if rule == "CA" and mv[0] == "learn":
                    dd = d - Ew.delta(sites)[0]
                if dd <= 0 or rng.random() < math.exp(-dd / params["T_hot"]):
                    if mv[0] == "flip":
                        E.x[mv[1]] ^= 1
                        cnt["state moves"] += 1
                    else:
                        E.s[3 * mv[1] + mv[2]] ^= 1
                        cnt["sign moves"] += 1
                        if rule == "CA":
                            dw, nvw, dagw = Ew.delta(sites)
                            Ew.s[3 * mv[1] + mv[2]] ^= 1
                            Ew.apply(sites, dw, nvw, dagw)
                    E.apply(sites, d, nv, dag)
                cnt["learning steps"] += 1
        # release the clamp: relax the interface with the rest, then probe if at rest
        relax_states(E, free_all, floor2, rng, params["tau"], cnt)
        if E.W == floor2:
            cnt["probes"] += 1
            if S.steer_probe(E, ports, target, floor2, rng, params["tau"], mem) == 0:
                return True
    return False


def _copy(E):
    Ec = object.__new__(E.__class__)
    Ec.__dict__.update({k: (list(v) if isinstance(v, list) else v) for k, v in E.__dict__.items()})
    Ec.L = [list(l) for l in E.L]
    if hasattr(E, "par"):
        Ec.par = list(E.par)
    return Ec


def run(rule, target, seed):
    sp = J.Space(1)
    rng = random.Random(seed)
    s, x = sp.start()
    E = G.GradeEngine(sp.K, sp.S, s, x)
    W.m1(E, 0, rng)
    cnt = {"probes": 0, "learning steps": 0, "state moves": 0, "sign moves": 0, "wrong copy steps": 0}
    P.STEPS[0] = 0
    found = learn_clamped(E, sp.K, sp.ports, target, 0, rng, rule, cnt)
    cnt["probe walk steps"] = P.STEPS[0]
    cnt["all steps"] = cnt["learning steps"] + cnt["wrong copy steps"] + cnt["probe walk steps"]
    m = F.read_map_k(sp.K, E.s, sp.ports)
    return {"rule": rule, "target": target, "seed": seed, "found": found and m == target, "map at the stop": m, **cnt}


def biased_walk(setting, seed, nprobes):
    """the unchanged learner taught an impossible map: the map of its law at each of its first nprobes probes"""
    sp = J.Space(1)
    rng = random.Random(seed)
    s, x = sp.start()
    E = S.engine(setting, sp, s, x)
    W.m1(E, 0, rng)
    maps = []
    stats = {"probes": 0, "candidate checks": 0}

    def note(sv):
        maps.append(F.read_map_k(sp.K, sv, sp.ports))
        return False
    params = dict(C.PARAMS, budget=10 ** 9)
    orig = S.steer_probe

    def counting_probe(E_, ports, target, floor2, rng_, tau, mem):
        note(E_.s)
        if len(maps) >= nprobes:
            raise StopIteration
        return orig(E_, ports, target, floor2, rng_, tau, mem)
    S.steer_probe = counting_probe
    try:
        S.learn(E, sp.K, sp.ports, IMPOSSIBLE, 0, rng, "B", stats, params=params)
    except StopIteration:
        pass
    finally:
        S.steer_probe = orig
    return maps


# ---------------------------------------------------------------- starts, rest laws and baselines

def rest_laws(setting):
    """one signing for every law at rest: F, no even face; GE, all shortest sums equal (laws with a satisfying state)"""
    B = J.Joined(1)
    K0 = B.copies[0]
    pt = [list(t) for t in B.pt]
    _, seqs = S.N.shortest_sequences(pt)
    out = []
    from pysat.solvers import Solver
    for law in S.UL.laws(B):
        if setting == "F":
            if K0.even_faces(law):
                continue
        elif len({sum(law[3 * k + pt[k].index(d)] for (k, d) in sq) % 2 for sq in seqs}) != 1:
            continue
        with Solver(name="cadical153", bootstrap_with=B.clauses(law)) as so:
            if so.solve():
                out.append(law)
    return out


def random_start(setting, rng):
    """a uniform law at rest, a uniform flip of each distinction (gauge), and the solver's first satisfying state, as a start"""
    B = J.Joined(1)
    law = list(rng.choice(rest_laws(setting)))
    for p in range(B.real):
        if rng.random() < 0.5:
            for i in range(B.nl):
                for k in range(3):
                    if B.pt[i][k] == p:
                        law[3 * i + k] ^= 1
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=B.clauses(law)) as so:
        assert so.solve()
        m = so.get_model()
    return law, [int(m[p] > 0) if p < len(m) else 0 for p in range(B.n)]


def start_engine(setting, start, rng):
    sp = J.Space(1)
    s, x = sp.start() if start == "fixed" else random_start(setting, rng)
    E = S.engine(setting, sp, s, x)
    W.m1(E, 0, rng)
    return sp, E


def run2(rule, target, seed, start="random", setting="GE"):
    """C or CA (clamped), or B (the unchanged learner), from a fixed or random start, every step counted"""
    rng = random.Random(seed)
    sp, E = start_engine(setting, start, rng)
    cnt = {"probes": 0, "learning steps": 0, "state moves": 0, "sign moves": 0, "wrong copy steps": 0}
    P.STEPS[0] = 0
    if rule == "B":
        stats = {"probes": 0, "candidate checks": 0}
        found = S.learn(E, sp.K, sp.ports, target, 0, rng, "B", stats)
        cnt["probes"] = stats["probes"]
        cnt["learning steps"] = stats["steps"] if stats["steps"] is not None else 2_000_000
    else:
        found = learn_clamped(E, sp.K, sp.ports, target, 0, rng, rule, cnt)
    cnt["probe walk steps"] = P.STEPS[0]
    cnt["all steps"] = cnt["learning steps"] + cnt["wrong copy steps"] + cnt["probe walk steps"]
    m = F.read_map_k(sp.K, E.s, sp.ports)
    return {"rule": rule, "target": target, "seed": seed, "start": start, "setting": setting, "found": found and m == target,
            "map at the stop": m, **cnt}


def walk2(setting, seed, nprobes, start):
    """biased_walk from a fixed or random start"""
    rng = random.Random(seed)
    sp, E = start_engine(setting, start, rng)
    maps = []
    orig = S.steer_probe

    def counting_probe(E_, ports, target, floor2, rng_, tau, mem):
        maps.append(F.read_map_k(sp.K, E_.s, sp.ports))
        if len(maps) >= nprobes:
            raise StopIteration
        return orig(E_, ports, target, floor2, rng_, tau, mem)
    S.steer_probe = counting_probe
    try:
        S.learn(E, sp.K, sp.ports, IMPOSSIBLE, 0, rng, "B", {"probes": 0, "candidate checks": 0}, params=dict(C.PARAMS, budget=10 ** 9))
    except StopIteration:
        pass
    finally:
        S.steer_probe = orig
    return maps


def probe_cost(setting, law, target, rng):
    """the sturdier probe's walk steps on one law at rest (from the solver's first satisfying state, relaxed by M1)"""
    sp = J.Space(1)
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=sp.K.clauses(law)) as so:
        assert so.solve()
        m = so.get_model()
    x = [int(m[p] > 0) if p < len(m) else 0 for p in range(sp.K.n)]
    E = S.engine(setting, sp, law, x)
    W.m1(E, 0, rng)
    P.STEPS[0] = 0
    S.steer_probe(E, sp.ports, target, 0, rng, C.PARAMS["tau"], {})
    return P.STEPS[0]
