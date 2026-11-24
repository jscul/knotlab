"""Build the targets and their founder starts (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B, "Targets", "Founder starts").

Targets: every structure of THIRD-HOLDER-20261123-001B's list of structures with a hidden excess (structures_found.json; the
seven-knot structure and the pencil 9-knot structure are in it and are marked), each with its six observer distinctions and
its table of old allowed words, computed here by contraction and by full enumeration.
Founder starts: every connected proper subset of a target's knots holding all six observer distinctions; the other proper
subsets are counted (no observer distinction missing first, then not connected) and not grown.

Writes targets.json and starts.jsonl to the artifact folder.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

t0 = time.time()
targets = c.load_targets()
rows = []
starts = []
skip = Counter()
for t in targets:
    ks = t['knots']
    names = sorted({m for _, mem in ks for m in mem})
    idx = {m: i for i, m in enumerate(names)}
    stars = [tuple(idx[m] for m in mem) for _, mem in ks]
    laws = [law for law, _ in ks]
    obs = tuple(idx[o] for o in c.OBS)
    T = c.contract([(s, c.lt(l, len(s))) for s, l in zip(stars, laws)], obs).reshape(64)
    Tb = c.brute_table(stars, laws, obs) if len(names) <= 28 else None
    h = Counter(m for _, mem in ks for m in mem)
    st = c.founder_starts(ks)
    cls = Counter(k for _, k in st)
    skip.update({k: v for k, v in cls.items() if k != 'grown'})
    for mask, kind in st:
        if kind != 'grown':
            continue
        sub = [k for k in range(len(ks)) if mask >> k & 1]
        hs = Counter(m for k in sub for m in ks[k][1])
        starts.append(dict(tid=t['tid'], mask=mask, knots=len(sub), D0=len(hs), L0=sum(1 for v in hs.values() if v == 1),
                           max_holders=max(hs.values()), any_nae=any(ks[k][0] == 'nae' for k in sub)))
    rows.append(dict(tid=t['tid'], tags=t['tags'], source=t['source'], knots=[c.fmt_knot(*k) for k in ks], side_A=t['side_A'],
                     n_knots=len(ks), n_distinctions=len(names), max_holders=max(h.values()),
                     table=[int(v) for v in T], table_brute_equal=(None if Tb is None else bool((T == Tb).all())),
                     recorded_score=t['score'], recorded_M=t['M'], starts_grown=cls.get('grown', 0),
                     starts_no_observer=cls.get('no_observer', 0), starts_not_connected=cls.get('not_connected', 0)))
(c.ART / 'targets.json').write_text(json.dumps(rows, indent=1))
c.dump(c.ART / 'starts.jsonl', starts)
summary = dict(targets=len(rows), starts_grown=len(starts), skipped=dict(skip), seconds=round(time.time() - t0, 1),
               by_target_size={k: v for k, v in sorted(Counter(r['n_knots'] for r in rows).items())},
               table_brute_equal=sum(1 for r in rows if r['table_brute_equal']),
               table_brute_not_run=sum(1 for r in rows if r['table_brute_equal'] is None),
               starts_with_three_holders=sum(1 for s in starts if s['max_holders'] >= 3),
               starts_without_nae=sum(1 for s in starts if not s['any_nae']),
               starts_D0_over_20=sum(1 for s in starts if s['D0'] > c.DMAX),
               tags={tag: [r['tid'] for r in rows if tag in r['tags']] for tag in ('seven', 'pencil', 'eighteen')})
(c.ART / 'build_summary.json').write_text(json.dumps(summary, indent=1))
print(json.dumps(summary))
