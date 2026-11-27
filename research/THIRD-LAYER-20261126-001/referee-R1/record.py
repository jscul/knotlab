"""Recount the archived tests and recover the freeze and earlier records."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
SETS = ('census', 'heldout', 'sampled', 'built', 'merge')
FREEZE = '965e73547a'
QUERIES = [
    'loose distinctions one relation component all laws',
    'closing implied input parity all loose distinctions',
    'ordinary parity birth projection pairs loops of four class facts',
    'whole held ring parities single knot class facts shortest changes',
    'parent closed lineages ordinary growth nested releases',
    'shared fact parity group sums second layer ring carriers',
    'funded nonclosing child component end operator common witnesses',
]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)


def objects(query):
    command = [sys.executable, '-B', 'scripts/track.py', 'objects', query,
               '--until', '2026-11-26', '--exclude', STUDY.name, '--limit', '6', '--json']
    hits = json.loads(subprocess.check_output(command, cwd=ROOT))
    result = {}
    for group in ('index', 'other_epics'):
        result[group] = []
        for hit in hits[group]:
            path = hit['record']
            exists_at_freeze = subprocess.run(
                ['git', 'cat-file', '-e', FREEZE + ':' + path],
                cwd=ROOT, stderr=subprocess.DEVNULL).returncode == 0
            result[group].append({'id': hit['id'], 'record': path, 'present at freeze': exists_at_freeze})
    return result


def recount(rows):
    counts = collections.Counter()
    families = collections.Counter()
    paired = collections.Counter()
    ends = collections.Counter()
    for row in rows:
        m = row['families']
        families[m] += 1
        assert row['T1 births across families'] == 0
        if m:
            assert row['T2 tuples'] == 2 ** (m - 1)
            assert row['T2 one rule, every proper subfamily free']
        stages = [s for s in row['rounds'] if 'least flips' in s]
        ends[next((s['end'] for s in row['rounds'] if 'end' in s), 'read to round 4')] += 1
        counts['starts'] += 1
        counts['stages'] += len(stages)
        counts['funded, read transitions'] += len(stages) - 1
        counts['m >= 3 with any funded, read transition'] += m >= 3 and len(stages) > 1
        counts['m >= 3 with rounds 3 and 4'] += m >= 3 and len(stages) == 5
        prev = None
        for s in stages:
            t = s['round']
            flips = s['least flips']
            assert len(flips) == m
            assert sum(v is None for v in flips) == (m if m == 1 else 0)
            counts['fixed requests'] += sum(v is None for v in flips)
            counts['capped requests'] += sum(isinstance(v, str) for v in flips)
            counts['finite minima'] += sum(type(v) is int for v in flips)
            if prev is not None:
                for i, w in enumerate(flips):
                    if type(w) is int:
                        baseline = stages[0]['least flips'][i]
                        counts['finite later family tests'] += 1
                        counts['frozen lower bound failures'] += w < baseline + 2*t
                        counts['increments smaller than two'] += w < prev[i] + 2
                        counts['increments greater than two'] += w > prev[i] + 2
            prev = flips
            if t >= 3:
                counts['stages round three or four'] += 1
                checked = s['every l_A a class fact']
                counts['stages with fixed family excluded from membership'] += checked is None and m == 1
                counts['starts with fixed family excluded from membership'] += checked is None and m == 1 and t == 3
                counts['stages with nonconstant family membership tested'] += checked is True
                assert checked is (True if m >= 2 else None)
                counts['stage dimension exceeds family rank at scale five'] += s['UPTO5 class facts'] > max(0, m - 1)
        if len(stages) == 5:
            d = stages[-1]['UPTO5 class facts']
            assert stages[-2]['UPTO5 class facts'] == d
            excess = d - max(0, m - 1)
            paired[excess] += 1
    return {'counts': dict(counts), 'families': dict(sorted(families.items())),
            'paired rounds by excess dimension': dict(sorted(paired.items())), 'ends': dict(ends)}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (1536 << 20, 1536 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    t0 = perf_counter()
    n = 4 if args.pilot else None
    summary = {}
    files = {}
    total = collections.Counter()
    fam = collections.Counter()
    extras = collections.Counter()
    for source in SETS:
        path = STUDY / ('frozen_' + source + '.jsonl')
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows = [json.loads(line) for line in path.read_text().splitlines()][:n]
        table = recount(rows)
        summary[source] = table
        total.update(table['counts'])
        fam.update(table['families'])
        extras.update(table['paired rounds by excess dimension'])
    queries = QUERIES[:1] if args.pilot else QUERIES
    hits = {query: objects(query) for query in queries}
    old = git('show', FREEZE + ':' + str((STUDY / 'README.md').relative_to(ROOT)))
    current = (STUDY / 'README.md').read_text()
    out = {'by roster': summary, 'totals': dict(total),
           'family count distribution': dict(sorted(fam.items())),
           'paired rounds by excess dimension': dict(sorted(extras.items())), 'input digests': files,
           'freeze': FREEZE, 'closed record': '25e1f48066',
           'entire freeze note equals beginning of closed note': current.startswith(old.rstrip()),
           'earlier record searches': hits}
    if args.pilot:
        print('Pilot elapsed seconds', round(perf_counter() - t0, 3))
    else:
        (HERE / 'record_counts.json').write_text(json.dumps(out, indent=2) + '\n')
        print('Starts', total['starts'], 'stages', total['stages'])


if __name__ == '__main__':
    main()
