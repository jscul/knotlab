"""Necessary family-wide partition and fresh-grant checks on fixed fresh draws."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations

from control_draws import OUT, read, save
from control_role_rows import signed_table
from census_weighted import canonical_weighted
from end_operator import End, _demands, step
from explosive_symmetry import inverse, profile_move


FAMILY_LIMIT = 25_000


def mask(names):
    return sum(1 << x for x in names)


def support_image(names, movement):
    return tuple(sorted(movement[x] for x in names))


def candidate_options(measurement, movement):
    kept = set(measurement['all_sign']['candidates'])
    return tuple(sorted({(support_image(p['support'], movement), support_image(p['fresh_twins'], movement),
                          support_image(p['inputs'], movement))
                         for p in measurement['screen']['predictions'] if p['name'] in kept}))


def disjoint_families(options):
    supports = tuple(mask(h) for h, _, _ in options)

    def visit(start, used, family):
        for i in range(start, len(options)):
            if supports[i] & used:
                continue
            current = (*family, i)
            yield current, used | supports[i]
            yield from visit(i + 1, used | supports[i], current)

    yield from visit(0, 0, ())


def precompute(c):
    minima = []
    for x, row in enumerate(c):
        levels = defaultdict(int)
        for y, signed in enumerate(row):
            if x != y:
                levels[signed] |= 1 << y
        minima.append(tuple(sorted(levels.items())))
    differing = tuple(tuple(mask(z for z in range(len(c)) if z not in (x, y) and c[x][z] != c[y][z])
                            for y in range(len(c))) for x in range(len(c)))
    return tuple(minima), differing


def previous_partition(inputs, old, c, differing):
    groups = []
    for x in inputs:
        for group in groups:
            y = group[0]
            if c[x][y] < 0 and not (differing[x][y] & old):
                group.append(x)
                break
        else:
            groups.append([x])
    return tuple(tuple(group) for group in groups)


def family_result(members, all_names, c, minima, differing):
    fresh = mask(x for _, f, _ in members for x in f)
    old = all_names ^ fresh
    if old.bit_count() < 3:
        return 'previous_carrier_arity', (), None
    inputs = tuple(sorted(x for _, _, names in members for x in names))
    x_set = mask(inputs)
    old_choices = {}
    for support, _, names in members:
        current = mask(support)
        for x in names:
            lowest, eligible = next((value, names & old) for value, names in minima[x] if names & old)
            if lowest >= 0 or (eligible & ~current).bit_count() < 2:
                return 'older_row_minimum', (), None
            old_choices[x] = eligible
    groups = previous_partition(inputs, old, c, differing)
    owner = {x: i for i, group in enumerate(groups) for x in group}
    parents = tuple(tuple(sorted(owner[x] for x in names)) for _, _, names in members)
    if any(len(set(p)) < len(p) for p in parents):
        return 'two_inputs_same_parent', groups, None
    demand, blocks = _demands(parents)
    if any(max(3 - len(names), 1, d) != len(f) for (_, f, names), d in zip(members, demand, strict=True)):
        return 'family_fresh_grant', groups, None

    unused = old & ~x_set
    deficits = []
    for group in groups:
        group_mask = mask(group)
        possible = unused
        for x in group:
            if (group_mask ^ (1 << x)) & ~old_choices[x]:
                return 'consumed_names_not_at_common_minimum', groups, None
            possible &= old_choices[x]
        need = max(0, 3 - len(group))
        if possible.bit_count() < need:
            return 'previous_holder_arity', groups, None
        if need:
            deficits.append((possible, need))
    # A preceding name can fill at most two of these missing incidences.
    # The union bound is a relaxation of the full allocation problem.
    candidates = 0
    for possible, _ in deficits:
        candidates |= possible
    if sum(need for _, need in deficits) > 2 * candidates.bit_count():
        return 'previous_capacity_union', groups, None

    plan = step(End({i: len(f) for i, (_, f, _) in enumerate(members)}, blocks), 'nae')
    assert plan.status == 'extend'
    profile = tuple(sorted((tuple(sorted(members[h][0] for h in child)), price)
                           for child, price in zip(plan.parents, plan.fresh, strict=True)))
    return 'necessary_checks_pass', groups, profile


def assess(options, c):
    total = (1 << len(c)) - 1
    minima, differing = precompute(c)
    status = Counter()
    survivors = {}
    for checked, (numbers, _) in enumerate(disjoint_families(options), start=1):
        if checked > FAMILY_LIMIT:
            return {'undecided': 'disjoint family limit', 'tested_before_limit': FAMILY_LIMIT}
        result, groups, profile = family_result(tuple(options[i] for i in numbers), total, c, minima, differing)
        status[result] += 1
        if result == 'necessary_checks_pass':
            survivors[numbers] = {'partition': groups, 'profile': profile}
    return {'families': status, 'survivors': survivors}


def actual_family(stage, measurement, options, movement):
    actual = set(measurement['screen']['actual_loose'])
    family = []
    for row in stage['rows']:
        f = actual.intersection(row)
        if f:
            family.append((support_image(row, movement), support_image(f, movement),
                           support_image(set(row) - f, movement)))
    return tuple(sorted(options.index(orientation) for orientation in family))


def observed_partition(stage, family, options, movement):
    consumed = {x for i in family for x in options[i][2]}
    answer = []
    cutoff = stage['limits'][-2]
    for older in stage['rows'][:cutoff]:
        part = tuple(x for x in support_image(older, movement) if x in consumed)
        if part:
            answer.append(part)
    assert sum(map(len, answer)) == len(consumed)
    return tuple(sorted(answer))


def draw_assessment(stage, cached):
    m = stage['weights']['inherited']
    if 'unread' in m:
        return {'undecided': 'exact pair table unread'}
    n = stage['width']
    counts = dict(zip(combinations(range(n), 2), m['disagreement_counts'], strict=True))
    table = canonical_weighted(n, m['total'], counts)
    movement = inverse(table.order)
    options = candidate_options(m, movement)
    if table.key not in cached:
        original = signed_table(n, m['total'], m['disagreement_counts'])
        canonical = tuple(tuple(original[x][y] for y in table.order) for x in table.order)
        cached[table.key] = (options, assess(options, canonical))
    other, result = cached[table.key]
    assert other == options
    if 'undecided' in result:
        return result
    actual = actual_family(stage, m, options, movement)
    ok = result['survivors']
    assert actual in ok
    assert ok[actual]['partition'] == observed_partition(stage, actual, options, movement)
    expected = profile_move(stage['profile'], movement)
    assert ok[actual]['profile'] == expected
    latest = set(i for family in ok for i in family)
    possibly_loose = {table.order[x] for i in latest for x in options[i][1]}
    prior = set(m['all_sign']['remaining_spent'])
    still = prior & possibly_loose
    return {'entering_false_indices': sorted(prior), 'remaining_false_indices': sorted(still),
            'removed_false_indices': sorted(prior - still), 'family_count_by_reason': result['families'],
            'independent_profile_count': len({finding['profile'] for finding in ok.values()}),
            'necessary_family_count': len(ok), 'actual_latest_count': len(actual),
            'oriented_holding_count_before_family': len(options), 'oriented_holding_count_after_family': len(latest)}


def summarize(records):
    totals = {a: Counter() for a in (1, 2)}
    reasons = {a: Counter() for a in (1, 2)}
    for record in records:
        a = record['age']
        target = totals[a]
        target['observations'] += 1
        if 'undecided' in record:
            target['undecided'] += 1
            continue
        target['complete'] += 1
        for category in ('entering_false_indices', 'removed_false_indices', 'remaining_false_indices'):
            target[category] += len(record[category])
            target[f'observations_with_{category}'] += bool(record[category])
        target['observations_with_one_necessary_family'] += record['necessary_family_count'] == 1
        target['observations_with_one_necessary_priced_profile'] += record['independent_profile_count'] == 1
        reasons[a].update(record['family_count_by_reason'])
    return {a: {'counts': row, 'family_count_by_reason': reasons[a]} for a, row in totals.items()}


def main():
    data = read(OUT / 'control_draws.json.gz')['nae']
    panels = {}
    cached = {}
    for panel, sample in data.items():
        rows = [dict(draw=item['draw'], age=stage['age'], **draw_assessment(stage, cached))
                for item in sample['draws'] for stage in item['stages']]
        panels[panel] = {'summary': summarize(rows), 'details': rows}
        print(panel, panels[panel]['summary'], flush=True)
    save(OUT / 'control_family_screen.json', dict(panels=panels, max_families_per_table=FAMILY_LIMIT,
         distinct_table_calculations=len(cached), fixed_draw_sha256=sha256((OUT / 'control_draws.json.gz').read_bytes()).hexdigest()))


if __name__ == '__main__':
    main()
