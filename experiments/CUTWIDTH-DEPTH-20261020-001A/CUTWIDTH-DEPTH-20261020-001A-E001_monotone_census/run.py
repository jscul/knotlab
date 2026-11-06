#!/usr/bin/env python3
"""Producer for CUTWIDTH-DEPTH-20261020-001A-E001 (frozen contract: contract.json).

For every roster graph: cutwidth, toggle width, monotone toggle width and the
cut game value (the least, over sweeps that may also remove vertices, of the
largest cut visited). For the 12-vertex cubic graphs: the depth certificates of
the parity network with charge 1 at vertex 0 (the sweep refutation at
cutwidth + 1, verified by substitution; the Fourier construction's consistency
at cutwidth, with random equations checked on it).

The 12-vertex cubic graphs are sampled as uniform random labelled cubic graphs
(configuration model, rejecting loops and multiple edges) until the published
number of isomorphism classes, 85, is reached; the same sampler must recover
the 19 classes on 10 vertices that exhaustive generation finds.
"""

from __future__ import annotations

import gzip
import heapq
import json
import random
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "CUTWIDTH-DEPTH-20261020-001A" / HERE.name
SEED = 20261020
PUBLISHED_CUBIC_12 = 85


# ---------------------------------------------------------------- graphs and isomorphism

def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def connected(n, edges):
    adj = adjacency(n, edges)
    seen, todo = {0}, [0]
    while todo:
        x = todo.pop()
        for y in adj[x] - seen:
            seen.add(y)
            todo.append(y)
    return len(seen) == n


def vertex_profile(adj, v):
    """Distance profile of v, with its triangle and square counts."""
    n = len(adj)
    dist = {v: 0}
    frontier = [v]
    while frontier:
        nxt = []
        for x in frontier:
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    nxt.append(y)
        frontier = nxt
    layers = Counter(dist.values())
    triangles = sum(1 for x, y in combinations(sorted(adj[v]), 2) if y in adj[x])
    squares = sum(len((adj[x] & adj[y]) - {v}) for x, y in combinations(sorted(adj[v]), 2))
    return (len(adj[v]), triangles, squares, tuple(layers[d] for d in range(1, max(layers) + 1)) if n > 1 else ())


def invariant(n, edges):
    adj = adjacency(n, edges)
    return tuple(sorted(vertex_profile(adj, v) for v in range(n)))


def isomorphic(n, e1, e2):
    a1, a2 = adjacency(n, e1), adjacency(n, e2)
    p1 = [vertex_profile(a1, v) for v in range(n)]
    p2 = [vertex_profile(a2, v) for v in range(n)]
    order = sorted(range(n), key=lambda v: (-len(a1[v]), p1[v]))
    mapping, used = {}, set()

    def place(i):
        if i == n:
            return True
        v = order[i]
        for w in range(n):
            if w in used or p2[w] != p1[v]:
                continue
            if all((u in a1[v]) == (mapping[u] in a2[w]) for u in mapping):
                mapping[v] = w
                used.add(w)
                if place(i + 1):
                    return True
                del mapping[v]
                used.discard(w)
        return False

    return place(0)


class Classes:
    def __init__(self, n):
        self.n = n
        self.buckets = defaultdict(list)
        self.reps = []

    def add(self, edges):
        key = invariant(self.n, edges)
        for rep in self.buckets[key]:
            if isomorphic(self.n, edges, rep):
                return False
        self.buckets[key].append(edges)
        self.reps.append(edges)
        return True


def labelled_cubic(n):
    out = []
    degree = [0] * n
    edges = [(0, 1), (0, 2), (0, 3)]
    degree[0] = 3
    for v in (1, 2, 3):
        degree[v] = 1

    def grow(v, low):
        if v < n and degree[v] == 3:
            while v < n and degree[v] == 3:
                v += 1
            low = v + 1
        if v == n:
            out.append(sorted(edges))
            return
        for w in range(max(low, v + 1), n):
            if degree[w] < 3 and (v, w) not in edges:
                edges.append((v, w))
                degree[v] += 1
                degree[w] += 1
                grow(v, w + 1)
                degree[v] -= 1
                degree[w] -= 1
                edges.pop()

    grow(1, 2)
    return out


def exhaustive_cubic(n):
    classes = Classes(n)
    for edges in labelled_cubic(n):
        if connected(n, edges):
            classes.add(edges)
    return classes.reps


def random_regular(n, d, rng):
    """A uniform random labelled d-regular simple graph (configuration model with rejection)."""
    while True:
        points = [v for v in range(n) for _ in range(d)]
        rng.shuffle(points)
        pairs = [tuple(sorted(points[i:i + 2])) for i in range(0, len(points), 2)]
        if any(a == b for a, b in pairs) or len(set(pairs)) < len(pairs):
            continue
        return sorted(pairs)


def sampled_cubic_classes(n, target, rng, extra, log):
    classes = Classes(n)
    draws = 0
    while len(classes.reps) < target:
        edges = random_regular(n, 3, rng)
        draws += 1
        if connected(n, edges):
            classes.add(edges)
        if draws % 20000 == 0:
            log(f"    sampler n={n}: {draws} draws, {len(classes.reps)} classes")
    reached = draws
    added_after = 0
    for _ in range(extra):
        edges = random_regular(n, 3, rng)
        if connected(n, edges) and classes.add(edges):
            added_after += 1
    return classes.reps, reached, added_after


def small_connected_graphs(n):
    pairs = list(combinations(range(n), 2))
    classes = Classes(n)
    for mask in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1]
        if len(edges) >= n - 1 and connected(n, edges):
            classes.add(edges)
    return classes.reps


def random_connected_gnp(n, p, rng):
    while True:
        edges = [(a, b) for a, b in combinations(range(n), 2) if rng.random() < p]
        if edges and connected(n, edges):
            return edges


# ---------------------------------------------------------------- widths (prediction side and observables)

def cut_mask(edges, members):
    return sum(1 << i for i, (a, b) in enumerate(edges) if ((members >> a) & 1) != ((members >> b) & 1))


def cutwidth_and_order(n, edges):
    width = {0: 0}
    choice = {}
    for members in range(1, 1 << n):
        size = bin(cut_mask(edges, members)).count("1")
        best = None
        for v in range(n):
            if (members >> v) & 1:
                w = width[members ^ (1 << v)]
                if best is None or w < best[0]:
                    best = (w, v)
        width[members] = max(size, best[0])
        choice[members] = best[1]
    order, members = [], (1 << n) - 1
    while members:
        v = choice[members]
        order.append(v)
        members ^= 1 << v
    return width[(1 << n) - 1], order[::-1]


def bottleneck(n, edges, step_cost, monotone=False):
    full = (1 << n) - 1
    best = {0: 0}
    heap = [(0, 0)]
    while heap:
        cost, members = heapq.heappop(heap)
        if members == full:
            return cost
        if cost > best[members]:
            continue
        for v in range(n):
            if monotone and (members >> v) & 1:
                continue
            nxt = members ^ (1 << v)
            new = max(cost, step_cost(members, v, nxt))
            if new < best.get(nxt, 1 << 30):
                best[nxt] = new
                heapq.heappush(heap, (new, nxt))
    return None


def widths(n, edges):
    stars = [sum(1 << i for i, e in enumerate(edges) if v in e) for v in range(n)]
    cache = {}

    def cm(members):
        if members not in cache:
            cache[members] = cut_mask(edges, members)
        return cache[members]

    def toggle(members, v, nxt):
        return bin(cm(members) | stars[v]).count("1")

    def cut_only(members, v, nxt):
        return bin(cm(nxt)).count("1")

    cw, order = cutwidth_and_order(n, edges)
    return {"cutwidth": cw, "order": order,
            "toggle_width": bottleneck(n, edges, toggle),
            "monotone_toggle_width": bottleneck(n, edges, toggle, monotone=True),
            "cut_game": bottleneck(n, edges, cut_only),
            "max_degree": max(len(a) for a in adjacency(n, edges))}


# ---------------------------------------------------------------- depth certificates (parity network, charge at vertex 0)

class Network:
    def __init__(self, n, edges, charge):
        self.n, self.edges, self.charge = n, edges, charge
        self.stars = [[i for i, e in enumerate(edges) if v in e] for v in range(n)]
        self.cache = {}

    def local(self, bag):
        if bag not in self.cache:
            members = set(bag)
            inside = [v for v in range(self.n) if set(self.stars[v]) <= members]
            position = {e: k for k, e in enumerate(bag)}
            self.cache[bag] = [f for f in product((0, 1), repeat=len(bag))
                               if all(sum(f[position[e]] for e in self.stars[v]) % 2 == self.charge[v] for v in inside)]
        return self.cache[bag]

    def equation(self, label):
        if label == "n:":
            return {"v:|": 1}, 1
        big_text, e_text, f_text = label[2:].split("|")
        big = tuple(int(t) for t in big_text.split(","))
        e = int(e_text)
        f = tuple(int(t) for t in f_text.split(",")) if f_text else ()
        small = tuple(x for x in big if x != e)
        at = big.index(e)
        form = Counter({var(small, f): 1})
        for g in self.local(big):
            if g[:at] + g[at + 1:] == f:
                form[var(big, g)] -= 1
        return dict(form), 0


def var(bag, f):
    return "v:" + ",".join(map(str, bag)) + "|" + ",".join(map(str, f))


def label(big, e, f):
    return f"m:{','.join(map(str, big))}|{e}|{','.join(map(str, f))}"


def marginal(net, small, big, g, scale, into):
    current, partial = tuple(small), [g]
    for e in [x for x in big if x not in small]:
        bigger = tuple(sorted(current + (e,)))
        at = bigger.index(e)
        nxt = []
        for h in partial:
            into[label(bigger, e, h)] = into.get(label(bigger, e, h), 0) + scale
            nxt += [f for f in net.local(bigger) if f[:at] + f[at + 1:] == h]
        current, partial = bigger, nxt


def cut_set(net, U):
    return {i for i, (a, b) in enumerate(net.edges) if (a in U) != (b in U)}


def sweep_certificate(net, order, skip=None):
    cert = {"n:": 1}
    t = 0
    U = set()
    for step, v in enumerate(order):
        before = tuple(sorted(cut_set(net, U)))
        bag = tuple(sorted(set(before) | set(net.stars[v])))
        U2 = U | {v}
        after = tuple(sorted(cut_set(net, U2)))
        t_next = (t + net.charge[v]) % 2
        if step != skip:
            for g in net.local(after):
                if sum(g) % 2 == t_next:
                    marginal(net, after, bag, g, 1, cert)
            for g in net.local(before):
                if sum(g) % 2 == t:
                    marginal(net, before, bag, g, -1, cert)
        t, U = t_next, U2
    return cert


def refutes(net, certificate):
    combined, constant = Counter(), 0
    for name, y in certificate.items():
        if y:
            form, c = net.equation(name)
            for v, a in form.items():
                combined[v] += y * a
            constant += y * c
    return all(a == 0 for a in combined.values()) and constant != 0


def fourier_spot_check(net, k, samples, rng):
    """Toggle relations at level k consistent (V not reachable); random equations hold on the Fourier solution."""
    n, full = net.n, (1 << net.n) - 1
    stars = [sum(1 << i for i in net.stars[v]) for v in range(n)]
    reach, todo = {0}, [0]
    while todo:
        members = todo.pop()
        cm = cut_mask(net.edges, members)
        for v in range(n):
            if bin(cm | stars[v]).count("1") <= k:
                nxt = members ^ (1 << v)
                if nxt not in reach:
                    reach.add(nxt)
                    todo.append(nxt)
    if full in reach:
        return False
    h = {}
    for members in reach:
        gamma = cut_mask(net.edges, members)
        sign = sum(net.charge[v] for v in range(n) if (members >> v) & 1) % 2
        h[gamma] = 1 - 2 * sign
    cuts = sorted({cut_mask(net.edges, members) for members in range(1 << (n - 1))})

    def z(bag, f):
        bag_mask = sum(1 << e for e in bag)
        total = 0
        for gamma in cuts:
            if gamma & ~bag_mask == 0 and gamma in h:
                parity = sum(f[j] for j, e in enumerate(bag) if (gamma >> e) & 1) % 2
                total += h[gamma] * (1 - 2 * parity)
        return Fraction(total, 2 ** len(bag))

    if z((), ()) != 1:
        return False
    for _ in range(samples):
        size = rng.randint(1, k)
        big = tuple(sorted(rng.sample(range(len(net.edges)), size)))
        e = rng.choice(big)
        small = tuple(x for x in big if x != e)
        f = rng.choice(net.local(small))
        at = big.index(e)
        if z(small, f) != sum(z(big, g) for g in net.local(big) if g[:at] + g[at + 1:] == f):
            return False
    return True


# ---------------------------------------------------------------- main

def main() -> int:
    started = time.time()
    rng = random.Random(SEED)
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    rows, certificates, lines = [], {}, []

    def log(message):
        print(message, flush=True)
        lines.append(message)

    def record(family, n, edges, **extra):
        w = widths(n, edges)
        row = {"part": "graph", "family": family, "vertices": n, "edges": [list(e) for e in edges], **w, **extra}
        rows.append(row)
        return row

    roster = []
    for n in (4, 6, 8, 10):
        for edges in exhaustive_cubic(n):
            roster.append(record("cubic", n, edges))
    log(f"[{time.time() - started:.0f}s] cubic graphs on 4-10 vertices: {len(roster)}")

    control_reps, control_draws, control_after = sampled_cubic_classes(10, 19, rng, 5000, log)
    exhaustive10 = [r for r in roster if r["vertices"] == 10]
    matched = all(any(isomorphic(10, rep, [tuple(e) for e in r["edges"]]) for r in exhaustive10) for rep in control_reps)
    sampler_control = len(control_reps) == 19 and control_after == 0 and matched
    log(f"[{time.time() - started:.0f}s] sampler control on 10 vertices: {len(control_reps)} classes after {control_draws} draws, "
        f"{control_after} more after 5000; all match exhaustive classes: {matched}")

    reps12, draws12, after12 = sampled_cubic_classes(12, PUBLISHED_CUBIC_12, rng, 20000, log)
    log(f"[{time.time() - started:.0f}s] 12 vertices: {len(reps12)} classes after {draws12} draws; {after12} new in 20000 more")
    depth_rows = []
    for index, edges in enumerate(reps12):
        row = record("cubic", 12, edges, sample_index=index)
        net = Network(12, edges, [1] + [0] * 11)
        cert = sweep_certificate(net, row["order"])
        biggest = max(len(name[2:].split("|")[0].split(",")) for name in cert if name.startswith("m:"))
        ok_sweep = refutes(net, cert)
        ok_fourier = fourier_spot_check(net, row["cutwidth"], 100, rng)
        certificates[f"cubic12|{index}"] = {"edges": edges, "order": row["order"], "sweep": cert}
        depth_rows.append({"index": index, "sweep_refutes": ok_sweep, "largest_bag": biggest,
                           "fourier_consistent_and_spot_checked": ok_fourier})
        row.update({"sweep_refutes_at_cw_plus_one": ok_sweep and biggest <= row["cutwidth"] + 1,
                    "fourier_consistent_at_cw": ok_fourier})
    log(f"[{time.time() - started:.0f}s] depth certificates on 12-vertex cubic graphs done")

    for n in (3, 4, 5, 6):
        graphs = small_connected_graphs(n)
        for edges in graphs:
            record("small", n, edges)
        log(f"[{time.time() - started:.0f}s] connected graphs on {n} vertices: {len(graphs)}")
    for n in (8, 10, 12):
        for _ in range(200):
            while True:
                edges = random_regular(n, 4, rng)
                if connected(n, edges):
                    break
            record("4-regular", n, edges)
    for n in (8, 9, 10):
        for _ in range(200):
            record("gnp", n, random_connected_gnp(n, 0.4, rng))
    log(f"[{time.time() - started:.0f}s] sampled graphs done")

    graphs = [r for r in rows if r["part"] == "graph" and r["vertices"] >= 3]
    sub = [r for r in graphs if r["max_degree"] <= 3]
    p1 = all(r["toggle_width"] == r["monotone_toggle_width"] == r["cutwidth"] + 1 for r in sub)
    p2 = all(r["cutwidth"] + 1 <= r["toggle_width"] <= r["monotone_toggle_width"] <= r["cutwidth"] + r["max_degree"] // 2
             for r in graphs)
    p3 = all(r["cut_game"] == r["cutwidth"] for r in graphs)
    p4 = all(r["toggle_width"] == r["monotone_toggle_width"] for r in graphs)
    twelve = [r for r in graphs if r["family"] == "cubic" and r["vertices"] == 12]
    p5 = len(twelve) == PUBLISHED_CUBIC_12 and all(r["sweep_refutes_at_cw_plus_one"] and r["fourier_consistent_at_cw"]
                                                   for r in twelve)
    edge_widths = widths(2, [(0, 1)])
    net0 = Network(12, reps12[0], [1] + [0] * 11)
    controls = {
        "sampler_recovers_the_19_on_10_vertices": sampler_control,
        "no_new_class_on_12_vertices_after_reaching_85": after12 == 0,
        "single_edge_has_tgw_equal_to_cw": edge_widths["toggle_width"] == edge_widths["cutwidth"],
        "cw_in_place_of_cw_plus_one_fails": not all(r["toggle_width"] == r["cutwidth"] for r in sub),
        "cw_plus_two_in_place_of_cw_plus_one_fails": not all(r["toggle_width"] == r["cutwidth"] + 2 for r in sub),
        "sweep_with_a_step_removed_fails": not refutes(net0, sweep_certificate(net0, widths(12, reps12[0])["order"], skip=5)),
    }
    gaps = Counter((r["family"], r["max_degree"], r["monotone_toggle_width"] - r["cutwidth"],
                    r["toggle_width"] - r["cutwidth"]) for r in graphs)
    result = {
        "experiment_id": "CUTWIDTH-DEPTH-20261020-001A-E001",
        "predictions": {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5},
        "signal": all((p1, p2, p3, p4, p5)) and all(controls.values()),
        "controls": controls,
        "counts": {"graphs": len(graphs), "max_degree_at_most_3": len(sub), "cubic_12": len(twelve),
                   "draws_to_reach_85": draws12, "families": dict(Counter(r["family"] for r in graphs))},
        "gaps": [{"family": f, "max_degree": d, "monotone_minus_cw": m, "toggle_minus_cw": t, "graphs": c}
                 for (f, d, m, t), c in sorted(gaps.items())],
        "cubic_12_widths": {f"cw={a},tgw={b}": c for (a, b), c in
                            sorted(Counter((r["cutwidth"], r["toggle_width"]) for r in twelve).items())},
        "wall_seconds": round(time.time() - started, 1),
    }
    with (ARTIFACT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    with gzip.open(ARTIFACT / "certificates.json.gz", "wt") as handle:
        json.dump(certificates, handle, sort_keys=True)
    (ARTIFACT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    log(json.dumps({"predictions": result["predictions"], "controls": controls, "counts": result["counts"],
                    "gaps": result["gaps"]}, indent=1))
    log("signal" if result["signal"] else "no signal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
