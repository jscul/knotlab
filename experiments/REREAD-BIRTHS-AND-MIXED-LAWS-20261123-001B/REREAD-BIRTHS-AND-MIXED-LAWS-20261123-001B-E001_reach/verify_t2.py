"""Verify every hidden excess found by T2 by full enumeration of the four finished structures (the stage with its laws, the
chosen observers renamed x1..y3, plus the supplied setting births), and say for each one met in a grown stage (t >= 1)
whether the same observer choice already gives a hidden excess at stage 0 of the same history (inherited) or not (new).
Writes verify_t2_<tag>.json.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --tag c2|c3
"""
import argparse
import glob
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402
import verify_excess as ve  # noqa: E402  (brute_joint_all, evaluate_joint)

ap = argparse.ArgumentParser()
ap.add_argument('--tag', default='c2')
args, _ = ap.parse_known_args()
t0 = time.time()
hits = []
for f in sorted(glob.glob(str(c.ART / f't2_hits_targets_{args.tag}_*.jsonl'))) + sorted(glob.glob(str(c.ART / f't2_hits_draws_{args.tag}_*.jsonl'))):
    hits += [json.loads(l) for l in open(f)]
stage0 = {}
for h in hits:
    if h['key']['t'] == 0 and 'si' in h['key']:
        stage0[h['key']['si']] = {tuple(e[0]) for e in h['examples']}
rows = []
for h in hits:
    knots = c.parse_knots(h['knots'])
    for obs, table, score in h['examples']:
        ren = {o: n for o, n in zip(obs, c.OBS)}
        # names x1..y3 not chosen as observers are renamed apart
        other = {m for _, mem in knots for m in mem if m in c.OBS and m not in ren}
        for m in other:
            ren[m] = 'old_' + m
        kn = [(law, tuple(ren.get(m, m) for m in mem)) for law, mem in knots]
        J, nn = ve.brute_joint_all(kn)
        ev = ve.evaluate_joint(J)
        key = h['key']
        inherited = None
        if key['t'] >= 1 and 'si' in key:
            inherited = tuple(obs) in stage0.get(key['si'], set())
        rows.append(dict(key=key, knots=h['knots'], knots_n=h['knots_n'], distinctions=h['distinctions'], observers=obs,
                         score_t2=score, full_enumeration=dict(hidden=ev['hidden'], score=str(ev['score']),
                                                                change=str(ev['change']), words=[int(J[a, b].sum()) for a in (0, 1) for b in (0, 1)],
                                                                distinctions_finished=nn),
                         agrees=ev['hidden'] and str(ev['score']) == score, inherited_from_stage0=inherited))
grown = [r for r in rows if r['key']['t'] >= 1]
smallest = min(rows, key=lambda r: (r['knots_n'], r['distinctions'])) if rows else None
smallest_grown = min(grown, key=lambda r: (r['knots_n'], r['distinctions'])) if grown else None
out = dict(tag=args.tag, stage_hits=len(hits), excess_choices_written=len(rows), all_agree=all(r['agrees'] for r in rows),
           grown=len(grown), grown_inherited=sum(1 for r in grown if r['inherited_from_stage0']),
           grown_new=sum(1 for r in grown if r['inherited_from_stage0'] is False), smallest=smallest,
           smallest_grown=smallest_grown, rows=rows, seconds=round(time.time() - t0, 1))
(c.ART / f'verify_t2_{args.tag}.json').write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: v for k, v in out.items() if k not in ('rows',)}, indent=1, default=str))
