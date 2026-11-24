"""Verify every hidden excess met in a grown stage of a founder start that has none (T1 runs), by full enumeration of the
four finished structures (the stage, its knots with their laws, plus the supplied setting births nae(x1, x2|x3, za) and
nae(y1, y2|y3, zb)): every word of each finished structure is enumerated, no table shortcut; hiding and the score are
computed exactly from the joint record counts (THIRD-HOLDER-20261123-001B common.brute_joint / evaluate_joint, COPIED below).
Also: for every grown stage whose table is proportional to its target's, whether the stage is the target itself up to
renaming of its non-observer distinctions (knot-distinction incidence with laws and observer names, networkx matching).

Stages with more than MAXD distinctions are not enumerated (listed as such).  With --mind only the rows whose stage has
between --mind and --maxd distinctions are taken (used to run the larger stages in separate runs).
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --tag c2 [--lo 0 --hi 100000]
       [--maxd 22] [--mind 23 --maxd 23 --out name.jsonl]
"""
import argparse
import glob
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np
from networkx.algorithms import isomorphism

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

MAXD = 26


# ---- COPIED from THIRD-HOLDER-20261123-001B common.py (enumerate_ok, brute_joint, evaluate_joint), knots as (law, members) --
def law_ok(law, s, k):
    if law == 'nae':
        return (s != 0) & (s != k)
    if law == 'even':
        return (s % 2) == 0
    return (s % 2) == 1


def enumerate_ok(names, knots, chunk_bits=22):
    n = len(names)
    pos = {nm: i for i, nm in enumerate(names)}
    total = 1 << n
    step = 1 << min(n, chunk_bits)
    for off in range(0, total, step):
        idx = np.arange(off, off + step, dtype=np.int64)
        bits = {nm: ((idx >> i) & 1).astype(np.int8) for nm, i in pos.items()}
        ok = np.ones(step, dtype=bool)
        for law, mem in knots:
            s = sum(bits[m].astype(np.int64) for m in mem)
            ok &= law_ok(law, s, len(mem))
        yield off, bits, ok


def brute_joint(knots, a, b):
    ks = list(knots) + [('nae', ('x1', f'x{2 + a}', 'za')), ('nae', ('y1', f'y{2 + b}', 'zb'))]
    names = []
    for law, mem in ks:
        for m in mem:
            if m not in names:
                names.append(m)
    J = np.zeros((16, 16), dtype=np.int64)
    for off, bits, ok in enumerate_ok(names, ks):
        ra = ((bits['x1'].astype(np.int64) * 4 + bits['x2'] * 2 + bits['x3']) * 2 + bits['za'])[ok]
        rb = ((bits['y1'].astype(np.int64) * 4 + bits['y2'] * 2 + bits['y3']) * 2 + bits['zb'])[ok]
        np.add.at(J, (ra, rb), 1)
    return J, len(names)


def evaluate_joint(J):
    SGN = c.SGN
    hidA = all(np.array_equal(J[a, 0].sum(1) * int(J[a, 1].sum()), J[a, 1].sum(1) * int(J[a, 0].sum())) for a in (0, 1))
    hidB = all(np.array_equal(J[0, b].sum(0) * int(J[1, b].sum()), J[1, b].sum(0) * int(J[0, b].sum())) for b in (0, 1))
    tv = Fraction(0)
    for a in (0, 1):
        p = [J[a, b].sum(1) for b in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(u), int(p[0].sum())) - Fraction(int(v), int(p[1].sum()))) for u, v in zip(*p)) / 2)
    for b in (0, 1):
        p = [J[a, b].sum(0) for a in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(u), int(p[0].sum())) - Fraction(int(v), int(p[1].sum()))) for u, v in zip(*p)) / 2)
    Ef = {}
    Ex = {}
    for a in (0, 1):
        for b in (0, 1):
            num = SGN @ J[a, b] @ SGN.T
            den = int(J[a, b].sum())
            Ef[a, b] = num / den
            Ex[a, b] = (num, den)
    best = Fraction(-1)
    arg = None
    allv = []
    gbest = 0.0
    for p in range(4):
        s = np.ones(4)
        s[p] = -1
        V = (s[0] * Ef[0, 0][:, None, :, None] + s[1] * Ef[0, 1][:, None, None, :] + s[2] * Ef[1, 0][None, :, :, None]
             + s[3] * Ef[1, 1][None, :, None, :])
        allv.append(V)
        gbest = max(gbest, float(np.abs(V).max()))
    for p in range(4):
        s = [1] * 4
        s[p] = -1
        for kA0, kA1, kB0, kB1 in np.argwhere(np.abs(allv[p]) >= gbest - 1e-7):
            v = (s[0] * Fraction(int(Ex[0, 0][0][kA0, kB0]), Ex[0, 0][1]) + s[1] * Fraction(int(Ex[0, 1][0][kA0, kB1]), Ex[0, 1][1])
                 + s[2] * Fraction(int(Ex[1, 0][0][kA1, kB0]), Ex[1, 0][1]) + s[3] * Fraction(int(Ex[1, 1][0][kA1, kB1]), Ex[1, 1][1]))
            if abs(v) > best:
                best = abs(v)
                arg = (int(kA0) + 1, int(kA1) + 1, int(kB0) + 1, int(kB1) + 1, p)
    return dict(hidden_A=bool(hidA), hidden_B=bool(hidB), hidden=bool(hidA and hidB), score=best, arg=arg, change=tv)
# ---- end COPIED ---------------------------------------------------------------------------------------------------------


def brute_joint_all(knots, chunk_bits=22):
    """The four joint record tables J[a, b] of the finished structures by enumerating every word of each: a word is a
    word of the stage's distinctions with values of za and zb; it is kept when every stage knot and both setting births
    nae(x1, x_{2+a}, za), nae(y1, y_{2+b}, zb) hold.  The stage knots are checked once per stage word for all four finished
    structures (they are common to the four); the births are checked for each (a, b, za, zb).  Same counts as brute_joint
    (checked in this script on the stages of at most 22 distinctions)."""
    names = []
    for law, mem in knots:
        for m in mem:
            if m not in names:
                names.append(m)
    J = {(a, b): np.zeros((16, 16), dtype=np.int64) for a in (0, 1) for b in (0, 1)}
    for off, bits, ok in enumerate_ok(names, knots, chunk_bits):
        x = [bits[o][ok].astype(np.int64) for o in c.OBS]
        for za in (0, 1):
            for zb in (0, 1):
                for a in (0, 1):
                    okA = ~((x[0] == x[1 + a]) & (x[0] == za))
                    ra = ((x[0] * 4 + x[1] * 2 + x[2]) * 2 + za)
                    for b in (0, 1):
                        okB = ~((x[3] == x[4 + b]) & (x[3] == zb))
                        rb = ((x[3] * 4 + x[4] * 2 + x[5]) * 2 + zb)
                        m = okA & okB
                        np.add.at(J[a, b], (ra[m], rb[m]), 1)
    return J, len(names) + 2


def incidence(knots):
    g = nx.Graph()
    for k, (law, mem) in enumerate(knots):
        g.add_node(('k', k), lab='knot:' + law)
        for m in mem:
            g.add_node(('d', m), lab=('obs:' + m) if m in c.OBS else 'd')
            g.add_edge(('k', k), ('d', m))
    return g


def same_structure(k1, k2):
    g1, g2 = incidence(k1), incidence(k2)
    if g1.number_of_nodes() != g2.number_of_nodes() or g1.number_of_edges() != g2.number_of_edges():
        return False
    gm = isomorphism.GraphMatcher(g1, g2, node_match=lambda a, b: a['lab'] == b['lab'])
    return gm.is_isomorphic()


def main():
    global MAXD
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='c2')
    ap.add_argument('--lo', type=int, default=0)
    ap.add_argument('--hi', type=int, default=10 ** 9)
    ap.add_argument('--mind', type=int, default=0, help='only rows whose stage has at least this many distinctions')
    ap.add_argument('--maxd', type=int, default=MAXD, help='enumerate stages of at most this many distinctions')
    ap.add_argument('--out', default=None)
    ap.add_argument('--no-separate', action='store_true', help='skip the separate enumeration of each finished structure')
    args = ap.parse_args()
    MAXD = args.maxd
    t0 = time.time()
    targets = {t['tid']: t for t in c.load_targets()}
    hits = [json.loads(l) for f in sorted(glob.glob(str(c.ART / f't1_hits_{args.tag}_*.jsonl'))) for l in open(f)]
    todo = [h for h in hits if (h['excess'] and not h['stage0_excess']) or (h['kind'] == 'proportional' and h['t'] >= 1)]
    todo = todo[args.lo:args.hi]
    out = []
    for h in todo:
        knots = [(law, tuple(mem)) for law, mem in h['knots']]
        D = len({m for _, mem in knots for m in mem})
        if D < args.mind or (args.mind and D > args.maxd):
            continue
        row = dict(si=h['si'], tid=h['tid'], mask=h['mask'], t=h['t'], kind=h['kind'], newborn_laws=h['newborn_laws'],
                   knots=[c.fmt_knot(l, m) for l, m in knots], D=D, eval_contraction=h['eval'])
        if h['kind'] == 'proportional':
            row['same_structure_as_target'] = same_structure(knots, targets[h['tid']]['knots'])
        if h['excess'] and not h['stage0_excess']:
            if D <= MAXD:
                J, nn = brute_joint_all(knots)
                if D <= 22 and not args.no_separate:      # the separate enumeration of each finished structure, as THIRD-HOLDER's brute_joint
                    same = all(np.array_equal(J[a, b], brute_joint(knots, a, b)[0]) for a in (0, 1) for b in (0, 1))
                    row['separate_enumeration_equal'] = bool(same)
                ev = evaluate_joint(J)
                M = np.array(h['table'], dtype=object).reshape(8, 8)
                agree = all(np.array_equal(J[a, b], (c.F[a].T.astype(object).dot(M).dot(c.F[b].astype(object))).astype(np.int64))
                            for a in (0, 1) for b in (0, 1))
                row.update(full_enumeration=dict(hidden=ev['hidden'], score=str(ev['score']), change=str(ev['change']),
                                                 arg=ev['arg'], words=[int(J[a, b].sum()) for a in (0, 1) for b in (0, 1)],
                                                 distinctions_finished=nn, joint_equals_table=bool(agree),
                                                 score_equals_contraction=str(ev['score']) == h['eval'][3]))
            else:
                row['full_enumeration'] = f'not run: {D} distinctions (more than {MAXD})'
        out.append(row)
    c.dump(c.ART / (args.out or f'verify_excess_{args.tag}_{args.lo}-{min(args.hi, 10 ** 6)}.jsonl'), out)
    ok = [r for r in out if isinstance(r.get('full_enumeration'), dict)]
    print(json.dumps(dict(rows=len(out), enumerated=len(ok),
                          all_hidden_excess=all(r['full_enumeration']['hidden'] and Fraction(r['full_enumeration']['score']) > 2
                                                for r in ok),
                          all_agree=all(r['full_enumeration']['joint_equals_table'] and r['full_enumeration']['score_equals_contraction']
                                        for r in ok),
                          not_enumerated=sum(1 for r in out if isinstance(r.get('full_enumeration'), str)),
                          same_structure=sum(1 for r in out if r.get('same_structure_as_target')),
                          proportional_rows=sum(1 for r in out if r['kind'] == 'proportional'),
                          seconds=round(time.time() - t0, 1))))


if __name__ == '__main__':
    main()
