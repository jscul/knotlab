"""Gate of COPYING-PARTS-20261123-001A: with ticket A's engine, unchanged,
(1) the disclosed counts of two-knot parts on Ring(5, 3) under FLOOR0 after rounds 2 to 10 for the three treatments;
(2) the trace of one two-knot part through two rounds under each treatment (extended to rounds 5 and 6 for the line of
    the join), checked against the pre-registration's first settled statement (deviations.md C14); written to
    trace_two_knot_part.txt.  The same checks, without the printed trace, under FLOOR1 and ONE-FEWER.
Writes gate.json and trace_two_knot_part.txt."""
import os

from cpcommon import E, N_series, OUT, TREATMENTS3, is_two_knot_part, log, part_shape, resources, two_knot_parts, \
    write

DISCLOSED = {'CANCEL-RETIRE': [5, 0, 10, 0, 20, 0, 40, 0, 80],
             'CANCEL-OFFSHOOT': [5, 5, 10, 15, 25, 40, 65, 105, 170],
             'CANCEL-WAIT': [5, 0, 10, 0, 25, 0, 60, 0, 145]}
S0 = 2           # the traced part is a two-knot part after round 2
R = 10


def births_from(rec, members):
    ms = set(members)
    return [b for b in rec['births'] if any(p in ms for p in b['parents'])]


def desc_members(run, s, Y):
    """t -> sorted list of members after round t descending from Y (A-D4)."""
    out = {}
    for t, anc in run.ancestry(s, {u: 0 for u in Y}):
        out[t] = sorted(anc)
    return out


def parts_of(run, t, members):
    ros = run.rosters[t]
    idx = sorted({ros.part_of[x] for x in members})
    return [(ros.parts[j], j) for j in idx]


def trace_and_check(run, law, lines):
    ros = run.rosters[S0]
    tk = two_knot_parts(ros)
    Yi = tk[0]
    Y = ros.parts[Yi]
    a, b = Y
    ms = [(sorted(M), c) for M, c in zip(ros.maxsets, ros.commons) if next(iter(M)) in set(Y)]
    lines.append('=' * 100)
    lines.append('Ring(5, 3) under %s' % law.name())
    lines.append('Traced part Y after round %d: members %s; h, k: %s; met sets %s (common knots %s); past its start: %s'
                 % (S0, list(Y), [(u, ros.h[u], ros.k[u]) for u in Y], [m for m, _ in ms], [list(c) for _, c in ms],
                    ros.part_past_start[Yi]))
    dm = desc_members(run, S0, Y)
    seen_knots = set(Y)        # knots of Y's line (members and the knots they made)
    per_round = {}
    for t in range(S0 + 1, S0 + 5):
        rec = run.records[t - 1]
        prev = dm[t - 1]
        nxt_short = set(run.records[t]['short']) if t < run.rounds_done else set()
        groups = [g for g in rec['groups'] if set(g) & set(prev)]
        canc = [g for g in rec['cancelled'] if set(g) & set(prev)]
        short = [u for u in rec['short'] if u in set(prev)]
        waiting = [u for u in rec['waiting'] if u in set(prev)]
        retired = [u for u in rec['retired'] if u in set(prev)]
        bs = births_from(rec, prev)
        lines.append('-- round %d (members of Y\'s line before it: %s, with h: %s)' % (
            t, prev, [(u, run.rosters[t - 1].h[u]) for u in prev]))
        lines.append('   groups containing them: %s' % groups)
        lines.append('   short: %s   cancelled groups: %s   waiting: %s   retired: %s' % (short, canc, waiting, retired))
        for x in bs:
            seen_knots.add(x['id'])
            lines.append('   birth %d: %-8s parents %-10s taken %-12s D=%d f=%d usable=%d barred=%d   short in round %d: %s'
                         % (x['id'], x['kind'], x['parents'], x['taken'], x['D'], x['f'], x['usable'], x['barred'],
                            t + 1, ('yes' if x['id'] in nxt_short else 'no') if t < run.rounds_done else 'n/a'))
        if not bs:
            lines.append('   no birth from Y\'s line')
        rt = run.rosters[t]
        pp = parts_of(run, t, dm[t])
        desc = []
        for P, j in pp:
            sh = part_shape(rt, P)
            com = [list(c) for M, c in zip(rt.maxsets, rt.commons) if next(iter(M)) in set(P)]
            desc.append('%s h=%s k=%s met sets %s common knots %s%s' % (
                list(P), sh['h'], sh['k'], [sorted(M) for M in rt.maxsets if next(iter(M)) in set(P)], com,
                ' [two-knot part]' if is_two_knot_part(rt, j) else ''))
        lines.append('   after round %d, parts of Y\'s line: %s' % (t, '; '.join(desc) if desc else 'none'))
        per_round[t] = {'groups': groups, 'cancelled': canc, 'short': short, 'waiting': waiting, 'retired': retired,
                        'births': bs, 'parts': [list(P) for P, _ in pp], 'two_knot': [is_two_knot_part(rt, j)
                                                                                     for _, j in pp]}
    # ---- checks against the settled statement (deviations.md C14)
    chk = {}
    r1 = per_round[S0 + 1]['births']
    joins = [x for x in r1 if x['kind'] == 'join']
    offs = [x for x in r1 if x['kind'] == 'offshoot']
    chk['s+1: three births'] = len(r1) == 3
    chk['s+1: one join of both members, D=2, f=1'] = (len(joins) == 1 and sorted(joins[0]['parents']) == [a, b]
                                                      and joins[0]['D'] == 2 and joins[0]['f'] == 1
                                                      and joins[0]['usable'] == 1)
    chk['s+1: one offshoot of each member, D=1, f=2'] = (len(offs) == 2 and sorted(x['parents'][0] for x in offs)
                                                         == [a, b] and all(x['D'] == 1 and x['f'] == 2 and
                                                                           x['usable'] == 2 for x in offs))
    if not (joins and len(offs) == 2):
        return chk, lines
    j = joins[0]['id']
    oa, ob = sorted(x['id'] for x in offs)
    r2 = per_round[S0 + 2]
    chk['s+2: j short'] = j in r2['short']
    chk['s+2: both groups of j cancelled, and only those'] = (sorted(map(tuple, r2['cancelled'])) ==
                                                              sorted([tuple(sorted((j, oa))), tuple(sorted((j, ob)))])
                                                              and sorted(map(tuple, r2['groups'])) ==
                                                              sorted(map(tuple, r2['cancelled'])))
    rt = run.rosters[S0 + 2]
    ok_rel = True
    for o in (oa, ob):
        bo = [x for x in r2['births'] if x['parents'] == [o]]
        ok = len(bo) == 2 and all(x['kind'] == 'offshoot' and x['D'] == 1 and x['f'] == 2 and x['usable'] == 2
                                  for x in bo)
        if ok:
            P = tuple(sorted(x['id'] for x in bo))
            ok = P in rt.parts and is_two_knot_part(rt, rt.parts.index(P))
            if ok:
                i = [k for k, M in enumerate(rt.maxsets) if M == frozenset(P)]
                ok = len(i) == 1 and tuple(rt.commons[i[0]]) == (o,)
        ok_rel = ok_rel and ok
    chk['s+2: each offshoot makes two offshoots, a two-knot part joinable only through it'] = ok_rel
    tr = law.treatment
    jb = [(t, x) for t in range(S0 + 2, S0 + 5) for x in per_round[t]['births'] if j in x['parents']]
    if tr == 'CANCEL-RETIRE':
        chk['retire: j retires in s+2'] = j in r2['retired']
        chk['retire: j makes nothing then or later (to round %d)' % run.rounds_done] = not any(
            j in b['parents'] for rec in run.records[S0 + 1:] for b in rec['births'])
        chk['retire: j not a member after s+2'] = all(j not in run.rosters[t].member_set
                                                      for t in range(S0 + 2, run.rounds_done + 1))
    elif tr == 'CANCEL-OFFSHOOT':
        ok = len(jb) == 1 and jb[0][0] == S0 + 2 and jb[0][1]['kind'] == 'offshoot'
        chk['offshoot: j makes one offshoot in s+2'] = ok
        if ok:
            jo = jb[0][1]['id']
            r_ = run.rosters[S0 + 2]
            chk['offshoot: it is a part of one member after s+2'] = (jo,) in r_.parts
            b3 = [x for x in per_round[S0 + 3]['births'] if x['parents'] == [jo]]
            r3 = run.rosters[S0 + 3]
            P = tuple(sorted(x['id'] for x in b3))
            chk['offshoot: it makes a two-knot part in s+3'] = (len(b3) == 2 and P in r3.parts and
                                                                 is_two_knot_part(r3, r3.parts.index(P)))
    elif tr == 'CANCEL-WAIT':
        chk['wait: j waits in s+2'] = j in r2['waiting']
        r3 = per_round[S0 + 3]
        chk['wait: j in no group in s+3 (asked for nothing), not short'] = (
            not any(j in g for g in run.records[S0 + 2]['groups']) and j not in run.records[S0 + 2]['short'])
        ok = len(jb) == 1 and jb[0][0] == S0 + 3 and jb[0][1]['kind'] == 'offshoot'
        chk['wait: j makes one offshoot in s+3'] = ok
        if ok:
            jo = jb[0][1]['id']
            chk['wait: it is a part of one member after s+3'] = (jo,) in run.rosters[S0 + 3].parts
            b4 = [x for x in per_round[S0 + 4]['births'] if x['parents'] == [jo]]
            r4 = run.rosters[S0 + 4]
            P = tuple(sorted(x['id'] for x in b4))
            chk['wait: it makes a two-knot part in s+4'] = (len(b4) == 2 and P in r4.parts and
                                                            is_two_knot_part(r4, r4.parts.index(P)))
    lines.append('   checks: ' + ', '.join('%s: %s' % (k, 'PASS' if v else 'FAIL') for k, v in chk.items()))
    return chk, lines


def main():
    out = {'counts': {}, 'trace_checks': {}}
    lines = ['Trace of one two-knot part through two rounds (rounds 3 and 4; rounds 5 and 6 added for the line of the',
             'join j), Ring(5, 3), each treatment, RELEASE, parity.  Written by gate.py of COPYING-PARTS-20261123-001A-',
             'E001 with ticket A\'s engine (unchanged).  "short in round t+1" is read from the record of round t+1.',
             'Checks: deviations.md C14 (the pre-registration\'s first settled statement).', '']
    for tr in TREATMENTS3:
        run = E.Run(E.ring(5, 3), E.Law('FLOOR0', tr), R)
        N = N_series(run)
        out['counts'][tr] = {'N_rounds_0_to_10': N, 'rounds_2_to_10': N[2:11], 'disclosed': DISCLOSED[tr],
                             'ok': N[2:11] == DISCLOSED[tr]}
        log('FLOOR0', tr, 'N(2..10) =', N[2:11], 'disclosed', DISCLOSED[tr], 'OK' if N[2:11] == DISCLOSED[tr] else
            'MISMATCH')
        chk, lines = trace_and_check(run, run.law, lines)
        out['trace_checks']['FLOOR0|' + tr] = chk
    lines.append('')
    lines.append('Same checks under FLOOR1 and ONE-FEWER (trace printed too):')
    for ration in ('FLOOR1', 'ONE-FEWER'):
        for tr in TREATMENTS3:
            run = E.Run(E.ring(5, 3), E.Law(ration, tr), R)
            chk, lines = trace_and_check(run, run.law, lines)
            out['trace_checks'][ration + '|' + tr] = chk
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'trace_two_knot_part.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    out['counts_ok'] = all(v['ok'] for v in out['counts'].values())
    out['trace_ok_floor0'] = all(all(v.values()) for k, v in out['trace_checks'].items() if k.startswith('FLOOR0|'))
    out['trace_ok_all_rations'] = all(all(v.values()) for v in out['trace_checks'].values())
    out['gate_pass'] = out['counts_ok'] and out['trace_ok_floor0']
    out['resources'] = resources()
    log('counts', out['counts_ok'], 'trace FLOOR0', out['trace_ok_floor0'], 'all rations', out['trace_ok_all_rations'])
    write('gate.json', out)


if __name__ == '__main__':
    main()
