"""Test (b): the funded sparse draws of the review-leads epic's ticket A (lib.p3_draws(), seed 2026112301; funded = the
recorded driver's first round extends: 280 per law), under ordinary growth (the recorded driver lib.grow) and rule Q with
conventions O and N, 12 rounds or 5,000 knots: outcome, births per round, growth kind, re-reading births per round, the
largest number of holders at each stage, first failing step of the operator test.  Every knot has the run's law:
'parity' (even parity; under rule Q a birth whose parity is implied by the old knots, by GF(2) elimination, gets no fresh
distinction) or 'nae' (no closing).

Rule Q runs with ticket A's next-round cap shortcut (bound_next=True, deviations A); nothing reported here depends on
the fresh counts it flags as lower bounds.  The stars up to the stage after the last stage with at most 22 distinctions
are kept (prefixes/b_<law>_arm<A>.jsonl.gz) for the extension check of q_rowg.py.

One JSON line per funded draw to draws_<law>_arm<A>.jsonl.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --law L --arm A
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qlaw  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--law', required=True, choices=('nae', 'parity'))
    ap.add_argument('--arm', type=int, required=True, choices=(0, 1, 2, 3))
    args = ap.parse_args()
    t_run = time.time()
    rows, prefixes = [], []
    drawn = 0
    for dr in qlaw.lib.p3_draws():
        if dr['arm'] != args.arm:
            continue
        drawn += 1
        t0 = time.time()
        h, ref = qlaw.reference_summary(dr['stars'], args.law)
        if ref['outcome'] == 'stall' or not h['births']:
            continue
        row = dict(arm=dr['arm'], draw=dr['draw'], n=dr['n'], law=args.law, ordinary=ref)
        for conv in ('O', 'N'):
            g = qlaw.run_ab(dr['stars'], args.law, conv, reread=True, bound_next=True)
            q = qlaw.history_summary(g)
            q['stars_sha256'] = qlaw.stars_digest(g.stars)
            row['Q' + conv] = q
            pre = qlaw.small_prefix(g.stars, g.n_at)
            if pre is not None and not any(g.rounds[t]['fresh_lower_bound'] for t in range(len(pre['n_at']) - 1)):
                pre.update(test='b', arm=dr['arm'], draw=dr['draw'], law=args.law, conv=conv,
                           reread_births=[g.rounds[t]['reread_births'] for t in range(len(pre['n_at']) - 1)])
                prefixes.append(pre)
        row['seconds'] = round(time.time() - t0, 2)
        rows.append(row)
    tag = f'{args.law}_arm{args.arm}'
    qlaw.dump(qlaw.ART / f'draws_{tag}.jsonl', rows)
    qlaw.dump(qlaw.ART / 'prefixes' / f'b_{tag}.jsonl.gz', prefixes)
    print(json.dumps(dict(run=tag, drawn=drawn, funded=len(rows), seconds=round(time.time() - t_run, 1),
                          slowest=max((r['seconds'] for r in rows), default=None))))


if __name__ == '__main__':
    main()
