"""Check frozen files, prior records, and the effect of exchanging two knot checks."""
import json
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from population import HERE, independent, owners, rebuild, supports_from_meetings, system
from whole_extension import witness_with_pair

ROOT = HERE.parents[2]
REL = HERE.parent.relative_to(ROOT).as_posix()
FREEZE = '4136dd3855'
CLOSE = '1484cd1f12'


def git(*args):
    return subprocess.check_output(['git','-c','core.packedGitWindowSize=16m','-c','core.packedGitLimit=64m',*args],cwd=ROOT)


def sign_for_order(row, holders, order):
    ranks = {k:i for i,k in enumerate(order)}
    intervals = {d:tuple(sorted(ranks[k] for k in holds)) for d,holds in holders.items()}
    sign = 0
    for i,(x,y) in enumerate(row['pairs']):
        a,b = intervals[x]
        c,d = intervals[y]
        if (a < c < b) != (a < d < b):
            sign |= 1 << i
    return sign


def sample_even_ring(n):
    knots = supports_from_meetings([(0,k+1) for k in range(n)]
                                  + [(k+1,(k+1)%n+1) for k in range(n)])
    row = system([knots])
    # A nonempty odd choice uses a pair. Force each possible pair in turn.
    trials = []
    for p in row['pairs']:
        witness,subproblems = witness_with_pair(row,p)
        trials.append(dict(required=p,split=witness is not None,subproblems=subproblems))
    return dict(ring_length=n,whole_odd=row['odd'],extra_meetings=0,
                some_split=any(t['split'] for t in trials),trials=trials)


def main():
    frozen = git('show',f'{FREEZE}:{REL}/README.md')
    final = git('show',f'{CLOSE}:{REL}/README.md')
    assert final.startswith(frozen)
    diff = git('diff',FREEZE,CLOSE,'--',REL+'/readers.py')
    assert not diff
    current = (HERE.parent/'readers.py').read_bytes()
    assert current == git('show',f'{FREEZE}:{REL}/readers.py')
    reports = dict(frozen_lines=len(frozen.splitlines()),added_lines=len(final.splitlines())-len(frozen.splitlines()),
                   original_search_byte_identical=True)
    rows = list(map(json.loads,(HERE/'rebuilt_inputs.jsonl').open()))
    exchanges = Counter()
    for row in rows:
        h=owners(row['supports'])
        knots = list(range(len(row['supports'])))
        base_rank = independent(row['checks'])
        for (a,b),eq in zip(combinations(knots,2),row['checks'],strict=True):
            rest = [k for k in knots if k not in (a,b)]
            left=sign_for_order(row,h,[a,b,*rest])
            right=sign_for_order(row,h,[b,a,*rest])
            assert left^right == eq
            assert independent([*row['checks'],left^row['cost']]) == base_rank
            exchanges[row['population']] += 1
    reports['exchange_of_every_knot_pair_per_code']=exchanges
    archive = {
        'birth':list(map(json.loads,(HERE.parent/'results.jsonl').open())),
        'type':list(map(json.loads,(HERE.parent/'census_types.jsonl').open())),
        'fixtures':list(json.loads((HERE.parent/'fixtures.json').read_text()).values()),
    }
    reports['archived_short_enumerations']={key:sum(r.get('enumeration agrees') is True for r in data)
                                            for key,data in archive.items()}
    primary_rows = [r for records in archive.values() for r in records]
    whole_rows = [r for r in archive['birth'] if 'whole: strict' in r]
    whole_rows += list(map(json.loads,(HERE.parent/'whole_only.jsonl').open()))
    reports['archived_gate_flags'] = dict(
        primary_rows=len(primary_rows),
        strict_search_agreements=sum(r['strict: integer program and satisfiability agree'] for r in primary_rows),
        primary_certificates_flagged_passed=sum(r['certificates pass'] for r in primary_rows),
        primary_unsettled=sum('unsettled' in r for r in primary_rows),
        whole_rows=len(whole_rows),whole_unsettled=sum('whole: unsettled' in r for r in whole_rows))
    seen_operators=json.loads(rebuild.CENSUS.read_text())
    reports['earlier_operator_and_current_strict_by_type'] = dict(Counter(
        f"earlier {old['operator']}, strict {r['strict']}"
        for old,r in zip(seen_operators,archive['type'],strict=True)))
    reports['even_ring_stress'] = sample_even_ring(6)
    query = 'multipartite parity contradiction local settings stabilizer readout opposite meeting all versus nothing disjoint anticommuting observables'
    def track(*args):
        return subprocess.check_output([sys.executable,'-B','scripts/track.py',*args],cwd=ROOT)
    found = json.loads(track('objects',query,'--until','2026-11-27','--exclude',HERE.parent.name,
                             '--limit','6','--json'))
    reports['prior_search'] = {
        'gate':track('objects-gate',REL+'/README.md').decode().strip(),
        'index_matches':[r['id'] for r in found['index']],
        'independent_query':query,
        'full_text_query':'reader.{0,90}(GHZ|fail to commute)|odd wheel|odd cycle graph state|odd ring.{0,80}reader|all.versus.nothing',
        'full_text_files':git('grep','--threads','1','-ilE',
            'reader.{0,90}(GHZ|fail to commute)|odd wheel|odd cycle graph state|odd ring.{0,80}reader|all.versus.nothing',
            FREEZE+'^','--','research/**/decision.md','docs/KNOT_INTUITION.md').decode().splitlines()
    }
    (HERE/'record_audit.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(reports['archived_short_enumerations'],reports['exchange_of_every_knot_pair_per_code'],
          reports['earlier_operator_and_current_strict_by_type'],reports['even_ring_stress']['some_split'])


if __name__ == '__main__':
    main()
