"""Recount result data and exhibit the small-level limits of #2 rigidity."""
import collections
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = ROOT / "research/ADDR-KNOTS-20261113-001/referee-R1/codex"
sys.path.insert(0, str(OLD))
from fresh_patterns import pattern, cnf, verify_assignment
from pysat.solvers import Glucose4

KEY = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
RUN = ROOT / "experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels"


def main():
    summary_path = ROOT / "research/LEVEL-RETURN-20261113-001/summary.json"
    summary = json.loads(summary_path.read_text())
    raw = [json.loads(x) for x in (RUN / "run3/results.jsonl").read_text().splitlines()]
    rigid = [json.loads(x) for x in (RUN / "run_rigid3/results.jsonl").read_text().splitlines()]
    assert len({r['case'] for r in raw}) == len(raw)
    counts = dict(collections.Counter(r.get('result', {}).get('verdict') for r in raw))
    assert counts == summary['verdicts']
    alt = {r['key'] for r in summary['R1']['rows']}
    r1 = [r['result'] for r in raw if r.get('result') and
          r['result'].get('kind') == 'level' and r['result']['n'] >= 13 and
          r['result'].get('key_id', '')[:16] in alt]
    second_states = []
    for n in [3, 4, 5]:
        triples = pattern(KEY, n)
        parity = [x.bit_count() & 1 for x in range(1 << n)]
        blocking = [i+1 if not v else -i-1 for i, v in enumerate(parity)]
        with Glucose4(bootstrap_with=cnf(triples)+[[-1], blocking]) as solver:
            assert solver.solve()
            values = [0] * (1 << n)
            for lit in solver.get_model(): values[abs(lit)-1] = int(lit > 0)
        assert values[0] == 0 and values != parity
        assert verify_assignment(triples, values)
        second_states.append({'n': n, 'knots': len(triples),
                              'model': ''.join(map(str, values)),
                              'not_parity_or_complement': True,
                              'checked_all_knots': True,
                              'parity_is_model': verify_assignment(triples, parity)})
    key3_path = OLD / 'returns/f4fd01e9afa5631440f1607276c889547b4767423ee44873e86cf9c85b7d2c4d.json'
    key3 = json.loads(key3_path.read_text())['key']
    triples3 = pattern(key3, 2)
    assert verify_assignment(triples3, [0, 0, 1, 1])
    assert verify_assignment(triples3, [0, 1, 1, 0])
    result = {
        'run3_rows': len(raw), 'run3_verdicts': counts,
        'r1_high_level_counts': dict(collections.Counter(r['verdict'] for r in r1)),
        'r1_undecided': [{'key': r['key_id'][:16], 'n': r['n']} for r in r1 if r['verdict']=='undecided'],
        'rigidity_missing': [{'case': r['case'], 'status': r['status'],
                              'result': r.get('result')} for r in rigid
                             if not r.get('result') or r['result'].get('verdict') in ['undecided','not alive: undecided']],
        'small_level_counterexamples_to_unqualified_parity_uniqueness': second_states,
        'pattern3_level2_nonrigidity': {'n': 2, 'knots': triples3,
                                      'models': ['0011', '0110'],
                                      'not_complements': True, 'checked_all_knots': True},
        'study_R4_holds_field': summary['R4_holds'],
        'input_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [summary_path, RUN/'run3/results.jsonl', RUN/'run_rigid3/results.jsonl']},
    }
    (HERE/'wording_results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
