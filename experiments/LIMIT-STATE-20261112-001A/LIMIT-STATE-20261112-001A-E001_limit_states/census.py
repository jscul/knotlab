"""LIMIT-STATE-20261112-001A: what a living state of the bottomless pattern looks like, on the families alive only in the usual limit.

Families: LIMIT-ONLY-20261112-001's W records of families alive only in the bottomless pattern (1,341, with their definitions).
The usual limit (LIMIT-ONLY-R1): a self-holding definition with a SELF call on its own three ends (pass-through) keeps the knot on
its ends at every later depth, so it gets that knot added; a family is genuine when this usual limit still lives.
For each genuine family, with G the usual limit's greatest fixed point and T its first dead finite depth:
  loose        - every self-holding definition's limit relation and the main relation at G allow every state of their ends;
  the finite part to depth D = T + 3 with G on the bottom SELF calls has, on its distinctions, exactly the restrictions of the
  living states of the usual limit. At each dead depth t (T <= t < D), the SELF calls made from level t - 1 copies ('calls of
  depth t') must include one with all its ends equal in every living state (lemma, by restriction; checked as a gate). Queries
  (SAT, exact): single - some living state has exactly one call with all ends equal at each of depths T, T+1, T+2; single ray -
  moreover each is made inside the copy of the one before.
Run from the repository root:  census.py --run WORKER WORKERS  |  census.py --summary
"""
import glob, gzip, hashlib, json, os, random, sys, time
from collections import Counter
import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census"))
import dlang as L

ROOT = os.path.join(HERE, "../../..")
SRC = os.path.join(ROOT, "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only")
OUT = os.environ.get("LS_OUT") or os.path.join(ROOT, "artifacts/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states")
EXTRA, KNOT_CAP = 3, 60000


def families():
    out = []
    for name in sorted(glob.glob(os.path.join(SRC, "sample_*.jsonl.gz"))):
        for line in gzip.open(name, "rt"):
            r = json.loads(line)
            if r.get("limit_only"):
                out.append([(k, l, [(c, tuple(a)) for c, a in calls]) for k, l, calls in r["defs"]])
    return out


def selfs_of(defs):
    return [i for i, d in enumerate(defs) if any(cl == "SELF" for cl, _ in d[2])]


def usual(defs):
    """Add the knot on its own ends to each self-holding definition with a pass-through SELF call."""
    out, passes = [], False
    for i, (k, l, calls) in enumerate(defs):
        pt = any(cl == "SELF" and sorted(a) == [0, 1, 2] for cl, a in calls)
        passes |= pt
        out.append((k, l, calls + ([("K", (0, 1, 2))] if pt else [])))
    return out, passes


def relation_clauses(vs, rel):
    """CNF forbidding the states of distinctions vs (bit j = vs[j]) outside rel."""
    cl = []
    for s in range(len(rel)):
        if not rel[s]:
            cl.append([-(v + 1) if (s >> j) & 1 else (v + 1) for j, v in enumerate(vs)])
    return cl


def expand(defs, D, G):
    """Depth-D pattern with SELF calls at the bottom constrained by G (no knot). Returns (clauses, calls by depth) where the calls of
    depth t are the SELF calls made from copies at level t - 1, as argument triples."""
    clauses, nv, calls_at, nknots, parent = [], [0], {}, [0], {}

    def call(i, actual, depth, lev, anc):
        k, l, calls = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        for callee, args in calls:
            a = [env[x] for x in args]
            if callee == "K":
                clauses.extend([[x + 1 for x in a], [-(x + 1) for x in a]])
                nknots[0] += 1
                if nknots[0] > KNOT_CAP:
                    raise OverflowError
            elif callee == "SELF":
                cid = (lev + 1, len(calls_at.setdefault(lev + 1, [])))
                calls_at[lev + 1].append(tuple(a))
                parent[cid] = anc
                if depth <= 1:
                    clauses.extend(relation_clauses(a, G[i]))
                else:
                    call(i, a, depth - 1, lev + 1, cid)
            else:
                call(callee, a, depth, lev, anc)

    k = defs[-1][0]
    nv[0] = k
    call(len(defs) - 1, list(range(k)), D, 0, None)
    return clauses, calls_at, nv[0], parent


def first_dead(defs):
    f = L.fate(defs)
    return f["first_dead"], f["after"]


def read(defs0, rng):
    defs, passes = usual(defs0)
    sl = selfs_of(defs)
    _, _, G = L.depth_sequence(defs, L.TOP)
    main_rel = L.relations(defs, G)[-1]
    genuine = bool(main_rel.any())
    rec = dict(passes=passes, genuine=genuine, nself=len(sl))
    if not genuine:
        return rec
    T, after = first_dead(defs)
    kinds = []
    for i in sl:
        pairs = int(G[i].sum()) // 2
        kinds.append("knot" if L.knot_test(G[i]) else {0: "none", 1: "three tied", 2: "two tied", 4: "free"}.get(pairs, "other"))
    rec.update(T=T, after=after, kinds=kinds, main_free=bool(main_rel.all()), loose=all(k == "free" for k in kinds) and bool(main_rel.all()))
    if T is None:
        rec["note"] = "usual limit changes the finite fate"
        return rec
    D = T + EXTRA
    if after == "recurrent":
        rec["skipped"] = "recurrent"
        return rec
    try:
        clauses, calls_at, n, parent = expand(defs, D, G)
    except (OverflowError, RecursionError):
        rec["skipped"] = "size"
        return rec
    rec["n"] = n
    depths = list(range(T, D))
    rec["calls"] = [len(calls_at.get(t, [])) for t in depths]
    top = [n + 1]                                                     # fresh variables after the distinctions

    def fresh():
        top[0] += 1
        return top[0]
    with Solver(name="cadical153", bootstrap_with=clauses) as s:
        rec["alive_part"] = s.solve()
    gates = []
    for t in depths:                                                  # gate: no all-equal call at a dead depth leaves no state
        with Solver(name="cadical153", bootstrap_with=clauses) as g:
            for a in calls_at.get(t, []):
                g.add_clause([x + 1 for x in a]); g.add_clause([-(x + 1) for x in a])
            gates.append(not g.solve())
    rec["gates"] = gates
    from pysat.card import CardEnc, EncType

    def query(ray):
        top[0] = n + 1
        cl = list(clauses)
        r = {}
        for t in depths:
            for j, a in enumerate(calls_at.get(t, [])):
                v = fresh(); r[(t, j)] = v
                x, y, z = [u + 1 for u in a]
                cl += [[-v, -x, y], [-v, x, -y], [-v, -y, z], [-v, y, -z]]          # chosen: all ends equal
                cl += [[v, x, y, z], [v, -x, -y, -z]]                               # not chosen: not all equal
            lits = [r[(t, j)] for j in range(len(calls_at.get(t, [])))]
            enc = CardEnc.equals(lits=lits, bound=1, top_id=top[0], encoding=EncType.seqcounter)
            top[0] = max(top[0], enc.nv)
            cl += enc.clauses
        if ray:
            for t in depths[1:]:
                for j in range(len(calls_at.get(t, []))):
                    p = parent.get((t, j))
                    cl.append([-r[(t, j)], r[p]] if p in r else [-r[(t, j)]])
        with Solver(name="cadical153", bootstrap_with=cl) as q:
            return q.solve()
    rec["single"] = query(False)
    rec["single_ray"] = query(True) if rec["single"] else False
    return rec


def run(worker, workers):
    os.makedirs(OUT, exist_ok=True)
    fams = families()
    f = open(os.path.join(OUT, f"runs_{worker}.jsonl"), "w")
    t0 = time.time()
    for idx, defs in enumerate(fams):
        if idx % workers != worker:
            continue
        rng = random.Random(int(hashlib.sha256(f"LS:{idx}".encode()).hexdigest()[:16], 16))
        r = read(defs, rng)
        r["idx"] = idx
        f.write(json.dumps(r) + "\n")
        f.flush()
    f.write(json.dumps(dict(kind="done", seconds=round(time.time() - t0))) + "\n")
    f.close()


def summarize():
    rows = [json.loads(x) for name in sorted(glob.glob(os.path.join(OUT, "runs_*.jsonl"))) for x in open(name)]
    rows = [r for r in rows if r.get("kind") != "done"]
    g = [r for r in rows if r["genuine"]]
    S = dict(families=len(rows), genuine=len(g), genuine_no_pass=sum(not r["passes"] for r in g),
             genuine_with_pass=sum(r["passes"] for r in g))
    S["loose_share"] = round(sum(r["loose"] for r in g) / len(g), 4) if g else None
    S["limit_kinds"] = dict(Counter(k for r in g for k in r["kinds"]))
    rd = [r for r in g if "single" in r]
    S["read"], S["not_read"] = len(rd), dict(Counter(r.get("skipped") or r.get("note") for r in g if "single" not in r))
    S["gate_failures"] = sum(not x for r in rd for x in r["gates"]) + sum(not r["alive_part"] for r in rd)
    chain = [r for r in rd if max(r["calls"]) == 1]
    br = [r for r in rd if max(r["calls"]) >= 2]
    S["chains"], S["branching"] = len(chain), len(br)
    S["chains_single_ray"] = sum(r["single_ray"] for r in chain)
    S["P1_single_share_branching"] = round(sum(r["single"] for r in br) / len(br), 4) if br else None
    S["P2_single_ray_share_branching"] = round(sum(r["single_ray"] for r in br) / len(br), 4) if br else None
    for a in (True, False):
        x = [r for r in br if r["loose"] == a]
        S[f"branching_loose={a}"] = dict(n=len(x), single=sum(r["single"] for r in x), single_ray=sum(r["single_ray"] for r in x))
    S["calls_by_offset_median"] = [float(np.median([r["calls"][j] for r in br])) for j in range(EXTRA)] if br else None
    S["T"] = dict(Counter(r["T"] for r in rd))
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))
