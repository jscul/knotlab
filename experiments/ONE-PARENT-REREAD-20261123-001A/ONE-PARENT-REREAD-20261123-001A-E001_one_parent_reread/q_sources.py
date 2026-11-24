"""Test (a): the seven recorded sources of the review-leads epic's ticket A (lib.recorded_sources()) under the
not-all-equal law, ordinary growth (the recorded driver lib.grow) and rule Q with conventions O and N, to 12 rounds or
5,000 knots: re-reading births per round, knots per stage, births per round, growth kind, the largest number of holders
of a distinction at each stage, outcome, first failing step of the operator test.

Rule Q runs with ticket A's next-round cap shortcut (bound_next=True, deviations A): when the round after a round is
certain to be capped, that round's fresh counts are lower bounds (flagged) and the history ends with a cap; nothing
reported here depends on those fresh counts.  The stars up to the stage after the last stage with at most 22
distinctions are kept for the extension check of q_rowg.py.

One JSON line per source and rule to sources.jsonl.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> [--law nae]
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
    ap.add_argument('--law', default='nae', choices=('nae', 'parity'))
    ap.add_argument('--out', default='sources.jsonl')
    args = ap.parse_args()
    t_run = time.time()
    rows, prefixes = [], []
    for name, stars in qlaw.lib.recorded_sources().items():
        t0 = time.time()
        h, ref = qlaw.reference_summary(stars, args.law)
        ref.update(source=name, law=args.law, rule='ordinary', conv=None, seconds=round(time.time() - t0, 2),
                   stars_sha256=qlaw.stars_digest(h['stars']))
        rows.append(ref)
        for conv in ('O', 'N'):
            t0 = time.time()
            g = qlaw.run_ab(stars, args.law, conv, reread=True, bound_next=True)
            row = qlaw.history_summary(g)
            row.update(source=name, law=args.law, rule='Q', conv=conv, seconds=round(time.time() - t0, 2),
                       stars_sha256=qlaw.stars_digest(g.stars),
                       rounds_with_reread=[t + 1 for t, x in enumerate(g.reread_births_per_round()) if x])
            rows.append(row)
            pre = qlaw.small_prefix(g.stars, g.n_at)
            if pre is not None and not any(g.rounds[t]['fresh_lower_bound'] for t in range(len(pre['n_at']) - 1)):
                pre.update(test='a', source=name, law=args.law, conv=conv)
                prefixes.append(pre)
        print(json.dumps({k: rows[-1][k] for k in ('source', 'outcome', 'n_at')}), flush=True)
    qlaw.dump(qlaw.ART / args.out, rows)
    qlaw.dump(qlaw.ART / 'prefixes' / f'a_{args.law}.jsonl.gz', prefixes)
    print(json.dumps(dict(rows=len(rows), seconds=round(time.time() - t_run, 1))))


if __name__ == '__main__':
    main()
