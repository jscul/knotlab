"""Replay saved shortest-path certificates without importing any producer.

Checks the saved graphs and certificates, not independent truth-table-to-graph
reconstruction. The latter is cross-checked by independent_validation.py.
All 512 depth readings are recomputed without extrapolation. Bad-value and
bad-gain controls must be rejected. Only adjacent verification.json is written.
"""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import resource
import time

HERE = Path(__file__).resolve().parent
INF = 10**20


def replay(graph, horizon, budget=None):
    current = {int(u): c for u, c in graph['initial'].items() if budget is None or c <= budget}
    vectors, answers = [], []
    for _ in range(horizon):
        vectors.append(dict(current))
        choices = [c+graph['closing'][u] for u, c in current.items()
                   if graph['closing'][u] is not None]
        value = min(choices, default=INF)
        answers.append(None if value == INF or (budget is not None and value > budget) else value)
        nxt = {}
        for u, cost in current.items():
            for v, weight in graph['edges'][u]:
                candidate = cost+weight
                if (budget is None or candidate <= budget) and candidate < nxt.get(v, INF):
                    nxt[v] = candidate
        current = nxt
    return answers, vectors


def validate_record(record):
    graph = record['graph']
    assert 'error' not in record
    assert all(c >= 1 for c in graph['initial'].values())
    assert all(c is None or c >= 1 for c in graph['closing'])
    assert all(w >= 0 for edges in graph['edges'] for v, w in edges)
    assert all(not ((int(F) | int(G)) & 1) for F, G in graph['states'])
    actual, vectors = replay(graph, len(record['L']))
    assert actual == record['L'], ('reading mismatch', record['idx'])
    assert record['recorded_prefix_agrees']
    cert = record['certificate']
    if cert:
        if cert['kind'] == 'eventually_no_ray_bond':
            assert not vectors[cert['from_s']-1]
            assert all(x is None for x in actual[cert['from_s']-1:])
        else:
            s, t, gain = cert['from_s'], cert['repeated_at_s'], cert['gain']
            a, b = vectors[s-1], vectors[t-1]
            assert a.keys() == b.keys()
            assert all(b[u] == a[u]+gain for u in a)
            assert t-s == cert['period']
            assert actual[s-1:t-1] == cert['recurring_values']
    budget_cert = record.get('bounded_budget_certificate')
    if budget_cert:
        values, truncated = replay(graph, budget_cert['repeated_at_s'], budget_cert['budget'])
        s, t = budget_cert['from_s'], budget_cert['repeated_at_s']
        assert truncated[s-1] == truncated[t-1]
        assert values == budget_cert['exact_prefix_when_finite']
        word = values[s-1:t-1]
        assert word == budget_cert['recurring_values']
        assert budget_cert['all_tail_values_finite'] == all(x is not None for x in word)
        assert budget_cert['all_tail_values_finite']
    return dict(idx=record['idx'], graph_states=len(graph['states']), depths_replayed=len(actual),
                exact_repeat_checked=bool(cert), bounded_budget_repeat_checked=bool(budget_cert))


def rejects(record):
    try:
        validate_record(record)
    except AssertionError:
        return True
    return False


def main():
    begin = time.monotonic()
    output = dict(producer_imports=[], checks=[], controls={}, summaries={})
    inputs = ['dp_samples.json', 'dp_controls.json', 'dp_plateaus.json']
    loaded = {name: json.loads((HERE/name).read_text()) for name in inputs}
    for name, data in loaded.items():
        for record in data['results']:
            output['checks'].append(dict(file=name, **validate_record(record)))
    sample = loaded['dp_samples.json']['results']
    bad = copy.deepcopy(sample[0])
    bad['L'][42] += 1
    output['controls']['changed_reading_rejected'] = rejects(bad)
    bad = copy.deepcopy(sample[0])
    bad['certificate']['gain'] += 1
    output['controls']['changed_gain_rejected'] = rejects(bad)
    # Accessible/coaccessible finite graph with two different residue slopes.
    counterexample = dict(initial={0: 0}, edges=[[[1, 0], [3, 0]], [[2, 0]], [[1, 0]], [[3, 1]]],
                          closing=[None, 0, None, 0])
    readings, _ = replay(counterexample, 32)
    # replay depth 1 counts zero middle edges, so discard that first reading.
    sequence = readings[1:]
    assert sequence == [0 if n % 2 else n-1 for n in range(1, 32)]
    output['residue_counterexample'] = dict(vertices=['q','a','c','b'], graph=counterexample,
                                           L_for_path_lengths_1_to_31=sequence,
                                           even_slope=1, odd_slope=0, minimum_cycle_mean=0)
    for group in ['rising', 'flat']:
        records = [r for r in sample if r['group'] == group]
        rates = {}
        for record in records:
            cert = record['certificate'] or record['bounded_budget_certificate']
            rate = str(Fraction(*cert['rate']))
            rates.setdefault(rate, []).append(record['idx'])
        output['summaries'][group] = dict(count=len(records), rate_to_ids=rates,
                                          L512_to_ids={str(v):[r['idx'] for r in records if r['L'][-1] == v]
                                                       for v in set(r['L'][-1] for r in records)})
    output['summaries']['targeted_plateaus'] = [dict(idx=r['idx'],
        certified_tail=r['bounded_budget_certificate']['recurring_values'])
        for r in loaded['dp_plateaus.json']['results']]
    output['all_passed'] = all(output['controls'].values())
    assert output['all_passed']
    output['inputs_sha256'] = {n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in inputs}
    output['elapsed_seconds'] = round(time.monotonic()-begin, 6)
    output['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (HERE/'verification.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(dict(checked=len(output['checks']), all_passed=output['all_passed'],
                         elapsed_seconds=output['elapsed_seconds'])))


if __name__ == '__main__':
    main()
