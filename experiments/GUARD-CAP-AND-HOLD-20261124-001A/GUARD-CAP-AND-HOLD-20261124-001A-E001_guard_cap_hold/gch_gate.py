"""Run item 1, the gate: this engine's own complete rounds, computed through the plan (GCH section 1), against the
reference engine, structure by structure.

For every start and law of the runs, after each round 1 to max(6, R) (R the largest last round any registered cutoff
needs; fewer where the growth has stopped), the incidence structures of knots and distinctions of the two engines must
be exactly isomorphic, with each knot coloured by its round of birth, its demand D, its fresh count f, its usable and
barred fresh counts, and what it keeps as a stayer in the latest round; distinctions coloured by barred or not.  Each
round's multiset of births (parents, D, f, usable, barred) and of stayers' kept counts is also compared directly.  An
isomorphism is accepted only after it has been verified edge by edge.  Three altered controls must be rejected
(pre-registration, run 1).  The start clause's condition is asserted for every start and law; the gate stops if it
fails.

    python -B gch_gate.py            # writes artifacts/.../gate.json
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

import lr_core as C
import lr_laws as L
import lr_reference as RF
from gch_configs import FAMILY_NAMES, gate_pairs, CAP3W, CAP3WF, R3H

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET_C = ROOT / 'experiments' / 'RING-IN-BALANCE-20261123-001C' / 'RING-IN-BALANCE-20261123-001C-E001_no_round'
sys.path.insert(0, str(TICKET_C))
import iso  # noqa: E402  (ticket C's exact isomorphism test, read-only reuse)

OUT = ROOT / 'artifacts' / 'GUARD-CAP-AND-HOLD-20261124-001A' / 'GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold'


def graph(places, holders, barred, colour):
    n = len(places)
    col = [iso.stable_int(('k',) + tuple(colour[x])) for x in range(n)]
    adj = [[] for _ in range(n)]
    lev = [colour[x][0] for x in range(n)]
    for d, hs in enumerate(holders):
        j = len(col)
        col.append(iso.stable_int(('d', bool(barred[d]) and len(hs) == 1)))
        adj.append([])
        lev.append(None)
        for x in hs:
            adj[x].append(j)
            adj[j].append(x)
    return iso.Graph(col, adj, lev)


def own_colours(S):
    col = []
    for x in range(len(S.places)):
        if S.born[x] == 0:
            col.append((0, None, None, None, None, S.held.get(x, 0)))
        else:
            f, uf = S.fu[x]
            col.append((S.born[x], S.D[x], f, uf, f - uf, S.held.get(x, 0)))
    return col


def ref_colours(S, birth_info, held):
    col = []
    for x in range(S.n_knots):
        if S.made[x] == 0:
            col.append((0, None, None, None, None, held.get(x, 0)))
        else:
            b = birth_info[x]
            col.append((S.made[x], b['D'], b['f'], b['usable'], b['barred'], held.get(x, 0)))
    return col


def round_multisets_own(S, rnd):
    births = Counter((len(S.parents[x]), S.D[x], S.fu[x][0], S.fu[x][1], S.fu[x][0] - S.fu[x][1])
                     for x in range(len(S.places)) if S.born[x] == rnd)
    return births, Counter(S.held.values())


def round_multisets_ref(rec):
    births = Counter((len(b['parents']), b['D'], b['f'], b['usable'], b['barred']) for b in rec['births'])
    return births, Counter(rec.get('held', {}).values())


def demand_diagnosis(Sr, rec):
    """For the reference's round just made: for each new knot, the groups of its demand roster (shared definitions
    step 6: new knots with holding 1, old members still holding a usable distinction) that contain it, split into
    groups of new knots only and groups that also hold an old member (a waiter or a stayer)."""
    E = RF.E
    new = {b['id'] for b in rec['births']}
    old = []
    for u in sorted(Sr.live):
        h, k = Sr.hk(u)
        if h > 0 and u not in new and Sr.made[u] < rec['round']:
            old.append((u, h, k))
    mem = [(x, 1, 0) for x in sorted(new)] + old
    ros = E.build_roster(Sr, mem)
    groups = E.groups_from(ros.members, ros.maxsets)
    oldset = {u for u, _, _ in old}
    out = {}
    for x in new:
        gs = [g for g in groups if x in g]
        out[x] = {'new_only': sum(1 for g in gs if not oldset.intersection(g)),
                  'with_old_member': sum(1 for g in gs if oldset.intersection(g)),
                  'old_members': sorted({u for g in gs for u in g if u in oldset})}
    return out


def compare_pair(start, fam, rounds, own_fam=None, max_knots=40000):
    """own_fam: the law the engine's own rounds use (differs from fam only in the altered controls)."""
    stars = C.start_stars(start)
    law = RF.ref_law(*fam)
    ofam = own_fam or fam
    Sr = RF.E.from_stars(stars)
    So = C.Str(stars)
    info = {}
    rows = []
    ok = True
    first_fail = None
    quiet = 0
    for t in range(1, rounds + 1):
        Sr, rec = RF.E.round_step(Sr, law)
        for b in rec['births']:
            info[b['id']] = b
        orec = C.own_round(So, *ofam)
        g1 = graph(So.places, So.holders, So.barred, own_colours(So))
        g2 = graph(Sr.places, Sr.holders, Sr.barred, ref_colours(Sr, info, rec.get('held', {})))
        same = iso.isomorphism(g1, g2) is not None
        mo, so_ = round_multisets_own(So, t)
        mr, sr = round_multisets_ref(rec)
        same_ms = (mo == mr) and (so_ == sr) and (sorted(orec['retired']) != None) and \
            (len(orec['retired']) == len(rec.get('retired', [])))
        good = same and same_ms
        # the same comparison with D left out: structure, f, usable and barred counts, stayers
        co = [c[:1] + (None,) + c[2:] for c in own_colours(So)]
        cr = [c[:1] + (None,) + c[2:] for c in ref_colours(Sr, info, rec.get('held', {}))]
        same_noD = iso.isomorphism(graph(So.places, So.holders, So.barred, co),
                                   graph(Sr.places, Sr.holders, Sr.barred, cr)) is not None
        strip = lambda ms: Counter((k[0], k[2], k[3], k[4]) for k in ms.elements())
        same_ms_noD = strip(mo) == strip(mr) and so_ == sr
        row = {'round': t, 'iso': same, 'multisets_equal': same_ms, 'iso_without_D': same_noD,
               'multisets_equal_without_D': same_ms_noD, 'knots': Sr.n_knots,
               'births': rec['n_births'], 'stayers': len(rec.get('held', {})), 'short': len(rec['short']),
               'retired': len(rec.get('retired', [])),
               'D_values': sorted(Counter(b['D'] for b in rec['births']).items())}
        if mo != mr:
            # where D differs: does the reference's demand roster hold groups with an old member that the plan's
            # demand (among one reading's births) leaves out?  Checked birth by birth: plan D + groups with an old
            # member == reference D, with the plan's D taken as the groups of new knots only.
            dg = demand_diagnosis(Sr, rec)
            diffs = [b for b in rec['births'] if dg[b['id']]['with_old_member']]
            row['D_diagnosis'] = {
                'births_whose_reference_demand_has_a_group_with_an_old_member': len(diffs),
                'reference_D_equals_new_only_plus_with_old': all(
                    dg[b['id']]['new_only'] + dg[b['id']]['with_old_member'] == b['D'] for b in rec['births']),
                'own_multiset_equals_reference_with_old_member_groups_removed':
                    mo == Counter((len(b['parents']), dg[b['id']]['new_only'], b['f'], b['usable'], b['barred'])
                                  for b in rec['births']),
                'old_members_in_those_groups_are_stayers': all(
                    all(u in rec.get('held', {}) for u in dg[b['id']]['old_members']) for b in diffs),
                'example': [{'birth': b['id'], 'parents': b['parents'], 'reference_D': b['D'],
                             'groups_new_only': dg[b['id']]['new_only'],
                             'groups_with_old_member': dg[b['id']]['with_old_member'],
                             'old_members': dg[b['id']]['old_members']} for b in diffs[:3]]}
        rows.append(row)
        if not good and first_fail is None:
            first_fail = t
        ok &= good
        if rec.get('stopped') or Sr.n_knots > max_knots:
            break
        if rec['n_births'] == 0 and not rec.get('retired'):
            quiet += 1
            if quiet >= 2:
                break
        else:
            quiet = 0
    return ok, rows, first_fail


def main():
    t0 = time.time()
    res = {'pairs': [], 'controls': [], 'start_clause': []}
    all_ok = True
    for (start, fam), cuts in sorted(gate_pairs().items(), key=lambda kv: (FAMILY_NAMES[kv[0][1]], kv[0][0])):
        ref1 = RF.RefData(C.start_stars(start), fam[0], fam[1], min(cuts), release=fam[2], fillers=fam[3])
        law = L.make_law(ref1, 'R3')
        bad = law.start_clause_condition()
        res['start_clause'].append({'start': start, 'law': FAMILY_NAMES[fam], 'violations': bad})
        if bad:
            print('START CLAUSE FAILS', start, FAMILY_NAMES[fam], bad, flush=True)
            res['pass'] = False
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / 'gate.json').write_text(json.dumps(res, indent=1) + '\n')
            sys.exit(1)
        Rmax = max(RF.RefData(C.start_stars(start), fam[0], fam[1], r, release=fam[2], fillers=fam[3]).R
                   for r in sorted(cuts))
        rounds = max(6, Rmax)
        ok, rows, ff = compare_pair(start, fam, rounds)
        all_ok &= ok
        res['pairs'].append({'start': start, 'law': FAMILY_NAMES[fam], 'family': list(fam), 'cutoffs': sorted(cuts),
                             'R_max': Rmax, 'rounds_checked': rows[-1]['round'], 'pass': ok, 'first_fail': ff,
                             'rows': rows})
        print(start, FAMILY_NAMES[fam], 'cutoffs', sorted(cuts), 'R', Rmax, 'rounds', rows[-1]['round'],
              'PASS' if ok else 'FAIL at %s' % ff, flush=True)
    for name, start, fam, own in [('RELEASE for HOLD', 'D2(4,3)', R3H, ('RATION-3', 'CANCEL-WAIT', 'RELEASE', False)),
                                  ('a fixed three for the cap', 'D2(4,3)', CAP3W, ('RATION-3', 'CANCEL-WAIT', 'RELEASE',
                                                                                  False)),
                                  ('the fillers left out', 'D2(4,3)', CAP3WF, ('CAP-3', 'CANCEL-WAIT', 'RELEASE', False))]:
        ok, rows, ff = compare_pair(start, fam, 6, own_fam=own)
        res['controls'].append({'control': name, 'start': start, 'law': FAMILY_NAMES[fam], 'own_law': list(own),
                                'rejected': not ok, 'rejected_at_round': ff,
                                'iso_at_that_round': rows[ff - 1]['iso'] if ff else None,
                                'multisets_at_that_round': rows[ff - 1]['multisets_equal'] if ff else None})
        print('control', res['controls'][-1], flush=True)
    res['pass'] = all_ok and all(c['rejected'] for c in res['controls'])
    for p in res['pairs']:
        p['pass_without_D'] = all(r['iso_without_D'] and r['multisets_equal_without_D'] for r in p['rows'])
        p['D_differs_only_by_groups_with_an_old_member'] = all(
            r['D_diagnosis']['own_multiset_equals_reference_with_old_member_groups_removed']
            for r in p['rows'] if 'D_diagnosis' in r)
    res['pass_without_D'] = all(p['pass_without_D'] for p in res['pairs']) and \
        all(c['rejected'] for c in res['controls'])
    res['pairs_where_D_differs'] = [[p['start'], p['law'], [r['round'] for r in p['rows']
                                                            if not (r['iso'] and r['multisets_equal'])]]
                                    for p in res['pairs'] if not p['pass']]
    res['D_differences_explained'] = all(p['D_differs_only_by_groups_with_an_old_member'] for p in res['pairs'])
    res['n_pairs'] = len(res['pairs'])
    res['n_rounds_compared'] = sum(len(p['rows']) for p in res['pairs'])
    res['iso_stats'] = dict(iso.STATS)
    res['seconds'] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'gate.json').write_text(json.dumps(res, indent=1) + '\n')
    print('GATE', 'PASS' if res['pass'] else 'FAIL', res['n_pairs'], 'pairs', res['n_rounds_compared'], 'rounds',
          res['seconds'], 's')


if __name__ == '__main__':
    main()
