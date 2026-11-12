"""SHORT-DESC-20261112-001A census: patterns weighted by short descriptions (dlang.py), their outcomes against baselines that use
less (uniform patterns with the same distinctions and knots; patterns with the same degrees), and the fates of nested families.
Run from the repository root:  census.py --run VARIANT WORKER TRIES   (one worker's share; output appended per pattern)
                                census.py --summary
"""
import hashlib, itertools, json, math, os, random, sys, time
from collections import Counter
import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "../../RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census"))
import dlang as L
import fates as F                                   # frozen RANDOM-FATES library: clauses, Reader (exact tie classes)

OUT = os.environ.get("SD_OUT") or os.path.join(HERE, "../../../artifacts/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census")
BASE_MIN_KNOTS = 7          # fewer knots always allow a state (the Fano plane is the smallest pattern with none)
BASE_MAX_N = 400            # baselines for patterns on at most this many distinctions
READ_MAX_N = 200            # tie shares and dead cores up to this many distinctions
READ_QUOTA = 1500           # tie readings per worker (the first eligible patterns, in order)
MIX_QUOTA = 300             # mixing check per worker: baselines again with chains twice as long


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def alive(K):
    with Solver(name="cadical153", bootstrap_with=[c for t in K for c in F.cls(t)]) as s:
        return s.solve()


def alive_by_ports(defs, t):
    if t is None:
        return bool(L.relations(defs, {})[-1].any())
    prev = {i: L.NAE for i, d in enumerate(defs) if any(cl == "SELF" for cl, _ in d[2])}
    for _ in range(t):
        rels = L.relations(defs, prev)
        prev = {i: rels[i] for i in prev}
    return bool(rels[-1].any())


def uniform_like(n, K, rng, per_knot=30):
    """Uniform over patterns of len(K) distinct knots using all n distinctions: a replace-one-knot chain from K (symmetric
    proposal; moves that would leave a distinction in no knot are refused)."""
    E, S = list(K), set(K)
    cnt = Counter(v for e in E for v in e)
    for _ in range(per_knot * len(E)):
        i = rng.randrange(len(E))
        new = tuple(sorted(rng.sample(range(n), 3)))
        if new in S:
            continue
        old = E[i]
        if any(cnt[v] == 1 and v not in new for v in old):
            continue
        for v in old:
            cnt[v] -= 1
        for v in new:
            cnt[v] += 1
        S.discard(old); S.add(new); E[i] = new
    return sorted(E)


def degree_like(K, rng, per_knot=20):
    """Same degrees: the switch chain of AGE-NEST-20261112-001 (swap one distinction between two knots)."""
    E, S = [tuple(sorted(t)) for t in K], set(K)
    for _ in range(per_knot * len(E)):
        i, j = rng.randrange(len(E)), rng.randrange(len(E))
        if i == j:
            continue
        a, b = E[i], E[j]
        u, v = rng.choice(a), rng.choice(b)
        if u in b or v in a:
            continue
        na = tuple(sorted([x for x in a if x != u] + [v]))
        nb = tuple(sorted([x for x in b if x != v] + [u]))
        if na in S or nb in S:
            continue
        S.discard(a); S.discard(b); S.add(na); S.add(nb)
        E[i], E[j] = na, nb
    return sorted(E)


def dead_core(K):
    """A minimal set of knots allowing no state (unsat core, then deletion): (knots, distinctions)."""
    m = len(K)
    sel = list(range(10 ** 6, 10 ** 6 + m))
    with Solver(name="cadical153") as s:
        for i, t in enumerate(K):
            for c in F.cls(t):
                s.add_clause(c + [-sel[i]])
        assert not s.solve(assumptions=sel)
        core = [x - sel[0] for x in s.get_core()]
        j = 0
        while j < len(core):
            trial = core[:j] + core[j + 1:]
            if s.solve(assumptions=[sel[i] for i in trial]):
                j += 1
            else:
                core = trial
    return len(core), len({v for i in core for v in K[i]})


def tie_share(n, K):
    R = F.Reader(n, K, samples=200, seed=0)
    try:
        cl = R.tie_classes()
    finally:
        R.close()
    return sum(len(c) * (len(c) - 1) // 2 for c in cl) / (n * (n - 1) / 2), max((len(c) for c in cl), default=1)


def run(variant, worker, tries):
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(seed_of("SD", variant, worker))
    cfg = L.VARIANTS[variant]
    rej, reads, mixes = Counter(), 0, 0
    f = open(os.path.join(OUT, f"runs_{variant}_{worker}.jsonl"), "w")
    t0 = time.time()
    for k in range(tries):
        d = L.sample(rng, **cfg)
        if "defs" in d and d.get("t") is not None:                  # a nested family (depth aside)
            fam = L.fate(d["defs"])
            f.write(json.dumps(dict(kind="family", try_=k, bits=d["bits"] - d["tbits"], ndefs=len(d["defs"]), **fam)) + "\n")
        if "reject" in d:
            rej[d["reject"]] += 1
            continue
        e = L.expand(d["defs"], d["t"])
        if e is None:
            rej["knotcap"] += 1
            continue
        n, K = e
        rec = dict(kind="pattern", try_=k, bits=d["bits"], t=d["t"], ndefs=len(d["defs"]), n=n, m=len(K),
                   maxdeg=max(Counter(v for t in K for v in t).values()))
        rec["alive"] = alive(K) if len(K) >= BASE_MIN_KNOTS else True
        rec["alive_ports"] = alive_by_ports(d["defs"], d["t"])
        if len(K) >= BASE_MIN_KNOTS and n <= BASE_MAX_N:
            brng = random.Random(seed_of("SDb", variant, worker, k))
            U = uniform_like(n, K, brng); D = degree_like(K, brng)
            rec["u_alive"], rec["d_alive"] = alive(U), alive(D)
            if mixes < MIX_QUOTA:
                mixes += 1
                rec["u60_alive"] = alive(uniform_like(n, K, brng, per_knot=60))
                rec["d40_alive"] = alive(degree_like(K, brng, per_knot=40))
            if n <= READ_MAX_N:
                if not rec["alive"]:
                    rec["core"] = dead_core(K)
                if not rec["u_alive"]:
                    rec["u_core"] = dead_core(U)
                if rec["alive"] and reads < READ_QUOTA:
                    reads += 1
                    rec["ties"] = tie_share(n, K)
                    for tag, gen in (("u", lambda: uniform_like(n, K, brng)), ("d", lambda: degree_like(K, brng))):
                        B = U if (tag == "u" and rec["u_alive"]) else (D if (tag == "d" and rec["d_alive"]) else None)
                        for _ in range(5):
                            if B is not None:
                                break
                            B = gen()
                            B = B if alive(B) else None
                        rec[tag + "_ties"] = tie_share(n, B) if B is not None else None
        f.write(json.dumps(rec) + "\n")
        if k % 2000 == 0:
            f.flush()
    f.write(json.dumps(dict(kind="counts", tries=tries, rejections=dict(rej), seconds=round(time.time() - t0))) + "\n")
    f.close()


def load(variant):
    pats, fams, counts = [], [], []
    for name in sorted(os.listdir(OUT)):
        if name.startswith(f"runs_{variant}_"):
            for line in open(os.path.join(OUT, name)):
                r = json.loads(line)
                (pats if r["kind"] == "pattern" else fams if r["kind"] == "family" else counts).append(r)
    return pats, fams, counts


def boot(x, reps=2000, seed=7):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    b = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(reps)]
    return [round(float(x.mean()), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]


def summarize(variant):
    pats, fams, counts = load(variant)
    S = dict(variant=variant, patterns=len(pats), families=len(fams))
    tries = sum(c["tries"] for c in counts)
    rej = Counter()
    for c in counts:
        rej.update(c["rejections"])
    S["tries"], S["rejections"] = tries, {k: round(v / tries, 4) for k, v in rej.items()} if tries else {}
    S["mismatch_ports_vs_solver"] = sum(p["alive"] != p["alive_ports"] for p in pats)
    m = np.array([p["m"] for p in pats]); n = np.array([p["n"] for p in pats]); dead = np.array([not p["alive"] for p in pats])
    S["knots_pct_10_50_90"] = np.percentile(m, [10, 50, 90]).tolist()
    S["dead_share"] = round(float(dead.mean()), 4)
    S["share_under_7_knots"] = round(float((m < 7).mean()), 4)
    S["dead_share_7plus"] = round(float(dead[m >= 7].mean()), 4)
    big = [p for p in pats if p["m"] >= 100]
    S["nested_share_100plus"] = round(sum(p["t"] is not None for p in big) / len(big), 4) if big else None
    B = [p for p in pats if "u_alive" in p]
    S["paired"] = len(B)
    S["S1_dead_minus_uniform"] = boot([(not p["alive"]) - (not p["u_alive"]) for p in B])
    S["S2_dead_minus_degree"] = boot([(not p["alive"]) - (not p["d_alive"]) for p in B])
    S["S5_nested_dead_minus_uniform"] = boot([(not p["alive"]) - (not p["u_alive"]) for p in B if p["t"] is not None])
    S["nested_paired"] = sum(p["t"] is not None for p in B)
    M = [p for p in B if "u60_alive" in p]
    S["mixing_dead_u30_u60_d20_d40"] = [round(float(np.mean([not p[k] for p in M])), 4) for k in ("u_alive", "u60_alive", "d_alive", "d40_alive")] if M else None
    S["mixing_checked"] = len(M)
    S["dead_desc_uniform_degree"] = [round(float(np.mean([not p[k] for p in B])), 4) for k in ("alive", "u_alive", "d_alive")]
    bins = [(7, 13), (13, 25), (25, 50), (50, 100), (100, 3001)]
    S["by_knots"] = {f"{a}-{b - 1}": dict(count=len(sel), dead=[round(float(np.mean([not p[k] for p in sel])), 4)
                                                                for k in ("alive", "u_alive", "d_alive")] if sel else None,
                                          minus_uniform=boot([(not p["alive"]) - (not p["u_alive"]) for p in sel]) if sel else None,
                                          minus_degree=boot([(not p["alive"]) - (not p["d_alive"]) for p in sel]) if sel else None)
                     for a, b in bins for sel in [[p for p in B if a <= p["m"] < b]]}
    C = [p for p in B if "core" in p]; CU = [p for p in B if "u_core" in p]
    S["core_distinctions_median"] = [float(np.median([p["core"][1] for p in C])) if C else None,
                                     float(np.median([p["u_core"][1] for p in CU])) if CU else None]
    T = [p for p in B if "ties" in p and p.get("u_ties") is not None]
    S["S3_ties_read"] = len(T)
    S["S3_tie_share_minus_uniform"] = boot([p["ties"][0] - p["u_ties"][0] for p in T]) if T else None
    TD = [p for p in B if "ties" in p and p.get("d_ties") is not None]
    S["tie_share_minus_degree"] = boot([p["ties"][0] - p["d_ties"][0] for p in TD]) if TD else None
    S["any_tie_desc_uniform"] = [round(float(np.mean([p["ties"][1] > 1 for p in T])), 4),
                                 round(float(np.mean([p["u_ties"][1] > 1 for p in T])), 4)] if T else None
    if fams:
        fc = Counter(x["fate"] for x in fams)
        S["S4_fates"] = {k: round(v / len(fams), 4) for k, v in fc.items()}
        S["first_dead_depths"] = dict(Counter(x["first_dead"] for x in fams if x["fate"] == "a while"))
        S["revives"] = sum(x["revives"] for x in fams)
        S["periods"] = dict(Counter(x["period"] for x in fams))
        S["limit_alive"] = round(float(np.mean([x["limit_alive"] for x in fams])), 4)
        kinds = Counter(k for x in fams for k in x["limit_kinds"])
        S["limit_kinds"] = {k: round(v / sum(kinds.values()), 4) for k, v in kinds.items()}
        S["after_first_death"] = dict(Counter(x["after"] for x in fams if x["after"]))
        S["fate_vs_limit"] = {f"{a}|{b}": v for (a, b), v in Counter((x["fate"], x["limit_alive"]) for x in fams).items()}
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--run":
        run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif sys.argv[1] == "--summary":
        out = {v: summarize(v) for v in L.VARIANTS if any(x.startswith(f"runs_{v}_") for x in os.listdir(OUT))}
        json.dump(out, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(out, indent=1))
