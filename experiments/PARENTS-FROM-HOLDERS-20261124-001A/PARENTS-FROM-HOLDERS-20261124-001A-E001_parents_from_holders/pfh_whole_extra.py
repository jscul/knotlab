"""Addition to run 5 (deviations.md, item 37; not registered): the whole-structure test of P8 on the last round of each P2
lineage with at most 2,000 knots.  Same method as pfh_report.whole_renamings.

    python -B pfh_whole_extra.py        # writes artifacts/.../whole_extra.json
"""
from __future__ import annotations

import resource
import time
from collections import defaultdict

import pfh_auto as AU
import pfh_common as PC
import pfh_iso as ISO
import pfh_pop as PP
import pfh_views as VW
from pfh_struct import Struct


def test(T):
    wintern = {}
    sv, depth = VW.unfold(T, 'full', 1, wintern, stable=True)
    st = sv['stable']
    byv = defaultdict(list)
    for k, c in enumerate(st):
        byv[c].append(k)
    mixed = [c for c, its in byv.items()
             if any(T.kinds[k] == 'P' for k in its) and any(T.kinds[k] != 'P' for k in its)]
    found = []
    searches = 0
    for c in mixed:
        its = byv[c]
        for p in [k for k in its if T.kinds[k] == 'P']:
            Gp = AU.whole_graph(T, root=T.items[p])
            for q in [k for k in its if T.kinds[k] != 'P']:
                searches += 1
                m = ISO.find_renaming(Gp, AU.whole_graph(T, root=T.items[q]))
                if m is not None:
                    if AU.structure_map(T, T, m) is None:
                        raise AssertionError('automorphism did not check')
                    found.append([list(T.items[p]), list(T.items[q]), T.kinds[q]])
                    break
            if found:
                break
    return {'stable_depth': depth, 'place_classes_by_stable_unfolding': len(byv),
            'groups_holding_parent_and_other_places': len(mixed), 'searches': searches,
            'found': found[:5], 'exists': bool(found)}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    PC.check_frozen()
    t0 = time.time()
    rows = []
    for start, fam, rc in PC.gate_pairs():
        S0, rounds, ev = PP.p2_lineage(start, fam, rc)
        last = None
        for t, S in enumerate(rounds, 1):
            if S.n_knots <= 2000:
                last = (t, S)
        t, S = last
        T = Struct.from_engine(S)
        r = test(T)
        r.update({'start': start, 'law': PC.LAW_NAMES[fam], 'round': t, 'knots': T.n,
                  'is_final_P2_structure': t == len(rounds)})
        rows.append(r)
        print(start, PC.LAW_SHORT[fam], 'round', t, 'knots', T.n, 'mixed groups', r['groups_holding_parent_and_other_places'],
              'exists', r['exists'], flush=True)
    PC.write_json(PC.OUT / 'whole_extra.json', {'note': 'addition to run 5, not registered (deviations.md item 37)',
                                                 'rows': rows, 'seconds': round(time.time() - t0, 1)})


if __name__ == '__main__':
    main()
