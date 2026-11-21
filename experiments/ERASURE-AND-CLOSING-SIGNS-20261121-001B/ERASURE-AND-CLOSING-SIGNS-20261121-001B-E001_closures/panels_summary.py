"""Calculate the registered draw, component, birth and cut denominators."""

from collections import Counter
import gzip
import json
from math import log, sqrt

from job import write
from panels_sources import COUNTS, LAWS, OUT
from controls import interval


def read(path):
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as file:
        return json.load(file)


def fraction(a, b):
    return {'numerator': a, 'denominator': b, 'estimate': a / b if b else None}


def draw_probability(entries, predicate):
    count = sum(predicate(d) for d in entries)
    eligible_unknown = sum(d['termination'] in ('holder_cap', 'name_cap') and not predicate(d) for d in entries)
    n = len(entries)
    result = fraction(count, n)
    result['unresolved_draws'] = eligible_unknown
    result['95pct'] = [interval(count, n)[0], interval(count + eligible_unknown, n)[1]]
    return result


def component_fraction(entries, panel, law, minimum_arity):
    qualifying = [[x for s in d['cuts'] for x in s['new_closing_components'] if x['closing_arity'] >= minimum_arity]
                  for d in entries]
    observed = sum(map(len, qualifying))
    positive = sum(e['operator_positive'] for events in qualifying for e in events)
    per_draw_max = 3 if panel == 'M' else 1
    upper = sum(per_draw_max - len(events) for d, events in zip(entries, qualifying, strict=True)
                if d['termination'] in ('holder_cap', 'name_cap'))
    estimate = fraction(positive, observed)
    estimate['possible_extra_components'] = upper
    estimate['odd_operator_negative'] = observed - positive
    estimate['undefined_possible'] = observed == 0
    if law == 'nae':
        return dict(estimate, method='unsigned NAE has no parity sign', **{'95pct': None})
    if not observed:
        return dict(estimate, method='conditional share', **{'95pct': [0., 1.] if upper else None})
    if panel == 'M':
        n = len(entries)
        delta = 3 * sqrt(log(40) / (2 * n))
        easy = [max(0., (positive - n * delta) / (observed + upper)),
                min(1., (positive + upper + n * delta) / (observed + upper))]
        return dict(estimate, method='independent-draw Hoeffding ratio', **{'95pct': easy})
    cp = [interval(positive, observed + upper)[0], interval(positive + upper, observed + upper)[1]]
    return dict(estimate, method='conditional Clopper-Pearson', **{'95pct': cp})


def count_cuts(cuts, minimum_arity=0):
    hist = Counter({x: 0 for x in range(3)})
    total_births = positive_cut = positive_births = 0
    closing_cut_births = other_births_in_closing_cut = old_closed = new_held_twice = 0
    components = Counter()
    zero_by_arity = Counter()
    for cut in cuts:
        events = [e for e in cut['new_closing_components'] if e['closing_arity'] >= minimum_arity]
        hist[len(events)] += 1
        positive_cut += any(e['operator_positive'] for e in events)
        components['closed'] += len(events)
        components['operator_positive'] += sum(e['operator_positive'] for e in events)
        total_births += len(cut['births'])
        positive_births += cut['positive_grants']
        old_closed += cut['preceding_closed_pieces']
        new_held_twice += cut['new_held_twice']
        if events:
            closing_cut_births += len(cut['births'])
            other_births_in_closing_cut += cut['positive_grants']
        for birth in cut['births']:
            if birth['fresh'] == 0 and len(birth['inputs']) >= minimum_arity:
                zero_by_arity[len(birth['inputs'])] += 1
    assert sum(zero_by_arity.values()) == components['closed']
    components['operator_negative'] = components['closed'] - components['operator_positive']
    return {'completed_cuts': len(cuts), 'cuts_by_new_closing_component_count': hist,
            'cut_fractions_by_new_closure_count': {k: fraction(v, len(cuts)) for k, v in sorted(hist.items())},
            'cuts_with_a_positive_component': fraction(positive_cut, len(cuts)), 'new_components': components,
            'births': total_births, 'positive_grants': positive_births, 'zero_by_arity': zero_by_arity,
            'newly_held_twice': new_held_twice, 'preceding_closed_piece_exposures': old_closed,
            'births_on_closing_cuts': closing_cut_births, 'other_births_on_closing_cuts': other_births_in_closing_cut}


def union_receipts(cuts):
    simultaneous = []
    all_patterns = Counter()
    kinds = Counter()
    for s in cuts:
        receipt = s.get('union_signs')
        if receipt is None:
            continue
        terminal = receipt['ordered_terminal_holders']
        all_patterns[len(terminal)] += len(receipt['scenarios'])
        new = s['new_closing_components']
        if len(new) != 2:
            continue
        both = {e['holder']: e['operator_positive'] for e in new}
        outcomes = tuple(int(both[h]) for h in terminal)
        literal = tuple((r['scalar_admits'], r['operator_admits']) for r in receipt['scenarios'])
        kinds[''.join(map(str, outcomes))] += 1
        simultaneous.append({'age': s['age'], 'outcomes': outcomes, 'scalar_and_operator': literal})
    return {'patterns_evaluated_by_number_of_actual_terminal_holders': all_patterns,
            'simultaneous_cuts': len(simultaneous), 'simultaneous_by_positive_flags': kinds,
            'simultaneous_by_age': Counter(c['age'] for c in simultaneous),
            'simultaneous_pattern_verdicts': [(k, v) for k, v in sorted(Counter(
                tuple(tuple(i for i in arm) for arm in c['scalar_and_operator']) for c in simultaneous).items())]}


def panel_law(records, panel, law):
    entries = [d['laws'][law] for d in records if d['panel'] == panel]
    assert len(entries) == COUNTS[panel]
    cuts = [cut for d in entries for cut in d['cuts']]
    end = Counter(x['termination'] for x in entries)
    families = {}
    for label, floor in (('all_arities', 0), ('arity_at_least_three', 3)):
        has = lambda d: any(e['closing_arity'] >= floor for c in d['cuts'] for e in c['new_closing_components'])
        admits = lambda d: any(e['operator_positive'] and e['closing_arity'] >= floor
                               for c in d['cuts'] for e in c['new_closing_components'])
        full_and_eligible = lambda d: any(c['whole_closed'] and any(e['closing_arity'] >= floor
                                            for e in c['new_closing_components']) for c in d['cuts'])
        full_and_admits = lambda d: any(c['whole_closed'] and any(e['operator_positive'] and e['closing_arity'] >= floor
                                            for e in c['new_closing_components']) for c in d['cuts'])
        overall = count_cuts(cuts, floor)
        share = component_fraction(entries, panel, law, floor)
        families[label] = {'at_least_one_closure': draw_probability(entries, has),
                           'at_least_one_admitting_closure': draw_probability(entries, admits) if law == 'parity' else None,
                           'eligible_whole_closure': draw_probability(entries, full_and_eligible),
                           'admitting_whole_closure': draw_probability(entries, full_and_admits) if law == 'parity' else None,
                           'per_component_admission': share,
                           'descriptive_closures_per_funded_birth': fraction(share['denominator'], overall['births']),
                           'descriptive_positive_per_funded_birth': fraction(share['numerator'], overall['births']) if law == 'parity' else None,
                           'per_cut_all': overall,
                           'per_cut_by_age': {str(age): count_cuts([c for c in cuts if c['age'] == age], floor)
                                              for age in range(1, 5)}}
    impossible = ['All ordinary not-all-equal births keep a fresh distinction.'] if law == 'nae' else []
    if panel in ('E', 'M'):
        impossible.append('The certified exponential ring does not close, so the whole cannot close.')
    return {'draws': len(entries), 'lawful_founders': sum(d['founder']['lawful'] for d in entries),
            'essential_founders': sum(d['founder']['essential'] for d in entries), 'termination_counts': end,
            'whole_closure': draw_probability(entries, lambda d: d['termination'] == 'closed'),
            'max_holders': max(len(c['after_rows']) for c in cuts),
            'max_distinctions': max(sum(len(k['names']) for k in c['components']) for c in cuts),
            'endpoints': families, 'signed_parity_applicable': law == 'parity',
            'structural_zero_explanations': impossible,
            'joint_sign_receipts': union_receipts(cuts) if law == 'parity' and panel == 'M' else None}


def main():
    all_records = read(OUT / 'panels_histories.json.gz')
    result = {panel: {law: panel_law(all_records, panel, law) for law in LAWS} for panel in COUNTS}
    write('panels_summary.json', result)
    for panel in COUNTS:
        for law in LAWS:
            d = result[panel][law]
            a = d['endpoints']['all_arities']
            c = a['per_cut_all']
            print(panel, law, d['lawful_founders'], d['termination_counts'], c['completed_cuts'], c['births'],
                  c['zero_by_arity'], c['new_components'], a['at_least_one_closure'], a['per_component_admission'], flush=True)


if __name__ == '__main__':
    main()
