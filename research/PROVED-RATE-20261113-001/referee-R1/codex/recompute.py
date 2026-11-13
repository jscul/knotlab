"""Fresh referee reconstruction, authored from the frozen spec and BOND-DEPTH mathematics.

Scope: epic PROVED-RATE-20261113-001, referee-R1. No producer code is read/imported.
Question: do independent reachable graphs, exact rates, gates and boundedness agree?
Inputs: the explicitly permitted census.py (ONLY its family enumerator), frozen spec,
        original BOND-DEPTH L records, published aggregate rate rows.
Forbidden: the study's entire E001_cycle_mean/codex subtree, including batch logs.
Representation: F and G are 256-bit integers, not the producer's frozensets. Block
truth tables and the greatest fixed point are recomputed by assignment enumeration.
Outputs: one exact row per selected complete family, all under this script's directory.
Selection: 40 smallest complete plus 10 smallest in four strata, union all 46 flat
zero-only families. Extra cases may be selected explicitly and reported separately.
Controls: independent simple-cycle enumeration on small synthetic weighted graphs;
          direct set-semantics comparisons and positive/negative residue controls.
Limits: one Python process, 7 GiB address-space cap, 540 seconds per family,
        2,000,000 graph nodes. A resource failure is retained, never treated as agreement.
Nonclaims: no theorem from finite depth fitting; no true least-bond growth, topology,
           SAT/complexity result, publication or repository lifecycle change.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import random
import resource
import signal
import sys
import time

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = Path(__file__).resolve().parent
BD = ROOT / 'experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py'
RECORDS = ROOT / 'artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl'
RATES = ROOT / 'artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl'
INF = 10 ** 9


def dump(path, value):
    path = Path(path)
    assert path.resolve().is_relative_to(HERE)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def load_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def bits(mask):
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask ^= b


def subsets(items, minimum=0):
    return [c for n in range(minimum, len(items) + 1) for c in itertools.combinations(items, n)]


def family_definitions():
    # This is the sole imported scientific helper. Never call BD.run_family, its
    # table helpers, depth_sequence, or any study implementation.
    spec = importlib.util.spec_from_file_location('permitted_bd_enumerator', BD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(module.families_one_def())


class Operation:
    """A block operation, constructed as explicit relational images."""

    def __init__(self, W, allowed, ray, terminal):
        self.W = W
        self.cost = len(W)
        self.full = self.make_images(W, allowed, ray, terminal)
        # Forgetting a selected distinction is precisely dropping that condition.
        self.forgotten = tuple(dict.fromkeys(
            image for i in range(len(W))
            for image in self.make_images(W[:i] + W[i + 1:], allowed, ray, terminal)
        ))
        self.cache_full = {}
        self.cache_forget = {}

    @staticmethod
    def make_images(W, allowed, ray, terminal):
        maps = []
        for value in range(1 << len(W)):
            T = [0] * 8
            for assignment in allowed:
                if any(((assignment >> w) & 1) != ((value >> i) & 1) for i, w in enumerate(W)):
                    continue
                source = assignment & 7
                target = 0 if terminal else sum(((assignment >> x) & 1) << i for i, x in enumerate(ray))
                T[source] |= 1 << target
            image = [0] * 256
            for R in range(1, 256):
                low = R & -R
                image[R] = image[R ^ low] | T[low.bit_length() - 1]
            maps.append(tuple(image))
        return tuple(dict.fromkeys(maps))

    @staticmethod
    def image_set(S, maps, cache):
        if S not in cache:
            image = 0
            for R in bits(S):
                for mapping in maps:
                    image |= 1 << mapping[R]
            cache[S] = image
        return cache[S]

    def apply(self, state):
        F, G = state
        nF = self.image_set(F, self.full, self.cache_full)
        nG = self.image_set(G, self.full, self.cache_full)
        nG |= self.image_set(F, self.forgotten, self.cache_forget)
        return nF, nG


class FreshDP:
    def __init__(self, definitions):
        assert len(definitions) == 1
        k, local_count, calls = definitions[0]
        assert k == 3
        self.V = k + local_count
        self.calls = calls
        self.ray = next(tuple(args) for name, args in calls if name == 'SELF')
        self.assignments = range(1 << self.V)
        # Greatest fixed point of existential local expansion from the full
        # boundary relation. This does not call the original limit-state code.
        G = 255
        self.limit_history = [G]
        while True:
            new = 0
            for a in self.assignments:
                if self.permitted(a, G, terminal=True):
                    new |= 1 << (a & 7)
            assert new & ~G == 0
            if new == G:
                break
            G = new
            self.limit_history.append(G)
        self.limit_relation = G
        allowed_mid = [a for a in self.assignments if self.permitted(a, G, terminal=False)]
        allowed_end = [a for a in self.assignments if self.permitted(a, G, terminal=True)]
        loc = tuple(range(3, self.V))
        self.middle_ops = [Operation(W, allowed_mid, self.ray, False) for W in subsets(loc)]
        self.close_ops = [Operation(W, allowed_end, self.ray, True) for W in subsets(loc, 1)]
        self.starts = {}
        for W in subsets(tuple(range(self.V)), 1):
            if not any(x < 3 for x in W):
                continue
            op = Operation(W, allowed_mid, self.ray, False)
            state = op.apply((1 << 255, 0))
            self.starts[state] = min(self.starts.get(state, INF), len(W))

    def permitted(self, a, relation, terminal):
        first = True
        for name, args in self.calls:
            value = sum(((a >> x) & 1) << i for i, x in enumerate(args))
            if name == 'K':
                if value in (0, 7):
                    return False
            elif name == 'SELF':
                if (not first or terminal) and not ((relation >> value) & 1):
                    return False
                first = False
            else:
                raise ValueError(name)
        return True

    def close(self, state):
        if state[1] & 1:  # a forgotten assignment already has an empty image
            return INF
        for op in self.close_ops:
            F, G = op.apply(state)
            if (F & 1) and not (G & 1):
                return op.cost
        return INF


def build_graph(dp, cap=2_000_000):
    states = list(dp.starts)
    index = {state: i for i, state in enumerate(states)}
    starts = {index[state]: c for state, c in dp.starts.items()}
    graph, closes = [], []
    cursor = 0
    while cursor < len(states):
        state = states[cursor]
        row = []
        for op in dp.middle_ops:
            target = op.apply(state)
            j = index.get(target)
            if j is None:
                if len(states) == cap:
                    raise RuntimeError('referee node cap reached; not a complete recomputation')
                j = len(states)
                index[target] = j
                states.append(target)
            row.append((j, op.cost))
        graph.append(row)
        closes.append(dp.close(state))
        cursor += 1
    return graph, closes, starts, states


def trim_and_scc(graph, closes):
    N = len(graph)
    reverse = [[] for _ in range(N)]
    for u, edges in enumerate(graph):
        for v, _ in edges:
            reverse[v].append(u)
    good = {i for i, c in enumerate(closes) if c < INF}
    queue = deque(good)
    while queue:
        for u in reverse[queue.popleft()]:
            if u not in good:
                good.add(u)
                queue.append(u)
    visited, order = set(), []
    for root in sorted(good):
        if root in visited:
            continue
        visited.add(root)
        stack = [(root, iter(graph[root]))]
        while stack:
            u, it = stack[-1]
            try:
                v, _ = next(it)
            except StopIteration:
                order.append(u)
                stack.pop()
                continue
            if v in good and v not in visited:
                visited.add(v)
                stack.append((v, iter(graph[v])))
    labels, comps = {}, []
    for root in reversed(order):
        if root in labels:
            continue
        label = len(comps)
        comp, todo = [], [root]
        labels[root] = label
        while todo:
            u = todo.pop()
            comp.append(u)
            for v in reverse[u]:
                if v in good and v not in labels:
                    labels[v] = label
                    todo.append(v)
        comps.append(comp)
    return good, comps, labels


def karp(graph, comp):
    n = len(comp)
    renumber = {u: i for i, u in enumerate(comp)}
    edges = [(renumber[u], renumber[v], w) for u in comp for v, w in graph[u] if v in renumber]
    if n == 1:
        return min((Fraction(w) for u, v, w in edges if u == v), default=None)
    # A super-source permits every vertex at length 0. Inside an SCC all these
    # arrays are finite; exact integer DP, followed by exact Fraction arithmetic.
    D = [[0] * n]
    for _ in range(n):
        d = [10 ** 18] * n
        for u, v, w in edges:
            d[v] = min(d[v], D[-1][u] + w)
        D.append(d)
    return min(max(Fraction(D[n][v] - D[k][v], n - k) for k in range(n)) for v in range(n))


def empty_cycles(graph):
    # The first action is W=(), the only zero-cost action.
    successor = [row[0][0] for row in graph]
    assert all(row[0][1] == 0 and all(w > 0 for _, w in row[1:]) for row in graph)
    basin, cycles = {}, []
    for root in range(len(graph)):
        if root in basin:
            continue
        trace, positions = [], {}
        u = root
        while u not in basin and u not in positions:
            positions[u] = len(trace)
            trace.append(u)
            u = successor[u]
        if u in basin:
            c = basin[u]
        else:
            c = len(cycles)
            cycles.append(trace[positions[u]:])
        for v in trace:
            basin[v] = c
    return cycles, basin


def bounded_test(graph, closes, productive):
    cycles, basin = empty_cycles(graph)
    touched = {basin[u] for u in productive}
    acceptable = {c for c in touched if all(closes[u] < INF for u in cycles[c])}
    return dict(
        bounded_all=bool(acceptable),
        bounded_good_cycles=len(acceptable),
        bounded_bad_cycles=len(touched - acceptable),
        bounded_good_starts=sum(basin[u] in acceptable for u in productive),
        bounded_bad_starts=sum(basin[u] not in acceptable for u in productive),
        bounded_affected_starts=0,
        bounded_missing_successors=0,
    ), cycles


def exact_eventual_bound(graph, closes, starts, productive, cycles):
    """Exact cofinite-language test, with finite positive certificates.

    P=lcm of all productive zero-cycle lengths. A length residue has a uniformly
    bounded accepting walk iff some accepting walk of that residue visits a
    zero-cycle state. Insert P steps at that visit for all larger same-residue
    lengths. Conversely any bounded-cost arbitrarily long walk contains a zero
    cycle, since weights are nonnegative integers. All transitions before and
    after the visit are retained; checking only direct closings would be too weak.
    """
    productive_cycles = [c for c in cycles if all(u in productive for u in c)]
    if not productive_cycles:
        return dict(eventually_bounded=False, period=None, zero_cycle_lengths=[],
                    reason='no productive zero cycle', missing_residues=None)
    P = math.lcm(*(len(c) for c in productive_cycles))
    if 2 * len(productive) * P > 8_000_000:
        return dict(eventually_bounded=None, period=P, reason='product size resource gate')
    zero_nodes = {u for c in productive_cycles for u in c}
    visited = {}
    queue = deque()
    for u, cost in starts.items():
        if u in productive:
            state = (u, 0, u in zero_nodes)
            if state not in visited:
                visited[state] = (0, cost)
                queue.append(state)
    representatives = {}
    while queue:
        state = queue.popleft()
        u, r, seen = state
        length, cost = visited[state]
        if seen and closes[u] < INF and r not in representatives:
            representatives[r] = dict(middle_length=length, depth=length + 1,
                                      total_cost=cost + closes[u], final_node=u)
        for v, w in graph[u]:
            if v not in productive:
                continue
            target = (v, (r + 1) % P, seen or v in zero_nodes)
            if target not in visited:
                visited[target] = (length + 1, cost + w)
                queue.append(target)
    missing = sorted(set(range(P)) - representatives.keys())
    return dict(eventually_bounded=not missing, period=P,
                zero_cycle_lengths=sorted(Counter(map(len, productive_cycles)).items()),
                residues_covered=sorted(representatives), missing_residues=missing,
                product_states=len(visited),
                depth_threshold=max((v['depth'] for v in representatives.values()), default=None) if not missing else None,
                uniform_cost_bound=max((v['total_cost'] for v in representatives.values()), default=None) if not missing else None,
                representatives=representatives)


def replay(graph, closes, starts, depths):
    L = []
    layer = dict(starts)
    for _ in range(depths):
        L.append(min((c + closes[u] for u, c in layer.items() if closes[u] < INF), default=INF))
        nxt = {}
        for u, c in layer.items():
            for v, w in graph[u]:
                if c + w < nxt.get(v, INF):
                    nxt[v] = c + w
        layer = nxt
    return L


COMPARE_FIELDS = [
    'nodes', 'complete', 'expanded_nodes', 'edges', 'trimmed_nodes', 'sccs',
    'cyclic_sccs', 'cyclic_scc_edges', 'max_cyclic_scc_nodes', 'lambda',
    'lambda_float', 'lambda_status', 'zero_mean', 'bounded_all',
    'bounded_good_cycles', 'bounded_bad_cycles', 'bounded_good_starts',
    'bounded_bad_starts', 'bounded_affected_starts', 'bounded_missing_successors',
    'gate_ok', 'gate_status', 'L_recomputed', 'mismatches', 'record_depths',
]


def compute_one(idx, defs, study, record):
    t0 = time.monotonic()
    stages = {}
    dp = FreshDP(defs)
    stages['relations_and_operations'] = time.monotonic() - t0
    t = time.monotonic()
    graph, closes, starts, states = build_graph(dp)
    stages['reachable_graph'] = time.monotonic() - t
    t = time.monotonic()
    productive, comps, labels = trim_and_scc(graph, closes)
    cyclic = [c for c in comps if len(c) > 1 or any(v == c[0] for v, _ in graph[c[0]])]
    rates = [karp(graph, c) for c in cyclic]
    rate = min(rates, default=None)
    stages['trim_scc_karp'] = time.monotonic() - t
    bounded, cycles = bounded_test(graph, closes, productive)
    t = time.monotonic()
    eventual = exact_eventual_bound(graph, closes, starts, productive, cycles)
    stages['exact_eventual_boundedness'] = time.monotonic() - t
    Lrecord = record.get('L', []) if record else []
    recomputed = replay(graph, closes, starts, len(Lrecord))
    discrepancies = [dict(idx=idx, s=i + 1, ours=a, record=b)
                     for i, (a, b) in enumerate(zip(recomputed, Lrecord)) if a != b]
    cyc_labels = {labels[c[0]] for c in cyclic}
    row = dict(idx=idx, definitions=defs, status='done', nodes=len(graph), expanded_nodes=len(graph),
               edges=sum(map(len, graph)), complete=True, trimmed_nodes=len(productive), sccs=len(comps),
               cyclic_sccs=len(cyclic),
               cyclic_scc_edges=sum(1 for u in productive for v, w in graph[u]
                                    if v in productive and labels[u] == labels[v] and labels[u] in cyc_labels),
               max_cyclic_scc_nodes=max(map(len, cyclic), default=0),
               **{'lambda': f'{rate.numerator}/{rate.denominator}' if rate is not None else None},
               lambda_float=float(rate) if rate is not None else None, lambda_status='complete',
               zero_mean=rate == 0, **bounded, exact_eventual_boundedness=eventual,
               L_recomputed=recomputed, gate_ok=not discrepancies if Lrecord else None,
               gate_status='checked' if Lrecord else 'skipped_no_record_L', mismatches=discrepancies,
               record_depths=len(Lrecord), limit_relation=dp.limit_relation, limit_history=dp.limit_history,
               record_class=study.get('record_class'),
               seconds=time.monotonic() - t0, stage_seconds=stages,
               peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    row['field_comparisons'] = {field: dict(ours=row[field], study=study.get(field), equal=row[field] == study.get(field))
                                for field in COMPARE_FIELDS}
    row['field_disagreements'] = [f for f, v in row['field_comparisons'].items() if not v['equal']]
    return row


def select_cases(study):
    complete = sorted([r for r in study if r['complete']], key=lambda r: (r['nodes'], r['idx']))
    strata = {
        '40_smallest_complete': [r['idx'] for r in complete[:40]],
        '10_smallest_positive': [r['idx'] for r in complete if r['lambda_float'] is not None and r['lambda_float'] > 0][:10],
        '10_smallest_bounded_all': [r['idx'] for r in complete if r['bounded_all'] is True][:10],
        '10_smallest_zero_mean_only': [r['idx'] for r in complete if r['zero_mean'] and r['bounded_all'] is False][:10],
        '10_smallest_lambda_none': [r['idx'] for r in complete if r['lambda'] is None][:10],
        'all_46_flat_zero_mean_only': [r['idx'] for r in complete if r['record_class'] == 'flat' and r['zero_mean'] and r['bounded_all'] is False],
    }
    chosen = {i for values in strata.values() for i in values}
    return dict(policy='ascending (reported nodes, idx), complete graphs only; overlapping strata are deduplicated',
                strata=strata, selected=[r['idx'] for r in complete if r['idx'] in chosen], unique_count=len(chosen),
                estimated_total_nodes=sum(r['nodes'] for r in complete if r['idx'] in chosen))


def alarm_handler(signum, frame):
    raise TimeoutError('540 seconds per family resource ceiling')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select-only', action='store_true')
    parser.add_argument('--ids', help='comma-separated explicit ids; default frozen selection')
    parser.add_argument('--output', default='recomputed.jsonl')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (7 * 1024 ** 3, 7 * 1024 ** 3))
    signal.signal(signal.SIGALRM, alarm_handler)
    study_rows = load_rows(RATES)
    by_idx = {r['idx']: r for r in study_rows}
    selection = select_cases(study_rows)
    selection['input_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (BD, RECORDS, RATES, Path(__file__))}
    selection_path = HERE / 'sample_selection.json'
    if not selection_path.exists():
        dump(selection_path, selection)
    if args.select_only:
        print(json.dumps(selection))
        return
    indices = list(map(int, args.ids.split(','))) if args.ids else selection['selected']
    definitions = family_definitions()
    records = {r['idx']: r for r in load_rows(RECORDS)}
    output = HERE / args.output
    assert output.resolve().is_relative_to(HERE)
    if output.exists():
        raise FileExistsError(output)
    t0 = time.monotonic()
    with output.open('x') as f:
        for idx in indices:
            signal.alarm(540)
            try:
                row = compute_one(idx, definitions[idx], by_idx[idx], records.get(idx))
            except (TimeoutError, MemoryError, RuntimeError) as ex:
                row = dict(idx=idx, status='resource_failure', error=repr(ex))
            finally:
                signal.alarm(0)
            f.write(json.dumps(row, sort_keys=True) + '\n')
            f.flush()
            print(json.dumps({k: row.get(k) for k in ('idx', 'status', 'nodes', 'lambda', 'bounded_all', 'field_disagreements', 'seconds')}) , flush=True)
    print(json.dumps(dict(completed=len(indices), elapsed_seconds=time.monotonic() - t0)), flush=True)


if __name__ == '__main__':
    main()
