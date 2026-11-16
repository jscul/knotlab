"""The two specified, disjoint subsets of the retained census, sorted by case id."""
import gzip
import json
from reuse import CENSUS


def populations():
    with gzip.open(CENSUS, 'rt') as stream:
        records = sorted((json.loads(line) for line in stream), key=lambda row: row['case'])
    assert len({r['case'] for r in records}) == len(records)
    D, U = [], []
    for r in records:
        profile = [x['L_N'] for x in r['levels']]
        if r['union'] == 'alive' and profile in ([2]*4, [3]*4, [3, 3, 4, 4]):
            D.append({'id': r['case'], 'key': r['key'], 'memberships': r['memberships'],
                      'pop': 'D', 'census': r, 'half_rate': profile == [3, 3, 4, 4]})
        if (any(m['family'] == 'E_R' for m in r['memberships'])
                and r['classes']['relative']['class'] == 'bounded'
                and 'undecided' in profile):
            U.append({'id': r['case'], 'key': r['key'], 'memberships': r['memberships'],
                      'pop': 'U', 'census': r, 'half_rate': False})
    assert not ({r['id'] for r in D} & {r['id'] for r in U})
    return {'D': D, 'U': U}
