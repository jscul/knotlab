"""The paired test (definitions section 5) and the per-run readings of runs 1, 3, 5, 6 and 7.

A run A is grown; for every registered pair (X, Y) after round s: B(i) (Y barred), B(ii) (Y removed, where defined),
X's trace in each and its first differing round, the way, the demand line, the masked runs M and M', the verdict with
the class of the linking knots, the marks "one part again" and "a joint birth".  Readings are in deviations.md.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import networkx as nx

import knots as K
import pm


# ---------------------------------------------------------------------------------------------- descent bookkeeping
def side_of(S, X, s):
    """X and its descendants (D 4.2): X, and every knot made after round s with a parent among them."""
    out = set(X)
    for x in range(S.n_knots):
        if S.made[x] > s and S.kind[x] != 'placed' and any(p in out for p in S.parents[x]):
            out.add(x)
    return out


def anc_or_self(S, u):
    a = S.ancestors(u)
    a.add(u)
    return a


# ---------------------------------------------------------------------------------------------------------- rosters
class RunView:
    """Run A (or any run) with its rosters per round, cached."""

    def __init__(self, run):
        self.run = run
        self.law = run.law
        self._ros = {}

    def roster(self, t):
        R = self._ros.get(t)
        if R is None:
            R = pm.roster_of(self.run.snap[t], self.law)
            self._ros[t] = R
        return R

    @property
    def R(self):
        return self.run.rounds_done


def two_knot_parts(R):
    """N(t): parts, past their start, of two members with h = 2, k = 0 each, lying in one met set (COPYING-PARTS)."""
    n = 0
    for P in R.parts:
        if len(P) != 2:
            continue
        a, b = P
        if (R.h[a], R.k[a], R.h[b], R.k[b]) != (2, 0, 2, 0):
            continue
        if a in R.meets_member or b in R.meets_member:
            continue
        if any(a in M and b in M for M in R.maxsets):
            n += 1
    return n


def roster_graph(R, members):
    ms = set(members)
    G = nx.Graph()
    for u in members:
        G.add_node(('m', u), c='m%d,%d' % (R.h[u], R.k[u]))
    for i, M in enumerate(R.maxsets):
        if next(iter(M)) in ms:
            G.add_node(('s', i), c='s')
            for u in M:
                G.add_edge(('s', i), ('m', u))
    return G


def same_parts(R1, m1, R2, m2):
    """SD line 29-30: a one-to-one renaming of members carrying h, k and the family of maximal met sets."""
    G1, G2 = roster_graph(R1, m1), roster_graph(R2, m2)
    if G1.number_of_nodes() != G2.number_of_nodes() or G1.number_of_edges() != G2.number_of_edges():
        return False
    if nx.weisfeiler_lehman_graph_hash(G1, node_attr='c') != nx.weisfeiler_lehman_graph_hash(G2, node_attr='c'):
        return False
    return nx.is_isomorphic(G1, G2, node_match=lambda a, b: a['c'] == b['c'])


def ring_returns(view):
    """The ring's own sameness test without "past its start": rounds t >= 1 at which some part is the same as the
    start's whole roster (R 20)."""
    R0 = view.roster(0)
    out = []
    for t in range(1, view.R + 1):
        Rt = view.roster(t)
        for P in Rt.parts:
            if len(P) == len(R0.members) and same_parts(R0, R0.members, Rt, P):
                out.append(t)
                break
    return out


def round_stats(view):
    rows = []
    for t in range(view.R + 1):
        Rt = view.roster(t)
        S = view.run.snap[t]
        cls = pm.roster_classes(Rt)
        mh = max((len(h) for h in S.holders), default=0)
        row = {'t': t, 'members': len(Rt.members), 'parts': len(Rt.parts), 'classes': len(set(cls)),
               'max_holders': mh, 'knots': S.n_knots - len(S.removed), 'N2': two_knot_parts(Rt),
               'part_sizes': sorted(len(P) for P in Rt.parts)}
        if t >= 1:
            rec = view.run.records[t - 1]
            row.update({'births': rec['n_births'], 'joins': rec['n_joins'], 'offshoots': rec['n_offshoots'],
                        'taking_births': rec['n_taking'], 'takes': rec['n_takes'], 'stalled': rec['stalled'],
                        'residual_stall': rec['residual_stall'], 'jammed': rec['jammed'], 'stopped': rec['stopped'],
                        'closing': rec['closing'], 'short': len(rec['short'])})
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------------- all-pairs checks (P1, P6, P16)
def all_pairs_checks(view):
    """For every round s and every later round t: a part after round t holding descendants of two classes of round s
    (wholly apart parts one part again), a birth with parents descended from two classes (a joint birth), and parts that
    come apart (descendants of one part of round s in two or more parts of round t)."""
    run = view.run
    out = {'one_part_again': [], 'joint_birth': [], 'came_apart': 0, 'came_apart_list': []}
    for s in range(0, view.R):
        Rs = view.roster(s)
        cls = pm.roster_classes(Rs)
        labc = {u: frozenset([cls[Rs.part_of[u]]]) for u in Rs.members}
        labp = {u: frozenset([Rs.part_of[u]]) for u in Rs.members}
        seen_apart = set()
        first_opa = first_joint = None
        for t in range(s + 1, view.R + 1):
            rec = run.records[t - 1]
            for b in rec['births']:
                pc = frozenset()
                pp = frozenset()
                for p in b['parents']:
                    pc |= labc.get(p, frozenset())
                    pp |= labp.get(p, frozenset())
                if pc:
                    labc[b['id']] = pc
                    labp[b['id']] = pp
                if len(pc) >= 2 and first_joint is None:
                    first_joint = (t, b['id'], sorted(pc))
            Rt = view.roster(t)
            where = defaultdict(set)
            for j, P in enumerate(Rt.parts):
                L = frozenset()
                for x in P:
                    L |= labc.get(x, frozenset())
                    for y in labp.get(x, ()):
                        where[y].add(j)
                if len(L) >= 2 and first_opa is None:
                    first_opa = (t, j, sorted(L))
            for y, js in where.items():
                if len(js) >= 2 and y not in seen_apart:
                    seen_apart.add(y)
                    out['came_apart_list'].append({'s': s, 'part': list(Rs.parts[y]), 't': t})
        if first_opa:
            out['one_part_again'].append({'s': s, 't': first_opa[0], 'classes': first_opa[2]})
        if first_joint:
            out['joint_birth'].append({'s': s, 't': first_joint[0], 'birth': first_joint[1],
                                       'classes': first_joint[2]})
        out['came_apart'] += len(seen_apart)
    out['came_apart_list'] = out['came_apart_list'][:50]
    return out


# ----------------------------------------------------------------------------------------------------- pair choice
def came_apart(view, s, X, Y):
    """D 5.8: whether X and Y have a common part in their ancestry (R 15)."""
    S = view.run.snap[s]
    AX = set()
    for u in X:
        AX |= anc_or_self(S, u)
    AY = set()
    for u in Y:
        AY |= anc_or_self(S, u)
    for r in range(0, s):
        Rr = view.roster(r)
        px = {Rr.part_of[z] for z in AX if z in Rr.part_of}
        py = {Rr.part_of[z] for z in AY if z in Rr.part_of}
        if px & py:
            return True
    return False


def select_pairs(view, every_pair=False, two_knot=False):
    """D 5.8.  every_pair: the HOLD arm (pairs not wholly apart taken too); two_knot: also the start's own pair at s=0."""
    out = []
    rng = range(1, min(6, view.R - 1) + 1)
    rounds = ([0] if two_knot else []) + list(rng)
    for s in rounds:
        if s >= view.R:
            continue
        Rs = view.roster(s)
        parts = Rs.parts[:8]
        cls = pm.roster_classes(Rs)
        n = 0
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                wa = cls[i] != cls[j]
                if s == 0:
                    if not two_knot:
                        continue
                elif not wa and not every_pair:
                    continue
                if n >= 4:
                    break
                out.append({'s': s, 'i': i, 'j': j, 'X': list(parts[i]), 'Y': list(parts[j]), 'wholly_apart': wa})
                n += 1
            if n >= 4:
                break
    for p in out:
        p['came_apart'] = came_apart(view, p['s'], p['X'], p['Y'])
    return out


# ------------------------------------------------------------------------------------------------------- the trace
def trace(run, X, s, upto=None):
    """D 5.2.  Returns per round t = s+1..upto: {'births': [...], 'members': [...], 'metsets': [...]}, and the demand
    line and the steps used for the way."""
    upto = run.rounds_done if upto is None else upto
    SE = run.snap[upto]
    Ss = run.snap[s]
    nd_s = Ss.n_distinctions
    xd = side_of(SE, X, s)
    newk = sorted(k for k in xd if SE.made[k] > s or (k >= Ss.n_knots))
    kmap = {k: ('n', i) for i, k in enumerate(newk)}
    fr = sorted(d for d in range(nd_s, SE.n_distinctions) if SE.holders[d] and SE.holders[d][0] in kmap)
    fmap = {d: ('f', i) for i, d in enumerate(fr)}

    def kn(k):
        if k < Ss.n_knots and SE.kind[k] != 'placed':
            return ('k', k)
        return kmap.get(k, ('x',))

    def dn(d):
        if d < nd_s:
            return ('d', d)
        return fmap.get(d, ('y',))
    rounds = []
    for t in range(s + 1, upto + 1):
        rec = run.records[t - 1]
        S = run.snap[t]
        births, dem, steps_groups, steps_flags, steps_takes, steps_fresh = [], [], [], [], [], []
        for b in rec['births']:
            if all(p in xd for p in b['parents']):
                nm = kn(b['id'])
                births.append((nm, b['kind'], tuple(kn(p) for p in b['parents']),
                               tuple(sorted(dn(d) for d in b['inputs'])),
                               tuple(sorted(dn(d) for d in b['shared_at_start'])), b['f'], b['usable'], b['barred']))
                dem.append((nm, b['D']))
                steps_flags.append((nm, b['implied']))
                steps_takes.append((nm, b['kind'], tuple(kn(p) for p in b['parents']),
                                    tuple(sorted(dn(d) for d in b['inputs']))))
                steps_fresh.append((nm, b['f'], b['usable'], b['barred']))
        cancelled = {tuple(g) for g in rec['cancelled']}
        shortset = set(rec['short'])
        for g in rec['groups']:
            if any(u in xd for u in g):
                # the group, whether it is kept or cancelled, and which of its members are short (deviations 39)
                steps_groups.append((tuple(sorted(kn(u) for u in g)), tuple(g) in cancelled,
                                     tuple(sorted((kn(u), u in shortset) for u in g))))
        owe = tuple(sorted((kn(u), c) for u, c in rec['owe'].items() if u in xd))
        mem = []
        for u in sorted(xd):
            if u in S.removed or u >= S.n_knots:
                continue
            h, k = S.hk(u)
            if h > 0:
                mem.append((kn(u), h, k))
        raw = defaultdict(set)
        live = {m for m in xd if m < S.n_knots and m not in S.removed and S.hk(m)[0] > 0}
        for u in live:
            for d in S.places[u]:
                for w in S.holders[d]:
                    if w != u:
                        raw[w].add(u)
        sets = {frozenset(v) for v in raw.values() if len(v) >= 2}
        maxi = [M for M in sets if not any(M < O for O in sets)]
        ms = sorted(tuple(sorted(kn(u) for u in M)) for M in maxi)
        rounds.append({'t': t, 'births': births, 'members': sorted(mem), 'metsets': ms,
                       'demand': dem,
                       'way': {'groups': (sorted(steps_groups), owe),
                               'trigger': (bool(rec['stalled']), bool(rec['residual_stall']), tuple(steps_flags)),
                               'takes': tuple(steps_takes), 'fresh': tuple(steps_fresh)}})
    return rounds


def course_key(r):
    return (r['births'], r['members'], r['metsets'])


def first_difference(tr1, tr2):
    """First round at which the courses differ (compared through the last round both reached), the way, and the first
    round at which the demand differs."""
    n = min(len(tr1), len(tr2))
    diff = None
    way = None
    for i in range(n):
        if course_key(tr1[i]) != course_key(tr2[i]):
            diff = tr1[i]['t']
            w1, w2 = tr1[i]['way'], tr2[i]['way']
            if w1['groups'] != w2['groups']:
                way = 'a group or owing'
            elif w1['trigger'] != w2['trigger']:
                way = 'a round-wide trigger'
            elif w1['takes'] != w2['takes']:
                way = 'a take'
            elif w1['fresh'] != w2['fresh']:
                way = 'fresh'
            else:
                way = 'met sets after the round'
            break
    dem = None
    for i in range(n):
        if tr1[i]['demand'] != tr2[i]['demand']:
            dem = tr1[i]['t']
            break
    return diff, way, dem, n


def first_appearance(tr):
    """Rename every knot and distinction of a trace by first appearance (D 5.3, fourth mark)."""
    km, dm = {}, {}

    def ren(x):
        if isinstance(x, tuple) and len(x) >= 1 and x[0] in ('k', 'n'):
            if x not in km:
                km[x] = ('K', len(km))
            return km[x]
        if isinstance(x, tuple) and len(x) >= 1 and x[0] in ('d', 'f'):
            if x not in dm:
                dm[x] = ('D', len(dm))
            return dm[x]
        if isinstance(x, tuple):
            return tuple(ren(y) for y in x)
        if isinstance(x, list):
            return [ren(y) for y in x]
        return x
    out = []
    for r in tr:
        out.append({'births': ren(r['births']), 'members': ren(r['members']), 'metsets': ren(r['metsets'])})
    # met sets and members as sets after renaming
    for r in out:
        r['members'] = sorted(r['members'])
        r['metsets'] = sorted(tuple(sorted(M)) for M in r['metsets'])
    return out


# ------------------------------------------------------------------------------------------------ comparison runs
def run_from(view, s, S_mod, law=None, ctx=None):
    A = view.run
    law = law or A.law
    prefix_snaps = A.snap[:s]
    prefix_recs = A.records[:s]
    r = pm.Run.__new__(pm.Run)
    pm.Run.__init__(r, S_mod, law, rounds=A.rounds_asked, knot_bound=A.knot_bound, ctx=ctx,
                    records=prefix_recs, snapshots=prefix_snaps)
    return r


def bar_part(S, Y):
    T = S.copy()
    for y in Y:
        for d in T.usable(y):
            T.barred[d] = True
    return T


def remove_part(S, Y, s):
    """B(ii) (D 5.1), or None when it is not defined."""
    Yset = set(Y)
    nd0 = None
    fresh, taken = {}, {}
    for y in Y:
        if S.kind[y] == 'start':
            fr = [d for d in S.places[y] if len(S.holders[d]) == 1]
            tk = [d for d in S.places[y] if len(S.holders[d]) >= 2]
        else:
            fr = [d for d in S.places[y] if S.holders[d][0] == y]
            tk = [d for d in S.places[y] if S.holders[d][0] != y]
        fresh[y], taken[y] = fr, tk
        for d in fr:
            if any(w not in Yset for w in S.holders[d]):
                return None
        for d in tk:
            if len(S.holders[d]) != 2:
                return None
    T = S.copy()
    for y in Y:
        for d in T.places[y]:
            T.holders[d].remove(y)
        for d in taken[y]:
            assert len(T.holders[d]) == 1
            T.barred[d] = True
        T.places[y] = []
        T.removed.add(y)
        T.cand.discard(y)
    T.span = pm.build_span(T)
    return T


class SideTracker:
    """Keeps X and its descendants up to date during a run (for the control "the choice is necessary")."""

    def __init__(self, X):
        self.xd = set(X)

    def on_round(self, run, S, rec):
        for b in rec['births']:
            if any(p in self.xd for p in b['parents']):
                self.xd.add(b['id'])


def masked_run(view, s, X, Y, mode):
    A = view.run
    S = A.snap[s]
    xd = side_of(S, X, s)
    yd = side_of(S, Y, s)
    mask = pm.Mask(mode, xd, yd)
    return run_from(view, s, S, ctx={'mask': mask})


# ------------------------------------------------------------------------------------------------------ the verdict
def linking(view, t, X, Y, s):
    """At round t of run A: whether X's and Y's descendants are connected using only met sets with a made common knot,
    only with a start common knot; the linking common knots and their class (R 17)."""
    A = view.run
    S = A.snap[t]
    Rt = view.roster(t)
    xd = side_of(S, X, s)
    yd = side_of(S, Y, s)
    xs = [u for u in Rt.members if u in xd]
    ys = [u for u in Rt.members if u in yd]
    both = set(xs) & set(ys)
    G_made, G_start, G_any = nx.Graph(), nx.Graph(), nx.Graph()
    for G in (G_made, G_start, G_any):
        G.add_nodes_from(Rt.members)
    for M, com in zip(Rt.maxsets, Rt.commons):
        # every met set (not only maximal) whose common knots are of one kind: recompute below from raw met sets
        pass
    # raw met sets with their common knots
    sc, _, _ = pm.met_sets(S, Rt.members)
    edges_by = defaultdict(set)
    for M, com in sc.items():
        L = sorted(M)
        made = any(S.made[w] > 0 for w in com)
        start = any(S.made[w] == 0 for w in com)
        for i, a in enumerate(L):
            for b in L[i + 1:]:
                G_any.add_edge(a, b)
                if made:
                    G_made.add_edge(a, b)
                if start:
                    G_start.add_edge(a, b)
                edges_by[(a, b)].update(com)

    def connected(G):
        if both:
            return True
        cx = set()
        for x in xs:
            cx |= nx.node_connected_component(G, x)
        return any(y in cx for y in ys)
    made_c = connected(G_made)
    start_c = connected(G_start)
    # linking knots: common knots of met sets holding an X-side and a Y-side member; else along a shortest path
    links = set()
    for M, com in sc.items():
        if any(u in xd for u in M) and any(u in yd for u in M):
            links.update(com)
    path_used = False
    if not links and xs and ys:
        H = G_any.copy()
        H.add_node('SX')
        H.add_node('SY')
        for x in xs:
            H.add_edge('SX', x)
        for y in ys:
            H.add_edge('SY', y)
        try:
            p = nx.shortest_path(H, 'SX', 'SY')
            path_used = True
            for a, b in zip(p[1:-2], p[2:-1]):
                e = (a, b) if a < b else (b, a)
                links.update(edges_by.get(e, ()))
        except nx.NetworkXNoPath:
            pass
    classes = {}
    for w in sorted(links):
        Ms = [M for M, com in sc.items() if w in com]
        anc_ok = False
        for M in Ms:
            us = [u for u in M if u in xd]
            vs = [v for v in M if v in yd]
            for u in us:
                for v in vs:
                    if w in S.ancestors(u) and w in S.ancestors(v) and not (w in S.parents[u] and w in S.parents[v]):
                        anc_ok = True
        if anc_ok:
            classes[w] = 'an ancestral common knot' + (' (a start knot)' if S.made[w] == 0 else ' (made)')
        elif S.made[w] > 0:
            classes[w] = 'a knot made by the growth that is no ancestor of both'
        else:
            classes[w] = 'a start knot that is no recorded ancestor of both'
    return {'made_connected': made_c, 'start_connected': start_c, 'links': sorted(links),
            'link_classes': {str(k): v for k, v in classes.items()}, 'via_path': path_used,
            'joint_member': bool(both)}


def verdict(law, way, confirmed, link):
    if law.joinable != 'MET':
        return 'supplied (the record alone)'
    if way == 'a round-wide trigger':
        return 'supplied (a round-wide trigger)'
    if law.take == 'FIRST' and way == 'a take':
        return 'supplied (its rule looked for the other part)'
    if confirmed and link is not None:
        if link['made_connected']:
            return 'through a knot the growth made'
        if link['start_connected']:
            return 'through a start knot'
        return 'unconfirmed (confirmed by a mask; linked through both kinds of met set)'
    return 'unconfirmed'


# ------------------------------------------------------------------------------------------------- one pair, fully
def one_part_again(view, s, X, Y):
    """D 4.3, first round t > s with a member of X or its descendants and one of Y's in one part (run A)."""
    A = view.run
    for t in range(s + 1, view.R + 1):
        S = A.snap[t]
        xd = side_of(S, X, s)
        yd = side_of(S, Y, s)
        Rt = view.roster(t)
        px = {Rt.part_of[u] for u in Rt.members if u in xd}
        py = {Rt.part_of[u] for u in Rt.members if u in yd}
        if px & py:
            return t
    return None


def joint_birth(view, s, X, Y):
    A = view.run
    S = A.snap[view.R]
    xd = side_of(S, X, s)
    yd = side_of(S, Y, s)
    for t in range(s + 1, view.R + 1):
        for b in A.records[t - 1]['births']:
            if any(p in xd for p in b['parents']) and any(p in yd for p in b['parents']):
                return t, b['id'], b['parents']
    return None


def comparison_knot_tests(view, s, run, kind):
    """R 18: the comparison run at its last round read."""
    law = run.law
    last = run.rounds_done
    if law.knot_law == 'parity':
        return K.test_run(run.snap, law, rounds=[last])
    out = K.test_run(run.snap, law, rounds=[last], only_new_after=s)
    if kind == 'B(ii)':
        # knots made by round s that failed in run A: retest directly at the last round
        fails = {f['knot'] for f in view.knot_fails_upto(s)}
        S = run.snap[last]
        redo = [u for u in fails if u not in S.removed and u < S.n_knots]
        if redo:
            d = K.nae_direct(S, redo)
            out['verdicts'] += len(d)
            out['fails'] += [K._fail_row(S, u, last, 'direct') for u, v in d.items() if not v]
    return out


def analyse_pair(view, p, b2=True, masks=True, kt=True):
    A = view.run
    s, X, Y = p['s'], p['X'], p['Y']
    res = dict(p)
    res['one_part_again'] = one_part_again(view, s, X, Y)
    jb = joint_birth(view, s, X, Y)
    res['joint_birth'] = jb[0] if jb else None
    res['joint_birth_detail'] = {'birth': jb[1], 'parents': list(jb[2])} if jb else None
    trA = trace(A, X, s)
    B1 = run_from(view, s, bar_part(A.snap[s], Y))
    trB = trace(B1, X, s)
    d, way, dem, n = first_difference(trA, trB)
    res.update({'course_differs': d, 'way': way, 'demand_line': dem, 'rounds_compared': n,
                'B1_rounds': B1.rounds_done, 'B1_stop': B1.stop})
    if kt:
        res['kt_B1'] = _kt_brief(comparison_knot_tests(view, s, B1, 'B(i)'))
    if b2:
        T = remove_part(A.snap[s], Y, s)
        if T is None:
            res['b2'] = 'not defined'
        else:
            B2 = run_from(view, s, T)
            trB2 = trace(B2, X, s)
            d2, way2, dem2, n2 = first_difference(trA, trB2)
            res['b2'] = {'course_differs': d2, 'way': way2, 'demand_line': dem2, 'rounds_compared': n2}
            if kt:
                res['kt_B2'] = _kt_brief(comparison_knot_tests(view, s, B2, 'B(ii)'))
    res['confirmed'] = None
    res['link'] = None
    if d is not None and masks:
        M = masked_run(view, s, X, Y, 'XY')
        trM = trace(M, X, s)
        dm, _, _, nm = first_difference(trM, trB)
        if kt:
            res['kt_M'] = _kt_brief(comparison_knot_tests(view, s, M, 'M'))
        if dm is None:
            res['confirmed'] = 'through a meeting'
        else:
            M2 = masked_run(view, s, X, Y, 'ISO')
            trM2 = trace(M2, X, s)
            dm2, _, _, _ = first_difference(trM2, trB)
            if kt:
                res['kt_M2'] = _kt_brief(comparison_knot_tests(view, s, M2, "M'"))
            if dm2 is None:
                res['confirmed'] = 'through a third part'
            else:
                res['confirmed'] = None
                res['M_differs_from_B1'] = dm
                res['M2_differs_from_B1'] = dm2
        if res['one_part_again'] is not None:
            res['link'] = linking(view, res['one_part_again'], X, Y, s)
        res['verdict'] = verdict(A.law, way, res['confirmed'] is not None, res['link'])
    elif d is not None:
        res['verdict'] = None
    return res


def _kt_brief(kt):
    return {'verdicts': kt['verdicts'], 'n_fails': len(kt['fails']), 'fails': kt['fails'][:10],
            'n_disagree': len(kt['disagree']), 'disagree': kt['disagree'][:10], 'untested': kt['untested'][:10],
            'n_untested': len(kt['untested']), 'birth_vs_direct': kt['birth_vs_direct']}


# --------------------------------------------------------------------------------------------------- a whole run
class Analysed:
    pass


def analyse_run(start_name, law, rev=False, every_pair=False, b2=True, masks=True, kt=True, start_struct=None,
                extra_pairs=None):
    S0 = start_struct if start_struct is not None else pm.start(start_name, reverse_names=rev)
    A = pm.Run(S0, law)
    view = RunView(A)
    out = {'start': start_name, 'names_reversed': rev, 'law': law.name(), 'law_fields': law.to_dict(),
           'rounds': A.rounds_done, 'stop': A.stop, 'guard': A.guard, 'knots': A.S.n_knots - len(A.S.removed)}
    out['per_round'] = round_stats(view)
    if start_name in ('Ring(5,3)', 'Ring(7,3)', 'D2(5,3)'):
        out['ring_returns'] = ring_returns(view)
    out['all_pairs'] = all_pairs_checks(view)
    kres = K.test_run(A.snap, law) if kt else None
    view._kt = kres
    view.knot_fails_upto = lambda s: [f for f in (kres['fails'] if kres else []) if f['round'] <= s]
    if kres is not None:
        out['knot_tests'] = _kt_brief(kres)
        out['knot_tests']['fails'] = kres['fails'][:40]
    pairs = select_pairs(view, every_pair=every_pair, two_knot=(start_name == 'two-knot'))
    if extra_pairs:
        pairs += extra_pairs
    out['pairs'] = [analyse_pair(view, p, b2=b2, masks=masks, kt=kt) for p in pairs]
    out['max_holders'] = max(r['max_holders'] for r in out['per_round'])
    return out, view
