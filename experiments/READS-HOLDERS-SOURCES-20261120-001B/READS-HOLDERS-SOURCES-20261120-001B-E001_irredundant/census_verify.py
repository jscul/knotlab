"""Replay the census tables by covering forbidden words and using an independent growth operator."""

from collections import Counter
from functools import cache
import gzip
from itertools import combinations, permutations
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
sys.path.insert(0, str(ROOT / 'experiments/ORDINARY-DYNAMICS-20261120-001A'
                       / 'ORDINARY-DYNAMICS-20261120-001A-E001_ordinary'))
from end_operator import from_stars, step


def indices(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask -= low


def to_mask(indices):
    return sum(2 ** index for index in indices)


def locally_allowed(projected, support, law):
    if law == 'parity':
        return projected.bit_count() % 2 == 0
    return 0 < projected < support


@cache
def restrictions(width, law):
    result = {}
    for scope in range(1 << width):
        if scope.bit_count() < 3:
            continue
        allowed = frozenset(word & scope for word in range(1 << width)
                            if locally_allowed(word & scope, scope, law))
        forbidden = to_mask(w for w in range(1 << width) if (w & scope) not in allowed)
        result[scope] = (allowed, forbidden)
    return result


def exact_candidates(width, words, law):
    word_bits = to_mask(words)
    return {s: excluded for s, (allowed, excluded) in restrictions(width, law).items()
            if excluded & word_bits == 0 and frozenset(w & s for w in words) == allowed}


def incidence_connected(supports):
    if not supports:
        return False
    waiting = set(supports)
    first = waiting.pop()
    visit = [first]
    for current in visit:
        reached = {s for s in waiting if s & current}
        visit.extend(reached)
        waiting.difference_update(reached)
    return not waiting


def covers(width, family, excluded):
    """Enumerate inclusion-minimal covers of the excluded words subject to the incidence cap."""
    supports = tuple(family)
    words_to_candidates = {w: to_mask(i for i, s in enumerate(supports) if family[s] >> w & 1)
                           for w in indices(excluded)}
    if not supports:
        return
    all_distinctions = (1 << width) - 1

    def visit(uncovered, available, chosen, seen, twice):
        if not uncovered:
            rows = tuple(supports[i] for i in chosen)
            if seen != all_distinctions or not incidence_connected(rows):
                return
            for row in rows:
                private = family[row]
                for other in rows:
                    if other != row:
                        private &= ~family[other]
                if not private:
                    return
            yield tuple(sorted(rows))
            return
        coverers = min((words_to_candidates[w] & available for w in indices(uncovered)),
                       key=int.bit_count)
        # Each cover is attributed to its first included candidate for the
        # selected word. An earlier branch keeps all later candidates.
        for i in indices(coverers):
            available &= ~(1 << i)
            row = supports[i]
            more_twice = twice | (seen & row)
            eligible = to_mask(j for j in indices(available) if not supports[j] & more_twice)
            yield from visit(uncovered & ~family[row], eligible, (*chosen, i), seen | row, more_twice)

    yield from visit(excluded, (1 << len(supports)) - 1, (), 0, 0)


def reference_growth(supports, law):
    result = step(from_stars(tuple(tuple(indices(s)) for s in supports)), law)
    children = Counter((tuple(sorted(supports[i] for i in parent_indices)), fresh)
                       for parent_indices, fresh in zip(result.parents, result.fresh, strict=True))
    status = 'births' if result.status == 'extend' else result.status
    return status, tuple(sorted((p, f, mult) for (p, f), mult in children.items()))


def state_symmetries(width, words):
    """Search original-word permutations using elementary Hamming-count invariants."""
    pairs_and_singles = [to_mask(which) for size in (1, 2) for which in combinations(range(width), size)]
    counts = {mask: tuple(sum(word.bit_count() == k and word & mask == mask for word in words)
                          for k in range(width + 1))
              for mask in pairs_and_singles}
    available = {i: [j for j in range(width) if counts[1 << i] == counts[1 << j]]
                 for i in range(width)}
    order = sorted(available, key=lambda i: len(available[i]))

    def extend(mapping, unused):
        if not unused:
            image = frozenset(to_mask(mapping[i] for i in indices(w)) for w in words)
            if image == words:
                yield tuple(mapping[i] for i in range(width))
            return
        source = order[len(mapping)]
        for target in available[source]:
            if target in unused and all(counts[(1 << source) | (1 << i)]
                                        == counts[(1 << target) | (1 << j)] for i, j in mapping.items()):
                mapping[source] = target
                yield from extend(mapping, unused - {target})
                del mapping[source]

    return tuple(extend({}, set(range(width))))


def permutation_classes(records, action, transports):
    original = set(records)
    unseen = original.copy()
    answer = 0
    while unseen:
        sample = next(iter(unseen))
        images = {action(sample, move) for move in transports}
        assert images <= original
        unseen -= images
        answer += 1
    return answer


def recode_roster(record, action):
    status, terms = record
    return status, tuple(sorted((tuple(sorted(action[s] for s in parents)), f, mult)
                                for parents, f, mult in terms))


def unmarked(record):
    status, entries = record
    parents = sorted({p for group, _, _ in entries for p in group})
    signatures = []
    for perm in permutations(range(len(parents))):
        rename = dict(zip(parents, perm, strict=True))
        signatures.append(tuple(sorted((tuple(sorted(rename[p] for p in group)), f, mult)
                                       for group, f, mult in entries)))
    return status, min(signatures)


def literal_start(width, law, words, row):
    supports = tuple(to_mask(group) for group in row['supports'])
    rules = restrictions(width, law)
    all_words = range(1 << width)
    assert frozenset(w for w in all_words if all((w & s) in rules[s][0] for s in supports)) == words
    for support, witness in zip(supports, row['deletion_words'], strict=True):
        assert frozenset(w & support for w in words) == rules[support][0]
        assert witness in all_words and (witness & support) not in rules[support][0]
        assert all((witness & s) in rules[s][0] for s in supports if s != support)
    births = tuple(sorted((tuple(sorted(to_mask(s) for s in b['parents'])), b['fresh'], b['multiplicity'])
                         for b in row['births']))
    assert reference_growth(supports, law) == (row['status'], births)
    return tuple(sorted(supports))


def verify(width, law, records):
    presentations = named_covers = symmetries_rechecked = 0
    for row in records:
        words = frozenset(indices(int(row['state_words_hex'], 16)))
        assert len(words) == row['allowed_states']
        family = exact_candidates(width, words, law)
        excluded = to_mask(w for w in range(1 << width) if w not in words)
        every_cover = tuple(covers(width, family, excluded))
        assert len(every_cover) == len(set(every_cover)) == row['named_presentations_per_state']
        every_roster = {reference_growth(p, law) for p in every_cover}
        assert len(every_roster) == row['named_rosters_per_state']
        assert len({unmarked(r) for r in every_roster}) == row['unmarked_rosters']
        if len(every_cover) > 1:
            symmetries = state_symmetries(width, words)
            assert len(symmetries) == row['state_automorphisms']
            actions = [{s: to_mask(p[i] for i in indices(s)) for s in family} for p in symmetries]
            assert permutation_classes(every_cover, lambda p, f: tuple(sorted(f[s] for s in p)), actions) \
                == len(row['presentations'])
            assert permutation_classes(every_roster, recode_roster, actions) == row['state_matched_rosters']
            symmetries_rechecked += 1
        for start in row['presentations']:
            assert literal_start(width, law, words, start) in every_cover
            presentations += 1
        named_covers += len(every_cover)
    return {'state_orbits': len(records), 'presentations_replayed': presentations,
            'named_covers_summed_over_representative_states': named_covers,
            'ambiguous_state_symmetries_recomputed': symmetries_rechecked}


def canonical_law(arity, law):
    names = [f'q{i}' for i in range(arity)]
    support = (1 << arity) - 1
    words = {f'{w:0{arity}b}' for w in range(support + 1) if locally_allowed(w, support, law)}
    clauses = [' '.join(('~' if b == '1' else '') + name for name, b in zip(names, word, strict=True))
               for w in range(support + 1) if (word := f'{w:0{arity}b}') not in words]
    command = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(clauses),
               '--loops', *names[:-1], '--contact', names[-1], '--json']
    report = json.loads(subprocess.check_output(command, env=dict(os.environ, PYTHONPATH=str(ROOT / 'tools')),
                                                cwd=ROOT, text=True))
    assert set(report['allowed']) == words and report['is_knot']
    return {k: report[k] for k in ('binding', 'loss_on_erasure', 'coexistence', 'is_knot')}


def prior_nae_controls():
    def solutions(rows, width):
        return frozenset(w for w in range(1 << width)
                         if all(locally_allowed(w & s, s, 'nae') for s in rows))

    small = tuple(map(to_mask, ((0, 1, 2), (3, 4, 5), (0, 3, 6), (1, 2, 4, 5))))
    broad = (*small[:-1], small[-1] | (1 << 6))
    words = solutions(small, 7)
    assert words == solutions(broad, 7)
    wide_projection = frozenset(w & broad[-1] for w in words)
    assert len(wide_projection) < len(restrictions(7, 'nae')[broad[-1]][0])

    nine = tuple(map(to_mask, ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))))
    nine_words = solutions(nine, 9)
    family = exact_candidates(9, nine_words, 'nae')
    indispensable = []
    for scope, forbidden in family.items():
        for other, mask in family.items():
            if other != scope:
                forbidden &= ~mask
        if forbidden:
            indispensable.append(scope)
    assert set(family) == {*nine, to_mask(range(3, 9))}
    assert set(indispensable) == set(nine)
    assert solutions(indispensable, 9) == nine_words
    return {'prior_seven': {'same_allowed_words': len(words), 'wider_projection': len(wide_projection),
                            'full_five_place_nae': len(restrictions(7, 'nae')[broad[-1]][0])},
            'prior_nine': {'same_allowed_words': len(nine_words), 'all_candidate_supports': len(family),
                           'indispensable_candidates': len(indispensable), 'unique_irredundant_cover': True}}


def main():
    raw = json.loads(gzip.decompress((OUTPUT / 'census_cases.json.gz').read_bytes()))
    summary = json.loads((OUTPUT / 'census_summary.json').read_text())
    receipt = {'replay': {}, 'canonical_law': {}, 'prior_controls': prior_nae_controls()}
    for width_text, laws in raw.items():
        width = int(width_text)
        receipt['replay'][width] = {law: verify(width, law, records) for law, records in laws.items()}
        receipt['canonical_law'][width] = {law: canonical_law(width, law) for law in laws}
        for law, validated in receipt['replay'][width].items():
            counts = summary['by_width'][width_text]['laws'][law]
            assert validated['presentations_replayed'] == counts['irredundant_up_to_renaming']
            assert validated['state_orbits'] == counts['state_classes_up_to_renaming']
        print(f'width {width}: verified {receipt["replay"][width]}', flush=True)
    for law, minimum_rows in summary['minima'].items():
        for minimum in minimum_rows.values():
            width, maximum, total = minimum['width_max_holders_total_holders']
            for state_id, pair in minimum['examples'].items():
                row = raw[str(width)][law][int(state_id) - 1]
                words = frozenset(indices(int(row['state_words_hex'], 16)))
                left = literal_start(width, law, words, pair['left'])
                right = literal_start(width, law, words, pair['right'])
                assert left != right and max(len(left), len(right)) == maximum and len(left) + len(right) == total
    (OUTPUT / 'census_verification.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
