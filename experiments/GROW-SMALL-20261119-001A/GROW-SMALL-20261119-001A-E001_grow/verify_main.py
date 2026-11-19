"""GROW-SMALL-20261119-001A, the frozen check outside the pipeline, on every collision with other states that pairs_grow.py found:
for every two members in different state groups, verify_t.check_pair (full tables by bonds when at most 15 vertices, the
renaming checked entry by entry, non-isomorphism by a second encoding, other states by weight enumerators or plib.states),
regrowth of both from relabelled starts, and the next round: do the two stages one round on still share a table read to 8, and
with other states (MEET-ONCE's states test on those tables; no escalation, since full tables there take hours)?  Also each pair's origin (origin.json).  Run: .venv/bin/python -B verify_main.py."""
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import verify_t as V  # noqa: E402
PG, GJ, L, PM2 = V.PG, V.GJ, V.L, V.PG.PM2
DEST = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow'


def start_of(prov):
    n, atlas, loose, rnd = prov
    PG.stage_stars({'atlas': atlas, 'loose': loose, 'round': 1})
    return GJ.SJ.arrangement(PG._G[atlas], tuple(int(c) for c in loose)), rnd


def one(g):
    sg = {i: i for i in range(g['classes'])}
    for rep, i, v, _ in g['tests']:
        if v == 'same':
            sg[i] = sg[rep]
    ms = g['members']
    out = []
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            if sg[i] == sg[j]:
                continue
            a = [frozenset(s) for s in ms[i]['stars']]
            b = [frozenset(s) for s in ms[j]['stars']]
            r = V.check_pair(a, b)
            sa, ra = start_of(ms[i]['prov'][0])
            sb, rb = start_of(ms[j]['prov'][0])
            r['relabel_ok'] = V.relabel_control(sa, ra) and V.relabel_control(sb, rb)
            r['rounds'] = [ra, rb]
            na, nb = GJ.grow(sa, ra + 1), GJ.grow(sb, rb + 1)
            if len(na) > ra and len(nb) > rb:
                x, y = na[ra], nb[rb]
                cl = [PM2_class(x), PM2_class(y)]
                if cl[0]['distinctions'] == cl[1]['distinctions'] and PG.candidates(cl):
                    # tables read to 8 agree; states on them (no escalation: full tables at these sizes take hours)
                    tx, ty = PM2.PM.table_at(x, 8)[0], PM2.PM.table_at(y, 8)[0]
                    v, _ = PM2.states_pooled(x, y, tx, ty)
                    r['next_round'] = {'same': 'same states', 'other': 'one table read to 8, other states',
                                       'undecided': 'one table read to 8, states undecided'}[v]
                else:
                    r['next_round'] = 'tables read to 8 differ'
            else:
                r['next_round'] = 'a side stalls or closes'
            out.append(r)
    return out


def PM2_class(stars):
    return {'stars': [sorted(s) for s in stars], 'prov': [], 'distinctions': len(L.owners(stars)), 'junctions': len(stars)}


def main():
    d = json.loads((DEST / 'grow_pairs.json').read_text())
    og = [g for g in d['groups'] if g.get('other_states_collision')]
    with Pool(8) as pool:
        rows = [x for r in pool.map(one, og) for x in r]
    s = Counter()
    for r in rows:
        s['pairs'] += 1
        s['checked_by_bonds'] += 'skipped' not in r
        s['tables_isomorphic_by_bonds'] += bool(r.get('full_tables_isomorphic'))
        s['renaming_ok'] += bool(r.get('renaming_checked_entry_by_entry'))
        s['non_isomorphic'] += bool(r.get('non_isomorphic_second_encoding'))
        s['other_states'] += str(r.get('states', '')).startswith('other')
        s['other_by_weights'] += 'weight' in str(r.get('states', ''))
        s['relabel_ok'] += r['relabel_ok']
        s['next_round: ' + r['next_round']] += 1
    origin = json.loads((DEST / 'origin.json').read_text())['summary']
    (DEST / 'verify_main.json').write_text(json.dumps({'summary': dict(sorted(s.items())), 'origin': origin, 'pairs': rows}, indent=1))
    print(json.dumps({'summary': dict(sorted(s.items())), 'origin': origin}, indent=1))


if __name__ == '__main__':
    main()
