"""Join the independent results by original identifier and check the claims at each closure."""
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from split_recount import verify
from split_search import ReaderSearch, split_choices


HERE = Path(__file__).resolve().parent


def indexed(filename):
    rows = {}
    with (HERE/filename).open() as stream:
        for r in map(json.loads,stream):
            key = (r['population'],r['key'])
            assert key not in rows
            rows[key] = r
    return rows


def main():
    inputs = indexed('rebuilt_inputs.jsonl')
    splits = indexed('split_rows.jsonl')
    rings = indexed('ring_rows.jsonl')
    assert inputs.keys() == splits.keys() == rings.keys()
    failures = {r['start']:r for r in map(json.loads,(HERE/'failure_rows.jsonl').open())}
    study_rows = {r['start']:r for r in map(json.loads,(HERE.parent/'results.jsonl').open())}
    birth_keys = {k for (p,k) in inputs if p=='birth'}
    assert birth_keys == set(failures) == set(study_rows)
    t = defaultdict(Counter)
    four_way = Counter()
    pos = 0
    five_ring_records = []
    for key in sorted(birth_keys):
        r,ring,data = splits['birth',key], rings['birth',key], inputs['birth',key]
        strict, general = r['strict_min'],r['general_min']
        count = failures[key]
        k4 = ring['four']
        assert (strict == 3) == k4 == count['every fewest odd is strict']
        assert (strict == count['fewest failing pairs, odd']) == bool(count['strict odd choices at minimum'])
        assert r['archived_fields_agree']
        if strict:
            fs = study_rows[key]['strict readers']
            verify(data, dict(readers=fs,failing_pairs=fs), True)
            assert len(fs) == strict
            pos+=1
        if ring['length']:
            assert strict == ring['length']
        if strict and general < strict:
            t['general uses fewer readers than strict'][f'{strict} to {general}'] += 1
        if strict and not ring['length']:
            t['strict without an odd ring'][strict] += 1
        if not strict and general:
            t['only a general split by minimum'][general] += 1
        if strict and count['fewest failing pairs, odd'] < strict:
            t['unrestricted failing-pair minimum below strict'][f"{count['fewest failing pairs, odd']} to {strict}"] += 1
        if ring['all_lengths'] == [5]:
            t['general minima where shortest ring has length five'][general] += 1
            search = ReaderSearch(data['supports'],data['pairs'])
            try:
                strict_count = split_choices(search)['strict_odd_choices']
            finally:
                search.free_data.cache_clear()
            five_ring_records.append(dict(census_start=key, strict_words=strict_count))
            t['number of strict odd words where shortest ring has length five'][strict_count] += 1
        four_way[str(ring['all_lengths'])] += 1
    extension = json.loads((HERE/'whole_extension.json').read_text())
    tested = {r['census_start'] for r in extension['rows']}
    positives = {k for (p,k),r in splits.items() if p == 'whole' and r['general_min']}
    assert tested == positives
    for r in extension['rows']:
        key = r['census_start']
        for field in ('new_split','new_strict_split'):
            w=r[field]
            if w:
                verify(inputs['whole',key],w,field=='new_strict_split')
                assert set(map(tuple,w['failing_pairs'])) - set(map(tuple,inputs['birth',key]['pairs']))
    extra = [r for r in extension['rows'] if r['new_strict_split']]
    compared = [{'census_start':k,'knots':r['knots'],'round':r['round'],
                 'birth':splits['birth',k]['general_min'],'whole':r['general_min']}
                for (p,k),r in splits.items() if p=='whole' and k in birth_keys
                and splits['birth',k]['general_min'] != r['general_min']]
    shape = json.loads((HERE/'shapes.json').read_text())
    norings = sum(t['strict without an odd ring'].values())
    assert norings == shape['closures']
    odd = {p:sum(r['odd'] for (q,_),r in inputs.items() if p==q)
           for p in ('birth','whole','type','fixture')}
    # In the five-knot fixture, suppress the sole two-distinction knot.
    f = inputs['fixture','closure F, grown']
    knots = list(map(set,f['supports']))
    middle, = (i for i,k in enumerate(knots) if len(k)==2)
    remaining = [i for i in range(len(knots)) if i!=middle]
    assert all(knots[a]&knots[b] or (knots[a]&knots[middle] and knots[b]&knots[middle])
               for a,b in combinations(remaining,2))
    # Two anticommuting self-adjoint qubit involutions have scalar common commutant.
    # A third setting commuting with both cannot also fail with a fourth on that qubit.
    key = 4308
    word = splits['birth',key]['general_witness']
    reader = next(g for g in word['readers'] if set(g) == {3,6,8,13})
    inside = [p for p in word['failing_pairs'] if p[0] in reader]
    assert inside == [[3,8],[3,13],[6,8]]
    report = dict(single_qubit_counterexample=dict(census_start=key,knots=8,
                  reader=reader,failing_pairs=inside),weighting='one vote per eligible census start, separately one vote per finished type',
                  total_inputs=len(inputs),odd_attainable=odd,
                  original_minimum_strict_witnesses_directly_verified=pos,
                  equal_closure_sets=['four mutually meeting knots','fewest strict readers is three',
                                      'all minimum odd failing-pair choices are strict'],
                  size_of_equal_sets=sum(r['four'] for (p,_),r in rings.items() if p=='birth'),
                  tables=t,five_ring_records=five_ring_records,available_ring_lengths=four_way,whole_general_minimum_changed=compared,
                  extra_whole_split_choices_at=extension['starts_with_new_choice'],
                  extra_strict_whole_split_at=[a['census_start'] for a in extra],
                  five_knot_fixture=dict(dimension=f['dimension'],odd_words=2**(f['dimension']-1),
                      two_distinction_knot=middle,removing_it_and_joining_its_holders_leaves_four_mutually_meeting_knots=True))
    (HERE/'reconciliation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=1))


if __name__=='__main__':
    main()
