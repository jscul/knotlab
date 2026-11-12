"""NEST-READ-20261112-001A census: what the law reads along the levels of self-nested patterns.

Nested families are sampled by the code of SHORT-DESC-20261112-001's language (dlang.py, fair coins), in two variants:
  knot   - SELF only in definitions with three ports: an inner pattern shares distinctions with the outside only through the
           knot that holds it (SHORT-DESC's main variant);
  direct - SELF only in definitions with four to six ports: the holding knot is the call's first three arguments (at depth 1
           SELF is that knot) and the inner pattern also shares the other arguments with the outside directly.
A distinction's level is the number of SELF substitutions above the call that made it (top: level 0). Each family is read at the
largest depth t <= 12 with at most 60 distinctions, kept when that pattern allows a state, has at least 8 distinctions, one of them at level 0, and distinctions at level 4 or more.
Strata: 'constraining' when some SELF definition, with SELF read as its holding knot, allows on its ports less than that knot
(not a superset of it); 'monotone' otherwise, where by monotonicity every depth allows on the outer distinctions at least what
depth 1 does (SHORT-DESC-R1's check). Quotas per worker: CONSTRAINING and MONOTONE families.
For one level-0 distinction u and up to two distinctions v per level s >= 1: steps apart d and the least bond containing u and v,
exact up to five members (sizes 2 to 5 over all distinctions, by the frozen RANDOM-FATES reader), else 'none within five'.
Baseline (less information, same sizes without nesting): a uniform pattern with the same distinctions and knots (SHORT-DESC's
replace-one-knot chain), alive, read for one pair at each nested pair's steps apart.
Run from the repository root:  census.py --run VARIANT WORKER FAMILIES   |   census.py --summary
"""
import hashlib, json, math, os, random, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SD = os.path.join(HERE, "../../SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census")
RF = os.path.join(HERE, "../../RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census")
sys.path.insert(0, SD); sys.path.insert(0, RF)
import dlang as L                                   # SHORT-DESC's code: gamma, caps
import fates as F                                   # frozen reader, steps
import importlib.util
_spec = importlib.util.spec_from_file_location("sd_census", os.path.join(SD, "census.py"))
SDC = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SDC)   # alive, uniform_like

OUT = os.environ.get("NR_OUT") or os.path.join(HERE, "../../../artifacts/NEST-READ-20261112-001A/NEST-READ-20261112-001A-E001_levels")
N_MIN, N_MAX, T_MAX, LEVEL_MIN, PAIRS_PER_LEVEL, BOND_MAX, CALL_CAP = 8, 60, 12, 4, 2, 5, 20000


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def sample_family(rng, variant):
    """dlang's code without the depth; SELF allowed only where the variant allows it. Returns defs or a rejection cause."""
    r, _ = L.gamma(rng)
    if r > L.DEF_CAP:
        return "defs"
    defs = []
    for i in range(r):
        km2, _ = L.gamma(rng)
        if km2 + 2 > 6:
            return "arity"
        k = km2 + 2
        l1, _ = L.gamma(rng)
        if l1 - 1 > L.LOCAL_CAP:
            return "locals"
        l = l1 - 1
        c, _ = L.gamma(rng)
        if c > L.CALL_CAP:
            return "calls"
        V = k + l
        self_here = (k == 3) if variant == "knot" else (k >= 4)
        options = ["K"] + list(range(i)) + (["SELF"] if self_here else [])
        calls = []
        for _ in range(c):
            callee = options[rng.randrange(len(options))]
            ar = 3 if callee == "K" else (k if callee == "SELF" else defs[callee][0])
            if ar > V:
                return "args"
            calls.append((callee, tuple(rng.sample(range(V), ar))))
        defs.append((k, l, calls))
    if not any(cl == "SELF" for d in defs for cl, _ in d[2]):
        return "not nested"
    return defs


def expand_levels(defs, t, knot_cap=4000):
    knots, level, nv, ncalls = set(), {}, [0], [0]

    def call(i, actual, depth, lev):
        ncalls[0] += 1
        if ncalls[0] > CALL_CAP:
            raise OverflowError
        k, l, calls = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        for j in range(nv[0], nv[0] + l):
            level[j] = lev
        nv[0] += l
        for callee, args in calls:
            a = [env[x] for x in args]
            if callee == "K" or (callee == "SELF" and depth <= 1):
                knots.add(tuple(sorted(a[:3])))
                if len(knots) > knot_cap:
                    raise OverflowError
            elif callee == "SELF":
                call(i, a, depth - 1, lev + 1)
            else:
                call(callee, a, depth, lev)

    k = defs[-1][0]
    for j in range(k):
        level[j] = 0
    nv[0] = k
    try:
        call(len(defs) - 1, list(range(k)), t, 0)
    except (OverflowError, RecursionError):
        return None
    used = sorted({v for e in knots for v in e})
    idx = {v: j for j, v in enumerate(used)}
    return len(used), sorted(tuple(sorted(idx[v] for v in e)) for e in knots), [level[v] for v in used]


def base_rel(k):
    """The holding knot on a definition's first three ports, as a relation on all k ports."""
    return np.array([s & 7 not in (0, 7) for s in range(2 ** k)])


def constraining(defs):
    """(constraining, tied): some SELF definition, SELF read as its holding knot, allows on its ports less than that knot; and
    some SELF definition ties two of its first three ports (its states there fall in at most two complementary pairs)."""
    selfs = [i for i, d in enumerate(defs) if any(cl == "SELF" for cl, _ in d[2])]
    rels = L.relations(defs, {i: base_rel(defs[i][0]) for i in selfs})
    con = any(np.any(base_rel(defs[i][0]) & ~rels[i]) for i in selfs)
    tied = any(0 < len({s & 7 for s in np.flatnonzero(rels[i])}) <= 4 for i in selfs)
    return con, tied


def berge_acyclic(n, K):
    """No cycle of knots: the incidence graph (distinctions and knots) is a forest."""
    parent = list(range(n + len(K)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, t in enumerate(K):
        for v in t:
            a, b = find(v), find(n + i)
            if a == b:
                return False
            parent[a] = b
    return True


def bond(R, u, v):
    size, _ = R.least_bond_with(u, v, exhaustive4=True, lens=[w for w in range(R.n) if w in R.used], lens_max=BOND_MAX)
    return size


def run(variant, worker, quota_c, quota_m):
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(seed_of("NR", variant, worker))
    f = open(os.path.join(OUT, f"runs_{variant}_{worker}.jsonl"), "w")
    rej, tries, t0 = Counter(), 0, time.time()
    kept = {"constraining": 0, "monotone": 0}
    quota = {"constraining": quota_c, "monotone": quota_m}
    while kept["constraining"] < quota_c or kept["monotone"] < quota_m:
        tries += 1
        defs = sample_family(rng, variant)
        if isinstance(defs, str):
            rej[defs] += 1
            continue
        con, tied = constraining(defs)
        stratum = "constraining" if con else "monotone"
        if kept[stratum] >= quota[stratum]:
            continue
        rej["tried " + stratum] += 1
        best = None
        for t in range(1, T_MAX + 1):
            e = expand_levels(defs, t)
            if e is None or e[0] > N_MAX:
                break
            best = (t, e)
        if best is None:
            rej["size"] += 1
            rej[stratum + " " + 'size'] += 1
            continue
        t, (n, K, lev) = best
        if max(lev) < LEVEL_MIN:
            rej["levels"] += 1
            rej[stratum + " " + 'levels'] += 1
            continue
        if n < N_MIN or min(lev) > 0:                   # too small, or no top distinction in a knot
            rej["degenerate"] += 1
            rej[stratum + " " + 'degenerate'] += 1
            continue
        if not SDC.alive(K):
            rej["dead"] += 1
            rej[stratum + " " + 'dead'] += 1
            continue
        kept[stratum] += 1
        prng = random.Random(seed_of("NRp", variant, worker, tries))
        top = [v for v in range(n) if lev[v] == 0]
        u = prng.choice(top)
        nbr = F.adjacency(n, K)
        dist = F.steps_from(nbr, u)
        R = F.Reader(n, K, samples=200, seed=0)
        pairs = []
        for s in range(1, max(lev) + 1):
            vs = [v for v in range(n) if lev[v] == s]
            for v in prng.sample(vs, min(PAIRS_PER_LEVEL, len(vs))):
                pairs.append(dict(s=s, d=dist.get(v), L=bond(R, u, v)))
        R.close()
        U = None
        for _ in range(5):
            B = SDC.uniform_like(n, K, prng)
            if SDC.alive(B):
                U = B
                break
        base = []
        if U is not None:
            RU = F.Reader(n, U, samples=200, seed=0)
            nbrU = F.adjacency(n, U)
            for p in pairs:
                cands = []
                for _ in range(40):
                    a = prng.randrange(n)
                    da = F.steps_from(nbrU, a)
                    cands = [b for b, x in da.items() if x == p["d"] and b != a]
                    if cands:
                        break
                if p["d"] is None or not cands:
                    base.append(dict(d=p["d"], L=None, found=False))
                    continue
                b = prng.choice(cands)
                base.append(dict(d=p["d"], L=bond(RU, a, b), found=True))
            RU.close()
        f.write(json.dumps(dict(kind="family", stratum=stratum, tied=tied, tries=tries, t=t, n=n, m=len(K), levels=max(lev), ndefs=len(defs),
                                acyclic=berge_acyclic(n, K), level_sizes=dict(Counter(lev)), pairs=pairs, base=base,
                                base_alive=U is not None)) + "\n")
        f.flush()
    f.write(json.dumps(dict(kind="counts", tries=tries, kept=kept, rejections=dict(rej), seconds=round(time.time() - t0))) + "\n")
    f.close()


def load(variant):
    fams, counts = [], []
    for name in sorted(os.listdir(OUT)):
        if name.startswith(f"runs_{variant}_") and name.endswith(".jsonl"):
            for line in open(os.path.join(OUT, name)):
                r = json.loads(line)
                (fams if r["kind"] == "family" else counts).append(r)
    return fams, counts


def share(xs):
    return round(float(np.mean(xs)), 4) if len(xs) else None


def boot_diff(a, b, reps=2000, seed=7):
    """Bootstrap over families of mean(a) - mean(b), a and b lists of per-family lists."""
    rng = np.random.default_rng(seed)
    a = [x for x in a]; b = [x for x in b]
    def m(fs):
        flat = [y for x in fs for y in x]
        return np.mean(flat) if flat else np.nan
    point = m(a) - m(b)
    idx = range(len(a))
    vals = []
    for _ in range(reps):
        ia = rng.integers(0, len(a), len(a)); ib = rng.integers(0, len(b), len(b))
        vals.append(m([a[i] for i in ia]) - m([b[i] for i in ib]))
    return [round(float(point), 4), round(float(np.nanpercentile(vals, 2.5)), 4), round(float(np.nanpercentile(vals, 97.5)), 4)]


def fam_lists(fams, pred):
    """Per family, the list of 'bonded within five' over its pairs that satisfy pred(pair)."""
    return [[p["L"] is not None for p in x["pairs"] if pred(p)] for x in fams]


def reach(p):
    return p["d"] is not None


def tf_short(p):
    """A tie-free bond shorter than the steps allow: 3 <= L <= 5 and L < d + 2."""
    return p["L"] is not None and 3 <= p["L"] < p["d"] + 2


def tf_bonded(p):
    return p["L"] is not None and p["L"] >= 3


def fam_lists_v(fams, pred, value):
    return [[value(p) for p in x["pairs"] if pred(p)] for x in fams]


def slope_ci(fams, excess=False, reps=2000, seed=7):
    """Mean over families of the least-squares slope, over level, of 'tie-free bond within five' (reachable pairs; families with
    pairs at three or more levels), with a bootstrap interval over families and the frozen band: die (interval below 0), grow
    (above 0), hold (otherwise). With excess, the value is the nested pair's minus its uniform pair's at the same steps apart,
    which removes what distance alone does."""
    sl = []
    for x in fams:
        if excess:
            ps = [(p, b) for p, b in zip(x["pairs"], x["base"]) if reach(p) and b.get("found")]
        else:
            ps = [(p, None) for p in x["pairs"] if reach(p)]
        if len({p["s"] for p, _ in ps}) < 3:
            continue
        s = np.array([p["s"] for p, _ in ps], float)
        y = np.array([tf_bonded(p) - (tf_bonded(b) if excess else 0) for p, b in ps], float)
        sl.append(float(np.polyfit(s, y, 1)[0]))
    if not sl:
        return None
    rng = np.random.default_rng(seed)
    sl = np.array(sl)
    b = [sl[rng.integers(0, len(sl), len(sl))].mean() for _ in range(reps)]
    lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
    return dict(mean=round(float(sl.mean()), 4), ci=[round(lo, 4), round(hi, 4)], families=len(sl),
                band="die" if hi < 0 else ("grow" if lo > 0 else "hold"))


def flat_share(lists):
    flat = [y for z in lists for y in z]
    return [share(flat), len(flat)]


def summarize(fams, counts):
    S = dict(families=len(fams))
    tries = sum(c["tries"] for c in counts)
    rej = Counter()
    for c in counts:
        rej.update(c["rejections"])
    S["tries"], S["rejections"] = tries, dict(rej)
    S["acyclic_families"] = sum(x["acyclic"] for x in fams)
    P = [(x, p) for x in fams for p in x["pairs"]]
    S["pairs"] = len(P)
    ok = lambda p: p["L"] is not None
    ac = [p for x, p in P if x["acyclic"] and p["d"] is not None]
    S["P1_acyclic_pairs"] = len(ac)
    S["P1_violations"] = sum((p["L"] != p["d"] + 2) if p["d"] + 2 <= BOND_MAX else ok(p) for p in ac)
    S["near_d_le3"] = flat_share(fam_lists(fams, lambda p: p["d"] is not None and p["d"] <= 3))
    S["far_d_ge4"] = flat_share(fam_lists(fams, lambda p: p["d"] is None or p["d"] >= 4))
    S["level1"] = flat_share(fam_lists(fams, lambda p: p["s"] == 1))
    S["level4plus"] = flat_share(fam_lists(fams, lambda p: p["s"] >= 4))
    by_d = {}
    for dd in (1, 2, 3, 4, 5, 6):
        a = [ok(p) for x, p in P if p["d"] == dd]
        b = [ok(bb) for x in fams for p, bb in zip(x["pairs"], x["base"]) if p["d"] == dd and bb["found"]]
        by_d[dd] = dict(nested=share(a), n=len(a), uniform=share(b), nu=len(b))
    S["bonded_by_d"] = by_d
    by_s = {}
    for s in range(1, 13):
        ps = [p for x, p in P if p["s"] == s]
        if not ps:
            continue
        ds = [p["d"] for p in ps if p["d"] is not None]
        by_s[s] = dict(n=len(ps), bonded=share([ok(p) for p in ps]), median_d=float(np.median(ds)) if ds else None,
                       unreachable=share([p["d"] is None for p in ps]),
                       ruler=share([ok(p) and p["d"] is not None and p["L"] == p["d"] + 2 for p in ps]),
                       shortcut=share([ok(p) and p["d"] is not None and p["L"] < p["d"] + 2 for p in ps]),
                       tie=share([p["L"] == 2 for p in ps]), Ls=dict(Counter(p["L"] for p in ps if ok(p))))
    S["by_level"] = by_s
    S["tied_families"] = sum(x["tied"] for x in fams)
    S["unreachable_pairs"] = sum(p["d"] is None for x, p in P)
    S["tie_share"] = share([p["L"] == 2 for x, p in P])
    S["tie_free_shortcut"] = flat_share(fam_lists_v(fams, reach, tf_short))
    S["raw_slope"] = slope_ci(fams)
    S["excess_slope"] = slope_ci(fams, excess=True)
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--run":
        run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    elif sys.argv[1] == "--summary":
        data = {v: load(v) for v in ("knot", "direct")}
        F_ = {(v, s): [x for x in data[v][0] if x["stratum"] == s] for v in data for s in ("constraining", "monotone")}
        out = {f"{v}/{s}": summarize(F_[(v, s)], data[v][1] if s == "constraining" else []) for v, s in F_}
        con = F_[("knot", "constraining")] + F_[("direct", "constraining")]
        mon = F_[("knot", "monotone")] + F_[("direct", "monotone")]
        mon_c = [x for x in mon if not x["acyclic"]]
        near = lambda p: p["d"] is not None and p["d"] <= 3
        far = lambda p: p["d"] is not None and p["d"] >= 4
        out["control_acyclic_violations"] = sum(out[k]["P1_violations"] for k in out if "/" in k)
        out["P2_monotone_cyclic_near_far"] = [flat_share(fam_lists(mon_c, near)), flat_share(fam_lists(mon_c, far)), len(mon_c)]
        out["P3_tie_free_shortcut_constraining_minus_monotone_cyclic"] = boot_diff(fam_lists_v(con, reach, tf_short),
                                                                                  fam_lists_v(mon_c, reach, tf_short))
        out["P3_shares"] = [flat_share(fam_lists_v(con, reach, tf_short)), flat_share(fam_lists_v(mon_c, reach, tf_short))]
        out["P4_constraining_excess_slope"] = slope_ci(con, excess=True)
        out["constraining_raw_slope"] = slope_ci(con)
        out["monotone_cyclic_excess_slope"] = slope_ci(mon_c, excess=True)
        out["constraining_tied_untied_slope"] = [slope_ci([x for x in con if x["tied"]]), slope_ci([x for x in con if not x["tied"]])]
        for v in ("knot", "direct"):
            out[f"by_level_tf_bonded_{v}_constraining"] = {s: flat_share(fam_lists_v(F_[(v, "constraining")], lambda p, s=s: p["s"] == s and reach(p), tf_bonded))
                                                           for s in range(1, 13)}
        out["direct_minus_knot_deep_tf_bonded_constraining"] = boot_diff(
            fam_lists_v(F_[("direct", "constraining")], lambda p: p["s"] >= 4 and reach(p), tf_bonded),
            fam_lists_v(F_[("knot", "constraining")], lambda p: p["s"] >= 4 and reach(p), tf_bonded))
        json.dump(out, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(out, indent=1))
