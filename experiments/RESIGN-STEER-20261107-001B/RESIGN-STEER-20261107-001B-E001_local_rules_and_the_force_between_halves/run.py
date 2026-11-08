"""RESIGN-STEER-20261107-001B-E001: local steering rules and the force between the two halves (exploratory; see contract.json).

After the split of RESIGN-STEER-20261107-001A, a consistent state of a law with two even faces is a perfect matching of the line-face
graph H minus those faces: each line agrees at one face. A clean move at an even face h re-signs the side of a line i at h that joins
h to the face where i agrees; i then agrees at h and the even face moves there (lemma 4.2 of that record). The rules below only see
the lines at h, where each agrees, and the experimenter's distance signal. The count of consistent states for even faces u, v is
2 #PM(H - {u, v}); it is compared with its least value 2 N(T), reached by adjacent faces (theorem 3).
Writes artifacts/RESIGN-STEER-20261107-001B/RESIGN-STEER-20261107-001B-E001_local_rules_and_the_force_between_halves/run/result.json."""
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
from networkx.algorithms import bipartite

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIB = ROOT / "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere"
sys.path.insert(0, str(LIB))
import steer_lib as L  # noqa: E402

OUT = ROOT / "artifacts/RESIGN-STEER-20261107-001B/RESIGN-STEER-20261107-001B-E001_local_rules_and_the_force_between_halves/run"
T0 = time.time()
RES = {}


def log(*a):
    print(*a, round(time.time() - T0, 1), "s", flush=True)


def sphere(m):
    S = L.SM.octahedral(m)
    K = L.Sphere(S, f"K_{m}")
    K.pos = {v: S.vname[v] for v in range(K.V)}
    K.inv = {p: v for v, p in K.pos.items()}
    return K


def start(K, rng):
    """the split at a random line: a perfect matching of H - {a, b} found with shuffled edges"""
    l = rng.randrange(K.n)
    a, b, _ = K.fv[l]
    tops = [("l", i) for i in range(K.n)]
    edges = [(("l", i), ("f", v)) for i in range(K.n) for v in K.fv[i] if v not in (a, b)]
    rng.shuffle(edges)
    G = nx.Graph()
    G.add_nodes_from(tops)
    G.add_edges_from(edges)
    M = bipartite.hopcroft_karp_matching(G, top_nodes=tops)
    match = {i: M[("l", i)][1] for i in range(K.n)}
    return l, match, [a, b]


def run_rule(K, match, holes, target, rule, rng, budget, decoy=None):
    match = dict(match)
    dt = K.dist(target)
    d = K.dist(decoy) if rule == "decoy" else dt
    j = 0 if dt[holes[0]] <= dt[holes[1]] else 1
    h, other, last, path = holes[j], holes[1 - j], None, []
    for step in range(budget + 1):
        if h == target:
            return True, step, path
        if step == budget:
            break
        moves = [(i, match[i]) for (i, _) in K.lines_at[h] if match[i] != other]
        if not moves:
            return False, step, path
        if rule == "random":
            i, w = rng.choice(moves)
        else:
            cand = ([mv for mv in moves if mv[1] != last] or moves) if rule in ("no_reversal", "decoy") else moves
            best = min(d[w] for _, w in cand)
            if rule == "strict" and best >= d[h]:
                return False, step, path
            i, w = rng.choice([mv for mv in cand if d[mv[1]] == best])
        match[i] = h
        path.append((i, h, w))
        last, h = h, w
    return False, budget, path


def replay_ok(K, l, match, holes, path, other):
    """replay a rule's moves as sign changes on a real state: every step keeps (no violated line, E = 0, even faces {h, other})"""
    s, _ = K.split_signing(l)
    x = K.K.assignment_from([K.fv[i].index(match[i]) for i in range(K.n)], s)
    for (i, h, w) in path:
        s[3 * i + K.side_between(i, h, w)] ^= 1
        v, _, D, E = K.tally(s, x)
        if v or E or sorted(D) != sorted([w, other]):
            return False
    return True


def rules_experiment(rng):
    rows, fails = [], []
    for m in (2, 3, 4, 5, 6, 7, 8, 10):
        K = sphere(m)
        budget = 40 * m
        trials = []
        while len(trials) < 300:
            l, match, holes = start(K, rng)
            t = rng.randrange(K.V)
            if t in holes:
                continue
            trials.append((l, match, holes, t, rng.randrange(K.V)))
        row = {"sphere": K.name, "faces": K.V, "budget": budget}
        for rule in ("strict", "sideways", "no_reversal", "random", "decoy"):
            ok, ratio = 0, []
            for (l, match, holes, t, decoy) in trials:
                r, st, path = run_rule(K, match, holes, t, rule, rng, budget, decoy)
                d0 = min(K.dist(t)[holes[0]], K.dist(t)[holes[1]])
                if r:
                    ok += 1
                    ratio.append(st / max(d0, 1))
                elif rule == "no_reversal":
                    r10, st10, _ = run_rule(K, match, holes, t, rule, rng, 10 * budget)
                    fails.append({"sphere": K.name, "start distance": d0, "reached with 10x budget": r10, "steps": st10})
            row[rule] = {"reached": ok, "of": len(trials), "mean steps / start distance": round(float(np.mean(ratio)), 2) if ratio else None}
        # replay a few no_reversal runs as real sign changes
        rep = []
        for (l, match, holes, t, decoy) in trials[:5]:
            r, st, path = run_rule(K, match, holes, t, "no_reversal", random.Random(1), budget)
            dt = K.dist(t)
            j = 0 if dt[holes[0]] <= dt[holes[1]] else 1
            rep.append(replay_ok(K, l, match, holes, path, holes[1 - j]))
        row["replayed as sign changes"] = all(rep)
        rows.append(row)
        log("rules", K.name, {k: row[k]["reached"] for k in ("strict", "sideways", "no_reversal", "random", "decoy")})
    return rows, fails


def landscape(m):
    K = sphere(m)
    a, b, _ = K.fv[0]
    logN = K.count_pm({a, b})
    corners = set(K.corners())
    src = {"corner": K.inv[(m, 0, 0)], "edge midpoint": K.inv[(m // 2, m - m // 2, 0)],
           "octant centre": K.inv[(m // 3, m // 3, m - 2 * (m // 3))]}
    out = {}
    for name, u in src.items():
        byd, vals = defaultdict(list), []
        for v in range(K.V):
            if v == u:
                continue
            y = K.count_pm({u, v}) - logN
            dd = K.dist(u)[v]
            byd[dd].append(y)
            vals.append((y, v, dd))
        lo, hi = min(vals), max(vals)
        out[name] = {
            "source": K.pos[u],
            "mean log(count / N) by distance": {str(dd): round(float(np.mean(ys)), 4) for dd, ys in sorted(byd.items())},
            "minimum": [round(lo[0], 6), K.pos[lo[1]], lo[2]],
            "maximum": [round(hi[0], 4), K.pos[hi[1]], hi[2], hi[1] in corners],
            "at corners": {str(K.pos[v]): round(y, 4) for y, v, dd in vals if v in corners},
            "share of other faces with count > N": round(sum(1 for y, v, dd in vals if y > 1e-9) / len(vals), 4),
        }
        log("landscape", K.name, name, out[name]["minimum"], out[name]["maximum"])
    return {"sphere": K.name, "log N": logN, "sources": out}


def exponent(m, rng):
    K = sphere(m)
    a, b, _ = K.fv[0]
    logN = K.count_pm({a, b})
    corners = K.corners()
    dc = {v: min(K.dist(c)[v] for c in corners) for v in range(K.V)}
    u = K.inv[(m // 3, m // 3, m - 2 * (m // 3))]
    byd = defaultdict(list)
    for v in range(K.V):
        if v != u and dc[v] >= m // 3 and K.dist(u)[v] <= m:
            byd[K.dist(u)[v]].append(v)
    pts = []
    for dd in sorted(byd):
        for v in rng.sample(byd[dd], min(3, len(byd[dd]))):
            pts.append((dd, K.count_pm({u, v}) - logN))
    ds = np.array([p[0] for p in pts], float)
    ys = np.array([p[1] for p in pts])
    sel = (ds >= 2) & (ds <= m // 2)
    slope = float(np.polyfit(np.log(ds[sel]), ys[sel], 1)[0])
    means = {str(int(dd)): round(float(np.mean([p[1] for p in pts if p[0] == dd])), 4) for dd in sorted(set(ds))}
    log("exponent", K.name, round(slope, 3))
    return {"sphere": K.name, "source": K.pos[u], "fit range": [2, m // 2], "slope": round(slope, 4), "mean log(count / N) by distance": means}


def ascent(m, runs, rng):
    K = sphere(m)
    corners = set(K.corners())
    cache = {}

    def ent(u, v):
        key = (min(u, v), max(u, v))
        if key not in cache:
            cache[key] = K.count_pm({u, v})
        return cache[key]
    a, b, _ = K.fv[0]
    logN = ent(a, b)
    ends, finals, steps = Counter(), [], []
    for _ in range(runs):
        h = list(K.fv[rng.randrange(K.n)][:2])
        st = 0
        while True:
            cur, best = ent(*h), None
            for j in (0, 1):
                for w in K.adj[h[j]]:
                    if w == h[1 - j]:
                        continue
                    e = ent(w, h[1]) if j == 0 else ent(h[0], w)
                    if e > cur + 1e-12 and (best is None or e > best[0]):
                        best = (e, j, w)
            if best is None:
                break
            h[best[1]] = best[2]
            st += 1
        u, v = h
        both = u in corners and v in corners
        anti = both and tuple(-c for c in K.pos[u]) == K.pos[v]
        ends["two corners, antipodal" if anti else ("two corners, not antipodal" if both else "not both on corners")] += 1
        finals.append(round(ent(u, v) - logN, 4))
        steps.append(st)
    cl = sorted(corners)
    cmax = max(ent(p, q) for p in cl for q in cl if p < q) - logN
    chance = len(corners) * (len(corners) - 1) / (K.V * (K.V - 1))
    log("ascent", K.name, dict(ends))
    return {"sphere": K.name, "runs": runs, "endpoints": dict(ends), "final log(count / N)": sorted(set(finals)),
            "largest log(count / N) over corner pairs": round(cmax, 4), "mean steps": round(float(np.mean(steps)), 1),
            "chance that a random pair is two corners": round(chance, 5)}


if __name__ == "__main__":
    rng = random.Random(20261107)
    rules, fails = rules_experiment(rng)
    RES["rules"] = rules
    RES["no_reversal failures rerun with 10x budget"] = fails
    RES["landscape"] = [landscape(m) for m in (4, 6, 8)]
    RES["exponent"] = [exponent(m, rng) for m in (12, 16)]
    RES["ascent"] = [ascent(m, 30 if m <= 6 else 12, rng) for m in (3, 4, 5, 6, 7, 8)]
    nr = [r["no_reversal"]["reached"] / r["no_reversal"]["of"] for r in rules]
    RES["decisions"] = {
        "no_reversal reaches >= 95% on every sphere": all(x >= 0.95 for x in nr),
        "every no_reversal failure reached with 10x budget": all(f["reached with 10x budget"] for f in fails),
        "K_16 slope within 0.1 of 1/2": abs(RES["exponent"][-1]["slope"] - 0.5) <= 0.1,
        "every ascent stops with both even faces on corners": all(set(a["endpoints"]) <= {"two corners, antipodal", "two corners, not antipodal"}
                                                                  for a in RES["ascent"]),
        "adjacent faces give the least count from every source": all(abs(s["minimum"][0]) < 1e-6 and s["minimum"][2] == 1
                                                                     for L_ in RES["landscape"] for s in L_["sources"].values()),
    }
    RES["seconds"] = round(time.time() - T0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")
    log("wrote", OUT / "result.json", RES["decisions"])
