"""Run 0: the controls of KD 8, checks E, F, R, I and N on the named starts, the unit tests of the readings, and the
run 4b probe.  usage: python -B run0.py [controls|checks|probe|all]   (writes run0_*.json in the artifact folder)"""
from __future__ import annotations

import sys
import time
from fractions import Fraction
from math import comb

import numpy as np

import ge
import kwr
import readings as RD

RES = {}


def check(name, cond, detail=None):
    RES[name] = {'ok': bool(cond), 'detail': detail}
    kwr.log('%-78s %s' % (name, 'ok' if cond else 'FAIL'), '' if cond else str(detail)[:600])
    return cond


# ----------------------------------------------------------------------------------------------- hand-built controls
def weave(L):
    """KD 8.3: the six-regular one-pair weave of L x L (two knots per square of the drawn grid): distinctions
    v(i, j) = (i mod L) + L (j mod L); knots [v(i,j), v(i+1,j), v(i,j+1)] and [v(i+1,j), v(i,j+1), v(i+1,j+1)]
    (the record's construction, SPACE-ORDER-20261117-001A weaves.py, R 10)."""
    def v(a, b):
        return (a % L) + L * (b % L)
    up, down = [], []
    for i in range(L):
        for j in range(L):
            up.append([v(i, j), v(i + 1, j), v(i, j + 1)])
            down.append([v(i + 1, j), v(i, j + 1), v(i + 1, j + 1)])
    return up + down


def control_counts(stars, sources, upto):
    S = kwr.pm.from_stars(stars)
    G = kwr.Graphs(S)
    D = G.hs(list(sources))
    return S, G, {u: kwr.counts_from(D[u], upto) for u in sources}


def controls():
    out = {}
    N = kwr.named()['controls']
    # 1. ring of knots R_400
    S, G, C = control_counts(N['R_400'], range(400), 64)
    ok = all(C[u] == [2 * r + 1 for r in range(65)] for u in C)
    vs = {RD.label(RD.read(C[u])) for u in C}
    g = RD.gate(C)
    out['R_400'] = {'formula_2r+1': ok, 'verdicts': sorted(vs), 'gate': _gate_short(g)}
    check('control 1 R_400: H = 2r + 1 from every knot (400), r <= 64', ok)
    check('control 1 R_400: POWER(1) from every knot', vs == {'POWER(1)'}, vs)
    check('control 1 R_400: gate j = 1 on [4, 64]', g['holds'] and g['j'] == 1 and g['range'] == [4, 64],
          _gate_short(g))
    # 2. branching T_12
    S, G, C = control_counts(N['T_12'], [0], 12)
    H = C[0]
    ok = H == [3 * 2 ** r - 2 for r in range(13)]
    Sinc, s0 = RD.increments(H, 0)
    vS = RD.read(Sinc, s0, kind='S')
    vH = RD.read(H)
    deg = np.diff(G.knot_graph.indptr) + np.bincount(G.knot_graph.indices, minlength=S.n_knots)
    leaves = [u for u in range(S.n_knots) if deg[u] == 1]
    out['T_12'] = {'H': H, 'S_reading': vS, 'H_reading': vH, 'knots': S.n_knots, 'leaves': len(leaves),
                   'degree_counts': {int(k): int(v) for k, v in zip(*np.unique(deg, return_counts=True))}}
    check('control 2 T_12: every knot meets three but the leaves (meets one)', set(deg.tolist()) == {1, 3},
          out['T_12']['degree_counts'])
    check('control 2 T_12: H = 3*2^r - 2 on [0, 12] from the root', ok, H)
    check('control 2 T_12: S reads LINREC(1) root 2, 2 fitted, 10 verified',
          vS['verdict'] == 'LINREC' and vS['k'] == 1 and vS['root'] == 2.0 and vS['fitted'] == 2
          and vS['verified'] == 10, vS)
    # 3. six-regular weave W_99
    W = weave(99)
    rng = kwr.rng_for('W_99', 'control', 'nae', 'control')
    src = kwr.sample_sorted(rng, range(len(W)), 16)
    S, G, C = control_counts(W, src, 32)
    ok = all(C[u] == [6 * r * r + 6 * r + 1 for r in range(33)] for u in C)
    g = RD.gate(C)
    out['W_99'] = {'sources': src, 'formula': ok, 'gate': _gate_short(g), 'example': C[src[0]][:6]}
    check('control 3 W_99: H = 6r^2 + 6r + 1 from 16 knots, r <= 32', ok, C[src[0]][:8])
    check('control 3 W_99: gate j = 2 on [4, 32]', g['holds'] and g['j'] == 2 and g['range'] == [4, 32],
          _gate_short(g))
    # 4. the fixed ration of three from one knot (L8, 65 rounds)
    gr = kwr.Grown('one-knot', kwr.make_law('L8'), 65)
    b = gr.births()
    okb = b == [comb(t + 2, 2) for t in range(1, len(b) + 1)]
    vb = RD.read(b, 1, kind='b')
    S = gr.S
    G = kwr.Graphs(S)
    s = G.steps_from_start(S.n_start)
    smin = min(int(s[u]) for u in gr.members[-1])
    ell = smin - 0
    H = kwr.counts_from(G.hs([0])[0], ell)
    okh = H == [comb(r + 3, 3) for r in range(ell + 1)]
    vH = RD.read(H)
    out['L8_one_knot'] = {'rounds': gr.rounds_done, 'stop': gr.stop, 'knots': S.n_knots, 'births_ok': okb,
                          'births_reading': vb, 'ell': ell, 'H_ok': okh, 'H_reading': vH}
    check('control 4 L8: 65 rounds reached, b(t) = C(t + 2, 2)', gr.rounds_done == 65 and okb, (gr.rounds_done, b[:5]))
    check('control 4 L8: births of degree 2 from round 1', vb['verdict'] == 'POWER' and vb['j'] == 2
          and vb['segment'][0] == 1, vb)
    check('control 4 L8: H from the start knot = C(r + 3, 3), POWER(3) on [0, %d]' % ell,
          okh and vH['verdict'] == 'POWER' and vH['j'] == 3 and vH['segment'][0] == 0 and vH['segment'][1] >= 64,
          (ell, vH))
    # 5. the comb (negative control for the gate)
    comb_stars = N['comb_64_64']
    spine = list(range(64))
    far = [127 + 64 * i for i in range(64)]
    mid = [64 + 64 * i + 31 for i in range(64)]
    ex = spine + far + mid
    S, G, C = control_counts(comb_stars, ex, 63)
    ok1 = C[0] == [comb(r + 2, 2) for r in range(64)]
    ok2 = all(C[u] == [r + 1 for r in range(64)] for u in far)
    g = RD.gate(C)
    out['comb'] = {'first_spine': ok1, 'far_ends': ok2, 'gate': _gate_short(g), 'K': len(ex)}
    check('control 5 comb: H = C(r + 2, 2) from the first spine knot, r <= 63', ok1, C[0][:6])
    check('control 5 comb: H = r + 1 from every far leg end', ok2)
    check('control 5 comb: the gate fails (192 knots examined)', (not g['holds']) and len(ex) == 192, _gate_short(g))
    # 6, 7. T_12 under not-all-equal: kappa between leaves, exact
    out['order_controls'] = tree_order_controls(N['T_12'])
    # 8. the bare rings' counts
    out['bare_rings'] = bare_rings()
    return out


def _gate_short(g):
    keep = ('holds', 'j', 'range', 'k', 'K', 'reason', 'spread', 'k_by_j_on_widest', 'least_l', 'zmax')
    return {k: g[k] for k in keep if k in g}


# ---------------------------------------------------------------------- exact kappa on a tree (independent of formula)
def tree_kappas(S, src):
    """Exact counts on a structure whose holder graph is a tree with every shared distinction held twice, under
    not-all-equal: for the first loose distinction a of knot src and the first loose b of every other knot v,
    returns {v: kappa(a, b)} as Fractions.  Two passes (inside, outside) in Python integers; no product formula."""
    Nk = S.n_knots
    H = S.holders
    shared = {u: [d for d in S.places[u] if len(H[d]) == 2] for u in range(Nk)}
    lam = {u: len(S.places[u]) - len(shared[u]) for u in range(Nk)}
    # root at src; parent edge of each knot
    par, pe = {src: None}, {src: None}
    order = [src]
    for x in order:
        for d in shared[x]:
            w = H[d][0] if H[d][1] == x else H[d][1]
            if w not in par:
                par[w], pe[w] = x, d
                order.append(w)
    assert len(order) == Nk
    children = {u: [] for u in range(Nk)}
    for w in order[1:]:
        children[par[w]].append(w)
    inside = {}
    for w in reversed(order[1:]):
        A0 = A1 = 1
        T = 1
        for c in children[w]:
            i0, i1 = inside[c]
            A0 *= i0
            A1 *= i1
            T *= (i0 + i1)
        L = 2 ** lam[w]
        inside[w] = (L * T - A0, L * T - A1)
    # outside messages: out[w][x] = weight of everything outside w's subtree given w's parent edge = x, a pinned to 0
    out = {}
    # the root src: places = its edge(s) to children, a (pinned 0) and its other loose ones (lam - 1 free)
    la = lam[src]
    for w in children[src]:
        # src's weight given its child edges y (w's edge x, siblings free) and a = 0:
        #   sum over other loose (la - 1 of them) of NAE(y, a=0, others) = 2^(la-1) - [y all 0]   (y all 1 never all
        #   equal with a = 0)
        sib = [c for c in children[src] if c != w]
        T = 1
        A0 = 1
        for c in sib:
            i0, i1 = inside[c]
            T *= (i0 + i1)
            A0 *= i0
        L = 2 ** (la - 1)
        out[w] = (L * T - A0, L * T)
    for p in order[1:]:
        for w in children[p]:
            sib = [c for c in children[p] if c != w]
            T = 1
            A = [1, 1]
            for c in sib:
                i0, i1 = inside[c]
                T *= (i0 + i1)
                A[0] *= i0
                A[1] *= i1
            L = 2 ** lam[p]
            o0, o1 = out[p]
            tot = (o0 + o1) * L * T
            out[w] = (tot - o0 * A[0], tot - o1 * A[1])
    res = {}
    for v in range(Nk):
        if v == src or lam[v] < 1:
            continue
        # v's weight with b fixed: given v's parent edge x and children edges y: loose others (lam - 1) free
        # N(b = beta) = sum_x out_v(x) * sum_y prod inside * (2^(lam-1) - [x,y all = beta... ])
        T = 1
        A = [1, 1]
        for c in children[v]:
            i0, i1 = inside[c]
            T *= (i0 + i1)
            A[0] *= i0
            A[1] *= i1
        L = 2 ** (lam[v] - 1)
        o0, o1 = out[v]
        # with b = beta, v is all equal only if parent edge, children edges and other loose all equal beta
        n_b0 = (o0 + o1) * L * T - o0 * A[0]
        n_b1 = (o0 + o1) * L * T - o1 * A[1]
        total = n_b0 + n_b1                     # = number of allowed states with a = 0
        # rho = P(a != b) = P(b = 1 | a = 0) by the flip; kappa = 1 - 2 rho
        res[v] = 1 - 2 * Fraction(n_b1, total)
    return res


def tree_order_controls(T12):
    S = kwr.pm.from_stars(T12)
    G = kwr.Graphs(S)
    deg = np.diff(G.knot_graph.indptr) + np.bincount(G.knot_graph.indices, minlength=S.n_knots)
    leaves = [u for u in range(S.n_knots) if deg[u] == 1]
    t0 = time.time()
    srcs = [leaves[0], leaves[-1], leaves[len(leaves) // 3]]
    allok = True
    strictly = True
    by_hs = {}
    n_pairs = 0
    for src in srcs:
        K = tree_kappas(S, src)
        hs = G.hs([src])[src]
        for v in leaves:
            if v == src:
                continue
            k = int(hs[v])
            formula = Fraction(-1, 3) ** (k + 1)
            n_pairs += 1
            if K[v] != formula:
                allok = False
            by_hs.setdefault(k, set()).add(K[v])
    ks = sorted(by_hs)
    one_value = all(len(by_hs[k]) == 1 for k in ks)
    for a, b in zip(ks, ks[1:]):
        if not (abs(next(iter(by_hs[b]))) < abs(next(iter(by_hs[a])))):
            strictly = False
    # counts of leaf pairs by hs over every pair (by the tree's levels), and the order test over every pair of pairs:
    # kappa depends on hs alone (checked from three sources; the automorphisms of the tree carry any leaf to any
    # other, R 11), so pairs with equal hs are tied and pairs with unequal hs concordant
    D = G.hs(leaves[:1])[leaves[0]]
    nh = {}
    # pairs of leaves at each hs: every leaf has the same profile, so n_h = (number of leaves) * profile / 2
    prof = {}
    for v in leaves[1:]:
        prof[int(D[v])] = prof.get(int(D[v]), 0) + 1
    L = len(leaves)
    for k, c in prof.items():
        nh[k] = L * c // 2
    tied = sum(c * (c - 1) // 2 for c in nh.values())
    conc = 0
    hs_sorted = sorted(nh)
    for i, a in enumerate(hs_sorted):
        for b in hs_sorted[i + 1:]:
            conc += nh[a] * nh[b]
    disc = 0 if strictly and one_value else None
    out = {'sources': srcs, 'pairs_checked_exactly': n_pairs, 'kappa_equals_formula': allok,
           'one_kappa_per_hs': one_value, 'strictly_smaller_when_hs_larger': strictly,
           'kappa_by_hs': {k: str(next(iter(by_hs[k]))) for k in ks}, 'leaf_pairs_by_hs': nh,
           'comparisons_over_every_pair_of_leaf_pairs': {'concordant': conc, 'discordant': disc, 'tied': tied},
           'seconds': round(time.time() - t0, 1)}
    check('control 6 T_12 nae: kappa = product formula on %d leaf pairs from 3 sources (exact count)' % n_pairs, allok,
          out['kappa_by_hs'])
    check('control 6 T_12 nae: |kappa| strictly smaller when hs larger; no discordant comparison',
          strictly and one_value and disc == 0, out)
    # 7. a known tie: two pairs of leaves with equal hs (hs = 4 in two different subtrees)
    K0 = tree_kappas(S, leaves[0])
    K1 = tree_kappas(S, leaves[-1])
    D0, D1 = G.hs([leaves[0]])[leaves[0]], G.hs([leaves[-1]])[leaves[-1]]
    v0 = next(v for v in leaves if D0[v] == 4)
    v1 = next(v for v in leaves if D1[v] == 4)
    tie = K0[v0] == K1[v1]
    c, d, t = ge.order_counts(ge.dense_rank([abs(K0[v0]), abs(K1[v1])]), [-4, -4])
    out['tie'] = {'pairs': [[leaves[0], v0], [leaves[-1], v1]], 'kappas': [str(K0[v0]), str(K1[v1])],
                  'order': {'concordant': c, 'discordant': d, 'tied': t}}
    check('control 7 T_12 nae: two leaf pairs at hs 4 have equal kappa; the order test counts them tied',
          tie and (c, d, t) == (0, 0, 1), out['tie'])
    return out


def bare_rings():
    """KD 8.8: Ring(n, 2) under L0: from a made knot of round t >= n with l >= n, H = 2r^2+2r+1 for r <= n-1 and
    n(2r+1) for r >= n; from a start knot 2r^2+2r+1 for r <= (n-1)/2, then +(n+1) a step to (r+1)^2 at r = n-1, then +n."""
    out = {}
    for n in (5, 7, 9, 11, 15, 21, 33):
        T = 3 * n
        gr = kwr.Grown('Ring(%d,2)' % n, kwr.make_law('L0'), T)
        S = gr.S
        G = kwr.Graphs(S)
        s = G.steps_from_start(S.n_start)
        smin = min(int(s[u]) for u in gr.members[-1])
        made = [u for u in range(S.n_knots) if n <= S.made[u] <= smin - n]
        D = G.hs(list(range(n)) + made)
        okm = True
        n_reg = n_upto = n_ext = 0
        listing = []
        for u in made:
            t = S.made[u]
            ell = smin - int(s[u])
            H = kwr.counts_from(D[u], ell)
            want = [2 * r * r + 2 * r + 1 if r <= n - 1 else n * (2 * r + 1) for r in range(ell + 1)]
            reg = (H == want)
            okm &= reg
            n_reg += reg
            m = min(t, ell)
            upto = H[:m + 1] == want[:m + 1]
            n_upto += upto
            # beyond r = t (when t < l): the count rises by n a step, H = n(t + r + 1)
            ext = upto and all(H[r] == n * (t + r + 1) for r in range(t + 1, ell + 1))
            n_ext += ext
            if not reg and len(listing) < 6:
                k = next(r for r in range(ell + 1) if H[r] != want[r])
                listing.append({'knot': u, 'round': t, 'l': ell, 'first_r_differing': k, 'H': H[max(0, k - 3):k + 3],
                                'registered': want[max(0, k - 3):k + 3]})
        oks = True
        for c in range(n):
            H = kwr.counts_from(D[c], smin)
            want = []
            for r in range(smin + 1):
                if r <= (n - 1) // 2:
                    want.append(2 * r * r + 2 * r + 1)
                elif r <= n - 1:
                    want.append(want[-1] + n + 1)
                else:
                    want.append(want[-1] + n)
            oks &= (H == want) and H[n - 1] == n * n
        out[n] = {'rounds': gr.rounds_done, 'made_checked': len(made), 'made_ok_registered_whole_range': okm,
                  'made_registered_whole_range': n_reg, 'made_registered_on_0_to_min_t_l': n_upto,
                  'made_registered_then_n(t+r+1)_beyond_t': n_ext, 'start_ok': oks,
                  'births': sorted(set(gr.births())), 'listing_registered_fails': listing}
        check('control 8 Ring(%d,2) L0: start-knot counts as KD 8.8 (%d start knots)' % (n, n), oks, out[n])
        check('control 8 Ring(%d,2) L0: made-knot counts as KD 8.8 on the whole kept range (%d of %d)'
              % (n, n_reg, len(made)), okm, listing[:2])
        check('control 8 Ring(%d,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (%d of %d)'
              % (n, n_ext, len(made)), n_ext == len(made) and n_upto == len(made), listing[:2])
    return out


# -------------------------------------------------------------------------------------------- checks E, F, R, I, N
def check_E(S):
    """KD 1.6: every distinction shared by a knot made after round 0 has two holders, the first holder and its child;
    holder-graph edges less start-start edges = parent-graph edges."""
    bad = []
    hedges = set()
    for d, hs in enumerate(S.holders):
        if len(hs) >= 2:
            if any(S.made[w] > 0 for w in hs):
                if len(hs) != 2:
                    bad.append(('holders', d, list(hs)))
                    continue
                a, b = sorted(hs, key=lambda w: (S.made[w], w))
                if a not in S.parents[b]:
                    bad.append(('not child', d, a, b))
            for i in range(len(hs)):
                for j in range(i + 1, len(hs)):
                    x, y = sorted((hs[i], hs[j]))
                    if not (S.made[x] == 0 and S.made[y] == 0):
                        hedges.add((x, y))
    pedges = set()
    for x in range(S.n_knots):
        for p in S.parents[x]:
            pedges.add(tuple(sorted((x, p))))
    if hedges != pedges:
        bad.append(('edges', len(hedges - pedges), len(pedges - hedges)))
    return bad


def check_R(gr, G, s):
    """KD 2.8: s(u) = least parent steps to a start knot; under RELEASE with STALL, OFFSHOOT, RETIRE: parents made in
    the round before and s(u) = u's round; for start knots c: B(t - e(c)) <= H(c, t) <= B(t)."""
    S = gr.S
    bad = []
    P = G.ps(list(range(S.n_start)))
    ps_min = np.min(np.vstack([P[c] for c in range(S.n_start)]), axis=0)
    if not np.array_equal(ps_min, s):
        bad.append(('s != least ps', int(np.sum(ps_min != s))))
    law = gr.law
    if law.release == 'RELEASE' and law.treatment in kwr.LEMMA_R_TREATMENTS:
        for x in range(S.n_start, S.n_knots):
            if any(S.made[p] != S.made[x] - 1 for p in S.parents[x]):
                bad.append(('parent not of the round before', x))
                break
            if int(s[x]) != S.made[x]:
                bad.append(('s != round', x, int(s[x]), S.made[x]))
                break
    # sandwich: e(c) within the start
    S0 = kwr.make_start(gr.start_key)
    G0 = kwr.Graphs(S0)
    D0 = G0.hs(list(range(S0.n_start)))
    Dc = G.hs(list(range(S.n_start)))
    fin_s = s[np.isfinite(s)].astype(int)
    tmax = int(fin_s.max()) if len(fin_s) else 0
    B = np.cumsum(np.bincount(fin_s, minlength=tmax + 1))
    for c in range(S.n_start):
        e = int(np.max(D0[c][np.isfinite(D0[c])]))
        H = kwr.counts_from(Dc[c], tmax)
        for t in range(tmax + 1):
            lo = B[t - e] if t - e >= 0 else 0
            if not (lo <= H[t] <= B[t]):
                bad.append(('sandwich', c, t, int(lo), H[t], int(B[t])))
                break
    return bad


def checks():
    out = {'E': [], 'F': [], 'R': [], 'I': [], 'N': []}
    names = list(kwr.named()['named_starts'])
    laws = [('L0', 'RELEASE'), ('L1', 'RELEASE'), ('L3', 'RELEASE'), ('L6', 'RELEASE'), ('L7', 'RELEASE'),
            ('L9', 'RELEASE'), ('L3', 'HOLD'), ('L6', 'HOLD')]
    nE = nF = nR = 0
    for key in names:
        for lab, rel in laws:
            law = kwr.make_law(lab, release=rel)
            T = 40
            gr = kwr.Grown(key, law, T + 10)
            S = gr.S
            badE = check_E(S)
            nE += 1
            if badE:
                out['E'].append({'start': key, 'law': lab, 'release': rel, 'bad': badE[:5]})
            # check F: H after round t and after round t + 10 agree on the kept range (t = min(T, last round))
            t = min(T, gr.rounds_done)
            if gr.rounds_done >= t + 1:
                Nt = gr.n_knots[t]
                Gt = kwr.Graphs(S, Nt)
                st = Gt.steps_from_start(S.n_start)
                mem = gr.members[t]
                if mem:
                    smin = int(min(st[u] for u in mem))
                    rng = kwr.rng_for(key, lab, 'nae', 'b')
                    cand = [u for u in range(S.n_start, Nt) if 4 * st[u] <= smin and u not in set(mem)]
                    src = list(range(S.n_start)) + kwr.sample_sorted(rng, cand, 8)
                    Dt = Gt.hs(src)
                    t2 = min(t + 10, gr.rounds_done)
                    G2 = kwr.Graphs(S, gr.n_knots[t2])
                    D2 = G2.hs(src)
                    for u in src:
                        ell = smin - int(st[u])
                        if ell < 0:
                            continue
                        if kwr.counts_from(Dt[u], ell) != kwr.counts_from(D2[u], ell):
                            out['F'].append({'start': key, 'law': lab, 'release': rel, 'knot': u, 't': t, 't2': t2})
                    nF += 1
            # check R on the whole run
            G = kwr.Graphs(S)
            s = G.steps_from_start(S.n_start)
            badR = check_R(gr, G, s)
            nR += 1
            if badR:
                out['R'].append({'start': key, 'law': lab, 'release': rel, 'bad': badR[:5]})
    check('check E (KD 1.6) on %d named-start runs' % nE, not out['E'], out['E'][:3])
    check('check F (KD 2.6) on %d named-start runs (start knots and 8 made knots each)' % nF, not out['F'], out['F'][:3])
    check('check R (KD 2.8) on %d named-start runs' % nR, not out['R'], out['R'][:3])
    # checks I and N on every stage of at most 20 distinctions of the named starts and of the small census starts
    nI = nN = npairs = 0
    keys = names + ['census:%d' % i for i in kwr.small_census()]
    for key in keys:
        for lab in ('L0', 'L1', 'L3', 'L6', 'L7'):
            gr = kwr.Grown(key, kwr.make_law(lab), 4)
            S = gr.S
            for t in range(0, gr.rounds_done + 1):
                Nt, nd = gr.n_knots[t], gr.n_dist[t]
                if nd > 20:
                    continue
                mem = gr.members[t]
                sc = ge.StageCount(S, Nt, nd)
                A = ge.enumerate_states(S, Nt, nd)
                if sc.Z() != len(A):
                    out['I'].append({'start': key, 'law': lab, 't': t, 'Z': sc.Z(), 'enum': len(A)})
                nI += 1
                for i in range(len(mem)):
                    for j in range(i + 1, len(mem)):
                        u, v = mem[i], mem[j]
                        if not sc.shared[u] or not sc.shared[v]:
                            continue
                        gZ, Nn = sc.pair(u, v)
                        lu, lv = ge.loose_of(S, u, Nt), ge.loose_of(S, v, Nt)
                        Ze, gZe, Ne = ge.enum_pair(S, A, u, v, lu[0], lv[0], Nt)
                        npairs += 1
                        if (gZ, Nn) != (gZe, Ne):
                            out['I'].append({'start': key, 'law': lab, 't': t, 'pair': [u, v], 'gZ': [gZ, gZe],
                                             'N': [Nn, Ne]})
                        # check N: every loose a of u and b of v: kappa(a,b) = gamma/((2^lu-1)(2^lv-1))
                        Du, Dv = 2 ** len(lu) - 1, 2 ** len(lv) - 1
                        want = Fraction(gZe, len(A) * Du * Dv)
                        for a in lu:
                            for b in lv:
                                _, _, ne = ge.enum_pair(S, A, u, v, a, b, Nt)
                                kap = 1 - 2 * Fraction(ne, len(A))
                                if kap != want:
                                    out['N'].append({'start': key, 'law': lab, 't': t, 'pair': [u, v], 'a': a,
                                                     'b': b, 'kappa': str(kap), 'lemma': str(want)})
                        nN += 1
    out['counts'] = {'E': nE, 'F': nF, 'R': nR, 'I_stages': nI, 'I_pairs': npairs, 'N_pairs': nN}
    check('check I: Z, gamma Z, N(a != b) by contraction = enumeration (%d stages, %d pairs)' % (nI, npairs),
          not out['I'], out['I'][:3])
    check('check N (Lemma N) by enumeration on %d member pairs, every loose distinction of each' % nN, not out['N'],
          out['N'][:3])
    return out


def probe_4b(limit_s=600):
    """The run 4b probe (R 18, R 22): the probe case Ring(5,3) under T1, 3 rounds, the identity numbering, every
    choice of the uniform takes enumerated up to 10^5 histories (counts and weights only; the grouping up to renaming
    stalled on this case in the first probe and is not timed); then, within the same 10 minutes, the histories of every
    registered case at the identity numbering, at most 20 s each."""
    import enum4b
    import warnings
    warnings.filterwarnings('ignore')
    t0 = time.time()
    deadline = t0 + limit_s
    out = {'cases': []}
    stars = kwr.start_stars('Ring(5,3)')
    a = time.time()
    h, n = enum4b.enumerate_case(stars, kwr.make_law('T1'), 3, cap=100000, deadline=deadline, keep=False)
    el = time.time() - a
    out['probe'] = {'start': 'Ring(5,3)', 'law': 'T1', 'rounds': 3, 'numbering': 'identity', 'histories': n,
                    'finished': h is not None, 'seconds': round(el, 1), 'seconds_per_history': round(el / max(n, 1), 5),
                    'numberings_registered': 80,
                    'estimate_one_case_all_numberings_seconds_at_least': round(80 * min(n, 100000) * el / max(n, 1)),
                    'grouping_up_to_renaming': 'stalled in the first probe (an exact isomorphism test on this case ran '
                                               'over 10 minutes); not timed'}
    kwr.log('probe 4b: Ring(5,3) T1 identity: %d histories, finished %s, %.1fs' % (n, h is not None, el))
    for key in ('two-knot', 'three-knot', 'Ring(5,3)'):
        st = kwr.start_stars(key)
        nb = 4 * len({d for s_ in st for d in s_})
        for lab in ('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'):
            if time.time() > deadline:
                out['cases'].append({'start': key, 'law': lab, 'histories': None, 'note': 'probe time used up'})
                continue
            a = time.time()
            h, n = enum4b.enumerate_case(st, kwr.make_law(lab), 3, cap=100000, deadline=min(deadline, a + 20),
                                         keep=False)
            out['cases'].append({'start': key, 'law': lab, 'histories': n, 'finished': h is not None,
                                 'seconds': round(time.time() - a, 2), 'numberings': nb})
            kwr.log('probe 4b count: %s %s %d histories finished %s %.1fs' % (key, lab, n, h is not None,
                                                                                time.time() - a))
    per = out['probe']['seconds_per_history']
    est = sum(min(c['histories'], 100000) * c['numberings'] * per for c in out['cases'] if c.get('histories'))
    out['estimate_seconds_one_process_lower_bound'] = round(est)
    out['run_4b_fits_10_minutes'] = est / 6 <= 600 and all(c.get('finished') for c in out['cases'])
    out['seconds'] = round(time.time() - t0, 1)
    return out


def ktest_check():
    """R 23: the two graph forms of the parity knot test (ktest.py) against the fold engine's parity_test (Gaussian
    elimination), on grown structures (the first 120 small census starts under L0, L3, L6, L1, 6 rounds) and 400 drawn
    two-holder structures (seed 2026112501); and the birth method against the direct test there under not-all-equal."""
    import random
    import ktest
    from knots import parity_test, nae_direct
    rng = random.Random(2026112501)
    n = bad = nfail = 0
    structs = []
    for i in kwr.small_census()[:120]:
        for lab in ('L0', 'L3', 'L6', 'L1'):
            structs.append(kwr.Grown('census:%d' % i, kwr.make_law(lab), 6).S)
    for trial in range(400):
        k = rng.randint(2, 9)
        stars = [[] for _ in range(k)]
        d = 0
        for a in range(k):
            for b in range(a + 1, k):
                if rng.random() < 0.4:
                    for _ in range(rng.randint(1, 2)):
                        stars[a].append(d)
                        stars[b].append(d)
                        d += 1
        for a in range(k):
            for _ in range(rng.randint(0, 3)):
                stars[a].append(d)
                d += 1
        stars = [s_ for s_ in stars if s_]
        structs.append(kwr.pm.from_stars(stars))
    for S in structs:
        N, nd = S.n_knots, S.n_distinctions
        pt = parity_test(S)
        A = ktest.parity_ranks_graph(S, N, nd, range(N))
        B = ktest.parity_kernel_graph(S, N, nd, range(N))
        for u in range(N):
            n += 1
            nfail += (not pt['pass'][u])
            if not (A[u] == B[u] == pt['pass'][u]):
                bad += 1
    check('graph forms of the parity test = Gaussian elimination (%d knots, %d failing)' % (n, nfail), bad == 0, bad)
    return {'knots': n, 'failing': nfail, 'disagreements': bad, 'structures': len(structs)}


def main():
    kwr.cap_memory(6)
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    res = {}
    t0 = time.time()
    if which in ('all', 'tests'):
        import test_readings
        ok = test_readings.main()
        res['unit_tests'] = {'ok': ok, 'tests': test_readings.RES}
        check('unit tests of the readings (%d)' % len(test_readings.RES), ok)
    if which in ('all', 'controls'):
        res['controls'] = controls()
    if which in ('all', 'checks'):
        res['checks'] = checks()
        sc = kwr.scratch64()
        five = kwr.five_order()
        marks = {five['order'][k] for k in range(len(five['order'])) if five['in_scratch_64'][k]}
        check('the 64 scratch starts reproduce five_knot_order.json\'s marks (59 five-knot)', marks == {i for i in sc if
              kwr.census()[i]['n'] == 5}, len(marks))
    if which in ('all', 'ktest'):
        res['ktest'] = ktest_check()
    if which in ('all', 'probe'):
        res['probe_4b'] = probe_4b()
    res['results'] = RES
    res['seconds'] = round(time.time() - t0, 1)
    kwr.write_json(kwr.out_path('run0_%s.json' % which), res)
    kwr.log('run 0 (%s): %d checks, %d failed, %.1fs' % (which, len(RES), sum(1 for r in RES.values() if not r['ok']),
                                                         time.time() - t0))


if __name__ == '__main__':
    main()
