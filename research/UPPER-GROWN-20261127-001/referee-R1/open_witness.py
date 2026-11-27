"""Literal state and deletion checks for a strict box formed in one funded round."""

import argparse
import contextlib
from dataclasses import asdict
from itertools import product
import io
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research/NAE-LAYER-20261127-001/referee-R1'))
sys.path.insert(0, str(ROOT / 'tools'))
from growth_rule import advance
from knotlab.cli import main as knot_test


START = ((4, 5, 6), (4, 7, 8), (0, 9, 10), (9, 11, 12), (1, 5, 12),
         (13, 14, 15), (7, 10, 11), (3, 14, 16), (2, 13, 16), (6, 8, 15))
CARRIERS = ((0, 9, 17), (2, 3, 16), (1, 5, 18), (7, 10, 13), (4, 6, 8), (11, 12, 14))
CROSS = tuple(product((0, 1), (2, 3), (4, 5)))
LOWER_NAMES = ('A0', 'A1', 'B0', 'B1', 'C0', 'C1')
UPPER_NAMES = ('P', 'Q', 'R')


def is_agreement(bits, members):
    result = bits[members[0]] == bits[members[1]]
    for other in members[2:]:
        result &= bits[members[0]] == bits[other]
    return result


def word_array(columns):
    words = np.zeros(len(columns[0]), dtype=np.uint8)
    for column in columns:
        words = words * 2 + column
    return words


def word_counts(encoded, mask, n):
    counts = np.bincount(encoded[mask], minlength=1 << n)
    return {format(i, f'0{n}b'): int(count) for i, count in enumerate(counts) if count}


def forbid(names, word):
    return ' '.join(('~' if int(value) else '') + name for name, value in zip(names, word, strict=True))


def image_clauses(names, words):
    return [forbid(names, word) for word in product((0, 1), repeat=len(names))
            if ''.join(map(str, word)) not in words]


def canonical(cnf, names, hidden=()):
    outcomes = []
    for contact in names:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = knot_test(['check', '--cnf', '; '.join(cnf),
                                '--loops', *(n for n in names if n != contact), '--contact', contact,
                                '--witnesses', *hidden, '--json'])
        if result:
            raise ValueError(buf.getvalue())
        report = json.loads(buf.getvalue())
        outcomes.append({k: report[k] for k in ('variables', 'is_knot', 'allowed')})
        assert report['is_knot']
    return outcomes


def lower_holders(knots, failed_laws, triples):
    # Counts for a retained subset S are the sum over violation sets contained
    # in the complement of S. Accumulate this sum in the subset order.
    total = 1 << len(knots)
    results = []
    for pick, reading in zip(CROSS, triples, strict=True):
        completions = np.bincount(failed_laws[reading == 7], minlength=total)
        for i in range(len(knots)):
            width = 1 << i
            paired = completions.reshape(-1, 2, width)
            paired[:, 1] += paired[:, 0]
        carrier_variables = set().union(*(CARRIERS[i] for i in pick))
        certificates = []
        for retained in range(1, total):
            allowed_violations = total - 1 - retained
            chosen = [i for i in range(len(knots)) if retained & (1 << i)]
            if completions[allowed_violations] or any(
                completions[allowed_violations | 1 << i] == 0 for i in chosen):
                continue
            reached = {chosen[0]}
            while True:
                held = set().union(*(knots[i] for i in reached))
                enlarged = {i for i in chosen if held.intersection(knots[i])}
                if reached == enlarged:
                    break
                reached = enlarged
            observed = set().union(*(knots[i] for i in chosen))
            certificates.append({'laws': chosen, 'connected': len(reached) == len(chosen),
                                 'unheld_carrier_distinctions': sorted(carrier_variables - observed)})
        assert certificates
        results.append(certificates)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deletions', type=int, default=12)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    start_time = perf_counter()
    grown = advance(START)
    assert grown.status == 'funded' and grown.supports == START + ((0, 1, 17), (2, 3, 18))
    assert set(CARRIERS[0]).isdisjoint(CARRIERS[1])
    assert len(set().union(*map(set, CARRIERS))) == sum(map(len, CARRIERS))
    # Each of the other two live parents has a different old witness. These are
    # the only two candidate pairs, so the reconstructed births have no tie.
    live = {i for i, k in enumerate(START) if any(sum(x in h for h in START) == 1 for x in k)}
    neighbors = [{j for j, h in enumerate(START) if i != j and set(k) & set(h)}
                 for i, k in enumerate(START)]
    reachable = {0}
    while set.union(*(neighbors[i] for i in reachable)) - reachable:
        reachable |= set.union(*(neighbors[i] for i in reachable))
    assert len(reachable) == len(START)
    join_witnesses = [(i, j, sorted(neighbors[i] & neighbors[j])) for i in sorted(live) for j in sorted(live)
                      if i < j and neighbors[i] & neighbors[j]]
    assert join_witnesses == [(2, 4, [3]), (7, 8, [5])]
    states = np.arange(1 << 19, dtype=np.uint32)
    bits = [((states >> x) & 1).astype(np.uint8) for x in range(19)]
    fail = np.zeros(len(states), dtype=np.uint16)
    for i, k in enumerate(grown.supports):
        fail |= is_agreement(bits, k).astype(np.uint16) << i
    allowed = fail == 0
    lower = [is_agreement(bits, c) for c in CARRIERS]
    six = word_array(lower)
    upper = [lower[i] != lower[i+1] for i in (0, 2, 4)]
    three = word_array(upper)
    ones = word_counts(six, allowed, 6)
    uppers = word_counts(three, allowed, 3)
    triples = [word_array([lower[i] for i in pick]) for pick in CROSS]
    lower_images = [word_counts(t, allowed, 3) for t in triples]
    assert list(uppers) == [format(i, '03b') for i in range(7)]
    assert all(set(img) == set(uppers) for img in lower_images)
    rows_lower = []
    for k in grown.supports:
        fix = word_array([bits[x] for x in k])
        counts = []
        for read in lower:
            counts.append(sum(bool(np.any(allowed & (fix == word) & read))
                              and bool(np.any(allowed & (fix == word) & ~read)) for word in range(8)))
        rows_lower.append(counts)
    assert min(min(row) for row in rows_lower) >= 1
    upper_unread = []
    for t in triples:
        upper_unread.append([sum(bool(np.any(allowed & (t == word) & read))
                                 and bool(np.any(allowed & (t == word) & ~read)) for word in range(8))
                             for read in upper])
    assert min(min(row) for row in upper_unread) >= 1
    member_flips = []
    for c, read in zip(CARRIERS, lower, strict=True):
        counts = []
        for x in c:
            changed = states ^ (1 << x)
            witness = allowed & allowed[changed] & ~bits[x].astype(bool) & (read != read[changed])
            counts.append(int(np.count_nonzero(witness)))
        member_flips.append(counts)
    assert all(min(c) >= 1 for c in member_flips)
    deletions = []
    for erased in range(min(12, args.deletions)):
        single = fail == (1 << erased)
        swap = word_counts(three, single, 3)
        assert '111' in swap
        raw = int(np.flatnonzero(single & (three == 7))[0])
        deletions.append({'erased_knot': erased, 'new_upper_111_states': swap['111'],
                          'first_restored_assignment_integer_lsb_distinction_zero': raw,
                          'upper_images_with_law_deleted': sorted(set(uppers) | set(swap)),
                          'lower_111_restored_counts': [int(np.count_nonzero(single & (t == 7))) for t in triples]})
    projected_cnf = image_clauses(LOWER_NAMES, ones)
    upper_definitions = []
    for i, name in enumerate(UPPER_NAMES):
        local = [*LOWER_NAMES[2*i:2*i+2], name]
        for values in product((0, 1), repeat=3):
            if values[2] != (values[0] != values[1]):
                upper_definitions.append(forbid(local, values))
    upper_knot = canonical(projected_cnf + upper_definitions, UPPER_NAMES, LOWER_NAMES)
    abstract_cnf = [forbid([LOWER_NAMES[i] for i in pick], (1, 1, 1)) for pick in CROSS]
    lower_law_deletions = []
    for erased, pick in enumerate(CROSS):
        six_word = ''.join(str(int(i in pick)) for i in range(6))
        assert all(any(six_word[i] == '0' for i in p) for j, p in enumerate(CROSS) if j != erased)
        assert all(six_word[i] != six_word[i+1] for i in (0, 2, 4))
        lower_law_deletions.append(six_word)
    result = {'start': START, 'independent_join_witnesses_parents_and_common_old_knot': join_witnesses,
              'growth_status': grown.status, 'births': [asdict(b) for b in grown.births],
              'grown_supports': grown.supports, 'start_connected': True, 'start_loose': [0, 1, 2, 3],
              'grown_loose': [17, 18], 'source_assignments_enumerated': len(states),
              'source_states_by_raw_six_reading_word': ones, 'source_states_with_all_laws': int(np.count_nonzero(allowed)),
              'six_disjoint_carriers': CARRIERS, 'mixed_fix_counts_by_source_knot_then_lower_reading': rows_lower,
              'single_flip_counts_each_carrier_member': member_flips, 'lower_triples': CROSS,
              'source_states_by_each_lower_triple': lower_images,
              'all_inclusion_minimal_sufficient_law_sets_per_lower_exclusion': lower_holders(grown.supports, fail, triples),
              'upper_as_pairwise_disagreement': uppers, 'mixed_fix_counts_by_lower_triple_then_upper_reading': upper_unread,
              'source_law_deletions': deletions,
              'six_reading_witnesses_restoring_upper_111_in_eight_clause_relation_on_each_clause_deletion': lower_law_deletions,
              'canonical_checks_each_contact_role': {
                  'each_lower_triple_from_literal_source_projection': [canonical(image_clauses(tuple(LOWER_NAMES[i] for i in pick), words),
                                                                         tuple(LOWER_NAMES[i] for i in pick))
                                                                  for pick, words in zip(CROSS, lower_images, strict=True)],
                  'upper_from_actual_six_reading_image_with_agreements_quantified_away': upper_knot,
                  'upper_from_eight_lower_laws_with_agreements_quantified_away': canonical(
                      abstract_cnf + upper_definitions, UPPER_NAMES, LOWER_NAMES)},
              'elapsed_seconds': round(perf_counter() - start_time, 5)}
    args.out.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print('states, six words, upper words, law deletions, seconds',
          result['source_states_with_all_laws'], len(ones), len(uppers), len(deletions), result['elapsed_seconds'])


if __name__ == '__main__':
    main()
