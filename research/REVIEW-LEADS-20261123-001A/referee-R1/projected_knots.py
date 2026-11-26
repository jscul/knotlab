"""Recover each local relation by enumerating ordinary words, then check K1–K3."""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def even_words(rows):
    holders = defaultdict(list)
    for k, row in enumerate(rows):
        for d in row:
            holders[d].append(k)
    paths = {k: [] for k in range(len(rows))}
    words = [0]
    for d, (u, v) in holders.items():
        stack = [(u, None, 1 << d)]
        while stack:
            now, parent, change = stack.pop()
            if now == v:
                words += [x ^ change for x in words]
                break
            for nxt, other in paths[now]:
                if nxt != parent:
                    stack.append((nxt, now, change | (1 << other)))
        else:
            paths[u].append((v, d))
            paths[v].append((u, d))
    for word in words:
        assert all(sum((word >> d) & 1 for d in row) % 2 == 0 for row in rows)
    return words


@cache
def knot(width, projections):
    if width < 3:
        return False
    names = [f"x{i}" for i in range(width)]
    excluded = set(range(1 << width)) - set(projections)
    clauses = [" ".join(("~" if (word >> i & 1) else "")+n for i, n in enumerate(names))
               for word in excluded]
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
           "--loops", *names[:-1], "--contact", names[-1], "--json"]
    proc = subprocess.run(cmd, env={**os.environ, "PYTHONPATH": str(ROOT/"tools")},
                          capture_output=True, text=True)
    proc.check_returncode()
    return json.loads(proc.stdout)["is_knot"]


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    args = p.parse_args()
    started = time.monotonic()
    parts = json.loads((HERE/'closed_parts.json').read_text())['closed_presentations']
    if args.pilot:
        parts = parts[:3]
    completed = Counter()
    for part in parts:
        rows = part['holdings']
        words = even_words(rows)
        assert len(words) == part['ordinary_even_words']
        verdicts = []
        for row in rows:
            proj = {sum(((w >> d) & 1) << i for i, d in enumerate(row)) for w in words}
            verdicts.append(knot(len(row), tuple(sorted(proj))))
        assert verdicts == part['canonical_parity_knots']
        completed['presentations'] += 1
        completed['all_projected_holdings_knots'] += all(verdicts)
        completed['ordinary_words_projected_over_presentations'] += len(words)
    print(json.dumps(dict(counts=dict(completed), relation_types=knot.cache_info().currsize,
                          elapsed_seconds=time.monotonic()-started), indent=2))
