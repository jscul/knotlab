"""Referee R1, item (b) follow-up: D1 with k0 = 2 (5d9c7de076fa, b4ba185b9c0f) is used for "from level 3". A tie from an anchor
at level 2 to S_3 and another from a (possibly different) anchor to S_(3+s) gives a level-3 to level-(3+s) tie only through a
common tie class. Here, in my explicit union of the descent's blocks (levels 2..k, my builder), I decide directly:
  (i) which anchors are tied to some element of S_(k+1), per level;
  (ii) whether some element of S_3 is tied to some element of S_(k+1) (k + 1 = 3 + s), per level, up to level KMAX + 1;
and (iii) the same question (ii) in the whole pattern P_NP by SAT. Writes referee_D_level3.json.
Usage: referee_check_D_level3.py KMAX NP"""
import json
import sys

import numpy as np
from pysat.solvers import Cadical195

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut, Oracle, hid, load_population, HERE, STUDY  # noqa: E402
from referee_check_D import explicit_block, letters, to_int  # noqa: E402  (my own helpers)

KMAX, NP = int(sys.argv[1]), int(sys.argv[2])
keys = {d['case']: d['key'] for d in load_population()}
chains = json.load(open(STUDY / 'chain_ties_constant-2.json'))
out = {}
for cid, row in chains.items():
    ch = row.get('chain')
    if not ch or ch['k0'] != 2:
        continue
    A = Aut(keys[cid])
    S = [to_int([int(c) for c in x]) for x in ch['S']]
    n = len(S)
    sol = Cadical195()
    anchors = [hid(x, 2) for x in S]
    S3 = None
    per_level = []
    cur, k = list(S), 2
    while k <= KMAX:
        c = letters(ch, k - 2)
        eb = explicit_block(A, cur, k)
        gl = [hid(x, k) for x in cur]
        for kn in eb:
            g = [gl[v] if v < n else hid(2 * cur[(v - n) // 2] + (v - n) % 2, k + 1) for v in kn]
            sol.add_clause([v + 1 for v in g])
            sol.add_clause([-v - 1 for v in g])
        nxt = [2 * cur[j] + c[j] for j in range(n)]
        deep = [hid(x, k + 1) for x in nxt]
        if k + 1 == 3:
            S3 = list(deep)

        def tied(a, b):
            return sum(sol.solve(assumptions=[sa * (a + 1), sb * (b + 1)]) for sa in (1, -1) for sb in (1, -1)) == 2
        anc = sorted({i for i in range(n) for j in range(n) if tied(anchors[i], deep[j])})
        lvl3 = None
        if S3 is not None and k + 1 > 3:
            lvl3 = [[a, b] for a in S3 for b in deep if tied(a, b)]
        per_level.append(dict(deep_level=k + 1, anchors_tied=anc, level3_ties=None if lvl3 is None else len(lvl3),
                              level3_example=None if not lvl3 else lvl3[0]))
        cur, k = nxt, k + 1
    sol.delete()
    # (iii) the whole pattern
    O = Oracle(keys[cid], NP)
    whole = []
    for lv in per_level:
        if lv['deep_level'] <= 3 or lv['deep_level'] > NP:
            continue
        lev = lv['deep_level']
        cur = list(S)
        for t in range(lev - 2):
            c = letters(ch, t)
            cur = [2 * cur[j] + c[j] for j in range(n)]
        deep = [hid(x, lev) for x in cur]
        found = None
        for a in S3:
            for b in deep:
                r = [O.solve([sa * (a + 1), sb * (b + 1)]) is not None for sa in (1, -1) for sb in (1, -1)]
                if sum(r) == 2:
                    found = [a, b]
                    break
            if found:
                break
        whole.append(dict(deep_level=lev, tie=found))
    O.close()
    out[cid] = dict(S=ch['S'], cycle=ch['cycle'], per_level=per_level, whole_pattern_N=NP, whole=whole)
    print(cid[:12], json.dumps(per_level)[:600], json.dumps(whole)[:300], flush=True)
json.dump(out, open(HERE / 'referee_D_level3.json', 'w'), indent=1)
