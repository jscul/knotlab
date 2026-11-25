"""Part 5: P9 (PR part 5; R 35-38).  For each of the 194 not-all-equal types of FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C,
the stage counted from its source (one round), the pair table of weights of disagreement, and whether two types with one
table have different next birth counts, named and under one consistent renaming."""
from __future__ import annotations

import gzip
import itertools
import json
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr
from multiprocessing import Pool

import networkx as nx
from networkx.algorithms import isomorphism as iso

import tc

D = tc.REPO + '/artifacts/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C-E001_pair_births/'


def nae_ok(bits):
    return 0 < sum(bits) < len(bits)


def load_types():
    c = json.load(gzip.open(D + 'census_cases.json.gz'))['nae']
    con = [x for x in c if x['first_status'] == 'births']
    dis = json.load(open(D + 'disconnected.json'))['nae']['cases']
    return [('connected', i, x) for i, x in enumerate(con)] + [('disconnected', i, x) for i, x in enumerate(dis)]


def tables_of(case):
    """Exact pair tables under counting from the start (one round from the source) and counting from the finish,
    by elimination over the source states (R 35)."""
    sw = case['source_width']
    src = case['source_rows']
    rows = case['stage_rows']
    assert rows[:len(src)] == src, 'stage rows begin with the source rows'
    births = rows[len(src):]
    W = case['stage_width']
    # source states
    A0 = [o for o in itertools.product((0, 1), repeat=sw) if all(nae_ok([o[p] for p in r]) for r in src)]
    # each birth: old places, fresh places
    B = []
    for r in births:
        old = [p for p in r if p < sw]
        fresh = [p for p in r if p >= sw]
        B.append((old, fresh))
    owner = {}
    for i, (old, fresh) in enumerate(B):
        for p in fresh:
            assert p not in owner
            owner[p] = i
    assert sorted(owner) == list(range(sw, W)), 'every fresh name belongs to one birth'
    pairs = list(itertools.combinations(range(W), 2))
    start_t = defaultdict(Fr)
    fin_t = defaultdict(int)
    total = 0
    n0 = len(A0)
    for o in A0:
        # per birth: completions, P(fresh=1), P(pair differ within birth); counts for the finish
        comp = []
        for old, fresh in B:
            ov = [o[p] for p in old]
            cs = [z for z in itertools.product((0, 1), repeat=len(fresh)) if nae_ok(ov + list(z))]
            comp.append(cs)
        c = [len(x) for x in comp]
        assert all(x >= 1 for x in c)
        prod = 1
        for x in c:
            prod *= x
        total += prod
        w0 = Fr(1, n0)

        def val(p):
            """(kind, data): old value, or (birth, index)."""
            return p
        # probabilities given o under counting from the start (uniform completions per birth, independent)
        p1 = {}
        for i, (old, fresh) in enumerate(B):
            for k, p in enumerate(fresh):
                p1[p] = Fr(sum(z[k] for z in comp[i]), c[i])
        for (a, b) in pairs:
            if a < sw and b < sw:
                d = Fr(int(o[a] != o[b]))
                dc = prod * int(o[a] != o[b])
            elif a < sw:
                i = owner[b]
                k = B[i][1].index(b)
                n_d = sum(1 for z in comp[i] if z[k] != o[a])
                d = Fr(n_d, c[i])
                dc = (prod // c[i]) * n_d
            else:
                i, j = owner[a], owner[b]
                if i == j:
                    ka, kb = B[i][1].index(a), B[i][1].index(b)
                    n_d = sum(1 for z in comp[i] if z[ka] != z[kb])
                    d = Fr(n_d, c[i])
                    dc = (prod // c[i]) * n_d
                else:
                    ka, kb = B[i][1].index(a), B[j][1].index(b)
                    n1a = sum(z[ka] for z in comp[i])
                    n1b = sum(z[kb] for z in comp[j])
                    pa, pb = Fr(n1a, c[i]), Fr(n1b, c[j])
                    d = pa * (1 - pb) + (1 - pa) * pb
                    n_d = n1a * (c[j] - n1b) + (c[i] - n1a) * n1b
                    dc = (prod // (c[i] * c[j])) * n_d
            start_t[(a, b)] += w0 * d
            fin_t[(a, b)] += dc
    return {'start': [start_t[p] for p in pairs], 'finish counts': [fin_t[p] for p in pairs], 'total': total,
            'pairs': pairs, 'source states': n0}


def brute_start_table(case):
    """Gate: the same table by the engine's history enumeration (small widths only)."""
    sw = case['source_width']
    src = case['source_rows']
    births = case['stage_rows'][len(src):]
    stages = [[('nae', tuple('d%d' % p for p in r)) for r in src], [('nae', tuple('d%d' % p for p in r)) for r in births]]
    H = tc.History(stages)
    Wt, _ = tc.counting(H, 0)
    dct = tc.as_dict(H, Wt)
    W = case['stage_width']
    out = []
    for a, b in itertools.combinations(range(W), 2):
        ia, ib = H.idx['d%d' % a], H.idx['d%d' % b]
        out.append(sum((x for w, x in dct.items() if ((w >> ia) & 1) != ((w >> ib) & 1)), Fr(0)))
    return out


def one(job):
    tc.cap_memory()
    scope, i, case = job
    t = time.time()
    T = tables_of(case)
    gate = {'finish pair counts = the archive’s pair_counts': T['finish counts'] == case['pair_counts'],
            'finish total = the archive’s total_words': T['total'] == case['total_words']}
    if case['stage_width'] <= 20:
        gate['start table = history enumeration'] = brute_start_table(case) == T['start']
    return {'scope': scope, 'index': i, 'source_rows': case['source_rows'], 'stage_width': case['stage_width'],
            'first_birth_count': case['first_birth_count'], 'next_status': case['next_status'],
            'next_birth_count': case['next_birth_count'], 'start table': [tc.fstr(x) for x in T['start']],
            'source states': T['source states'], 'gate': gate, 'wall_s': round(time.time() - t, 3)}


def renaming_equal(r1, r2):
    W = r1['stage_width']
    if W != r2['stage_width']:
        return False
    pairs = list(itertools.combinations(range(W), 2))

    def G(r):
        g = nx.Graph()
        g.add_nodes_from(range(W))
        for (a, b), x in zip(pairs, r['start table']):
            g.add_edge(a, b, w=x)
        return g
    gm = iso.GraphMatcher(G(r1), G(r2), edge_match=lambda e1, e2: e1['w'] == e2['w'])
    return gm.is_isomorphic()


def invariant(r):
    W = r['stage_width']
    pairs = list(itertools.combinations(range(W), 2))
    per = defaultdict(list)
    for (a, b), x in zip(pairs, r['start table']):
        per[a].append(x)
        per[b].append(x)
    return (W, tuple(sorted(r['start table'], key=Fr)), tuple(sorted(tuple(sorted(v, key=Fr)) for v in per.values())))


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    jobs = load_types()
    with Pool(nproc) as pool:
        rows = list(pool.imap(one, jobs, chunksize=4))
    gate_ok = all(all(v for v in r['gate'].values()) for r in rows)
    # named: identical tables over the archive's stage names
    named = defaultdict(list)
    for k, r in enumerate(rows):
        named[(r['stage_width'], tuple(r['start table']))].append(k)
    named_groups = [g for g in named.values() if len(g) > 1]
    named_conflicts = [g for g in named_groups if len({rows[k]['next_birth_count'] for k in g}) > 1
                       or len({rows[k]['next_status'] for k in g}) > 1]
    # under one consistent renaming
    inv = defaultdict(list)
    for k, r in enumerate(rows):
        inv[invariant(r)].append(k)
    ren_groups = []
    for g in inv.values():
        left = list(g)
        while left:
            k = left.pop(0)
            grp = [k] + [m for m in left if renaming_equal(rows[k], rows[m])]
            left = [m for m in left if m not in grp]
            if len(grp) > 1:
                ren_groups.append(grp)
    ren_conflicts = [g for g in ren_groups if len({rows[k]['next_birth_count'] for k in g}) > 1
                     or len({rows[k]['next_status'] for k in g}) > 1]
    p9 = not named_conflicts and not ren_conflicts
    out = {'part': 5, 'types': len(rows), 'connected': sum(1 for r in rows if r['scope'] == 'connected'),
           'disconnected': sum(1 for r in rows if r['scope'] == 'disconnected'), 'gates pass': gate_ok,
           'gate failures': [(r['scope'], r['index'], r['gate']) for r in rows if not all(r['gate'].values())],
           'named: groups of types sharing one table': [[(rows[k]['scope'], rows[k]['index'], rows[k]['next_birth_count'])
                                                        for k in g] for g in named_groups],
           'under renaming: groups of types sharing one table': [[(rows[k]['scope'], rows[k]['index'],
                                                                   rows[k]['next_birth_count']) for k in g]
                                                                 for g in ren_groups],
           'named conflicts': named_conflicts, 'renaming conflicts': ren_conflicts,
           'P9 holds (the tables decide the next birth count)': p9,
           'distinct tables under renaming': len(rows) - sum(len(g) - 1 for g in ren_groups),
           'rows': rows, 'wall_s': round(time.time() - T0, 1), 'processes': nproc,
           'largest wall per type (s)': max(r['wall_s'] for r in rows)}
    tc.dump('part5_p9.json', out)
    print({k: v for k, v in out.items() if k != 'rows'})


if __name__ == '__main__':
    main()
