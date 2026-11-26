"""Independently enumerate the specified receiver roster and inspect versioned prediction evidence."""
from collections import Counter
from datetime import datetime, timezone
from functools import cache
import argparse
import gzip
import itertools
import json
from pathlib import Path
import re
import subprocess
import time

from networkx.generators.atlas import graph_atlas_g

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
ORIGINAL = '6a8851e45a'
REGISTER = '28f7d7d9a9'
FOLDER = STUDY.relative_to(ROOT)
NAME = re.compile(r'n(\d):g(\d+):(\d+)@(\d+)')


def all_sharings(n):
    """Generate all connected pair-sharing patterns as numbered sets, before renaming."""
    pairs = tuple(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        shares = frozenset(p for i, p in enumerate(pairs) if mask & (1 << i))
        reached = {0}
        for _ in range(n - 1):
            reached |= {u for p in shares if reached.intersection(p) for u in p}
        if len(reached) == n:
            yield shares


@cache
def names_for(n, shares):
    """Numberings putting a sharing pattern in its least description."""
    by_sharings = {}
    for naming in itertools.permutations(range(n)):
        renamed = tuple(sorted(tuple(sorted((naming[x], naming[y]))) for x, y in shares))
        by_sharings.setdefault(renamed, []).append(naming)
    least = min(by_sharings)
    return least, by_sharings[least]


def key(n, shares, loose, site):
    least, numberings = names_for(n, shares)
    alternatives = []
    for names in numberings:
        counts = [0] * n
        for i, value in enumerate(loose):
            counts[names[i]] = value
        alternatives.append((tuple(counts), names[site]))
    return least, min(alternatives)


def enumerate_starts(n):
    found = set()
    seen = set()
    for shares in all_sharings(n):
        least, _ = names_for(n, shares)
        if least in seen:
            continue
        seen.add(least)
        degrees = Counter(i for pair in shares for i in pair)
        ranges = [range(max(3 - degrees[i], 0), 4) for i in range(n)]
        for loose in itertools.product(*ranges):
            if any(loose):
                for site in range(n):
                    found.add(key(n, shares, loose, site))
    return found


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.packedGitWindowSize=16m', '-c', 'core.packedGitLimit=64m', *args], cwd=ROOT, text=True).strip()


def history():
    """Limit history to the closed record, including its preceding register addition."""
    evidence = {}
    for name in ('README.md', 'rule.py', 'rule_runs.jsonl.gz'):
        evidence[name] = git('log', '--format=%h %cI', ORIGINAL, '--', str(FOLDER / name)).splitlines()
    archive = STUDY / 'rule_runs.jsonl.gz'
    archive_time = int.from_bytes(archive.read_bytes()[4:8], 'little')
    before = git('show', f'{REGISTER}:docs/ASSUMPTIONS.md')
    return {
        'version_history_through_close': evidence,
        'first_register_commit': git('show', '-s', '--format=%h %cI', REGISTER),
        'register_describes_result_as_checked': 'checked under caps of six and seven' in before,
        'rule_archive_gzip_header_utc': datetime.fromtimestamp(archive_time, timezone.utc).isoformat(),
        'commits_with_an_earlier_version_of_the_note': evidence['README.md'][1:],
        'local_note_mtime_utc': datetime.fromtimestamp((STUDY / 'README.md').stat().st_mtime, timezone.utc).isoformat(),
        'local_code_mtime_utc': datetime.fromtimestamp((STUDY / 'rule.py').stat().st_mtime, timezone.utc).isoformat(),
        'local_archive_mtime_utc': datetime.fromtimestamp(archive.stat().st_mtime, timezone.utc).isoformat(),
    }


def census(limit_n):
    counts = {}
    t = time.monotonic()
    for n in range(1, limit_n + 1):
        observed = set()
        expected = enumerate_starts(n)
        ids = [m for name in archive_names if (m := NAME.fullmatch(name)) and int(m[1]) == n]
        for m in ids:
            number, placement = int(m[2]), int(m[4])
            # The atlas is used only to decode the record's integer names.
            shares = frozenset(tuple(sorted(p)) for p in atlas[number].edges())
            observed.add(key(n, shares, tuple(map(int, m[3])), placement))
        counts[str(n)] = {'enumerated': len(expected), 'archive_labels': len(ids),
                          'distinct_archive_forms': len(observed), 'extra': len(observed - expected),
                          'missing': len(expected - observed)}
        assert observed == expected and len(ids) == len(observed)
    return counts, time.monotonic() - t


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true', help='time enumeration through three knots and archive scan')
    opts = parser.parse_args()
    t0 = time.monotonic()
    names = Counter()
    copier_rows = {}
    with gzip.open(STUDY / 'receivers_runs.jsonl.gz', 'rt') as source:
        for line in source:
            row = json.loads(line)
            names[row['A']] += 1
            if row['A'] in ('copier', 'n2:g3:22@0'):
                copier_rows[row['law'], row['d'], row['A']] = row['by sender']
    scan = time.monotonic() - t0
    archive_names = set(names)
    atlas = graph_atlas_g()
    counts, elapsed = census(3 if opts.pilot else 4)
    extras = sorted(name for name in names if not NAME.fullmatch(name))
    duplicate = [v == copier_rows[law, d, 'copier'] for (law, d, name), v in copier_rows.items() if name == 'n2:g3:22@0']
    assert set(names.values()) == {20} and extras == ['copier', 'ring', 'source'] and len(duplicate) == 20 and all(duplicate)
    out = {'enumeration': counts, 'label_count': len(names), 'extra_names': extras,
           'extra_knot_counts': {'copier': 2, 'ring': 5, 'source': 7},
           'copier_duplicates': 'n2:g3:22@0',
           'duplicate_all_five_sender_records_equal_law_distance_cells': sum(duplicate),
           'distinct_sited_starts_in_646_labels': len(names) - 1,
           'first_advisor_question_range_percent': [1, 10], 'note_range_receivers': [3, 30],
           'cap_three_six_of_646_percent': 100 * 6 / len(names),
           'earliest_register_and_note_evidence': history(),
           'seconds_archive_scan': round(scan, 3), 'seconds_enumeration': round(elapsed, 3)}
    if not opts.pilot:
        (HERE / 'roster_history.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
