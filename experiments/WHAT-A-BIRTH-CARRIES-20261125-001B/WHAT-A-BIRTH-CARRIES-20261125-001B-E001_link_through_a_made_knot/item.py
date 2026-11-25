"""One item (a law, a start, a knot law) with every registered reading (BD2 4 to 6, 1.3), as one JSON record."""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import itertools
import time
from collections import Counter

import networkx as nx

import eng
import read
import wbc
from read import View


class Cfg:
    def __init__(self, rounds=7, s_range=(1, 2, 3, 4), knot_test='registered', bars='registered', mult=1,
                 max_tested_pairs=8, with_courses=True, structure_invariants=False, registry=None, courses_all=False):
        self.rounds, self.s_range, self.knot_test, self.bars, self.mult = rounds, s_range, knot_test, bars, mult
        self.max_tested_pairs = max_tested_pairs
        self.with_courses = with_courses
        self.structure_invariants = structure_invariants
        self.registry = registry
        self.courses_all = courses_all


def subsets_of(Y):
    """BD2 4.4: every subset for |Y| <= 4; otherwise Y, the empty set and the |Y| subsets of size |Y| - 1."""
    Y = tuple(Y)
    if len(Y) <= 4:
        out = []
        for r in range(len(Y), -1, -1):
            out += [tuple(c) for c in itertools.combinations(Y, r)]
        return out
    return [Y, ()] + [tuple(y for y in Y if y != z) for z in Y]


def structure_invariant(S):
    """BD2 7.3: the multiset of per-knot labels and a Weisfeiler-Leman hash (4 iterations) of the structure."""
    G = nx.Graph()
    labs = []
    for u in range(S.n_knots):
        h, k = S.hk(u)
        lab = 'K%d|%s|%d|%d|%d|%d' % (S.made[u], S.kind[u], len(S.places[u]), h, k, len(S.parents[u]))
        labs.append(lab)
        G.add_node(('k', u), l=lab)
    for d in range(S.n_distinctions):
        G.add_node(('d', d), l='D%d|%d' % (len(S.holders[d]), S.barred[d]))
        for u in S.holders[d]:
            G.add_edge(('k', u), ('d', d), t='i')
    for u in range(S.n_knots):
        for p in S.parents[u]:
            G.add_edge(('k', u), ('k', p), t='p')
    lab_h = read.hkey(tuple(sorted(Counter(labs).items())))
    wl = nx.weisfeiler_lehman_graph_hash(G, node_attr='l', edge_attr='t', iterations=4)
    return '%d|%d|%s|%s' % (S.n_knots, S.n_distinctions, lab_h, wl)


def course_out(c):
    if c is None:
        return None
    return {'n_knots': c['n_knots'], 'labels': c['labels'], 'edges': c['edges'], 'invariant': wbc.course_invariant(c)}


def reader_counts(v0, s, last):
    """Reader test item 4 (BD2 3), on the run with every member of Y barred: X's births (a parent from X only) at
    which the take, the ration or SHORT-BY changes what the newborn holds or takes from the recorded base law
    (B 20)."""
    run = v0.run
    law = run.law
    c = Counter()
    for t in range(s + 1, last + 1):
        rec = run.recs[t - 1]
        for b in rec['births']:
            if not any(v0.xonly(p) for p in b['parents']):
                continue
            c['births'] += 1
            if b['takes']:
                c['take_changes'] += 1
            if law.ration in eng.RATIONS_OWING and not b['implied']:
                if b['f'] != max(3 - b['p'], 1):
                    c['ration_changes'] += 1
        if law.treatment == 'SHORT-BY':
            for u in rec['short']:
                if v0.xonly(u):
                    c['short_members'] += 1
                    if not rec['act'][u].endswith('keep 0'):
                        c['short_by_changes'] += 1
    return dict(c)


def analyse_item(law, sname, stars, cfg, item_id=None):
    T0 = time.time()
    runA = eng.Run(law, stars=stars, rounds=cfg.rounds, mult=cfg.mult)
    out = {'item': item_id, 'law': law.to_dict(), 'law_name': law.name(), 'start': sname,
           'rounds_read': runA.rounds_read, 'stop': runA.stop, 'guard': runA.guard, 'knots': runA.S.n_knots,
           'peaks': runA.peaks(), 's': {}, 'pairs': [], 'tested_pairs': 0, 'untested_differing_pairs': 0}
    t0 = time.time()
    if cfg.knot_test == 'none':
        out['knot_test_A'] = None
    else:
        out['knot_test_A'] = read.knot_test_full(runA)
    out['sec_knot_test_A'] = round(time.time() - t0, 3)
    if cfg.structure_invariants:
        out['structure_invariants'] = [structure_invariant(S) for S in runA.snaps]
    keysA = read.Keys(runA)
    tested = 0
    reader = Counter()
    for s in cfg.s_range:
        if runA.rounds_read < s:
            out['s'][s] = {'reached': False}
            continue
        if runA.rounds_read > s:
            R_s = runA.recs[s]['roster']
        else:
            try:
                R_s = eng.build_roster(runA.snaps[s], eng.live_members(runA.snaps[s]), 'parts', eng.Guard(cfg.mult))
            except eng.GuardStop as g:
                out['s'][s] = {'reached': True, 'parts': None, 'guard': [g.what, g.value]}
                continue
        parts = eng.roster_parts(R_s) if R_s.parts is None else R_s.parts
        member_part = {u: i for i, P in enumerate(parts) for u in P}
        cls = eng.classes_of_parts(runA.snaps[s], parts)
        bitsA = read.desc_bits(runA, s, member_part)
        meetA = read.first_meetings(runA, s, bitsA)
        pairs = [(i, j) for i in range(len(parts)) for j in range(len(parts)) if i != j and cls[i] != cls[j]]
        pairs.sort(key=lambda ij: (min(parts[ij[0]]), min(parts[ij[1]])))
        out['s'][s] = {'reached': True, 'parts': [list(P) for P in parts], 'n_ordered_pairs': len(pairs),
                       'no_meeting_pairs': [], 'last_round_read': runA.rounds_read}
        idx_cache, anc_cache = {}, {}
        sym_cache = {}

        def idx_anc(run, bits, t, cache_key):
            k = (cache_key, t)
            if k not in idx_cache:
                idx_cache[k] = read.RoundIndex(run.recs[t - 1], bits)
                anc_cache[k] = read.ancestor_bits(run.snaps[t])
            return idx_cache[k], anc_cache[k]

        meet_pairs = []
        for i, j in pairs:
            m = meetA.get((min(i, j), max(i, j)))
            if m is None:
                out['s'][s]['no_meeting_pairs'].append([i, j])
            else:
                meet_pairs.append((i, j, m))
        # the bars on Y (BD2 4.4), for each Y of a pair with a meeting in run A (B 12)
        bar_runs = {}
        for j in sorted({j for _, j, _ in meet_pairs}):
            Y = parts[j]
            runs = {}
            for A in subsets_of(Y):
                if cfg.bars == 'A0' and A not in (Y, ()):
                    continue
                if A == Y:
                    runs[A] = (runA, keysA, bitsA, meetA)
                else:
                    r = eng.Run(law, base=runA, base_round=s, bar=[y for y in Y if y not in A], rounds=cfg.rounds,
                                mult=cfg.mult)
                    k = read.Keys(r, base=keysA)
                    b = read.desc_bits(r, s, member_part)
                    runs[A] = (r, k, b, read.first_meetings(r, s, b))
            bar_runs[j] = runs
        for i, j, (t, how) in meet_pairs:
            X, Y = parts[i], parts[j]
            vA = View(runA, keysA, bitsA, i, j, s, X, Y)
            ia, aa = idx_anc(runA, bitsA, t, 'A')
            L = read.linking(vA, t, ia, aa)
            rec = {'s': s, 'X': list(X), 'Y': list(Y), 'X_part': i, 'Y_part': j, 'meeting_round': t,
                   'meeting_how': how}
            rec.update(L)
            runs = bar_runs[j]
            r0, k0, b0, m0 = runs[()]
            v0 = View(r0, k0, b0, i, j, s, X, Y)
            last = min(runA.rounds_read, r0.rounds_read)
            mt0 = m0.get((min(i, j), max(i, j)))
            rec['barred_run'] = {'rounds_read': r0.rounds_read, 'stop': r0.stop, 'guard': r0.guard,
                                 'meeting_round': mt0[0] if mt0 else None}
            rec['last_round_both_read'] = last
            td, ca, c0 = read.first_course_difference(vA, v0, s, last)
            rec['course_differs'] = td is not None
            rec['course_first_differs_round'] = td
            if (L['strict'] or cfg.courses_all) and cfg.with_courses:
                rec['course_A'] = course_out(ca)
                rec['course_barred'] = course_out(c0)
            elif ca is not None:
                rec['course_A_invariant'] = wbc.course_invariant(ca)
                rec['course_barred_invariant'] = wbc.course_invariant(c0) if c0 is not None else None
            if cfg.registry is not None and ca is not None:
                rec['course_class_A'] = cfg.registry.classify(ca)
                rec['course_class_barred'] = cfg.registry.classify(c0) if c0 is not None else None
            if td is not None:
                fd = read.attribution(v0, vA, s, last)
                rec['attribution'] = fd
                rec['attribution_accepted'] = bool(fd and fd['class'] == 'through the meeting')
                rec['meets_against_does_not_meet'] = mt0 is None
                rec['y_side_knots_first_differing_demand'] = y_side_demand(v0, vA, s, last)
            if L['strict']:
                rc = reader_counts(v0, s, last)
                for k_, v_ in rc.items():
                    reader[k_] += v_
                if cfg.bars != 'A0':
                    rec['subsets'] = subset_readings(runs, i, j, s, X, Y, law, cfg, idx_anc)
                    rec['checks'] = {
                        'start_knot_holds_linking_distinction': L['start_knot_holds_linking_distinction'],
                        'start_knot_in_linking_set_of_a_barred_run': rec['subsets']['start_knot_in_a_barred_link'],
                        'symmetry_exchanging_X_Y_fixing_linking_knots': sym_cached(
                            sym_cache, runA.snaps[s], X, Y, [x['knot'] for x in L['linking'] if x['made'] <= s]),
                        'linking_knots_made_after_s': [x['knot'] for x in L['linking'] if x['made'] > s],
                        'ancestry': {x['knot']: x['ancestry'] for x in L['linking']}}
                if td is not None:
                    do_kt = cfg.knot_test != 'none' and tested < cfg.max_tested_pairs
                    rec['lasting'] = lasting(runA, keysA, r0, k0, member_part, i, j, s, X, Y, td, cfg, do_kt)
                    if do_kt:
                        tested += 1
                        rec['knot_test_barred'] = read.knot_test_barred(r0, s, cfg.knot_test == 'full')
                        rec['knot_test_lasting'] = rec['lasting'].pop('_kt', None)
                    elif cfg.knot_test != 'none':
                        out['untested_differing_pairs'] += 1
                        rec['knot_test_barred'] = 'not run: undecided, knot test not run'
            out['pairs'].append(rec)
        del bar_runs
    out['tested_pairs'] = tested
    out['reader_item4'] = dict(reader)
    out['seconds'] = round(time.time() - T0, 3)
    return out


def sym_cached(cache, S, X, Y, fixed):
    k = (frozenset((tuple(X), tuple(Y))), tuple(sorted(fixed)))
    if k not in cache:
        t = time.time()
        cache[k] = read.symmetry_exchanging(S, X, Y, fixed)
        cache[k]['sec'] = round(time.time() - t, 3)
    return cache[k]


def y_side_demand(v0, vA, s, last):
    """BD2 6.9: at the first differing demand entry (step 6), the partners of Y's descent with no answer in the other
    run, with their kind, parents and round (from both runs)."""
    for t in range(s + 1, last + 1):
        E0, EA = read.values(v0, t), read.values(vA, t)
        for e0, ea in wbc.align(E0, EA):
            k = (e0 or ea)['kind']
            if k != 'demand':
                continue
            if e0 is not None and ea is not None and e0['value'] == ea['value']:
                continue
            p0 = {x[0]: x for x in (e0['part'] if e0 else [])}
            pa = {x[0]: x for x in (ea['part'] if ea else [])}
            out = []
            for which, P, Q, v in (('barred run', p0, pa, v0), ('run A', pa, p0, vA)):
                inv = {key: u for u, key in enumerate(v.keys.k)}
                for key, x in P.items():
                    if key in Q or x[1] not in ('Y only', 'both'):
                        continue
                    u = inv[key]
                    S = v.run.snaps[t]
                    out.append({'run': which, 'knot': u, 'descent': x[1], 'kind': S.kind[u],
                                'parents': list(S.parents[u]), 'round': S.made[u]})
            return {'round': t, 'pos': list((e0 or ea)['pos']), 'value_barred': e0 and e0['value'],
                    'value_A': ea and ea['value'], 'y_side': out}
    return None


def subset_readings(runs, i, j, s, X, Y, law, cfg, idx_anc):
    """BD2 6.4 to 6.6 and the barred-run half of check 6.8 (b), over the subsets' runs of one pair."""
    subs = list(runs)
    views = []
    meets = []
    start_in_link = False
    for A in subs:
        r, k, b, m = runs[A]
        v = View(r, k, b, i, j, s, X, Y)
        views.append(v)
        mt = m.get((min(i, j), max(i, j)))
        info = {'A': list(A), 'rounds_read': r.rounds_read, 'stop': r.stop, 'meeting_round': mt[0] if mt else None}
        if mt is not None:
            ix, an = idx_anc(r, b, mt[0], ('bar', j, A))
            L = read.linking(v, mt[0], ix, an)
            info['strict'] = L['strict']
            info['link_verdict'] = L['link_verdict']
            if len(A) < len(Y) and any(x['made'] == 0 for x in L['linking']):
                start_in_link = True
        else:
            info['strict'] = False
            info['link_verdict'] = 'no meeting'
        meets.append(info)
    last = min(v.run.rounds_read for v in views)
    courses = [read.course(v, last) for v in views]
    cls = []
    reps = []
    for c in courses:
        for ci, rc in enumerate(reps):
            if read.same_course(c, rc):
                cls.append(ci)
                break
        else:
            cls.append(len(reps))
            reps.append(c)
    for info, c in zip(meets, cls):
        info['course_class'] = c
    how_many = []
    which = []
    for a, b in itertools.combinations(range(len(subs)), 2):
        A, B = subs[a], subs[b]
        if len(A) != len(B):
            if A and B and meets[a]['strict'] and meets[b]['strict'] and cls[a] != cls[b]:
                how_many.append([list(A), list(B)])
        elif A != B and meets[a]['meeting_round'] is not None and meets[b]['meeting_round'] is not None \
                and cls[a] != cls[b]:
            which.append([list(A), list(B)])
    out = {'subsets': meets, 'compared_through_round': last, 'n_classes': len(reps),
           'classes_by_size': sorted({(len(A), c) for A, c in zip(subs, cls)}),
           'how_many': how_many, 'which_at_equal_number': which,
           'no_meeting_subsets': [list(A) for A, mi in zip(subs, meets) if mi['meeting_round'] is None],
           'start_knot_in_a_barred_link': start_in_link}
    if len(reps) > 1:
        out['m'] = read.m_reading(views, cls, s, last)
        v = VALUES_AT_ONE_BIRTH[law_value(law)]
        out['more_than_v_classes'] = len(reps) > v if v is not None else False
    else:
        out['m'] = {'verdict': 'no difference', 'm': 0, 'classes': 1}
    return out


VALUES_AT_ONE_BIRTH = {'1': 1, '2': 2, '3': 3, 'h(u) + 1': None, 'unbounded': None}
_ORDER = ['1', '2', '3', 'h(u) + 1', 'unbounded']


def law_value(law):
    vals = []
    vals.append('2' if law.take in ('MET-SOLE', 'STEPS1-SOLE', 'STEPS2-SOLE') else '1')
    r = law.ration
    vals.append({'FLOOR1': '2', 'CAP-3': '3', 'ORD': 'unbounded', 'PARENT-OWING': 'unbounded',
                 'PARENT-OWING-CAP3': '2', 'PARENT-OWING-CAP4': '3'}.get(r, 'unbounded'))
    vals.append('h(u) + 1' if law.treatment == 'SHORT-BY' else '1')
    return max(vals, key=_ORDER.index)


def lasting(runA, keysA, r0, k0, member_part, i, j, s, X, Y, td, cfg, do_kt):
    """BD2 6.7: both runs rerun from round t_d with every member not from X only barred, to round t_d + 2, the same
    knot bound; it lasts when the rosters descended from X only are not the same in rounds t_d + 1 and t_d + 2."""
    out = {'t_d': td}
    reruns = []
    for base, keys in ((runA, keysA), (r0, k0)):
        if base.rounds_read < td:
            return {'t_d': td, 'verdict': 'undecided', 'why': 'a run did not read round t_d'}
        bits = read.desc_bits(base, s, member_part)
        vb = View(base, keys, bits, i, j, s, X, Y)
        Sd = base.snaps[td]
        bar = [u for u, h, k in eng.live_members(Sd) if not vb.xonly(u)]
        rr = eng.Run(base.law, base=base, base_round=td, bar=bar, rounds=td + 2, mult=cfg.mult)
        reruns.append(rr)
    out['reruns'] = [{'rounds_read': rr.rounds_read, 'stop': rr.stop, 'guard': rr.guard} for rr in reruns]
    if any(rr.rounds_read < td + 2 for rr in reruns):
        out['verdict'] = 'undecided'
        out['why'] = 'a rerun stopped first'
    else:
        diff = []
        for r in (td + 1, td + 2):
            vs = []
            for rr in reruns:
                bits = read.desc_bits(rr, s, member_part)
                vs.append(View(rr, None, bits, i, j, s, X, Y))
            R1, R2 = read.xonly_roster(vs[0], r), read.xonly_roster(vs[1], r)
            diff.append(not read.rosters_same(R1, R2))
        out['rosters_differ'] = {td + 1: diff[0], td + 2: diff[1]}
        out['verdict'] = 'lasts' if all(diff) else 'does not last'
    if do_kt:
        out['_kt'] = [read.knot_test_barred(rr, td, cfg.knot_test == 'full') for rr in reruns]
    return out
