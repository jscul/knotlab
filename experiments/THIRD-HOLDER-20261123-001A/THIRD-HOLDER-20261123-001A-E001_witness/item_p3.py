"""P3: two and three births per setting.

Setting a adds k not-all-equal births, each on its own loose copy of x1 and of x2 (a = 0) or x3 (a = 1) and one fresh
distinction; Bob likewise with y1 and y2 or y3.  Copies are made by further holders on the copying pairs: x1 copies by
even(x1_i, a, b), x2 copies by even(x2_i, d, e), x3 copies by odd(x3_i, d, e), y1 copies by even(y1_i, p, q), y2 copies by
even(y2_i, r, t), y3 copies by odd(y3_i, r, t).  The record is the three old values and the k fresh ones.

usage:
  item_p3.py full K SA SB [PART NPARTS]
                             full enumeration of the finished structure (K births, settings SA SB), every knot on every
                             assignment; optionally only part PART of NPARTS of the record values (split into runs);
                             writes joint_k{K}_{SA}{SB}_full[_partPofN].json
  item_p3.py build K         writes the structure, counts extra holders, canonical test of every knot, side tables and an
                             exhaustive backtracking search of each finished structure; writes structure_k{K}.json, joint_k{K}_side.json,
                             joint_k{K}_backtrack.json, build_k{K}.json
  item_p3.py summary         compares the computations and evaluates score and hiding; writes item_p3.json
"""
import sys, json, time, os, glob
from fractions import Fraction
import numpy as np
import common as c

mode = sys.argv[1]
if mode == 'full':
    k, sa, sb = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    part, nparts = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (0, 1)
    S = c.build(k)
    n_outer = 1 << (len(S['recA']) + len(S['recB']))
    rng = (part * n_outer // nparts, (part + 1) * n_outer // nparts)
    t0 = time.time()
    J, nv, nk = c.full_joint(S, sa, sb, progress=128, outer_range=rng if nparts > 1 else None)
    dt = time.time() - t0
    tag = '' if nparts == 1 else f'_part{part}of{nparts}'
    done = J[J >= 0]
    json.dump(dict(k=k, settings=[sa, sb], distinctions=nv, knots=nk, assignments=2 ** nv, outer_values=list(rng),
                   assignments_in_this_run=2 ** nv * (rng[1] - rng[0]) // n_outer, allowed_in_this_run=int(done.sum()), seconds=round(dt, 1),
                   table=J.tolist()), open(f'{c.ART}/joint_k{k}_{sa}{sb}_full{tag}.json', 'w'))
    print(f'k={k} settings ({sa},{sb}){tag}: {nv} distinctions, {nk} knots, 2^{nv} assignments in all; outer values {rng[0]}..{rng[1] - 1}; '
          f'allowed words in this run {int(done.sum())}, {dt:.0f}s')

elif mode == 'build':
    k = int(sys.argv[2])
    S = c.build(k)
    old_knots = S['a_knots'] + S['b_knots']
    extra_old, over_old = c.extra_holders(old_knots)
    fin = {}
    for sa in (0, 1):
        for sb in (0, 1):
            names, kn = c.finished(S, sa, sb)
            e, o = c.extra_holders(kn)
            fin[f'{sa}{sb}'] = dict(distinctions=len(names), knots=len(kn), extra_holders=e, held_more_than_twice=o)
    # canonical test of every knot that occurs (old knots and every birth)
    allk = old_knots + [b for s in (0, 1) for b in S['births_A'][s] + S['births_B'][s]]
    canon = [all(r['knot'] for r in c.canonical_check(law, mem)) for law, mem in allk]
    struct = dict(k=k, old_distinctions=c.old_names(S), alice_knots=S['a_knots'], bob_knots=S['b_knots'],
                  births_alice={str(s): S['births_A'][s] for s in (0, 1)}, births_bob={str(s): S['births_B'][s] for s in (0, 1)},
                  record_alice=S['recA'], record_bob=S['recB'], shared=c.SHARED)
    json.dump(struct, open(f'{c.ART}/structure_k{k}.json', 'w'), indent=1)
    print(f'k={k}: {len(c.old_names(S))} old distinctions, {len(old_knots)} old knots ({len(S["a_knots"])} Alice, {len(S["b_knots"])} Bob), '
          f'{2 * k} fresh; extra holders in the old structure {extra_old}: {over_old}')
    print(f'   finished structures: {fin}')
    print(f'   canonical test: {sum(canon)}/{len(canon)} knots pass with every choice of contact')
    Jside = {}; Jbt = {}; copies_ok = True; nodes = {}; tside = {}
    for sa in (0, 1):
        for sb in (0, 1):
            t0 = time.time()
            TA, TB, Js = c.side_tables(S, sa, sb)
            tside[f'{sa}{sb}'] = round(time.time() - t0, 1)
            Jside[sa, sb] = Js
            names, kn = c.finished(S, sa, sb)
            words = []
            t0 = time.time()
            bt, nd = c.backtrack_counts(names, kn, S['recA'] + S['recB'], words_out=words)
            Jbt[sa, sb] = bt.reshape(Js.shape); nodes[f'{sa}{sb}'] = nd
            for w in words:
                for v in ('x1', 'x2', 'x3', 'y1', 'y2', 'y3'):
                    for i in range(2, k + 1):
                        if w[c.copy_name(v, i)] != w[v]: copies_ok = False
            print(f'   settings ({sa},{sb}): side tables {int(Js.sum())} words ({tside[f"{sa}{sb}"]}s); backtracking {int(bt.sum())} words, '
                  f'{nd} nodes ({time.time() - t0:.0f}s); side = backtracking: {np.array_equal(Js, Jbt[sa, sb])}', flush=True)
    M = c.old_table(S) if k <= 2 else None
    c.save_joint(f'{c.ART}/joint_k{k}_side.json', Jside)
    c.save_joint(f'{c.ART}/joint_k{k}_backtrack.json', Jbt)
    json.dump(dict(k=k, extra_holders_old=extra_old, held_more_than_twice_old=over_old, finished=fin, canonical_all_pass=all(canon),
                   n_knots_checked=len(canon), copies_copy=copies_ok, backtrack_nodes=nodes, side_seconds=tside,
                   old_words_full_enumeration=(int(M.sum()) if M is not None else None)),
              open(f'{c.ART}/build_k{k}.json', 'w'), indent=1)
    print(f'   every copy equals its original in every allowed word: {copies_ok}; old words {int(M.sum()) if M is not None else "not enumerated"}')

elif mode == 'summary':
    out = {}
    pred = {2: Fraction(68, 25), 3: Fraction(260, 81)}
    held = True
    for k in (2, 3):
        b = json.load(open(f'{c.ART}/build_k{k}.json'))
        Js = c.load_joint(f'{c.ART}/joint_k{k}_side.json')
        Jb = c.load_joint(f'{c.ART}/joint_k{k}_backtrack.json')
        agree_bt = all(np.array_equal(Js[ab], Jb[ab]) for ab in Js)
        full = {}
        for sa in (0, 1):
            for sb in (0, 1):
                p = f'{c.ART}/joint_k{k}_{sa}{sb}_full.json'
                parts = sorted(glob.glob(f'{c.ART}/joint_k{k}_{sa}{sb}_full_part*of*.json'))
                if os.path.exists(p):
                    full[sa, sb] = np.array(json.load(open(p))['table'], dtype=np.int64)
                elif parts:
                    tabs = [np.array(json.load(open(f))['table'], dtype=np.int64) for f in parts]
                    nparts = int(parts[0].split('of')[-1].split('.')[0])
                    T = np.full(tabs[0].shape, -1, dtype=np.int64)
                    for t_ in tabs:
                        assert np.all((T < 0) | (t_ < 0)), 'overlapping parts'
                        T = np.where(t_ >= 0, t_, T)
                    if len(parts) == nparts and np.all(T >= 0):
                        full[sa, sb] = T
        agree_full = (all(np.array_equal(Js[ab], full[ab]) for ab in full) if full else None)
        ev = c.evaluate_tables(Js, k)
        ok = Fraction(ev['score']) == pred[k] and ev['hidden_alice'] and ev['hidden_bob'] and agree_bt and (agree_full is not False)
        held &= ok
        ctrl = c.evaluate_tables(c.control_tables(Js, k), k)
        ev.update(prediction=str(pred[k]), side_equals_backtracking=agree_bt,
                  full_enumeration_structures=len(full), side_equals_full=agree_full, extra_holders=b['extra_holders_old'],
                  held_more_than_twice=b['held_more_than_twice_old'], canonical_all_pass=b['canonical_all_pass'], copies_copy=b['copies_copy'],
                  control_score=ctrl['score'], held=bool(ok))
        out[f'k{k}'] = ev
        print(f'k={k}: score {ev["score"]} = {ev["score_float"]:.9f} (prediction {pred[k]}); hidden {ev["hidden_alice"]},{ev["hidden_bob"]}; '
              f'largest change {ev["largest_change"]}; totals {ev["totals"]}; outcome choice {ev["outcome_choice"]}')
        print(f'      side tables = backtracking {agree_bt}; side tables = full enumeration {agree_full} ({len(full)} of 4 finished structures enumerated in full); '
              f'extra holders {b["extra_holders_old"]}; control weighting {ctrl["score"]}')
    out['P3'] = 'held' if held else 'failed'
    print('P3:', 'HELD' if held else 'FAILED')
    json.dump(out, open(f'{c.ART}/item_p3.json', 'w'), indent=1)
