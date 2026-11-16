"""U pilot (DIRECT-REACH-20261115-001, the thread's own wrapper, 2026-11-16): the first 6 population-U descriptions by case id.

Reuses the gated Codex modules unchanged (codex/ties.py, codex/reach.py, codex/retention.py). Per description: the N = 9 union fate and
tie classes (step 1); then, for every s at which the census was undecided, L = 2 from a spanning tie class if there is one, otherwise the
census search at top level 3 with k_max = 10 and 900 s (step 5 of codex_spec.md). Step 2's 300 s threshold search, the homomorphisms and
life to depth 12 are skipped: the 900 s search tries the smaller sizes first, and the pilot asks only whether 900 s decides the cells.
The first U description already ran this path in the Codex smoke (codex/case_results/U/00a344d3f150...json) and is not rerun.
"""
import json
from pathlib import Path
import shutil
import sys
import time

CODEX = Path(__file__).resolve().parents[1] / 'codex'
sys.path.insert(0, str(CODEX))
from reuse import pattern  # noqa: E402
from population import populations  # noqa: E402
from retention import ProofStore, context, union_fate  # noqa: E402
from ties import compute_ties  # noqa: E402
from reach import query  # noqa: E402

HERE = Path(__file__).resolve().parent
PANEL = []
SKIP = {'00a344d3f150db37014b0d13d3ca12acf65eee4350350df05052e6df304ce805'}


def setup(params):
    global PANEL
    PANEL = [row for row in populations()['U'][:6] if row['id'] not in SKIP]
    (CODEX / 'tmp').mkdir(exist_ok=True)


def cases():
    for row in PANEL:
        yield row['id'], row


def run(case_id, payload):
    work = CODEX / 'case_work' / ('pilot_' + case_id)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    started = time.monotonic()
    key = payload['key']
    store = ProofStore(work, 1023)
    try:
        K = pattern.pattern(key, 9)
        with context(store):
            fate = union_fate(K, 1023, work, 600)
        ties = compute_ties(K, 1023, work, case_id, store=store) if fate['verdict'] == 'alive' else None
        followups = []
        for row in payload['census']['levels']:
            if row['L_N'] != 'undecided':
                continue
            s = row['s']
            span = next((r for r in (ties or {}).get('summaries', []) if r['k0'] == 3 and r['s'] == s and r['spanning']), None)
            if span is not None:
                followups.append({'s': s, 'L_N': 2, 'reused_step_1': True})
                continue
            q = query(key, work, store, 3, [s], k_max=10, budget=900)
            lv = q['levels'][0]
            followups.append({'s': s, 'L_N': lv['L_N'], 'seconds': lv.get('seconds'),
                              'bond': (lv.get('anywhere') or {}).get('bond')})
        out = {'case': case_id, 'key': key, 'census_levels': [r['L_N'] for r in payload['census']['levels']],
               'union_N9': fate['verdict'], 'tie_forced_pairs': (ties or {}).get('forced_pair_count'),
               'followups': followups, 'decided_all': all(isinstance(f['L_N'], int) for f in followups),
               'seconds': time.monotonic() - started, 'refutations': store.records, 'incomplete': store.incomplete}
        (HERE / 'pilot_U_results').mkdir(parents=True, exist_ok=True)
        (HERE / 'pilot_U_results' / (case_id + '.json')).write_text(json.dumps(out, indent=1, sort_keys=True))
        out.pop('refutations')
        return out
    finally:
        if work.exists():
            shutil.rmtree(work)
