"""The tests of a clock and a second part (TD 3 to 6; the claim, section 5), written from the frozen text.

For a run A, a clock Y (a series of returns of parts of two or more members) and j in (0, 1) with four equal periods
after t_j, every second part X (TD 3.1): the bars B(r), B'(r), Ball(r) for r = 1, 2, 3 in that order, the masked run
M(r) where B(r) differs, the test with X barred, X's own and joint knots per period, the lag, and the verdicts of TD 4.6
for C and C-iii.  Readings are numbered in deviations.md (cited "dev n").
"""
from __future__ import annotations

import time
from collections import Counter, defaultdict

import tf_engine as E
import tf_series as Se


# ----------------------------------------------------------------------------------------------- sides and knots
def side_set(S, X, s, upto=None):
    """X and its descendants (FD 4.2, TD 3.2): X and every knot made after round s with a parent among them."""
    out = set(X)
    made, parents = S.made, S.parents
    for x in range(S.n_knots):
        if made[x] > s and (upto is None or made[x] <= upto):
            for p in parents[x]:
                if p in out:
                    out.add(x)
                    break
    return out


def own_joint_by_round(S, Xside, Yside, s, hi):
    """Per round t in (s, hi]: X's own knots (a parent among X's side, none among Y's) and joint knots (TD 3.4)."""
    own, joint = Counter(), Counter()
    for x in range(S.n_knots):
        t = S.made[x]
        if t <= s or t > hi:
            continue
        px = any(p in Xside for p in S.parents[x])
        if not px:
            continue
        py = any(p in Yside for p in S.parents[x])
        if py:
            joint[t] += 1
        else:
            own[t] += 1
    return own, joint


def nd_after(S, t):
    """Number of distinctions after round t (distinctions are named in order of creation)."""
    m = -1
    for u in range(S.n_knots):
        if S.made[u] > t:
            break
        for d in S.places[u]:
            if d > m:
                m = d
    return m + 1


def hk_at(S, u, t):
    h = k = 0
    H, B, made = S.holders, S.bar_at, S.made
    for d in S.places[u]:
        hs = H[d]
        if len(hs) == 1 or made[hs[1]] > t:
            if B[d] <= t:
                k += 1
            else:
                h += 1
    return h, k


# ------------------------------------------------------------------------------------------------------ the trace
class Tracer:
    """FD 5.2's trace of X from round s in one run, with the renaming of FD 5.2, and the steps of FD 5.5 for the way."""

    def __init__(self, run, X, s):
        S = run.S
        self.run, self.S, self.s = run, S, s
        self.side = side_set(S, X, s)
        ns = 0
        while ns < S.n_knots and S.made[ns] <= s:
            ns += 1
        self.ns = ns
        self.nd_s = nd_after(S, s)
        newk = sorted(k for k in self.side if k >= ns)
        self.kmap = {k: ('n', i) for i, k in enumerate(newk)}
        fr = []
        for k in newk:
            for d in S.places[k]:
                if d >= self.nd_s and S.holders[d][0] == k:
                    fr.append(d)
        fr.sort()
        self.fmap = {d: ('f', i) for i, d in enumerate(fr)}

    def kn(self, k):
        if k < self.ns:
            return ('k', k)
        return self.kmap.get(k, ('x',))

    def dn(self, d):
        if d < self.nd_s:
            return ('d', d)
        return self.fmap.get(d, ('y',))

    def round(self, t):
        S, run, side = self.S, self.run, self.side
        rec = run.records[t - 1]
        kn, dn = self.kn, self.dn
        births, dem, flags, takes, fresh = [], [], [], [], []
        for b in rec['births']:
            if all(p in side for p in b['parents']):
                nm = kn(b['id'])
                births.append((nm, b['kind'], tuple(sorted(kn(p) for p in b['parents'])),
                               tuple(sorted(dn(d) for d in b['inputs'])),
                               tuple(sorted(dn(d) for d in b['shared_at_start'])), b['f'], b['usable'], b['barred']))
                dem.append((nm, b['D']))
                flags.append((nm, b['implied']))
                takes.append((nm, b['kind'], tuple(sorted(kn(p) for p in b['parents'])),
                              tuple(sorted(dn(d) for d in b['inputs']))))
                fresh.append((nm, b['f'], b['usable'], b['barred']))
        canc = {tuple(g) for g in rec['cancelled']}
        shortset = set(rec['short'])
        groups = []
        for g in rec['groups']:
            if any(u in side for u in g):
                groups.append((tuple(sorted(kn(u) for u in g)), tuple(g) in canc,
                               tuple(sorted((kn(u), u in shortset) for u in g))))
        owe = tuple(sorted((kn(u), c) for u, c in rec['owe'].items() if u in side))
        mem = []
        live = []
        for u in side:
            if S.made[u] <= t:
                h, k = hk_at(S, u, t)
                if h > 0:
                    mem.append((kn(u), h, k))
                    live.append(u)
        raw = defaultdict(set)
        made = S.made
        for u in live:
            for d in S.places[u]:
                for w in S.holders[d]:
                    if made[w] > t:
                        break
                    if w != u:
                        raw[w].add(u)
        sets = {frozenset(v) for v in raw.values() if len(v) >= 2}
        maxi = [M for M in sets if not any(M < O for O in sets)]
        ms = sorted(tuple(sorted(kn(u) for u in M)) for M in maxi)
        return {'t': t, 'course': (tuple(sorted(births)), tuple(sorted(mem)), tuple(ms)), 'demand': tuple(sorted(dem)),
                'way': {'groups': (tuple(sorted(groups)), owe),
                        'trigger': (bool(rec['stalled']), bool(rec['residual_stall']), tuple(sorted(flags))),
                        'takes': tuple(sorted(takes)), 'fresh': tuple(sorted(fresh))}}

    def rounds(self, lo, hi):
        hi = min(hi, self.run.rounds_done)
        return [self.round(t) for t in range(lo, hi + 1)]


def first_difference(trA, trB, lo, hi):
    """First round in [lo, hi] at which the courses differ (both traces must cover it), the way (FD 5.5), and the first
    round at which the demand differs; and the last round compared."""
    a = {r['t']: r for r in trA}
    b = {r['t']: r for r in trB}
    last = lo - 1
    dem = None
    for t in range(lo, hi + 1):
        if t not in a or t not in b:
            break
        last = t
        if dem is None and a[t]['demand'] != b[t]['demand']:
            dem = t
        if a[t]['course'] != b[t]['course']:
            w1, w2 = a[t]['way'], b[t]['way']
            if w1['groups'] != w2['groups']:
                way = 'a group or owing'
            elif w1['trigger'] != w2['trigger']:
                way = 'a round-wide trigger'
            elif w1['takes'] != w2['takes']:
                way = 'a take'
            elif w1['fresh'] != w2['fresh']:
                way = 'fresh'
            else:
                way = 'met sets or members after the round'
            return t, way, dem, last
    return None, None, dem, last


# ----------------------------------------------------------------------------------------------- comparison runs
class Comparisons:
    """Comparison runs started from run A after a round, cached by what they change (dev 16): a run is grown once
    and its process time is charged to every test that uses it."""

    def __init__(self, A, law, rounds, knot_bound, limit=600.0):
        self.A, self.law = A, law
        self.rounds, self.knot_bound, self.limit = rounds, knot_bound, limit
        self.cache = {}
        self.views = {}

    def view(self, t):
        V = self.views.get(t)
        if V is None:
            V = self.A.S.view(t, with_span=(self.law.knot_law == 'parity'))
            self.views[t] = V
        return V

    def run(self, key, t, bar=(), mask=None, rounds=None):
        """key identifies the run; t the round after which it leaves run A; bar the knots whose usable loose
        distinctions are barred after round t; mask a Mask (masked runs); rounds: grown through (default the bound)."""
        if key in self.cache:
            return self.cache[key]
        V = self.view(t).copy()
        for y in bar:
            for d in V.usable(y):
                V.bar_at[d] = t
        clock = E.Clock(self.limit)
        A = self.A
        prefix = {'records': A.records[:t], 'rosters': A.rosters[:t]}
        ctx = {'mask': mask} if mask is not None else None
        c0 = time.process_time()
        R = E.Run(V, self.law, rounds=min(self.rounds, rounds or self.rounds), knot_bound=self.knot_bound, ctx=ctx,
                  clock=clock, prefix=prefix, keep_rosters=(mask is None))
        sec = time.process_time() - c0
        self.cache[key] = (R, sec)
        return R, sec


# ------------------------------------------------------------------------------------------------------- the classes
def classes_of(S, R, t):
    """FD 1.6: link two parts when a member of one holds a distinction a member of the other holds."""
    n = len(R.parts)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    first = {}
    for u in R.members:
        pu = R.part_of[u]
        for d in S.places[u]:
            q = first.get(d)
            if q is None:
                first[d] = pu
            else:
                a, b = find(q), find(pu)
                if a != b:
                    par[b] = a
    return [find(i) for i in range(n)]


def second_parts(A, t, Pj, limit=8):
    """TD 3.1: parts of the roster after round t, wholly apart from P_j, with a member made after round 0, in order of
    their smallest member name, at most `limit`."""
    R = A.roster(t)
    cls = classes_of(A.S, R, t)
    pj = R.part_of[Pj[0]]
    out = []
    for i, P in enumerate(R.parts):
        if i == pj or cls[i] == cls[pj]:
            continue
        if not any(A.S.made[u] > 0 for u in P):
            continue
        out.append(list(P))
        if len(out) >= limit:
            break
    return out


def origin(A, ser, j, X, Pj, tj):
    """TD 3.3, three facts."""
    S = A.S
    # (a) a common part in their ancestry at an earlier round
    ax, ay = set(), set()
    for u in X:
        ax |= S.ancestors(u) | {u}
    for u in Pj:
        ay |= S.ancestors(u) | {u}
    came_apart = False
    for r in range(0, tj):
        R = A.roster(r)
        px = {R.part_of[z] for z in ax if z in R.part_of}
        py = {R.part_of[z] for z in ay if z in R.part_of}
        if px & py:
            came_apart = True
            break
    # (b) descends from a part given off by Y at a tick t_i <= t_j
    from_off = []
    for i in range(1, j + 1):
        tk = ser['ticks'][i - 1]
        ti = tk['t']
        Ri = A.roster(ti)
        lab = Se.descent_labels(A, ti)
        bits = 0
        for o in tk['off']:
            bits |= 1 << Ri.part_of[o['part'][0]]
        if any(lab.get(u, 0) & bits for u in X):
            from_off.append(i)
    # (c) members of mixed descent: one descended from Y's series before t_j and one not
    lab0 = Se.descent_labels(A, ser['t0'])
    R0 = A.roster(ser['t0'])
    bit0 = 1 << R0.part_of[ser['P0'][0]]
    d = [bool(lab0.get(u, 0) & bit0) for u in X]
    mixed = any(d) and not all(d)
    return {'came_apart': came_apart, 'from_parts_given_off': from_off, 'mixed_descent': mixed,
            'any_descended_from_Y_series': any(d)}


# --------------------------------------------------------------------------------------------- the meeting's class
def meeting(A, law, t_lo, t_hi, Xside, Yside):
    """In run A, the first round t in [t_lo, t_hi] at which a member of X's side and a member of Y's side are joinable
    in the roster read for round t or in its demand roster (replayed), with the common knots linking them, each
    classed as FD 5.7 (dev 19)."""
    S = A.S
    for t in range(t_lo, t_hi + 1):
        for which in ('roster', 'demand'):
            if which == 'roster':
                R = A.roster(t - 1)
                mets = R.metsets
            else:
                V = S.view(t - 1, with_span=(law.knot_law == 'parity'))
                Xs = {x for x in Xside if x < V.n_knots}
                Ys = {y for y in Yside if y < V.n_knots}
                try:
                    rec, _ = E.round_step(V, law, {'capture': True})
                except (E.GuardStop, E.LimitReached):
                    continue
                DR = rec.get('_DR')
                if DR is None:
                    continue
                mets = DR.metsets
                Xs2, Ys2 = set(Xs), set(Ys)
                for b in rec['births']:
                    if any(p in Xs2 for p in b['parents']):
                        Xs2.add(b['id'])
                    if any(p in Ys2 for p in b['parents']):
                        Ys2.add(b['id'])
                Xside_t, Yside_t = Xs2, Ys2
            if which == 'roster':
                Xside_t, Yside_t = Xside, Yside
            links = set()
            for M, com in mets.items():
                if any(u in Xside_t for u in M) and any(u in Yside_t for u in M):
                    links.update(com)
            if links:
                cl = {}
                for w in sorted(links):
                    made = S.made[w] > 0
                    anc = False
                    for M, com in mets.items():
                        if w not in com:
                            continue
                        us = [u for u in M if u in Xside_t]
                        vs = [v for v in M if v in Yside_t]
                        for u in us:
                            for v in vs:
                                if u < S.n_knots and v < S.n_knots:
                                    au, av = S.ancestors(u), S.ancestors(v)
                                    if w in au and w in av and not (w in S.parents[u] and w in S.parents[v]):
                                        anc = True
                    if anc:
                        cl[w] = 'an ancestral common knot (%s)' % ('made' if made else 'a start knot')
                    elif made:
                        cl[w] = 'a knot made by the growth that is no ancestor of both'
                    else:
                        cl[w] = 'a start knot that is no recorded ancestor of both'
                any_made = any(S.made[w] > 0 for w in links)
                return {'round': t, 'roster': which, 'links': sorted(links)[:20], 'n_links': len(links),
                        'classes': Counter(cl.values()), 'made_by_growth': any_made}
    return None


# ------------------------------------------------------------------------------------------------------ one test
def own_per_period(own, ticks_rounds):
    """Own knots in each period (t_a, t_b] for consecutive tick rounds."""
    out = []
    for a, b in zip(ticks_rounds, ticks_rounds[1:]):
        out.append(sum(own[t] for t in range(a + 1, b + 1)))
    return out


def ruled_out_treatment(law):
    return (law.treatment == 'CANCEL-OFFSHOOT' and law.release == 'RELEASE' and law.knot_law == 'nae'
            and not law.fillers and not law.no_offshoot)


def y_chain(run, s, P):
    """The chain of first returns from part P after round s (no filter, least-name convention): its tick rounds."""
    ticks = []
    cur_s, cur_P = s, tuple(P)
    T = run.rounds_done
    while cur_s < T:
        Rs = run.roster(cur_s)
        if cur_P not in Rs.parts:
            break
        i = Rs.parts.index(cur_P)
        lab = Se.descent_labels(run, cur_s)
        bit = 1 << i
        found = None
        for t in range(cur_s + 1, T + 1):
            Rt = run.roster(t)
            hits = []
            alive = False
            for j, Q in enumerate(Rt.parts):
                a = -1
                o = 0
                new = False
                for x in Q:
                    v = lab.get(x, 0)
                    a &= v
                    o |= v
                    if run.S.made[x] > cur_s:
                        new = True
                if o & bit:
                    alive = True
                if a != -1 and (a & bit) and new and len(Q) == len(cur_P) and Se.same_parts(Rs, cur_P, Rt, Q):
                    hits.append(j)
            if hits:
                fj = min(hits, key=lambda j: Rt.parts[j][0])
                found = (t, Rt.parts[fj])
                break
            if not alive:
                break
        if found is None:
            break
        ticks.append(found[0])
        cur_s, cur_P = found
    return ticks


def run_tests(A, law, ser, j, comps, X_limit=8, analysis_clock=None, second_pass=False):
    """All tests (Y, j, X) of one clock and one j.  Returns a list of rows."""
    S = A.S
    ticks = ser['ticks']
    per = ser['periods']
    if j + 4 > len(per) or len(set(per[j:j + 4])) != 1:
        return []
    P = per[j]
    tj = ser['t0'] if j == 0 else ticks[j - 1]['t']
    Pj = ser['P0'] if j == 0 else ticks[j - 1]['part']
    tr = [tj] + [ticks[j + i]['t'] for i in range(4)]       # t_j, t_{j+1}, ..., t_{j+4}
    Xs = second_parts(A, tj, Pj, X_limit)
    rows = []
    Yside_A = side_set(S, Pj, tj)
    for X in Xs:
        c_start = time.process_time()
        used = {}
        row = {'t0': ser['t0'], 'Y_size': ser['size'], 'Y_periods': per, 'j': j, 't_j': tj, 'P_j': Pj,
               'period': P, 'tick_rounds': tr, 'X': X, 'second_pass': second_pass}
        row['origin'] = origin(A, ser, j, X, Pj, tj)
        Xside_A = side_set(S, X, tj)
        ownA, jointA = own_joint_by_round(S, Xside_A, Yside_A, tj, A.rounds_done)
        row['own_A_per_period'] = own_per_period(ownA, tr)
        row['joint_A_per_period'] = own_per_period(jointA, tr)
        row['own_A_by_round'] = {t: ownA[t] for t in sorted(ownA)}
        c = row['own_A_per_period']
        clause1 = len(c) == 4 and len(set(c)) == 1 and c[0] > 0
        row['clause1'] = clause1
        trcA = Tracer(A, X, tj)
        trA_cache = {}

        def trA(lo, hi):
            out = []
            for t in range(lo, min(hi, A.rounds_done) + 1):
                if t not in trA_cache:
                    trA_cache[t] = trcA.round(t)
                out.append(trA_cache[t])
            return out
        bars = []
        c_iii_fail = False
        c_fail = not clause1
        for r in (1, 2, 3):
            if c_iii_fail and c_fail:
                bars.append({'r': r, 'not_run': 'both claims decided failed before this bar (dev 20)'})
                continue
            tb = tr[r]
            tick = ticks[j + r - 1]
            Pr = tick['part']
            bar_knots = tuple(sorted(u for u in Pr if u not in Xside_A))
            bres = {'r': r, 't_bar': tb, 'X_desc_in_barred_part': sum(1 for u in Pr if u in Xside_A)}
            B, sec = comps.run(('B', tb, bar_knots), tb, bar=bar_knots)
            used[('B', tb, bar_knots)] = sec
            bres['B'] = {'rounds': B.rounds_done, 'stop': B.stop, 'guard': B.guard}
            if B.stop == 'limit':
                bres['unfinished'] = True
                bars.append(bres)
                continue
            trcB = Tracer(B, X, tj)
            w2 = tb + 2 * P
            w4 = tb + 4 * P
            tB = trcB.rounds(tb + 1, w4)
            tA = trA(tb + 1, w4)
            d2, way2, dem2, last2 = first_difference(tA, tB, tb + 1, w2)
            d4, way4, dem4, last4 = first_difference(tA, tB, tb + 1, w4)
            bres['course_differs'] = d4
            bres['way'] = way4
            bres['demand_differs'] = dem4
            bres['compared_through'] = last4
            # own and joint knots after the bar
            Yside_B = side_set(B.S, Pj, tj)
            Xside_B = side_set(B.S, X, tj)
            ownB, jointB = own_joint_by_round(B.S, Xside_B, Yside_B, tj, B.rounds_done)
            bres['own_B_after_bar_by_round'] = {t: ownB[t] for t in sorted(ownB) if t > tb}
            bres['joint_B_after_bar'] = sum(v for t, v in jointB.items() if t > tb)
            bres['own_A_after_bar_by_round'] = {t: ownA[t] for t in sorted(ownA) if t > tb}
            e_r = sum(v for t, v in ownB.items() if t > tb)
            bres['e'] = e_r
            late = [t for t, v in ownB.items() if t > w2 and v > 0]
            bres['own_after_lag_rounds'] = sorted(late)
            # the lag (TD 5.2)
            L = None
            for Lc in range(0, 2 * P + 1):
                a = tb + Lc
                if B.rounds_done < a + 2 * P or A.rounds_done < a + 2 * P:
                    break
                if any(ownB[t] > 0 for t in range(a + 1, B.rounds_done + 1)):
                    continue
                p1 = sum(ownA[t] for t in range(a + 1, a + P + 1))
                p2 = sum(ownA[t] for t in range(a + P + 1, a + 2 * P + 1))
                if p1 > 0 and p2 > 0:
                    L = Lc
                    break
            bres['lag'] = L
            if L is not None:
                # which of the three (TD 5.2)
                a = tb + L
                memX = [u for u in Xside_B if B.S.made[u] <= B.rounds_done and hk_at(B.S, u, B.rounds_done)[0] > 0]
                if not memX:
                    bres['how'] = 'ended'
                else:
                    last_rec = B.records[B.rounds_done - 1]
                    waiting = set(last_rec['waiting']) | set(last_rec['held'])
                    if all(u in waiting for u in memX):
                        bres['how'] = 'all members wait'
                    else:
                        bres['how'] = 'closed'
            # C-iii for this bar
            grown2 = min(A.rounds_done, B.rounds_done) >= w2
            if d2 is not None:
                bres['c_iii'] = 'differs'
            elif grown2:
                bres['c_iii'] = 'equal'
                c_iii_fail = True
            else:
                bres['c_iii'] = 'not grown'
            # C for this bar: an own knot later than t_bar + 2 periods decides a failure
            if late:
                c_fail = True
            grown4 = min(A.rounds_done, B.rounds_done) >= w4
            bres['grown_2_periods'] = grown2
            bres['grown_4_periods'] = grown4
            # masked run where B(r) differs
            if d4 is not None:
                Xside_t = {x for x in Xside_A if S.made[x] <= tb}
                mk = E.Mask('XY', Xside_t, set(Pr))
                mkey = ('M', tb, tuple(X), tuple(Pr))
                M, secm = comps.run(mkey, tb, mask=mk, rounds=w4)      # read only through the windows (dev 39)
                used[mkey] = secm
                bres['M'] = {'rounds': M.rounds_done, 'stop': M.stop}
                if M.stop == 'limit':
                    bres['M_unfinished'] = True
                else:
                    trcM = Tracer(M, X, tj)
                    tM = trcM.rounds(tb + 1, w4)
                    hi2 = min(w2, B.rounds_done)
                    dm2, _, _, lastm2 = first_difference(tM, tB, tb + 1, hi2)
                    bres['M_equals_B_2'] = (dm2 is None and lastm2 >= hi2)
                    hi4 = min(w4, B.rounds_done)
                    dm4, _, _, lastm4 = first_difference(tM, tB, tb + 1, hi4)
                    bres['M_equals_B_4'] = (dm4 is None and lastm4 >= hi4)
                    bres['M_differs_from_B_at'] = dm4
                    if d2 is not None and bres['M_equals_B_2']:
                        Yr_side = side_set(S, Pr, tb)
                        bres['meeting'] = meeting(A, law, tb + 1, d2, Xside_A, Yr_side)
            # B'(r): the parts given off at tick j + r (not X's side); Ball(r): every qualifying part
            off_knots = tuple(sorted(u for o in tick['off'] for u in o['part'] if u not in Xside_A))
            if off_knots:
                B2, sec2 = comps.run(('B1', tb, off_knots), tb, bar=off_knots)
                used[('B1', tb, off_knots)] = sec2
                if B2.stop == 'limit':
                    bres["B'"] = 'unfinished'
                else:
                    tB2 = Tracer(B2, X, tj).rounds(tb + 1, w4)
                    dd, ww, _, ll = first_difference(tA, tB2, tb + 1, w4)
                    bres["B'"] = {'course_differs': dd, 'way': ww, 'compared_through': ll}
            else:
                bres["B'"] = 'no parts given off: nothing barred (the same as run A)'
            if tick['copies']:
                all_knots = tuple(sorted(set(bar_knots) | {u for cp in tick['copies'] for u in cp
                                                           if u not in Xside_A}))
                B3, sec3 = comps.run(('B', tb, all_knots), tb, bar=all_knots)
                used[('B', tb, all_knots)] = sec3
                if B3.stop == 'limit':
                    bres['Ball'] = 'unfinished'
                else:
                    tB3 = Tracer(B3, X, tj).rounds(tb + 1, w4)
                    dd, ww, _, ll = first_difference(tA, tB3, tb + 1, w4)
                    bres['Ball'] = {'course_differs': dd, 'way': ww, 'compared_through': ll}
            else:
                bres['Ball'] = 'one qualifying part: the same as B(r)'
            bars.append(bres)
        row['bars'] = bars
        # the test with X barred
        xb = tuple(sorted(X))
        BX, secx = comps.run(('XB', tj, xb), tj, bar=xb)
        used[('XB', tj, xb)] = secx
        if BX.stop == 'limit':
            row['X_barred'] = 'unfinished'
        else:
            row['X_barred'] = {'Y_ticks_A': y_chain(A, tj, Pj), 'Y_ticks_X_barred': y_chain(BX, tj, Pj),
                               'rounds': BX.rounds_done, 'stop': BX.stop}
        # verdicts (TD 4.6)
        row.update(verdicts(row, bars, law, clause1, P))
        # TD 6 (1) who made Y and X; (2) what made the meeting
        y_made = any(S.made[u] > 0 for u in Pj)
        row['who_made'] = ('both made by births after round 0' if y_made
                           else 'one of them is a part of start knots as given')
        mk = []
        for b in bars:
            if b.get('way') == 'a round-wide trigger':
                mk.append('no meeting (a round-wide trigger)')
            elif b.get('meeting'):
                mk.append('knots the growth made' if b['meeting']['made_by_growth'] else 'only start knots')
        row['what_made_meeting'] = mk
        row['seconds_runs'] = round(sum(used.values()), 2)
        row['seconds_analysis'] = round(time.process_time() - c_start - 0.0, 2)
        row['seconds'] = round(row['seconds_runs'] + row['seconds_analysis'], 2)
        if row['seconds'] > comps.limit or any(b.get('unfinished') for b in bars):
            row['unfinished'] = True
            row['verdict_C'] = 'unfinished'
            row['verdict_C_iii'] = 'unfinished'
        rows.append(row)
    return rows


def verdicts(row, bars, law, clause1, P):
    """TD 4.6, bars in the order r = 1, 2, 3 (dev 18, 20)."""
    out = {}
    run_bars = [b for b in bars if 'not_run' not in b and not b.get('unfinished')]
    # C-iii
    fail = any(b.get('c_iii') == 'equal' for b in run_bars)
    held = (len(run_bars) == 3 and all(b.get('c_iii') == 'differs' and b.get('M_equals_B_2') for b in run_bars))
    if fail:
        out['verdict_C_iii'] = 'fails'
    elif held:
        out['verdict_C_iii'] = 'holds'
    else:
        out['verdict_C_iii'] = 'undecided'
        why = []
        for b in bars:
            if 'not_run' in b:
                continue
            if b.get('unfinished'):
                why.append('r=%d unfinished' % b['r'])
            elif b.get('c_iii') == 'not grown':
                why.append('r=%d not grown through two periods' % b['r'])
            elif b.get('c_iii') == 'differs' and not b.get('M_equals_B_2'):
                why.append('r=%d differs, the masked run does not reproduce it (unconfirmed)' % b['r'])
        out['undecided_C_iii_why'] = why
    # C
    late = any(b.get('own_after_lag_rounds') for b in run_bars)
    if not clause1:
        out['verdict_C'] = 'fails'
        out['C_fail_reason'] = 'clause 1'
    elif late:
        out['verdict_C'] = 'fails'
        out['C_fail_reason'] = 'an own knot after the lag'
    else:
        es = {b.get('e') for b in run_bars}
        ok = (len(run_bars) == 3 and all(b.get('grown_4_periods') and b.get('lag') is not None
                                         and b.get('M_equals_B_4') for b in run_bars) and len(es) == 1)
        if ok:
            out['verdict_C'] = 'holds (before the knot test and the numberings)'
        else:
            out['verdict_C'] = 'undecided'
            why = []
            for b in bars:
                if 'not_run' in b or b.get('unfinished'):
                    continue
                if not b.get('grown_4_periods'):
                    why.append('r=%d not grown through four periods' % b['r'])
                if b.get('lag') is None:
                    why.append('r=%d no lag found' % b['r'])
                if not b.get('M_equals_B_4'):
                    why.append('r=%d not through a meeting' % b['r'])
            if len(es) > 1:
                why.append('e differs between the bars')
            out['undecided_C_why'] = why
    if ruled_out_treatment(law):
        out['ruled_out_by_treatment'] = bool(run_bars) and all(b.get('joint_B_after_bar', 1) == 0 for b in run_bars)
    # TD 6 (1) and (2)
    return out
