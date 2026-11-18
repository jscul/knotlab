"""Ground truth for DECIDE-SMALL-20261117-001 (the thread's own code, 2026-11-17): the census's certified search (LEVEL-REACH,
DIRECT-REACH's threshold adaptation, LRAT certificates) computes L_9(3, s), s = 1..4, on 50 decided patterns of patterns.jsonl:
every pattern decided by T3, T4 or T5, then the first decided ones in draw order, to 50. Each decided reading must fit its verdict:
- T1 and T3 (forgetting length r): L >= 1 + ceil(s / r) (Theorems F and F');
- T5 (product length l0): L >= (floor(n / l0) + 3) / 2 with n = min(s - 1, s + r - R) (Theorem G on the component);
- T2: L <= the two-orbit bond at (s, tier 9 - 3 - s) (Theorem K);
- T4: L <= the least orbit-and-block or stem bond there (Theorem K*).
Certificates go to DIRECT-REACH's codex/certificates_decide/ (retention requires a path under codex/), packed afterwards
into artifacts/DECIDE-SMALL-20261117-001/. Writes ground_truth.json."""
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODEX = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex'
sys.path.insert(0, str(CODEX))
sys.path.insert(0, str(HERE))
import retention  # noqa: E402
retention.PROOF_DIR = CODEX / 'certificates_decide'  # retention needs it under codex/; packed into artifacts/ afterwards
retention.PROOF_DIR.mkdir(parents=True, exist_ok=True)
from retention import ProofStore  # noqa: E402
import reach  # noqa: E402
from reuse import search  # noqa: E402
import decide  # noqa: E402

N, K0, S = 9, 3, 4


def certified_L(key, budget):
    wd = Path(tempfile.mkdtemp())
    try:
        store = ProofStore(wd, (1 << 12) - 1)
        reach.NAMESPACE['BUDGET'] = float(budget)
        original = search.SearchEngine.search

        def retained(engine, *a, **kw):
            with retention.context(store, kw.get('deadline')):
                return original(engine, *a, **kw)
        search.SearchEngine.search = retained
        try:
            with retention.context(store):
                res = reach.CENSUS_COMPUTE(key, wd, N=N, k0=K0, S=S, histograms=False, k_max=10, selected_s=None)
        finally:
            search.SearchEngine.search = original
        return {lv['s']: lv['L_N'] for lv in res['levels']}, sorted(store.records)
    finally:
        shutil.rmtree(wd, ignore_errors=True)


def bounds(row, s):
    """(lower, upper) from the verdict at depth 9, tier r = 9 - 3 - s."""
    tree = decide.WindowTree(row['key'])
    r = N - K0 - s
    v = row['verdict']
    if v in ('grows (T1)', 'grows (T3)'):
        rr = row['T1_r'] if v == 'grows (T1)' else row['T3_r']
        return 1 + math.ceil(s / rr), None
    if v == 'grows (T5)':
        F = tree.feasible(20)
        r0 = next(x for x in range(19) if F[x] == F[x + 1])
        n = min(s - 1, s + r - (r0 + 1))
        return (max(n, 0) // row['T5_l0'] + 3) / 2, None
    if v == 'bounded (T2)':
        e = decide.every_depth_cross(tree, 3)
        return None, decide.at(e, r, s, 1, e['r0'])
    if v == 'bounded (T4)':
        b = decide.every_depth_block(tree, 3, cap=8)
        h = decide.every_depth_head(tree, 3, 2, cap=8)
        vals = [decide.at(b, r, s, 1, b['r0'] + 1), decide.at(h, r, s, 3, h['r0'])]
        vals = [x for x in vals if x is not None]
        return None, (min(vals) if vals else None)
    return None, None


if __name__ == '__main__':
    rows = [json.loads(l) for l in open(HERE / 'patterns.jsonl')]
    decided = [r for r in rows if r['verdict'].startswith(('grows', 'bounded'))]
    late = [r for r in decided if r['verdict'] in ('grows (T3)', 'grows (T5)', 'bounded (T4)')]
    pick = late + [r for r in decided if r not in late][:max(0, 50 - len(late))]
    out, bad = [], 0
    for r in pick:
        L, refs = certified_L(r['key'], 60)
        cells = []
        for s in range(1, S + 1):
            lo, hi = bounds(r, s)
            val = L.get(s)
            ok = None
            if isinstance(val, int):
                ok = (lo is None or val >= lo) and (hi is None or val <= hi)
                bad += not ok
            cells.append(dict(s=s, L9=val, lower=lo, upper=hi, fits=ok))
        out.append(dict(index=r['index'], pattern=r['pattern'], verdict=r['verdict'], cells=cells, refutations=len(refs)))
        print(r['index'], r['verdict'], [(c['s'], c['L9'], c['fits']) for c in cells], flush=True)
        json.dump(dict(rows=out, misfits=bad), open(HERE / 'ground_truth.json', 'w'), indent=1)
    print('misfits', bad)
