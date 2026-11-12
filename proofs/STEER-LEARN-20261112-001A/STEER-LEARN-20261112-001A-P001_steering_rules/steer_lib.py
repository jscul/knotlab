"""A learner whose examples steer its search (research/STEER-LEARN-20261112-001/preregistration.md).

Two settings on one copy of (2, 0, 4) (J1): F, the drawn engine (dissonance with the drawing's faces; the learner rests at 4 law classes);
GE, NATIVE-GRADE-20261112-001's graded value-free engine (64 laws at rest). Four learners, each run to its first stop at one target:
B, the credit learner unchanged; P, persistence targeting; M, make and break; A, two-sided acceptance. The probe is the sturdier probe
over every input pattern, step for step, but it also keeps what it saw: for each example, the end state of its positive walk and, when a
negative check fails, the wrong state it reached. Costs: world probes (each a full probe of the current law), and candidate checks (each a
candidate law checked against the stored states), charged as probes too."""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-GRADE-20261112-001A/NATIVE-GRADE-20261112-001A-P001_a_graded_native_rule"))
import grade_lib as G  # noqa: E402

N, UL, J, F, W, C, I = G.N, G.UL, G.J, G.F, G.W, G.C, G.I
P = F._parity_lib().L3.P
import itertools  # noqa: E402

PATTERNS = list(itertools.product((0, 1), repeat=3))


def engine(setting, sp, s, x):
    return W.Engine(sp.K, sp.S, s, x) if setting == "F" else G.GradeEngine(sp.K, sp.S, s, x)


def reach_end(E, clamp, floor2, rng, tau, T=0.7, fresh=False):
    """probe_lib.reach_counted, draw for draw, also returning the end state and the knots violated in it"""
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
    P.STEPS[0] += t
    x_end = list(E.x)
    viol = [i for i in range(E.n) if E.viol[i]]
    E.restore(snap)
    return ok, x_end, viol


def steer_probe(E, ports, target, floor2, rng, tau, mem):
    """the sturdier probe (THREE-IN-20261110-001B's rule over every input pattern), keeping what it saw in mem"""
    ins, o = ports[:-1], ports[-1]
    bad = 0
    mem["plus"], mem["minus"], mem["fail_viol"] = [], [], []
    for x, y in zip(PATTERNS, target):
        cl = dict(zip(ins, x))
        if y == "u":
            a = reach_end(E, {**cl, o: 0}, floor2, rng, tau)
            b = reach_end(E, {**cl, o: 1}, floor2, rng, tau) if a[0] else (False, None, [])
            ok = a[0] and b[0]
            for r in (a, b):
                if r[1] is not None:
                    (mem["plus"] if r[0] else mem["fail_viol"]).append(r[1] if r[0] else r[2])
            bad += not ok
            continue
        y = int(y)
        a = reach_end(E, {**cl, o: y}, floor2, rng, tau)
        if not a[0]:
            mem["fail_viol"].append(a[2])
            bad += 1
            continue
        mem["plus"].append(a[1])
        wrong = {**cl, o: 1 - y}
        hit = False
        for k in range(P.NEG_WALKS):
            r = reach_end(E, wrong, floor2, rng, P.NEG_TAU, fresh=k > 0)
            if r[0]:
                mem["minus"].append(r[1])
                hit = True
                break
        bad += hit
    return bad


def violates(E, x, i, flip_k):
    """would knot i be violated in state x if the sign at its place flip_k were changed (None: unchanged signs)"""
    lit = [x[E.pt[i][k]] ^ E.s[3 * i + k] ^ (1 if k == flip_k else 0) for k in range(3)]
    return lit[0] == lit[1] == lit[2]


def learn(E, K, ports, target, floor2, rng, rule, stats, params=None, xor_law=None):
    """credit_lib.learn, step for step for rule B, with the steering hooks of P, M and A; stops at the first passing probe"""
    params = params or dict(C.PARAMS, budget=2_000_000)
    nb = C.neighbourhoods(E)
    use_credit = rule == "B" and any(y != "u" for y in target)
    r, att, fails, above = 0, I.near_lines(K, ports, 0), 0, 0
    cool = set()
    mem = {"plus": [], "minus": [], "fail_viol": []}
    tabu = []
    for t in range(params["budget"]):
        if t % params["probe_every"] == 0:
            if E.W == floor2:
                above = 0
                stats["probes"] += 1
                if xor_law is not None and stats.get("xor seen at probe") is None and xor_law(E.s):
                    stats["xor seen at probe"] = stats["probes"]
                if steer_probe(E, ports, target, floor2, rng, params["tau"], mem) == 0:
                    stats["steps"] = t
                    return True
                fails += 1
                if fails % params["widen"] == 0 and r < params["rmax"]:
                    r += 1
                    att = I.near_lines(K, ports, r)
                if use_credit and fails % params["pin_every"] == 0:
                    cool = C.cooled_lines(E, nb, rng, params["tau_pin"], att, set(ports))
                if rule == "M" and mem["fail_viol"]:
                    cands = [(i, k) for i in mem["fail_viol"][0] for k in range(3) if (i, k) not in tabu]
                    if cands:
                        best, bscore = [], None
                        for (i, k) in cands:
                            stats["candidate checks"] += 1
                            sc = sum(violates(E, xs, i, k) for xs in mem["plus"])
                            if bscore is None or sc < bscore:
                                best, bscore = [(i, k)], sc
                            elif sc == bscore:
                                best.append((i, k))
                        i, k = rng.choice(best)
                        d, nv, dag = E.delta([(i, k)])
                        E.s[3 * i + k] ^= 1
                        E.apply([(i, k)], d, nv, dag)
                        tabu = (tabu + [(i, k)])[-5:]
            else:
                above += 1
                if above % params["widen"] == 0 and r < params["rmax"]:
                    r += 1
                    att = I.near_lines(K, ports, r)
        if rng.random() < 0.5:
            p = rng.randrange(E.n)
            sites, mv = E.sites_of_point[p], ("flip", p)
            hot = any(i in att for (i, _) in sites)
        else:
            ls = [st for st in E.learn_sites() if st[0] in att and st[0] not in cool]
            if not ls:
                continue
            if rule == "P" and mem["fail_viol"]:
                heat = {}
                for v in mem["fail_viol"]:
                    for i in v:
                        heat[i] = heat.get(i, 0) + 1
                wts = [1 + heat.get(st[0], 0) for st in ls]
                st = rng.choices(ls, weights=wts)[0]
            else:
                st = rng.choice(ls)
            sites, mv, hot = [st], ("learn",) + st, True
        T = params["T_hot"] if hot else params["T_cold"]
        d, nv, dag = E.delta(sites)
        if E.W + d > floor2 + params["envelope"]:
            continue
        accept = d <= 0 or rng.random() < math.exp(-d / T)
        if rule == "A" and mv[0] == "learn" and (mem["plus"] or mem["minus"]):
            i, k = mv[1], mv[2]
            stats["candidate checks"] += 1
            plus_rise = any(violates(E, xs, i, k) and not violates(E, xs, i, None) for xs in mem["plus"])
            minus_rise = any(violates(E, xs, i, k) and not violates(E, xs, i, None) for xs in mem["minus"])
            if not plus_rise and minus_rise:
                accept = True
        if accept:
            if mv[0] == "flip":
                E.x[mv[1]] ^= 1
            else:
                E.s[3 * mv[1] + mv[2]] ^= 1
            E.apply(sites, d, nv, dag)
    stats["steps"] = None
    return False


def run(setting, rule, target, seed, xor_law=None):
    sp = J.Space(1)
    rng = random.Random(seed)
    s, x = sp.start()
    E = engine(setting, sp, s, x)
    W.m1(E, 0, rng)
    stats = {"probes": 0, "candidate checks": 0}
    found = learn(E, sp.K, sp.ports, target, 0, rng, rule, stats, xor_law=xor_law)
    m = F.read_map_k(sp.K, E.s, sp.ports)
    return {"setting": setting, "rule": rule, "target": target, "seed": seed, "found": found and m == target, "map at the stop": m,
            "world probes": stats["probes"], "candidate checks": stats["candidate checks"],
            "charged probes": stats["probes"] + stats["candidate checks"], "steps": stats["steps"],
            "xor seen at probe": stats.get("xor seen at probe")}
