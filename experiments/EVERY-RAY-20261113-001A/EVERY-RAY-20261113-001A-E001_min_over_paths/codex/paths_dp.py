"""Frozen EVERY-RAY DP, including entry choices and carried-port state.

The plain interface is (F, Gf).  The optional extension (F, Gf, T) records
which child ports still hold a main port; only T=0 accepts as uncarried.
"""
from __future__ import annotations

from collections import Counter, deque
import gzip
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import signal
import threading
import time
import traceback

for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CENSUS_DIR = ROOT / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex"
CENSUS_RECORDS = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
_spec = importlib.util.spec_from_file_location("every_ray_reach_census", CENSUS_DIR / "reach_dp.py")
CENSUS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CENSUS)

Preparation = CENSUS.Preparation
Block = CENSUS.Block
Operation = CENSUS.Operation
FamilyDP = CENSUS.FamilyDP
L = CENSUS.L
GA = CENSUS.GA
INF = CENSUS.INF
NODE_CAP = CENSUS.NODE_CAP
FAMILY_SECONDS = CENSUS.FAMILY_SECONDS
BLOCK_CAP = CENSUS.BLOCK_CAP
MEMORY_BYTES = CENSUS.MEMORY_BYTES
FamilyLimit = CENSUS.FamilyLimit
MemoryLimit = CENSUS.MemoryLimit
rss_bytes = CENSUS.rss_bytes
subsets = CENSUS.subsets
recompute_layers = CENSUS.recompute_layers
_CHECK_MASK = (1 << 14) - 1


def load_census_records(path=CENSUS_RECORDS):
    """Load the authorized family archive, rejecting duplicate keys."""
    rows = {}
    with gzip.open(path, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["key"] in rows:
                raise ValueError("Duplicate census family key")
            rows[row["key"]] = row
    return rows


def self_call_count(key):
    """Count SELF calls in the same first holding definition used by census.

    No truth tables or limit computation are needed for population selection.
    Nonholding definitions are followed in the census's depth-first call order.
    """
    defs = json.loads(key) if isinstance(key, str) else key
    holding = {i for i, (_, _, calls) in enumerate(defs)
               if any(c == "SELF" for c, _ in calls)}

    def first(i):
        if i in holding:
            return i
        for c, _ in defs[i][2]:
            if c == "K":
                continue
            target = first(c)
            if target is not None:
                return target
        return None

    S = first(len(defs) - 1)
    return 0 if S is None else sum(c == "SELF" for c, _ in defs[S][2])


def is_eligible(key, census_row):
    return not str(census_row.get("class", "")).startswith(("S1 ", "S2 ", "S3 ")) and self_call_count(key) >= 2


def eligible_keys(records):
    items = records.items() if isinstance(records, dict) else ((r["key"], r) for r in records)
    return sorted(key for key, row in items if is_eligible(key, row))


def s4_free(prep):
    """Path-independent S4: every SELF argument is relevant, including TOP.

    Symbolic inlining keeps oversized blocks out of memory.  A Boolean marks
    an own distinction; all newly allocated inlined distinctions are own.
    """
    if prep.S is None or prep.own[prep.S] == 0:
        return False
    S = prep.S

    def scan(i, actual):
        _, own, calls = prep.u[i]
        env = list(actual) + [True] * own
        for c, args in calls:
            a = [env[x] for x in args]
            if c == "K":
                relevant = True
            elif c == "SELF" or c in prep.holding:
                target = i if c == "SELF" else c
                relevant = (i == S and c == "SELF") or not prep.G[target].all()
            else:
                if scan(c, a):
                    return True
                continue
            if relevant and any(a):
                return True
        return False

    return not scan(S, [False] * 3)


class PathFamilyDP:
    """Census blocks with one operation list per possible onward SELF call.

    A fixed ray selects an independent pair (entry_index, fixed_index).
    Omitting both permits every entry and every onward SELF call (A1/A5).
    """
    def __init__(self, prep, checkpoint=lambda: None, fixed_index=None, entry_index=None,
                 track_carried=False):
        main, S, entry, spine = prep.blocks("first")
        self.track_carried = track_carried
        self.flat_main, self.flat_S = main, S
        self.self_indices = [j for j, (c, _) in enumerate(S["calls"]) if c == prep.S]
        self.c = len(self.self_indices)
        self.entry_indices = [j for j, (c, _) in enumerate(main["calls"]) if c == prep.S]
        if fixed_index is not None:
            if not 0 <= fixed_index < self.c:
                raise ValueError("fixed SELF index is outside S")
        if entry_index is not None and not 0 <= entry_index < len(self.entry_indices):
            raise ValueError("fixed entry index is outside main")
        # A fixed_index with no explicit entry retains the corresponding census
        # ray convention for compatibility with existing focused comparisons.
        if entry_index is None and fixed_index is not None:
            entry_index = fixed_index if prep.main == prep.S else 0
        selected_entries = range(len(self.entry_indices)) if entry_index is None else (entry_index,)
        closing = Block(S, spine, prep.G, terminal=True)
        self.starts = {}
        self.start_blocks = {}
        for e in selected_entries:
            entry = self.entry_indices[e]
            first = Block(main, entry, prep.G)
            self.start_blocks[entry] = first
            T = sum(1 << j for j, a in enumerate(main["calls"][entry][1]) if a < main["k"])
            for W in subsets(tuple(range(main["V"])), 1):
                if not any(x < main["k"] for x in W):
                    continue
                F = first.start_image(W)
                Gf = 0
                for i in range(len(W)):
                    Gf |= first.start_image(W[:i] + W[i + 1:])
                node = (F, Gf, T) if track_carried else (F, Gf)
                self.starts[node] = min(self.starts.get(node, INF), len(W))
                checkpoint()
        own = tuple(range(3, S["V"]))
        self.middle_ops, self.close_ops, self.blocks_by_call = [], [], {}
        selected = range(self.c) if fixed_index is None else (fixed_index,)
        self.pass_through_calls = {i for i, j in enumerate(self.self_indices)
                                   if sorted(S["calls"][j][1]) == [0, 1, 2]}
        for call_index in selected:
            j = self.self_indices[call_index]
            middle = self.start_blocks[j] if prep.main == prep.S and j in self.start_blocks else Block(S, j, prep.G)
            self.blocks_by_call[call_index] = middle
            for W in subsets(own):
                op = Operation(middle, W)
                op.call_index, op.flat_call_index = call_index, j
                op.pass_through = call_index in self.pass_through_calls
                args = S["calls"][j][1]
                op.carried_map = tuple(sum(1 << p for p, a in enumerate(args)
                                          if a < 3 and (T >> a) & 1) for T in range(8))
                self.middle_ops.append(op)
                checkpoint()
        for W in subsets(own, 1):
            self.close_ops.append(Operation(closing, W))
            checkpoint()

    def close(self, node):
        node = node[:2]
        if node[1] & 1:
            return INF
        for op in self.close_ops:
            F, Gf = op.apply(node)
            if F & 1 and not Gf & 1:
                return op.cost
        return INF


def build_path_graph(ctx, result=None, checkpoint=lambda: None, cap=NODE_CAP):
    """BFS over every (SELF index, W) edge; retain parallel call labels.

    Returns graph, closes, zero_successors, indexed starts, edge labels, states.
    A zero successor is recorded for each selected SELF call, with ``None``
    marking an edge omitted by the cap.  No functional successor is assumed.
    """
    if result is None:
        result = {}
    states = list(ctx.starts)
    if len(states) > cap:
        raise ValueError("node cap is below the number of start states")
    index = {v: i for i, v in enumerate(states)}
    starts = {index[v]: cost for v, cost in ctx.starts.items()}
    graph, closes, zero_successors, labels = [], [], [], []
    hit_cap = False
    cursor = 0
    try:
        while cursor < len(states):
            result.update(nodes=len(states), expanded_nodes=cursor)
            checkpoint()
            edges, zero, call_labels = [], [], []
            for number, op in enumerate(ctx.middle_ops):
                state = states[cursor]
                target = op.apply(state[:2])
                if ctx.track_carried:
                    target = (*target, op.carried_map[state[2]])
                j = index.get(target)
                if j is None:
                    if len(states) >= cap:
                        hit_cap = True
                    else:
                        j = len(states)
                        index[target] = j
                        states.append(target)
                if j is not None:
                    edges.append((j, op.cost))
                    call_labels.append(op.call_index)
                if op.cost == 0:
                    zero.append(j)
                if number & 127 == 0:
                    checkpoint()
            graph.append(edges)
            labels.append(call_labels)
            closes.append(ctx.close(states[cursor]))
            zero_successors.append(tuple(zero))
            cursor += 1
    finally:
        result.update(nodes=len(states), expanded_nodes=len(graph))
    result.update(complete=not hit_cap, edges=sum(map(len, graph)))
    return graph, closes, zero_successors, starts, labels, states


def _components(adjacency, retained, checkpoint=lambda: None):
    """Iterative SCCs of the retained directed graph."""
    n = len(adjacency)
    reverse = [[] for _ in range(n)]
    work = 0
    for u in retained:
        for v in adjacency[u]:
            if v is not None and v in retained:
                reverse[v].append(u)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
    visited, order = set(), []
    for root in retained:
        if root in visited:
            continue
        visited.add(root)
        stack, offsets = [root], [0]
        while stack:
            u = stack[-1]
            at = offsets[-1]
            if at == len(adjacency[u]):
                order.append(u)
                stack.pop()
                offsets.pop()
            else:
                offsets[-1] += 1
                v = adjacency[u][at]
                if v is not None and v in retained and v not in visited:
                    visited.add(v)
                    stack.append(v)
                    offsets.append(0)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
    assigned, components = set(), []
    for root in reversed(order):
        if root in assigned:
            continue
        todo, component = [root], []
        assigned.add(root)
        while todo:
            u = todo.pop()
            component.append(u)
            for v in reverse[u]:
                if v not in assigned:
                    assigned.add(v)
                    todo.append(v)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        components.append(component)
    return components, reverse


def _cycle_witness(adjacency, component, checkpoint=lambda: None):
    """One explicit directed cycle from a cyclic SCC, without enumeration."""
    allowed = set(component)
    root = component[0]
    path, offsets, positions, done = [root], [0], {root: 0}, set()
    work = 0
    while path:
        u, at = path[-1], offsets[-1]
        if at == len(adjacency[u]):
            path.pop()
            offsets.pop()
            positions.pop(u)
            done.add(u)
        else:
            offsets[-1] += 1
            v = adjacency[u][at]
            if v in allowed:
                if v in positions:
                    return path[positions[v]:]
                if v not in done:
                    positions[v] = len(path)
                    path.append(v)
                    offsets.append(0)
        work += 1
        if work & _CHECK_MASK == 0:
            checkpoint()
    raise ValueError("Cyclic SCC has no cycle witness")


def productive_and_zero_cycles(graph, closes, zero_successors, checkpoint=lambda: None):
    reverse = [[] for _ in graph]
    work = 0
    for u, edges in enumerate(graph):
        for v, _ in edges:
            if 0 <= v < len(graph):
                reverse[v].append(u)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
    productive = {u for u, cost in enumerate(closes) if cost < INF}
    todo = deque(productive)
    while todo:
        for u in reverse[todo.popleft()]:
            if u not in productive:
                productive.add(u)
                todo.append(u)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
    zero = [tuple(v for v in row if v is not None and 0 <= v < len(graph)) for row in zero_successors]
    components, zero_reverse = _components(zero, productive, checkpoint)
    cyclic = [c for c in components if len(c) > 1 or c[0] in zero[c[0]]]
    cycles = [_cycle_witness(zero, c, checkpoint) for c in cyclic]
    return productive, cycles, cyclic, zero, zero_reverse


def exact_eventual_bound(graph, closes, starts, productive, cycles, checkpoint=lambda: None):
    """The referee's residue test with explicit branching-zero SCC witnesses.

    ``cycles`` contains one directed zero-cost cycle from each productive
    zero-cost SCC.  Their LCM P is a pumping period.  Testing visits to these
    chosen cycles is exact: a walk visiting any other zero-cycle vertex can
    make a zero-cost detour through the chosen cycle in its SCC and repeat
    that closed detour P times, preserving its original residue modulo P.
    Conversely, every bounded-cost sufficiently long accepting walk visits a
    zero-cost cycle.  Thus neither SCC branching nor unchosen cycles are lost.
    """
    cycles = [c for c in cycles if c and all(u in productive for u in c)]
    if not cycles:
        return dict(eventually_bounded=False, period=None, zero_cycle_lengths=[],
                    reason="no productive zero cycle", missing_residues=None)
    P = math.lcm(*(len(c) for c in cycles))
    if 2 * len(productive) * P > 8_000_000:
        return dict(eventually_bounded=None, period=P, reason="product size resource gate",
                    cycle_witnesses=cycles)
    zero_nodes = {u for c in cycles for u in c}
    visited, queue = {}, deque()
    for u, cost in starts.items():
        if u in productive:
            state = (u, 0, u in zero_nodes)
            if state not in visited:
                visited[state] = (0, cost)
                queue.append(state)
    representatives = {}
    work = 0
    while queue:
        state = queue.popleft()
        u, residue, seen = state
        length, cost = visited[state]
        if seen and closes[u] < INF and residue not in representatives:
            representatives[residue] = dict(middle_length=length, depth=length + 1,
                                            total_cost=cost + closes[u], final_node=u)
        for v, w in graph[u]:
            if v not in productive:
                continue
            target = (v, (residue + 1) % P, seen or v in zero_nodes)
            if target not in visited:
                visited[target] = (length + 1, cost + w)
                queue.append(target)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        checkpoint()
    missing = sorted(set(range(P)) - representatives.keys())
    return dict(eventually_bounded=not missing, period=P,
                zero_cycle_lengths=sorted(Counter(map(len, cycles)).items()),
                cycle_witnesses=cycles, residues_covered=sorted(representatives), missing_residues=missing,
                product_states=len(visited),
                depth_threshold=max((v["depth"] for v in representatives.values()), default=None) if not missing else None,
                uniform_cost_bound=max((v["total_cost"] for v in representatives.values()), default=None) if not missing else None,
                representatives=representatives)


def _bounded_all(closes, productive, zero, complete, checkpoint):
    accepting = {u for u in productive if closes[u] < INF}
    comps, _ = _components(zero, accepting, checkpoint)
    good = [c for c in comps if len(c) > 1 or c[0] in zero[c[0]]]
    reverse = [[] for _ in zero]
    for u in productive:
        for v in zero[u]:
            if v in productive:
                reverse[v].append(u)
    basin = {u for c in good for u in c}
    queue = deque(basin)
    while queue:
        for u in reverse[queue.popleft()]:
            if u not in basin:
                basin.add(u)
                queue.append(u)
        checkpoint()
    return dict(bounded_all=True if good else False if complete else None,
                bounded_good_cycles=len(good), bounded_good_starts=len(basin),
                bounded_bad_starts=len(productive - basin) if complete else 0,
                bounded_affected_starts=0 if complete else len(productive - basin))


def analyze_path_graph(graph, closes, zero_successors, starts, complete,
                       edge_labels=None, pass_through_calls=(), checkpoint=lambda: None):
    """Census exact Karp plus branching-zero boundedness and residue test."""
    size = len(graph)
    if len(closes) != size or len(zero_successors) != size:
        raise ValueError("Graph and closing/zero arrays differ in size")
    # An interrupted externally supplied prefix may retain targets belonging to
    # unexpanded states.  Their transitions and closings are unknown, not edges.
    out_of_range = any(not 0 <= v < size for row in graph for v, _ in row)
    if out_of_range:
        complete = False
        graph = [[(v, w) for v, w in row if 0 <= v < size] for row in graph]
        if edge_labels is not None:
            edge_labels = None  # Labels cannot be safely reindexed by inference.
    # GA is reused for trim/SCC/exact Karp only; its functional empty-successor
    # output is discarded and recomputed below on all zero-cost transitions.
    result = GA.analyze_graph(graph, closes, [None] * size, complete, checkpoint)
    result["complete"] = complete
    productive, cycles, zero_comps, zero, _ = productive_and_zero_cycles(
        graph, closes, zero_successors, checkpoint)
    result.update(_bounded_all(closes, productive, zero, complete, checkpoint))
    result["bounded_bad_cycles"] = max(0, len(zero_comps) - result["bounded_good_cycles"])
    result["bounded_missing_successors"] = sum(v is None for row in zero_successors for v in row)
    exact = exact_eventual_bound(graph, closes, starts, productive, cycles, checkpoint)
    result["exact_eventual_boundedness"] = exact
    for field in ("eventually_bounded", "period", "uniform_cost_bound", "missing_residues"):
        result[field] = exact.get(field)
    result["onset_depth"] = exact.get("depth_threshold")
    result["zero_cost_cyclic_sccs"] = len(zero_comps)
    result["zero_cost_cycle_witnesses"] = cycles
    pass_calls = set(pass_through_calls)
    if edge_labels is not None:
        component_for = {u: i for i, c in enumerate(zero_comps) for u in c}
        uses_pass = any(w == 0 and label in pass_calls and u in component_for
                        and component_for.get(v) == component_for[u]
                        for u, row in enumerate(graph)
                        for (v, w), label in zip(row, edge_labels[u]))
        result["zero_mean_cycle_uses_pass_through"] = True if uses_pass else False if complete else None
    else:
        result["zero_mean_cycle_uses_pass_through"] = None
    result["pass_through_zero_cycle"] = result["zero_mean_cycle_uses_pass_through"]
    return result


def classify(row):
    positive = row.get("bounded_all") is True or row.get("eventually_bounded") is True
    if positive:
        return "bounded"
    if row.get("status") in ("timeout", "error", "memory_limit", "aggregate_memory_limit", "block_size") or not row.get("complete"):
        return "unresolved"
    if row.get("trimmed_nodes") == 0:
        return "none at any depth"
    if row.get("cyclic_sccs") == 0:
        return "lost at large depths"
    if row.get("lambda_float") is not None and row["lambda_float"] > 0:
        return "grows"
    if row.get("lambda_float") == 0 and row.get("eventually_bounded") is False:
        return "mixed by residue"
    return "unresolved"


def first_ray_port_masks(prep, depths=30):
    """A9 port transport on the census first ray, without large inlining."""
    if prep.S is None:
        return [], None

    def first_entry(i, actual):
        _, own, calls = prep.u[i]
        env = list(actual) + [False] * own
        for c, args in calls:
            if c == "K":
                continue
            mapped = tuple(env[a] for a in args)
            if c == "SELF" or c in prep.holding:
                target = i if c == "SELF" else c
                if target == prep.S:
                    return sum(1 << j for j, value in enumerate(mapped) if value)
            else:
                found = first_entry(c, mapped)
                if found is not None:
                    return found
        return None

    T = first_entry(prep.main, [True] * prep.k)
    if T is None:
        return [], None
    args = next(args for c, args in prep.u[prep.S][2] if c == "SELF")
    masks = []
    for _ in range(max(depths, 16)):
        masks.append(T)
        T = sum(1 << j for j, a in enumerate(args) if a < 3 and (T >> a) & 1)
    return masks[:depths], bool(T)


def _carry(key, census_row, c):
    result = dict(census_row)
    result.update(key=key, c=c, first_ray_class=census_row.get("class"),
                  path_class=census_row.get("class"), L_path=list(census_row.get("L_ray", [])),
                  lambda_path=census_row.get("lambda"), lambda_path_float=census_row.get("lambda_float"),
                  census_status=census_row.get("status"), census_seconds=census_row.get("seconds"),
                  census_nodes=census_row.get("nodes"), carried=True, one_ray=c == 1,
                  seconds=0, nodes=0, expanded_nodes=0, status="one_ray" if c == 1 else "carried_settled",
                  mixed_path_needed=False if c == 1 else None,
                  fixed_index_status="one_ray" if c == 1 else "not_applicable_settled",
                  zero_mean_cycle_uses_pass_through=None,
                  pass_through_zero_cycle=None,
                  rescued_first_ray_none_lost=False, symmetry_inequivalent=False if c < 2 else None,
                  symmetry_status="one_ray" if c == 1 else "not_applicable_settled", ambiguities=[],
                  class_path_uncarried=None, class_uncarried=None, bounded_split=None,
                  first_ray_carried=None, L_path_uncarried=[])
    if c == 1 and not str(census_row.get("class", "")).startswith(("S1 ", "S2 ", "S3 ")):
        prep = Preparation(json.loads(key))
        masks, flag = first_ray_port_masks(prep)
        result["first_ray_carried"] = flag
        result["first_ray_port_masks"] = masks
        result["L_path_uncarried"] = [value if T == 0 else INF
                                         for value, T in zip(result["L_path"], masks)]
        cls = census_row.get("class")
        if flag:
            unc = "none at any depth"
        elif cls in ("grows", "bounded", "mixed by residue", "none at any depth", "S4 free own distinctions"):
            unc = cls
        elif cls == "lost at large depths" and any(v < INF for v in result["L_path_uncarried"]):
            unc = cls
        else:
            unc = "unresolved"
        result.update(class_path_uncarried=unc, class_uncarried=unc,
                      uncarried_evidence="fixed single ray: transport independent of members; after T becomes empty the accepting sequence is unchanged")
        if cls == "bounded":
            result["bounded_split"] = "bounded, uncarried" if unc == "bounded" else "bounded, carried only"
    if c == 1 and census_row.get("S") is not None and not str(census_row.get("class", "")).startswith(("S1 ", "S2 ", "S3 ")):
        calls = json.loads(key)[census_row["S"]][2]
        passthrough = any(name == "SELF" and sorted(args) == [0, 1, 2] for name, args in calls)
        if not passthrough or census_row.get("class") in ("grows", "lost at large depths", "none at any depth", "S4 free own distinctions"):
            result["zero_mean_cycle_uses_pass_through"] = False
        elif census_row.get("lambda_float") == 0 or census_row.get("bounded_all") is True or census_row.get("eventually_bounded") is True:
            result["zero_mean_cycle_uses_pass_through"] = True
        result["pass_through_zero_cycle"] = result["zero_mean_cycle_uses_pass_through"]
        result["pass_through_cycle_evidence"] = "single SELF call: every transition has that call label; census cycle/boundedness certificate"
    if census_row.get("class") == "S4 free own distinctions":
        result.update(census_class=census_row["class"], settled_case=census_row["class"],
                      path_class="none at any depth", class_path="none at any depth",
                      **{"class": "none at any depth"}, L_path=[INF] * 30,
                      L_path_uncarried=[INF] * 30, class_path_uncarried="none at any depth",
                      class_uncarried="none at any depth")
    ambiguous_entries = (c == 1 and result.get("first_ray_carried") is not None
            and census_row.get("class") != "S4 free own distinctions"
            and prep.targets[prep.main].get(prep.S, 0) > 1)
    if ambiguous_entries and result.get("main_block_size", BLOCK_CAP + 1) <= BLOCK_CAP:
        main = prep.flat(prep.main)
        ambiguous_entries = len({tuple(args) for target, args in main["calls"] if target == prep.S}) > 1
    if ambiguous_entries:
        # A1 permits every main entry, but the unchanged c=1 carry rule says
        # L_path=L_ray. G-reg exhibits different graphs for this intersection.
        # The hand-off explicitly forbids choosing an ambiguous convention.
        result.update(census_evidence=dict(census_row), census_class=census_row.get("class"), census_lambda=census_row.get("lambda"),
                      census_L_ray=list(census_row.get("L_ray", [])),
                      status="skipped_ambiguity", complete=False, one_ray_entry_ambiguity=True,
                      path_class="unresolved", class_path="unresolved", **{"class": "unresolved"},
                      L_path=[], lambda_path=None, lambda_path_float=None,
                      L_path_uncarried=[], class_path_uncarried="unresolved", class_uncarried="unresolved",
                      bounded_split=None, mixed_path_needed=None, fixed_index_status="skipped_ambiguity",
                      bounded_all=None, eventually_bounded=None, exact_eventual_boundedness=None,
                      zero_mean_cycle_uses_pass_through=None, pass_through_zero_cycle=None)
        result["lambda"] = result["lambda_float"] = None
        result["ambiguities"].append("A1 ranges over several main entries for c=1, while the unchanged one-ray carry rule and G-reg require the census first entry. Which rule governs these families? Path computation skipped; census evidence retained separately.")
    return result


def _fixed_rays(prep, result, checkpoint, node_cap):
    rows = []
    main = prep.flat(prep.main)
    entries = [j for j, (c, _) in enumerate(main["calls"]) if c == prep.S]
    pairs = [(e, i) for e in range(len(entries)) for i in range(result["c"])]
    result["fixed_index_pairs_total"] = len(pairs)
    for e, i in pairs:
        checkpoint()
        detail = dict(index=i, entry_index=e, nodes=0, expanded_nodes=0, complete=False, status="done")
        context = PathFamilyDP(prep, checkpoint, fixed_index=i, entry_index=e)
        graph, closes, zero, starts, labels, states = build_path_graph(context, detail, checkpoint, node_cap)
        pass_calls = context.pass_through_calls
        del context
        detail.update(analyze_path_graph(graph, closes, zero, starts, detail["complete"],
                                         labels, pass_calls, checkpoint))
        detail["class"] = classify(detail)
        rows.append({k: detail.get(k) for k in ("index", "entry_index", "status", "class", "nodes", "complete", "lambda",
                                               "bounded_all", "eventually_bounded")})
        result["fixed_index_rays"] = rows
        if detail["class"] == "bounded":
            result["mixed_path_needed"] = False
        del graph, closes, zero, starts, labels, states
        if result["mixed_path_needed"] is False:
            break  # A bounded pair decides the existential diagnostic.
    result["fixed_index_rays"] = rows
    if any(r.get("class") == "bounded" for r in rows):
        result["mixed_path_needed"] = False
    elif len(rows) == len(pairs) and all(r.get("class") not in (None, "unresolved") for r in rows):
        result["mixed_path_needed"] = True
    else:
        result["mixed_path_needed"] = None
    result["fixed_index_status"] = "bounded_pair_found" if result["mixed_path_needed"] is False else "done"


def compute_family(key, census_row=None, seconds=FAMILY_SECONDS, node_cap=NODE_CAP,
                   force_dp=False, check_fixed_rays=True, track_carried=True, values_only=False):
    """Compute one capped family; failures never become growth verdicts."""
    start = time.monotonic()
    c = self_call_count(key)
    if census_row is not None and not force_dp and (c == 1 or str(census_row.get("class", "")).startswith(("S1 ", "S2 ", "S3 "))):
        return _carry(key, census_row, c)
    result = dict(key=key, c=c, first_ray_class=None if census_row is None else census_row.get("class"),
                  nodes=0, expanded_nodes=0, complete=False, L_path=[], seconds=0,
                  status="running", stage="usual_limit", carried=False, one_ray=c == 1,
                  lambda_path=None, lambda_path_float=None, bounded_all=None,
                  eventually_bounded=None, mixed_path_needed=False if c == 1 else None,
                  fixed_index_rays=[], fixed_index_status="not_needed", ambiguities=[],
                  zero_mean_cycle_uses_pass_through=None, symmetry_inequivalent=None,
                  pass_through_zero_cycle=None,
                  symmetry_status="not_computed", rescued_first_ray_none_lost=False,
                  class_path_uncarried="unresolved", class_uncarried="unresolved",
                  bounded_split=None, first_ray_carried=None, L_path_uncarried=[],
                  **{"lambda": None, "lambda_float": None})
    peak, checked = rss_bytes(), start
    stop_guard = threading.Event()
    guard_thread = None

    def checkpoint(force=False):
        nonlocal peak, checked
        now = time.monotonic()
        if now - start >= seconds:
            raise FamilyLimit
        if force or now - checked >= .05:
            checked = now
            peak = max(peak, rss_bytes())
            if peak > MEMORY_BYTES:
                raise MemoryLimit("worker RSS passed 3 GB")

    def alarm(*_):
        raise FamilyLimit

    def memory_alarm(signum, _):
        raise MemoryLimit("worker RSS passed 3 GB" if signum == signal.SIGUSR2 else "aggregate own-run RSS passed 7.5 GB")

    def guard():
        nonlocal peak
        while not stop_guard.wait(.05):
            peak = max(peak, rss_bytes())
            if peak > MEMORY_BYTES:
                os.kill(os.getpid(), signal.SIGUSR2)
                return

    old_alarm = signal.signal(signal.SIGALRM, alarm)
    old_mem = signal.signal(signal.SIGUSR1, memory_alarm)
    old_own = signal.signal(signal.SIGUSR2, memory_alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        checkpoint(True)
        prep = Preparation(json.loads(key))
        result.update(prep.info())
        masks, flag = first_ray_port_masks(prep)
        result.update(first_ray_carried=flag, first_ray_port_masks=masks)
        cls = CENSUS.settled(prep)
        if cls and not force_dp:
            result.update(status="settled", class_path_uncarried=cls, class_uncarried=cls, **{"class": cls})
            return result
        if prep.S is None:
            result.update(status="settled", **{"class": "S2 no copy"})
            return result
        own_self = [tuple(args) for target, args in prep.u[prep.S][2] if target == "SELF"]
        result["literal_duplicate_self_calls"] = len(own_self) - len(set(own_self))
        result["pass_through_self_calls"] = [i for i, args in enumerate(own_self) if sorted(args) == [0, 1, 2]]
        if not force_dp and s4_free(prep):
            result.update(status="settled", settled_case="S4 free own distinctions",
                          class_path_uncarried="none at any depth", class_uncarried="none at any depth",
                          L_path=[INF] * 30, L_path_uncarried=[INF] * 30,
                          **{"class": "none at any depth"})
            return result
        if result["main_block_size"] > BLOCK_CAP or result["s_block_size"] > BLOCK_CAP:
            result.update(status="block_size", **{"class": "unresolved"})
            return result
        guard_thread = threading.Thread(target=guard, daemon=True)
        guard_thread.start()
        result["stage"] = "block_tables"
        ctx = PathFamilyDP(prep, checkpoint, track_carried=track_carried)
        from call_symmetry import diagnostics
        result.update(diagnostics(prep, ctx.flat_S))
        result["port_transport_extended"] = track_carried
        result["stage"] = "reachable_graph"
        graph, closes, zero, starts, labels, states = build_path_graph(ctx, result, checkpoint, node_cap)
        pass_calls = ctx.pass_through_calls
        del ctx
        result["stage"] = "min_plus_layers"
        result["L_path"] = recompute_layers(graph, closes, starts, 30, checkpoint)
        if values_only:
            result.update(status="finite_layers", stage="finite_layers_finished",
                          layer_values_are_upper_bounds=not result["complete"],
                          **{"class": "unresolved"})
            return result
        result["stage"] = "trim_scc_karp_exact_bound"
        result.update(analyze_path_graph(graph, closes, zero, starts, result["complete"], labels, pass_calls, checkpoint))
        result["status"] = "done"
        result["class"] = classify(result)
        if track_carried:
            result["stage"] = "uncarried_min_plus_layers"
            unc_closes = [cost if state[2] == 0 else INF for state, cost in zip(states, closes)]
            result["L_path_uncarried"] = recompute_layers(graph, unc_closes, starts, 30, checkpoint)
            result["stage"] = "uncarried_trim_scc_karp_exact_bound"
            unc = dict(status="done", complete=result["complete"])
            unc.update(analyze_path_graph(graph, unc_closes, zero, starts, result["complete"], labels, pass_calls, checkpoint))
            unc["class"] = classify(unc)
            result.update(uncarried_result=unc, class_path_uncarried=unc["class"], class_uncarried=unc["class"])
        del graph, closes, zero, starts, labels, states
        if result["class"] == "bounded" and c >= 2 and check_fixed_rays:
            result["stage"] = "fixed_index_rays"
            _fixed_rays(prep, result, checkpoint, node_cap)
        elif result["class"] == "bounded" and c >= 2:
            result["fixed_index_status"] = "not_requested"
        result["stage"] = "finished"
    except FamilyLimit:
        # Thread fix (2026-11-13, after the sample's B stratum crashed at 25 of 100): the checkpoint's own time test can raise
        # FamilyLimit just before the armed timer fires, so the alarm then escaped this handler. Ignore it first; no result changes.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
        signal.setitimer(signal.ITIMER_REAL, 0)
        result.update(status="timeout", **{"class": classify(dict(result, status="timeout"))})
        if result.get("stage") == "fixed_index_rays":
            result["fixed_index_status"] = "timeout"
    except (MemoryLimit, MemoryError) as exc:
        status = "aggregate_memory_limit" if "aggregate" in str(exc) else "memory_limit"
        result.update(status=status, error=str(exc), **{"class": classify(dict(result, status=status))})
    except Exception as exc:
        result.update(status="error", error=repr(exc), traceback=traceback.format_exc(),
                      **{"class": classify(dict(result, status="error"))})
    finally:
        # Block before the first handler mutation: an alarm arriving during
        # that mutation previously escaped this finally block. A signal that
        # wins the first block attempt is consumed by its handler, then retried.
        cleanup_signals = {signal.SIGALRM, signal.SIGUSR1, signal.SIGUSR2}
        while True:
            try:
                previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
                break
            except (FamilyLimit, MemoryLimit):
                continue
        while True:
            try:
                signal.pthread_sigmask(signal.SIG_BLOCK, cleanup_signals)
                for sig in cleanup_signals:
                    signal.signal(sig, signal.SIG_IGN)
                break
            except (FamilyLimit, MemoryLimit):
                continue
        signal.setitimer(signal.ITIMER_REAL, 0)
        stop_guard.set()
        if guard_thread is not None:
            guard_thread.join()
        # Pending guard signals are discarded under IGN before old handlers
        # are restored. The timer and this family's guard have both stopped.
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        signal.signal(signal.SIGALRM, old_alarm)
        signal.signal(signal.SIGUSR1, old_mem)
        signal.signal(signal.SIGUSR2, old_own)
        result["seconds"] = round(time.monotonic() - start, 6)
        result["peak_rss_bytes"] = max(peak, rss_bytes())
        result["process_peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if result["peak_rss_bytes"] > MEMORY_BYTES:
            result["memory_cap_exceeded"] = True
            if result["status"] in ("done", "settled"):
                result.update(status="memory_limit", error="worker RSS passed 3 GB")
                result["class"] = classify(result)
        result["path_class"] = result.get("class", "unresolved")
        result["lambda_path"] = result.get("lambda")
        result["lambda_path_float"] = result.get("lambda_float")
        result["class_path"] = result["path_class"]
        if result["path_class"] == "bounded":
            result["bounded_split"] = ("bounded, uncarried" if result.get("class_path_uncarried") == "bounded"
                                       else "bounded, carried only")
        result["rescued_first_ray_none_lost"] = (result["first_ray_class"] in ("none at any depth", "lost at large depths")
                                                    and result.get("class") in ("grows", "bounded"))
    return result
