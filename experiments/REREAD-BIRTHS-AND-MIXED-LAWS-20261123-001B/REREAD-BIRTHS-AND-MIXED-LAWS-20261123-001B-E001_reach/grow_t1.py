"""Grow every founder start and test T1 (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B, "Growth", "T1").

For each founder start (starts.jsonl, written by build_targets.py): ordinary growth by the recorded operator under the
not-all-equal structure rule (every start holds a not-all-equal founder; checked), 3 rounds or until a stage passes 20
distinctions.  Founders keep the target's laws and signs; every assignment of parity (even) or not-all-equal to the
newborns is enumerated (at most 4,096 per history, else 4,096 drawn by seed 2026112340).  At every stage and for every
assignment (restricted to the newborns of that stage) the table of allowed words on the target's six observer distinctions,
every other distinction forgotten, is computed exactly and tested: (i) same support as the target's; (ii) proportional to
it; (iii) hidden excess with the supplied setting births.  The gate "support never shrinks along any history" is checked
for every assignment at every stage.

One JSON line per history to t1_<lo>-<hi>.jsonl; every (ii) or (iii) hit in full to t1_hits_<lo>-<hi>.jsonl.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --lo 0 --hi 5000 [--choices 2|3]
"""
import argparse
import itertools
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lo', type=int, required=True)
    ap.add_argument('--hi', type=int, required=True)
    ap.add_argument('--choices', type=int, default=2, choices=(2, 3))
    ap.add_argument('--tids', type=str, default=None, help='comma list: only these targets')
    ap.add_argument('--tag', type=str, default='')
    args = ap.parse_args()
    choices = ('even', 'nae') if args.choices == 2 else ('even', 'odd', 'nae')
    t0 = time.time()
    targets = {t['tid']: t for t in json.loads((c.ART / 'targets.json').read_text())}
    tk = {t['tid']: t['knots'] for t in c.load_targets()}
    starts = [json.loads(l) for l in (c.ART / 'starts.jsonl').open()]
    only = None if args.tids is None else {int(x) for x in args.tids.split(',')}
    ev = c.Evaluator()
    lines, hits = [], []
    for si in range(args.lo, min(args.hi, len(starts))):
        s = starts[si]
        if only is not None and s['tid'] not in only:
            continue
        tgt = targets[s['tid']]
        Ttar = np.array(tgt['table'], dtype=np.int64)
        sup_tar = c.support_key(Ttar)
        ks = tk[s['tid']]
        stars, laws, names, obs, sub = c.start_stars(ks, s['mask'])
        assert any(l == 'nae' for l in laws)
        h = c.grow(stars, 'nae')
        st = h['stars']
        nf = h['n_at'][0]
        n_new = h['n_at'][-1] - nf
        A, mode = c.assignments(n_new, (s['tid'], s['mask']), k=len(choices))
        rec = dict(si=si, tid=s['tid'], mask=s['mask'], founders=nf, n_at=h['n_at'], D_at=h['D_at'], outcome=h['outcome'],
                   newborns=n_new, assignments=int(A.shape[0]), mode=mode,
                   births=[[(len(p), len(f)) for p, _, f in r] for r in h['births']], stages=[])
        stage0_excess = None
        prev_sup = None   # map restricted assignment bytes -> support at previous stage
        shrink = 0
        changed = 0
        for t, n in enumerate(h['n_at']):
            nb = n - nf
            R = np.unique(A[:, :nb], axis=0) if nb else np.zeros((1, 0), dtype=np.int8)
            T = c.stage_tables(st, laws, nf, n, R, obs, choices=choices)
            sups = [c.support_key(row) for row in T]
            # support along every history: compare with the stage before, same assignment of the earlier newborns
            cur = {}
            for r, sp in zip(R, sups):
                cur[r.tobytes()] = sp
                if prev_sup is not None:
                    pk = r[:prev_nb].tobytes()
                    ps = prev_sup[pk]
                    if not set(ps) <= set(sp):
                        shrink += 1
                    if set(ps) != set(sp):
                        changed += 1
            prev_sup, prev_nb = cur, nb
            same_sup = [sp == sup_tar for sp in sups]
            prop = [same_sup[i] and c.proportional(T[i], Ttar) for i in range(len(R))]
            norm = [c.normalize(row) for row in T]
            evs = ev.run(norm)
            hid = [e[0] and e[1] for e in evs]
            exc = [c.is_excess(e) for e in evs]
            best_f = max([e[2] for e in evs if e[0] and e[1] and e[2] is not None], default=None)
            best_x = max([e[3] for e in evs if e[3] is not None], default=None)
            distinct = len({x.tobytes() if x.dtype != object else repr(tuple(x)) for x in norm})
            if t == 0:
                stage0_excess = bool(exc[0])
            new_exc = [e and not stage0_excess for e in exc]
            rec['stages'].append(dict(t=t, knots=n, D=h['D_at'][t], tables=len(R), distinct_tables=distinct,
                                      support_equal=sum(same_sup), proportional=sum(prop), hidden=sum(hid),
                                      excess=sum(exc), new_excess=sum(new_exc), best_hidden_float=best_f,
                                      best_hidden_exact=None if best_x is None else str(best_x),
                                      support_size=sorted({len(sp) for sp in sups})))
            # written in full: every table proportional to the target's, every excess in a history whose start has
            # none (at most 50 of each kind per stage, all counted above); one excess per stage otherwise
            wrote = Counter()
            for i in range(len(R)):
                kind = 'proportional' if prop[i] else ('new_excess' if new_exc[i] else ('excess' if exc[i] else None))
                if kind is None:
                    continue
                wrote[kind] += 1
                if wrote[kind] > (1 if kind == 'excess' else 50):
                    continue
                hits.append(dict(si=si, tid=s['tid'], mask=s['mask'], t=t, kind=kind, excess=bool(exc[i]),
                                 stage0_excess=stage0_excess, newborn_laws=[choices[int(v)] for v in R[i]],
                                 knots=[(laws[k] if k < nf else choices[int(R[i][k - nf])],
                                         [names[d] if d < len(names) else f'f{d}' for d in st[k]]) for k in range(n)],
                                 table=[int(v) for v in T[i]], eval=[evs[i][0], evs[i][1], evs[i][2],
                                                                    None if evs[i][3] is None else str(evs[i][3])]))
        rec['stage0_excess'] = stage0_excess
        rec['support_shrinks'] = shrink
        rec['support_changes'] = changed
        rec['start_support_size'] = len(c.support_key(c.stage_tables(st, laws, nf, nf, np.zeros((1, 0), np.int8), obs)[0]))
        rec['target_support_size'] = len(sup_tar)
        lines.append(rec)
    tag = args.tag or (f'c{args.choices}')
    c.dump(c.ART / f't1_{tag}_{args.lo:05d}-{args.hi:05d}.jsonl', lines)
    c.dump(c.ART / f't1_hits_{tag}_{args.lo:05d}-{args.hi:05d}.jsonl', hits)
    print(json.dumps(dict(lo=args.lo, hi=args.hi, histories=len(lines), hits=len(hits), exact_calls=ev.exact_calls,
                          seconds=round(time.time() - t0, 1))))


if __name__ == '__main__':
    main()
