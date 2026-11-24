"""Run B4 under the ordinary law: Ring(n, 3), n = 5, 7, 8, 9, 10, 11; Ring(n, 3) with one loose distinction removed from
knot 0, and from every knot of even number, n = 5, 7, 9; Ring(n, 2), n = 5, 7.  R = 12 (14 for n = 5), cut off past
6,000 knots.  For every knot made in rounds 1 to R: its round r, parents p, fresh distinctions f and demand D; the table
of rounds by (p, f); on the rings with a leftover on every knot the formula r = f + 2p - 3 - 2e (deviations.md B7),
with e also recovered from the line of descent where the stretch is shorter than the ring.  Evidence for P6 and G
(ordinary-law checks).  Writes b4.json."""
import networkx as nx

from bref import E, log, ordinary_checks, resources, write

CAP = 6000


def ring_removed(n, removed):
    stars = E.ring_stars(n, 3)
    for i in removed:
        stars[i] = stars[i][:-1]        # drop one loose distinction (its last)
    return E.from_stars(stars)


def births_by_id(run):
    return {b['id']: b for rec in run.records for b in rec['births']}


def pf_table(run, last_round):
    S = run.S
    tab = {}
    for x in range(S.n_knots):
        r = S.made[x]
        if r < 1 or r > last_round:
            continue
        key = '%d,%d' % (len(S.parents[x]), len(S.fresh[x]))
        t = tab.setdefault(key, {'count': 0, 'min_round': r, 'max_round': r})
        t['count'] += 1
        t['min_round'] = min(t['min_round'], r)
        t['max_round'] = max(t['max_round'], r)
    for t in tab.values():
        t['spread'] = t['max_round'] - t['min_round']
    return dict(sorted(tab.items(), key=lambda kv: tuple(map(int, kv[0].split(',')))))


def lineage_check(run, n):
    """P6(a) on a ring with a leftover on every knot (deviations.md B7)."""
    S = run.S
    B = births_by_id(run)
    ros0 = run.rosters[0]
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for M in ros0.maxsets:
        G.add_edge(*sorted(M))
    cyc_of = {}
    for comp in nx.connected_components(G):
        for u in comp:
            cyc_of[u] = frozenset(comp)
    anc = [0] * S.n_knots      # bitmask of start-knot ancestors
    lo = [0] * S.n_knots       # bitmask of start knots whose round-1 offshoot is an ancestor or the knot itself
    for x in range(S.n_knots):
        if S.made[x] == 0:
            anc[x] = 1 << x
            continue
        a = l = 0
        for p in S.parents[x]:
            a |= anc[p]
            l |= lo[p]
        if S.made[x] == 1 and len(S.parents[x]) == 1 and S.parents[x][0] < n:
            l |= 1 << S.parents[x][0]
        anc[x], lo[x] = a, l
    rows = {'checked': 0, 'formula_ok': 0, 'formula_fail': [], 'e_formula_counts': {},
            'short_stretch': 0, 'lineage_e_equal': 0, 'lineage_fail': [], 'round_free_ok': 0, 'p_ok': 0,
            'D_ok': 0, 'not_a_path': 0, 'multi_cycle': 0}
    for x in range(S.n_knots):
        r = S.made[x]
        if r < 1:
            continue
        p, f = len(S.parents[x]), len(S.fresh[x])
        D = B[x]['D']
        rows['checked'] += 1
        v = f + 2 * p - r
        ok = v in (3, 5, 7)
        e_f = (v - 3) / 2
        rows['e_formula_counts'][str(e_f)] = rows['e_formula_counts'].get(str(e_f), 0) + 1
        if ok:
            rows['formula_ok'] += 1
        elif len(rows['formula_fail']) < 10:
            rows['formula_fail'].append({'id': x, 'r': r, 'p': p, 'f': f, 'D': D, 'f+2p-r': v})
        A = [i for i in range(n) if anc[x] >> i & 1]
        J = [i for i in range(n) if lo[x] >> i & 1]
        cycs = {cyc_of[i] for i in A}
        if len(cycs) != 1:
            rows['multi_cycle'] += 1
            continue
        cyc = next(iter(cycs))
        L, j = len(A), len(J)
        if L >= len(cyc):
            continue                      # stretch not shorter than the ring: e not recovered (B7)
        rows['short_stretch'] += 1
        H = G.subgraph(A)
        if not (nx.is_connected(H) and H.number_of_edges() == L - 1):
            rows['not_a_path'] += 1
            continue
        ends = [u for u in A if H.degree(u) <= 1]
        e_l = sum(1 for u in ends if not (lo[x] >> u & 1))
        if r == L + j - 1:
            rows['round_free_ok'] += 1
        if p == j + e_l:
            rows['p_ok'] += 1
        if D == L - j + 2:
            rows['D_ok'] += 1
        if ok and e_f == e_l:
            rows['lineage_e_equal'] += 1
        elif len(rows['lineage_fail']) < 10:
            rows['lineage_fail'].append({'id': x, 'r': r, 'p': p, 'f': f, 'D': D, 'L': L, 'j': j, 'ends': ends,
                                         'e_formula': e_f, 'e_lineage': e_l})
    rows['all_formula_ok'] = rows['formula_ok'] == rows['checked']
    rows['all_lineage_ok'] = (rows['lineage_e_equal'] == rows['short_stretch'] and rows['not_a_path'] == 0
                              and rows['multi_cycle'] == 0)
    return rows


def main():
    starts = []
    for n in (5, 7, 8, 9, 10, 11):
        starts.append(('Ring(%d,3)' % n, n, E.ring(n, 3), 'all', 14 if n == 5 else 12))
    for n in (5, 7, 9):
        starts.append(('Ring(%d,3)-knot0' % n, n, ring_removed(n, [0]), 'removed', 12))
        starts.append(('Ring(%d,3)-even' % n, n, ring_removed(n, list(range(0, n, 2))), 'removed', 12))
    for n in (5, 7):
        starts.append(('Ring(%d,2)' % n, n, E.ring(n, 2), 'none', 12))
    out = {'runs': {}}
    for name, n, S, leftovers, R in starts:
        par = E.parity_knot_test(S)
        run = E.Run(S, E.ORDINARY, R, knot_cap=CAP)
        last = run.rounds_done
        rec = {'n': n, 'leftovers': leftovers, 'R': R, 'rounds_done': last, 'cut_off': run.cut_off,
               'knots': run.S.n_knots, 'kind': run.kind(), 'start_parity_pass': par['all_pass'],
               'births': [r['n_births'] for r in run.records],
               'ordinary': ordinary_checks(run),
               'pf_table': pf_table(run, min(last, 12)),
               'pf_table_all_rounds': pf_table(run, last)}
        tab = rec['pf_table']
        rec['max_spread_by_round_12'] = max(t['spread'] for t in tab.values())
        rec['pf_with_spread_over_4'] = [k for k, t in tab.items() if t['spread'] > 4]
        if leftovers == 'all':
            rec['P6a'] = lineage_check(run, n)
        if leftovers == 'none':
            rec['all_p2_f2'] = list(rec['pf_table_all_rounds'].keys()) == ['2,2']
        out['runs'][name] = rec
        log(name, rec['kind'], 'rounds', last, 'knots', rec['knots'], 'cut' if run.cut_off else '',
            'max spread', rec['max_spread_by_round_12'],
            ('P6a formula %s lineage %s' % (rec['P6a']['all_formula_ok'], rec['P6a']['all_lineage_ok'])
             if 'P6a' in rec else ''))
    out['resources'] = resources()
    write('b4.json', out)


if __name__ == '__main__':
    main()
