"""Focused implementation checks; fixtures are not the unselected brute30 gate."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import time
import top_data as d


def run(brute_fixtures=False):
    started=time.monotonic()
    cat=json.loads((d.HERE/'catalog.json').read_text())
    actual=Counter(('in:' if r['in_scope'] else 'out:')+r['final_verdict'] for r in cat['rows'])
    expected={'in:bounded_window':5067,'in:bounded_path_DP':7,'in:growing':632,'in:undecided':83,'out:bounded_window':129,'out:undecided':46}
    if actual!=expected:raise ValueError(('final population mismatch',actual))
    bounded=sorted((r['key'] for r in cat['rows'] if r['bounded']),key=d.top_order)[:200]
    if bounded!=cat['bounded_controls']:raise ValueError('bounded sample ordering')
    census=d.inputs.load_records()
    forgetting=sorted((k for k,r in census.items() if r['verdict']=='certified'),key=d.top_order)[:100]
    if forgetting!=[r['key'] for r in cat['forgetting_controls']]:raise ValueError('forgetting sample ordering')
    import controls
    c=controls.run()
    result=dict(passed=True,population=dict(actual),selection_counts=dict(bounded=len(bounded),forgetting=len(forgetting),two_block=len(cat['selected_two_block'])),pinning_controls=c,
                scope='implementation validation, not the unspecified official 30-family gate')
    if brute_fixtures:
        import two_block_brute
        fixtures=json.loads((d.HERE/'validation_fixtures.json').read_text())
        result['brute_fixtures']={name:two_block_brute.compare_family(key) for name,key in fixtures.items()}
        result['passed']=all(v['passed'] for v in result['brute_fixtures'].values())
        result['brute_checks']=sum(len(v['checks']) for v in result['brute_fixtures'].values())
        if not result['passed']:
            d.dump('validation.json',result)
            raise ValueError('independent unfolding fixture mismatch or cap')
    elif (d.HERE/'validation.json').exists():
        prior=json.loads((d.HERE/'validation.json').read_text())
        for k in ('brute_fixtures','brute_checks'):
            if k in prior:result[k]=prior[k]
    result['seconds']=time.monotonic()-started
    if (d.HERE/'frozen_sources.json').exists():
        import job
        job.setup({})
        result['frozen_sources_verified']=True
    d.dump('validation.json',result)
    print(json.dumps(dict(passed=result['passed'],brute_checks=result.get('brute_checks'),seconds=result['seconds']),indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--brute-fixtures',action='store_true');a=p.parse_args();run(a.brute_fixtures)
