"""Gate G of RING-IN-BALANCE-20261123-001A: the items computable by this engine.

The comparison with the pilot's two programs is not done here (the engine's author has not seen them): traces.py writes
a1_trace.json for that comparison.  Writes gate.json.
"""
import json
import os
import subprocess
import sys

from common import E, OUT, load, log, resources, write

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def births(run):
    return [r['n_births'] for r in run.records]


def no_coming_apart(run):
    # a part comes apart only from a part that returns (definitions); checked also in the stronger form that the
    # descendants of any part never occupy more than one part of a later roster
    c, at = run.max_descendant_parts()
    rets = run.find_returns()
    off = [r for r in rets if r['n_off'] > 0]
    return {'returns_found': len(rets), 'returns_giving_parts_off': len(off), 'max_parts_from_one_part': c,
            'at': at, 'ok': not off and c <= 1}


def main():
    G = {}
    # G1 ordinary Ring(5, 3)
    r53 = E.Run(E.ring(5, 3), E.ORDINARY, 8, knot_cap=6000)
    b = births(r53)
    G['G1 ordinary Ring(5,3) births 10,15,25,40,65,105'] = {'ok': b[:6] == [10, 15, 25, 40, 65, 105], 'births': b}
    # G2 ordinary Ring(5, 2)
    r52 = E.Run(E.ring(5, 2), E.ORDINARY, 8)
    b = births(r52)
    G['G2 ordinary Ring(5,2) five births every round'] = {'ok': all(x == 5 for x in b), 'births': b}
    # G3 seven-knot generator
    g7 = E.Run(E.generator7(), E.ORDINARY, 5)
    b = births(g7)
    fr = [r['fresh_total'] for r in g7.records]
    G['G3 generator births 8,12,19,32,56 fresh 25,42,75,140,269'] = {
        'ok': b == [8, 12, 19, 32, 56] and fr == [25, 42, 75, 140, 269], 'births': b, 'fresh': fr}
    # G4 no part comes apart in any ordinary run (here; A1's ordinary runs are checked in a1.py, A4's in a4.py)
    g7b = E.Run(E.generator7(), E.ORDINARY, 6, knot_cap=6000)
    items = {'Ring(5,3) R=8': no_coming_apart(r53), 'Ring(5,2) R=8': no_coming_apart(r52),
             'generator R=6': no_coming_apart(g7b)}
    for n in range(3, 17):
        items['Ring(%d,3) R=8' % n] = no_coming_apart(E.Run(E.ring(n, 3), E.ORDINARY, 8, knot_cap=6000))
    G['G4 no part comes apart in any ordinary run'] = {'ok': all(v['ok'] for v in items.values()), 'runs': items}
    # G5 hand trace under the two added rules
    two = E.Run(E.ring(5, 3), E.TWO_ADDED, 2)
    rr = [(r['n_joins'], r['n_offshoots']) for r in two.records]
    G['G5 two added rules Ring(5,3): round 1 five joins + five offshoots; round 2 ten offshoots, no join'] = {
        'ok': rr == [(5, 5), (0, 10)], 'joins_offshoots': rr}
    # G6 pilot comparison: not done by this engine
    G['G6 A1 equals the pilot programs'] = {'ok': None, 'note': 'not computed here: a1_trace.json is written by '
                                                                'traces.py for the thread to compare'}
    # G7 planted failing knot (and the NAE case) - recomputed here, also in test_engine.py
    S = E.from_stars([['a', 'b', 'l1', 'l2', 'l3'], ['a', 'b', 'e', 'f', 'g'], ['e', 'f', 'g']])
    res = E.parity_knot_test(S)
    T = E.from_stars([[0, 1, 4], [0, 1, 2, 3], [2, 3, 4]])
    nae = E.nae_knot_test(T)
    G['G7 two parity methods agree on a planted failing knot'] = {
        'ok': 0 in res['rank_fail'] and 0 in res['cut_fail'] and not res['disagree'],
        'rank_fail': res['rank_fail'], 'cut_fail': res['cut_fail'], 'disagree': res['disagree'],
        'nae_small_case_fail': nae['fail']}
    # G8 STALL mutant
    st = E.Run(E.ring(5, 3), E.Law('CAP-3', 'STALL'), 3)
    first_stall = next((r['round'] for r in st.records if r['stalled']), None)
    G['G8 STALL in place of CANCEL-WAIT: Ring(5,3) stalls in round 2'] = {
        'ok': first_stall == 2, 'first_stall': first_stall,
        'short_in_round_2': st.records[1]['short']}
    # G9 self-checks (test_engine.py must have been run first)
    try:
        te = load('test_engine.json')
        G['G9 engine self-checks (test_engine.py)'] = {'ok': bool(te.get('_all_ok')),
                                                         'checks': {k: v['ok'] for k, v in te.items()
                                                                    if not k.startswith('_')}}
    except FileNotFoundError:
        G['G9 engine self-checks (test_engine.py)'] = {'ok': False, 'note': 'test_engine.json missing'}
    # G10 determinism across processes and hash seeds
    code = ('import sys, json; sys.path.insert(0, %r); import engine as E; '
            'r = E.Run(E.ring(7, 3), E.TWO_ADDED, 10); '
            'print(json.dumps([r.trace(True), r.find_returns(), r.records, r.S.to_dict()], sort_keys=True))' % HERE)
    outs = []
    for seed in ('0', '12345'):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        outs.append(subprocess.run([PY, '-B', '-c', code], capture_output=True, text=True, env=env).stdout)
    G['G10 determinism across processes (two hash seeds)'] = {'ok': bool(outs[0]) and outs[0] == outs[1],
                                                               'bytes': len(outs[0])}
    computed = [v['ok'] for v in G.values() if v['ok'] is not None]
    out = {'items': G, 'all_computed_ok': all(computed), 'resources': resources()}
    for k, v in G.items():
        log('%-95s %s' % (k, {True: 'PASS', False: 'FAIL', None: 'n/a'}[v['ok']]))
    write('gate.json', out)


if __name__ == '__main__':
    main()
