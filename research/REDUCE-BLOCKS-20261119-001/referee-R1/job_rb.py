"""Shared-runner job for the referee's check of REDUCE-BLOCKS-20261119-001 (own code: the referee's EXPLOSIVE-R1 grower with the
program's rule, groups as maximal cliques of the candidate graph with no common neighbour, structural implied test; its own blocks,
hub realization and other realizations; the study's hublib.hub_realization run only as the object under test).

The comparison is stronger than the study's per-round multiset of (parent count, fresh count): every junction is named by its
round, the names of its parents and its fresh count (round-0 live knots by their name in X), and the per-round multisets of
(parent names, fresh) are compared, so equal signatures mean the same junctions with the same parents round by round (up to
exchanging twin offshoots of one parent).

For each start X, in a forked child with an address-space and time limit:
- X's live knots, open counts and maximal blocks (own code); "no live knot" counted apart (the amendment);
- the realizations, each checked for: its blocks (every N(w) ∩ live with two or more points) are exactly X's maximal blocks;
  connected; every dead knot with three places; open counts kept:
    mine   one dead hub per maximal block, hubs chained hub to hub, one dead connector per live knot in no block;
    theirs hublib.hub_realization (the object under test);
    random mine plus hubs on random sub-blocks, duplicate hubs, one live-to-live touch where it adds no block, extra dead shares;
- grown from round 1 against X: mine, theirs and random must equal X's signature; a control that changes D (a maximal block of
  three or more replaced by hubs on all its sub-blocks one smaller) should usually differ;
- Lemma R step 3 directly on X's growth: at every round t >= 1 each live junction's neighbours are exactly its parents, and the
  candidate pairs are exactly the pairs sharing a parent.

Cases: census-c (every touch-census arrangement, chunk c of 32, 6 rounds); rand-n (125 own random starts of n = 6..14 knots within
eight places, multiple shares allowed, no filter, 7 rounds); stage-i (EXPLOSIVE's explosive cap-7 start i: its stages after s = 1..7
rounds taken as starts, 3 rounds, against their realizations, and against the continuation of the growth itself).

  .venv/bin/python -B scripts/longrun.py launch research/REDUCE-BLOCKS-20261119-001/referee-R1/job_rb.py \\
      --out runs/referee-rb --unit referee-rb --workers 3 --case-timeout 7200 --case-mem 4G --mem-max 13G
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/EXPLOSIVE-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/MERGE-BURST-20261119-001/referee-R1",
          "proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce"):
    sys.path.insert(0, str(ROOT / p))
PARAMS = {}


def setup(params):
    PARAMS.update(params)


# ---- starts as (sizes, edges); edges may repeat (two knots sharing several distinctions) ----

def analyse(sizes, edges):
    n = len(sizes)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    ls = set(live)
    fam = {frozenset(nb[w] & ls) for w in range(n)}
    big = {B for B in fam if len(B) >= 2}
    maximal = {B for B in big if not any(B < C for C in big)}
    return {"live": live, "open": opn, "blocks": big, "maximal": maximal, "nb": nb, "shared": sh}


def connected(n, edges):
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    if n == 0:
        return True
    seen, st = {0}, [0]
    while st:
        u = st.pop()
        for v in nb[u]:
            if v not in seen:
                seen.add(v)
                st.append(v)
    return len(seen) == n


def pad(n, edges, dead):
    """Give every dead knot three places by extra shares with a dead neighbour (adding one dead knot if there is only one)."""
    sh = Counter()
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
    dead = sorted(dead)
    if len(dead) == 1:
        edges.append((dead[0], n))
        dead.append(n)
        sh[dead[0]] += 1
        sh[n] += 1
        n += 1
    nbd = defaultdict(set)
    for a, b in edges:
        if a in dead and b in dead:
            nbd[a].add(b)
            nbd[b].add(a)
    for w in dead:
        while sh[w] < 3:
            x = min(nbd[w])
            edges.append((min(w, x), max(w, x)))
            sh[w] += 1
            sh[x] += 1
    return n, edges, sh


def realize(A, extra_blocks=(), touch=None, dead_extra=0, rng=None):
    """A start whose live knots are X's (with their open counts) and whose blocks are the given hub sets: one dead hub per set in
    A's maximal blocks plus extra_blocks, hubs chained, one dead connector per live knot in no hub set; an optional live-to-live
    touch; dead_extra random extra dead-to-dead shares.  Returns (sizes, edges, livemap: index -> X's live knot)."""
    live = A["live"]
    lid = {k: i for i, k in enumerate(live)}
    hubsets = sorted(A["maximal"], key=sorted) + list(extra_blocks)
    e, n, chain = [], len(live), []
    for B in hubsets:
        for k in sorted(B):
            e.append((lid[k], n))
        chain.append(n)
        n += 1
    inb = set().union(*hubsets) if hubsets else set()
    for k in live:
        if k not in inb:
            e.append((lid[k], n))
            chain.append(n)
            n += 1
    e += [(a, b) for a, b in zip(chain, chain[1:])]
    if touch is not None:
        e.append((lid[touch[0]], lid[touch[1]]))
    for _ in range(dead_extra):
        a, b = rng.sample(chain, 2) if len(chain) >= 2 else (None, None)
        if a is not None:
            e.append((min(a, b), max(a, b)))
    n, e, sh = pad(n, e, set(range(len(live), n)))
    sizes = [sh[i] + A["open"][live[i]] if i < len(live) else sh[i] for i in range(n)]
    return sizes, sorted(tuple(sorted(x)) for x in e), {i: k for i, k in enumerate(live)}


def check_realization(A, sizes, edges, livemap):
    """Its blocks are exactly A's maximal blocks; connected; dead knots with three places; open counts kept."""
    B = analyse(sizes, edges)
    blocks = {frozenset(livemap[i] for i in S) for S in B["blocks"]}
    deadok = all(sizes[k] >= 3 for k in range(len(sizes)) if B["open"][k] == 0)
    openok = sorted(livemap[i] for i in B["live"]) == sorted(A["live"]) and all(
        B["open"][i] == A["open"][livemap[i]] for i in B["live"])
    maximal = {B for B in blocks if not any(B < C for C in blocks)}
    return {"its maximal blocks are X's": maximal == A["maximal"], "no other blocks": blocks == A["maximal"],
            "connected": connected(len(sizes), edges),
            "dead knots have three places": deadok, "open counts kept": openok}


# ---- growth signatures ----

def signature(G, livemap, T, intern, maxj, step3=False):
    import job_expl as JX
    names = {k: intern.setdefault(("L", livemap[k]), len(intern)) for k in livemap}
    sig, bad3 = [], Counter()
    for t in range(1, T + 1):
        before = len(G.bits)
        r = G.step(JX.floored, None, None)
        if r != "ok":
            sig.append(r)
            break
        cnt = Counter()
        for j in range(before, len(G.bits)):
            pn = tuple(sorted(names.get(p, -1) for p in G.parents[j]))
            names[j] = intern.setdefault((t, pn, G.fresh[j]), len(intern))
            cnt[(pn, G.fresh[j])] += 1
        sig.append(sorted(cnt.items()))
        if step3:
            lv = [j for j in G.live if any(len(G.owner[b]) == 1 for b in G.bits[j])]
            bad3["live junctions checked"] += len(lv)
            bad3["neighbours are not exactly the parents"] += sum(G.nbr[j] != G.parents[j] for j in lv)
            if len(lv) <= 1500:
                ls = set(lv)
                cand = set()
                for w in range(len(G.bits)):
                    cand |= set(itertools.combinations(sorted(G.nbr[w] & ls), 2))
                byp = defaultdict(list)
                for j in lv:
                    for p in G.parents[j]:
                        byp[p].append(j)
                share = set()
                for js in byp.values():
                    share |= set(itertools.combinations(sorted(js), 2))
                bad3["rounds where candidate pairs were compared"] += 1
                bad3["candidate pairs differ from pairs sharing a parent"] += cand != share
        if len(G.bits) > maxj:
            sig.append("cap")
            break
    return sig, bad3


def agree(a, b):
    m = min(len(a), len(b))
    if a[:m] != b[:m]:
        return False
    return len(a) == len(b) or "cap" in (a[m - 1], b[m - 1]) or m == 0


def stars(sizes, edges):
    import job_ring as JR
    return JR.stars_of(len(sizes), list(edges), list(sizes))


def sub_blocks_control(A):
    big = [B for B in sorted(A["maximal"], key=sorted) if len(B) >= 3]
    if not big:
        return None
    B = big[0]
    rest = {C for C in A["maximal"] if C != B}
    subs = {frozenset(S) for S in itertools.combinations(sorted(B), len(B) - 1)}
    return dict(A, maximal=rest | subs)


def compare_all(sizes, edges, T, maxj, rng, with_theirs=True):
    import job_expl as JX
    A = analyse(sizes, edges)
    out = {}
    intern = {}
    if not A["live"]:
        G = JX.grower(stars(sizes, edges))
        out["no live knot; X makes nothing"] = G.step(JX.floored, None, None) == "closed"
        if with_theirs:
            import hublib as HB
            out["theirs is empty"] = HB.hub_realization(sizes, edges) == ([], [])
        return out
    X, b3 = signature(JX.grower(stars(sizes, edges)), {k: k for k in A["live"]}, T, intern, maxj, step3=True)
    out["X"] = [len(X), X[-1] if isinstance(X[-1], str) else "alive"]
    out["step 3"] = dict(b3)
    reals = {"mine": realize(A)}
    if with_theirs:
        import hublib as HB
        sh_, eh = HB.hub_realization(sizes, edges)
        reals["theirs"] = (sh_, [tuple(x) for x in eh], {i: k for i, k in enumerate(A["live"])})
    # random: sub-blocks and duplicates, one safe live-to-live touch, extra dead shares
    extra = []
    for B in sorted(A["maximal"], key=sorted):
        if len(B) >= 3 and rng.random() < 0.5:
            extra.append(frozenset(rng.sample(sorted(B), rng.randint(2, len(B) - 1))))
        if rng.random() < 0.3:
            extra.append(B)
    lone = [k for k in A["live"] if not any(k in B for B in A["maximal"])]
    touch = tuple(rng.sample(lone, 2)) if len(lone) >= 2 and rng.random() < 0.7 else None
    reals["random"] = realize(A, extra, touch, rng.randint(0, 3), rng)
    out["random has a live-to-live touch"] = touch is not None
    for name, (s2, e2, lm) in reals.items():
        out[name + " realization"] = check_realization(A, s2, e2, lm)
        Y, _ = signature(JX.grower(stars(s2, e2)), {i: lm[i] for i in lm}, T, intern, maxj)
        out[name + " grows like X"] = agree(X, Y)
    C = sub_blocks_control(A)
    if C is not None:
        s2, e2, lm = realize(C)
        Y, _ = signature(JX.grower(stars(s2, e2)), lm, T, intern, maxj)
        out["control made"] = True
        out["control (a maximal block split) grows like X"] = agree(X, Y)
    return out


def isolated(fn, args, mem, seconds):
    import multiprocessing as mp
    import time
    ctx = mp.get_context("fork")
    a, b = ctx.Pipe(duplex=False)

    def child(conn):
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        try:
            conn.send(fn(*args))
        except MemoryError:
            conn.send({"skip": "memory"})
        except Exception as x:  # noqa: BLE001  (reported as an error, never as a limit)
            conn.send({"error": repr(x)[:300]})
    pr = ctx.Process(target=child, args=(b,))
    pr.start()
    b.close()
    res = {"skip": "time"}
    t0 = time.time()
    while time.time() - t0 < seconds:
        if a.poll(0.5):
            try:
                res = a.recv()
            except EOFError:
                res = {"skip": "memory"}
            break
        if not pr.is_alive() and not a.poll(0):
            res = {"skip": "memory"}
            break
    pr.kill()
    pr.join(5)
    return res


def tally(results):
    s = Counter()
    bad = []
    for key, r in results:
        if "skip" in r:
            s["stopped by the limits (" + r["skip"] + ")"] += 1
            continue
        if "error" in r:
            s["errors"] += 1
            if len(bad) < 10:
                bad.append({"start": key, "error": r["error"]})
            continue
        s["compared"] += 1
        for k, v in r.items():
            if isinstance(v, bool):
                s[k] += v
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    s[k + ": " + k2] += int(v2)
        wrong = [k for k in ("mine grows like X", "theirs grows like X", "random grows like X") if k in r and not r[k]]
        wrong += [k for k in r if k.endswith("realization") and not all(
            v for k2, v in r[k].items() if not (k.startswith("random") and k2 == "no other blocks"))]
        wrong += ["step 3"] if r.get("step 3", {}).get("neighbours are not exactly the parents") or r.get("step 3", {}).get(
            "candidate pairs differ from pairs sharing a parent") else []
        if "no live knot; X makes nothing" in r and not (r["no live knot; X makes nothing"] and r.get("theirs is empty", True)):
            wrong.append("empty")
        if wrong:
            s["starts with a failure"] += 1
            if len(bad) < 10:
                bad.append({"start": key, "failed": wrong})
    return {"counts": dict(s), "failures": bad}


# ---- populations ----

def census_keys():
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok":
            rows += [a["key"] for a in r["result"]["arrangements"]]
    rows.sort(key=str)
    return rows


def key_start(key):
    sizes, flat = key
    n = len(sizes)
    e = []
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def sample(n, rng, P=8):
    """A random connected start of n knots within P places: a random tree, a few extra shares (repeats allowed), and some knots
    made dead by setting their places to their shared count when it is three or more."""
    while True:
        sizes = [rng.randint(3, P) for _ in range(n)]
        deg = [0] * n
        order = list(range(n))
        rng.shuffle(order)
        e, ok = [], True
        for i in range(1, n):
            v = order[i]
            cand = [u for u in order[:i] if deg[u] < sizes[u]]
            if not cand or deg[v] >= sizes[v]:
                ok = False
                break
            u = rng.choice(cand)
            e.append((min(u, v), max(u, v)))
            deg[u] += 1
            deg[v] += 1
        if not ok:
            continue
        want = rng.choice((0, 1, 2, 3, 4, 6))
        for _ in range(want * 4):
            if want <= 0:
                break
            u, v = rng.sample(range(n), 2)
            if deg[u] < sizes[u] and deg[v] < sizes[v]:
                e.append((min(u, v), max(u, v)))
                deg[u] += 1
                deg[v] += 1
                want -= 1
        for k in range(n):
            if deg[k] >= 3 and rng.random() < 0.2:
                sizes[k] = deg[k]
        return sizes, sorted(e)


def stage_case(x, s, T, maxj):
    """X's stage after s rounds taken as a start, against its realizations, and against the continuation itself."""
    import job_expl as JX
    G = JX.grower(stars(x["sizes"], x["edges"]))
    for _ in range(s):
        if G.step(JX.floored, None, None) != "ok":
            return {"skip": "ended before the stage"}
    st = [list(b) for b in G.bits]
    own = defaultdict(list)
    for j, q in enumerate(st):
        for b in q:
            own[b].append(j)
    sizes = [len(q) for q in st]
    edges = sorted(tuple(sorted(v)) for v in own.values() if len(v) == 2)
    rng = random.Random(f"stage-{s}")
    out = compare_all(sizes, edges, T, maxj, rng)
    A = analyse(sizes, edges)
    intern = {}
    a, _ = signature(JX.grower(st), {k: k for k in A["live"]}, T, intern, maxj)
    b, _ = signature(G, {k: k for k in A["live"]}, T, intern, maxj)
    out["the stage as a start grows like the continuation"] = agree(a, b)
    out["stage junctions, live, maximal blocks"] = {"junctions": len(st), "live": len(A["live"]), "maximal": len(A["maximal"])}
    return out


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [(f"stage-{i:02d}", {"kind": "stage", "i": i}) for i in range(16)]
    allc += [(f"rand-{n:02d}", {"kind": "rand", "n": n}) for n in range(14, 5, -1)]
    allc += [(f"census-{c:02d}", {"kind": "census", "c": c}) for c in range(32)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    import hublib  # noqa: F401  (the object under test, imported before forking)
    import job_expl  # noqa: F401
    res = []
    if p["kind"] == "census":
        for key in census_keys()[p["c"]::32]:
            sizes, e = key_start(key)
            rng = random.Random(json.dumps(key))
            res.append((key, isolated(compare_all, (sizes, e, 6, 100_000, rng), 2_500_000_000, 120)))
        return tally(res)
    if p["kind"] == "rand":
        rng = random.Random(f"referee-rb-{p['n']}")
        for _ in range(125):
            sizes, e = sample(p["n"], rng)
            r2 = random.Random(rng.random())
            res.append(([sizes, e], isolated(compare_all, (sizes, e, 7, 150_000, r2), 3_500_000_000, 240)))
        return tally(res)
    import job_mb as MB
    pop = MB.population()
    x = pop[p["i"]]
    per = []
    for s in range(1, 8):
        r = isolated(stage_case, (x, s, 3, 150_000), 3_500_000_000, 600)
        per.append([s, r.get("skip") or "compared", r.get("stage junctions, live, maximal blocks")])
        if r.get("skip") != "ended before the stage":
            res.append(([x["sizes"], x["edges"], s], r))
    out = tally(res)
    out["stages"] = per
    return out
