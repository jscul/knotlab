"""Reconcile tested start-round occurrences and the raw closure rows."""
import argparse
from collections import Counter
import json
from time import perf_counter

from growth_replay import HERE, LAWS


def records(file):
    return [json.loads(line) for line in file.read_text().splitlines()]


def main(pilot):
    closed = {r['census_id']:r for r in json.loads((HERE/'closed_counts.json').read_text())['rows']}
    open_total = json.loads((HERE/'trace_strict_example.json').read_text())['per_law']
    closure, tested = {}, {}
    for law in LAWS:
        paths = sorted((HERE.parent/'out').glob(law+'_*'))
        count = Counter()
        for file in paths[:1] if pilot else paths:
            for r in records(file)[:-1]:
                x = closed[int(r['start'].split()[1])]
                assert x['bonds'] == r['bonds'] and x['boxes'] == r['boxes'] == 0
                assert r['a birth needed'] == 0 and r['example'] == [] and 'not searched' not in r
                count['search and birth fields matched'] += 1
        closure[law] = count

    evidence = ['open_eight_census.jsonl', 'open_eight_larger.jsonl', 'open_eight_sample_420_pilot.jsonl']
    evidence += sorted(p.name for p in HERE.glob('open_eight_target_*.jsonl'))
    used={law:set() for law in LAWS}
    automatic = {}
    for name in evidence[:1] if pilot else evidence:
        header,*rows,footer=records(HERE/name)
        assert 'seconds total' in footer
        for law in LAWS:
            info=header['roster']['coverage counts'][law]
            assert info['all formed open'] == open_total[law]['open stages after a funded round']
            automatic[law]=info['fewer than 12 distinctions']
        assert len(rows)==header['selected']
        count=Counter()
        for r in rows:
            assert r['strict boxes'] == 0 and r['structural candidates'] == 0
            for c in r['cases']:
                key=(c['census start'],c['round'])
                law=c['law']
                if key not in used[law]:
                    used[law].add(key)
                    count[law]+=1
        tested[name]={'normalized_systems':len(rows),'additional_stage_occurrences':count}
    limits={law:dict(all_open=open_total[law]['open stages after a funded round'],
                     fewer_than_12_distinctions=automatic[law], searched=len(used[law]),
                     remaining=open_total[law]['open stages after a funded round']-
                               len(used[law])-automatic[law]) for law in LAWS}
    return dict(archived_closure_rows=closure,open_eight_clause_searches=tested,coverage=limits)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    t=perf_counter()
    results=main(args.pilot)
    if not args.pilot:
        (HERE/'coverage.json').write_text(json.dumps(results,indent=2)+'\n')
    print(results['coverage'],round(perf_counter()-t,4))
