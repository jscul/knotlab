"""Rebuild compact physical ledgers, audit coverage, and check relabellings."""

from collections import Counter, defaultdict, deque
from hashlib import sha256
from math import comb, factorial
import gzip
import json

from representatives_growth import grow
from representatives import OUT, SIZES
from panels_sources import founder_check, width
from census_exact_rates import owners


LAWS = ('parity', 'nae')


def decoded(founder, law):
    rows = tuple(map(tuple, founder))
    items = [rows]
    for i, cut in enumerate(law['cuts'], start=1):
        assert cut['age'] == i
        assert (cut['before_holders'], cut['before_names']) == (len(rows), width(rows))
        assert [x['holder'] for x in cut['births']] == list(range(len(rows), cut['after_holders']))
        rows = (*rows, *(tuple(x['support']) for x in cut['births']))
        assert (cut['after_holders'], cut['after_names']) == (len(rows), width(rows))
        items.append(rows)
    assert (law['final_holders'], law['final_width'], law['age']) == (len(rows), width(rows), len(items) - 1)
    assert law['would_cross_b251'] == (len(rows) > 512 or width(rows) > 4096)
    if law['termination'] == 'closed':
        assert law['cuts'][-1]['whole_closed'] and law['terminal_arity'] == len(law['terminal']['support'])
    elif law['termination'] == 'stalled':
        assert law['stall']['attempted_age'] == law['age'] + 1 and law['stall']['shortages']
    else:
        assert law['termination'] == 'open' and law['age'] == 4
    return items


def transport_births(before, alternate_before, left, right, holders, names):
    old_left, old_right = owners(before), owners(alternate_before)
    left_loose = {x for x, h in old_left.items() if len(h) == 1}
    right_loose = {x for x, h in old_right.items() if len(h) == 1}
    assert {names[x] for x in left_loose} == right_loose
    by_group = defaultdict(deque)
    for b in right:
        by_group[tuple(sorted(b['parents'])), b['fresh']].append(b)
    paired = []
    for a in left:
        roster = tuple(sorted(holders[h] for h in a['parents']))
        b = by_group[roster, a['fresh']].popleft()
        assert a['following_demand'] == b['following_demand']
        right_input = {old_right[y][0]: y for y in b['inputs']}
        for x in a['inputs']:
            names[x] = right_input[holders[old_left[x][0]]]
        paired.append((a, b))
    assert all(not k for k in by_group.values())
    assert {names[x] for x in left_loose} == right_loose
    for a, b in paired:
        holders[a['holder']] = b['holder']
        names.update(zip(a['new_names'], b['new_names'], strict=True))
        assert {names[x] for x in a['support']} == set(b['support'])


def relabel(item, law):
    founder = tuple(map(tuple, item['founder_rows']))
    nearest = item['laws'][law]
    holder_move = {i: len(founder) - 1 - i for i in range(len(founder))}
    name_move = {i: width(founder) - 1 - i for i in range(width(founder))}
    moved = tuple(tuple(sorted(name_move[x] for x in row)) for row in reversed(founder))
    raw = {'source_rows': moved, 'source_name_permutation': list(name_move.values()),
           'source_holder_order_to_original': list(holder_move.values()), 'before_permutation': founder}
    lawful = founder_check(raw, law)
    assert lawful['lawful'] and lawful['essential']
    later = grow(moved, law)
    fields = ('termination', 'age', 'terminal_arity', 'positive', 'final_width', 'final_holders')
    assert all(nearest[k] == later[k] for k in fields)
    before, counterpart = decoded(founder, nearest), decoded(moved, later)

    def check_rows(rows, alternatives):
        assert sorted(holder_move.values()) == list(range(len(rows)))
        assert sorted(name_move.values()) == list(range(width(rows)))
        for i, row in enumerate(rows):
            assert {name_move[x] for x in row} == set(alternatives[holder_move[i]])

    check_rows(before[0], counterpart[0])
    for i, (cut, other) in enumerate(zip(nearest['cuts'], later['cuts'], strict=True)):
        transport_births(before[i], counterpart[i], cut['births'], other['births'], holder_move, name_move)
        assert cut['whole_closed'] == other['whole_closed']
        check_rows(before[i + 1], counterpart[i + 1])
    if nearest['stall']:
        old, new = nearest['stall'], later['stall']
        assert {holder_move[h]: lost for h, lost in old['shortages']} == dict(new['shortages'])
        mapped = {tuple(sorted(holder_move[h] for h in g)) for g in old['multi_parent_groups']}
        assert mapped == set(new['multi_parent_groups'])
    if nearest['terminal']:
        assert holder_move[nearest['terminal']['holder']] == later['terminal']['holder']
    return {'id': item['id'], 'law': law, 'founder_distinction_permutation': tuple(reversed(range(width(founder)))),
            'founder_holder_permutation': tuple(reversed(range(len(founder)))), 'termination': nearest['termination'],
            'funded_age': nearest['age'], 'width': nearest['final_width'], 'founder': lawful}


def verify_coverage(records):
    groups = defaultdict(list)
    for item in records:
        groups[item['n'], tuple(map(tuple, item['edges']))].append(item)
    summary = {}
    for n in SIZES:
        seen = Counter()
        count = weight = 0
        for (m, edges), rows in groups.items():
            if m != n:
                continue
            expected = factorial(n) // rows[0]['uncoloured_aut']
            by_extra = Counter()
            for r in rows:
                assert len(r['extra']) == n and not set(r['extra']) - {0, 1}
                assert all(len(s) >= 3 for s in r['founder_rows'])
                holder_pairs = tuple(sorted(v for v in owners(r['founder_rows']).values() if len(v) == 2))
                assert holder_pairs == edges
                k = sum(r['extra'])
                assert r['aut'] * r['labelled'] == factorial(n)
                assert r['mass'] == r['labelled'] * 3 ** (n - k)
                assert r['uncoloured_aut'] == r['aut'] * r['decoration_orbit_size']
                by_extra[k] += r['labelled']
                weight += r['mass']
                count += 1
            assert by_extra == {k: comb(n, k) * expected for k in range(n + 1)}
            seen.update(by_extra)
        assert seen == {k: comb(n, k) * n ** (n - 2) for k in range(n + 1)}
        assert weight == n ** (n - 2) * 4 ** n
        summary[n] = {'classes': count, 'labelled_by_extra': seen, 'integer_mass': weight}
    return summary


def audit(records):
    sampled = {}
    repeated_unary = {}
    closure = []
    denominators = Counter()
    largest = [0, 0]
    cap_weight = Counter()
    for r in records:
        for law in LAWS:
            m = r['laws'][law]
            rows = decoded(r['founder_rows'], m)
            state = (m['termination'], m['age'], m['terminal_arity'], m['positive'])
            sampled.setdefault((r['n'], law, *state), r)
            for c in m['cuts']:
                unary = [tuple(b['parents']) for b in c['births'] if len(b['parents']) == 1]
                if len(set(unary)) != len(unary):
                    repeated_unary.setdefault((r['n'], law), r)
            denominators[f'{law}_physical_cuts'] += m['age']
            denominators[f'{law}_births'] += sum(len(c['births']) for c in m['cuts'])
            largest = list(map(max, zip(largest, (m['final_holders'], m['final_width']), strict=True)))
            cap_weight[r['n'], law] += r['mass'] if m['would_cross_b251'] else 0
            if m['terminal']:
                closure.append({'n': r['n'], 'founder_id': r['id'], 'age': m['age'], 'arity': m['terminal_arity'],
                                'operator_admits': m['positive'], 'labelled': r['labelled'], 'mass': r['mass'],
                                'source': r['founder_rows'], 'before_rows': rows[-2],
                                'after_rows': rows[-1], 'terminal': m['terminal']})
    candidates = {(r['id'], key[1]): r for key, r in (*sampled.items(), *repeated_unary.items())}
    checked = [relabel(r, law) for (_, law), r in sorted(candidates.items())]
    referrals = [{'n': k[0], 'law': k[1], 'termination': k[2], 'age': k[3], 'terminal_arity': k[4],
                  'positive': k[5], 'founder_id': r['id']} for k, r in sampled.items()]
    return {'records': len(records), 'independent_relabel_checks': checked,
            'realised_strata': referrals, 'representative_closures': closure, 'replayed': denominators,
            'max_holders_and_distinctions': largest, 'resource_cap_mass': [(list(k), v) for k, v in sorted(cap_weight.items())]}


def main():
    path = OUT / 'representatives.json.gz'
    with gzip.open(path, 'rt') as data:
        records = json.load(data)
    result = audit(records)
    result['coverage'] = verify_coverage(records)
    result['representatives_sha256'] = sha256(path.read_bytes()).hexdigest()
    (OUT / 'representatives_audit.json').write_text(json.dumps(result, sort_keys=True) + '\n')
    print(result['records'], len(result['independent_relabel_checks']), result['replayed'],
          result['max_holders_and_distinctions'], flush=True)


if __name__ == '__main__':
    main()
