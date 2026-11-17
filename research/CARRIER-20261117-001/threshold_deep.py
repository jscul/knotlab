"""Deeper threshold readings (CARRIER-20261117-001, the thread's own wrapper, 2026-11-17): is there a bond of at most c members meeting
level 3 and level 3 + s at depth N? The query is threshold.py's (copied, so that the run's own file stays as it ran), with N, s and c
as arguments; every refutation is certified by LRAT into codex/certificates_carrier/.
Usage: threshold_deep.py <index> <N> <c> <budget> <s> [<s> ...]; writes threshold_deep_<index>_N<N>_c<c>.json (the first two bound-6 runs wrote _N<N>.json, renamed to _c6)."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODEX = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex'
sys.path.insert(0, str(CODEX))
import retention  # noqa: E402
retention.PROOF_DIR = CODEX / 'certificates_carrier'
retention.PROOF_DIR.mkdir(exist_ok=True)
from retention import ProofStore  # noqa: E402
import reach  # noqa: E402
from reuse import search  # noqa: E402


def query(key, workdir, store, k0, s_values, k_max, budget, N):
    reach.NAMESPACE['BUDGET'] = float(budget)
    original = search.SearchEngine.search

    def retained_search(engine, *args, **kwargs):
        with retention.context(store, kwargs.get('deadline')):
            return original(engine, *args, **kwargs)
    search.SearchEngine.search = retained_search
    try:
        with retention.context(store):
            result = reach.CENSUS_COMPUTE(key, workdir, N=N, k0=k0, S=max(s_values), histograms=False, k_max=k_max,
                                          selected_s=s_values)
    finally:
        search.SearchEngine.search = original
    for row in result['levels']:
        value = row['L_N']
        verdict = ('yes' if isinstance(value, int) and value <= k_max else
                   'no' if value == 'none' or (isinstance(value, str) and value.startswith('> ')) else 'undecided')
        row['thresholds'] = {str(k_max): verdict}
    return result


if __name__ == '__main__':
    index, N, c, budget = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    s_values = [int(x) for x in sys.argv[5:]]
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    key = third[index]['key']
    wd = Path(tempfile.mkdtemp())
    try:
        store = ProofStore(wd, (1 << 12) - 1)
        res = query(key, wd, store, 3, s_values, k_max=c, budget=budget, N=N)
    finally:
        shutil.rmtree(wd, ignore_errors=True)
    cells = [dict(s=lv['s'], L_N=lv['L_N'], within_bound=lv['thresholds'][str(c)], bond=(lv.get('anywhere') or {}).get('bond'),
                  seconds=lv.get('seconds')) for lv in res['levels']]
    out = dict(index=index, key=key, N=N, k0=3, bound=c, budget=budget, cells=cells, refutations=sorted(store.records),
               incomplete=len(store.incomplete))
    json.dump(out, open(HERE / ('threshold_deep_%s_N%d_c%d.json' % (index, N, c)), 'w'), indent=1)
    print(index, N, c, [(x['s'], x['L_N'], x['within_bound']) for x in cells], flush=True)
