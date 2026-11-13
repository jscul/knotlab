"""Independent finite-state ray-bond audit (exploratory, no asymptotic fits).

Inputs: the frozen family definitions and recorded L values. Only the producer's
families_one_def loader and L (dlang) fixed-point evaluator are reused. All block
enumeration, projection/forgetting maps, shortest paths and certificates are new.
Sample: 20 smallest recorded state counts in each L(30)>L(1) / equal group.
Observable: exact minimum cardinality, None means no bond. Controls: selected
reported bounded/no-bond cases; exact prefix agreement; independent SAT checks
live in independent_validation.py. Limits: one invocation <540s, 7GiB address
space, graph <=20000 states; failures are retained, never reclassified.

Run: .venv/bin/python -B <this-file> --output dp_samples.json
"""
import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py'
DATA = ROOT / 'artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds'
INF = 10**12


def producer_loader():
    spec = importlib.util.spec_from_file_location('bd_loader_only', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def members(bits):
    while bits:
        b = bits & -bits
        yield b.bit_length() - 1
        bits -= b


def block_rows(definition, relation, terminal):
    """Enumerate actual assignments, independently of producer block helpers."""
    k, local, calls = definition
    assert k == 3
    ray = next(tuple(args) for callee, args in calls if callee == 'SELF')
    rows = []
    for assignment in range(1 << (k + local)):
        first = True
        valid = True
        for callee, args in calls:
            value = sum(((assignment >> a) & 1) << j for j, a in enumerate(args))
            if callee == 'K':
                valid &= value not in (0, 7)
            elif callee == 'SELF':
                if terminal or not first:
                    valid &= bool(relation[value])
                first = False
            else:
                raise ValueError('one-definition audit only')
        if valid:
            output = 0 if terminal else sum(((assignment >> a) & 1) << j for j, a in enumerate(ray))
            rows.append((assignment, assignment & 7, output))
    return rows


class Operator:
    def __init__(self, full, forget, cost):
        self.full = full
        self.forget = forget
        self.cost = cost
        self.cache_full = {}
        self.cache_forget = {}

    @staticmethod
    def family_image(family, maps, cache):
        if family not in cache:
            image = 0
            for R in members(family):
                for mapping in maps:
                    image |= 1 << mapping[R]
            cache[family] = image
        return cache[family]

    def apply(self, state):
        F, G = state
        return (self.family_image(F, self.full, self.cache_full),
                self.family_image(G, self.full, self.cache_full) |
                self.family_image(F, self.forget, self.cache_forget))


def reach_map(singletons):
    out = bytearray(256)
    for R in range(1, 256):
        b = R & -R
        out[R] = out[R ^ b] | singletons[b.bit_length() - 1]
    return bytes(out)


def operators(rows, subsets):
    """Forgetting one selected variable unions its two assignment tables."""
    unique = {}
    for subset in subsets:
        mask = sum(1 << i for i in subset)
        values = [sum(((a >> j) & 1) << v for j, v in enumerate(subset))
                  for a in range(1 << len(subset))]
        tables = {a: [0]*8 for a in values}
        for assignment, port, out in rows:
            tables[assignment & mask][port] |= 1 << out
        full = tuple(sorted(set(reach_map(t) for t in tables.values())))
        forgot = set()
        for variable in subset:
            bit = 1 << variable
            for a in values:
                if not a & bit:
                    forgot.add(reach_map([x | y for x, y in zip(tables[a], tables[a | bit])]))
        key = (full, tuple(sorted(forgot)))
        if key not in unique or len(subset) < unique[key].cost:
            unique[key] = Operator(*key, len(subset))
    return list(unique.values())


def subsets(items, nonempty=False):
    return [c for n in range(int(nonempty), len(items)+1) for c in itertools.combinations(items, n)]


def viable(state):
    # 0 in G can never disappear. 0 in F means the already selected prefix is
    # constrained: adding a required last-block member cannot give a minimal set.
    return not ((state[0] | state[1]) & 1)


def build_graph(defs, evaluator, cap=20000):
    _, _, G = evaluator.depth_sequence(defs, evaluator.TOP)
    definition = defs[0]
    V = sum(definition[:2])
    locals_ = list(range(3, V))
    regular = block_rows(definition, G[0], False)
    terminal = block_rows(definition, G[0], True)
    first_choices = [W for W in subsets(list(range(V)), True) if any(v < 3 for v in W)]
    initial_ops = operators(regular, first_choices)
    middle_ops = operators(regular, subsets(locals_))
    terminal_ops = operators(terminal, subsets(locals_, True))
    start = (1 << 255, 0)
    initial = {}
    for op in initial_ops:
        state = op.apply(start)
        if viable(state):
            initial[state] = min(initial.get(state, INF), op.cost)
    states = list(initial)
    ids = {state: i for i, state in enumerate(states)}
    edges, closing = [], []
    cursor = 0
    while cursor < len(states):
        if len(states) > cap:
            raise RuntimeError('graph cap exceeded')
        state = states[cursor]
        last = INF
        for op in terminal_ops:
            F, Gf = op.apply(state)
            if F & 1 and not Gf & 1:
                last = min(last, op.cost)
        closing.append(last)
        outgoing = {}
        for op in middle_ops:
            target = op.apply(state)
            if not viable(target):
                continue
            if target not in ids:
                ids[target] = len(states)
                states.append(target)
            v = ids[target]
            outgoing[v] = min(outgoing.get(v, INF), op.cost)
        edges.append(sorted(outgoing.items()))
        cursor += 1
    init = {ids[st]: c for st, c in initial.items()}
    reverse = [[] for _ in states]
    for u, row in enumerate(edges):
        for v, _ in row:
            reverse[v].append(u)
    keep = {i for i, c in enumerate(closing) if c < INF}
    queue = collections.deque(keep)
    while queue:
        for u in reverse[queue.popleft()]:
            if u not in keep:
                keep.add(u)
                queue.append(u)
    order = sorted(keep)
    remap = {old: new for new, old in enumerate(order)}
    return dict(
        states_before_coaccessibility=len(states),
        states=[[str(states[u][0]), str(states[u][1])] for u in order],
        initial={remap[u]: c for u, c in init.items() if u in keep},
        edges=[[[remap[v], w] for v, w in edges[u] if v in keep] for u in order],
        closing=[None if closing[u] == INF else closing[u] for u in order],
        operators=[len(initial_ops), len(middle_ops), len(terminal_ops)],
        G=[int(x) for x in G[0]])


def exact_sequence(graph, horizon=512):
    n = len(graph['states'])
    vector = [INF]*n
    for u, c in graph['initial'].items():
        vector[int(u)] = c
    seen = {}
    values = []
    certificate = None
    normalizers = []
    for depth in range(1, horizon+1):
        ans = min((vector[u]+c for u, c in enumerate(graph['closing']) if c is not None), default=INF)
        values.append(None if ans >= INF else ans)
        finite = [c for c in vector if c < INF]
        if not finite:
            certificate = dict(kind='eventually_no_ray_bond', from_s=depth)
            values.extend([None]*(horizon-depth))
            break
        mn = min(finite)
        normalizers.append(mn)
        key = tuple(None if c >= INF else c-mn for c in vector)
        if key in seen:
            old_depth, old_mn = seen[key]
            period = depth-old_depth
            gain = mn-old_mn
            certificate = dict(kind='exact_full_vector_repeat_on_productive_graph',
                               from_s=old_depth, repeated_at_s=depth, period=period,
                               gain=gain, rate=[gain, period],
                               recurring_values=values[old_depth-1:depth-1],
                               normalized_vector=list(key))
            for s in range(depth+1, horizon+1):
                previous = values[s-1-period]
                values.append(None if previous is None else previous+gain)
            break
        seen[key] = (depth, mn)
        successor = [INF]*n
        for u, c in enumerate(vector):
            if c >= INF:
                continue
            for v, w in graph['edges'][u]:
                successor[v] = min(successor[v], c+w)
        vector = successor
    return values, certificate, normalizers


def bounded_budget_certificate(graph, budget, horizon=2048):
    """Discard costs above B; nonnegative edges make this exact below B.

    A raw-vector recurrence with finite outputs on its whole period proves a
    bounded exact tail. A missing output here means only '> B or absent'.
    """
    n = len(graph['states'])
    vector = [INF]*n
    for u, c in graph['initial'].items():
        if c <= budget:
            vector[int(u)] = c
    seen, values = {}, []
    for depth in range(1, horizon+1):
        answer = min((vector[u]+c for u, c in enumerate(graph['closing']) if c is not None), default=INF)
        values.append(answer if answer <= budget else None)
        key = tuple(None if c >= INF else c for c in vector)
        if key in seen:
            old = seen[key]
            word = values[old-1:depth-1]
            return dict(kind='exact_budget_truncated_vector_repeat', budget=budget,
                        from_s=old, repeated_at_s=depth, period=depth-old, gain=0,
                        rate=[0, depth-old], recurring_values=word,
                        all_tail_values_finite=all(x is not None for x in word),
                        exact_prefix_when_finite=values, vector=list(key))
        seen[key] = depth
        nxt = [INF]*n
        for u, c in enumerate(vector):
            if c >= INF:
                continue
            for v, w in graph['edges'][u]:
                if c+w <= budget:
                    nxt[v] = min(nxt[v], c+w)
        vector = nxt
    return None


def check_untrimmed_anchor(defs, evaluator, depth=40):
    """Small independent unpruned replay to expose the frozen normalizer."""
    _, _, G = evaluator.depth_sequence(defs, evaluator.TOP)
    V = sum(defs[0][:2])
    rows = block_rows(defs[0], G[0], False)
    first = operators(rows, [W for W in subsets(list(range(V)), True) if any(i < 3 for i in W)])
    middle = operators(rows, subsets(list(range(3, V))))
    layer = {}
    for op in first:
        st = op.apply((1 << 255, 0))
        layer[st] = min(layer.get(st, INF), op.cost)
    minima, counts = [], []
    for _ in range(depth):
        minima.append(min(layer.values()))
        counts.append(len(layer))
        nxt = {}
        for st, c in layer.items():
            for op in middle:
                ns = op.apply(st)
                nxt[ns] = min(nxt.get(ns, INF), c+op.cost)
        layer = nxt
    return dict(minima=minima, states=counts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='dp_samples.json')
    parser.add_argument('--per-group', type=int, default=20)
    parser.add_argument('--ids', default='')
    parser.add_argument('--horizon', type=int, default=512)
    args = parser.parse_args()
    begin = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (7*1024**3, 7*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (525, 530))
    module = producer_loader()
    families = dict(module.families_one_def())  # permitted loader reuse
    rows = [json.loads(line) for line in (DATA/'runs_merged.jsonl').read_text().splitlines()]
    by_idx = {r['idx']: r for r in rows}
    candidates = [r for r in rows if r.get('rate') is None and len(r['L']) == 30 and min(r['L']) < 10**9]
    groups = dict(rising=[r for r in candidates if r['L'][-1] > r['L'][0]],
                  flat=[r for r in candidates if r['L'][-1] == r['L'][0]])
    selected = []
    if args.ids:
        selected = [('targeted_control', int(i)) for i in args.ids.split(',')]
    else:
        for name, group in groups.items():
            selected.extend((name, r['idx']) for r in sorted(group, key=lambda r:(r['states'], r['idx']))[:args.per_group])
    result = dict(method='independent truth-table subset automaton, exact shortest paths',
                  imports_reused=['census.families_one_def (including usual-limit loading)',
                                  'census.L = dlang: depth_sequence, TOP'],
                  producer_functions_not_called=['run_family','block_relation','tables','brute','ray_cnf','summarize'],
                  sample_rule='ascending (recorded states, idx), L30>L1 vs L30==L1; complete-30 undetermined only',
                  horizon=args.horizon,
                  input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (SOURCE, DATA/'runs_merged.jsonl')},
                  groups={k:len(v) for k,v in groups.items()}, results=[])
    for group, idx in selected:
        start = time.monotonic()
        record = dict(idx=idx, group=group, definition=families[idx], recorded=by_idx[idx])
        try:
            graph = build_graph(families[idx], module.L)
            values, cert, normalizers = exact_sequence(graph, args.horizon)
            recorded_values = [None if c >= 10**9 else c for c in by_idx[idx]['L']]
            record.update(graph=graph, L=values, certificate=cert,
                          productive_normalizers=normalizers,
                          recorded_prefix_agrees=values[:len(recorded_values)] == recorded_values)
            if group == 'flat' or (cert is None and all(x is not None for x in values)):
                finite = [x for x in recorded_values if x is not None]
                budget_cert = bounded_budget_certificate(graph, max(finite)) if finite else None
                record['bounded_budget_certificate'] = budget_cert
            if idx in [selected[0][1], selected[-1][1]]:
                record['untrimmed_anchor'] = check_untrimmed_anchor(families[idx], module.L)
        except Exception as exc:
            record['error'] = repr(exc)
        record['seconds'] = round(time.monotonic()-start, 4)
        result['results'].append(record)
        result['seconds'] = round(time.monotonic()-begin, 4)
        result['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (HERE/args.output).write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({k:record.get(k) for k in ['idx','group','seconds','recorded_prefix_agrees','certificate','error']}, default=str), flush=True)


if __name__ == '__main__':
    main()
