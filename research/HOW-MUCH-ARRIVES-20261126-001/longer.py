"""longer.py: the cases that weaken, grown on to round 32 (one size past the run's 16), and their shells."""
import json, sys
import amount
amount.ROUNDS = 32
out = []
for start, change, at in [('two-touching', 'mark', 0), ('two-touching', 'mark', 1), ('two-touching', 'move', [0, 1]), ('two-touching', 'move', [1, 0]),
                          ('chain3', 'mark', 1), ('chain3', 'move', [0, 2]), ('chain3', 'move', [2, 0]),
                          ('chain3', 'mark', 0), ('chain3', 'mark', 2)]:
    st = amount.STARTS[start]
    base = amount.Growth(st, amount.law_ord()).run(32)
    ch = [list(k) for k in st]
    if change == 'mark': ch[at].append(1 + max(d for k in st for d in k)); focus = at
    else:
        i, j = at; d = amount.loose_of(st)[i][-1]; ch[i].remove(d); ch[j].append(d); focus = i
    g = amount.Growth(ch, amount.law_ord()).run(32)
    rows = amount.compare(base, g, focus=focus)
    out.append({'start': start, 'change': change, 'at': at, 'verdicts': amount.summary(rows),
                'sig1 damage by round': [sum(r['sig1']) for r in rows], 'n + n\'': [r['n'] + r["n'"] for r in rows],
                'name damage by round': [sum(r['name']) for r in rows], 'last shells': rows[-1]['shells']})
for o in out: print(json.dumps(o))
