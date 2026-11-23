"""Read back the enrolled knots and joint child using only final physical holdings.

The input is a connected marked preparation after three complete funded cuts.
The roles have the marker multiplicities registered in the prospective design.
No birth order, parent annotations, switch settings or Boolean values are read.
"""
from collections import Counter, defaultdict, deque


def inspect(stars):
    stars = [set(row) for row in stars]
    by_name = defaultdict(list)
    for holder, row in enumerate(stars):
        for name in row:
            by_name[name].append(holder)
    contacts = [Counter() for row in stars]
    for pair in by_name.values():
        if len(pair) > 2:
            raise ValueError('a payment has more than two holders')
        if len(pair) == 2:
            a, b = pair
            contacts[a][b] += 1
            contacts[b][a] += 1
    source = {h for h, counts in enumerate(contacts) if max(counts.values(), default=0) >= 2}
    order = dict.fromkeys(source, 0)
    queue = deque(source)
    while queue:
        old = queue.popleft()
        for h in contacts[old]:
            if h not in order:
                order[h] = order[old] + 1
                queue.append(h)
    assert len(order) == len(stars) and max(order.values()) == 3
    initial = {}
    for h in source:
        loose = sum(len(source.intersection(by_name[d])) == 1 for d in stars[h])
        if loose:
            key = loose, max(contacts[h][k] for k in source if k in contacts[h])
            assert key not in initial, 'the registered enrollment is ambiguous'
            initial[key] = h
    direct = (3, 3) in initial
    family = 'direct' if direct else 'balanced'
    anchor_roles = ['A', 'Aprime', 'C', 'Cprime', 'K' if direct else 'U']
    founders = {role: initial[(1, count)] for count, role in enumerate(anchor_roles, 3)}
    donors = {'B': initial[(3, 3)]} if direct else {'P': initial[(2, 3)], 'Q': initial[(2, 4)]}
    founders.update(donors)
    assert len(founders) == len(initial)

    def incident_at(h, age):
        return {k for k in contacts[h] if order[k] == age}

    enrolled = {}
    for role in anchor_roles[:4] + (['K'] if direct else []):
        child, = incident_at(founders[role], 1)
        enrolled[role] = child
    older = {role: incident_at(child, 0) for role, child in enrolled.items()}
    r, s = enrolled['A'], enrolled['C']
    r_contacts = older['A']
    s_contacts = older['C']
    role_of = {h: role for role, h in founders.items()}
    # Identify a birth from its full roster of physical payers.
    later = {h: incident_at(h, 1) for h in order if order[h] == 2}
    joint = [h for h, payers in later.items() if payers == {r, s}]
    assert len(joint) == int(bool(r_contacts & s_contacts))
    assert all((payers == {r,s}) or not {r,s} <= payers for payers in later.values())
    assert all(contacts[h][k] == 1 for h, payers in later.items() for k in payers)
    assert set(r_contacts & s_contacts) <= set(donors.values())
    partner = {}
    for name, h in [('R', r), ('S', s)]:
        reduced = Counter(len(payers) for payers in later.values() if h in payers)
        partner[name] = [[arity, count] for arity, count in sorted(reduced.items())]
    return {
        'family': family, 'cohorts': [sum(v == n for v in order.values()) for n in (1,2,3)],
        'R_payers': sorted(role_of[h] for h in r_contacts), 'S_payers': sorted(role_of[h] for h in s_contacts),
        'R_own_shared_and_loose': [len(r_contacts), len(stars[r]) - len(r_contacts)],
        'S_own_shared_and_loose': [len(s_contacts), len(stars[s]) - len(s_contacts)],
        'common_earlier_payers': sorted(role_of[h] for h in r_contacts & s_contacts),
        'joint_children': len(joint), 'funded_children_by_arity': partner,
    }


def matched_direct_words(cases):
    """Make the two first cohorts agree on every value under matched anchor names."""
    from itertools import product

    def lawful(law, bits):
        return sum(bits) % 2 == 0 if law == 'parity' else len(set(bits)) == 2

    snapshots = {}
    for case in cases:
        if case['family'] != 'direct' or case['switches'][1] != 1:
            continue
        run = case['runs'][0]
        law = case['law']
        values = {int(d): bit for d, bit in run['levels'][0]['word'].items()}
        for bank in run['cuts'][0]['births']:
            assert len(bank['fresh']) == 2
            values.update(dict.fromkeys(bank['fresh'], 1))
        assert all(lawful(law, [values[d] for d in row]) for row in run['levels'][1]['holdings'])
        labels = {}
        enrolled = run['observation']['enrollment']
        for role in ('R', 'S'):
            bank, = [b for b in run['cuts'][0]['births'] if b['knot'] == enrolled[role]]
            local = {str(d):values[d] for d in bank['paid']}
            local.update({f'{role}-fresh-{i}':values[d] for i,d in enumerate(bank['fresh'])})
            labels[role] = local
        for cut, level in zip(run['cuts'][1:], run['levels'][2:], strict=True):
            for birth in cut['births']:
                paid = [values[d] for d in birth['paid']]
                choices = product((0,1), repeat=len(birth['fresh']))
                extension = next(bits for bits in choices if lawful(law, [*paid,*bits]))
                values.update(zip(birth['fresh'], extension, strict=True))
            assert all(lawful(law, [values[d] for d in row]) for row in level['holdings'])
        snapshots[law,case['switches'][0]] = labels
    answer = {}
    for law in ('parity','nae'):
        on, off = snapshots[law,1], snapshots[law,0]
        assert on['S'] == off['S']
        extra, = on['R'].keys() - off['R'].keys()
        assert on['R'][extra] == 0
        assert {k:v for k,v in on['R'].items() if k != extra} == off['R']
        answer[law] = {'intact':on, 'interrupted':off, 'only_extra_R_payment':extra,
                       'continuous_valued_cuts_verified':3}
    return answer


def audit(path):
    import gzip
    import json

    with gzip.open(path, 'rt') as stream:
        cases = json.load(stream)
    rows = []
    checked = 0
    for case in cases:
        observed = None
        for run in case['runs']:
            holdings = run['levels'][-1]['holdings']
            result = inspect(holdings)
            if observed is None:
                observed = result
            assert result == observed
            reversed_labels = [[-1 - int(d) for d in r] for r in reversed(holdings)]
            assert inspect(reversed_labels) == observed
            checked += 1
        assert inspect(case['coherent_relabelling']['levels'][-1]['holdings']) == observed
        assert inspect(case['alternate_word']['levels'][-1]['holdings']) == observed
        e, f, *_ = case['switches']
        expected = (e == 1 and f == 1) if observed['family'] == 'direct' else (e == f)
        assert observed['joint_children'] == int(expected)
        rows.append({'law':case['law'], 'switches':case['switches'], **observed})
    assert len(rows) == 24 and checked == 112
    return {'primary_presentation_law_cells':len(rows), 'donor_bindings_checked':checked,
            'method':'Final holdings only. Founder roles and kin relations recovered independently without a ledger.',
            'matched_local_values':matched_direct_words(cases), 'rows':rows}


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    raw = Path(__file__).resolve().parents[2] / 'artifacts' / 'EARLIER-EVENT-AND-LATER-BIRTH-20261122-001B'
    parser.add_argument('replay', nargs='?', type=Path, default=raw / 'EARLIER-EVENT-AND-LATER-BIRTH-20261122-001B-E001_matched_replay' / 'physical_replay.json.gz')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = json.dumps(audit(args.replay), indent=2) + '\n'
    if args.output:
        args.output.write_text(out)
    else:
        print(out, end='')
