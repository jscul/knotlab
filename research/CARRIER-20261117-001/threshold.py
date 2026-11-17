"""The empirical test of Conjecture C' (CARRIER-20261117-001, the thread's own wrapper, 2026-11-17). For each of the 25 open patterns
of KEEP-REACH (13 whose top joints become products, 12 with a hidden dependence), at depth N = 11 from level 3 and s in {5, 6}: is
there a bond of at most c members, c the parent's two-orbit bound (8db5da810c00: 5; bace53f8f952: 4; ca1efb37ad88: 6)? C' predicts no
(the reach outgrows any bound without a two-orbit bond from the top). The search is DIRECT-REACH's threshold adaptation of the census
search (codex/reach.py) with every refutation certified by LRAT; its certificates are written to codex/certificates_carrier/ and
packed into one zstd archive afterwards. One process per pattern: `threshold.py <index>`; writes threshold_<index>.json."""
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
    """reach.query with the depth N as a parameter (reach.query fixes N = 9); otherwise the same code path."""
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

BOUND = {'8db5da810c00': 5, 'bace53f8f952': 4, 'ca1efb37ad88': 6}
index = sys.argv[1]
budget = int(sys.argv[2]) if len(sys.argv) > 2 else 900
rows = {str(json.loads(l)['index']): json.loads(l) for l in open(ROOT / 'research/KEEP-REACH-20261117-001/mutants_keep.jsonl')}
key = rows[index]['key']
c = BOUND[index.split('-')[0]]
wd = Path(tempfile.mkdtemp())
try:
    store = ProofStore(wd, (1 << 12) - 1)
    res = query(key, wd, store, 3, [5, 6], k_max=c, budget=budget, N=11)
finally:
    shutil.rmtree(wd, ignore_errors=True)
cells = [dict(s=lv['s'], L_N=lv['L_N'], within_bound=lv['thresholds'][str(c)], bond=(lv.get('anywhere') or {}).get('bond'),
              seconds=lv.get('seconds')) for lv in res['levels']]
out = dict(index=index, key=key, N=11, k0=3, bound=c, budget=budget, cells=cells,
           refutations=sorted(store.records), incomplete=len(store.incomplete))
json.dump(out, open(HERE / ('threshold_%s.json' % index), 'w'), indent=1)
print(index, c, [(x['s'], x['L_N'], x['within_bound']) for x in cells])
