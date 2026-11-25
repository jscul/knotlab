"""Run 3: the knot test of runs 1 and 2 (KD 6.2): every start knot, and 200 knots sampled uniformly (class
`knot-test`) per run, on run 2's registered runs (the structure after round 2T, or the last round read) and on run 1's
runs of the 219 three- and four-knot starts (after round 100 or the last round), both knot laws.  Not-all-equal: the
birth method at each knot's birth (start knots directly), and the direct test where the knot has at most 12 places.
Parity: the parity run is the not-all-equal run up to its first closing birth (Settled 4, R 9), tested by the two graph
forms of ranks and kernel (R 23).
usage: python -B run3.py run --procs 4 [--limit N]      writes run3.jsonl.gz"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import time

import kwr
import ktest
import run1
import run2
from run5 import _View


DIRECT_PLACES = 6       # R 31: the direct comparison in run 3 on sampled knots of at most 6 places


class _Prefix:
    """The structure after an earlier round as the prefix of knots < N (places fixed at birth), for the birth method
    and the direct test, which read holders only through a test against the knots left (knots.jointly_free) or not
    at all (knots.nae_direct): the holder lists need no filtering."""

    def __init__(self, S, N, nd):
        self.places = S.places[:N]
        self.holders = S.holders
        self.removed = set()
        self.n_knots = N
        self.n_distinctions = nd


def items():
    out = []
    for it in run2.items():
        if it['kind'] in ('named', 'bare ring', 'census'):
            out.append({'source': 'run2', 'start': it['start'], 'law': it['law'], 'rounds': 2 * it['T']})
    for it in run1.items():
        if it['small']:
            out.append({'source': 'run1', 'start': it['start'], 'law': it['law'], 'rounds': run1.ROUNDS})
    for k, it in enumerate(out):
        it['item'] = k
    return out


def run_item(it):
    t0 = time.time()
    key, lab = it['start'], it['law']
    gr = kwr.Grown(key, kwr.make_law(lab), it['rounds'], parts_every_round=False)
    S = gr.S
    rec = {'item': it['item'], 'source': it['source'], 'start': key, 'law': lab, 'rounds_done': gr.rounds_done,
           'stop': gr.stop, 'knots': S.n_knots, 'parity_closing_round': gr.parity_closing_round}
    from knots import jointly_free, nae_direct
    # not-all-equal
    smp = kwr.sample_sorted(kwr.rng_for(key, lab, 'nae', 'knot-test'), range(S.n_start, S.n_knots), 200)
    test = list(range(S.n_start)) + sorted(smp)
    res = {}
    V0 = _View(S, gr.n_knots[0], gr.n_dist[0])
    res.update(nae_direct(V0, list(range(S.n_start))))
    by_round = {}
    for u in smp:
        by_round.setdefault(S.made[u], []).append(u)
    for t, us in sorted(by_round.items()):
        Vb = _Prefix(S, gr.n_knots[t - 1], gr.n_dist[t - 1])
        nd = gr.n_dist[t - 1]
        for u in us:
            res[u] = jointly_free(Vb, [d for d in S.places[u] if d < nd])
    small = [u for u in smp if len(S.places[u]) <= DIRECT_PLACES]
    direct = nae_direct(S, small) if small else {}
    rec['nae'] = {'tested': sum(1 for u in test if res.get(u) is not None),
                  'untested': sum(1 for u in test if res.get(u) is None),
                  'fails': [{'knot': u, 'round': S.made[u], 'kind': S.kind[u], 'parents': list(S.parents[u])}
                            for u in test if res.get(u) is False],
                  'direct_compared': len(direct), 'disagree': sum(1 for u in direct if direct[u] != res.get(u))}
    # parity: the run up to its first closing birth
    c = gr.parity_closing_round
    if c is None:
        Np, ndp, drop = S.n_knots, S.n_distinctions, None
    else:
        Np = gr.n_knots[c]
        ndp = gr.n_dist[c]
        drop = Np - 1          # the closing birth is the round's only birth and the last knot of that round
    smp_p = kwr.sample_sorted(kwr.rng_for(key, lab, 'parity', 'knot-test'), range(S.n_start, Np), 200)
    test_p = list(range(S.n_start)) + sorted(smp_p)
    A = ktest.parity_ranks_graph(S, Np, ndp, test_p, drop_fresh_of=drop)
    B = ktest.parity_kernel_graph(S, Np, ndp, test_p, drop_fresh_of=drop)
    rec['parity'] = {'tested': len(test_p), 'structure_knots': Np, 'closing_round': c,
                     'fails': [{'knot': u, 'round': S.made[u], 'kind': S.kind[u], 'parents': list(S.parents[u])}
                               for u in test_p if not A[u]],
                     'disagree': sum(1 for u in test_p if A[u] != B[u])}
    rec['seconds'] = round(time.time() - t0, 2)
    return rec


def _init():
    kwr.cap_memory(6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    its = items()
    if a.limit:
        its = its[:a.limit]
    path = kwr.out_path('run3.jsonl.gz')
    done = {r['item'] for r in kwr.read_jsonl(path)}
    its = [x for x in its if x['item'] not in done]
    kwr.log('run 3: %d items' % len(its))
    W = kwr.JsonlWriter(path)
    t0 = time.time()
    with mp.Pool(a.procs, initializer=_init, maxtasksperchild=50) as pool:
        for k, rec in enumerate(pool.imap_unordered(run_item, its)):
            W.write(rec)
            if (k + 1) % 100 == 0 or k + 1 == len(its):
                kwr.log('run 3: %d/%d, %.0fs' % (k + 1, len(its), time.time() - t0))
    W.close()


if __name__ == '__main__':
    main()
