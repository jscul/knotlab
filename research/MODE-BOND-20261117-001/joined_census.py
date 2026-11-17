"""The product test along joined children only (MODE-BOND-20261117-001, the thread's own code): on the census's 786 small-orbit
descriptions alive at every depth (181 distinct patterns), and on KEEP-REACH's 39 third-class descriptions. A description that passes
grows linearly (Theorem G on the component of level 3); a bounded one must fail. Writes joined_census.json."""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree  # noqa: E402
from decorated import Decorated  # noqa: E402
from growth13 import joined_automaton  # noqa: E402


def light(key):
    D = Decorated.__new__(Decorated)
    D.tree = WindowTree(key)
    F = D.tree.feasible(20)
    D.r0 = next(r for r in range(19) if F[r] == F[r + 1])
    D.Fc = F[D.r0]
    D.nt = len(D.tree.types)
    return D


if __name__ == '__main__':
    census = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/census_keep.json'))['rows']
    keys = {}
    for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
        r = json.loads(line)
        if 'key' in r and r.get('case') in census:
            keys[r['case']] = r['key']
    out = {'census': {}, 'third': {}}
    for cid, row in census.items():
        if not (row.get('small_orbits') and row.get('alive_every_depth')):
            continue
        a = joined_automaton(light(keys[cid]))
        out['census'][cid[:12]] = dict(forgets=row.get('r_stable') is not None, l0=a['l0'])
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    for idx, r in third.items():
        a = joined_automaton(light(r['key']))
        out['third'][idx] = dict(kind=r['kind'], l0=a['l0'])
    c = out['census'].values()
    tally = dict(forget_pass=sum(v['forgets'] and v['l0'] is not None for v in c), forget_fail=sum(v['forgets'] and v['l0'] is None for v in c),
                 never_pass=sum((not v['forgets']) and v['l0'] is not None for v in c), never_fail=sum((not v['forgets']) and v['l0'] is None for v in c))
    tk = {}
    for v in out['third'].values():
        k = (v['kind'][:24], v['l0'] is not None)
        tk[str(k)] = tk.get(str(k), 0) + 1
    out['tally'] = tally
    out['third_tally'] = tk
    json.dump(out, open(HERE / 'joined_census.json', 'w'), indent=1)
    print(tally, tk)
