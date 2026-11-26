"""Rank the attained wholes and components from their physical holdings."""

from collections import Counter, defaultdict
import argparse
import gzip
import json
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
TICKET = HERE.parent.name
DATA = HERE.parents[2] / 'artifacts' / TICKET / (TICKET + '-E001_closures')
PANEL_ORDER = 'TEMS'


def physical_components(rows):
    holders = defaultdict(list)
    for i, row in enumerate(rows):
        for x in row:
            holders[x].append(i)
    assert all(1 <= len(hs) <= 2 for hs in holders.values())
    unseen = set(range(len(rows)))
    while unseen:
        chosen = unseen.pop()
        knots = {chosen}
        pending = [chosen]
        while pending:
            for name in rows[pending.pop()]:
                for peer in holders[name]:
                    if peer in unseen:
                        unseen.remove(peer)
                        knots.add(peer)
                        pending.append(peer)
        names = {x for i in knots for x in rows[i]}
        yield frozenset(knots), names, all(len(holders[x]) == 2 for x in names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    start = perf_counter()
    with gzip.open(DATA / 'panels_histories.json.gz','rt') as f:
        draws = json.load(f)
    entries = defaultdict(list)
    carried = Counter()
    shorter = Counter()
    for d in draws:
        panel = d['panel']
        if args.pilot and d['draw'] > 4:
            continue
        for law, history in d['laws'].items():
            seen = set()
            assert all(not closed for _,_,closed in physical_components(d['source_rows']))
            for cut in history['cuts']:
                rows = cut['after_rows']
                parts = list(physical_components(rows))
                all_closed = all(closed for _,_,closed in parts)
                closed = {knots for knots, _, c in parts if c}
                assert seen <= closed
                assert all_closed == cut['whole_closed']
                reported = {frozenset(e['component_holders']):e for e in cut['new_closing_components']}
                assert reported.keys() == closed - seen
                if panel == 'M' and law == 'parity':
                    carried[len(seen)] += 1
                seen = closed
                for knots, names, _ in parts:
                    if knots not in reported:
                        continue
                    e = reported[knots]
                    child, = [i for i in knots if i >= cut['before_holder_count']]
                    assert child == e['holder'] and names == set(e['component_names'])
                    arity = len(rows[child])
                    assert arity == e['closing_arity']
                    shorter[arity] += 1
                    if not e['operator_positive']:
                        continue
                    scope = ['component', 'whole' if all_closed else 'continuing_component']
                    tie_break = [arity, cut['age'], PANEL_ORDER.index(panel), d['draw'], child]
                    for choice in scope:
                        sizes = ([len(rows),len(set().union(*rows))] if choice == 'whole' else
                                 [len(knots),len(names)])
                        for population in (panel,'all'):
                            entries[population,choice].append(sizes + tie_break)
    expected = json.loads((DATA/'panels_witnesses.json').read_text())
    result = {}
    for population in ('all', *PANEL_ORDER):
        local = expected if population == 'all' else expected['panels'][population]
        result[population] = {}
        for choice, alias in [('whole','whole_arity_at_least_three'),
                              ('component','component_arity_at_least_three'),
                              ('continuing_component','continuing_arity_at_least_three')]:
            options = entries[population,choice]
            for field, eligible in [(choice, options), (alias,[x for x in options if x[2] >= 3])]:
                result[population][field] = min(eligible, default=None)
                if not args.pilot:
                    archive = local[field]
                    assert result[population][field] == (archive and archive['ranking_key'])
    elapsed = perf_counter() - start
    output = dict(rank_keys=result, mixed_steps_by_previously_closed_count=carried,
                  terminal_arities=shorter,elapsed_seconds=elapsed)
    (HERE / ('rankings_pilot.json' if args.pilot else 'rankings.json')).write_text(
        json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(sum(shorter.values()), 'closures,', round(elapsed, 3), 'seconds')


if __name__ == '__main__':
    main()
