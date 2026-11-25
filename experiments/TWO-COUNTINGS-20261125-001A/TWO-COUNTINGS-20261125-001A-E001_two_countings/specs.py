"""The registered setting tests built from structures.json and TD 4.1 / 8.2."""
from __future__ import annotations

import tc

REC_A = ['x1', 'x2', 'x3', 'za']
REC_B = ['y1', 'y2', 'y3', 'zb']


def setting_knots(optA=('x2', 'x3'), optB=('y2', 'y3'), zA='za', zB='zb', xA='x1', xB='y1'):
    KA = {a: [('nae', (xA, optA[a], zA))] for a in (0, 1)}
    KB = {b: [('nae', (xB, optB[b], zB))] for b in (0, 1)}
    return KA, KB


def check_against_file(S, start_key, fin_prefix, pre_extra=()):
    """The finished structures of structures.json equal start (+ pre_extra) + the TD 4.1 setting knots."""
    for a in (0, 1):
        for b in (0, 1):
            fin = S['%s%d%d' % (fin_prefix, a, b)]
            KA, KB = setting_knots()
            mine = list(S[start_key]) + list(pre_extra) + KA[a] + KB[b]
            assert sorted(fin) == sorted(mine), (start_key, a, b)


def eleven(optA=('x2', 'x3'), optB=('y2', 'y3'), S=None):
    S = S or tc.load_structures()
    KA, KB = setting_knots(optA, optB)
    return {'name': 'eleven %s/%s' % ('-'.join(optA), '-'.join(optB)), 'pre': [S['eleven (start)']], 'KA': KA,
            'KB': KB, 'recA': REC_A, 'recB': REC_B}


OPT_A = [('x2', 'x3'), ('x2', 'c'), ('x3', 'c')]
OPT_B = [('y2', 'y3'), ('y2', 't'), ('y3', 't')]


def smallest_gain(S=None):
    S = S or tc.load_structures()
    part = S['smallest gain: part']
    rnd = S['smallest gain: part + rule-Q round 1']
    births = [k for k in rnd if k not in part]
    assert len(births) == 2 and rnd[:len(part)] == part
    KA, KB = setting_knots()
    return {'name': 'smallest gain', 'pre': [part, births], 'KA': KA, 'KB': KB, 'recA': REC_A, 'recB': REC_B}


def simple(start_key, name, S=None):
    S = S or tc.load_structures()
    KA, KB = setting_knots()
    return {'name': name, 'pre': [S[start_key]], 'KA': KA, 'KB': KB, 'recA': REC_A, 'recB': REC_B}


def file_checks(S=None):
    S = S or tc.load_structures()
    check_against_file(S, 'eleven (start)', 'eleven + settings ')
    check_against_file(S, 'smallest gain: part + rule-Q round 1', 'smallest gain finished ')
    check_against_file(S, 'seven (start)', 'seven + settings ')
    check_against_file(S, 'eight (start)', 'eight + settings ')
    check_against_file(S, 'nine, the pencil (start)', 'nine + settings ')
    check_against_file(S, 'eighteen (start)', 'eighteen + settings ')
    return True
