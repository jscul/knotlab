"""The frozen census of BOARD-DIST-20261110-001B: which boards one-bit laws allow.

Usage: run.py [--nmax 6] [--tmax 16] [--kmax 8] [--out DIR] [--controls-only] [--stress]

B1: for each law of the family and each listed board (the tree, the six lines, the plane, every finite
board with at most nmax places), whether the board is allowed (R0) and whether it is allowed with no
frozen place (R0F); predictions P1 (refinement), P2 (collapse), P3 (refinement without frozen places).
B2: identity of indiscernibles at radius 1 (R1): whether boards exist, the largest, whether one is
non-abelian, whether one is plane-like and abelian; prediction P4.
B3: the relation on (e(1, xyXY), s(1), s(xyXY)) and its K1-K3 verdict by knotlab.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import board_lib as bl  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLUG = 'BOARD-DIST-20261110-001B-E001_which_boards_one_bit_laws_allow'
DEFAULT_OUT = os.path.join(ROOT, 'artifacts', 'BOARD-DIST-20261110-001B', SLUG)


def knot_verdict(rel):
    """K1-K3 of a relation on (e, a, b) by knotlab check, loops a and b, contact e."""
    states = [(e, a, b) for e in (0, 1) for a in (0, 1) for b in (0, 1)]
    clauses = []
    for (e, a, b) in states:
        if (e, a, b) not in rel:
            lit = lambda v, name: ('~' + name) if v else name
            clauses.append(' '.join((lit(e, 'e'), lit(a, 'a'), lit(b, 'b'))))
    if not rel:
        return {'is_knot': False, 'note': 'empty relation'}
    if not clauses:
        return {'is_knot': False, 'note': 'full relation'}
    out = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', '; '.join(clauses),
                          '--loops', 'a', 'b', '--contact', 'e', '--json'],
                         cwd=ROOT, env={**os.environ, 'PYTHONPATH': os.path.join(ROOT, 'tools')},
                         capture_output=True, text=True, check=True)
    rep = json.loads(out.stdout)
    return {k: rep[k] for k in ('is_knot', 'binding', 'loss_on_erasure', 'coexistence', 'allowed')}


def run(laws, nmax, tmax, kmax, log):
    t0 = time.time()
    keys = [k for k, _ in laws]
    Ls = [L for _, L in laws]
    nl = len(laws)
    res = {k: {} for k in keys}

    # ---- named infinite boards --------------------------------------------------------------
    for k, L in laws:
        H = bl.half_tree_sets(L)
        P = bl.tree_patterns(L, H)
        res[k]['tree'] = bool(P)
        res[k]['tree_unfrozen'] = {bl.centre(p) for p in P} == {0, 1}
        for (a, b) in bl.LINES:
            ok, vals = bl.line_solutions(L, a, b)
            res[k]['line(%d,%d)' % (a, b)] = ok
            res[k]['line(%d,%d)_unfrozen' % (a, b)] = vals == {0, 1}
        rels = bl.square_relations(L, H)
        res[k]['square_relation'] = rels[(0, 4)]
        res[k]['path_relations'] = {'%s,%s' % (bl.PATH_NAMES[i], bl.PATH_NAMES[j]): r for (i, j), r in rels.items()}
    log('named infinite boards and the square relation: %.1fs' % (time.time() - t0))

    # ---- finite boards ----------------------------------------------------------------------
    boards = []
    for n in range(1, nmax + 1):
        bs = bl.finite_boards(n)
        log('finite boards with %d places: %d' % (n, len(bs)))
        boards.extend(bs)
    fin_allowed = np.zeros((len(boards), nl), dtype=bool)
    fin_unfrozen = np.zeros((len(boards), nl), dtype=bool)
    for i, bd in enumerate(boards):
        a, u = bl.allowed_on_finite(bd, Ls)
        fin_allowed[i], fin_unfrozen[i] = a, u
    log('finite boards checked: %.1fs' % (time.time() - t0))
    abel = [bl.is_abelian(*bd) for bd in boards]

    # ---- the plane --------------------------------------------------------------------------
    trs = bl.tori(tmax)
    torus_any = np.zeros(nl, dtype=bool)
    uses0 = np.zeros(nl, dtype=bool)
    uses1 = np.zeros(nl, dtype=bool)
    Larr = np.array(Ls, dtype=np.int64)
    forb = (~Larr) & 0xFFFFFFFF
    for (abd, bd) in trs:
        bits, masks = bl.board_patterns(bd)
        valid = (masks[:, None] & forb[None, :]) == 0
        n = len(bd[0])
        cols = np.arange(1 << n)
        torus_any |= valid.any(axis=0)
        uses1 |= (valid & (cols != 0)[:, None]).any(axis=0)
        uses0 |= (valid & (cols != (1 << n) - 1)[:, None]).any(axis=0)
    log('tori up to index %d (%d lattices): %.1fs' % (tmax, len(trs), time.time() - t0))
    for j, (k, L) in enumerate(laws):
        if torus_any[j]:
            res[k]['plane'] = True
            res[k]['plane_certificate'] = 'torus'
        else:
            res[k]['plane'] = None
            for kk in range(3, kmax + 1):
                if not bl.box_sat(L, kk):
                    res[k]['plane'] = False
                    res[k]['plane_certificate'] = 'box %d' % kk
                    break
            if res[k]['plane'] is None:
                res[k]['plane_certificate'] = 'undecided'
        if res[k]['plane']:
            if uses0[j] and uses1[j]:
                res[k]['plane_unfrozen'] = True
            else:
                res[k]['plane_unfrozen'] = None
                for kk in range(3, kmax + 1):
                    s0, s1 = bl.box_sat(L, kk, 0), bl.box_sat(L, kk, 1)
                    if not (s0 and s1):
                        res[k]['plane_unfrozen'] = False
                        break
        else:
            res[k]['plane_unfrozen'] = False if res[k]['plane'] is False else None
    log('the plane decided: %.1fs' % (time.time() - t0))

    # ---- covers among the listed boards -----------------------------------------------------
    cover_pairs = []
    for i, big in enumerate(boards):
        for j, small in enumerate(boards):
            if i != j and len(big[0]) > len(small[0]) and bl.covers(big, small):
                cover_pairs.append((i, j))
    line_quot = {ab: [j for j, bd in enumerate(boards) if bl.line_quotient_of(bd, *ab)] for ab in bl.LINES}
    log('covering pairs among finite boards: %d (%.1fs)' % (len(cover_pairs), time.time() - t0))

    # ---- predictions P1, P2, P3 -------------------------------------------------------------
    viol = {'P1': [], 'P2': [], 'P3': []}
    for li, k in enumerate(keys):
        r = res[k]
        for tag, A, tree, lines, plane in (('P1', fin_allowed, r['tree'], {ab: r['line(%d,%d)' % ab] for ab in bl.LINES}, r['plane']),
                                           ('P3', fin_unfrozen, r['tree_unfrozen'], {ab: r['line(%d,%d)_unfrozen' % ab] for ab in bl.LINES}, r['plane_unfrozen'])):
            col = A[:, li]
            for (i, j) in cover_pairs:
                if col[j] and not col[i]:
                    viol[tag].append([k, 'finite %d covers finite %d' % (i, j)])
            anything = col.any() or any(lines.values()) or bool(plane)
            if anything and not tree:
                viol[tag].append([k, 'some board allowed, the tree not'])
            if plane is False:
                for j in range(len(boards)):
                    if abel[j] and col[j]:
                        viol[tag].append([k, 'abelian finite %d allowed, the plane not' % j])
                for ab, v in lines.items():
                    if v:
                        viol[tag].append([k, 'line %s allowed, the plane not' % (ab,)])
            for ab, js in line_quot.items():
                if not lines[ab] and any(col[j] for j in js):
                    viol[tag].append([k, 'a finite quotient of line %s allowed, the line not' % (ab,)])
        # P2: the collapse (the one-place board, index 0) allowed iff every listed board allowed
        allb = fin_allowed[:, li].all() and r['tree'] and all(r['line(%d,%d)' % ab] for ab in bl.LINES) and r['plane'] is True
        if bool(fin_allowed[0, li]) != bool(allb):
            viol['P2'].append([k, 'collapse %s, every board %s' % (bool(fin_allowed[0, li]), bool(allb))])
    log('P1 %d, P2 %d, P3 %d violations' % (len(viol['P1']), len(viol['P2']), len(viol['P3'])))

    for li, k in enumerate(keys):
        res[k]['finite_allowed'] = [int(i) for i in np.nonzero(fin_allowed[:, li])[0]]
        res[k]['finite_unfrozen'] = [int(i) for i in np.nonzero(fin_unfrozen[:, li])[0]]

    # ---- B2: identity of indiscernibles at radius 1 -----------------------------------------
    bad_cert = []
    for k, L in laws:
        r = res[k]
        any_ = bl.ioi1_sat(L, 'any')
        r['ioi1_any'] = any_ is not None
        if any_ is not None and not bl.verify_ioi1(L, *any_):
            bad_cert.append([k, 'any'])
        mx = 0
        if any_ is not None:
            for size in range(bin(L).count('1'), 0, -1):
                cert = bl.ioi1_sat(L, 'any', at_least=size)
                if cert is not None:
                    if not bl.verify_ioi1(L, *cert):
                        bad_cert.append([k, 'max'])
                    mx = len(cert[0])
                    r['ioi1_max_components'] = sorted(len(c) for c in bl.components(*cert))
                    break
        r['ioi1_max'] = mx
        na = bl.ioi1_sat(L, 'nonab') if any_ is not None else None
        r['ioi1_nonabelian'] = na is not None
        if na is not None and not bl.verify_ioi1(L, *na):
            bad_cert.append([k, 'nonab'])
        pl = bl.ioi1_sat(L, 'planelike') if any_ is not None else None
        r['ioi1_planelike_abelian'] = pl is not None
        if pl is not None:
            V, sx, sy = pl
            if not bl.verify_ioi1(L, *pl) or not all(sx[sy[t]] == sy[sx[t]] for t in V):
                bad_cert.append([k, 'planelike'])
            r['ioi1_planelike_sizes'] = sorted(len(c) for c in bl.components(*pl))
    viol['P4'] = [[k, 'plane-like abelian IoI1 board, no non-abelian one'] for k in keys
                  if res[k]['ioi1_planelike_abelian'] and not res[k]['ioi1_nonabelian']]
    log('IoI1 census: %.1fs; P4 %d violations; %d bad certificates' % (time.time() - t0, len(viol['P4']), len(bad_cert)))

    # ---- B3: K1-K3 of the square relation ---------------------------------------------------
    verdicts = {}
    for k in keys:
        res[k]['path_knots'] = []
        for pair, r in res[k]['path_relations'].items():
            rel = tuple(tuple(t) for t in r)
            if rel not in verdicts:
                verdicts[rel] = knot_verdict(set(rel))
            if verdicts[rel]['is_knot']:
                res[k]['path_knots'].append(pair)
        res[k]['square_knot'] = '1,xyXY' in res[k]['path_knots']
    log('square relations: %d distinct (%.1fs)' % (len(verdicts), time.time() - t0))

    summary = summarize(res, keys, boards, abel, viol, bad_cert, verdicts)
    meta = {'nmax': nmax, 'tmax': tmax, 'kmax': kmax, 'finite_boards': len(boards),
            'finite_boards_by_size': [sum(1 for b in boards if len(b[0]) == n) for n in range(1, nmax + 1)],
            'abelian_finite_boards': int(sum(abel)), 'covering_pairs': len(cover_pairs), 'tori': len(trs),
            'seconds': round(time.time() - t0, 1)}
    return {'meta': meta, 'summary': summary, 'violations': viol, 'bad_certificates': bad_cert,
            'boards': [[list(b[0]), list(b[1])] for b in boards], 'laws': res,
            'square_verdicts': [[list(map(list, rel)), v] for rel, v in verdicts.items()]}


def summarize(res, keys, boards, abel, viol, bad_cert, verdicts):
    life = [k for k in keys if k.startswith('L')]
    cnt = lambda pred, ks=life: sum(1 for k in ks if pred(res[k]))
    s = {
        'laws': len(life),
        'tree_allowed': cnt(lambda r: r['tree']),
        'collapse_allowed': cnt(lambda r: 0 in r['finite_allowed']),
        'plane_allowed': cnt(lambda r: r['plane'] is True),
        'plane_not_allowed': cnt(lambda r: r['plane'] is False),
        'plane_undecided': cnt(lambda r: r['plane'] is None),
        'line(1,0)_allowed': cnt(lambda r: r['line(1,0)']),
        'line(1,1)_allowed': cnt(lambda r: r['line(1,1)']),
        'line(1,2)_allowed': cnt(lambda r: r['line(1,2)']),
        'some_finite_allowed': cnt(lambda r: bool(r['finite_allowed'])),
        'tree_but_no_finite': cnt(lambda r: r['tree'] and not r['finite_allowed']),
        'nothing_allowed': cnt(lambda r: not r['tree']),
        'tree_unfrozen': cnt(lambda r: r['tree_unfrozen']),
        'plane_unfrozen': cnt(lambda r: r['plane_unfrozen'] is True),
        'ioi1_any': cnt(lambda r: r['ioi1_any']),
        'ioi1_nonabelian': cnt(lambda r: r['ioi1_nonabelian']),
        'ioi1_planelike_abelian': cnt(lambda r: r['ioi1_planelike_abelian']),
        'ioi1_abelian_only': cnt(lambda r: r['ioi1_any'] and not r['ioi1_nonabelian']),
        'ioi1_max_size': max([res[k]['ioi1_max'] for k in life], default=0),
        'square_knot': cnt(lambda r: r['square_knot']),
        'path_knot_beyond_constancy': cnt(lambda r: any(p != '1,xyXY' for p in r['path_knots'])),
        'path_knot_pairs': sorted({p for k in life for p in res[k]['path_knots']}),
        'violations': {t: len(v) for t, v in viol.items()},
        'bad_certificates': len(bad_cert),
        'named': {k: {f: res[k][f] for f in ('tree', 'plane', 'line(1,0)', 'line(1,1)', 'line(1,2)', 'tree_unfrozen',
                                             'plane_unfrozen', 'ioi1_any', 'ioi1_max', 'ioi1_nonabelian',
                                             'ioi1_planelike_abelian', 'square_relation', 'square_knot', 'path_knots')}
                  | {'collapse': 0 in res[k]['finite_allowed'],
                     'finite_allowed_count': len(res[k]['finite_allowed'])}
                  for k in keys if k in ('L%d' % bl.PARITY0, 'L%d' % bl.PARITY1, 'atom')},
    }
    return s


def controls(log):
    """The cheapest controls: the full law (every pattern allowed) and the empty law."""
    laws = [('full', (1 << 32) - 1), ('empty', 0)]
    out = run(laws, 4, 4, 4, log)
    f, e = out['laws']['full'], out['laws']['empty']
    ok = (f['tree'] and f['plane'] and all(f['line(%d,%d)' % ab] for ab in bl.LINES)
          and len(f['finite_allowed']) == out['meta']['finite_boards'] and f['ioi1_any'] and f['ioi1_max'] == 32
          and not e['tree'] and e['plane'] is False and not e['finite_allowed'] and not e['ioi1_any'])
    return ok, {'full': {kk: f[kk] for kk in ('tree', 'plane', 'ioi1_max', 'ioi1_nonabelian', 'ioi1_planelike_abelian', 'square_relation', 'square_knot', 'path_knots')},
                'empty': {kk: e[kk] for kk in ('tree', 'plane', 'ioi1_any', 'square_relation')}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nmax', type=int, default=6)
    ap.add_argument('--tmax', type=int, default=16)
    ap.add_argument('--kmax', type=int, default=8)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--controls-only', action='store_true')
    ap.add_argument('--tag', default='census')
    args = ap.parse_args()
    logs = []

    def log(m):
        logs.append(m)
        print(m, flush=True)
    ok, ctl = controls(log)
    log('controls %s' % ('passed' if ok else 'FAILED'))
    if args.controls_only:
        print(json.dumps(ctl, indent=1))
        return
    out = run(bl.law_family(), args.nmax, args.tmax, args.kmax, log)
    out['controls'] = {'passed': ok, **ctl}
    out['log'] = logs
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, '%s.json' % args.tag), 'w') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out['summary'], indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
