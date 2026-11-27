"""Check the freeze, weighting, and logical strength of the recorded gates."""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
import os
from pathlib import Path
from random import Random
import subprocess
import sys
from time import perf_counter

from recount import advance, archive_records, census_index, load_census, ordered_chains, supports_of

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
CLAUSES = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
QUERIES = (
    'chain of eight three-place knots step one layer up four clauses ordinary growth',
    'upper agreement at any single lower bond six disjoint carriers',
    'ordinary growth under equal census start weighting long chains three-place knots',
    'four clauses both either rival laws upper reading birth essential',
)
BITS = tuple(product(range(2), repeat=3))
ALL = set(BITS)
EXPECTED = ALL - {(1, 1, 1)}


def command(*args):
    return subprocess.check_output(args, cwd=ROOT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})


def lower(word, triple):
    return tuple(word[i] for i in triple)


def upper(word, both):
    return tuple((min if i == both else max)(word[2*i:2*i+2]) for i in range(3))


def lower_source(skip=None):
    return [w for w in product(range(2),repeat=6)
            if all(lower(w,t) != (1,1,1) for j,t in enumerate(CLAUSES) if j != skip)]


def logic(pilot):
    full = lower_source()
    deletions = []
    for j in range(4):
        larger = lower_source(j)
        deletions.append([sum(upper(w, b) == (1,1,1) for w in larger) for b in range(3)])
    baseline = [{upper(w,b) for w in full} for b in range(3)]
    assert all(x == EXPECTED for x in baseline)
    # A function on the seven allowed inputs of one lower bond has 128
    # possible tables. The largest compatible domain is sufficient: all
    # the requirements tested below persist under adding allowed words.
    possible_determinations = []
    for j,t in enumerate(CLAUSES[:1] if pilot else CLAUSES):
        keys = sorted(EXPECTED)
        for i in range(3):
            for operator in ('either','both'):
                maps = 0
                example = None
                for outputs in product(range(2),repeat=7):
                    f = dict(zip(keys,outputs))
                    domain = [w for w in full if f[lower(w,t)] ==
                              (max if operator == 'either' else min)(w[2*i:2*i+2])]
                    if all({lower(w,s) for w in domain} == EXPECTED for s in CLAUSES) and all(
                        {upper(w,b) for w in domain} == EXPECTED for b in range(3)):
                        maps += 1
                        if example is None:
                            example = {'lower_words':[''.join(map(str,w)) for w in domain],
                                       'function_on_000_through_110': list(outputs)}
                possible_determinations.append({'clause':j,'pair':i,'role':operator,
                                               'compatible_functions':maps,'example':example})
    # Compare direct projected image with the canonical knot check.
    checks = []
    for contact in ('p',) if pilot else ('p','q','r'):
        places = [x for x in 'pqr' if x != contact]
        ans = json.loads(command(sys.executable,'-B','-m','knotlab','check','--cnf','~p ~q ~r',
                                 '--loops',*places,'--contact',contact,'--json'))
        checks.append({'contact':contact,'result':ans})
    return {'six_reading_conjunction_words':len(full),'upper_images':[sorted(s) for s in baseline],
            'lower_law_deletions_upper_111_words':deletions,
            'one_defining_bond_function_search':possible_determinations,'canonical_projected_checks':checks}


def freeze_and_prior(pilot):
    hashes = {}
    for line in (STUDY/'frozen.sha256').read_text().splitlines():
        digest,path = line.split()
        observed = [hashlib.sha256(command('git','show',f'{rev}:{path}')).hexdigest()
                    for rev in ('604ddb09f1','97b657fc1c')]
        assert observed == [digest,digest]
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
        hashes[path] = digest
    freeze_rows = command('git','ls-tree','-r','--name-only','604ddb09f1','--',
                          str((STUDY/'out').relative_to(ROOT))).decode().splitlines()
    prior = {}
    for query in QUERIES[:1] if pilot else QUERIES:
        result = json.loads(command(sys.executable,'-B','scripts/track.py','objects',query,
                                    '--until','2026-11-27','--exclude',STUDY.name,'--limit','8','--json'))
        prior[query] = {key:[{'id':r['id'],'record':r['record']} for r in result[key]]
                        for key in ('index','other_epics')}
    return {'frozen_close_and_current_sha256':hashes,'archived_outputs_at_freeze':freeze_rows,
            'this_study_has_post':(STUDY/'post').exists(),'prior_searches':prior}


def all_census(pilot):
    census = load_census()
    selected = {census_index(row) for chunk in archive_records() for row in chunk}
    sample = set(Random(64387).sample(range(len(census)),32)) if pilot else set(range(len(census)))
    counts = {}
    for i in sorted(sample):
        support = supports_of(census[i])
        funded = False
        for rd in range(7):
            has = next(ordered_chains(support),None) is not None
            buckets = ('all', 'selected' if i in selected else 'outside_sample', f'{len(census[i][2])}_starting_knots')
            for b in buckets:
                cell = counts.setdefault(b,{}).setdefault(rd,Counter())
                cell['stages'] += 1
                cell['holds_chain'] += has
            if rd == 6:
                break
            change = advance(support)
            if change.status != 'funded':
                break
            support = change.supports
    return {'starts':len(sample),'pilot_seed':64387 if pilot else None,'rounds':counts}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args = p.parse_args()
    result = {}
    for name,fn in [('census',all_census),('freeze_and_prior',freeze_and_prior),('logical_controls',logic)]:
        start = perf_counter()
        result[name] = fn(args.pilot)
        result[name]['seconds'] = round(perf_counter()-start,3)
    dest = HERE/('record_pilot.json' if args.pilot else 'record_check.json')
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(dest.name,result['census']['rounds']['all'])
    print({k:v['seconds'] for k,v in result.items()})

if __name__ == '__main__':
    main()
