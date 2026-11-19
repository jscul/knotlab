"""Score CLUSTER-ALL-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>

T1 and T3 from the runner; T2 from JOIN-GROWTH-20261118-001B's recorded growths (runs/join-growth, -mem, -mem2), each compared
with the rule on bare sizes over every recorded round."""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clusters as Cl  # noqa: E402
ROOT = Cl.ROOT
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    recs = load_results(sys.argv[1])
    out = {}
    for part in ('T1', 'T3', 'T4', 'T5'):
        arr = [a for cid, r in sorted(recs.items()) if cid.startswith(part) and r.get('status') == 'ok'
               for a in r['result']['arrangements']]
        missing = [cid for cid, r in recs.items() if cid.startswith(part) and r.get('status') != 'ok']
        out[part] = {'arrangements': len(arr), 'shards_not_ok': missing,
                     'verdicts': dict(Counter(a['verdict'] for a in arr)),
                     'by_outcome': {f'{v}/{o}': n for (v, o), n in Counter((a['verdict'], a['outcome']) for a in arr).items()},
                     'out_of_scope_why': dict(Counter(a['why'] for a in arr if a['verdict'] == 'out of scope')),
                     'misses': [a for a in arr if a['verdict'] == 'miss'][:200]}
    jg = _load('jg_job', ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/job.py')
    jr = {}
    for d in ('runs/join-growth', 'runs/join-growth-mem', 'runs/join-growth-mem2'):
        for k, r in load_results(str(ROOT / d)).items():
            if r.get('status') == 'ok':
                jr[k] = r
    t2 = {}
    for cid, p in jg.cases():
        if cid not in jr:
            t2[cid] = {'verdict': 'not grown'}
            continue
        e = [tuple(x) for x in p['edges']]
        sizes = Cl.J.bare_sizes(p['n'], e, p['surplus'])
        g = jr[cid]['result']
        c = g['counts']
        pred = Cl.series(sizes, e, len(c) + 1)
        if pred is None:
            v = 'out of scope'
        elif pred == 'stall':
            v = 'match' if g['outcome'] == 'stall' else 'miss'
        else:
            v = 'match' if pred[:len(c)] == c and (g['outcome'] != 'closed' or not any(pred[len(c):])) else 'miss'
        t2[cid] = {'verdict': v, 'rounds': len(c) - 1, 'why': Cl.analyse(sizes, e).get('why') if pred is None else None}
    out['T2'] = {'starts': len(t2), 'verdicts': dict(Counter(v['verdict'] for v in t2.values())),
                 'misses': [k for k, v in t2.items() if v['verdict'] == 'miss'], 'cases': t2}
    out['T4']['each'] = {cid: [a['verdict'], a['outcome'], a['counts'][:10], a.get('why')] for cid, r in sorted(recs.items())
                         if cid.startswith('T4') and r.get('status') == 'ok' for a in r['result']['arrangements']}
    out['verdict'] = {p: out[p]['verdicts'].get('miss', 0) == 0 and not out[p].get('shards_not_ok') for p in ('T1', 'T3', 'T4', 'T5')}
    out['verdict']['T2_consistency'] = out['T2']['verdicts'].get('miss', 0) == 0
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps({p: out[p]['verdicts'] for p in ('T1', 'T2', 'T3', 'T4', 'T5')}, indent=1), out['verdict'])


if __name__ == '__main__':
    main()
