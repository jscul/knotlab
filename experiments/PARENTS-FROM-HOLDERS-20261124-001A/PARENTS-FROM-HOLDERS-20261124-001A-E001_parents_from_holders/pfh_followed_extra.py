"""Addition to run 4 (deviations.md, item 40; not registered): ORD's written-out pair at d = 5 followed from round to round.

    python -B pfh_followed_extra.py     # writes artifacts/.../followed_extra.json
"""
from __future__ import annotations

import json
import resource

import pfh_common as PC
import pfh_report as RP
from pfh_classes import LawRun


def main():
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    PC.check_frozen()
    w = json.loads((PC.OUT / 'pairs_ORD.json').read_text())['written_pairs_P2_full']['5']
    lr = LawRun('ORD', log=lambda *a: None)
    lr.build()
    lr.prepare()
    lab = w['parent_place']['structure']
    rec = [r for r in lr.structs if r.label == lab][0]
    T = rec.T
    i = rec.offset + T.item_index[(w['parent_place']['knot'], w['parent_place']['distinction'])]
    rec2 = [r for r in lr.structs if r.label == w['other_place']['structure']][0]
    j = rec2.offset + rec2.T.item_index[(w['other_place']['knot'], w['other_place']['distinction'])]
    fol = RP.followed_pair(lr, rec.pair, i, j, 'full', 10)
    fol['pair'] = [w['parent_place'], w['other_place']]
    fol['note'] = 'addition to run 4, not registered (deviations.md item 40)'
    PC.write_json(PC.OUT / 'followed_extra.json', {'ORD': fol})
    print(json.dumps(fol['rows']))


if __name__ == '__main__':
    main()
