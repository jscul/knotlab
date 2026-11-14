"""Exhaust the remaining support sizes in sampled censored window states."""
import itertools
import json
import time
from pathlib import Path
from window_audit import Window, canonical, direct_check

HERE = Path(__file__).resolve().parent


def full_bond(w, q):
    labels, allowed = w.relation(q)
    n = len(labels)
    universe = (1 << (1 << n)) - 1
    positives = [sum(1 << s for s in range(1 << n) if (s >> j) & 1) for j in range(n)]
    cache = {}
    def shattered(support):
        if support in cache:
            return cache[support]
        portions = [allowed]
        for j in support:
            updated = []
            for row in portions:
                a, b = row & positives[j], row & (universe ^ positives[j])
                if not a or not b:
                    cache[support] = False
                    return False
                updated.extend((a, b))
            portions = updated
        cache[support] = True
        return True
    for k in range(7, n + 1):
        for support in itertools.combinations(range(n), k):
            if not any(labels[j] < w.km for j in support):
                continue
            if not any(labels[j] >= w.km + 3 for j in support):
                continue
            if not shattered(support) and all(shattered(support[:j] + support[j + 1:]) for j in range(k)):
                return [labels[j] for j in support]
    return None


def main():
    started = time.monotonic()
    data = json.loads((HERE / 'window_inputs.json').read_text())
    cases = []
    for record in data['records']:
        w = Window(json.loads(record['digest']['key']), record['census']['S'])
        states = [s for s in record['certificate']['window']['state_bonds'] if s['g'] == '> 6']
        findings = []
        for state in states:
            q = int(state['J'], 16), canonical(state['partition'])
            assert w.least_bond(q)[0] is None
            support = full_bond(w, q)
            findings.append({'J': state['J'], 'partition': list(q[1]),
                             'window_distinctions': len(w.relation(q)[0]),
                             'larger_bond': support})
        targets = {(int(s['J'], 16), tuple(s['partition'])): s
                   for s in findings if s['larger_bond'] is not None}
        current = dict(w.starts)
        depth = 0
        while targets:
            assert depth < 2000
            for q in set(current).intersection(targets):
                found = targets.pop(q)
                level = {'s': depth, 'winner': {'U': len(found['larger_bond']), 'state': q,
                         'path': current[q], 'support': tuple(found['larger_bond'])}}
                found['direct'] = direct_check(w, level)
            following = {}
            for q, (entry, word) in current.items():
                for label in range(len(w.generators)):
                    following.setdefault(w.step(q, label), (entry, word + (label,)))
            current = following
            depth += 1
        cases.append({'key_sha256': record['digest']['key_sha256'], 'states': findings})
    output = {'families': len(cases), 'censored_states': sum(len(r['states']) for r in cases),
              'larger_bonds': sum(s['larger_bond'] is not None for r in cases for s in r['states']),
              'cases': cases, 'seconds': round(time.monotonic() - started, 3),
              'nonclaim': 'Sample only; no proof that the size-six cutoff is exhaustive in every census family.'}
    (HERE / 'window_censor_probe.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if k != 'cases'}))


if __name__ == '__main__':
    main()
