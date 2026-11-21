"""Group complete pair tables, keeping next counts and named profiles distinct."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations

from explosive_rates import LAWS, WEIGHTS
from explosive_stages import read, write
from explosive_symmetry import inverse, profile_match, profile_move, rows_move, table_moves
from census_compare import named_nae_state
from census_rate_tables import as_tuple, fingerprints
from census_stages import mask_of, reduced
from census_verify_wider import separating_check
from controls import interval
from local_parts import physical_parts
from multiple_meetings import multiple_tree


def group_data(key, records, law):
    moves, automorphisms = table_moves(key)
    cases = []
    canon_profiles, canon_states = set(), set()
    profile_types = []
    for record in records:
        assert record['ordering']['automorphisms'] == automorphisms
        move = inverse(record['ordering']['order'])
        stage = record['stage']
        profile = profile_move(stage['profile'], move)
        canon_profiles.add((stage['next_status'], profile))
        names = rows_move(stage['rows'], move)
        if law == 'nae':
            def read_state(supports):
                return named_nae_state(supports)
        else:
            def read_state(supports):
                return reduced(map(mask_of, supports))
        state = read_state(names)
        canon_states.add(state)
        profile_mover = next((m for m in moves if profile_move(profile, m) != profile), None)
        state_mover = next((m for m in moves if read_state(rows_move(names, m)) != state), None)
        status = stage['next_status']
        profile_label = None
        for i, (s, p, movable) in enumerate(profile_types):
            if s == status and (p == profile or (movable and profile_mover is not None and profile_match(key, p, profile) is not None)):
                profile_label = i
                break
        if profile_label is None:
            profile_label = len(profile_types)
            profile_types.append((status, profile, profile_mover is not None))
        cases.append(dict(record=record, canonical_profile=profile, canonical_state=state,
                          unmarked_profile=profile_label, profile_mover=profile_mover, state_mover=state_mover))
    return dict(cases=cases, automorphisms=automorphisms,
                named_profile_ambiguous=len(canon_profiles) > 1 or any(c['profile_mover'] is not None for c in cases),
                named_state_ambiguous=len(canon_states) > 1 or any(c['state_mover'] is not None for c in cases),
                unmarked_profile_types=len(profile_types),
                scalar_ambiguous=len({(c['stage']['next_status'], c['stage']['next_count']) for c in records}) > 1,
                ages=tuple(sorted({c['stage']['age'] for c in records})))


def matrix_counts(width, ordering):
    return dict(zip(combinations(range(width), 2), ordering['counts'], strict=True))


def gather(physical, rates, law, weighting):
    known = []
    unread = []
    sources = {item['id']: item for item in physical[law]['sources']}
    for result in rates['reads'][law]:
        source, age = sources[result['source_id']], result['age']
        stage = source['stages'][age - 1]
        ordering = result['weights'][weighting]
        if 'unread' in ordering:
            unread.append((source['id'], age, ordering['unread']))
            continue
        counts = matrix_counts(stage['width'], ordering)
        known.append(dict(source=source, stage=stage, ordering=ordering, key=as_tuple(ordering['key']),
                          fingerprint=fingerprints(stage['width'], ordering['total'], counts)))
    return known, unread


def rank(a, b):
    return (max(a['source']['source_width'], b['source']['source_width']), a['stage']['width'],
            len(a['source']['source_rows']) + len(b['source']['source_rows']), a['stage']['age'] + b['stage']['age'],
            a['source']['id'], b['source']['id'], a['stage']['age'], b['stage']['age'])


def witness(a, b, law, move=None):
    records = [c['record'] for c in (a, b)]
    shapes = []
    for c, r in zip((a, b), records, strict=True):
        s = r['stage']
        canonical = inverse(r['ordering']['order'])
        current_profile = c['canonical_profile']
        if move is not None and len(shapes) == 1:
            canonical = tuple(move[x] for x in canonical)
            current_profile = profile_move(current_profile, move)
        shapes.append(dict(source_id=r['source']['id'], source=r['source']['source_rows'], age=s['age'],
                           next_count=s['next_count'], status=s['next_status'],
                           old_to_common_names=canonical, reached=rows_move(s['rows'], canonical),
                           next_profile=current_profile))
    result = dict(rank=rank(*records), pair=shapes, self_symmetry=move, table_key=records[0]['key'])
    if law == 'parity':
        old, new = [reduced(map(mask_of, side['reached'])) for side in shapes]
        result['least_separating_order_support'] = separating_check(old, new, records[0]['stage']['width'])
    return result


def minima(groups, law):
    found = {}

    def add(label, a, b, move=None):
        score = rank(a['record'], b['record'])
        if label not in found or score < found[label][0]:
            found[label] = (score, a, b, move)

    for group in groups:
        for a in group['cases']:
            if a['profile_mover'] is not None:
                add('named_profile_by_symmetry', a, a, a['profile_mover'])
        for a, b in combinations(group['cases'], 2):
            r, s = [c['record']['stage'] for c in (a, b)]
            if (r['next_status'], r['next_count']) != (s['next_status'], s['next_count']):
                add('scalar', a, b)
            if a['unmarked_profile'] != b['unmarked_profile']:
                add('unmarked_profile', a, b)
            if a['canonical_profile'] != b['canonical_profile']:
                add('named_profile_between_records', a, b)
    return {label: witness(a, b, law, move) for label, (_, a, b, move) in found.items()}


def screen(records):
    by_width = defaultdict(list)
    for result in records:
        by_width[result['stage']['width']].append(result)
    passes = Counter()
    for group in by_width.values():
        for a, b in combinations(group, 2):
            classes = ['all']
            lhs, rhs = a['stage'], b['stage']
            if (lhs['next_status'], lhs['next_count']) != (rhs['next_status'], rhs['next_count']):
                classes.append('different_scalar')
            reason = 'equal_complete_table'
            if a['fingerprint'][1] != b['fingerprint'][1]:
                reason = 'rate_multiset'
            elif a['fingerprint'][2] != b['fingerprint'][2]:
                reason = 'incident_rate_multisets'
            elif a['key'] != b['key']:
                reason = 'complete_permutation_check'
            for case in classes:
                passes[f'{case}:{reason}'] += 1
    return dict(passes)


def compare(physical, rates, law, weighting):
    records, unread = gather(physical, rates, law, weighting)
    by_key = defaultdict(list)
    by_literal = defaultdict(list)
    for item in records:
        by_key[item['key']].append(item)
        trace = item['ordering']
        exact = tuple(Fraction(c, trace['total']) for c in trace['counts'])
        by_literal[item['stage']['width'], exact].append(item)
    tally = Counter(observations=len(records), classes=len(by_key), literal_classes=len(by_literal),
                    original_named=sum(r['source']['named_source_multiplicity'] for r in records))
    groups = []
    membership = {}
    records_out = []
    for i, (key, candidates) in enumerate(by_key.items()):
        group = group_data(key, candidates, law)
        groups.append(group)
        tally['multiple_records_classes'] += len(candidates) > 1
        tally['cross_age_classes'] += group['ages'] == (1, 2)
        for flag in ('scalar_ambiguous', 'named_profile_ambiguous', 'named_state_ambiguous'):
            tally[flag] += group[flag]
        tally['unmarked_profile_ambiguous'] += group['unmarked_profile_types'] > 1
        tally['classes_with_a_profile_moving_symmetry'] += any(c['profile_mover'] is not None for c in group['cases'])
        tally['classes_with_a_state_moving_symmetry'] += any(c['state_mover'] is not None for c in group['cases'])
        for case in group['cases']:
            r = case['record']
            index = (r['source']['id'], r['stage']['age'])
            membership[index] = dict(group=i, ambiguous_scalar=group['scalar_ambiguous'],
                                     ambiguous_named_profile=group['named_profile_ambiguous'],
                                     ambiguous_unmarked_profile=group['unmarked_profile_types'] > 1)
            records_out.append({'source_id': index[0], 'age': index[1], 'group': i,
                                'unmarked_profile': case['unmarked_profile'],
                                'profile_symmetry_witness': case['profile_mover'],
                                'state_symmetry_witness': case['state_mover']})
    tally['literal_scalar_ambiguities'] = sum(len({(i['stage']['next_status'], i['stage']['next_count']) for i in items}) > 1
                                             for items in by_literal.values())
    tally['literal_parent_profile_ambiguities'] = sum(len({(i['stage']['next_status'], as_tuple(i['stage']['profile']))
                                                          for i in items}) > 1 for items in by_literal.values())
    return dict(counts=dict(tally), pair_screen=screen(records), minima=minima(groups, law),
                unread=unread, table_members=records_out), membership


def weighting_change(physical, rates, law):
    old_read = {}
    status = Counter()
    max_difference = Fraction(0)
    witness = None
    observations = []
    sources = {s['id']: s for s in physical[law]['sources']}
    for result in sorted(rates['reads'][law], key=lambda r: (r['source_id'], r['age'])):
        source_id, age = result['source_id'], result['age']
        stage = sources[source_id]['stages'][age - 1]
        left, right = [result['weights'][w] for w in WEIGHTS]
        if 'unread' in left or 'unread' in right:
            status['unread'] += 1
            continue
        n = stage['width']
        observed_left, observed_right = [matrix_counts(n, r) for r in (left, right)]
        ls, rs = left['total'], right['total']
        if age == 1:
            old_read[source_id] = rs, observed_right
        elif source_id in old_read:
            d, values = old_read[source_id]
            assert all(c * rs == observed_right[pair] * d for pair, c in values.items())
            status['second_stage_old_marginal_reproduced'] += 1
        changes = 0
        for pair in observed_left:
            delta = observed_left[pair] * rs - observed_right[pair] * ls
            if delta:
                changes += 1
                if abs(delta) * max_difference.denominator > max_difference.numerator * ls * rs:
                    max_difference = Fraction(abs(delta), ls * rs)
                    witness = dict(source_id=source_id, age=age, pair=pair,
                                   uniform=(observed_left[pair], ls), inherited=(observed_right[pair], rs))
        same = as_tuple(left['key']) == as_tuple(right['key'])
        status['observations_with_changed_named_rates'] += changes > 0
        status['observations_with_changed_unmarked_rates'] += not same
        status['pairs_changed'] += changes
        status['pairs_read'] += len(observed_left)
        observations.append(dict(source_id=source_id, age=age, pairs_read=len(observed_left),
                                 pairs_changed=changes, table_key_changed=not same))
    return dict(read=len(observations), counts=dict(status), maximum_change=(max_difference.numerator, max_difference.denominator),
                maximum_change_witness=witness, observations=observations)


def part_c_failure(stage):
    for names, rows in physical_parts(tuple(map(tuple, stage['rows']))):
        if len(names) > 10 and len(rows) >= 3 and any(len(s) > 3 for s in rows) and not multiple_tree(rows):
            meetings = [set(a) & set(b) for a, b in combinations(rows, 2) if set(a) & set(b)]
            return {'part_width': len(names), 'holders': len(rows), 'arities': tuple(sorted(map(len, rows))),
                    'single_meetings': sum(len(s) == 1 for s in meetings),
                    'meetings': len(meetings), 'includes_cycle': len(meetings) >= len(rows)}
    return None


def sample_counts(physical, law, member, changes):
    draws = physical[law]['samples']['draws']
    changed = {(w['source_id'], w['age']): w for w in changes['observations']}
    labels = ('scalar', 'named_profile', 'unmarked_profile')
    by_age = {}
    detail = []
    for age in (1, 2):
        tally = Counter({f'{w}:ambiguous_{label}': 0 for w in WEIGHTS for label in labels})
        for draw in draws:
            attempt = draw['attempts'][age - 1] if len(draw['attempts']) >= age else 'no_prior_cut'
            tally[attempt] += 1
            if attempt != 'births':
                continue
            stage = draw['stages'][age - 1]
            idx = draw['source_id'], age
            tally[f"next_{stage['next_status']}"] += 1
            for weighting in WEIGHTS:
                element = member[weighting].get(idx)
                if element is None:
                    tally[f'{weighting}:unread'] += 1
                else:
                    tally[f'{weighting}:read'] += 1
                    for label in labels:
                        tally[f'{weighting}:ambiguous_{label}'] += element[f'ambiguous_{label}']
            failure = part_c_failure(stage) if law == 'nae' else None
            if law == 'nae':
                tally['part_C_hypothesis_fails'] += failure is not None
            flags = changed.get(idx)
            if flags is not None:
                tally['weight_changes_some_pair'] += flags['pairs_changed'] != 0
            detail.append(dict(draw=draw['draw'], source_id=draw['source_id'], age=age, next_status=stage['next_status'],
                               next_count=stage['next_count'], weights={w: member[w].get(idx) for w in WEIGHTS},
                               part_C_failure=failure, changed_pair_count=None if flags is None else flags['pairs_changed']))
        n = tally['births']
        intervals = {k: interval(v, n) for k, v in tally.items() if n and ('ambiguous' in k or k.startswith('part_C'))}
        by_age[age] = dict(draws=len(draws), reached=n, **dict(tally), intervals=intervals)
    return dict(by_age=by_age, draws=detail)


def main():
    physical = read('explosive_stages.json.gz')
    rates = read('explosive_rates.json.gz')
    output = {}
    for law in LAWS:
        summaries, members = {}, {}
        for weight in WEIGHTS:
            if law == 'parity' and weight == 'inherited':
                summaries[weight], members[weight] = summaries['uniform'], members['uniform']
            else:
                summaries[weight], members[weight] = compare(physical, rates, law, weight)
            print(law, weight, summaries[weight]['counts'], flush=True)
        changes = weighting_change(physical, rates, law)
        samples = sample_counts(physical, law, members, changes)
        output[law] = dict(weights=summaries, weighting_change=changes, fresh_samples=samples)
    proven_outside = []
    for source in physical['nae']['sources']:
        for stage in source['stages']:
            tested = part_c_failure(stage)
            assert tested is not None
            proven_outside.append(tested | {'source_id': source['id'], 'age': stage['age']})
    output['part_C_failure'] = proven_outside
    write('explosive_comparison.json.gz', output)


if __name__ == '__main__':
    main()
