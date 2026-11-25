"""The expected dependence case birth by birth (brief, item 4), and a reported refinement of check (c).

For the first pair (registered order) with a meeting only through made knots and a course difference of each item of
MET-SOLE with FLOOR1/PARENT-OWING/CANCEL-OFFSHOOT (L10) on the ring starts and the unsymmetric ring, both knot laws:
the values used at X's births (RD 3.3) in both runs (Y usable, Y barred), round by round from s + 1 to the first
differing round, entry by entry, with the first differing entry marked; the knots of its differing part with their
descent, kind, parents and round; the linking knot's ancestry. Also, for every such pair of these items and of
L02's: whether the structure after round s has a renaming exchanging X and Y that fixes every linking knot AND every
start knot (deviations 34; reported beside the registered check, never in place of it).

  python -B expected_listing.py
"""
import sys

sys.dont_write_bytecode = True

import json
from collections import Counter

import common
from common import log
import eng
import read
import wbc
from read import View


def values_listing(vO, vA, s, t_end):
    lines = []
    for t in range(s + 1, t_end + 1):
        EO, EA = read.values(vO, t), read.values(vA, t)
        first = wbc.first_difference(EO, EA)
        lines.append('  round %d: %d entries (Y barred), %d (Y usable)%s' % (
            t, len(EO), len(EA), '' if first is None else '; first differing entry: step %d %s' % (
                first['step'], first['kind'])))
        for eo, ea in wbc.align(EO, EA):
            e = eo or ea
            if e['kind'] in ('group', 'member', 'act', 'roundwide'):
                continue
            mark = '   ' if (eo is not None and ea is not None and eo['value'] == ea['value']) else '>> '
            lines.append('   %s%s %s: barred %s | usable %s' % (mark, e['kind'], e['pos'][1] if len(e['pos']) > 1
                                                                 else '', eo and eo['value'], ea and ea['value']))
    return lines


def main():
    common.check_frozen()
    st = common.load('starts.json')
    stars = dict(st['stars'])
    stars[st['extra']['name']] = st['extra']['stars']
    fam = {L['id']: L for L in common.load('family.json')['search']}
    lines = []
    extra = []
    for lid in ('L10', 'L02'):
        L = fam[lid]
        for sname in ('Ring(5,3)', 'Ring(5,3)+1', 'D2(5,3)', 'Ring(7,3)', 'Ring(5,3)+1+2'):
            for kl in ('parity', 'nae'):
                law = eng.Law(L['ration'], L['treatment'], L['take'], kl)
                runA = eng.Run(law, stars=stars[sname])
                keysA = read.Keys(runA)
                cnt = Counter()
                listed = False
                for s in (3, 4):
                    R = runA.recs[s]['roster']
                    parts = eng.roster_parts(R)
                    mp = {u: i for i, P in enumerate(parts) for u in P}
                    cls = eng.classes_of_parts(runA.snaps[s], parts)
                    bits = read.desc_bits(runA, s, mp)
                    meet = read.first_meetings(runA, s, bits)
                    pairs = sorted(((i, j) for i in range(len(parts)) for j in range(len(parts))
                                    if i != j and cls[i] != cls[j] and (min(i, j), max(i, j)) in meet),
                                   key=lambda ij: (min(parts[ij[0]]), min(parts[ij[1]])))
                    for i, j in pairs:
                        t = meet[(min(i, j), max(i, j))][0]
                        X, Y = parts[i], parts[j]
                        vA = View(runA, keysA, bits, i, j, s, X, Y)
                        Lk = read.linking(vA, t, read.RoundIndex(runA.recs[t - 1], bits),
                                          read.ancestor_bits(runA.snaps[t]))
                        if not Lk['strict']:
                            continue
                        fixed = [x['knot'] for x in Lk['linking'] if x['made'] <= s]
                        S = runA.snaps[s]
                        both = read.symmetry_exchanging(S, X, Y, sorted(set(fixed) | set(range(S.n_start))))
                        cnt['strict'] += 1
                        cnt['fixing start knots too: %s' % both['answer']] += 1
                        if lid != 'L10' or listed:
                            continue
                        r0 = eng.Run(law, base=runA, base_round=s, bar=list(Y))
                        k0 = read.Keys(r0, base=keysA)
                        b0 = read.desc_bits(r0, s, mp)
                        v0 = View(r0, k0, b0, i, j, s, X, Y)
                        last = min(runA.rounds_read, r0.rounds_read)
                        fd = read.attribution(v0, vA, s, last)
                        if fd is None:
                            continue
                        listed = True
                        lines.append('=== %s, %s (%s); s = %d; X = %s, Y = %s; meeting round %d (%s)' % (
                            sname, law.name(), lid, s, list(X), list(Y), t, '/'.join(meet[(min(i, j), max(i, j))][1])))
                        for x in Lk['linking']:
                            lines.append('  linking knot %d: made in round %d, %s of %s, %s; ancestry %s' % (
                                x['knot'], x['made'], x['kind'], x['parents'], x['class'], x['ancestry']))
                            for ld in x['linking_distinctions']:
                                lines.append('    linking distinction %d: holders %s' % (ld['d'], ld['holders']))
                        lines.append('  run with Y barred: rounds read %d, meeting %s' % (
                            r0.rounds_read, read.first_meetings(r0, s, b0).get((min(i, j), max(i, j)))))
                        lines += values_listing(v0, vA, s, fd['round'])
                        lines.append('  first differing used value: round %d, step %d, %s; barred %s; usable %s; '
                                     'class %s' % (fd['round'], fd['step'], fd['kind'], fd['value_A'],
                                                   fd['value_B'], fd['class']))
                        inv = {k: u for u, k in enumerate(keysA.k)}
                        for x in fd['part']:
                            u = inv.get(x[0])
                            Sx = runA.snaps[fd['round']]
                            if u is not None:
                                lines.append('    differing part: knot %d (%s), %s of %s, round %d; places %d' % (
                                    u, x[1], Sx.kind[u], list(Sx.parents[u]), Sx.made[u], len(Sx.places[u])))
                            else:
                                lines.append('    differing part: %s (in the barred run only)' % (x,))
                        J = [u for u in range(runA.snaps[t].n_knots) if runA.snaps[t].made[u] == t
                             and set(runA.snaps[t].parents[u]) == set(X)]
                        for u in J:
                            b = [bb for bb in runA.recs[t - 1]['births'] if bb['id'] == u][0]
                            lines.append('  X\'s join at round %d (run A): knot %d, D = %d, p = %d, f = %d' % (
                                t, u, b['D'], b['p'], b['f']))
                extra.append({'law': lid, 'start': sname, 'knot_law': kl, 'counts': dict(cnt)})
                log(lid, sname, kl, dict(cnt))
    with open(common.out_path('expected_case_listing.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    common.write_json('check_c_fixing_start_knots.json', extra)


if __name__ == '__main__':
    main()
