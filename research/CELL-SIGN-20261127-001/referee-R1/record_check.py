"""Verify the frozen record, weighting, planarity strata and the forced deletion."""
from collections import Counter, defaultdict
import gzip
from itertools import combinations, permutations
import json
from pathlib import Path
from subprocess import check_output

import networkx as nx

from minimal_measure import measure_cycles
from scope_check import HERE, INPUT, PRIOR, RESEARCH

STUDY = HERE.parent
ROOT = RESEARCH.parent
FREEZE, CLOSE = 'f7bf89cadb', 'caa1869940'


def git(*args):
    return check_output(['git', *args], cwd=ROOT, text=True)


def compare_freeze():
    study = STUDY.relative_to(ROOT).as_posix()
    old = git('show', f'{FREEZE}:{study}/README.md')
    new = git('show', f'{CLOSE}:{study}/README.md')
    assert new.startswith(old)
    blobs = [git('rev-parse', f'{revision}:{study}/cellsign.py').strip() for revision in (FREEZE, CLOSE)]
    assert blobs[0] == blobs[1]
    return dict(freeze=FREEZE, close=CLOSE, original_lines=len(old.splitlines()),
                appended_lines=len(new.splitlines())-len(old.splitlines()), code_blob=blobs[0])


def compare_published():
    holdings = {(r['population'],r['key']):r
                for r in map(json.loads, INPUT.read_text().splitlines())}
    earlier = json.loads(PRIOR.read_text())
    groups, scope, rows, names = {}, {}, [], Counter()
    fewest = overlap = evaluations = 0
    for pop, file, identifier in [('birth','results','start'),('type','census_types','type')]:
        earlier_rows = {r['id']:r for r in earlier[pop]['rows']}
        strata = defaultdict(Counter)
        labels = defaultdict(Counter)
        for row in map(json.loads, (STUDY / (file+'.jsonl')).read_text().splitlines()):
            key = row[identifier]
            supports = list(map(set, holdings[pop,key]['supports']))
            meets = nx.Graph()
            meets.add_nodes_from(range(len(supports)))
            meets.add_edges_from((a,b) for a,b in combinations(meets,2) if supports[a] & supports[b])
            planar = nx.check_planarity(meets)[0]
            assert planar == (earlier_rows[key]['minor'] is None)
            tally = row['tallies'].get('minimal strict even',{})
            oriented = tally.get('orientable',0)
            non = tally.get('choices',0) - oriented
            grouping = 'planar' if planar else 'nonplanar'
            strata[grouping].update(rows=1, orientable_even=oriented, nonorientable_even=non,
                                    rows_with_orientable=int(bool(oriented)),rows_with_nonorientable=int(bool(non)),
                                    rows_with_both=int(bool(non and oriented)))
            label = row["readers study's kind"]
            small = row['free choices'] <= 14
            labels[label].update(rows=1, small=int(small))
            bounds = len(set().union(*supports))//2
            rows.append(dict(population=pop,id=key,planar=planar,kind=label,small=small,
                             natural_strict_size_bound=bounds,orientable_even=oriented,nonorientable_even=non))
            assert not any((row.get('P1 failures'),row.get('unsettled'),row['corollary failures'],row['theorem failures']))
            for name, t in row['tallies'].items():
                assert t['theorem holds']==t['choices']
                evaluations += t['choices']
                names[name] += t['choices']
                if name == 'fewest strict':
                    fewest += t['choices']
                    assert row['fewest strict readers']<=8
                if name.startswith('minimal') and small:
                    overlap += t['choices']
        scope[pop] = dict(labels)
        groups[pop] = dict(strata)
    return dict(weighting="One per labelled choice per start or finished type. A planarity row count gives one vote per start or type.",
                planarity_on_archived_prefix=groups, scope=scope, rows=rows, appearances=names,
                total_appearances=evaluations, fewest_already_in_minimal=fewest,
                minimal_already_in_small_codes=overlap, distinct_within_location=evaluations-fewest-overlap)


def compare_coverage():
    """Rebuild every row of the predecessor's table from its independent word lists."""
    parent = PRIOR.parent
    old = json.loads((parent/'cells.json').read_text())['coverage_of_all_listed_words']['rows']
    counts = Counter()
    locations = defaultdict(set)
    with gzip.open(parent/'choices.jsonl.gz', 'rt') as stream:
        for row in map(json.loads,stream):
            holders = {v:[i for i,s in enumerate(row['supports']) if v in s] for v in {v for s in row['supports'] for v in s}}
            crosses = [[tuple(sorted((u,v))) for u in holders[x] for v in holders[y]] for x,y in row['pairs']]
            for word,minimal in row['words']:
                mult = Counter(pair for i in word for pair in crosses[i])
                group = row['population'],minimal,len(word)==row['fewest'],max(mult.values())
                counts[group] += 1
                locations[group].add(row['id'])
    result = [dict(population=p,minimal=m,fewest=f,highest_cover_count=c,labelled_words=counts[p,m,f,c],
                   distinct_locations=len(locations[p,m,f,c])) for p,m,f,c in sorted(counts)]
    assert result==old
    return result


def hand_controls():
    # A failing pair corresponds to positions (0,2) and (1,3) of its cycle.
    # Permuting labels independently tests the local descent step.
    cases = Counter()
    for cycle in permutations(range(4)):
        a,c,b,d = cycle
        interleaves = (min(a,b)<c<max(a,b)) != (min(a,b)<d<max(a,b))
        descents = sum(u>v for u,v in zip(cycle,cycle[1:]+cycle[:1]))
        assert descents%2 == interleaves
        cases[descents] += 1
    source = next(r for r in map(json.loads,INPUT.read_text().splitlines()) if r['population']=='birth' and r['key']==3997)
    positions = [1,5,7,13,17]
    selected = [source['pairs'][i] for i in positions]
    before = []
    for x,y in selected:
        a,b = [i for i,s in enumerate(source['supports']) if x in s]
        c,d = [i for i,s in enumerate(source['supports']) if y in s]
        before.append((a,c,b,d))
    assert before[2]==before[3]
    assert len({v for pair in selected for v in pair})==2*len(selected)
    after = [before[i] for i in (0,1,4)]
    data = [measure_cycles(lists) for lists in (before,after)]
    assert [r['euler'] for r in data] == [2,1]
    assert [r['max_coverage'] for r in data] == [4,2]
    assert [r['sign'] for r in data] == [1,1]
    return dict(descent_counts_over_all_24_orders=cases, doubled_pair_deletion=dict(
        interpretation="Five-pair choice at the closure grown from census start 3997. Knot 3 holds two marked values. Deleting cells 2 and 3 (from zero) is the forced doubled-pair move.",
        indices=positions,failing_pairs=selected,supports=source['supports'],before=before,after=after,
        before_properties=data[0],after_properties=data[1]))


def main():
    result=dict(freeze=compare_freeze(),published_accounting=compare_published(),previous_full_coverage_table=compare_coverage(),hand_controls=hand_controls())
    (HERE/'record_check.json').write_text(json.dumps(result,indent=1)+'\n')
    counts=result['published_accounting']
    print(result['freeze'],counts['total_appearances'],counts['distinct_within_location'],counts['planarity_on_archived_prefix'])

if __name__=='__main__':
    main()
