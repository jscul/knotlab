"""Reach census: exact relational block maps; no state quotient is taken.

Finite sets of interface masks are encoded as 256-bit integers. Forgetting a
member uses the *full* table for the subset with that member removed.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
from pathlib import Path
import resource
import signal
import threading
import time
import traceback
from collections import deque

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INF = 10**9
NODE_CAP = 300_000
FAMILY_SECONDS = 300
BLOCK_CAP = 12
MEMORY_BYTES = 3_000_000_000
LS_PATH = ROOT / "experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py"
BD_PATH = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
PR_DIR = ROOT / "experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex"
REF_PATH = ROOT / "research/PROVED-RATE-20261113-001/referee-R1/codex/recompute.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LS = load_module("reach_input_ls", LS_PATH)
L = LS.L
GA = load_module("reach_input_graph", PR_DIR / "graph_algorithms.py")
REF = load_module("reach_input_referee", REF_PATH)


def canonical(defs):
    return json.dumps(defs, separators=(",", ":"), ensure_ascii=True)


def normalized(defs):
    return [(k, l, [(c, tuple(a)) for c, a in calls]) for k, l, calls in defs]


def members(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def rss_bytes(pid=None):
    try:
        return int(Path(f"/proc/{pid or 'self'}/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (FileNotFoundError, ProcessLookupError):
        return 0


class FamilyLimit(Exception):
    pass


class MemoryLimit(Exception):
    pass


class Preparation:
    """Usual definitions, exact inlining counts, then bounded materialization."""
    def __init__(self, defs):
        self.defs = normalized(defs)
        self.u, self.passes = LS.usual(self.defs)
        self.holding = {i for i, (_, _, calls) in enumerate(self.u)
                        if any(c == "SELF" for c, _ in calls)}
        _, _, self.G = L.depth_sequence(self.u, L.TOP)
        self.alive = bool(L.relations(self.u, self.G)[-1].any())
        self.main = len(self.u) - 1
        self.own = []
        self.targets = []
        for i, (_, own, calls) in enumerate(self.u):
            counts = {}
            for c, _ in calls:
                if c == "K":
                    continue
                if c == "SELF" or c in self.holding:
                    t = i if c == "SELF" else c
                    counts[t] = counts.get(t, 0) + 1
                else:
                    own += self.own[c]
                    for t, n in self.targets[c].items():
                        counts[t] = counts.get(t, 0) + n
            self.own.append(own)
            self.targets.append(counts)
        self.S = self.main if self.main in self.holding else self.first_holding(self.main)
        self.k = self.u[self.main][0]

    def first_holding(self, i):
        for c, _ in self.u[i][2]:
            if c == "K":
                continue
            if c == "SELF":
                return i
            if c in self.holding:
                return c
            first = self.first_holding(c)
            if first is not None:
                return first
        return None

    def flat(self, i):
        k = self.u[i][0]
        next_id = k
        calls = []

        def inline(j, actual):
            nonlocal next_id
            _, l, body = self.u[j]
            env = list(actual) + list(range(next_id, next_id + l))
            next_id += l
            for c, args in body:
                a = tuple(env[x] for x in args)
                if c == "K":
                    calls.append(("K", a))
                elif c == "SELF" or c in self.holding:
                    calls.append((j if c == "SELF" else c, a))
                else:
                    inline(c, a)

        inline(i, tuple(range(k)))
        assert next_id == k + self.own[i]
        return dict(k=k, V=next_id, calls=calls)

    def info(self):
        S = self.S
        return dict(n_defs=len(self.u), k_main=self.k, main_own=self.own[self.main],
                    s_own=None if S is None else self.own[S], S=S,
                    usual_limit_alive=self.alive, main_block_size=self.k+self.own[self.main],
                    s_block_size=None if S is None else 3+self.own[S],
                    alt_differs=False if S is None else
                    (self.targets[self.main].get(S, 0) > 1 or self.targets[S].get(S, 0) > 1))

    def blocks(self, ray="first"):
        main = self.flat(self.main)
        S = self.flat(self.S)
        entry = [j for j, (c, _) in enumerate(main["calls"]) if c == self.S]
        spine = [j for j, (c, _) in enumerate(S["calls"]) if c == self.S]
        at = 0 if ray == "first" else -1
        return main, S, entry[at], spine[at]


def settled(prep, S=None, ray_index=None):
    if not prep.alive:
        return "S1 limit dead"
    if prep.S is None:
        return "S2 no copy"
    if prep.own[prep.S] == 0:
        return "S3 no own distinctions"
    if S is not None:
        used = set()
        for j, (c, args) in enumerate(S["calls"]):
            if c == "K" or j == ray_index or not prep.G[c].all():
                used.update(args)
        if not any(v >= 3 for v in used):
            return "S4 free own distinctions"
    return None


class Block:
    def __init__(self, flat, ray_index, G, terminal=False):
        self.k, self.V = flat["k"], flat["V"]
        self.ray = flat["calls"][ray_index][1]
        assignments = np.arange(1 << self.V, dtype=np.int64)
        ok = np.ones(len(assignments), bool)
        for j, (c, args) in enumerate(flat["calls"]):
            if j == ray_index and not terminal:
                continue
            values = sum(((assignments >> x) & 1) << b for b, x in enumerate(args))
            ok &= (L.NAE if c == "K" else G[c])[values]
        self.allowed = assignments[ok]
        self.incoming = self.allowed & 7
        self.outgoing = np.zeros(len(self.allowed), dtype=np.int64) if terminal else sum(
            ((self.allowed >> x) & 1) << b for b, x in enumerate(self.ray))
        self.raw = {}
        self.compiled = {}
        self.start_cache = {}

    def table(self, W):
        if W not in self.raw:
            projection = np.zeros(len(self.allowed), dtype=np.int64)
            for b, x in enumerate(W):
                projection |= ((self.allowed >> x) & 1) << b
            table = np.zeros((1 << len(W), 8), dtype=np.uint8)
            np.bitwise_or.at(table, (projection, self.incoming), (1 << self.outgoing).astype(np.uint8))
            self.raw[W] = np.unique(table, axis=0)
        return self.raw[W]

    def start_image(self, W):
        if W not in self.start_cache:
            image = np.bitwise_or.reduce(self.table(W), axis=1)
            self.start_cache[W] = sum(1 << int(v) for v in np.unique(image))
        return self.start_cache[W]

    def compile_full(self, W):
        if W not in self.compiled:
            raw = self.table(W)
            images = np.zeros((len(raw), 256), dtype=np.uint8)
            for b in range(8):
                width = 1 << b
                images[:, width:2*width] = images[:, :width] | raw[:, b:b+1]
            full = tuple(sum(1 << int(v) for v in np.unique(images[:, r])) for r in range(256))
            self.compiled[W] = full
        return self.compiled[W]


class Operation:
    def __init__(self, block, W):
        self.W = W
        self.cost = len(W)
        self.full = block.compile_full(W)
        forgot = [block.compile_full(W[:i]+W[i+1:]) for i in range(len(W))]
        self.forgotten = tuple(0 for _ in range(256))
        if forgot:
            self.forgotten = tuple(__import__("functools").reduce(int.__or__, ts) for ts in zip(*forgot))
        self.fc, self.gc = {}, {}

    @staticmethod
    def image(state, table, cache):
        v = cache.get(state)
        if v is None:
            v = 0
            for r in members(state):
                v |= table[r]
            if len(cache) >= 2048:
                cache.clear()
            cache[state] = v
        return v

    def apply(self, state):
        F, Gf = state
        return (self.image(F, self.full, self.fc),
                self.image(Gf, self.full, self.fc) | self.image(F, self.forgotten, self.gc))


def subsets(items, minimum=0):
    return (W for n in range(minimum, len(items)+1) for W in itertools.combinations(items, n))


class FamilyDP:
    def __init__(self, prep, ray="first", checkpoint=lambda: None):
        main, S, entry, spine = prep.blocks(ray)
        first = Block(main, entry, prep.G)
        middle = first if prep.main == prep.S and entry == spine else Block(S, spine, prep.G)
        closing = Block(S, spine, prep.G, terminal=True)
        self.starts = {}
        for W in subsets(tuple(range(main["V"])), 1):
            if not any(x < main["k"] for x in W):
                continue
            F = first.start_image(W)
            Gf = 0
            for i in range(len(W)):
                Gf |= first.start_image(W[:i]+W[i+1:])
            node = (F, Gf)
            self.starts[node] = min(self.starts.get(node, INF), len(W))
            checkpoint()
        own = tuple(range(3, S["V"]))
        self.middle_ops, self.close_ops = [], []
        for W in subsets(own):
            self.middle_ops.append(Operation(middle, W))
            if W:
                self.close_ops.append(Operation(closing, W))
            checkpoint()

    def close(self, node):
        if node[1] & 1:
            return INF
        for op in self.close_ops:
            F, Gf = op.apply(node)
            if F & 1 and not Gf & 1:
                return op.cost
        return INF


def build_graph(ctx, result, checkpoint, cap=NODE_CAP):
    nodes = list(ctx.starts)
    index = {v: i for i, v in enumerate(nodes)}
    starts = {index[v]: cost for v, cost in ctx.starts.items()}
    graph, closes, empty = [], [], []
    hit_cap = len(nodes) >= cap
    cursor = 0
    try:
        while cursor < len(nodes):
            result["nodes"] = len(nodes)
            result["expanded_nodes"] = cursor
            checkpoint()
            edges = []
            empty_successor = None
            for op in ctx.middle_ops:
                target = op.apply(nodes[cursor])
                j = index.get(target)
                if j is None:
                    if len(nodes) >= cap:
                        hit_cap = True
                        continue
                    j = len(nodes)
                    index[target] = j
                    nodes.append(target)
                edges.append((j, op.cost))
                if op.cost == 0:
                    empty_successor = j
            graph.append(edges)
            closes.append(ctx.close(nodes[cursor]))
            empty.append(empty_successor)
            cursor += 1
    finally:
        result.update(nodes=len(nodes), expanded_nodes=len(graph))
    result.update(complete=not hit_cap and len(nodes) < cap, edges=sum(map(len, graph)))
    return graph, closes, empty, starts


def recompute_layers(graph, closes, starts, depths=30, checkpoint=lambda: None):
    layer, values = dict(starts), []
    for _ in range(depths):
        values.append(min((cost+closes[u] for u, cost in layer.items() if closes[u] < INF), default=INF))
        nxt = {}
        for u, cost in layer.items():
            for v, w in graph[u]:
                if cost+w < nxt.get(v, INF):
                    nxt[v] = cost+w
            checkpoint()
        layer = nxt
    return values


def productive_and_cycles(graph, closes, empty):
    reverse = [[] for _ in graph]
    for u, edges in enumerate(graph):
        for v, _ in edges:
            reverse[v].append(u)
    productive = {u for u, c in enumerate(closes) if c < INF}
    queue = deque(productive)
    while queue:
        for u in reverse[queue.popleft()]:
            if u not in productive:
                productive.add(u)
                queue.append(u)
    done, cycles = set(), []
    for root in range(len(graph)):
        if root in done:
            continue
        trace, positions = [], {}
        u = root
        while u is not None and u not in done and u not in positions:
            positions[u] = len(trace)
            trace.append(u)
            u = empty[u]
        if u in positions:
            cycles.append(trace[positions[u]:])
        done.update(trace)
    return productive, cycles


def classify(row):
    if row["status"] in ("timeout", "error", "memory_limit", "aggregate_memory_limit", "block_size"):
        return "unresolved"
    positive = row.get("bounded_all") is True or row.get("eventually_bounded") is True
    if not row.get("complete"):
        return "bounded" if positive else "unresolved"
    if row.get("lambda_float") == 0 and row.get("exact_eventual_boundedness", {}).get("reason") == "product size resource gate":
        return "unresolved"
    if row.get("trimmed_nodes") == 0:
        return "none at any depth"
    if row.get("cyclic_sccs") == 0:
        return "lost at large depths"
    if positive:
        return "bounded"
    if row.get("lambda_float", 0) > 0:
        return "grows"
    if row.get("lambda_float") == 0 and row.get("eventually_bounded") is False:
        return "mixed by residue"
    return "unresolved"


def compute_family(key, ray="first", force_dp=False, seconds=FAMILY_SECONDS, node_cap=NODE_CAP):
    start = time.monotonic()
    result = dict(key=key, ray=ray, nodes=0, expanded_nodes=0, complete=False,
                  n_defs=None, k_main=None, main_own=None, s_own=None,
                  usual_limit_alive=None, main_block_size=None, s_block_size=None,
                  S=None, alt_differs=None,
                  trimmed_nodes=None, bounded_all=None, eventually_bounded=None,
                  period=None, onset_depth=None, uniform_cost_bound=None, missing_residues=None,
                  L_ray=[], seconds=0, status="running", stage="usual_limit",
                  **{"lambda": None, "lambda_float": None})
    peak = rss_bytes()
    checked = start
    stop_guard = threading.Event()
    guard_thread = None

    def checkpoint(force=False):
        nonlocal peak, checked
        now = time.monotonic()
        if now-start >= seconds:
            raise FamilyLimit
        if force or now-checked >= .05:
            checked = now
            peak = max(peak, rss_bytes())
            if peak > MEMORY_BYTES:
                raise MemoryLimit("worker RSS passed 3 GB")

    def alarm(signum, frame):
        raise FamilyLimit

    def memory_alarm(signum, frame):
        raise MemoryLimit("worker RSS passed 3 GB" if signum == signal.SIGUSR2 else "aggregate own-run RSS passed 7.5 GB")

    def memory_guard():
        nonlocal peak
        while not stop_guard.wait(.05):
            peak = max(peak, rss_bytes())
            if peak > MEMORY_BYTES:
                os.kill(os.getpid(), signal.SIGUSR2)
                return

    old_alarm = signal.signal(signal.SIGALRM, alarm)
    old_mem = signal.signal(signal.SIGUSR1, memory_alarm)
    old_own_mem = signal.signal(signal.SIGUSR2, memory_alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        checkpoint(True)
        definitions = json.loads(key)
        result.update(n_defs=len(definitions), k_main=definitions[-1][0])
        prep = Preparation(definitions)
        result.update(prep.info())
        cls = settled(prep)
        if cls and not force_dp:
            result.update(status="settled", **{"class": cls})
            return result
        # S4 uses only which distinctions occur; do not materialize an oversized
        # block. Its exact dependency set is gathered by symbolic inlining below.
        if not force_dp and s4_free(prep, ray):
            result.update(status="settled", **{"class": "S4 free own distinctions"})
            return result
        if result["main_block_size"] > BLOCK_CAP or result["s_block_size"] > BLOCK_CAP:
            result.update(status="block_size", **{"class": "unresolved"})
            return result
        guard_thread = threading.Thread(target=memory_guard, daemon=True)
        guard_thread.start()
        result["stage"] = "block_tables"
        ctx = FamilyDP(prep, ray, checkpoint)
        result["stage"] = "reachable_graph"
        graph, closes, empty, starts = build_graph(ctx, result, checkpoint, node_cap)
        del ctx
        result["stage"] = "min_plus_layers"
        result["L_ray"] = recompute_layers(graph, closes, starts, 30, checkpoint)
        result["stage"] = "trim_scc_karp_bounded"
        result.update(GA.analyze_graph(graph, closes, empty, result["complete"], checkpoint))
        result["stage"] = "exact_eventual_bound"
        productive, cycles = productive_and_cycles(graph, closes, empty)
        exact = REF.exact_eventual_bound(graph, closes, starts, productive, cycles)
        checkpoint(True)
        result["exact_eventual_boundedness"] = exact
        for field in ("eventually_bounded", "period", "uniform_cost_bound", "missing_residues"):
            result[field] = exact.get(field)
        result["onset_depth"] = exact.get("depth_threshold")
        result["status"] = "done"
        result["class"] = classify(result)
    except FamilyLimit:
        result.update(status="timeout", **{"class": "unresolved"})
    except (MemoryLimit, MemoryError) as exc:
        result.update(status="aggregate_memory_limit" if "aggregate" in str(exc) else "memory_limit",
                      error=str(exc), **{"class": "unresolved"})
    except Exception as exc:
        result.update(status="error", error=repr(exc), traceback=traceback.format_exc(), **{"class": "unresolved"})
    finally:
        # Thread fix (2026-11-13, after the full run crashed at 110,262 families): the alarm can fire while it is being
        # disarmed, after the family has finished; ignore it here instead of killing the worker. No result is changed.
        try:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            signal.setitimer(signal.ITIMER_REAL, 0)
        except FamilyLimit:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            signal.setitimer(signal.ITIMER_REAL, 0)
        stop_guard.set()
        if guard_thread is not None:
            guard_thread.join()
        signal.signal(signal.SIGALRM, old_alarm)
        signal.signal(signal.SIGUSR1, old_mem)
        signal.signal(signal.SIGUSR2, old_own_mem)
        result["seconds"] = round(time.monotonic()-start, 6)
        result["peak_rss_bytes"] = max(peak, rss_bytes())
        result["process_peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if result["peak_rss_bytes"] > MEMORY_BYTES:
            result["memory_cap_exceeded"] = True
            if result["status"] in ("done", "settled"):
                result.update(status="memory_limit", error="worker RSS passed 3 GB",
                              **{"class":"unresolved"})
    return result


def s4_free(prep, ray="first"):
    """Exact S4 without building large inlined bodies.

    To test whether *any* own distinction participates it suffices to carry a
    port/own Boolean through inlining. All newly allocated distinctions are own.
    First/last SELF of S is already a literal call in S (earlier callees cannot
    call their later caller); it cannot arise inside an inlined earlier body.
    """
    if prep.S is None or prep.own[prep.S] == 0:
        return False
    S = prep.S
    self_positions = [j for j, (c, _) in enumerate(prep.u[S][2]) if c == "SELF"]
    selected = self_positions[0 if ray == "first" else -1]

    def scan(i, actual):
        _, own, calls = prep.u[i]
        env = list(actual) + [True]*own
        for j, (c, args) in enumerate(calls):
            a = [env[x] for x in args]
            if c == "K":
                relevant = True
            elif c == "SELF" or c in prep.holding:
                target = i if c == "SELF" else c
                relevant = (i == S and c == "SELF" and j == selected) or not prep.G[target].all()
            else:
                if scan(c, a):
                    return True
                continue
            if relevant and any(a):
                return True
        return False

    return not scan(S, [False]*3)
