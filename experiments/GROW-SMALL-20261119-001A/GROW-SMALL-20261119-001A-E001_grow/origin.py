"""GROW-SMALL-20261119-001A, after the pairing: for every collision with other states found by pairs_grow.py, were the two
stages' starts already a static collision with other states (carried), or did the growth make one (created)?  For each pair of
members in different state groups, the first provenance of each gives its start (at most 7 junctions); the starts' full tables
by bonds are compared by isomorphism, and their states by plib.states.  Run: .venv/bin/python -B origin.py -> origin.json."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pairs_grow as PG  # noqa: E402
L, SJ = PG.L, PG.SJ
DEST = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow'


def start_of(prov):
    n, atlas, loose, rnd = prov
    PG.stage_stars({'atlas': atlas, 'loose': loose, 'round': 1})  # builds the graph cache
    return SJ.arrangement(PG._G[atlas], tuple(int(c) for c in loose)), rnd


def main():
    d = json.loads((DEST / 'grow_pairs.json').read_text())
    rows, c = [], Counter()
    for g in d['groups']:
        if not g.get('other_states_collision') or g.get('states_undecided'):
            continue
        ms = g['members']
        # the examine record keeps up to 4 members in order; its tests (rep, i, verdict) place each class in a state group
        sg = {i: i for i in range(g['classes'])}
        for rep, i, v, _ in g['tests']:
            if v == 'same':
                sg[i] = sg[rep]
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                if sg[i] == sg[j]:
                    continue
                a, ra = start_of(ms[i]['prov'][0])
                b, rb = start_of(ms[j]['prov'][0])
                ta, la = L.table(a)
                tb, lb = L.table(b)
                if len(la) == len(lb) and L.iso(L.coloured(ta, la), L.coloured(tb, lb)):
                    st = L.states(a, b, ta, tb)
                    kind = 'carried (starts share a table, other states)' if st == 'other' else f'starts share a table, states {st}'
                else:
                    kind = 'created (starts have different tables)'
                c[kind] += 1
                rows.append({'distinctions': g['distinctions'], 'rounds': [ra, rb], 'kind': kind,
                             'starts': [ms[i]['prov'][0], ms[j]['prov'][0]]})
    (DEST / 'origin.json').write_text(json.dumps({'summary': dict(c), 'pairs': rows}, indent=1))
    print(json.dumps(dict(c), indent=1))


if __name__ == '__main__':
    main()
