"""Fresh named controls using both word weightings and the same source draws."""

from collections import Counter
from functools import cache
from hashlib import sha256
from itertools import combinations
from math import factorial
from random import Random

from control_measure import OUTPUT, TICKET, WEIGHTS, binary_table, parity_table, record, save, stages, width
from control_role_rows import TESTS
from explosive_rates import nae_rates
from explosive_stages import align_replay, indexed_rings, ring_images, ring_source
from census_stages import connected_archive
from controls import interval


LAWS = ('nae', 'parity')
PANELS = ('small', 'explosive')


def source_choice(rng, panel, small, rings):
    if panel == 'explosive':
        pattern = rng.choice(rings)
        indexed = ring_source(pattern)
        canonical = ring_source(min(ring_images(pattern)))
        return indexed.rows, canonical.rows, {'indexed_pattern': pattern}
    n = rng.randrange(3, 9)
    named_weights = tuple(factorial(n) // x.automorphisms for x in small[n])
    ticket = rng.randrange(sum(named_weights))
    for i, (source, count) in enumerate(zip(small[n], named_weights, strict=True)):
        if ticket < count:
            return source.rows, source.rows, {'source_archive_index': i, 'named_multiplicity': count,
                                              'named_width_denominator': sum(named_weights)}
        ticket -= count
    raise AssertionError('weighted source draw was out of bounds')


def numerical(stage, law, weighting):
    if law == 'parity':
        total, counts = parity_table(stage)
        return total, counts, {'method': 'binary nullspace'}
    try:
        total, counts, cost = binary_table(stage, weighting)
        return total, counts, cost | {'method': 'binary distinction contraction'}
    except ValueError as issue:
        try:
            total, counts = nae_rates(stage, weighting)
            return total, counts, {'method': 'integer holder contraction', 'binary_bound': issue.args}
        except ValueError as fallback:
            return None, None, {'unread': (issue.args, fallback.args)}


@cache
def template_observations(source, law):
    template = stages(source, law)
    tables = [{w: numerical(s, law, w) for w in WEIGHTS} for s in template['stages']]
    return template, tables


def rate_dict(width_n, value):
    return dict(zip(combinations(range(width_n), 2), value['disagreement_counts'], strict=True))


def verify_marginal(prior_counts, prior_total, after_width, after):
    later = rate_dict(after_width, after)
    expected_total = after['total']
    assert all(later[pair] * prior_total == count * expected_total for pair, count in prior_counts.items())
    return len(prior_counts)


def fresh_panel(law, panel, small, rings):
    digest = sha256(f'{TICKET}|{law}|{panel}|318792'.encode()).hexdigest()
    rng = Random(int(digest, 16))
    result = []
    for index in range(1, 33):
        basis, canonical, details = source_choice(rng, panel, small, rings)
        renaming = list(range(width(basis)))
        rng.shuffle(renaming)
        names = tuple(tuple(sorted(renaming[x] for x in row)) for row in basis)
        actual = stages(names, law)
        template, templates = template_observations(canonical, law)
        assert actual['attempts'] == template['attempts']
        cut_reports = []
        old_total, old_counts, _ = numerical({'rows': names, 'width': width(names), 'limits': (len(names),)}, law, 'uniform')
        assert old_total is not None
        for stage, model, numbers in zip(actual['stages'], template['stages'], templates, strict=True):
            transport = align_replay(model, stage)
            weights = {}
            for w, (total, counts, cost) in numbers.items():
                if total is None:
                    weights[w] = cost
                    continue
                assigned = {tuple(sorted((transport[a], transport[b]))): c for (a, b), c in counts.items()}
                ordered = {pair: assigned[pair] for pair in combinations(range(stage['width']), 2)}
                weights[w] = record(stage, law, w, total, ordered, cost)
            new = dict(stage, transport_template_to_draw=transport, weights=weights)
            if 'unread' not in weights['inherited']:
                current = weights['inherited']
                if old_counts is not None:
                    new['inherited_preserved_pair_entries'] = verify_marginal(old_counts, old_total, stage['width'], current)
                old_total, old_counts = current['total'], rate_dict(stage['width'], current)
            else:
                old_counts = None
            if all('unread' not in weights[w] for w in WEIGHTS):
                a, b = (weights[w] for w in WEIGHTS)
                new['changed_pair_entries'] = sum(x * b['total'] != y * a['total']
                                                  for x, y in zip(a['disagreement_counts'], b['disagreement_counts'], strict=True))
            cut_reports.append(new)
        actual['stages'] = cut_reports
        result.append(dict(draw=index, source_permutation=renaming, **details, **actual))
    return {'seed_sha256': digest, 'draws': result}


def summarize(population):
    out = []
    trials = population['draws']
    for age in (1, 2):
        status = Counter(r['attempts'][age - 1] if len(r['attempts']) >= age else 'not_attempted' for r in trials)
        observed = [r['stages'][age - 1] for r in trials if len(r['stages']) >= age]
        assert status['births'] == len(observed)
        data = dict(age=age, source_draws=len(trials), observed=len(observed), attempts=status,
                    next_status=Counter(r['next_status'] for r in observed),
                    largest_width=max((r['width'] for r in observed), default=0),
                    observations_changing_word_weight=sum(r.get('changed_pair_entries', 0) > 0 for r in observed),
                    verified_inherited_old_pair_entries=sum(r.get('inherited_preserved_pair_entries', 0) for r in observed),
                    weights={})
        for w in WEIGHTS:
            readable = [r['weights'][w] for r in observed if 'unread' not in r['weights'][w]]
            screened = [r['screen'] for r in readable]
            aggregate = {test: Counter() for test in TESTS}
            for row in screened:
                for key, counts in row['per_test'].items():
                    aggregate.setdefault(key, Counter()).update(counts)
            first_failures = sum(bool(r['historical_false']) for r in screened)
            last_failures = sum(bool(r['surviving_false']) for r in screened)
            data['weights'][w] = dict(read=len(readable), unread=len(observed) - len(readable),
                                      methods=Counter(r['cost']['method'] for r in readable),
                                      actual_loose=sum(len(r['actual_loose']) for r in screened),
                                      actual_spent=sum(r['spent_names'] for r in screened),
                                      after_minimum_spent=aggregate['minimum_and_arity']['retained_spent'],
                                      historical_false_indices=sum(len(r['historical_false']) for r in screened),
                                      after_preliminary_spent=aggregate['unary_binary_input_row']['retained_spent'],
                                      surviving_false_indices=sum(len(r['surviving_false']) for r in screened),
                                      observations_with_historical_false=first_failures,
                                      observations_with_surviving_false=last_failures,
                                      historical_stage_95pct=interval(first_failures, len(screened)) if screened else None,
                                      surviving_stage_95pct=interval(last_failures, len(screened)) if screened else None,
                                      tests=aggregate)
        out.append(data)
    return out


def main():
    catalogue = connected_archive()
    rings = tuple(indexed_rings())
    assert len(rings) == 40
    raw, summaries = {law: {} for law in LAWS}, {law: {} for law in LAWS}
    for law in LAWS:
        for panel in PANELS:
            raw[law][panel] = fresh_panel(law, panel, catalogue[law], rings)
            summaries[law][panel] = summarize(raw[law][panel])
            for a in summaries[law][panel]:
                print(law, panel, a['age'], a['observed'], a['attempts'],
                      [(w, r['read'], r['historical_false_indices'], r['surviving_false_indices']) for w, r in a['weights'].items()],
                      flush=True)
    save(OUTPUT / 'control_panels.json.gz', raw)
    save(OUTPUT / 'control_panel_summary.json', summaries)


if __name__ == '__main__':
    main()
