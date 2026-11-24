"""Reports for one law after its classes are computed (runs 2 to 5; deviations.md, items 22-27).

  population_tables(lr)     for each kind of look, distance and population: places by kind, classes, mixed classes,
                            classes of C and S only, the groups of the mixed classes, the guard count
  written_pairs(lr)         run 4: per distance with a confusable pair in P2, the pair of greatest farness, with an
                            explicit renaming checked place by place and its least separating distance up to 10
  followed_pair(lr, ...)    run 4: one pair followed from round to round
  whole_renamings(lr)       run 5: final P2 structures of at most 2,000 knots
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict

import pfh_auto as AU
import pfh_iso as ISO
import pfh_look as LK
import pfh_views as VW
from pfh_classes import DMAX, VARIANTS, greedy_renaming

KN = ('P', 'C', 'S')


def popcodes(lr):
    """For each structure: its population code: ('serial', run) or ('P2', round, in_P1)."""
    out = []
    for rec in lr.structs:
        if rec.kind == 'serial':
            out.append(('serial', rec.run))
        else:
            out.append(('P2', rec.round, rec.in_p1))
    return out


def population_members(code):
    """Names of the populations a structure belongs to."""
    if code[0] == 'serial':
        return ['P1', 'P1P2', 'P1 serial']
    _, t, p1 = code
    out = ['P2', 'P1P2', 'P2 round %d' % t]
    if p1:
        out += ['P1', 'P1 reference round %d' % t, 'P1 reference']
    return out


def population_tables(lr):
    codes = popcodes(lr)
    code_ids = {}
    sid_code = []
    for c in codes:
        if c not in code_ids:
            code_ids[c] = len(code_ids)
        sid_code.append(code_ids[c])
    pops_of_code = [population_members(c) for c in sorted(code_ids, key=code_ids.get)]
    pops_of_sid = [pops_of_code[k] for k in sid_code]
    allpops = sorted({p for ps in pops_of_code for p in ps}, key=_popkey)
    kinds = lr.kinds
    sid_of = lr.sid_of
    n = lr.n_items
    item_code = [sid_code[sid_of[i]] for i in range(n)]
    # guard: least of the distances to the nearest start knot and to the nearest member, per item
    ghist = defaultdict(Counter)
    for rec in lr.structs:
        k = sid_code[rec.sid]
        for (a, b) in rec.guard:
            ghist[k][min(a, b, DMAX + 1)] += 1
    guard = {}
    for p in allpops:
        for d in range(1, DMAX + 1):
            guard[(p, d)] = sum(cnt for k, h in ghist.items() if p in pops_of_code[k]
                                for g, cnt in h.items() if g > d)
    out = {}
    for v in VARIANTS:
        for d in range(1, DMAX + 1):
            cls = lr.cls[(v, d)]
            agg = defaultdict(Counter)        # class -> Counter((code, kind))
            for i in range(n):
                agg[cls[i]][(item_code[i], kinds[i])] += 1
            # per class and population: counts of P, C, S
            pc = {}
            for c, cnt in agg.items():
                q = defaultdict(lambda: [0, 0, 0])
                for (k, kd), m in cnt.items():
                    for p in pops_of_code[k]:
                        q[p][kd] += m
                pc[c] = q
            mixed_pooled = [c for c, q in pc.items() if q['P1P2'][0] and (q['P1P2'][1] or q['P1P2'][2])]
            mixed_set = set(mixed_pooled)
            members = defaultdict(lambda: ([], []))
            for i in range(n):
                c = cls[i]
                if c in mixed_set:
                    members[c][0 if kinds[i] == 0 else 1].append(i)
            table = {}
            for p in allpops:
                nk = [0, 0, 0]
                ncls = nmixed = ncs = 0
                for c, q in pc.items():
                    if p not in q:
                        continue
                    a, b, s_ = q[p]
                    if a + b + s_ == 0:
                        continue
                    ncls += 1
                    nk[0] += a
                    nk[1] += b
                    nk[2] += s_
                    if a and (b or s_):
                        nmixed += 1
                    elif b and s_:
                        ncs += 1
                groups = Counter()
                for c in mixed_pooled:
                    q = pc[c]
                    if p not in q or not (q[p][0] and (q[p][1] or q[p][2])):
                        continue
                    Pi = [i for i in members[c][0] if p in pops_of_sid[sid_of[i]]]
                    Qi = [i for i in members[c][1] if p in pops_of_sid[sid_of[i]]]
                    groups[_group(lr, Pi, Qi)] += 1
                table[p] = {'places': {'P': nk[0], 'C': nk[1], 'S': nk[2]}, 'classes': ncls, 'mixed_classes': nmixed,
                            'classes_child_and_start_only': ncs, 'mixed_by_group': dict(groups),
                            'guard_count': guard[(p, d)]}
            out['%s d=%d' % (v, d)] = table
    least = {}
    for v in VARIANTS:
        for p in allpops:
            ds = [d for d in range(1, DMAX + 1) if out['%s d=%d' % (v, d)][p]['mixed_classes'] == 0]
            least['%s %s' % (v, p)] = min(ds) if ds else None
    return {'tables': out, 'least_distance_no_confusable_pair': least, 'populations': allpops}


def _popkey(p):
    import re
    m = re.search(r'(\d+)$', p)
    return (p.rstrip('0123456789').strip(), int(m.group(1)) if m else -1)


def _group(lr, Pi, Qi):
    sP = {lr.sid_of[i] for i in Pi}
    sQ = {lr.sid_of[i] for i in Qi}
    if sP & sQ:
        return 'within one structure'
    pairs_P = {lr.structs[s].pair for s in sP}
    pairs_Q = {lr.structs[s].pair for s in sQ}
    if pairs_P & pairs_Q:
        return 'across rounds of one start'
    return 'across starts'


# ============================================================================== farness and pairs

def farness(lr, i):
    rec = lr.structs[lr.sid_of[i]]
    a, b = rec.guard[i - rec.offset]
    return min(a, b), a, b


def item_record(lr, i):
    rec = lr.structs[lr.sid_of[i]]
    T = rec.T
    x, e = T.items[i - rec.offset]
    y = T.other(x, e)
    f, a, b = farness(lr, i)
    made = T.made[x] if T.made is not None else None
    out = {'structure': rec.label, 'population': 'P2 round %s' % rec.round if rec.kind == 'P2' else 'P1 serial',
           'structure_knots': T.n, 'knot': x, 'distinction': e, 'other_holder': y,
           'kind': T.kinds[i - rec.offset], 'round_of_birth_of_knot': made,
           'round_of_birth_of_other_holder': T.made[y] if T.made is not None else None,
           'distance_to_start': a, 'distance_to_member': b if b < 10 ** 6 else None,
           'knot_parents': list(T.parents[x]), 'other_holder_parents': list(T.parents[y])}
    if T.ref_id is not None:
        out['reference_knot'] = T.ref_id[x]
        out['reference_other_holder'] = T.ref_id[y]
    return out


def explicit_renaming(lr, i, j, v, d):
    """An explicit renaming of the look of item i onto that of item j at d, found directly between the two and checked
    place by place (deviations.md, item 19); None when they are not alike."""
    Li, Gi, Ii = lr.look(i, v, d)
    Lj, Gj, Ij = lr.look(j, v, d)
    if Gi.n != Gj.n or sorted(Gi.colour) != sorted(Gj.colour):
        return None
    m = greedy_renaming(Gi, Gj)
    if m is None:
        m = ISO.find_renaming(Gi, Gj)
    if m is None:
        return None
    km, dm = LK.full_renaming(Li, Ii, Lj, Ij, m)
    ok, why = LK.check_renaming(Li, Lj, km, dm)
    if not ok:
        raise AssertionError('explicit renaming failed: %s' % why)
    return LK.renaming_record(Li, Lj, km, dm), LK.look_summary(Li)


def alike_direct(lr, i, j, v, d):
    """Alike at d, decided directly (no class table): used beyond distance 6."""
    Li, Gi, Ii = lr.look(i, v, d) if d <= DMAX else _look_any(lr, i, v, d)
    Lj, Gj, Ij = lr.look(j, v, d) if d <= DMAX else _look_any(lr, j, v, d)
    if Gi.n != Gj.n or sorted(Gi.colour) != sorted(Gj.colour):
        return False
    m = greedy_renaming(Gi, Gj)
    if m is None:
        m = ISO.find_renaming(Gi, Gj)
    if m is None:
        return False
    km, dm = LK.full_renaming(Li, Ii, Lj, Ij, m)
    ok, why = LK.check_renaming(Li, Lj, km, dm)
    if not ok:
        raise AssertionError(why)
    return True


def _look_any(lr, i, v, d):
    rec = lr.structs[lr.sid_of[i]]
    T = rec.T
    x, e = T.items[i - rec.offset]
    L = LK.extract(T, x, e, d, v)
    root, unr = VW.in_look(L, lr.intern_far(v))
    G, info = LK.compress(L, extra=unr)
    return L, G, info


def least_separating(lr, i, j, v, d0, dmax=10):
    for d in range(d0, dmax + 1):
        if not alike_direct(lr, i, j, v, d):
            return d
    return None


def written_pairs(lr, v='full', population='P2'):
    """Run 4: for each d with a confusable pair in the population, the pair of greatest farness."""
    out = {}
    codes = popcodes(lr)
    pops_of_sid = [population_members(c) for c in codes]
    for d in range(1, DMAX + 1):
        cls = lr.cls[(v, d)]
        P = defaultdict(list)
        Q = defaultdict(list)
        for i in range(lr.n_items):
            if population not in pops_of_sid[lr.sid_of[i]]:
                continue
            (P if lr.kinds[i] == 0 else Q)[cls[i]].append(i)
        best = None
        nmixed = 0
        for c in P:
            if c not in Q:
                continue
            nmixed += 1
            bp = max(P[c], key=lambda i: (farness(lr, i)[0], lr.structs[lr.sid_of[i]].T.n, -i))
            bq = max(Q[c], key=lambda i: (farness(lr, i)[0], lr.structs[lr.sid_of[i]].T.n, -i))
            fp = farness(lr, bp)[0]
            fq = farness(lr, bq)[0]
            key = (min(fp, fq), fp + fq, max(lr.structs[lr.sid_of[bp]].T.n, lr.structs[lr.sid_of[bq]].T.n),
                   -min(bp, bq))
            if best is None or key > best[0]:
                best = (key, bp, bq, c)
        if best is None:
            out[d] = None
            continue
        key, bp, bq, c = best
        rn = explicit_renaming(lr, bp, bq, v, d)
        if rn is None:
            raise AssertionError('two places of one class have no direct renaming')
        sep = least_separating(lr, bp, bq, v, d + 1, 10)
        out[d] = {'mixed_classes_in_population': nmixed, 'farness': key[0],
                  'parent_place': item_record(lr, bp), 'other_place': item_record(lr, bq),
                  'group': _group(lr, [bp], [bq]), 'look_at_d': rn[1], 'renaming': rn[0],
                  'least_separating_distance_up_to_10': sep}
    return out


def followed_pair(lr, start, i0, j0, v='full', dmax=10):
    """Follow two places of one start's P2 lineage from round to round (the same knots and distinctions)."""
    rec0 = lr.structs[lr.sid_of[i0]]
    T0 = rec0.T
    xi, ei = T0.items[i0 - rec0.offset]
    rec1 = lr.structs[lr.sid_of[j0]]
    xj, ej = rec1.T.items[j0 - rec1.offset]
    rows = []
    for sid in lr.lineages[start]:
        rec = lr.structs[sid]
        T = rec.T
        a = T.item_index.get((xi, ei))
        b = T.item_index.get((xj, ej))
        if a is None or b is None:
            continue
        a += rec.offset
        b += rec.offset
        sep = None
        alike_upto = 0
        for d in range(1, dmax + 1):
            if alike_direct(lr, a, b, v, d):
                alike_upto = d
            else:
                sep = d
                break
        rows.append({'round': rec.round, 'knots': T.n, 'least_separating_distance': sep,
                     'alike_up_to': alike_upto, 'searched_up_to': dmax})
    return {'start': start, 'places': [[xi, ei, T0.kinds[i0 - rec0.offset]], [xj, ej, rec1.T.kinds[j0 - rec1.offset]]],
            'rows': rows}


# ============================================================================== run 5

def whole_renamings(lr, max_knots=2000):
    out = []
    wintern = {}
    for start in lr.pairs:
        sid = lr.lineages[start][-1]
        rec = lr.structs[sid]
        T = rec.T
        if T.n > max_knots:
            out.append({'start': start, 'round': rec.round, 'knots': T.n, 'tested': False,
                        'reason': 'more than %d knots' % max_knots})
            continue
        sv, depth = VW.unfold(T, 'full', 1, wintern, stable=True)
        st = sv['stable']
        byv = defaultdict(list)
        for k, c in enumerate(st):
            byv[c].append(k)
        mixed = [c for c, its in byv.items()
                 if any(T.kinds[k] == 'P' for k in its) and any(T.kinds[k] != 'P' for k in its)]
        found = []
        tests = 0
        for c in mixed:
            its = byv[c]
            Ps = [k for k in its if T.kinds[k] == 'P']
            Qs = [k for k in its if T.kinds[k] != 'P']
            # every P place against every non-P place of the group would be exhaustive; orbits make it one per orbit
            for p in Ps:
                Gp = AU.whole_graph(T, root=T.items[p])
                for q in Qs:
                    tests += 1
                    Gq = AU.whole_graph(T, root=T.items[q])
                    m = ISO.find_renaming(Gp, Gq)
                    if m is not None:
                        sm = AU.structure_map(T, T, m)
                        if sm is None:
                            raise AssertionError('automorphism did not check')
                        found.append({'parent_place': list(T.items[p]), 'other_place': list(T.items[q]),
                                      'other_kind': T.kinds[q]})
                        break
                if found:
                    break
        out.append({'start': start, 'round': rec.round, 'knots': T.n, 'tested': True,
                    'stable_depth': depth, 'place_classes_by_stable_unfolding': len(byv),
                    'groups_holding_parent_and_other_places': len(mixed), 'searches': tests,
                    'automorphism_carrying_parent_place_to_other': found[:5],
                    'exists': bool(found)})
    return out


def choose_followed(lr, v='full'):
    """Run 4's pair to follow: a confusable pair of one start (one structure, or two rounds of it) in P2 at the greatest
    distance, of greatest farness (deviations.md, item 26).  Returns (d, start, i, j) or None."""
    codes = popcodes(lr)
    for d in range(DMAX, 0, -1):
        cls = lr.cls[(v, d)]
        P = defaultdict(list)
        Q = defaultdict(list)
        for i in range(lr.n_items):
            rec = lr.structs[lr.sid_of[i]]
            if rec.kind != 'P2':
                continue
            (P if lr.kinds[i] == 0 else Q)[cls[i]].append(i)
        best = None
        for c in P:
            if c not in Q:
                continue
            byp = defaultdict(lambda: ([], []))
            for i in P[c]:
                byp[lr.structs[lr.sid_of[i]].pair][0].append(i)
            for i in Q[c]:
                byp[lr.structs[lr.sid_of[i]].pair][1].append(i)
            for start, (a, b) in byp.items():
                if not a or not b:
                    continue
                bp = max(a, key=lambda i: (farness(lr, i)[0], -lr.structs[lr.sid_of[i]].round, -i))
                bq = max(b, key=lambda i: (farness(lr, i)[0], -lr.structs[lr.sid_of[i]].round, -i))
                key = (min(farness(lr, bp)[0], farness(lr, bq)[0]), -bp)
                if best is None or key > best[0]:
                    best = (key, start, bp, bq)
        if best is not None:
            return d, best[1], best[2], best[3]
    return None
