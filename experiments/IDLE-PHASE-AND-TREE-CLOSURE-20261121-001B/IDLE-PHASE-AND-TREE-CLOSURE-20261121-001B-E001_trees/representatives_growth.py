"""Exact uncapped physical rosters and independent closure checks."""

from collections import Counter
import sys

from representatives import ROOT
from panels_certificates import graph_of
from panels_physical import fresh_closures, ledger, physical_components
from panels_sources import width
from census_stages import advance, end_of
from census_verify_wider import naelib, replay_allocation
from end_operator import proposals, step


SIGNED = 'FOUR-READINGS-20261120-001A'
sys.path.insert(0, str(ROOT / 'experiments' / SIGNED / f'{SIGNED}-E001_signed_rules'))
from census import pauli_solution, product as pauli_product, verify_paulis


HORIZON = 4


def native_turn(rows, law, present, visible_groups, forecast):
    old = len(rows)
    engine = naelib.S.from_junctions(rows)
    live = [h for h in engine.live if engine.loose(h)]
    physical_supply = {h: len(engine.loose(h)) for h in live}
    assert physical_supply == present.opens
    groups = tuple(tuple(sorted(g)) for g in engine.groups_among(live))
    assert Counter(groups) == Counter(visible_groups)
    demands = Counter(h for g in groups for h in g)
    shortage = {h: demands[h] - available for h, available in physical_supply.items() if demands[h] > available}
    assert shortage == dict(forecast.shortages)
    rule = (naelib.parity_rule if law == 'parity' else naelib.nae_rule)(naelib.F.fewest)
    native = engine.step(rule, None)
    if native is None:
        assert shortage
        return 'stalled', rows, (), ()
    if not native['new']:
        assert not live
        return 'closed', rows, (), ()
    got = tuple(tuple(s) for s in engine.bits_of)
    roster = []
    lookahead = []
    for h, row in enumerate(got[old:], start=old):
        names = row[:engine.parents[h]]
        parents = tuple(sorted(next(o for o in engine.owner[x] if o != h) for x in names))
        roster.append((parents, engine.fresh[h]))
        lookahead.append((parents, engine.fresh[h], engine.demand_at_birth[h]))
    return 'births', got, tuple(roster), tuple(lookahead)


def named_paulis(rows, closure):
    holders = closure['component_holders']
    _, physical = graph_of(rows, holders)
    names = closure['component_names']
    owner = {h: i for i, h in enumerate(holders)}
    holding = {x: tuple(owner[h] for h in pair) for pair, marks in physical.items() for x in marks}
    ends = tuple(holding[x] for x in names)
    odd = {owner[closure['holder']]}
    operators = pauli_solution(ends, odd)
    assert (operators is not None) == closure['operator_positive']
    if operators is None:
        return {'exists': False, 'odd_holder': closure['holder'], 'cycle_form_inconsistent': True}
    verify_paulis(ends, operators, odd)
    named = dict(zip(names, operators, strict=True))
    for h in holders:
        together = (0, 0, 0)
        for x in rows[h]:
            together = pauli_product(together, named[x])
        assert together == (2 if h == closure['holder'] else 0, 0, 0)
    return {'exists': True, 'odd_holder': closure['holder'], 'actual_named_operators': tuple(named.items())}


def grow(source, law):
    rows = tuple(map(tuple, source))
    initial = physical_components(rows)
    assert len(initial) == 1 and initial[0]['loose']
    termination = 'open'
    stalled = terminal = None
    old_components = initial
    complete = []
    for age in range(1, HORIZON + 1):
        present, available = end_of(rows)
        forecast = step(present, 'nae')
        groups = proposals(present)
        outcome, after, proposed = advance(rows, law)
        second, other, physical_roster, physical_prices = native_turn(rows, law, present, groups, forecast)
        if forecast.status == 'stall':
            assert outcome == 'stall' and second == 'stalled'
            termination = 'stalled'
            owed = Counter(h for p in groups for h in p)
            stalled = {'attempted_age': age, 'holders': len(rows), 'names': width(rows),
                       'multi_parent_groups': groups, 'openings_and_demand': tuple(
                           {'holder': h, 'available_names': tuple(sorted(v)), 'demand': owed[h],
                            'shortfall': max(0, owed[h] - len(v))} for h, v in sorted(available.items())),
                       'shortages': forecast.shortages}
            break
        assert forecast.status == 'extend' and outcome == second == 'births'
        assert Counter(proposed) == Counter(physical_roster)
        assert tuple(p for p, _ in proposed) == forecast.parents
        replay_allocation(rows, after, other, proposed, physical_roster)
        births = ledger(rows, after, proposed, law)
        assert Counter((x['parents'], x['fresh'], d) for x, d in zip(births, forecast.demand, strict=True)) == Counter(physical_prices)
        for born, d, price in zip(births, forecast.demand, forecast.fresh, strict=True):
            assert born['fresh'] == (0 if (law == 'parity' and born['old_span_rows'] is not None) else price)
            assert born['fresh'] or d == 0
            born['following_demand'] = d
        current = physical_components(after)
        assert len(current) == 1
        closing, _ = fresh_closures(rows, after, old_components, current, births, law)
        is_closed = not current[0]['loose']
        assert is_closed == bool(closing)
        complete.append({'age': age, 'before_holders': len(rows), 'before_names': width(rows),
                         'after_holders': len(after), 'after_names': width(after), 'births': births,
                         'whole_closed': is_closed})
        rows, old_components = after, current
        if is_closed:
            assert len(closing) == 1 and law == 'parity'
            terminal = closing[0]
            terminal['binary_pauli'] = named_paulis(rows, terminal)
            termination = 'closed'
            break
    return {'termination': termination, 'age': len(complete), 'cuts': complete, 'stall': stalled,
            'terminal_arity': terminal['closing_arity'] if terminal else None,
            'positive': terminal['operator_positive'] if terminal else None,
            'terminal': terminal, 'final_width': width(rows), 'final_holders': len(rows),
            'would_cross_b251': len(rows) > 512 or width(rows) > 4096}
