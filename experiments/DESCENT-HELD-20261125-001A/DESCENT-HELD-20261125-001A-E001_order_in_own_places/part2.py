"""Part 2: restarts (DH 5.4, 5.5; P8, P8b).  Writes part2.json.  Readings: deviations 24-26.

python -B part2.py
"""
from __future__ import annotations

import itertools
import sys
import time
from collections import defaultdict

from dh_common import STARTS_JSON, write, log, n_procs, load_avg
import dh_engine as E
from dh_census import census, kept_parity, census_canon, structure_canon

STARS = {k: v['stars'] for k, v in STARTS_JSON['starts'].items()}
CONTROL_STARTS = ['LONE-THREE', 'LONE-FOUR', 'TWO-KNOT', 'THREE-KNOT', 'Ring(5,3)', 'D2(4,3)']
CONTROL_LAWS = [L.name for L in E.LAWS[:7]] + ['H-R3W']


# ------------------------------------------------------------------------------------------------ DH 4.4 parts
def part_structure(S, part, t):
    """DH 4.4: the knots of `part`, each with all its places as after round t; holders inside the part; barred marks
    as after round t.  Returns (places in local numbering, holders_in by local distinction, barred set)."""
    part = sorted(part)
    loc = {u: i for i, u in enumerate(part)}
    dl = {}
    places = []
    for u in part:
        P = []
        for d in S.places[u]:
            if d not in dl:
                dl[d] = len(dl)
            P.append(dl[d])
        places.append(P)
    holders_in = {}
    barred = set()
    for d, j in dl.items():
        holders_in[j] = [loc[h] for h in S.holders[d] if h in loc and S.born[h] <= t]
        if S.bround[d] is not None and S.bround[d] <= t:
            barred.add(j)
    return places, holders_in, barred


# ------------------------------------------------------------------------------------------------ (2a) census restarts
def census_restart_job(idx):
    n, gi, loose, stars = census()[idx]
    out = {'idx': idx, 'n': n, 'kept': kept_parity(stars), 'laws': {}}
    for L in E.RECORDED:
        S, recs, end = E.grow(stars, L, None, 'parity', R=1, N=10 ** 9)
        new = recs[0]['new'] if recs else []
        m = len(new)
        prefix, subset, complete = [], [], []
        reasons = defaultdict(int)
        for j in range(1, m + 1):
            if n + j > 5:
                break
            pl, hi, ba = part_structure(S, list(range(n)) + new[:j], 1)
            key, why = structure_canon(pl, hi, ba)
            if key is None:
                reasons[why] += 1
            else:
                prefix.append((j, key))
                if j == m:
                    complete.append(key)
        for size in range(1, min(m, 5 - n) + 1):
            for sub in itertools.combinations(new, size):
                pl, hi, ba = part_structure(S, list(range(n)) + list(sub), 1)
                key, why = structure_canon(pl, hi, ba)
                if key is not None:
                    subset.append(key)
        out['laws'][L.name] = {'round1_new': m, 'closing': bool(recs and recs[0]['closing']),
                               'prefix': prefix, 'complete': complete, 'subset': subset, 'not_allowed': dict(reasons)}
    return out


def census_restarts(pool):
    C = census()
    canon = {}
    kept = {}
    for idx, (n, gi, loose, stars) in enumerate(C):
        canon[census_canon(n, gi, loose)] = idx
    kept_flags = pool.map(kept_parity, [c[3] for c in C], chunksize=50)
    sources = [i for i, c in enumerate(C) if c[0] <= 4]
    res = pool.map(census_restart_job, sources)
    kept_set = {i for i, k in enumerate(kept_flags) if k}

    def collect(src_filter):
        by_law = {}
        union_prefix, union_complete, union_subset = set(), set(), set()
        listing = defaultdict(list)
        for r in res:
            if not src_filter(r):
                continue
            for ln, v in r['laws'].items():
                b = by_law.setdefault(ln, {'prefix': set(), 'complete': set(), 'subset': set()})
                for j, key in v['prefix']:
                    c = canon.get(key)
                    if c is not None and c in kept_set:
                        b['prefix'].add(c)
                        listing[c].append([r['idx'], ln, j, j == v['round1_new']])
                for key in v['complete']:
                    c = canon.get(key)
                    if c is not None and c in kept_set:
                        b['complete'].add(c)
                for key in v['subset']:
                    c = canon.get(key)
                    if c is not None and c in kept_set:
                        b['subset'].add(c)
        for b in by_law.values():
            union_prefix |= b['prefix']; union_complete |= b['complete']; union_subset |= b['subset']
        return {'by_law': {ln: {k: len(v) for k, v in b.items()} for ln, b in by_law.items()},
                'prefix': len(union_prefix), 'complete': len(union_complete),
                'within_only': len(union_prefix - union_complete), 'subset': len(union_subset),
                'complete_list': sorted(union_complete), 'prefix_list': sorted(union_prefix),
                'subset_minus_prefix': len(union_subset - union_prefix),
                'by_law_lists': {ln: {k: sorted(v) for k, v in b.items()} for ln, b in by_law.items()},
                'how_reached': {str(c): listing[c][:6] for c in sorted(union_prefix)}}
    all223 = collect(lambda r: True)
    kept220 = collect(lambda r: r['kept'])
    by_size = defaultdict(int)
    for c in all223['prefix_list']:
        by_size[C[c][0]] += 1
    return {'sources_all': len(sources), 'sources_kept': sum(1 for r in res if r['kept']),
            'kept_census': len(kept_set), 'from_223': all223, 'from_220_kept': kept220,
            'same_515_from_both': all223['prefix_list'] == kept220['prefix_list'],
            'reached_by_size': dict(by_size),
            'not_allowed_reasons': _sum_reasons(res)}


def _sum_reasons(res):
    out = defaultdict(int)
    for r in res:
        for v in r['laws'].values():
            for k, c in v['not_allowed'].items():
                out[k] += c
    return dict(out)


# ------------------------------------------------------------------------------------------------ (2b) restart control
def control_job(args):
    start, ln = args
    L = E.LAW[ln]
    S, recs, end = E.grow(STARS[start], L, None, 'parity', R=5, N=3000)
    rows = []
    for t in (1, 2, 3):
        if S.round <= t:
            rows.append({'t': t, 'applicable': False,
                         'why': 'the run ended at round %d (%s): no continuation after round %d' % (S.round, end, t)})
            continue
        stars_t, barred_t = E.snapshot_stars(S, t)
        R2, rr, end2 = E.grow(stars_t, L, None, 'parity', R=2, N=3000, barred_labels=barred_t)
        k_reached = min(R2.round, S.round - t)
        tt = t + k_reached
        stars_o, barred_o = E.snapshot_stars(S, tt)
        stars_r, barred_r = E.snapshot_stars(R2, k_reached)
        births_o = [q['births'] for q in recs[t:tt]]
        births_r = [q['births'] for q in rr[:k_reached]]
        names = stars_o == stars_r and barred_o == barred_r
        stage = 1 if names else None
        iso = None
        sig = None
        if not names:
            if len(stars_o) <= 300:
                iso = E.isomorphic(stars_o, barred_o, stars_r, barred_r)
                stage = 2
            else:
                stage = 3
                sig = E.signature(R2, rr, None)['knots'] == E.signature(S, recs[:tt], None)['knots']
        rows.append({'t': t, 'applicable': True, 'k': k_reached, 'knots': len(stars_o), 'births_continuation': births_o,
                     'births_restart': births_r, 'equal_names': names, 'stage': stage, 'isomorphic': iso,
                     'signature_equal (a signature)': sig,
                     'equal': bool(names or iso or sig) and births_o == births_r})
    return {'start': start, 'law': ln, 'rows': rows}


# ------------------------------------------------------------------------------------------------ (2c) arm-W hand-ins
def handin_job(args):
    start, ln, form = args
    L = E.LAW[ln]
    S, recs, end = E.grow(STARS[start], L, form, 'parity', R=1, N=10 ** 9)
    if not recs or not recs[0]['new']:
        return {'start': start, 'law': ln, 'form': form, 'applicable': False}
    a = E.condition_a(S, form)
    c = E.condition_c(S, form)
    d = E.condition_d(S)
    stars1, barred1 = E.snapshot_stars(S, 1)
    H = E.Struct(stars1, barred1)
    kap = [H.kappa(u, form) % 3 for u in range(len(H.places))]
    new_side_wrong = new_side_right = parent_side_right = parent_side_wrong = 0
    for x in recs[0]['new']:
        for y in S.parents[x]:
            dd = [q for q in S.places[x] if y in S.holders[q]]
            for _ in dd:
                pred_new_side = (kap[y] - kap[x]) % 3 == 2      # predicts "y is x's parent"
                if pred_new_side:
                    new_side_wrong += 1                          # in the hand-in no knot has a parent
                else:
                    new_side_right += 1
                pred_parent_side = (kap[x] - kap[y]) % 3 == 2
                if pred_parent_side:
                    parent_side_wrong += 1
                else:
                    parent_side_right += 1
    handin_a = E.condition_a(H, form)
    pr = E.place_rule(H, form, keep_wrong=0)
    ok = (new_side_right == 0 and parent_side_wrong == 0) if (a and c and d) else None
    return {'start': start, 'law': ln, 'form': form, 'applicable': True, 'a': a, 'c': c, 'd': d,
            'old_parent_places': new_side_wrong + new_side_right,
            'wrong_from_new_knot_side': new_side_wrong, 'right_from_new_knot_side': new_side_right,
            'right_from_parent_side': parent_side_right, 'wrong_from_parent_side': parent_side_wrong,
            'handin_meets_a': handin_a, 'handin_place_rule_by_kind': pr['by_kind'],
            'handin_carries_barred': len(barred1), 'P8_second_half': ok}


def main():
    import multiprocessing as mp
    procs = n_procs()
    log('part 2, load %.1f, %d processes' % (load_avg(), procs))
    out = {'part': 2, 'load_at_start': load_avg(), 'processes': procs}
    t0 = time.time()
    census()
    with mp.Pool(procs) as pool:
        t = time.time(); out['census_restarts'] = census_restarts(pool); out['census_restarts']['seconds'] = round(time.time() - t, 1)
        log('census restarts', out['census_restarts']['from_223']['prefix'], out['census_restarts']['from_223']['complete'],
            out['census_restarts']['from_223']['subset'])
        t = time.time()
        ctl = pool.map(control_job, [(s, ln) for ln in CONTROL_LAWS for s in CONTROL_STARTS])
        app = [r for c in ctl for r in c['rows'] if r['applicable']]
        out['restart_control'] = {'runs': ctl, 'tests': len(app), 'equal': sum(r['equal'] for r in app),
                                  'by_stage': {str(s): sum(1 for r in app if r['stage'] == s) for s in (1, 2, 3)},
                                  'not_applicable': sum(1 for c in ctl for r in c['rows'] if not r['applicable']),
                                  'seconds': round(time.time() - t, 1)}
        log('restart control', out['restart_control']['tests'], out['restart_control']['equal'],
            out['restart_control']['by_stage'])
        t = time.time()
        hi = pool.map(handin_job, [(s, L.name, f) for s in CONTROL_STARTS for L in E.RELEASE_BASES for f in E.FORMS])
        app = [r for r in hi if r['applicable']]
        out['handins'] = {'runs': hi, 'n': len(hi), 'applicable': len(app),
                          'conditions_hold': sum(1 for r in app if r['P8_second_half'] is not None),
                          'as_stated': sum(1 for r in app if r['P8_second_half']),
                          'otherwise': [[r['start'], r['law'], r['form']] for r in app if r['P8_second_half'] is False],
                          'seconds': round(time.time() - t, 1)}
        log('hand-ins', out['handins']['applicable'], out['handins']['conditions_hold'], out['handins']['as_stated'])
    out['seconds'] = round(time.time() - t0, 1)
    write('part2.json', out)
    log('part 2 written', out['seconds'])


if __name__ == '__main__':
    main()
