"""Replays of the disagreements with the disclosed prototype numbers, birth by birth (P, "Disagreements": parents,
inputs, holders of each input, fresh count, tie classes, descents).  Writes replays.json.

usage: python -B replay.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402
import run2  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def births_listing(run, X, Y, s, pat, upto, knot_law):
    """Every birth of rounds s+1..upto with a parent among pat and its descendants, in raw names."""
    out = []
    for t in range(s + 1, upto + 1):
        Sb, Sa = run.snap[t - 1], run.snap[t]
        side = P.side_of(Sa, pat, s)
        desc = mc.descent_map(Sa, X, Y, s)
        T = mc.ties(Sa, knot_law, seed=t)
        for b in run.records[t - 1]['births']:
            if not any(p in side for p in b['parents']):
                continue
            out.append({'round': t, 'knot': b['id'], 'kind': b['kind'], 'parents': b['parents'],
                        'parents\' descents': [desc.get(p) for p in b['parents']],
                        'inputs': b['inputs'], 'holders of each input at the start of the round':
                        {str(d): list(Sb.holders[d]) for d in b['inputs']}, 'taken by the rule': b['rule_takes'],
                        'fresh count': b['f'], 'fresh': b['fresh'], 'implied': b['implied'],
                        'its descent': desc.get(b['id']),
                        'tie classes of its inputs and fresh distinctions after the round':
                        [c for c in T.classes if set(c) & set(b['inputs'] + b['fresh'])]})
    return out


def trace_rows(run, pat, s, upto):
    tr = [r for r in P.trace(run, pat, s, min(upto, run.rounds_done)) if r['t'] <= upto]
    return [{'t': r['t'], 'births (name, kind, parents, inputs, shared at start, fresh, usable, barred)':
             [list(map(str, b)) for b in r['births']]} for r in tr]


def course_disagreement(kl):
    """PO3/PO4: Y's course in ystart-one-2 under CAP-3(CANCEL-OFFSHOOT), MET(NEWEST)."""
    d = mc.design('ystart-one-2')
    law = mc.make_law('CAP-3(OFFSHOOT)', 'MET', 'NEWEST', kl)
    A = mc.grow(d, law)
    v = P.RunView(A)
    s = d.s
    BX = mc.run_from_state(A, s, P.bar_part(A.snap[s], d.X))
    B1 = mc.run_from_state(A, s, P.bar_part(A.snap[s], d.Y))
    M = P.masked_run(v, s, d.X, d.Y, 'XY')
    MY1 = P.masked_run(v, s, d.Y, d.X, 'ISO')
    T = min(A.rounds_done, B1.rounds_done, BX.rounds_done, M.rounds_done)
    cy, _, _ = run2.course(A, BX, d.Y, s, T)
    c_T, _, _ = run2.course(M, BX, d.Y, s, T)
    Tm = min(M.rounds_done, BX.rounds_done)
    c_all, _, _ = run2.course(M, BX, d.Y, s, Tm)
    c_y1, _, _ = run2.course(MY1, BX, d.Y, s, min(MY1.rounds_done, BX.rounds_done))
    return {'law': law.name(), 'rounds reached (A, B(i), B_X, M, M\'_Y)': [A.rounds_done, B1.rounds_done,
                                                                         BX.rounds_done, M.rounds_done,
                                                                         MY1.rounds_done],
            'A stopped': {'stop': A.stop, 'guard': A.guard}, 'T': T,
            'Y course, A against B_X through T': cy,
            'Y course, M against B_X through T (D 7.1: every comparison at T)': c_T,
            'Y course, M against B_X through the last round both reached': c_all,
            "Y course, M'_Y against B_X through the last round both reached": c_y1,
            'reading at T': 'through a meeting' if c_T['differs'] is None else 'not through a meeting',
            'reading through M and B_X\'s own last round': 'through a meeting' if c_all['differs'] is None else (
                'through a third part' if c_y1['differs'] is None else 'unconfirmed'),
            'trace of Y, run A': trace_rows(A, d.Y, s, A.rounds_done),
            'trace of Y, B_X': trace_rows(BX, d.Y, s, BX.rounds_done),
            'trace of Y, M': trace_rows(M, d.Y, s, M.rounds_done),
            'births of Y and its descendants, B_X': births_listing(BX, d.X, d.Y, s, d.Y, BX.rounds_done, kl),
            'births of Y and its descendants, M': births_listing(M, d.X, d.Y, s, d.Y, M.rounds_done, kl)}


def census_disagreement():
    """P13: the runs in which a part the same as made-4's, made-5's or made-6's Y is counted, with the part and the
    reference, members with h and k, the maximal met sets, the members' births."""
    out = {}
    for m in ('made-4', 'made-5', 'made-6'):
        rows = []
        for base in mc.BASES_CAP3 + mc.BASES_FBP:
            for take in ('MET', 'STEPS-1'):
                for ch in mc.RULES:
                    law = mc.make_law(base, take, ch, 'parity')
                    dm = mc.design(m)
                    Am, vm, refm = run2.run_design(dm, law, 'parity')
                    if refm is None:
                        continue
                    for name in mc.DESIGNS_MADE:
                        d = mc.design(name)
                        A, v, ref = run2.run_design(d, law, 'parity')
                        for t in range(d.s + 1, A.rounds_done + 1):
                            S = A.snap[t]
                            R = v.roster(t)
                            desc = mc.descent_map(S, d.X, d.Y, d.s)
                            parts = mc.form_reading(refm, S, R, desc)
                            if not parts:
                                continue
                            p_ = parts[0]
                            Rs = vm.roster(dm.s)
                            Ss = Am.snap[dm.s]
                            rows.append({
                                'law': law.name(), 'design': name, 'first round': t, 'parts': len(parts),
                                'descents of the first part': p_['descents'],
                                'the part (knot, h, k, places, parents, kind, descent)': [
                                    (u, R.h[u], R.k[u], S.places[u], list(S.parents[u]), S.kind[u], desc.get(u))
                                    for u in p_['part']],
                                'its maximal met sets': [sorted(M_) for M_ in R.maxsets if set(M_) & set(p_['part'])],
                                'the reference: %s\'s Y after round %d (knot, h, k, places, parents)' % (m, dm.s): [
                                    (u, Rs.h[u], Rs.k[u], Ss.places[u], list(Ss.parents[u])) for u in refm.members],
                                'the reference\'s maximal met sets': [sorted(M_) for M_ in Rs.maxsets
                                                                      if set(M_) & set(refm.members)],
                                'births of the part\'s members': [b for b in births_listing(
                                    A, d.X, d.Y, d.s, d.X + d.Y, t, 'parity') if b['knot'] in p_['part']]})
                            break
        out[m] = {'runs': len(rows), 'rows': rows}
    return out


def census_floor1():
    """P13 again, with every law's parts compared with each member's Y after round s under COPY-LAW(t) with the same
    treatment, taking rule, rule and knot law (the other reading of which run "Y as it was after round s" comes from)."""
    from collections import Counter
    anyc, xo, n = Counter(), Counter(), 0
    for base in mc.BASES_CAP3 + mc.BASES_FBP:
        t = base.split('(')[1]
        for take in ('MET', 'STEPS-1'):
            for ch in mc.RULES:
                law = mc.make_law(base, take, ch, 'parity')
                lawF = mc.make_law('COPY-LAW(' + t, take, ch, 'parity')
                refs = {m: run2.run_design(mc.design(m), lawF, 'parity')[2] for m in mc.CLASS_MADE}
                for name in mc.DESIGNS_MADE:
                    d = mc.design(name)
                    A, v, ref = run2.run_design(d, law, 'parity')
                    n += 1
                    hit, hx = set(), set()
                    for tt in range(d.s + 1, A.rounds_done + 1):
                        S = A.snap[tt]
                        desc = mc.descent_map(S, d.X, d.Y, d.s)
                        for m, rf in refs.items():
                            ps = mc.form_reading(rf, S, v.roster(tt), desc)
                            if ps:
                                hit.add(m)
                            if any(p_['descent'] == 'X only' for p_ in ps):
                                hx.add(m)
                    anyc.update(hit)
                    xo.update(hx)
    return {'runs': n, 'members made': dict(anyc), 'by descent from X only': dict(xo)}


def guard_listing(n_hist=3):
    """P8b's disclosure (the fold engine's guard stopping most drawn histories of made-4 to made-6 under
    CAP-3(CANCEL-OFFSHOOT)): the first drawn histories of run 4, drawn as run 4 draws them (the same generator, four
    rounds each), round by round: knots, members, the roster's joinable pairs and largest met set against the guard,
    births; and whether the next round (s + 5) would meet the guard or pass 500 knots."""
    import random
    import run4
    out = {'guard limits': dict(pm.GUARD), 'knot bound': mc.KNOT_BOUND}
    for name in ('made-4', 'made-5', 'made-6'):
        d = mc.design(name)
        law = run4.law_every('CAP-3(OFFSHOOT)', 'parity')
        label = run4.law_label(law)
        pre = mc.grow(d.start(), law, rounds=d.s)
        rnd = random.Random('2026112502|%s|%s' % (name, label))
        hs = []
        for h in range(n_hist):
            S = pre.snap[d.s]
            rows = []
            for t in range(d.s, d.s + 4):
                if S.n_knots > mc.KNOT_BOUND:
                    rows.append({'round': t + 1, 'not grown': 'past 500 knots after round %d' % t})
                    break
                try:
                    T, rec, pk = run4.random_child(S, law, rnd)
                except pm.GuardStop as g:
                    rows.append({'round': t + 1, 'guard': str(g)})
                    break
                R = pm.roster_of(T.copy(), law)
                rows.append({'round': t + 1, 'knots': T.n_knots, 'members': len(R.members), 'births': len(rec['births']),
                             'roster pairs': R.n_pairs, 'largest met set': max([len(M) for M in R.maxsets] or [0]),
                             'demand groups': rec.get('demand_groups')})
                S = T
            hs.append(rows)
        out[name] = hs
    return out


def main():
    C.cap_memory(6)
    out = {'PO3, PO4: Y\'s course confirmed through a meeting (359 here, 357 disclosed)':
           {kl: course_disagreement(kl) for kl in ('parity', 'nae')},
           'P13: the census of the made family (made-4 15, made-5 7, made-6 34 here; 13, 6, 11 disclosed)':
           census_disagreement(),
           'P13 with every member\'s Y taken under COPY-LAW(t) (the same treatment, taking rule, rule)': census_floor1(),
           'P8b: the guard and the first drawn histories of made-4 to made-6 under CAP-3(CANCEL-OFFSHOOT)':
           guard_listing()}
    C.write_json('replays.json', out)


if __name__ == '__main__':
    main()
