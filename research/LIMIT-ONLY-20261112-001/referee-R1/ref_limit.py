"""LIMIT-ONLY-R1: the referee's own recomputation of LIMIT-ONLY-20261112-001.

Independent of dlang.py and census.py. Port relations are computed by bitset algebra: an assignment of a definition's V
distinctions is one bit of a 2^V-bit integer, a call's satisfying set is an OR of ANDs of literal masks, and the ports are read
by folding the locals away. The sampler (fair coins, the frozen draw order) is the referee's own from SHORT-DESC-R1.

  ref_limit.py e WORKER WORKERS     class E share -> result_e_<worker>.jsonl
  ref_limit.py w WORKER             class W worker (150,000 tries) -> result_w_<worker>.jsonl, compared row by row with the census
  ref_limit.py sat                  expansions checked by a SAT solver -> result_sat.json
  ref_limit.py summary              -> result_summary.json
"""
import gzip
import hashlib
import itertools
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts" / "LIMIT-ONLY-20261112-001A" / "LIMIT-ONLY-20261112-001A-E001_limit_only"
N3 = 0b01111110                         # the knot on three ports: every state but 000 and 111 (bit j of a state = port j)
TOP3 = 0xFF
CAPS = dict(defs=6, locals=6, calls=12, depth=6)

_MASKS = {}


def masks(V):
    """Literal masks over the 2^V assignments: pos[j] has bit a set iff distinction j is 1 in assignment a."""
    if V not in _MASKS:
        n = 1 << V
        full = (1 << n) - 1
        pos = []
        for j in range(V):
            block = ((1 << (1 << j)) - 1) << (1 << j)          # within a period of 2^(j+1): the upper half
            period = 1 << (j + 1)
            m = 0
            for start in range(0, n, period):
                m |= block << start
            pos.append(m)
        _MASKS[V] = (pos, [full ^ m for m in pos], full)
    return _MASKS[V]


def call_mask(V, args, rel):
    """Assignments of V distinctions whose values on args form a state allowed by rel (bit s, bit i of s = arg i)."""
    pos, neg, full = masks(V)
    out = 0
    for s in range(1 << len(args)):
        if rel >> s & 1:
            m = full
            for i, x in enumerate(args):
                m &= pos[x] if s >> i & 1 else neg[x]
                if not m:
                    break
            out |= m
    return out


def fold(ok, V, k):
    """The port relation: fold the locals (high bits of the assignment index) onto the ports."""
    width = 1 << V
    while width > (1 << k):
        width >>= 1
        ok = (ok & ((1 << width) - 1)) | (ok >> width)
    return ok


class Family:
    def __init__(self, defs):
        self.defs = [(k, l, [(c, tuple(a)) for c, a in calls]) for k, l, calls in defs]
        self.selfs = [i for i, (_, _, calls) in enumerate(self.defs) if any(c == "SELF" for c, _ in calls)]
        self.kmask = []
        for k, l, calls in self.defs:
            m = masks(k + l)[2]
            for c, a in calls:
                if c == "K":
                    m &= call_mask(k + l, a, N3)
            self.kmask.append(m)
        self.cache = {}

    def rels(self, X):
        """Port relation of every definition when the SELF calls of definition i hold the relation X[i]."""
        if X in self.cache:
            return self.cache[X]
        sx = dict(zip(self.selfs, X))
        out = []
        for i, (k, l, calls) in enumerate(self.defs):
            ok = self.kmask[i]
            for c, a in calls:
                if not ok:
                    break
                if c == "SELF":
                    ok &= call_mask(k + l, a, sx[i])
                elif c != "K":
                    ok &= call_mask(k + l, a, out[c])
            out.append(fold(ok, k + l, k))
        out = tuple(out)
        self.cache[X] = out
        return out

    def step(self, X):
        r = self.rels(X)
        return tuple(r[i] for i in self.selfs), r[-1] != 0


def kind_of(rel):
    S = [s for s in range(8) if rel >> s & 1]
    if S and len(S) < 8 and all(len({tuple((s >> j) & 1 for j in range(3) if j != d) for s in S}) == 4 for d in range(3)):
        return "knot"
    return {0: "none", 1: "three tied", 2: "two tied", 4: "free"}.get(len(S) // 2, "other")


def k_reachable(defs):
    seen, todo = set(), [len(defs) - 1]
    while todo:
        i = todo.pop()
        if i in seen:
            continue
        seen.add(i)
        for c, _ in defs[i][2]:
            if c == "K":
                return True
            if c != "SELF":
                todo.append(c)
    return False


def read(defs):
    F = Family(defs)
    n = len(F.selfs)
    NN, TT = (N3,) * n, (TOP3,) * n
    # the orbit of the knot: X_0 = knot, depth t reads main at X_{t-1}
    orbit, alive, seen, X = [NN], [], {NN: 0}, NN
    while True:
        X2, a = F.step(X)
        alive.append(a)
        if X2 in seen:
            c0 = seen[X2]
            break
        seen[X2] = len(orbit)
        orbit.append(X2)
        X = X2
    period = len(orbit) - c0
    cycle = orbit[c0:]
    first_dead = next((j + 1 for j, a in enumerate(alive) if not a), None)
    fate = "forever" if first_dead is None else ("at once" if first_dead == 1 else "a while")
    after = None if first_dead is None else ("recurrent" if any(alive[c0:]) else "stays dead")
    # the limit: from 'nothing' (TOP) down to the greatest fixed point
    G = TT
    while True:
        G2, _ = F.step(G)
        assert all(g2 & ~g == 0 for g, g2 in zip(G, G2)), "not decreasing"
        if G2 == G:
            break
        G = G2
    limit_alive = F.rels(G)[-1] != 0
    image, _ = F.step(NN)
    up = all(N3 & ~r == 0 for r in image)
    down = all(r & ~N3 == 0 for r in image)
    comp = "equal" if up and down else ("up" if up else ("down" if down else "incomparable"))
    P = NN
    while True:
        Y = tuple(N3 & r for r in F.step(P)[0])
        if Y == P:
            break
        P = Y
    l2_pred = F.rels(P)[-1] != 0
    finite_alive = first_dead is None
    limit_only = (not finite_alive) and limit_alive
    l1 = (not limit_only) or any(g & 1 for g in G)
    kind = None
    if l2_pred != finite_alive:
        kind = "period above 1" if period > 1 else ("fixed point outside the knot" if any(x & 1 for x in orbit[-1])
                                                    else "other")
    union = tuple(0 for _ in range(n))
    for C in cycle:
        union = tuple(u | c for u, c in zip(union, C))
    return dict(fate=fate, first_dead=first_dead, period=period, after=after, limit_alive=limit_alive, limit_only=limit_only,
                comparability=comp, L1_ok=l1, L2_pred=l2_pred, L2_ok=(l2_pred == finite_alive), L2_failure=kind,
                limit_kinds=[kind_of(g) for g in G],
                # referee extras
                limit_knot_all_equal=[bool(g & 1) for g in G if kind_of(g) == "knot"],
                cycle_leaves_knot=any(u & ~N3 & 0xFF for u in union),
                cycle_alive=[alive[j] for j in range(c0, len(orbit))],
                k_reachable=k_reachable(F.defs), depths_read=len(alive))


# ---------- class E ----------

def class_e(worker, workers):
    out = open(HERE / f"result_e_{worker}.jsonl", "w")
    idx = -1
    for l in range(4):
        V = 3 + l
        opts = [("K", c) for c in itertools.combinations(range(V), 3)] + \
               [("SELF", p) for p in itertools.permutations(range(V), 3)]
        for c in (1, 2, 3):
            for body in itertools.combinations(range(len(opts)), c):
                if not any(opts[j][0] == "SELF" for j in body):
                    continue
                idx += 1
                if idx % workers != worker:
                    continue
                defs = [(3, l, [opts[j] for j in body])]
                r = read(defs)
                r["l"], r["c"] = l, c
                if r["limit_only"] or not r["L1_ok"] or not r["L2_ok"] or r["fate"] != "forever":
                    r["defs"] = defs
                out.write(json.dumps(r) + "\n")
    out.close()


# ---------- class W ----------

def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def gamma(rng):
    z = 0
    while rng.random() < 0.5:
        z += 1
    n = 1
    for _ in range(z):
        n = 2 * n + (rng.random() < 0.5)
    return n, 2 * z + 1


def sample(rng, arity_cap=6, self_ok=True):
    bits = 0.0
    r, b = gamma(rng)
    bits += b
    if r > CAPS["defs"]:
        return None, bits, None
    defs = []
    for i in range(r):
        x, b = gamma(rng)
        bits += b
        k = x + 2
        if k > arity_cap:
            return None, bits, None
        x, b = gamma(rng)
        bits += b
        l = x - 1
        if l > CAPS["locals"]:
            return None, bits, None
        c, b = gamma(rng)
        bits += b
        if c > CAPS["calls"]:
            return None, bits, None
        V = k + l
        opts = ["K"] + list(range(i)) + (["SELF"] if self_ok and k == 3 else [])
        calls = []
        for _ in range(c):
            ce = opts[rng.randrange(len(opts))]
            bits += math.log2(len(opts))
            ar = 3 if ce in ("K", "SELF") else defs[ce][0]
            if ar > V:
                return None, bits, None
            calls.append((ce, tuple(rng.sample(range(V), ar))))
            bits += math.log2(math.perm(V, ar))
        defs.append((k, l, calls))
    if not any(ce == "SELF" for d in defs for ce, _ in d[2]):
        return defs, bits, None
    t, b = gamma(rng)
    return defs, bits, t


FIELDS = ["fate", "first_dead", "period", "after", "limit_alive", "limit_only", "comparability", "L1_ok", "L2_pred", "L2_ok",
          "L2_failure", "limit_kinds"]


def class_w(worker, tries=150000):
    rng = random.Random(seed_of("LO", worker))
    rec = [json.loads(x) for x in gzip.open(ART / f"sample_{worker}.jsonl.gz", "rt")]
    rec = [r for r in rec if r.get("kind") != "done"]
    out = open(HERE / f"result_w_{worker}.jsonl", "w")
    j, mism = 0, Counter()
    for _ in range(tries):
        defs, bits, t = sample(rng)
        if defs is None or t is None:
            continue
        r = read(defs)
        c = rec[j] if j < len(rec) else {}
        j += 1
        r["match"] = [f for f in FIELDS if c.get(f) != r[f]] + ([] if abs(c.get("bits", -1) - bits) < 1e-6 else ["bits"])
        for f in r["match"]:
            mism[f] += 1
        if r["limit_only"] or not r["L1_ok"] or not r["L2_ok"] or r["match"]:
            r["defs"] = defs
        out.write(json.dumps(r) + "\n")
    out.write(json.dumps(dict(kind="done", rows=j, census_rows=len(rec), mismatches=dict(mism))) + "\n")
    out.close()


# ---------- SAT checks on expanded patterns ----------

def expand(defs, t, bottom=True, cap=60000):
    """Depth-t pattern (bottom=True: SELF at depth 1 is a knot) or the truncation (bottom=False: SELF at depth 1 dropped)."""
    knots, nv = set(), [defs[-1][0]]

    def go(i, actual, depth):
        k, l, calls = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        for ce, args in calls:
            a = [env[x] for x in args]
            if ce == "K" or (ce == "SELF" and depth <= 1):
                if ce == "K" or bottom:
                    knots.add(tuple(sorted(a)))
                    if len(knots) > cap:
                        raise OverflowError
            elif ce == "SELF":
                go(i, a, depth - 1)
            else:
                go(ce, a, depth)
    try:
        go(len(defs) - 1, list(range(defs[-1][0])), t)
    except OverflowError:
        return None
    return knots


def sat(knots):
    from pysat.solvers import Solver
    if not knots:
        return True
    cls = [c for e in knots for c in ([a + 1 for a in e], [-(a + 1) for a in e])]
    with Solver(name="cadical153", bootstrap_with=cls) as s:
        return s.solve()


def sat_checks():
    rows = []
    for name in sorted(HERE.glob("result_w_*.jsonl")) + sorted(HERE.glob("result_e_*.jsonl")):
        for x in open(name):
            r = json.loads(x)
            if "defs" in r and (r["limit_only"] or not r["L2_ok"]):
                rows.append((name.name[7], r))
    rng = random.Random(7)
    out = Counter()
    examples = []
    for cls, r in rows:
        defs = [(k, l, [(c, tuple(a)) for c, a in calls]) for k, l, calls in r["defs"]]
        if r["limit_only"]:
            fd = r["first_dead"]
            # the first dead depth is unsatisfiable, the one before satisfiable; truncations (no bottom knots) satisfiable
            for t, want in ([(fd - 1, True)] if fd > 1 else []) + [(fd, False), (fd + 1, r["after"] == "recurrent" and None)]:
                if want is None or t < 1:
                    continue
                K = expand(defs, t)
                if K is None:
                    out["limit-only depth: over cap"] += 1
                    continue
                out[f"limit-only depth {'alive' if want else 'dead'}: {'ok' if sat(K) == want else 'MISMATCH'}"] += 1
            for t in range(1, fd + 3):
                K = expand(defs, t, bottom=False)
                if K is None:
                    out["limit-only truncation: over cap"] += 1
                    break
                out[f"limit-only truncation alive: {'ok' if sat(K) else 'MISMATCH'}"] += 1
        else:
            # L2 failures are alive at every depth: check the depths through the orbit's first cycle and one period more
            for t in range(1, r["depths_read"] + r["period"] + 1):
                K = expand(defs, t)
                if K is None:
                    out[f"L2 failure ({cls}): over cap"] += 1
                    break
                ok = sat(K)
                out[f"L2 failure ({cls}) depth alive: {'ok' if ok else 'MISMATCH'}"] += 1
                if not ok and len(examples) < 5:
                    examples.append(dict(defs=r["defs"], t=t))
    json.dump(dict(counts=dict(out), examples=examples), open(HERE / "result_sat.json", "w"), indent=1)
    print(json.dumps(dict(out), indent=1))


# ---------- pass-through SELF calls: the union of the finite patterns ----------

def pass_through(defs):
    """SELF definitions with a SELF call on their own three ports (in some order)."""
    return {i for i, (k, l, calls) in enumerate(defs) if any(c == "SELF" and sorted(a) == [0, 1, 2] for c, a in calls)}


def reachable(defs):
    seen, todo = set(), [len(defs) - 1]
    while todo:
        i = todo.pop()
        if i not in seen:
            seen.add(i)
            todo += [c for c, _ in defs[i][2] if c not in ("K", "SELF")]
    return seen


def union_limit_alive(defs):
    """The union-limit: the bottomless pattern plus the knot on the ports of every copy of a pass-through definition (the
    knot each finite pattern places there at every later depth). Greatest fixed point from TOP, by compactness."""
    F = Family(defs)
    pt = pass_through(F.defs)
    sx_order = F.selfs

    def rels(X):
        sx = dict(zip(sx_order, X))
        out = []
        for i, (k, l, calls) in enumerate(F.defs):
            ok = F.kmask[i]
            for c, a in calls:
                if c == "SELF":
                    ok &= call_mask(k + l, a, sx[i])
                elif c != "K":
                    ok &= call_mask(k + l, a, out[c])
            r = fold(ok, k + l, k)
            out.append(r & N3 if i in pt else r)
        return out
    G = (TOP3,) * len(sx_order)
    while True:
        r = rels(G)
        G2 = tuple(r[i] for i in sx_order)
        if G2 == G:
            return r[-1] != 0
        G = G2


def expand_union(defs, t, cap=60000):
    """The union-limit's truncation at level t: K knots, SELF at depth 1 dropped, the knot on every pass-through copy's ports."""
    pt = pass_through(defs)
    knots, nv = set(), [defs[-1][0]]

    def go(i, actual, depth):
        k, l, calls = defs[i]
        if i in pt:
            knots.add(tuple(sorted(actual)))
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        for ce, args in calls:
            a = [env[x] for x in args]
            if ce == "K":
                knots.add(tuple(sorted(a)))
            elif ce == "SELF":
                if depth > 1:
                    go(i, a, depth - 1)
            else:
                go(ce, a, depth)
            if len(knots) > cap:
                raise OverflowError
    try:
        go(len(defs) - 1, list(range(defs[-1][0])), t)
    except OverflowError:
        return None
    return knots


def pt_census():
    """Regenerate W and split every family by pass-through SELF calls; check the union-limit by SAT on limit-only families."""
    rows = []
    for w in range(8):
        rng = random.Random(seed_of("LO", w))
        for _ in range(150000):
            defs, bits, t = sample(rng)
            if defs is None or t is None:
                continue
            r = read(defs)
            reach = reachable(defs)
            pt = pass_through(defs) & reach
            sd = {i for i in reach if i in Family(defs).selfs}
            r["pt"] = "all" if pt and pt == sd else ("some" if pt else "none")
            r["union_alive"] = union_limit_alive(defs) if r["fate"] != "forever" else True
            r["defs"] = defs
            rows.append(r)
    S = {}
    S["families_by_pt"] = dict(Counter(r["pt"] for r in rows))
    dy = [r for r in rows if r["fate"] != "forever"]
    S["dying_by_pt_and_bottomless_limit"] = {f"{a}|{b}": v for (a, b), v in sorted(Counter((r["pt"], r["limit_alive"]) for r in dy).items())}
    lo = [r for r in rows if r["limit_only"]]
    S["limit_only_by_pt"] = dict(Counter(r["pt"] for r in lo))
    S["limit_only_by_pt_and_union_limit"] = {f"{a}|{b}": v for (a, b), v in sorted(Counter((r["pt"], r["union_alive"]) for r in lo).items())}
    S["limit_only_by_pt_and_comparability"] = {f"{a}|{b}": v for (a, b), v in sorted(Counter((r["pt"], r["comparability"]) for r in lo).items())}
    S["dying_by_pt_and_union_limit"] = {f"{a}|{b}": v for (a, b), v in sorted(Counter((r["pt"], r["union_alive"]) for r in dy).items())}
    gen = [r for r in lo if r["union_alive"]]
    S["union_limit_only"] = len(gen)
    S["union_limit_only_by_comparability"] = dict(Counter(r["comparability"] for r in gen))
    S["union_limit_only_first_dead"] = dict(sorted(Counter(r["first_dead"] for r in gen).items()))
    S["union_limit_only_limit_kinds"] = dict(Counter(k for r in gen for k in r["limit_kinds"]))
    S["union_limit_only_no_K"] = sum(not r["k_reachable"] for r in gen)
    # all-pass-through families: death is monotone in depth (each finite pattern contains the one before)
    S["all_pt_dying_recurrent"] = sum(1 for r in dy if r["pt"] == "all" and r["after"] == "recurrent")
    # SAT: the union-limit's truncations on limit-only families, up to the depth the orbit was read plus two
    chk = Counter()
    for r in lo:
        verdict = None
        for t in range(1, r["depths_read"] + 3):
            K = expand_union(r["defs"], t)
            if K is None:
                verdict = "over cap"
                break
            if not sat(K):
                verdict = False
                break
        else:
            verdict = True
        chk[f"{r['pt']}|computed {r['union_alive']}|SAT {verdict}"] += 1
    S["union_limit_sat_check"] = dict(chk)
    small = sorted(gen, key=lambda r: (len(r["defs"]), sum(len(d[2]) for d in r["defs"]), sum(d[1] for d in r["defs"])))[:4]
    S["smallest_union_limit_only"] = [dict(defs=r["defs"], first_dead=r["first_dead"], comparability=r["comparability"]) for r in small]
    smallpt = sorted([r for r in lo if r["pt"] == "all"], key=lambda r: (len(r["defs"]), sum(len(d[2]) for d in r["defs"])))[:3]
    S["smallest_pass_through_limit_only"] = [dict(defs=r["defs"], first_dead=r["first_dead"]) for r in smallpt]
    json.dump(S, open(HERE / "result_pt.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


# ---------- summary ----------

def summarize(prefix):
    rows = []
    for name in sorted(HERE.glob(f"result_{prefix}_*.jsonl")):
        rows += [json.loads(x) for x in open(name)]
    done = [r for r in rows if r.get("kind") == "done"]
    rows = [r for r in rows if r.get("kind") != "done"]
    S = dict(families=len(rows))
    S["fate_x_limit"] = {f"{a}|{b}": v for (a, b), v in sorted(Counter((r["fate"], r["limit_alive"]) for r in rows).items())}
    S["comparability"] = dict(Counter(r["comparability"] for r in rows))
    S["L1_exceptions"] = sum(not r["L1_ok"] for r in rows)
    S["L2_failures_by_comparability"] = dict(Counter(r["comparability"] for r in rows if not r["L2_ok"]))
    S["L2_failures_by_kind"] = dict(Counter(r["L2_failure"] for r in rows if not r["L2_ok"]))
    S["L2_failures_wrong_way"] = sum(1 for r in rows if not r["L2_ok"] and r["L2_pred"])
    S["L2_failures_cycle_inside_knot"] = sum(1 for r in rows if not r["L2_ok"] and not r["cycle_leaves_knot"])
    S["L2_failures_among_incomparable"] = [sum(not r["L2_ok"] for r in rows if r["comparability"] == "incomparable"),
                                           sum(r["comparability"] == "incomparable" for r in rows)]
    S["compactness_violations"] = sum(1 for r in rows if not r["limit_alive"] and (r["fate"] == "forever" or r["after"] == "recurrent"))
    lo = [r for r in rows if r["limit_only"]]
    S["limit_only"] = len(lo)
    if lo:
        S["limit_only_by_comparability"] = dict(Counter(r["comparability"] for r in lo))
        S["limit_only_first_dead"] = dict(sorted(Counter(r["first_dead"] for r in lo).items()))
        S["limit_only_after"] = dict(Counter(r["after"] for r in lo))
        S["limit_only_limit_kinds"] = dict(Counter(k for r in lo for k in r["limit_kinds"]))
        S["limit_only_knot_kinds_allowing_all_equal"] = [sum(sum(r["limit_knot_all_equal"]) for r in lo),
                                                         sum(len(r["limit_knot_all_equal"]) for r in lo)]
        S["limit_only_no_K_reachable"] = sum(not r["k_reachable"] for r in lo)
        S["limit_only_one_definition"] = sum(len(r["defs"]) == 1 for r in lo)
        S["limit_only_period"] = dict(Counter(r["period"] for r in lo))
        S["limit_only_up_dying_at_once"] = sum(1 for r in lo if r["comparability"] in ("up", "equal"))
    dying = [r for r in rows if r["fate"] != "forever"]
    S["dying"] = len(dying)
    S["dying_alive_in_limit"] = sum(r["limit_alive"] for r in dying)
    S["dying_by_comparability"] = dict(Counter(r["comparability"] for r in dying))
    S["by_comparability_fate"] = {f"{a}|{b}": v for (a, b), v in sorted(Counter((r["comparability"], r["fate"]) for r in rows).items())}
    if done:
        S["census_match"] = done
    return S


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "e":
        class_e(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "w":
        class_w(int(sys.argv[2]))
    elif cmd == "sat":
        sat_checks()
    elif cmd == "pt":
        pt_census()
    elif cmd == "summary":
        out = dict(E=summarize("e"), W=summarize("w"))
        json.dump(out, open(HERE / "result_summary.json", "w"), indent=1)
        print(json.dumps(out, indent=1))
