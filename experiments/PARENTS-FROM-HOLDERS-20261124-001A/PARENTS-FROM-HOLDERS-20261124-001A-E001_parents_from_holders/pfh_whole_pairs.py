"""Addition to run 4 (deviations.md, item 39; not registered): for each law, the confusable pairs within one structure
at d = 6 (full look) that a renaming of the whole structure exchanges.  Reads the class table that pfh_run.py left in
the session scratchpad.

    python -B pfh_whole_pairs.py        # writes artifacts/.../whole_pairs.json
"""
from __future__ import annotations

import gzip
import pickle
import resource
from array import array
from collections import Counter, defaultdict

import pfh_auto as AU
import pfh_common as PC
import pfh_iso as ISO
from pfh_classes import LawRun


def law_pairs(short, d=6):
    lr = LawRun(short, log=lambda *a: None)
    lr.build()
    meta = pickle.load(gzip.open(PC.SCRATCH / ('classes_%s.pkl.gz' % short)))
    if meta['labels'] != [r.label for r in lr.structs]:
        raise RuntimeError('class table does not match the rebuilt structures')
    cls = array('i')
    cls.frombytes(meta['cls']['full %d' % d])
    P = defaultdict(list)
    Q = defaultdict(list)
    for i in range(lr.n_items):
        (P if lr.kinds[i] == 0 else Q)[cls[i]].append(i)
    res = Counter()
    rows = []
    for c in sorted(P):
        if c not in Q:
            continue
        byS = defaultdict(lambda: ([], []))
        for i in P[c]:
            byS[lr.sid_of[i]][0].append(i)
        for i in Q[c]:
            byS[lr.sid_of[i]][1].append(i)
        pair = next(((s, a[0], b[0]) for s, (a, b) in sorted(byS.items()) if a and b), None)
        if pair is None:
            res['mixed classes with no pair within one structure'] += 1
            continue
        s, p, q = pair
        rec = lr.structs[s]
        T = rec.T
        xp = T.items[p - rec.offset]
        xq = T.items[q - rec.offset]
        m = ISO.find_renaming(AU.whole_graph(T, root=xp), AU.whole_graph(T, root=xq))
        ok = m is not None and AU.structure_map(T, T, m) is not None
        res['exchanged by a renaming of the whole structure' if ok else 'not exchanged by any renaming of the whole structure'] += 1
        rows.append({'structure': rec.label, 'knots': T.n, 'parent_place': list(xp), 'other_place': list(xq),
                     'other_kind': T.kinds[q - rec.offset], 'whole_structure_renaming': ok})
    return {'distance': d, 'counts': dict(res), 'pairs': rows}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    PC.check_frozen()
    import sys
    laws = sys.argv[1:] or ['F1O', 'F1R', 'R3W', 'ORD']
    path = PC.OUT / 'whole_pairs.json'
    import json
    out = json.loads(path.read_text()) if path.exists() else {}
    out['note'] = 'addition to run 4, not registered (deviations.md item 39)'
    for short in laws:
        out[short] = law_pairs(short)
        print(short, out[short]['counts'], flush=True)
    PC.write_json(path, out)


if __name__ == '__main__':
    main()
