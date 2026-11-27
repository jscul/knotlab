"""Check census coverage, freeze history, earlier records and prior-work searches."""
import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from functools import cache
from itertools import combinations, permutations, product
from operator import itemgetter
from subprocess import check_output

from census_tools import HERE, SOURCE

STUDY = HERE.parent
ROOT = HERE.parents[2]
SUBJECT = STUDY.name
SEARCHES = ["presentation allowed states marked loose", "necessary holders irredundant not-all-equal",
            "full allowed states closed six names all sizes", "completed system Whitney",
            "tree loop nine facts", "ordinary parity tree closes", "start family pair cost"]
EARLIER = ["STATES-GROWTH-20261119-001", "MANY-VALUED-20261119-001",
           "THREE-READERS-AND-GROWTH-20261120-001", "MARKED-LOOSE-20261127-001",
           "SELECTED-KNOTS-20261127-001", "ORDINARY-DYNAMICS-20261120-001",
           "TREE-PROOF-20261127-001", "READS-HOLDERS-SOURCES-20261120-001"]
REVISIONS = ["01938c1654", "5766f5c23b", "dd6f5b03b8", "5f7eb36f7c", "b7a842aa73"]


def git(*args):
    return check_output(["git", *args], cwd=ROOT, text=True)


@cache
def loose_options(floors, budget):
    return sum(sum(x) <= budget for x in product(*(range(f, 3) for f in floors)))


def labelled_total(n, stride):
    pairs = list(combinations(range(n), 2))
    total = 0
    for i, m in enumerate(product(range(3), repeat=len(pairs))):
        if i % stride or sum(m) > 12:
            continue
        degree = [0] * n
        component = list(range(n))
        for (a, b), amount in zip(pairs, m):
            if amount:
                degree[a] += amount
                degree[b] += amount
                left, right = component[a], component[b]
                component = [left if v == right else v for v in component]
        if min(degree) < 1 or len(set(component)) > 1:
            continue
        floors = tuple(sorted(max(0, 3-d) for d in degree))
        total += loose_options(floors, 12 - sum(m))
    return total


@cache
def reorderings(n):
    pairs = list(combinations(range(n), 2))
    return [itemgetter(*([pairs.index(tuple(sorted((p[a], p[b])))) for a, b in pairs]
                         + [len(pairs)+p[a] for a in range(n)]))
            for p in permutations(range(n))]


def roster_coverage(pilot):
    rows = json.loads(SOURCE.read_text())
    seen = set()
    labelled = Counter()
    classes = Counter()
    for n, meetings, loose in rows[::101 if pilot else 1]:
        assert 3 <= n <= 5 and all(0 <= l <= 2 for l in loose)
        m = {(a,b): v for a,b,v in meetings}
        pairs = list(combinations(range(n), 2))
        assert set(m) <= set(pairs) and all(v in (1,2) for v in m.values())
        assert sum(m.values()) + sum(loose) <= 12
        assert min(loose[i]+sum(v for pair,v in m.items() if i in pair) for i in range(n)) >= 3
        reach = {0}
        for _ in range(n):
            for a,b in m:
                if a in reach or b in reach:
                    reach.update((a,b))
        assert len(reach) == n
        key = tuple(m.get(pair, 0) for pair in pairs) + tuple(loose)
        orbit = {fn(key) for fn in reorderings(n)}
        normalized = min(orbit)
        assert normalized not in seen
        seen.add(normalized)
        classes[n] += 1
        labelled[n] += len(orbit)
    direct = {n:labelled_total(n, 101 if pilot else 1) for n in (3,4,5)}
    if not pilot:
        assert labelled == direct
    return dict(archived_classes=classes, labelled_from_orbits=labelled,
                independent_labelled_total=direct, pilot=pilot)


def archive(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def count_records():
    old = archive(STUDY.parent / 'MARKED-LOOSE-20261127-001' / 'frozen_census.jsonl')
    old = [v for v in old if 'start' in v]
    now = archive(STUDY / 'frozen_parity.jsonl')[:-1]
    assert old == now
    held = archive(STUDY.parent / 'MARKED-LOOSE-20261127-001' / 'frozen_heldout.jsonl')
    frozen_nae = archive(STUDY / 'frozen_nae.jsonl')
    historical = archive(ROOT / 'runs' / 'referee-states' / 'results.jsonl')
    pair_rows = [p for entry in historical if entry['case'] == 'D'
                 for p in entry['result']['pairs'] if p['same states']]
    eligible = [p for p in pair_rows if all(p['three-connected'])]
    small_stages = [s for entry in historical if entry['case'].startswith('B-')
                    for s in entry['result']['stages']]
    irr = [s for s in small_stages if not s['redundant']]
    return {'identical_parity_rows_in_prior_marked_study':len(now),
            'unique_in_first_200_under_parity':sum(r['presentations']==1 for r in now[:200]),
            'unique_in_first_200_under_not_all_equal':sum(r['presentations']==1 for r in frozen_nae[:200]),
            'prior_held_out_rows':len(held),
            'held_out_with_alternatives':sum(r['presentations']>1 for r in held),
            'held_out_fixed_family_and_tree':sum(r['family partitions']==r['trees']==1 for r in held),
            'older_same_state_pairs':len(pair_rows), 'older_both_three_connected':len(eligible),
            'older_inducing_isomorphism_when_both_three_connected':sum(p['isomorphism inducing the renaming'] for p in eligible),
            'older_irredundant_stages':len(irr),
            'older_saturated_irredundant_stages':sum(s['verdict']=='saturated' for s in irr)}


def literature(pilot):
    result = {}
    for q in SEARCHES[:1] if pilot else SEARCHES:
        data = json.loads(check_output([sys.executable, '-B', 'scripts/track.py', 'objects', q,
            '--until', '2026-11-27', '--exclude', SUBJECT, '--limit','8','--json'], cwd=ROOT))
        result[q] = {k:[r['epic'] for r in data[k]] for k in ('index','other_epics')}
    return result


def chronology():
    here = str(STUDY.relative_to(ROOT))
    result = {rev:git('diff-tree', '--no-commit-id', '--name-only','-r',rev,'--',here
                      ).splitlines() for rev in REVISIONS}
    claims = {}
    for rev in REVISIONS:
        readme = git('show',rev+':'+here+'/README.md')
        claims[rev] = {
            "four advisor predictions": "a4." in readme,
            "recursion result": "closes at round 3" in readme,
            "family and tree hypothesis": "H_d." in readme,
            "first 200 disclosed": "seen before the freeze on the first 200" in readme,
            "2000 deviation": "first 2,000" in readme,
            "1194 recorded": "1,194 of the planned" in readme,
        }
    present = {s:bool(git('ls-tree','-d','01938c1654','--','research/'+s).strip())
               for s in EARLIER}
    return dict(modified_files=result, note_at_revision=claims, prior_records_present_at_first_freeze=present)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    a = p.parse_args()
    begin = time.monotonic()
    results = dict(roster=roster_coverage(a.pilot), searches=literature(a.pilot), **count_records())
    if not a.pilot:
        results['freeze']=chronology()
        results['roster_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        (HERE / 'record.json').write_text(json.dumps(results,indent=2)+'\n')
    print('pilot' if a.pilot else 'complete', round(time.monotonic()-begin,3),'seconds')


if __name__ == '__main__':
    main()
