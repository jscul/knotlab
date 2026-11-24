"""Run A1: Ring(n, 3), n = 3..16, under the two added rules (R = 12), the three added rules (R = 20) and ordinary
growth (R = 8), cut off past 6,000 knots.  Evidence for P1, P2, P3, P4, P5 and G (ordinary runs).  Writes a1.json."""
import networkx as nx

from common import E, log, resources, write

LAWS = [('two', E.TWO_ADDED, 12), ('three', E.THREE_ADDED, 20), ('ordinary', E.ORDINARY, 8)]
CAP = 6000


def brief_returns(run):
    return [{k: r[k] for k in ('s', 't', 'period', 'part_size', 'n_off', 'off_sizes')} for r in run.find_returns()]


def is_one_cycle(members, msets, n):
    if len(msets) != n or any(len(M) != 2 for M in msets):
        return False
    G = nx.Graph()
    G.add_nodes_from(members)
    for M in msets:
        G.add_edge(*sorted(M))
    return G.number_of_edges() == n and nx.is_connected(G) and all(d == 2 for _, d in G.degree())


def part_info(ros, members):
    ms = [M for M in ros.maxsets if next(iter(M)) in set(members)]
    return {'n': len(members), 'h': sorted(ros.h[u] for u in members), 'k': sorted(ros.k[u] for u in members),
            'metset_sizes': sorted(len(M) for M in ms)}


# ------------------------------------------------------------------------------------------------- P1, P2

def p1_p2(run, n):
    start = run.rosters[0]
    p1, p2 = [], []
    for t in range(2, 13, 2):
        if t > run.rounds_done:
            p1.append({'t': t, 'ok': False, 'why': 'round not run'})
            continue
        ros = run.rosters[t]
        waited = tuple(sorted(run.records[t - 1]['waiting']))
        row = {'t': t, 'past_start': ros.past_start, 'n_waited': len(waited), 'is_part': waited in ros.parts}
        if row['is_part']:
            j = ros.parts.index(waited)
            ms = ros.part_maxsets(j)
            row.update(part_info(ros, waited))
            row['one_cycle'] = is_one_cycle(waited, ms, n)
            row['same_as_start'] = run.cache.same(ros, waited, start, None)
            row['ok'] = (ros.past_start and len(waited) == n and set(row['h']) == {3} and set(row['k']) == {0}
                         and row['one_cycle'] and row['same_as_start'])
        else:
            row['ok'] = False
        p1.append(row)
        # P2: descendants of that part after round t + 2
        if t + 2 > run.rounds_done:
            p2.append({'t': t, 'checked': False, 'why': 't + 2 > R (deviations D8)'})
            continue
        if not row['is_part']:
            p2.append({'t': t, 'checked': True, 'ok': False, 'why': 'waited knots do not form a part'})
            continue
        tr = run.track(t, waited)
        e = tr[2]
        rt = run.rosters[t + 2]
        whole = e['whole_parts']
        same_idx = [j for j in whole if run.cache.same(ros, waited, rt, rt.parts[j])]
        others = [j for j in whole if j not in same_idx[:1]]
        oinfo = [part_info(rt, rt.parts[j]) for j in others]
        others_ok = all(o['n'] == 2 and o['h'] == [2, 2] and o['metset_sizes'] == [2] for o in oinfo)
        q = {'t': t, 'checked': True, 'n_parts': len(e['parts']), 'all_whole': e['parts'] == whole,
             'n_same': len(same_idx), 'n_others': len(others), 'others_ok': others_ok,
             'other_shapes': sorted({(o['n'], tuple(o['h']), tuple(o['k']), tuple(o['metset_sizes'])) for o in oinfo})}
        q['ok'] = (q['all_whole'] and len(e['parts']) == n + 1 and len(same_idx) >= 1 and len(others) == n
                   and others_ok)
        q['other_shapes'] = [list(map(list, x[1:])) + [x[0]] for x in q['other_shapes']]
        p2.append(q)
    return p1, p2


# ------------------------------------------------------------------------------------------------------ P3

def follow(run, t0, members, smax):
    """Descendants of a part, s rounds after t0: number of parts, members, and the sub-roster's identity."""
    out = []
    tr = run.track(t0, members)
    for e in tr[:smax + 1]:
        t = e['t']
        out.append({'s': t - t0, 't': t, 'n_parts': len(e['parts']), 'n_members': len(e['members']),
                    'members': tuple(e['members'])})
    return out


def compare_population(run, pop, smax, R):
    """pop: list of (t0, part members).  For each s: all followed descendant sub-rosters the same; s + 2 members."""
    by_s = {}
    for t0, P in pop:
        for e in follow(run, t0, P, min(smax, R - t0)):
            by_s.setdefault(e['s'], []).append((e['t'], e))
    rows = []
    for s in sorted(by_s):
        items = by_s[s]
        t_ref, ref = items[0]
        same_all = all(run.cache.same(run.rosters[t_ref], ref['members'], run.rosters[t], e['members'])
                       for t, e in items[1:])
        counts = sorted({e['n_members'] for _, e in items})
        nparts = sorted({e['n_parts'] for _, e in items})
        rows.append({'s': s, 'n_followed': len(items), 'all_same': same_all, 'member_counts': counts,
                     'part_counts': nparts, 'count_ok': counts == [s + 2], 'one_part': nparts == [1],
                     'ok': same_all and counts == [s + 2] and nparts == [1]})
    return rows


def p3(run, n):
    R = run.rounds_done
    # reading P3-a: the two-member parts beside the waited part after every even round t0
    pop_a = []
    prev_members = run.rosters[0].members
    prev_round = 0
    for t0 in range(2, R + 1, 2):
        ros = run.rosters[t0]
        waited = tuple(sorted(run.records[t0 - 1]['waiting']))
        tr = run.track(prev_round, prev_members)
        e = [x for x in tr if x['t'] == t0][0]
        for j in e['whole_parts']:
            if ros.parts[j] != waited:
                pop_a.append((t0, ros.parts[j]))
        prev_members, prev_round = waited, t0
    # reading P3-b: every part given off by any return
    pop_b = [(r['t'], tuple(P)) for r in run.find_returns() for P in r['off_parts']]
    return {'a': {'population': len(pop_a), 'first_rounds': sorted({t for t, _ in pop_a}),
                  'rows': compare_population(run, pop_a, 10, R)},
            'b': {'population': len(pop_b), 'first_rounds': sorted({t for t, _ in pop_b}),
                  'rows': compare_population(run, pop_b, 10, R)}}


# ------------------------------------------------------------------------------------------------------ P4

def p4(run, n):
    R = run.rounds_done
    rows = []
    for t in range(1, R + 1):
        ros = run.rosters[t]
        want = (2 * n, 1) if t % 2 else (3 * n, n + 1)
        got = (len(ros.members), len(ros.parts))
        rows.append({'t': t, 'members': got[0], 'parts': got[1], 'ok': got == want})
    bal = run.in_balance(1, 2)

    def ended(pop):
        res = []
        for t0, P in pop:
            if t0 >= R:
                continue
            dk = run.descendant_knots(t0, P)
            tr = run.track(t0, P)
            later_members = sum(len(e['members']) for e in tr if e['t'] > t0)
            births = {b['id']: b for rec in run.records for b in rec['births']}
            usable0 = [births[x]['usable'] for x in dk]
            ok = (len(dk) == 1 and run.S.made[dk[0]] == t0 + 1 and usable0 == [0] and run.S.hk(dk[0])[0] == 0
                  and later_members == 0)
            res.append({'t0': t0, 'size': len(P), 'n_desc_knots': len(dk), 'usable': usable0,
                        'later_members': later_members, 'ok': ok})
        return {'checked': len(res), 'all_ok': all(r['ok'] for r in res),
                'failures': [r for r in res if not r['ok']][:5],
                'desc_knot_counts': sorted({r['n_desc_knots'] for r in res})}
    pop_formal = [(r['t'], tuple(P)) for r in run.find_returns() for P in r['off_parts']]
    ros2 = run.rosters[2]
    waited2 = tuple(sorted(run.records[1]['waiting']))
    pop_r2 = [(2, P) for P in ros2.parts if P != waited2]
    return {'in_balance_from_1_period_2': bal, 'births_every_round': all(r['n_births'] > 0 for r in run.records),
            'rows_ok': all(r['ok'] for r in rows), 'bad_rows': [r for r in rows if not r['ok']][:5],
            'ended_formal': ended(pop_formal), 'ended_with_round2': ended(pop_formal + pop_r2),
            'balance_summary': run.balance_summary(4)}


# ------------------------------------------------------------------------------------------------------ P5

def p5_chain(run, n):
    R = run.rounds_done
    rets = {(r['s'], tuple(r['part'])): r for r in run.find_returns()}
    ros2 = run.rosters[2]
    chains = []
    for P in ros2.parts:
        cur, s, steps = P, 2, []
        while s + 2 <= R:
            r = rets.get((s, cur))
            if r is None or r['t'] != s + 2:
                break
            steps.append({'s': s, 't': r['t'], 'n_off': r['n_off'], 'off_sizes': r['off_sizes']})
            cur, s = tuple(r['same_part']), r['t']
        full = len(steps) == (R - 2) // 2 and all(x['n_off'] == n // 2 for x in steps)
        if steps:
            chains.append({'part_size': len(P), 'steps': len(steps), 'n_offs': sorted({x['n_off'] for x in steps}),
                           'full_chain_n_over_2': full})
    n_full = sum(1 for c in chains if c['full_chain_n_over_2'])
    return {'chains': chains, 'n_full_chains': n_full, 'parts_after_round_2': len(ros2.parts)}


def no_coming_apart(run):
    c, at = run.max_descendant_parts()
    rets = run.find_returns()
    off = [r for r in rets if r['n_off'] > 0]
    return {'returns_found': len(rets), 'returns_giving_parts_off': len(off), 'max_parts_from_one_part': c,
            'at': at, 'ok': not off and c <= 1}


def main():
    out = {'runs': {}, 'P1': {}, 'P2': {}, 'P3': {}, 'P4': {}, 'P5': {}, 'G_ordinary': {}}
    for lname, law, R in LAWS:
        for n in range(3, 17):
            run = E.Run(E.ring(n, 3), law, R, knot_cap=CAP)
            key = 'Ring(%d,3)|%s' % (n, lname)
            out['runs'][key] = {'summary': run.summary(), 'returns': brief_returns(run),
                                'balance': run.balance_summary(4), 'trace': run.trace()}
            if lname == 'two':
                if n % 2 == 1 and 5 <= n <= 15:
                    a, b = p1_p2(run, n)
                    out['P1'][key] = a
                    out['P2'][key] = b
                if n in (5, 7, 9):
                    out['P3'][key] = p3(run, n)
                if n in (3, 4, 6) or n % 2 == 0:
                    rets = run.find_returns()
                    out['P5'][key] = {'n': n, 'kind': run.kind(),
                                      'returns_giving_parts_off': sum(1 for r in rets if r['n_off'] > 0),
                                      'first_return': brief_returns(run)[:1],
                                      'chain': p5_chain(run, n) if n >= 8 else None}
            if lname == 'three' and n % 2 == 1 and 5 <= n <= 15:
                out['P4'][key] = p4(run, n)
            if lname == 'ordinary':
                out['G_ordinary'][key] = no_coming_apart(run)
            log(key, run.summary()['kind'], 'rounds', run.rounds_done, 'knots', run.S.n_knots,
                'cut' if run.cut_off else '')
    out['resources'] = resources()
    write('a1.json', out)


if __name__ == '__main__':
    main()
