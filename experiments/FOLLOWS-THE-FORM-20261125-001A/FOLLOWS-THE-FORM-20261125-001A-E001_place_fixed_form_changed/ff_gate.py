"""Run R0, the gate, of FOLLOWS-THE-FORM-20261125-001A-E001.

  python -B ff_gate.py starts            # the three starts of FF 2, the run counts, the seeds' shapes
  python -B ff_gate.py run --chunk i/8   # a chunk of the 400 sampled runs (deviations 3, 24, 25)
  python -B ff_gate.py summary           # gate.json
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import random
import time
from collections import defaultdict

import ff_core as C

if C.FOLD_DIR not in sys.path:
    sys.path.append(C.FOLD_DIR)
import pm  # noqa: E402  (the fold engine, unchanged, read-only; already on the path through eng)

WRITTEN = {   # FF 2, the three starts written out for checking
    ('B', 'mixed', 'one:2'): [[0, 1, 2, 6], [0, 3, 4, 5], [7, 8, 6]],
    ('D', 'mixed', 'two:1,2'): [[0, 2, 3, 8], [0, 1, 4], [1, 5, 6, 7], [9, 10, 8], [9, 11, 12]],
    ('A', None, None): [[0, 1, 2, 3]],
}
COUNTS = {'R1': 13680, 'R2': 5490, 'R2u': 5490, 'R3': 5670, 'R4': 5490}


def check_starts():
    sd = C.seeds_cached()
    out = {'starts': [], 'counts': {}, 'ok': True}
    for (f, fam, s), want in WRITTEN.items():
        S = None if s is None else sd['second'][fam][s]
        got, _, _ = C.build_start(sd['first'][f], S)
        ok = got == want
        out['starts'].append({'first': f, 'second': s, 'want': want, 'got': got, 'equal': ok})
        out['ok'] &= ok
    for rs, n in COUNTS.items():
        m = len(C.runset_runs(rs))
        out['counts'][rs] = m
        out['ok'] &= m == n
    raw = C.load_seeds()
    fams = {fam: len(v) for fam, v in raw['second'].items()}
    out['families'] = fams
    out['ok'] &= fams == {'mixed': 50, 'chains': 62, 'second': 37, 'fresh': 60}
    for s in raw['second']['chains']:
        C.chain_counts(s)
    # every start of every run set, linked and unlinked, has three or more places a knot (asserted in build_start)
    for rs in COUNTS:
        for r in C.runset_runs(rs):
            C.start_of(r)
    out['three_places_everywhere'] = True
    return out


def sample():
    runs = C.runset_runs('R1') + C.runset_runs('R2')
    rng = random.Random(1)
    return rng.sample(runs, 400)


# ----------------------------------------------------------------------------------------- the second growth
KIND = {'start': 0, 'join': 1, 'offshoot': 2}


def wl_invariant(S, iters=4):
    """Weisfeiler-Leman refinement over knots and distinctions (deviations 24): the sorted multiset of final labels."""
    nk, nd = S.n_knots, S.n_distinctions
    removed = set(S.removed)
    ks = [u for u in range(nk) if u not in removed]
    children = defaultdict(list)
    for u in ks:
        for p in S.parents[u]:
            children[p].append(u)
    kl = {u: hash((0, S.made[u], KIND[S.kind[u]], len(S.parents[u]))) for u in ks}
    dl = {d: hash((1, bool(S.barred[d]), len(S.holders[d]))) for d in range(nd)}
    for _ in range(iters):
        nk_ = {u: hash((kl[u], tuple(sorted(dl[d] for d in S.places[u])), tuple(sorted(kl[p] for p in S.parents[u])),
                        tuple(sorted(kl[c] for c in children[u])))) for u in ks}
        nd_ = {d: hash((dl[d], tuple(sorted(kl[u] for u in S.holders[d])))) for d in range(nd)}
        kl, dl = nk_, nd_
    return hash((tuple(sorted(kl.values())), tuple(sorted(dl.values()))))


def compare_no_take(r):
    stars, n_first, n_second = C.start_of(r)
    run, _, _ = C.grow(r)
    law = pm.Law(ration=r['ration'], treatment=r['treatment'], release='RELEASE', knot_law=r['knot_law'],
                 closing='IMPLIED', take=None)
    R = pm.Run(pm.from_stars(stars), law, rounds=C.rounds_for(r['family']), knot_bound=3000)
    diffs, wl_diffs = [], []
    if len(run.snaps) != len(R.snap):
        diffs.append('rounds read: eng %d, pm %d' % (len(run.snaps) - 1, len(R.snap) - 1))
    for i, (A, B) in enumerate(zip(run.snaps, R.snap)):
        if A.places != B.places:
            diffs.append('round %d: places' % i)
        if [tuple(p) for p in A.parents] != [tuple(p) for p in B.parents]:
            diffs.append('round %d: parents' % i)
        if A.made != B.made or A.kind != B.kind:
            diffs.append('round %d: made/kind' % i)
        if A.barred != B.barred:
            diffs.append('round %d: barred' % i)
        if wl_invariant(A) != wl_invariant(B):
            wl_diffs.append(i)
    gA = None if run.guard is None else (run.guard['round'], run.guard['what'])
    gB = None if R.guard is None else (R.guard['round'], R.guard['what'])
    if run.stop != R.stop or gA != gB:
        diffs.append('stop: eng %s %s, pm %s %s' % (run.stop, gA, R.stop, gB))
    took = sum(len(b['takes']) for rec in run.recs for b in rec['births'])
    if took:
        diffs.append('a birth took under no taking rule: %d' % took)
    return {'check': 'second growth', 'exact_equal': not diffs, 'wl_equal': not wl_diffs and len(run.snaps) == len(R.snap),
            'diffs': diffs[:6], 'wl_diff_rounds': wl_diffs[:6], 'rounds_read': run.rounds_read, 'stop': run.stop,
            'knots': run.S.n_knots, 'rounds_compared': min(len(run.snaps), len(R.snap))}


def takes_by_words(S0, births):
    """The take of a sole candidate recomputed from the rule's words (deviations 25), on the structure at the start of
    the round; holders rebuilt from the place lists."""
    hold = defaultdict(set)
    for u, P in enumerate(S0.places):
        for d in P:
            hold[d].add(u)
    mcache = {}

    def meets(u):
        m = mcache.get(u)
        if m is None:
            m = set()
            for d in S0.places[u]:
                m |= hold[d]
            m.discard(u)
            mcache[u] = m
        return m

    out = []
    for b in births:
        ps = list(b['parents'])
        if b['kind'] == 'offshoot':
            p = ps[0]
            own = set(S0.places[p])
            cands = {d for w in meets(p) for d in S0.places[w] if len(hold[d]) >= 2 and d not in own}
        else:
            common = None
            for p in ps:
                common = set(meets(p)) if common is None else (common & meets(p))
            common -= set(ps)
            held = set()
            for p in ps:
                held |= set(S0.places[p])
            cands = {d for w in common for d in S0.places[w] if len(hold[d]) >= 2 and d not in held}
        out.append(sorted(cands) if len(cands) == 1 else [])
    return out


def check_takes(r):
    run, _, _ = C.grow(r)
    n = nt = 0
    bad = []
    for t in range(1, run.rounds_read + 1):
        births = run.recs[t - 1]['births']
        want = takes_by_words(run.snaps[t - 1], births)
        for b, w in zip(births, want):
            n += 1
            nt += len(w)
            if list(b['takes']) != w:
                bad.append({'round': t, 'birth': b['id'], 'engine': list(b['takes']), 'rule': w})
    return {'check': 'takes', 'exact_equal': not bad, 'births': n, 'takes': nt, 'bad': bad[:6],
            'rounds_read': run.rounds_read, 'stop': run.stop, 'knots': run.S.n_knots}


def run_chunk(chunk):
    i, n = (int(x) for x in chunk.split('/'))
    C.cap_memory(6)
    smp = sample()
    out = C.JsonLines(C.out_path('gate_%dof%d.jsonl.gz' % (i, n)))
    t0 = time.time()
    for j, r in enumerate(smp):
        if j % n != i:
            continue
        t1 = time.time()
        row = compare_no_take(r) if r['take'] is None else check_takes(r)
        row.update({'sample_index': j, 'key': C.run_key(r), 'sec': round(time.time() - t1, 3)})
        out.write(row)
    out.close()
    C.log('gate chunk', chunk, 'done', '%.1fs' % (time.time() - t0))


def summary(n=8):
    st = check_starts()
    rows = []
    for i in range(n):
        rows += list(C.read_jsonl(C.out_path('gate_%dof%d.jsonl.gz' % (i, n))))
    rows.sort(key=lambda x: x['sample_index'])
    assert len(rows) == 400 and [x['sample_index'] for x in rows] == list(range(400))
    sg = [x for x in rows if x['check'] == 'second growth']
    tk = [x for x in rows if x['check'] == 'takes']
    res = {
        'starts': st,
        'sampled_runs': len(rows),
        'second_growth': {'runs': len(sg), 'exact_equal': sum(x['exact_equal'] for x in sg),
                          'wl_equal': sum(x['wl_equal'] for x in sg),
                          'rounds_compared': sum(x['rounds_compared'] for x in sg),
                          'first_differing': next((x for x in sg if not x['exact_equal']), None)},
        'takes': {'runs': len(tk), 'exact_equal': sum(x['exact_equal'] for x in tk),
                  'births': sum(x['births'] for x in tk), 'takes': sum(x['takes'] for x in tk),
                  'first_differing': next((x for x in tk if not x['exact_equal']), None)},
        'sample_by_runset': {rs: sum(1 for x in rows if x['key'].startswith(rs + '|')) for rs in ('R1', 'R2')},
    }
    ok_sg = all(x['exact_equal'] or x['wl_equal'] for x in sg)
    res['verdict'] = 'holds' if (st['ok'] and ok_sg and all(x['exact_equal'] for x in tk)) else 'fails'
    with open(C.out_path('gate.json'), 'w') as f:
        json.dump(res, f, indent=1, sort_keys=True)
    C.log('gate:', res['verdict'], json.dumps({k: res[k] for k in ('second_growth', 'takes')})[:600])
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('starts', 'run', 'summary', 'time'))
    ap.add_argument('--chunk', default='0/1')
    a = ap.parse_args()
    C.check_frozen()
    if a.what == 'starts':
        print(json.dumps(check_starts(), indent=1))
    elif a.what == 'run':
        run_chunk(a.chunk)
    elif a.what == 'time':
        C.cap_memory(6)
        smp = sample()
        t0 = time.time()
        for r in smp[:16]:
            compare_no_take(r) if r['take'] is None else check_takes(r)
        dt = (time.time() - t0) / 16
        C.log('gate: %.3f s a sampled run; estimate on 8 processes %.1f min' % (dt, dt * 400 / 8 / 60))
    else:
        summary()
