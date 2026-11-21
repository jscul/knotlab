"""Complete global physical cuts, checked against the separate native engine."""

from collections import Counter, defaultdict

from panels_sources import founder_check, width
from panels_certificates import closure_signs, mask, older_span, scalar, span_basis, union_signs
from census_exact_rates import components, owners
from census_stages import advance, end_of
from census_verify_wider import native, replay_allocation
from end_operator import step


HOLDER_LIMIT = 512
NAME_LIMIT = 4096
HORIZON = 4


def physical_components(rows):
    memberships = defaultdict(list)
    for i, row in enumerate(rows):
        for x in row:
            memberships[x].append(i)
    assert all(len(d) in (1, 2) for d in memberships.values())
    packed = []
    known = set()
    for anchor in range(len(rows)):
        if anchor in known:
            continue
        queue = [anchor]
        known.add(anchor)
        for h in queue:
            for x in rows[h]:
                for other in memberships[x]:
                    if other not in known:
                        known.add(other)
                        queue.append(other)
        names = tuple(sorted({x for h in queue for x in rows[h]}))
        loose = tuple(x for x in names if len(memberships[x]) == 1)
        packed.append({'holders': tuple(sorted(queue)), 'names': names, 'loose': loose})
    assert tuple((c['holders'], c['names']) for c in packed) == tuple(components(rows))
    return tuple(packed)


def ledger(before, after, proposals, law):
    previous = owners(before)
    old_n = width(before)
    assert after[:len(before)] == before
    early = span_basis(before) if law == 'parity' else None
    births = []
    used_old = []
    used_new = []
    for h, (parents, count) in enumerate(proposals, len(before)):
        row = after[h]
        inputs = tuple(x for x in row if x < old_n)
        fresh = tuple(x for x in row if x >= old_n)
        assert len(set(row)) == len(row) and len(fresh) == count
        assert all(len(previous[x]) == 1 for x in inputs)
        observed = tuple(sorted(previous[x][0] for x in inputs))
        assert len(set(observed)) == len(observed) and observed == tuple(sorted(parents))
        provenance = older_span(early, inputs) if early is not None else None
        if law == 'parity':
            assert (provenance is not None) == (count == 0)
            if provenance is not None:
                witness = 0
                for i in provenance:
                    witness ^= mask(before[i])
                assert witness == mask(inputs)
        else:
            assert count > 0
        used_old.extend(inputs)
        used_new.extend(fresh)
        births.append({'holder': h, 'parents': parents, 'inputs': inputs, 'fresh': count,
                       'new_names': fresh, 'support': row, 'old_span_rows': provenance})
    assert sorted(used_old) == sorted(x for x, holders in previous.items() if len(holders) == 1)
    assert sorted(used_new) == list(range(old_n, width(after)))
    if law == 'parity':
        old = scalar(before, tuple(range(len(before))))
        new = scalar(after, tuple(range(len(after))))
        assert new['rank'] == old['rank'] + sum(b['fresh'] != 0 for b in births)
        assert new['words'] == old['words'] << sum(b['fresh'] - 1 for b in births if b['fresh'])
    return births


def fresh_closures(before, after, old, current, births, law):
    old_labels = {h: c for c in old for h in c['holders']}
    old_closed = {c['holders'] for c in old if not c['loose']}
    after_closed = {c['holders'] for c in current if not c['loose']}
    assert old_closed <= after_closed
    new_closed = after_closed - old_closed
    zero = [birth for birth in births if birth['fresh'] == 0]
    seen = set()
    closure = []
    for item in zero:
        parents = item['parents']
        old_component = old_labels[parents[0]]
        assert all(old_labels[h] == old_component for h in parents)
        assert set(item['inputs']) == set(old_component['loose']) and len(parents) == len(item['inputs'])
        connected = next(c for c in current if item['holder'] in c['holders'])
        assert set(connected['holders']) == {*old_component['holders'], item['holder']}
        assert connected['holders'] in new_closed and not connected['loose']
        assert connected['holders'] not in seen
        seen.add(connected['holders'])
        certificate = closure_signs(after, connected['holders'], item['holder'])
        closure.append({**item, 'closing_arity': len(item['support']),
                        'component_holders': connected['holders'], 'component_names': connected['names'],
                        'old_component_holders': old_component['holders'], 'old_component_names': old_component['names'],
                        'old_component_loose': old_component['loose'], **certificate})
    assert seen == new_closed
    if law == 'nae':
        assert not closure
    return sorted(closure, key=lambda e: min(e['component_holders'])), len(old_closed)


def grow(draw, law):
    rows = tuple(map(tuple, draw['source_rows']))
    admissible = founder_check(draw, law)
    initial = physical_components(rows)
    history = []
    if not admissible['lawful']:
        return {'founder': admissible, 'initial_components': initial, 'cuts': history, 'termination': 'ineligible'}
    if all(not c['loose'] for c in initial):
        return {'founder': admissible, 'initial_components': initial, 'cuts': history, 'termination': 'initial_no_loose'}
    closed_events = []
    terminal = 'still_open'
    censored = None
    old = initial
    for age in range(1, HORIZON + 1):
        present, _ = end_of(rows)
        prospect = step(present, 'nae', max_births=HOLDER_LIMIT - len(rows))
        if prospect.status == 'cap':
            terminal = 'holder_cap'
            censored = {'proposed_age': age, 'births_lower_bound': prospect.planned_births_lower,
                        'previous_width': width(rows), 'previous_holders': len(rows)}
            break
        outcome, after, roster = advance(rows, law)
        assert (outcome == 'births') == (prospect.status == 'extend')
        if outcome == 'births' and width(after) > NAME_LIMIT:
            terminal = 'name_cap'
            censored = {'proposed_age': age, 'proposed_width': width(after), 'proposed_holders': len(after),
                        'previous_width': width(rows), 'previous_holders': len(rows)}
            break
        direct, alternative, native_roster = native(rows, law)
        assert outcome == direct and Counter(roster) == Counter(native_roster)
        if outcome != 'births':
            assert outcome in ('closed', 'stall')
            terminal = outcome
            break
        replay_allocation(rows, after, alternative, roster, native_roster)
        births = ledger(rows, after, roster, law)
        assert len(after) <= HOLDER_LIMIT
        current = physical_components(after)
        newly, previous_closed = fresh_closures(rows, after, old, current, births, law)
        closed_events.extend(newly)
        cut = {'age': age, 'before_holder_count': len(rows), 'before_name_count': width(rows),
               'after_rows': after, 'births': births, 'components': current, 'new_closing_components': newly,
               'new_held_twice': sum(len(s['inputs']) for s in births),
               'positive_grants': sum(s['fresh'] > 0 for s in births), 'preceding_closed_pieces': previous_closed,
               'whole_closed': all(not component['loose'] for component in current)}
        if law == 'parity' and draw['panel'] == 'M' and closed_events:
            cut['union_signs'] = union_signs(after, current, closed_events)
        history.append(cut)
        rows, old = after, current
        if cut['whole_closed']:
            terminal = 'closed'
            break
    return {'founder': admissible, 'initial_components': initial, 'cuts': history, 'termination': terminal,
            'last_complete_age': len(history), 'censored': censored,
            'signed_parity_applicable': law == 'parity'}
