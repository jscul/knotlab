"""BOND-DEPTH-20261112-001A: least bonds along one ray of copies, exactly, in one-definition nested families.

Family: a three-port self-holding definition D (main), read in its usual limit (LIMIT-STATE's usual(): the knot on its ports added
when it passes its own ports to SELF). The ray: C_0 = main, C_j = the copy made by D's first SELF call inside C_{j-1}. Block j is C_j:
its 3 ports, its own distinctions (locals), its K calls, and its other SELF calls (side branches) as the limit relation G on their
arguments; the last block's ray call is G too. Consecutive blocks share the ray call's 3 arguments (the interface).
A bond W must lie in the ray's own distinctions (the ray restriction; L_ray >= the true least bond). W contains a port of C_0 and
an own distinction of C_s. Exact by a DP over blocks with state (F, G): F the family of reachable interface-state sets (8-bit
masks) over all assignments of W so far, G the same with one member of W already forgotten; constrained iff some assignment
reaches nothing; minimal iff none of the one-forgotten ones does. Cost |W|, minimised by levels. Blocks 1..s-1 are the same map, so
L(s) is eventually linear plus periodic: detected exactly by a repeat of the normalised cost vector over (F, G) states.
Run from the repository root:  census.py --validate  |  census.py --run WORKER WORKERS  |  census.py --summary
"""
import glob, importlib.util, itertools, json, os, random, sys, time
from collections import deque
import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("ls", os.path.join(HERE, "../../LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py"))
LS = importlib.util.module_from_spec(_s); _s.loader.exec_module(LS)
L = LS.L
OUT = os.environ.get("BD_OUT") or os.path.join(HERE, "../../../artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds")
SMAX, STATE_CAP = 30, 20000
INF = 10 ** 9


def block_relation(defs, G, last):
    """Allowed assignments of the block's env (ports 0..2, locals 3..), as a boolean array over 2^V; the ray call's args."""
    k, l, calls = defs[0]
    V = k + l
    A = (np.arange(2 ** V)[:, None] >> np.arange(V)) & 1
    ok = np.ones(2 ** V, bool)
    ray = None
    for callee, args in calls:
        idx = (A[:, list(args)] << np.arange(3)).sum(1)
        if callee == "K":
            ok &= L.NAE[idx]
        elif callee == "SELF":
            if ray is None:
                ray = tuple(args)
                if last:
                    ok &= G[0][idx]
            else:
                ok &= G[0][idx]
    return ok, ray, V


def tables(defs, G, last):
    """For each W subset of the created distinctions (bit mask over env), each assignment alpha of W: T[sigma] = mask of tau."""
    ok, ray, V = block_relation(defs, G, last)
    k = 3
    asg = np.arange(2 ** V)
    port = asg & 7
    out = np.zeros(2 ** V, dtype=np.int64)
    if not last:
        out = sum((((asg >> ray[b]) & 1) << b) for b in range(3))
    return ok, ray, V, port, out


def run_family(defs, smax=SMAX):
    """L(s) for s = 1..smax (INF where no ray bond exists), with the eventual (rate, period) when detected."""
    _, _, Gd = L.depth_sequence(defs, L.TOP)
    G = [Gd[0]]
    okM, rayM, V, port, out = tables(defs, G, last=False)
    okE, _, _, portE, _ = tables(defs, G, last=True)
    k, l = 3, V - 3
    loc = list(range(3, V))

    def trans(ok, W, alpha_bits, last, forget=None):
        """sigma -> tau mask (or sigma -> nonempty for the last block), for W (list) with values alpha_bits; forget: index in W."""
        sel = ok.copy()
        a = np.arange(2 ** V)
        for i, w in enumerate(W):
            if forget is not None and i == forget:
                continue
            sel &= ((a >> w) & 1) == ((alpha_bits >> i) & 1)
        T = [0] * 8
        for sg in range(8):
            m = sel & (port == sg)
            if last:
                T[sg] = 1 if m.any() else 0
            else:
                T[sg] = int(np.bitwise_or.reduce(1 << out[m])) if m.any() else 0
        return T

    def step(R, T):
        r = 0
        for sg in range(8):
            if (R >> sg) & 1:
                r |= T[sg]
        return r

    # first block (main): W0 contains at least one port; created = ports + locals; incoming: none (all port states free)
    subsets_mid = [list(c) for n in range(0, l + 1) for c in itertools.combinations(loc, n)]
    subsets_first = [list(c) for n in range(1, V + 1) for c in itertools.combinations(range(V), n) if any(x < 3 for x in c)]
    subsets_last = [list(c) for n in range(1, l + 1) for c in itertools.combinations(loc, n)]
    cacheM, cacheE = {}, {}

    def tabs(W, last):
        key = tuple(W)
        cache = cacheE if last else cacheM
        if key not in cache:
            ok = okE if last else okM
            full = [trans(ok, W, a, last) for a in range(2 ** len(W))]
            forg = [[trans(ok, W, a, last, forget=i) for a in range(2 ** len(W))] for i in range(len(W))]
            cache[key] = (full, forg)
        return cache[key]

    def advance(F, Gf, W, last):
        full, forg = tabs(W, last)
        nF = frozenset(step(R, T) for R in F for T in full)
        nG = set(step(R, T) for R in Gf for T in full)
        for i in range(len(W)):
            for R in F:
                for T in forg[i]:
                    nG.add(step(R, T))
        return nF, frozenset(nG)

    START = (frozenset([255]), frozenset())        # before block 0: every port state possible; nothing forgotten
    # level 0
    layer = {}
    for W in subsets_first:
        st = advance(*START, W, last=False)
        if st not in layer or layer[st] > len(W):
            layer[st] = len(W)
    Ls, seen, rate = [], {}, None
    for s in range(1, smax + 1):
        # close with the last block
        best = INF
        for st, c in layer.items():
            for W in subsets_last:
                F, Gf = advance(*st, W, last=True)
                if 0 in F and 0 not in Gf and c + len(W) < best:
                    best = c + len(W)
        Ls.append(best)
        if s == smax or len(layer) > STATE_CAP:
            break
        key = None
        if layer:
            mn = min(layer.values())
            key = frozenset((st, c - mn) for st, c in layer.items())
            if key in seen:
                s0, mn0 = seen[key]
                rate = dict(period=s - s0, gain=mn - mn0, from_s=s0)
            else:
                seen[key] = (s, mn)
        if rate:
            break
        nl = {}
        for st, c in layer.items():
            for W in subsets_mid:
                ns = advance(*st, W, last=False)
                if nl.get(ns, INF) > c + len(W):
                    nl[ns] = c + len(W)
        layer = nl
    return dict(L=Ls, rate=rate, states=len(layer))


def ray_cnf(defs, s):
    """CNF of blocks C_0..C_s on the ray (side SELF calls and the last ray call as G); returns clauses, n, top ports, last locals."""
    _, _, Gd = L.depth_sequence(defs, L.TOP)
    G = Gd[0]
    k, l, calls = defs[0]
    cl, nv = [], [3]
    ports = [0, 1, 2]
    top = list(ports)
    created = []
    for j in range(s + 1):
        env = ports + list(range(nv[0], nv[0] + l)); nv[0] += l
        created.append(([0, 1, 2] if j == 0 else []) + env[3:])
        ray = None
        for callee, args in calls:
            a = [env[x] for x in args]
            if callee == "K":
                cl += [[x + 1 for x in a], [-(x + 1) for x in a]]
            elif ray is None and callee == "SELF":
                ray = a
                if j == s:
                    cl += LS.relation_clauses(a, G)
            else:
                cl += LS.relation_clauses(a, G)
        ports = ray
    return cl, nv[0], top, created


def brute(defs, s, maxsize=7):
    cl, n, top, created = ray_cnf(defs, s)
    pool = sorted(set(x for c in created for x in c))
    last = [x for x in created[-1] if x not in created[0]] if s > 0 else created[-1]
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        if not S.solve():
            return "dead"
        def free(W):
            return all(S.solve(assumptions=[(w + 1) if (a >> i) & 1 else -(w + 1) for i, w in enumerate(W)]) for a in range(2 ** len(W)))
        for size in range(2, maxsize + 1):
            for W in itertools.combinations(pool, size):
                if not any(w in top for w in W) or not any(w in last for w in W):
                    continue
                if free(W):
                    continue
                if all(free([x for x in W if x != y]) for y in W):
                    return size
    return None


def families_one_def():
    fams = LS.families()
    out = []
    for idx, d in enumerate(fams):
        if len(d) != 1:
            continue
        ud, _ = LS.usual(d)
        _, _, G = L.depth_sequence(ud, L.TOP)
        if L.relations(ud, G)[-1].any():
            out.append((idx, ud))
    return out


def validate():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(7)
    fams = families_one_def()
    res = dict(cases=0, agree=0, disagree=[], skipped=0)
    for idx, d in rng.sample(fams, 40):
        r = run_family(d, smax=3)
        for s in (1, 2, 3):
            if s > len(r["L"]):
                continue
            b = brute(d, s)
            dp = r["L"][s - 1]
            if b is None and dp > 7:
                res["skipped"] += 1
                continue
            res["cases"] += 1
            if (b if b is not None else INF) == dp or (b is None and dp > 7):
                res["agree"] += 1
            else:
                res["disagree"].append(dict(idx=idx, s=s, brute=b, dp=dp))
    # chains with no cycle of knots: D(a, b, c) = K(a, b, x), SELF(x, y, z) with fresh x, y, z: least bond = steps apart + 2
    chains = [[(3, 3, [("K", (0, 1, 3)), ("SELF", (3, 4, 5))])], [(3, 2, [("K", (0, 3, 4)), ("SELF", (4, 1, 3))])]]
    res["chains"] = [run_family(LS.usual(c)[0], smax=6)["L"] for c in chains]
    json.dump(res, open(os.path.join(OUT, "validation.json"), "w"), indent=1)
    print(json.dumps(res))


def run(worker, workers):
    os.makedirs(OUT, exist_ok=True)
    f = open(os.path.join(OUT, f"runs_{worker}.jsonl"), "w")
    for j, (idx, d) in enumerate(families_one_def()):
        if j % workers != worker:
            continue
        t0 = time.time()
        r = run_family(d)
        f.write(json.dumps(dict(idx=idx, l=d[0][1], seconds=round(time.time() - t0, 1), **r)) + "\n")
        f.flush()
    f.close()


def extrapolate(r, upto=60):
    """L(s) to s = upto from the detected repeat (exact), else None beyond what was computed."""
    Ls = list(r["L"])
    if not r["rate"]:
        return Ls
    p, g, s0 = r["rate"]["period"], r["rate"]["gain"], r["rate"]["from_s"]
    while len(Ls) < upto:
        s = len(Ls) + 1
        Ls.append(Ls[s - 1 - p] + g if Ls[s - 1 - p] < INF else INF)
    return Ls


def summarize():
    from collections import Counter
    rows = [json.loads(x) for n in sorted(glob.glob(os.path.join(OUT, "runs_*.jsonl"))) for x in open(n)]
    S = dict(families=len(rows))
    cls = Counter()
    for r in rows:
        if all(x >= INF for x in r["L"]):
            c = "no ray bond"
        elif r["rate"] is None:
            c = "undetermined within 30"
        elif r["rate"]["gain"] == 0:
            c = "bounded"
        else:
            c = "growing"
        r["cls"] = c
        cls[c] += 1
    S["classes"] = dict(cls)
    gr = [r for r in rows if r["cls"] == "growing"]
    S["growth_rates"] = dict(Counter(f'{r["rate"]["gain"]}/{r["rate"]["period"]}' for r in gr))
    bd = [r for r in rows if r["cls"] == "bounded"]
    S["bounded_limits"] = dict(Counter(min(x for x in r["L"] if x < INF) if any(x < INF for x in r["L"]) else None for r in bd))
    S["P1_bounded_share"] = round(cls["bounded"] / len(rows), 4) if rows else None
    S["transient_from_s"] = dict(Counter(r["rate"]["from_s"] for r in rows if r["rate"]))
    S["states_max"] = max(r["states"] for r in rows) if rows else None
    S["capped"] = sum(r["states"] > STATE_CAP for r in rows)
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--validate":
        validate()
    elif sys.argv[1] == "--run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))
