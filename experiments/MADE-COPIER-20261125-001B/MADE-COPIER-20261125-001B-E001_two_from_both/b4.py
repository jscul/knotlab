"""Run B4, the renaming check (PB1): for the 18 starts of starts_b.json "renaming starts" and each of their ten renamed
starts, the structure after every round against the renamed start's, compared exactly: a renaming is built round by
round as DB 7 states it (start knots and the distinctions shared or barred at the start by an isomorphism of the two
starts; new knots to births of the same kind whose parents correspond; each birth's input from a parent to the input
from that parent's image, which permutes that parent's usable loose distinctions; fresh distinctions in order), and is
then verified knot by knot and distinction by distinction.  Where it cannot be built, the two structures are compared
by invariants (a difference proves them different) and otherwise by an exact isomorphism search.

usage: python -B b4.py [--procs 4]
"""
import argparse
import os
import sys
import time
import traceback
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P
nx = mcb.nx
RS = mcb.STB['renaming starts']


def incidence(S):
    G = nx.Graph()
    for u in range(S.n_knots):
        if u in S.removed:
            continue
        G.add_node(('k', u), c='k%d|%s' % (S.made[u], S.kind[u]))
    for d in range(S.n_distinctions):
        if S.holders[d]:
            G.add_node(('d', d), c='d%d' % int(bool(S.barred[d])))
            for u in S.holders[d]:
                G.add_edge(('d', d), ('k', u))
    return G


def start_iso(S1, S2):
    G1, G2 = incidence(S1), incidence(S2)
    gm = nx.algorithms.isomorphism.GraphMatcher(G1, G2, node_match=lambda a, b: a['c'] == b['c'])
    if not gm.is_isomorphic():
        return None
    m = gm.mapping
    kmap = {a[1]: b[1] for a, b in m.items() if a[0] == 'k'}
    dmap = {a[1]: b[1] for a, b in m.items() if a[0] == 'd'}
    return kmap, dmap


def invariants(S):
    return (S.n_knots - len(S.removed), sum(1 for d in range(S.n_distinctions) if S.holders[d]),
            tuple(sorted(Counter((S.made[u], S.kind[u], len(S.places[u]),
                                  sum(1 for d in S.places[u] if len(S.holders[d]) == 1),
                                  sum(1 for d in S.places[u] if S.barred[d]))
                                 for u in range(S.n_knots) if u not in S.removed).items())),
            tuple(sorted(Counter((len(S.holders[d]), bool(S.barred[d])) for d in range(S.n_distinctions)
                                 if S.holders[d]).items())))


def verify(S1, S2, kmap, dmap):
    k1 = [u for u in range(S1.n_knots) if u not in S1.removed]
    k2 = {u for u in range(S2.n_knots) if u not in S2.removed}
    if len(k1) != len(k2) or set(kmap.get(u) for u in k1) != k2:
        return False
    d1 = [d for d in range(S1.n_distinctions) if S1.holders[d]]
    d2 = {d for d in range(S2.n_distinctions) if S2.holders[d]}
    if len(d1) != len(d2) or set(dmap.get(d) for d in d1) != d2:
        return False
    for u in k1:
        v = kmap[u]
        if S1.made[u] != S2.made[v] or S1.kind[u] != S2.kind[v]:
            return False
        if sorted(dmap[d] for d in S1.places[u]) != sorted(S2.places[v]):
            return False
    for d in d1:
        if bool(S1.barred[d]) != bool(S2.barred[dmap[d]]):
            return False
    return True


class Renaming:
    """sigma_t, extended round by round (DB 7)."""

    def __init__(self, kmap, dmap):
        self.k = dict(kmap)
        self.d = dict(dmap)
        self.inv = {v: u for u, v in self.d.items()}

    def set_d(self, a, b):
        old = self.d.get(a)
        e = self.inv.get(b)
        if old == b:
            return
        if e is not None and old is not None:
            self.d[e] = old
            self.inv[old] = e
        self.d[a] = b
        self.inv[b] = a

    def extend(self, Sb1, rec1, Sb2, rec2):
        pool = defaultdict(list)
        for b in rec2['births']:
            key = (b['kind'], frozenset(b['parents']), b['f'], b['usable'])
            pool[key].append(b)
        for b in rec1['births']:
            img = frozenset(self.k[p] for p in b['parents'])
            key = (b['kind'], img, b['f'], b['usable'])
            if not pool.get(key):
                return False
            b2 = pool[key].pop(0)
            self.k[b['id']] = b2['id']
            # each input from a parent p goes to the input from p's image
            for d in b['inputs']:
                ps = [p for p in Sb1.holders[d] if p in b['parents']]
                if len(ps) != 1:
                    return False
                p2 = self.k[ps[0]]
                cand = [x for x in b2['inputs'] if p2 in Sb2.holders[x]]
                if len(cand) != 1:
                    return False
                self.set_d(d, cand[0])
            for a, c in zip(b['fresh'], b2['fresh']):
                self.d[a] = c
                self.inv[c] = a
        return all(not v for v in pool.values())


class _Timeout(Exception):
    pass


def exact_iso(G1, G2, seconds=60):
    import signal

    def h(*a):
        raise _Timeout()
    old = signal.signal(signal.SIGALRM, h)
    signal.alarm(seconds)
    try:
        return nx.vf2pp_is_isomorphic(G1, G2, node_label='c')
    except _Timeout:
        return None
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def compare_runs(A1, A2, search_seconds=10):
    """Round by round: 'renaming' (built and verified), 'differs' (invariants or the Weisfeiler-Lehman hash prove it),
    'same by search', 'not refuted'.  A run proven different at some round is not searched further (deviations 28)."""
    out = {'rounds': [A1.rounds_done, A2.rounds_done], 'per_round': []}
    si = start_iso(A1.snap[0], A2.snap[0])
    if si is None:
        out['start'] = 'not isomorphic'
        return out
    sig = Renaming(*si)
    built = True
    pending = []
    n = min(A1.rounds_done, A2.rounds_done)
    for t in range(0, n + 1):
        S1, S2 = A1.snap[t], A2.snap[t]
        if t >= 1 and built:
            built = sig.extend(A1.snap[t - 1], A1.records[t - 1], A2.snap[t - 1], A2.records[t - 1])
        if built and verify(S1, S2, sig.k, sig.d):
            out['per_round'].append('renaming')
            continue
        built = False
        if invariants(S1) != invariants(S2):
            out['per_round'].append('differs')
            continue
        G1, G2 = incidence(S1), incidence(S2)
        if nx.weisfeiler_lehman_graph_hash(G1, node_attr='c') != nx.weisfeiler_lehman_graph_hash(G2, node_attr='c'):
            out['per_round'].append('differs')
            continue
        out['per_round'].append('undecided')
        pending.append(t)
    if A1.rounds_done != A2.rounds_done:
        out['per_round'].append('differs (rounds reached)')
    if search_seconds and not any(x.startswith('differs') for x in out['per_round']):
        for t in pending:
            G1, G2 = incidence(A1.snap[t]), incidence(A2.snap[t])
            same = exact_iso(G1, G2, search_seconds)
            out['per_round'][t] = 'same by search' if same is True else 'differs' if same is False else 'not refuted'
    return out


def do_job(job):
    cb.cap_memory(job.get('mem', 7))
    t0 = time.time()
    out = {'job': job, 'rows': []}
    try:
        kl = job['knot_law']
        if job['take']:
            law = mc.make_law(job['base'], job['take'], job['choice'], kl)
        else:
            law = mcb.law1(job['base'], kl, job['release'])
        out['law'] = law.name()
        for name, r in RS.items():
            S = pm.from_stars(r['stars'])
            A1 = mcb.grow(S, law, job['base'])
            for rn in r['renamed']:
                S2 = pm.from_stars(rn['stars'], reverse_names=rn['names'].startswith('reversed'))
                A2 = mcb.grow(S2, law, job['base'])
                # deviations 28: under MET (the control) only a proof of difference is sought; with no taking rule a
                # round where the renaming cannot be built is searched for 10 seconds
                c = compare_runs(A1, A2, search_seconds=0 if job['take'] else 10)
                pr = c['per_round']
                verdict = ('a renaming at every round' if pr and all(x == 'renaming' for x in pr) else
                           'the same at every round (some by search)' if pr and all(
                               x in ('renaming', 'same by search') for x in pr) else
                           'differs' if any(x.startswith('differs') for x in pr) else
                           'not proven different' if job['take'] else 'not refuted')
                if verdict == 'differs':
                    pr = [x for x in pr if x != 'undecided']
                out['rows'].append({'start': name, 'renaming': rn['renaming'], 'verdict': verdict,
                                    'rounds compared': len(pr), 'first difference': next(
                                        (i for i, x in enumerate(pr) if x.startswith('differs')), None),
                                    'by search': sum(1 for x in pr if x == 'same by search'),
                                    'knot fails (original, renamed)': [mc.knot_tests_A(A1)['n_fails'],
                                                                       mc.knot_tests_A(A2)['n_fails']]
                                    if job.get('knots') else None})
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def jobs():
    js = []
    for base in mcb.BASES6:
        for rel in ('RELEASE', 'HOLD'):
            for kl in ('nae', 'parity'):
                js.append({'base': base, 'take': None, 'choice': None, 'release': rel, 'knot_law': kl})
    for base in mcb.BASES6:
        for ch in ('OLDEST', 'NEWEST'):
            for kl in ('nae', 'parity'):
                js.append({'base': base, 'take': 'MET', 'choice': ch, 'release': 'RELEASE', 'knot_law': kl})
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    args = ap.parse_args()
    js = jobs()
    cb.log('run B4:', len(js), 'jobs')
    out = cb.JsonLines('b4.jsonl.gz')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        for f in as_completed([ex.submit(do_job, j) for j in js]):
            r = f.result()
            out.write(r)
            cb.log(r.get('law'), r.get('seconds'), r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
