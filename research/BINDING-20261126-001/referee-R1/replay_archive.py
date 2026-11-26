"""Recount the frozen relation spaces and check parity growth against the source records."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import perf_counter

from replay_growth import (
    HERE, LAYERS_REFEREE, RESEARCH, bicycle, grow, holders, input_rows, member,
    members, names_of, projection_rank_loss, row_mask, span, start_items,
)


STUDY = HERE.parent
CENSUS_ROSTER = RESEARCH / 'FORBID-EDITS-20261126-001' / 'starts.json'


def reference_growth():
    """The older shared growth engine is used only for ordered-support comparisons."""
    experiments = RESEARCH.parent / 'experiments'
    for subdir in (
        'NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae',
        'FORBIDDING-JOIN-20261120-001B/FORBIDDING-JOIN-20261120-001B-E001_free_readings',
    ):
        sys.path.insert(0, str(experiments / subdir))
    import naelib
    from rival_growth import grow as reference

    def advance(old):
        result, info = reference(old, 'parity', 'ordinary', naelib)
        return (old, info['status']) if result is None else (result, 'funded')

    return advance


def archive_checks(expected, supports, allowed, law_changes, basis, source_size):
    width = len(holders(supports))
    assert (width, allowed, law_changes, len(basis)) == (
        expected['distinctions'], expected['dim Z'], expected['dim of laws ∩ changes'], expected['dim B'],
    )
    rows = [row_mask(row) for row in supports]
    evidence = tuple(expected['elements'])
    unfolded = []
    actual = span(basis)
    for entry in evidence:
        law_indices = entry['knots summing to it']
        word = 0
        for knot in law_indices:
            word ^= rows[knot]
        assert word and member(word, actual)
        assert word.bit_count() == entry['size']
        assert any(knot >= source_size for knot in law_indices) == entry['holds a knot born after the start']
        unfolded.append(word)
    assert len(span(unfolded)) == len(unfolded) == min(len(basis), 6)
    return len(unfolded), len(unfolded) == len(basis)


def birth_checks(old, new):
    old_holders, new_holders = holders(old), holders(new)
    newborn_names = set(new_holders) - set(old_holders)
    assert new[:len(old)] == old
    assert all(len(new_holders[name]) == 1 for name in newborn_names)
    assert all(len(new_holders[name]) == 2 for name in old_holders)
    used_old = [name for row in new[len(old):] for name in row if name in old_holders]
    assert Counter(used_old) == Counter(name for name, knots in old_holders.items() if len(knots) == 1)
    implied = [row for row in new[len(old):] if not newborn_names.intersection(row)]
    old_laws = span(map(row_mask, old))
    assert all(member(row_mask(row), old_laws) for row in implied)
    assert projection_rank_loss(old, new) == 0
    return len(implied), row_mask(newborn_names), old_laws


def witness_references():
    built = json.loads((LAYERS_REFEREE / 'built_search.json').read_text())
    ten_knot = json.loads((LAYERS_REFEREE / 'extended_witness.json').read_text())[0]
    return built, ten_knot


def recount(pilot):
    tick = perf_counter()
    reference = reference_growth()
    ordered_roster = json.loads(CENSUS_ROSTER.read_text())
    built, ten_knot = witness_references()
    report = {
        'pilot': pilot,
        'archive_width_limit': 600,
        'groups': {},
        'witnesses': {},
        'old_state_projection_checks': 0,
        'births_without_fresh_distinctions': 0,
        'births_without_fresh_distinctions_with_unimplied_law': 0,
        'largest_holder_count': 0,
        'source_support_checks': Counter(),
        'archive_checks': Counter(),
        'exact_shared_engine_checks': defaultdict(Counter),
        'nonzero_stage_keys': [],
        'source_archive_sha256': {},
    }
    stage_digest = sha256()
    positive_keys = set()
    for group in ('census', 'heldout', 'witnesses'):
        witness_group = group == 'witnesses'
        rounds = 3 if witness_group else 2
        results = report['groups'][group] = {
            'starts_by_size': Counter(),
            'rounds': [dict(status=Counter(), B_rank=Counter(), largest_width=0,
                            B_rank_outside_source_laws=Counter()) for _ in range(rounds + 1)],
        }
        original = None
        densest = set()
        if not witness_group:
            archive_path = STUDY / f'forced_{group}.jsonl'
            archive_bytes = archive_path.read_bytes()
            report['source_archive_sha256'][archive_path.name] = sha256(archive_bytes).hexdigest()
            original = {row['start']: row for line in archive_bytes.splitlines() for row in (json.loads(line),)}
            by_width = sorted(original.values(), key=lambda row: max(
                r.get('distinctions', 0) for r in row['rounds']))
            densest = {row['start'] for row in by_width[-5:]}
        seen = Counter()
        for i, (name, source) in enumerate(start_items(group)):
            size = len(source)
            seen[size] += 1
            test_reference = witness_group or seen[size] <= 12 or name in densest
            if pilot and not test_reference:
                continue
            results['starts_by_size'][size] += 1
            expected = original.pop(name) if original is not None else None
            if expected is not None:
                assert size == expected['knots']
                report['archive_checks']['start records'] += 1
            if group == 'census':
                record_size, mult, loose = ordered_roster[i]
                assert size == record_size and source == input_rows(mult, loose), name
                report['source_support_checks']['ordered census sources'] += 1
            if witness_group:
                report['witnesses'][name] = witness_rows = []
                if i < 3:
                    assert source == tuple(map(tuple, built[(0, 17, 20)[i]]['source']))
                    report['source_support_checks']['archived built sources'] += 1
                if i == 3:
                    assert source == tuple(map(tuple, ten_knot['start supports']))
                    report['source_support_checks']['archived ten-knot source'] += 1

            supports = source
            source_laws = span(map(row_mask, source))
            processed = 0
            for round_no, result in enumerate(results['rounds']):
                processed += 1
                expected_round = expected['rounds'][round_no] if expected else None
                if expected_round is not None:
                    assert expected_round['round'] == round_no
                fresh = 0
                previous_laws = source_laws
                if round_no:
                    old, supports = supports, None
                    supports, status = grow(old)
                    if test_reference:
                        assert (supports, status) == reference(old), (name, round_no)
                        report['exact_shared_engine_checks'][group][status] += 1
                    if status != 'funded':
                        assert not expected_round or expected_round['end'] == status, (name, round_no)
                        result['status'][status] += 1
                        break
                    zero_fresh, fresh, previous_laws = birth_checks(old, supports)
                    report['old_state_projection_checks'] += 1
                    report['births_without_fresh_distinctions'] += zero_fresh
                    if witness_group and i == 3:
                        saved = ten_knot['rounds'][round_no - 1]['new supports']
                        assert supports[len(old):] == tuple(map(tuple, saved))
                        report['source_support_checks']['archived ten-knot birth rounds'] += 1

                owner = holders(supports)
                width = len(owner)
                report['largest_holder_count'] = max(report['largest_holder_count'], max(map(len, owner.values())))
                if width > 600:
                    assert not expected_round or expected_round['end'] == 'not read'
                    result['status']['not read'] += 1
                    break
                allowed, law_changes, basis = bicycle(supports)
                assert all(word & fresh == 0 and member(word, previous_laws) for word in basis)
                result['status']['read'] += 1
                result['largest_width'] = max(result['largest_width'], width)
                result['B_rank'][len(basis)] += 1
                laws_rank = len(span((*source_laws.values(), *basis))) - len(source_laws)
                result['B_rank_outside_source_laws'][laws_rank] += 1
                stage_digest.update(json.dumps((name, round_no, supports, sorted(members(basis)))).encode())
                if basis:
                    positive_keys.add((name, round_no))
                    report['archive_checks']['nonzero B stages including repeated witness stages'] += 1
                    report['archive_checks']['nonzero B elements including repeated witness stages'] += (1 << len(basis)) - 1
                if expected_round is not None:
                    checked, complete = archive_checks(expected_round, supports, allowed, law_changes, basis, size)
                    report['archive_checks']['stage rank records'] += 1
                    report['archive_checks']['recorded B basis vectors'] += checked
                    report['archive_checks']['complete recorded B spans'] += complete
                if witness_group:
                    witness_rows.append({
                        'round': round_no, 'knots': len(supports), 'distinctions': width,
                        'dim Z': allowed, 'dim of laws ∩ changes': law_changes, 'dim B': len(basis),
                        'dim B outside source laws': laws_rank,
                        'nonzero B supports': [list(names_of(word)) for word in sorted(members(basis)) if word],
                    })
            if expected is not None:
                assert processed == len(expected['rounds']), name
        assert pilot or not original, group

    report['nonzero_stage_keys'] = sorted(positive_keys)
    report['ordered_support_and_B_sha256'] = stage_digest.hexdigest()
    report['elapsed_seconds'] = round(perf_counter() - tick, 3)
    report['peak_memory_kib'] = getrusage(RUSAGE_SELF).ru_maxrss
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = recount(args.pilot)
    raw = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(raw)
        print(json.dumps({
            **report['archive_checks'],
            'unique nonzero B stages': len(report['nonzero_stage_keys']),
            'old state projection checks': report['old_state_projection_checks'],
            'elapsed seconds': report['elapsed_seconds'],
            'peak memory KiB': report['peak_memory_kib'],
        }))
    else:
        print(raw, end='')
