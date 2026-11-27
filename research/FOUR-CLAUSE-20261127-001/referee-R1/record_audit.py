"""Check sample membership, archived stage rows, freeze history, and prior records."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from math import ceil
from pathlib import Path
import random
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = HERE.parents[2]
EARLIER = STUDY.parent / 'UPPER-GROWN-20261127-001'
FREEZE, CLOSE = '59177ac458', 'a37e1d0ec8'
QUERIES = (
    'four-clause step six agreements sampled grown stages',
    'agreement of agreements one layer up disjoint carriers',
    'both either birth essential four clauses ordinary and rival growth',
    'chain eight three-place knots four clauses six agreements',
)


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def rank(row):
    return int(row['start'].split()[1])


def archive_check(pilot):
    population = len(json.loads((STUDY.parent / 'FORBID-EDITS-20261126-001/starts.json').read_text()))
    ranks = list(range(population))
    pilot10 = set(random.Random(1).sample(ranks, 10))
    earlier = set(random.Random(20261128).sample([r for r in ranks if r not in pilot10], 1000))
    saved_previous = {rank(r) for file in (EARLIER/'out').glob('census_*.jsonl') for r in rows(file)}
    assert saved_previous == earlier
    pilots = {p.name: {rank(r) for r in rows(p)} for p in (EARLIER/'pilot').glob('*.jsonl')}
    assert pilot10 == pilots['p10.jsonl']
    excluded = earlier | pilot10 | {420}
    pool = [r for r in ranks if r not in excluded]
    selected = sorted(random.Random(20261130).sample(pool, 600))
    stage_rows = []
    starts_with = Counter()
    chunks = {}
    for i in range(1 if pilot else 12):
        file = STUDY/'out'/f'four_{i}.jsonl'
        records = rows(file)
        assert list(map(rank, records)) == selected[i::12]
        chunks[file.name] = {'count': len(records), 'sha256': sha256(file.read_bytes()).hexdigest()}
        for rec in records:
            stages = rec['rounds']
            assert [r['round'] for r in stages] == list(range(len(stages)))
            assert all((r['distinctions'] > 19) == r.get('not read',False) for r in stages)
            read = [r for r in stages if not r.get('not read')]
            grown_read = [r for r in read if r['round']]
            omitted = [r for r in stages if r.get('not read')]
            starts_with['total'] += 1
            starts_with['grew'] += len(stages)>1
            starts_with['grown_read'] += bool(grown_read)
            starts_with['any_omitted'] += bool(omitted)
            starts_with['grown_read_and_omitted'] += bool(omitted and grown_read)
            starts_with['only_omitted_grown'] += bool(omitted and not grown_read)
            starts_with['both_grown_read'] += len(grown_read)==2
            starts_with['no_grown_stage'] += len(stages)==1
            stage_rows.extend((rank(rec), r) for r in stages)
    stage_counts = {}
    birth_field = 'a birth needed, proper, free, not read at one lower bond'
    proper_field = 'proper and pairs free and not read at one lower bond'
    for t in range(3):
        at_round = [(idx,r) for idx,r in stage_rows if r['round']==t]
        read = [r for _,r in at_round if not r.get('not read')]
        skipped = [r for _,r in at_round if r.get('not read')]
        for r in read:
            assert r['relations read'] == 3*min(60,r['patterns'])
        stage_counts[t] = {
            'grown_or_start':len(at_round), 'read':len(read), 'over_cap':len(skipped),
            'over_cap_by_distinctions':dict(sorted(Counter(r['distinctions'] for r in skipped).items())),
            'max_patterns':max(r['patterns'] for r in read),
            'stages_with_at_least_12_distinctions':sum(r['distinctions']>=12 for r in read),
            'stages_with_at_least_12_distinctions_and_4_bonds':sum(r['distinctions']>=12 and r['bonds']>=4 for r in read),
            'totals':{f:sum(r[f] for r in read) for f in ('bonds','patterns','relations read','seven upper words',proper_field,'a birth needed',birth_field)},
            'stages_with_patterns':[idx for idx,r in at_round if r.get('patterns',0)],
        }
    candidates = {idx for idx,r in stage_rows if r['round'] and r.get(birth_field,0)}
    return {
        'population':population, 'excluded_union':len(excluded), 'eligible_pool':len(pool),
        'discovery_rank_in_previous_sample':420 in earlier,
        'unexcluded_saved_pilots':sorted(set.union(*pilots.values())-excluded),
        'actual_pilot_overlap':{p:sorted(ids & set(selected)) for p,ids in pilots.items()},
        'previous_main_sample_overlap':len(set(selected)&earlier), 'seed':20261130,
        'chunks':chunks, 'starts':starts_with, 'rounds':stage_counts,
        'positive_starts':sorted(candidates), 'F2_min_starts':ceil(starts_with['grown_read']*0.05),
        'study_has_post_directory':(STUDY/'post').is_dir(),
    }


def history():
    hits = {}
    for entry in (STUDY/'frozen.sha256').read_text().splitlines():
        checksum, path = entry.split()
        frozen = subprocess.check_output(['git','show',f'{FREEZE}:{path}'],cwd=ROOT)
        closed = subprocess.check_output(['git','show',f'{CLOSE}:{path}'],cwd=ROOT)
        assert checksum == sha256(frozen).hexdigest() == sha256(closed).hexdigest() == sha256((ROOT/path).read_bytes()).hexdigest()
        hits[path] = checksum
    assert not subprocess.check_output(['git','ls-tree','-r','--name-only',FREEZE,'--',str((STUDY/'out').relative_to(ROOT))],cwd=ROOT)
    return {'freeze_commit':FREEZE,'close_commit':CLOSE,'same_at_freeze_close_and_audit':hits,'output_files_in_freeze':0}


def prior_work(pilot):
    results = {}
    for query in QUERIES[:1] if pilot else QUERIES:
        raw = subprocess.check_output([sys.executable,'-B','scripts/track.py','objects',query,'--exclude',STUDY.name,
                                      '--until','2026-11-27','--limit','12','--json'],cwd=ROOT)
        found = json.loads(raw)
        results[query] = {group:[{'id':v['id'],'record':v['record']} for v in found[group]]
                          for group in ('index','other_epics')}
    return results


def controls():
    words = list(product(range(2),repeat=6))
    triples = [(a,2+b,4+c) for a,b,c in product(range(2),repeat=3) if (a^b^c)==0]
    keep = [w for w in words if all(not all(w[i] for i in t) for t in triples)]

    def upper(w,b):
        return tuple(int(all(pair) if j==b else any(pair)) for j,pair in enumerate((w[:2],w[2:4],w[4:])))

    def properties(domain,b):
        u = set(upper(w,b) for w in domain)
        pair_sizes = [len({(v[i],v[j]) for v in u}) for i,j in combinations(range(3),2)]
        read_at_one = []
        for t in triples:
            for i in range(3):
                by_fix = {}
                for w in domain:
                    by_fix.setdefault(tuple(w[j] for j in t),set()).add(upper(w,b)[i])
                read_at_one.append(all(len(v)==1 for v in by_fix.values()))
        return {'lower_words':len(domain),'upper_words':sorted(''.join(map(str,v)) for v in u),
                'lower_triple_image_sizes':[len({tuple(w[j] for j in t) for w in domain}) for t in triples],
                'upper_pair_image_sizes':pair_sizes,'determined_out_of_12':sum(read_at_one)}

    trimmed = [w for w in keep if upper(w,0)!=(0,0,0)]
    assert all(properties(trimmed,0)[key]==v for key,v in
               [('upper_pair_image_sizes',[4]*3),('lower_triple_image_sizes',[7]*4),('determined_out_of_12',0)])
    result = {'full_conjunction':[properties(keep,b) for b in range(3)],
              'remove_A_both_upper_000':[properties(trimmed,b) for b in range(3)]}
    # Relabelling the two members of any one pair exchanges the two four-clause choices.
    # With all eight exclusions, the same three pairs witness both choices.
    eight = list(product((0,1),(2,3),(4,5)))
    domain = [w for w in words if all(not all(w[i] for i in t) for t in eight)]
    result['eight_clause_positive_control'] = {'lower_words':len(domain),'distinct_four_clause_choices_same_pairs':2,
                                              'roles_per_choice':[properties(domain,b) for b in range(3)]}
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args = p.parse_args()
    start = perf_counter()
    out = {'archive':archive_check(args.pilot),'freeze':history(),'prior_searches':prior_work(args.pilot),
           'abstract_reading_controls':controls()}
    out['seconds']=round(perf_counter()-start,3)
    dest = HERE/('record_pilot.json' if args.pilot else 'record_counts.json')
    dest.write_text(json.dumps(out,indent=2)+'\n')
    print(dest.name, out['seconds'])


if __name__ == '__main__':
    main()
