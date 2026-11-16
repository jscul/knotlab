"""L <= 3 at every depth for the constant-3 descriptions by anchored chains (chain_ties.search_bounded3_machines), with automatic
states for life and for the freeness of the pair of a constrained triple that lies on one side. DIRECT-REACH-20261115-001, the thread's own code, 2026-11-16."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'exploratory'))
from chain_ties import search_bounded3_machines  # noqa: E402
from separation import machines  # noqa: E402
from window_types import population_D  # noqa: E402

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'constant-3'
    prof_of = {'constant-2': [2] * 4, 'constant-3': [3] * 4, 'half-rate': [3, 3, 4, 4]}
    wt = json.load(open(HERE / 'exploratory/window_tree_census.json'))['cases']
    rows = {}
    for cid, key, prof, cls in population_D():
        if prof != prof_of[which]:
            continue
        Ms = machines(key)
        r = search_bounded3_machines(key, Ms) if Ms else None
        rows[cid] = dict(profile=prof, relative_class=cls, bounded_orbits='k3' in wt[cid], machines=Ms, chain=r)
        print(cid[:12], prof, cls, 'bounded' if 'k3' in wt[cid] else 'growing', 'machines', len(Ms),
              json.dumps(r)[:160], flush=True)
    json.dump(rows, open(HERE / ('chain_bounded3_%s.json' % which), 'w'), indent=1)
    for b in (True, False):
        sub = [r for r in rows.values() if r['bounded_orbits'] == b]
        print('bounded' if b else 'growing', len(sub), 'with L <= 3 at every depth:', sum(1 for r in sub if r['chain']))
