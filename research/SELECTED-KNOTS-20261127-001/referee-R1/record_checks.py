"""Test the frozen low-level solver routines against literal states and inspect provenance."""
import argparse
import ast
from collections import Counter
import hashlib
import itertools
import json
import resource
import subprocess
import sys
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
SOURCES = [STUDY / 'tree.py', ROOT / 'research/THIRD-LAYER-20261126-001/minflip.py',
           ROOT / 'research/BUILT-BINDING-20261126-001/built.py']
FREEZE = '23c0cd52d0'
CLOSED = '6423f637b8'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def test_target(path, name):
    # Isolate just the unmodified function being tested. Do not import the
    # producing module, its growth engine, its readers or its scorer.
    parsed = ast.parse(path.read_text())
    target, = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == name]
    deps = [n for n in parsed.body if isinstance(n, ast.ImportFrom)
            and n.module and n.module.startswith('pysat.')]
    env = {'itertools': itertools}
    tree = ast.Module(body=[*deps, target], type_ignores=[])
    exec(compile(tree, str(path), 'exec'), env)
    return env[name]


def verify_solver(pilot):
    exact, one, tuples = [test_target(p, n) for p, n in zip(SOURCES, ['least_exact', 'least', 'tuples_solver'])]
    examples = [[[2, 13, 29]], [[2, 13, 29], [29, 31, 53]],
                [[1, 7, 11], [7, 12, 42], [11, 42, 99]]]
    out = {'single-target checks': 0, 'joint-target checks': 0, 'tuple images checked': 0,
           'satisfiable zero targets': 0, 'infeasible joint targets': 0, 'joint caps below finite minimum': 0}
    for rows in (examples[:1] if pilot else examples):
        names = sorted(set().union(*map(set, rows)))
        states = [set(x for x, b in zip(names, flags) if b)
                  for flags in itertools.product(range(2), repeat=len(names))]
        states = [s for s in states if all(len(s & set(r)) % 2 == 0 for r in rows)]
        supports = [s for k in range(1, len(names)+1) for s in itertools.combinations(names, k)]
        for sup in supports:
            weights = [len(s) for s in states if len(s.intersection(sup)) % 2]
            for k in (1, len(names)):
                ans = min(weights) if weights else None
                expected = f'more than {k}' if ans is not None and ans > k else ans
                assert one(rows, sup, k) == expected
                out['single-target checks'] += 1
        # All singleton and adjacent-pair supports, including repeated and
        # incompatible requests. The solver fixture uses noncontiguous names.
        places = [(x,) for x in names] + list(zip(names, names[1:]))
        for cs in itertools.combinations_with_replacement(places, 2):
            truth = {}
            for s in states:
                key = tuple(len(s.intersection(c)) % 2 for c in cs)
                truth[key] = min(truth.get(key, len(names) + 1), len(s))
            assert set(tuples(rows, cs)) == set(truth)
            out['tuple images checked'] += 1
            for target in itertools.product(range(2), repeat=2):
                for k in (1, len(names)):
                    ans = truth.get(target)
                    if ans == 0:
                        out['satisfiable zero targets'] += 1
                    if ans is None:
                        out['infeasible joint targets'] += 1
                    if ans is not None and ans > k:
                        out['joint caps below finite minimum'] += 1
                    expected = ans if ans is not None and ans <= k else f'more than {k}'
                    assert exact(rows, list(zip(cs, target)), k) == expected
                    out['joint-target checks'] += 1
    out['cap boundary fixtures'] = []
    for n in ([60] if pilot else [39,40,41,59,60,61]):
        # An isolated optimiser fixture forces n named variables equal.
        rows = [(j, j+1) for j in range(n-1)]
        a = exact(rows, [([0], 1), ([n-1], 1)], 60)
        b = one(rows, [0], 40)
        fixed = one(rows, [0,n-1], 40)
        assert a == (n if n <= 60 else 'more than 60')
        assert b == (n if n <= 40 else 'more than 40') and fixed is None
        out['cap boundary fixtures'].append({'known weight': n, 'pair cap 60': a, 'sum cap 40': b})
    from pair_shortcut import groups, grow, start
    rows = start(4)
    loose, _, _ = groups(rows)
    middle = [x for xs in loose[1:-1] for x in xs]
    targets = [(loose[0], 1), (middle, 0), (loose[-1], 1)]
    out['nine-knot outer pair measured by frozen solver'] = []
    for t, expected in enumerate((6, 10)):
        value = exact(rows, targets)
        assert value == expected
        out['nine-knot outer pair measured by frozen solver'].append(value)
        if t == 0:
            rows = grow(rows)
    return out


def earlier(query):
    args = [sys.executable, '-B', 'scripts/track.py', 'objects', query, '--until', '2026-11-26',
            '--exclude', STUDY.name, '--limit', '8', '--json']
    hits = json.loads(subprocess.check_output(args, cwd=ROOT))
    return {k: [{'id': h['id'], 'record': h['record'],
                 'present at freeze': subprocess.run(['git', 'cat-file', '-e', FREEZE + ':' + h['record']],
                                                     cwd=ROOT, stderr=subprocess.DEVNULL).returncode == 0}
                for h in hits[k]] for k in ('index','other_epics')}


def provenance(pilot):
    path = (STUDY / 'README.md').relative_to(ROOT)
    old = git('show', f'{FREEZE}:{path}')
    closed = git('show', f'{CLOSED}:{path}')
    assert closed.startswith(old)
    paths = [*SOURCES, *sorted(STUDY.glob('frozen_*.jsonl')), STUDY/'overlap.json', STUDY/'third_algebra.json']
    digest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert all(git('show', f'{FREEZE}:{p.relative_to(ROOT)}') == p.read_bytes() for p in SOURCES)
    assert all(git('show', f'{CLOSED}:{p.relative_to(ROOT)}') == p.read_bytes() for p in paths)
    names = lambda p: [json.loads(s)['start'] for s in p.read_text().splitlines()]
    reuses = {}
    for name in ('census', 'heldout', 'sampled', 'built'):
        fn = f'frozen_{name}.jsonl'
        previous = ROOT / 'research/THIRD-LAYER-20261126-001' / fn
        a, b = names(STUDY/fn), names(previous)
        reuses[name] = {'current': len(a), 'earlier': len(b), 'equal in order': a == b}
    queries = ['family parities least flipping changes single linkage cluster higher layer shared facts',
               'single linkage tree pair cost clusters minimum crossing family sums',
               'ordinary parity funded end common witness families connected',
               'whole held class facts single knot class facts linear combinations',
               'binding disjoint carriers ring birth third layer chosen facts']
    return {'freeze': FREEZE, 'closure': CLOSED, 'freeze text preserved verbatim': True,
            'solver source unchanged since freeze': True, 'closed raw matches current': True,
            'hashes': digest, 'frozen rosters reused in order': reuses,
            'prior-work queries': {q: earlier(q) for q in queries[:1 if pilot else None]}}


def readable_leaf_counts(pilot):
    from cost_check import Stage, cases, starting_families
    from recount import canonical, dendrogram, partition, partition_facts
    result = {}
    for roster in ('census', 'heldout', 'sampled', 'built'):
        archived = {r['start']: r for line in (STUDY/f'frozen_{roster}.jsonl').read_text().splitlines()
                    if (r := json.loads(line))}
        counts = Counter()
        for name, rows in cases(roster, pilot):
            r = archived[name]
            m = r['families']
            if m < 2:
                continue
            stage = Stage(rows)
            families, _ = starting_families(stage)
            assert len(families) == m
            singles = {1 << i for i,g in enumerate(families) if len(g) == 1}
            distances = {tuple(map(int,s.split('-'))): v for s,v in r['distances'].items()}
            places, laws, _, _ = dendrogram(m, distances)
            counts['starts read'] += 1
            counts['starts with a family on one starting knot'] += bool(singles)
            counts['families'] += m
            counts['families on one starting knot'] += len(singles)
            counts['node equations of at least three places'] += sum(len(k) >= 3 for k in laws)
            counts['such equations with a single-holder leaf'] += sum(
                len(k) >= 3 and any(places[i] in singles for i in k) for k in laws)
            counts['starts with at least three families'] += m >= 3
            counts['such starts with a single-holder leaf'] += m >= 3 and bool(singles)
            universe = (1 << m) - 1
            if m <= 6:
                for row in r['rounds']:
                    if 'end' in row:
                        continue
                    for k in (8, 12):
                        blocks = partition(m, distances, k - 2 - 2*row['round'])
                        kept = partition_facts(blocks, universe)
                        assert len(kept) == row[f'SK3 k={k}']['kept sums']
                        counts[f'rows at {k} with an invariant single-holder family'] += any(
                            canonical(v, universe) in kept for v in singles)
        result[roster] = counts
    return result


def equivalent_bases():
    certificate = json.loads((HERE/'natural_places.json').read_text())['three_rings_of_four']
    words = set(certificate['allowed words'])
    tree = certificate['node with children, in place numbers']
    four, = certificate['three four-place knots sharing three different places']
    whole_ring_places = [i for i, p in enumerate(certificate['places as family sets']) if len(p) == 2]
    alternate = [whole_ring_places, *four]
    tables = {}
    for label, basis in [('parent and children', tree), ('whole-ring triple and three four-place relations', alternate)]:
        masks = [sum(1 << i for i in places) for places in basis]
        universe = range(1 << len(certificate['places as family sets']))
        states = {x for x in universe if all((x & m).bit_count() % 2 == 0 for m in masks)}
        assert states == words and len(words) == 32
        deletion = [sum(all((x & m).bit_count() % 2 == 0 for j,m in enumerate(masks) if i != j)
                        for x in universe) for i in range(len(masks))]
        assert deletion == [64] * 4
        tables[label] = {'relations as place indices': basis, 'joint states': len(states),
                         'total place occurrences': sum(map(len, basis)),
                         'states when deleting each equation from this basis': deletion}
    return tables


def guide_counts():
    path = ROOT/'research/THIRD-LAYER-20261126-001/referee-R1/scale_counts.json'
    selected = [r for r in json.loads(path.read_text())['large-scale rows']
                if r['round'] == 4 and r.get('in archived read')]
    results = Counter()
    for row in selected:
        scale = str(row['one-below-minimum scale'])
        assert scale in ('10', '12')
        reading = row['by scale'][scale]
        for key in ('facts', 'ring facts'):
            results[key] += all(f['class fact'] and not f['a sum of single-knot facts'] for f in reading[key])
    assert (len(selected), results['facts'], results['ring facts']) == (12, 8, 4)
    return {'starts': len(selected), 'all families whole-held': results['facts'], 'all rings whole-held': results['ring facts']}


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (1024 << 20, 1024 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    t0 = perf_counter()
    results = {'solver controls': verify_solver(args.pilot), 'records': provenance(args.pilot),
               'direct single-knot family reads': readable_leaf_counts(args.pilot),
               'two symmetric bases on the same nine places': equivalent_bases(),
               'earlier scale table cited in public guide': guide_counts()}
    print('Seconds', round(perf_counter() - t0, 3), 'joint-target checks', results['solver controls']['joint-target checks'])
    if not args.pilot:
        (HERE/'record_checks.json').write_text(json.dumps(results, indent=2) + '\n')
