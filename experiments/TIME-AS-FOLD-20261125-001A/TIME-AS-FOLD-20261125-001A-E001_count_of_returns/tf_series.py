"""Series of returns, ticks, clocks, the parts given off and copies (TD 2), written from the frozen text.

Readings are numbered in deviations.md (cited "dev n").  A run gives rosters[t], the live roster after round t.
"""
from __future__ import annotations

import itertools
from collections import Counter, defaultdict

import networkx as nx

import tf_engine as E


# ---------------------------------------------------------------------------------------------------- sameness
def part_data(R, P):
    """(members, h, k, maximal met sets of the part) and an invariant; cached on the roster."""
    key = ('pd', P)
    c = R._cache.get(key)
    if c is not None:
        return c
    Ps = set(P)
    if 'by_first' not in R._cache:
        bf = defaultdict(list)
        for M in R.maxsets:
            bf[R.part_of[next(iter(M))]].append(M)
        R._cache['by_first'] = bf
    msets = R._cache['by_first'][R.part_of[P[0]]] if P else []
    sizes_of = defaultdict(list)
    for M in msets:
        for x in M:
            sizes_of[x].append(len(M))
    sig = {u: (R.h[u], R.k[u], tuple(sorted(sizes_of[u]))) for u in P}
    inv = (len(P), tuple(sorted(sig.values())), tuple(sorted(len(M) for M in msets)))
    c = (P, sig, msets, inv)
    R._cache[key] = c
    return c


def _graph(P, sig, msets):
    G = nx.Graph()
    for u in P:
        G.add_node(('m', u), c=('m',) + sig[u])
    for i, M in enumerate(msets):
        G.add_node(('s', i), c=('s', len(M)))
        for u in M:
            G.add_edge(('s', i), ('m', u))
    return G


def same_parts(R1, P1, R2, P2, force_vf2=False):
    """SD lines 29-30: a one-to-one renaming of members carrying h, k and the family of inclusion-maximal met sets."""
    _, s1, m1, i1 = part_data(R1, P1)
    _, s2, m2, i2 = part_data(R2, P2)
    if i1 != i2:
        return False
    if len(P1) <= 1:
        return True
    fam1 = {M for M in m1}
    if len(P1) <= 6 and not force_vf2:
        # brute force over renamings that keep each member's signature
        classes1 = defaultdict(list)
        classes2 = defaultdict(list)
        for u in P1:
            classes1[s1[u]].append(u)
        for u in P2:
            classes2[s2[u]].append(u)
        keys = sorted(classes1)
        target = {frozenset(M) for M in m2}
        for combo in itertools.product(*[itertools.permutations(classes2[k]) for k in keys]):
            mp = {}
            for k, perm in zip(keys, combo):
                for a, b in zip(classes1[k], perm):
                    mp[a] = b
            if {frozenset(mp[x] for x in M) for M in fam1} == target:
                return True
        return False
    return iso_refine(P1, s1, m1, P2, s2, m2)


def _bip(P, sig, msets):
    """The part as a coloured graph: member nodes 0..n-1, met-set nodes n.., adjacency lists, initial colours."""
    idx = {u: i for i, u in enumerate(P)}
    n = len(P)
    adj = [[] for _ in range(n + len(msets))]
    col = [('m',) + sig[u] for u in P] + [('s', len(M)) for M in msets]
    for j, M in enumerate(msets):
        for u in M:
            adj[idx[u]].append(n + j)
            adj[n + j].append(idx[u])
    return adj, col


def _refine(adjs, cols):
    """Joint colour refinement of several graphs (colours renamed alike in all): returns the stable colourings, or
    None when the colour histograms differ."""
    while True:
        keys = sorted({c for col in cols for c in col}, key=repr)
        ren = {c: i for i, c in enumerate(keys)}
        cur = [[ren[c] for c in col] for col in cols]
        hist = [sorted(c) for c in cur]
        if any(h != hist[0] for h in hist[1:]):
            return None
        sigs = [[(c[v], tuple(sorted(c[w] for w in adj[v]))) for v in range(len(adj))] for adj, c in zip(adjs, cur)]
        ncol = len(set(cur[0]))
        nsig = len(set(sigs[0]))
        if nsig == ncol:
            return cur
        cols = sigs


def _iso_search(adj1, adj2, c1, c2, depth=0):
    r = _refine([adj1, adj2], [c1, c2])
    if r is None:
        return False
    c1, c2 = r
    cells = defaultdict(list)
    for v, c in enumerate(c1):
        cells[c].append(v)
    nonsingle = [c for c, vs in cells.items() if len(vs) > 1]
    if not nonsingle:
        mp = {}
        inv = {c: v for v, c in enumerate(c2)}
        for v, c in enumerate(c1):
            mp[v] = inv[c]
        for v in range(len(adj1)):
            if sorted(mp[w] for w in adj1[v]) != sorted(adj2[mp[v]]):
                return False
        return True
    k = min(nonsingle, key=lambda c: (len(cells[c]), c))
    v1 = cells[k][0]
    big = max(max(c1), max(c2)) + 1
    for v2 in [v for v, c in enumerate(c2) if c == k]:
        d1 = list(c1)
        d2 = list(c2)
        d1[v1] = big
        d2[v2] = big
        if _iso_search(adj1, adj2, d1, d2, depth + 1):
            return True
    return False


def iso_refine(P1, s1, m1, P2, s2, m2):
    """Isomorphism of the two coloured member/met-set graphs by colour refinement and individualisation (dev 32)."""
    adj1, col1 = _bip(P1, s1, m1)
    adj2, col2 = _bip(P2, s2, m2)
    if len(adj1) != len(adj2):
        return False
    return _iso_search(adj1, adj2, col1, col2)


def same_brute(R1, P1, R2, P2):
    """Brute force over every member bijection (G3's check of altered copies)."""
    if len(P1) != len(P2):
        return False
    _, s1, m1, _ = part_data(R1, P1)
    _, s2, m2, _ = part_data(R2, P2)
    target = {frozenset(M) for M in m2}
    hk2 = {u: (R2.h[u], R2.k[u]) for u in P2}
    for perm in itertools.permutations(P2):
        mp = dict(zip(P1, perm))
        if any((R1.h[a], R1.k[a]) != hk2[b] for a, b in mp.items()):
            continue
        if {frozenset(mp[x] for x in M) for M in m1} == target:
            return True
    return False


def past_start(R, P):
    return not any(u in R.meets_member for u in P)


def direct_meetings(R, P):
    """Pairs of members of P that meet directly, and how many of them lie in no maximal met set (not carried)."""
    Ps = set(P)
    pairs = set()
    for w in P:
        for u in R.member_meets.get(w, ()):
            if u in Ps and u != w:
                pairs.add((min(u, w), max(u, w)))
    if not pairs:
        return 0, 0
    _, _, msets, _ = part_data(R, P)
    nc = 0
    for a, b in pairs:
        if not any(a in M and b in M for M in msets):
            nc += 1
    return len(pairs), nc


# ------------------------------------------------------------------------------------------------------- descent
def descent_labels(run, s):
    """Labels (bit sets over the parts of the roster after round s) of every member after every round t >= s:
    a member of a part P after round s carries P; a knot made after s carries the union of its parents' (dev 6)."""
    cache = getattr(run, '_labels', None)
    if cache is None:
        cache = run._labels = {}
    if s in cache:
        return cache[s]
    S = run.S
    Rs = run.roster(s)
    lab = {}
    for u in Rs.members:
        lab[u] = 1 << Rs.part_of[u]
    n0 = 0
    while n0 < len(S.made) and S.made[n0] <= s:
        n0 += 1
    for x in range(n0, S.n_knots):
        v = 0
        for p in S.parents[x]:
            v |= lab.get(p, 0)
        if v:
            lab[x] = v
    cache[s] = lab
    return lab


# --------------------------------------------------------------------------------------------------- first returns
class Returns:
    """For every round s and every part P after s that is searched (past its start when the filter is on), its first
    return (TD 2.3): the least t > s with a part Q every member of which descends from P, with a member made after s,
    the same as P.  Records every qualifying Q, the parts given off (TD 2.7, mixed labelled) and the followed Q."""

    def __init__(self, run, past, convention='least', clock=None):
        self.run = run
        self.past = past
        self.convention = convention
        self.first = {}           # (s, part index) -> dict or None
        T = run.rounds_done
        S = run.S
        for s in range(0, T):
            Rs = run.roster(s)
            pend = set(i for i, P in enumerate(Rs.parts) if (not past or past_start(Rs, P)))
            if not pend:
                continue
            lab = descent_labels(run, s)
            for i in list(pend):
                self.first[(s, i)] = None
            for t in range(s + 1, T + 1):
                if not pend:
                    break
                Rt = run.roster(t)
                alive = 0
                qual = defaultdict(list)
                info = []
                for j, Q in enumerate(Rt.parts):
                    a = -1
                    o = 0
                    new = False
                    for x in Q:
                        v = lab.get(x, 0)
                        a &= v
                        o |= v
                        if S.made[x] > s:
                            new = True
                    if a == -1:
                        a = 0
                    alive |= o
                    info.append((a, o, new))
                cand = defaultdict(list)
                for j, Q in enumerate(Rt.parts):
                    a, o, new = info[j]
                    if not new or not a:
                        continue
                    x = a
                    while x:
                        low = x & -x
                        i = low.bit_length() - 1
                        x ^= low
                        if i in pend:
                            cand[i].append(j)
                for i in sorted(pend):
                    bit = 1 << i
                    if not alive & bit:
                        pend.discard(i)          # no member descends from P any more: no return (dev 8)
                        continue
                    P = Rs.parts[i]
                    hits = []
                    for j in cand.get(i, ()):
                        Q = Rt.parts[j]
                        if len(Q) == len(P) and same_parts(Rs, P, Rt, Q):
                            hits.append(j)
                    if hits:
                        pend.discard(i)
                        if convention == 'least':
                            fj = min(hits, key=lambda j: Rt.parts[j][0])
                        else:
                            fj = max(hits, key=lambda j: Rt.parts[j][0])
                        off = []
                        for j, Q in enumerate(Rt.parts):
                            if j in hits:
                                continue
                            a, o, new = info[j]
                            if o & bit:
                                off.append({'part': list(Q), 'mixed': not bool(a & bit)})
                        dm_p = direct_meetings(Rs, P)
                        dm_q = direct_meetings(Rt, Rt.parts[fj])
                        self.first[(s, i)] = {'t': t, 'qual': hits, 'follow': fj, 'off': off,
                                              'direct_P': dm_p, 'direct_Q': dm_q}
                if clock is not None:
                    clock.check()


def build_series(run, past, convention='least', clock=None):
    """TD 2.4: series of returns from every searched part that is not the followed first return of an earlier part."""
    RT = Returns(run, past, convention, clock)
    T = run.rounds_done
    followed = set()
    for (s, i), fr in RT.first.items():
        if fr is not None:
            followed.add((fr['t'], fr['follow']))
    out = []
    for s in range(0, T + 1):
        Rs = run.roster(s)
        for i, P in enumerate(Rs.parts):
            if (s, i) not in RT.first:
                continue                       # not searched (not past its start under the filter, or last round)
            if (s, i) in followed:
                continue
            ser = {'t0': s, 'P0': list(P), 'size': len(P), 'ticks': []}
            cur = (s, i)
            while True:
                fr = RT.first.get(cur)
                if fr is None:
                    break
                t = fr['t']
                Rt = run.roster(t)
                Q = Rt.parts[fr['follow']]
                tick = {'t': t, 'part': list(Q), 'copies': [list(Rt.parts[j]) for j in fr['qual'] if j != fr['follow']],
                        'off': fr['off'], 'n_off': len(fr['off']), 'n_mixed': sum(1 for o in fr['off'] if o['mixed']),
                        'direct_P': fr['direct_P'], 'direct_Q': fr['direct_Q']}
                ser['ticks'].append(tick)
                cur = (t, fr['follow'])
                if cur not in RT.first:
                    break                      # Q not searched (not past its start under the filter, or last round)
            prev = s
            per = []
            for tk in ser['ticks']:
                per.append(tk['t'] - prev)
                prev = tk['t']
            ser['periods'] = per
            out.append(ser)
    return out, RT


def equal_stretches(periods, n=4):
    """Indices j (0-based tick index of t_j, with t_0 the series' start) such that the n periods after t_j are equal."""
    out = []
    for j in range(0, len(periods) - n + 1):
        if len(set(periods[j:j + n])) == 1:
            out.append(j)
    return out


def describe(series):
    """Per series: clock (two or more members and four consecutive equal periods), ticks giving parts off, copies."""
    for ser in series:
        ser['endless_chain'] = ser['size'] == 1
        st = equal_stretches(ser['periods'])
        ser['equal_stretches'] = st
        ser['clock'] = ser['size'] >= 2 and bool(st)
        off_flags = [tk['n_off'] > 0 for tk in ser['ticks']]
        ser['ticks_off'] = sum(off_flags)
        ser['ticks_copies'] = sum(1 for tk in ser['ticks'] if tk['copies'])
        ser['ticks_off_or_copies'] = sum(1 for tk in ser['ticks'] if tk['n_off'] > 0 or tk['copies'])
        # a clock giving parts off at four ticks: primary, the four ticks after some t_j of four equal periods each
        # give parts off (dev 12); secondary, a clock with four or more ticks giving parts off anywhere
        ser['clock_off4'] = ser['clock'] and any(all(off_flags[j:j + 4]) for j in st)
        ser['clock_off4_anywhere'] = ser['clock'] and ser['ticks_off'] >= 4
    return series


def start_roster_returns(run):
    """TD 2.8: rounds t >= 1 at which some part is the same as the start's whole roster."""
    R0 = run.roster(0)
    whole = tuple(R0.members)
    if not whole:
        return []
    # the whole roster as one "part": signature with all maximal met sets
    out = []
    key = ('pd', whole)
    if key not in R0._cache:
        sizes_of = defaultdict(list)
        for M in R0.maxsets:
            for x in M:
                sizes_of[x].append(len(M))
        sig = {u: (R0.h[u], R0.k[u], tuple(sorted(sizes_of[u]))) for u in whole}
        inv = (len(whole), tuple(sorted(sig.values())), tuple(sorted(len(M) for M in R0.maxsets)))
        R0._cache[key] = (whole, sig, list(R0.maxsets), inv)
    for t in range(1, run.rounds_done + 1):
        Rt = run.roster(t)
        for Q in Rt.parts:
            if len(Q) == len(whole) and same_parts(R0, whole, Rt, Q):
                out.append(t)
                break
    return out


def acting_knots(run, ser, k=None):
    """Knots descended from the series' first part that are parents of a birth in a round of the series (dev 24):
    the start knots among them, and (k given) those with no ancestor exactly k parent steps above them."""
    if not ser['ticks']:
        return 0, 0
    S = run.S
    s = ser['t0']
    Rs = run.roster(s)
    lab = descent_labels(run, s)
    bit = 1 << Rs.part_of[ser['P0'][0]]
    last = ser['ticks'][-1]['t']
    st, kk = set(), set()
    for t in range(s + 1, last + 1):
        for b in run.records[t - 1]['births']:
            for p in b['parents']:
                if lab.get(p, 0) & bit:
                    if S.made[p] == 0:
                        st.add(p)
                    if k is not None and not S.level(p, k):
                        kk.add(p)
    return len(st), len(kk)


def series_summary(series):
    clocks = [s for s in series if s['clock']]
    return {'n_series': len(series), 'n_clocks': len(clocks),
            'clock': bool(clocks),
            'clock_off4': any(s['clock_off4'] for s in series),
            'clock_off4_anywhere': any(s['clock_off4_anywhere'] for s in series),
            'series_off2': any(s['ticks_off'] >= 2 for s in series),
            'max_ticks_off': max((s['ticks_off'] for s in series), default=0),
            'max_ticks_off_or_copies': max((s['ticks_off_or_copies'] for s in series), default=0),
            'endless_chains': sum(1 for s in series if s['endless_chain'] and s['ticks']),
            'tick_off_any': any(s['ticks_off'] >= 1 for s in series),
            'mixed_parts_given_off': sum(tk['n_mixed'] for s in series for tk in s['ticks']),
            'copies': sum(len(tk['copies']) for s in series for tk in s['ticks']),
            'direct_not_carried': sum(tk['direct_Q'][1] for s in series for tk in s['ticks'])}


def compact(series, maxn=400):
    """A compact listing of series for the outputs (members listed for the first part and each tick's part)."""
    out = []
    for s in series:
        if not s['ticks']:
            continue
        out.append({'t0': s['t0'], 'P0': s['P0'], 'size': s['size'], 'periods': s['periods'],
                    'ticks': [[tk['t'], tk['part'], tk['n_off'], tk['n_mixed'], len(tk['copies']),
                               tk['direct_Q'][0], tk['direct_Q'][1]] for tk in s['ticks']],
                    'clock': s['clock'], 'clock_off4': s['clock_off4'], 'ticks_off': s['ticks_off']})
        if len(out) >= maxn:
            break
    return out
