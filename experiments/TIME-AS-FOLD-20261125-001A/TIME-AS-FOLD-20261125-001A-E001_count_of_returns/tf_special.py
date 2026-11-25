"""P4's round-1 reading (the pre-registration's "Settled by construction", item 7) under L2 on the ring starts.

For Ring(5,3), Ring(7,3), Ring(9,3) (and the other ring starts), each choice and each of L2's three base laws, both knot
laws: round 1 under MET and under the control: the candidates of each birth by kind, every birth's (kind, fresh,
demand), the parts after round 1 (members), h after round 1, and the short members in round 2.
Usage: python -B tf_special.py p4
"""
from __future__ import annotations

import sys
from collections import Counter

import tf_common as C
import tf_engine as E
import tf_runs as RN

L2_BASES = ('RING-LAW', 'CAP-3(RETIRE)', 'CAP-3(OFFSHOOT)')


def round1(stars, law):
    S = E.from_stars(stars)
    cands = []
    T = S.copy()
    rec, R0 = E.round_step(T, law)
    # candidates, read on the start (the structure at the start of round 1)
    if law.take is not None:
        for b in rec['births']:
            c = E.candidates(S, law, {'kind': b['kind'], 'parents': tuple(b['parents'])})
            cands.append((b['kind'], len(c) if c is not None else None))
    T2 = T.copy()
    rec2, R1 = E.round_step(T2, law)
    births = sorted(Counter((b['kind'], b['f'], b['D']) for b in rec['births']).items())
    return {'candidates': sorted(Counter(cands).items()), 'births_kind_f_D': births,
            'parts_after_r1': sorted(len(P) for P in R1.parts), 'members_after_r1': list(R1.members),
            'h_after_r1': sorted(set(R1.h.values())), 'short_in_r2': len(rec2['short']),
            'parents_loose_r1': sorted((tuple(b['parents']), tuple(b['loose'])) for b in rec['births'])}


def p4():
    named = C.named_stars()
    rows = []
    for st in RN.RING_STARTS:
        for base in L2_BASES:
            for ch in RN.CHOICES:
                for kl in RN.KNOT_LAWS:
                    met = E.Law.from_base(base, knot_law=kl, take='MET', choice=ch)
                    ctl = E.Law.from_base(base, knot_law=kl)
                    a = round1(named[st], met)
                    b = round1(named[st], ctl)
                    item7 = None
                    if st in ('Ring(5,3)', 'Ring(7,3)', 'Ring(9,3)'):
                        # item 7: an offshoot has exactly two candidates, a join none; the births are the control's in
                        # their parents and loose inputs; the parts after round 1 are unions of the control's with the
                        # same members
                        cand_ok = all((k == 'offshoot' and n == 2) or (k == 'join' and n == 0)
                                      for (k, n), _ in a['candidates'])
                        same_births = a['parents_loose_r1'] == b['parents_loose_r1']
                        same_members = sorted(a['members_after_r1']) == sorted(b['members_after_r1'])
                        item7 = {'candidates_ok': cand_ok, 'births_as_control': same_births,
                                 'same_members_after_r1': same_members,
                                 'fresh_differ': a['births_kind_f_D'] != b['births_kind_f_D']}
                    rows.append({'start': st, 'base': base, 'choice': ch, 'knot_law': kl, 'MET': a, 'control': b,
                                 'item7': item7})
    C.write_json('p4_round1.json', rows)
    C.log('P4 round 1: %d rows' % len(rows))


if __name__ == '__main__':
    C.cap_memory()
    {'p4': p4}[sys.argv[1]]()
