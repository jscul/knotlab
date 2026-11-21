"""Test every hypothesized newest family using only an indexed pair table."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import isqrt
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PRIOR = 'LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A'
sys.path.insert(0, str(ROOT / 'experiments' / PRIOR / (PRIOR + '-E001_loose_roles')))
from role_options import analyze, selections, derive_old_bounds, parent_covers
from previous_cut import End, proposals, step, evaluate


def read_table(path):
    rates = [Fraction(x) for x in json.loads(path.read_text())]
    width = (1 + isqrt(1 + 8 * len(rates))) // 2
    if width * (width - 1) // 2 != len(rates):
        raise ValueError('Need one marginal per unordered pair.')
    return width, rates


def previous_parents(correlation, old, inputs):
    """Use the necessary and sufficient physical relation on assumed previous loose names."""
    pending = set(inputs)
    groups = []
    while pending:
        x = min(pending)
        siblings = {y for y in pending - {x} if correlation[x][y] < 0 and all(
            correlation[x][z] == correlation[y][z] for z in old - {x, y})}
        group = {x} | siblings
        groups.append(tuple(sorted(group)))
        pending -= group
    return tuple(groups)


def hypothetical_price(options, packed, groups):
    current = [options[i] for i in packed]
    by_name = {x: i for i, group in enumerate(groups) for x in group}
    prior_parents = [tuple(sorted(by_name[x] for x in row['inputs'])) for row in current]
    if any(len(set(parents)) != len(parents) for parents in prior_parents):
        return 'two inputs in one earlier parent', None
    if any(n > 1 and len(parents) > 1 for parents, n in Counter(prior_parents).items()):
        return 'repeated multiparent birth', None
    witnesses = tuple(tuple(i for i, ps in enumerate(prior_parents) if j in ps) for j in range(len(groups)))
    end = End({i: len(row['fresh']) for i, row in enumerate(current)}, witnesses)
    proposed = proposals(end)
    demand = Counter(i for p in proposed for i in p)
    granted = [max(1, 3 - len(ps), demand[i]) for i, ps in enumerate(prior_parents)]
    measured = [len(row['fresh']) for row in current]
    if granted != measured:
        return 'newest fresh price', {'due': granted, 'claimed': measured}
    next_cut = step(end, 'nae')
    assert next_cut.status == 'extend'
    named = sorted((tuple(sorted(tuple(current[i]['support']) for i in ps)), q)
                   for ps, q in zip(next_cut.parents, next_cut.fresh, strict=True))
    return 'paid', {'previous_parent_classes': groups, 'previous_child_roster': prior_parents,
                    'witnesses': witnesses, 'next_groups': proposed, 'next_priced_roster': named}


def screen(n, rates, weighting):
    scale, corr, ternaries, initial, options = analyze(n, rates)
    # Use only the data table here. The last comparison with the physical reference runs separately.
    entered = list(selections(options)); findings = []
    for packed in entered:
        selected = [options[i] for i in packed]
        fresh = {name for row in selected for name in row['fresh']}
        inputs = {name for row in selected for name in row['inputs']}
        old = set(range(n)) - fresh
        entry = {'selected': packed, 'fresh': sorted(fresh), 'inputs': sorted(inputs)}
        if weighting == 'inherited':
            groups = previous_parents(corr, old, inputs)
            reason, witness = hypothetical_price(options, packed, groups)
            entry['partition'] = groups
            entry['partition_price'] = reason
            if witness is not None:
                entry['partition_calculation'] = witness
        bounds = derive_old_bounds(scale, corr, ternaries, options, packed, weighting)
        entry['candidate_predecessor_supports_per_input'] = {u: len(choices) for u, choices in bounds.items()}
        if not bounds:
            entry['complete_old_assignments'] = 0
            entry['branch_result'] = 'no complete set of possible earlier companion bounds'
            findings.append(entry)
            continue
        old_counts = Counter(); viable = []
        for holders in parent_covers(bounds):
            if weighting == 'inherited':
                physical_groups = {tuple(sorted(set(h) & inputs)) for h in holders}
                if physical_groups != set(groups):
                    old_counts['forbidden previous loose partition'] += 1
                    continue
            result, detail = evaluate(n, options, packed, holders)
            old_counts[result] += 1
            if result == 'viable':
                viable.append(dict(holders=holders, **detail))
        entry['complete_old_assignments'] = sum(old_counts.values())
        entry['older_costs'] = dict(old_counts)
        entry['surviving_assignments'] = viable
        entry['branch_result'] = 'older assignments survive' if viable else 'no admissible older assignment'
        findings.append(entry)
    return dict(weighting=weighting, scale=scale, n=n, per_name=initial, options=options,
                branches=findings, necessary_branch_count=len(findings),
                outcomes=Counter(e['branch_result'] for e in findings),
                partition_price_outcomes=Counter(e.get('partition_price','not applied') for e in findings))


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(); parser.add_argument('weighting', choices=['inherited', 'uniform'])
    parser.add_argument('--table', type=Path); args = parser.parse_args()
    n, rates = read_table(args.table or OUT / f'target_{args.weighting}.json')
    data = screen(n, rates, args.weighting)
    (OUT / f'branches_{args.weighting}.json').write_text(json.dumps(data, indent=2) + '\n')
    live = [b for b in data['branches'] if b.get('surviving_assignments')]
    print('options', len(data['options']), 'families', data['necessary_branch_count'],
          'after partition and price', data['partition_price_outcomes'], 'after older holders', data['outcomes'],
          'surviving complete assignments', sum(len(b['surviving_assignments']) for b in live), flush=True)
    print('surviving families', [b['selected'] for b in live])


if __name__ == '__main__':
    main()
