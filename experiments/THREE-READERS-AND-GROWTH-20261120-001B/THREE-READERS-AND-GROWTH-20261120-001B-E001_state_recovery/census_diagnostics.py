"""State-only recovery tests and physical controls for the ten-distinction census."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations
from math import factorial
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EARLIER = ROOT / 'experiments/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant'
sys.path.insert(0, str(EARLIER))
from census_irredundant import raw_start
from census_verify import covers, exact_candidates, indices, reference_growth, to_mask


@dataclass(frozen=True)
class StateReadings:
    candidates: dict
    mandatory: dict
    single_word: dict
    missing_mandatory: int
    missing_single_word: int
    one_place_repairs: tuple
    loose_candidates: tuple


def union(masks):
    combined = 0
    for mask in masks:
        combined |= mask
    return combined


@cache
def zero_word_mask(width, name):
    return to_mask(word for word in range(1 << width) if not word & (1 << name))


def repaired_words(width, allowed, name):
    zero = zero_word_mask(width, name)
    step = 1 << name
    return (((allowed & zero) << step) | ((allowed & ~zero) >> step)) & ~allowed


def state_readings(width, allowed):
    candidates = exact_candidates(width, tuple(indices(allowed)), 'nae')
    seen = twice = 0
    for excluded in candidates.values():
        twice |= seen & excluded
        seen |= excluded
    assert seen == ((1 << (1 << width)) - 1) ^ allowed
    single_candidate_violation = seen & ~twice
    mandatory = {s: next(indices(excluded & single_candidate_violation))
                 for s, excluded in candidates.items() if excluded & single_candidate_violation}

    derivatives = tuple(repaired_words(width, allowed, name) for name in range(width))
    assert all(derivatives)
    single_word = {}
    for support in candidates:
        precise = seen
        for name, derivative in enumerate(derivatives):
            precise &= derivative if support & (1 << name) else ~derivative
        if precise:
            single_word[support] = next(indices(precise))
    assert single_word.keys() <= mandatory.keys()

    missing_mandatory = seen & ~union(candidates[s] for s in mandatory)
    missing_single_word = seen & ~union(candidates[s] for s in single_word)
    loose_candidates = tuple(tuple(s for s, excluded in candidates.items()
                                   if s & (1 << name) and not boundary & ~excluded)
                             for name, boundary in enumerate(derivatives))
    return StateReadings(candidates, mandatory, single_word, missing_mandatory,
                         missing_single_word, derivatives, loose_candidates)


def odd_closed_remainder(supports):
    waiting = set(range(len(supports)))
    while waiting:
        component = [waiting.pop()]
        for i in component:
            reached = {j for j in waiting if supports[i] & supports[j]}
            component.extend(reached)
            waiting -= reached
        if len(component) % 2 and all(supports[i].bit_count() == 2 for i in component):
            if all(count == 2 for count in incidence(supports[i] for i in component).values()):
                return True
    return False


def incidence(supports):
    return Counter(name for support in supports for name in indices(support))


def physical_properties(supports):
    repeat = any((a & b).bit_count() >= 2 for a, b in combinations(supports, 2))
    three = any(a & b and b & c and a & c for a, b, c in combinations(supports, 3))
    short, odd = [], []
    for removed in supports:
        remainder = [s & ~removed for s in supports if s != removed]
        if any(r.bit_count() < 2 for r in remainder):
            short.append(removed)
        if odd_closed_remainder(remainder):
            odd.append(removed)
    assert not short or repeat
    assert not odd or three
    return repeat, three, tuple(short), tuple(odd)


def names(supports):
    return [list(indices(s)) for s in supports]


def example(readings, allowed, name, supports, physical_holders):
    return {'state_words_hex': hex(allowed), 'state_count': allowed.bit_count(), 'supports': names(supports),
            'distinction': name, 'actual_holders': names(physical_holders),
            'candidate_sole_holders': names(readings.loose_candidates[name]),
            'forbidden_words_repaired_by_flip': list(indices(readings.one_place_repairs[name]))}


def counts_of_roles(readings, allowed, supports, named_multiplicity, examples):
    tally = Counter(loose=0, loose_unique=0, loose_multiple_candidates=0, shared=0,
                    shared_passing_sole_holder_test=0)
    for name, candidate_holders in enumerate(readings.loose_candidates):
        actual_holders = tuple(s for s in supports if s & (1 << name))
        if len(actual_holders) == 1:
            assert actual_holders[0] in candidate_holders
            tally['loose'] += 1
            if len(candidate_holders) == 1:
                tally['loose_unique'] += 1
                continue
            kind = 'loose_multiple_candidates'
        else:
            assert len(actual_holders) == 2
            tally['shared'] += 1
            if not candidate_holders:
                continue
            kind = 'shared_passing_sole_holder_test'
        tally[kind] += 1
        if kind not in examples:
            examples[kind] = example(readings, allowed, name, supports, actual_holders)
    return tally, Counter({k: v * named_multiplicity for k, v in tally.items()})


def full_diagnostic(width, allowed, readings, case):
    """Every legal named cover of a state missed by mandatory candidates."""
    excluded = ((1 << (1 << width)) - 1) ^ allowed
    realizations = tuple(covers(width, readings.candidates, excluded))
    assert len(realizations) == case['named_presentations_per_state']
    recovered = []
    for supports in realizations:
        deletions = tuple(next(indices(readings.candidates[s] & ~union(readings.candidates[t]
                                                                     for t in supports if t != s)))
                          for s in supports)
        recovered.append(raw_start(supports, reference_growth(supports, 'nae'), deletions))
    sole_holders = [set() for _ in range(width)]
    changes_in_status = []
    for i in range(width):
        holder_families = {tuple(s for s in p if s & (1 << i)) for p in realizations}
        sole_holders[i] = {h[0] for h in holder_families if len(h) == 1}
        if len({len(h) for h in holder_families}) > 1:
            changes_in_status.append(i)
    return {'state_words_hex': hex(allowed), 'state_count': allowed.bit_count(),
            'state_automorphisms': case['state_automorphisms'],
            'named_states': case['named_states_in_orbit'],
            'possible_sole_holders_by_distinction': [names(sorted(s)) for s in sole_holders],
            'distinctions_with_loose_and_shared_covers': changes_in_status,
            'distinctions_with_different_actual_sole_holders': [i for i, h in enumerate(sole_holders) if len(h) > 1],
            'named_first_rosters': case['named_rosters_per_state'],
            'state_matched_rosters': case['state_matched_rosters'], 'unmarked_rosters': case['unmarked_rosters'],
            'presentation_types': len(case['presentations']), 'named_presentations': recovered,
            'all_candidate_supports': names(readings.candidates),
            'mandatory_witnesses': [[list(indices(s)), w] for s, w in readings.mandatory.items()],
            'single_word_repair_witnesses': [[list(indices(s)), w] for s, w in readings.single_word.items()],
            'forbidden_words_allowed_by_mandatory_candidates': readings.missing_mandatory.bit_count(),
            'witness_word_allowed_by_mandatory_candidates': next(indices(readings.missing_mandatory))}


def diagnostics(width, state_cases):
    total = Counter(state_orbits=0, named_states=0, mandatory_orbits=0, mandatory_named_states=0,
                    single_word_orbits=0, single_word_named_states=0, residual_orbits=0,
                    residual_named_states=0, preserved_orbits=0, preserved_named_states=0)
    strata = defaultdict(Counter)
    flags = defaultdict(Counter)
    unresolved = []
    missed_by_single_word = []
    literal_examples = {}
    names_in_cases = Counter()
    names_with_labels = Counter()
    for case in state_cases:
        allowed = int(case['state_words_hex'], 16)
        readings = state_readings(width, allowed)
        mandatory_complete = not readings.missing_mandatory
        single_word_complete = not readings.missing_single_word
        state_names = case['named_states_in_orbit']
        total['state_orbits'] += 1
        total['named_states'] += state_names
        total['mandatory_orbits'] += mandatory_complete
        total['mandatory_named_states'] += mandatory_complete * state_names
        total['single_word_orbits'] += single_word_complete
        total['single_word_named_states'] += single_word_complete * state_names
        if mandatory_complete:
            assert case['named_presentations_per_state'] == 1
        else:
            unresolved.append(full_diagnostic(width, allowed, readings, case))

        if not single_word_complete:
            missed_by_single_word.append({
                'state_words_hex': hex(allowed), 'state_count': allowed.bit_count(),
                'named_states': state_names, 'physical_types': case['presentations'],
                'candidate_supports': names(readings.candidates),
                'mandatory_without_single_word_repair': names(s for s in readings.mandatory
                                                                if s not in readings.single_word),
                'one_word_missed_by_single_word_repairs': next(indices(readings.missing_single_word)),
                'mandatory_reader_recovers_relation': mandatory_complete,
            })

        for presentation_index, start in enumerate(case['presentations']):
            supports = tuple(to_mask(group) for group in start['supports'])
            physical_names = factorial(width) // start['presentation_automorphisms']
            repeat, three, short, odd = physical_properties(supports)
            restored = not short and not odd
            preserved = not three and not short
            if restored:
                assert single_word_complete
            if preserved:
                assert restored
            if presentation_index == 0:
                total['residual_orbits'] += restored
                total['residual_named_states'] += restored * state_names
                total['preserved_orbits'] += preserved
                total['preserved_named_states'] += preserved * state_names
            stratum = f'repeated_meeting_{int(repeat)}_three_pairwise_meet_{int(three)}'
            tally = strata[stratum]
            examples = (('short_remainder', short), ('odd_closed_remainder', odd))
            for label, removed in examples:
                if removed and label not in literal_examples:
                    literal_examples[label] = {'supports': names(supports), 'erased_supports': names(removed),
                                               'state_words_hex': hex(allowed), 'state_count': allowed.bit_count(),
                                               'single_word_recovers_holdings': single_word_complete}
            conditions = {'presentations': True, 'residual_certificate': restored, 'preserved_class': preserved,
                          'short_remainder': bool(short), 'odd_closed_remainder': bool(odd),
                          'incomplete_single_word_repair': not single_word_complete,
                          'incomplete_mandatory_reader': not mandatory_complete,
                          'loose_distinctions_present': start['has_loose_distinction']}
            for label, flag in conditions.items():
                tally[label] += flag
                tally[label + '_named'] += flag * physical_names
            role_counts, labelled = counts_of_roles(readings, allowed, supports, physical_names, literal_examples)
            names_in_cases.update(role_counts)
            names_with_labels.update(labelled)
            flags[stratum].update(role_counts)
    for key in sorted(strata):
        strata[key]['per_distinction'] = dict(flags[key])
    return {'recovery': total, 'irredundant_presentations_by_meeting_pattern': strata,
            'distinctive_reads_over_presentation_representatives': names_in_cases,
            'distinctive_reads_over_named_presentations': names_with_labels,
            'undecided_by_mandatory_reader': unresolved,
            'undecided_by_single_word_repair': missed_by_single_word, 'literal_examples': literal_examples}
