"""control.py: two controls run after the full run, before the referee.
(1) Unrelated starts of the same kind of growth compared with each other, as if one were the other with a change:
    if the ancestry-free readings find no damage between them, those readings cannot tell where a change is, only how
    a round's count of each kind of birth differs.
(2) The weakening cases at round 32 read by name shell by shell: which births the change re-makes by descent."""
import json, collections
import amount
law = amount.law_ord()
out = {'unrelated starts': [], 'by name, shell by shell': []}
for a, b in [('two-touching', 'chain3'), ('ring5-bare', 'ring7-bare')]:
    g = amount.Growth(amount.STARTS[a], law).run(32); h = amount.Growth(amount.STARTS[b], law).run(32)
    rows = amount.compare(g, h)
    out['unrelated starts'].append({'G': a, "G'": b, 'verdicts': amount.summary(rows),
        'name damage by round': [sum(r['name']) for r in rows], 'sig0 damage by round': [sum(r['sig0']) for r in rows],
        'sig1 damage by round': [sum(r['sig1']) for r in rows], 'n': [r['n'] for r in rows], "n'": [r["n'"] for r in rows]})
def by_name_shells(g, h, focus, t):
    dg, dh = g.distances(focus, t), h.distances(focus, t)
    sh = collections.defaultdict(lambda: [[], []])
    for x in g.rows[t - 1]['births']: sh[dg.get(x['id'], -1)][0].append(x['name'])
    for x in h.rows[t - 1]['births']: sh[dh.get(x['id'], -1)][1].append(x['name'])
    return {str(r): [len(p), len(q), sum(amount.diff(p, q))] for r, (p, q) in sorted(sh.items())}
for start, change, at in [('two-touching', 'mark', 0), ('chain3', 'mark', 1), ('two-touching', 'move', [0, 1]), ('chain3', 'move', [0, 2])]:
    st = amount.STARTS[start]; g = amount.Growth(st, law).run(32); ch = [list(k) for k in st]
    if change == 'mark': ch[at].append(1 + max(d for k in st for d in k)); focus = at
    else: i, j = at; d = amount.loose_of(st)[i][-1]; ch[i].remove(d); ch[j].append(d); focus = i
    h = amount.Growth(ch, law).run(32)
    out['by name, shell by shell'].append({'start': start, 'change': change, 'at': at, 'round': 32,
        'shells by name [G, G\', damage]': by_name_shells(g, h, focus, 32)})
print(json.dumps(out))
