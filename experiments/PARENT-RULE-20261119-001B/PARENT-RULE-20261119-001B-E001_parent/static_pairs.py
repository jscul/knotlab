"""PARENT-RULE-20261119-001B part S pairing.  Run: .venv/bin/python -B static_pairs.py runs/parent-static -> static_pairs.json.

Rows sharing a sorted-rows hash and a number of distinctions are rebuilt; their exact tables grouped by isomorphism (VF2 with
Weisfeiler-Leman colours); each group split into state groups (a junction-graph isomorphism, else every table isomorphism on twin
classes checked by rank, cap 5,000: same, other, undecided).  For every two arrangements of one table group in different state
groups (an other-states pair), which properties both sides have: P1, P1 in the backed stratum, peel depth at least 1 and at least
2, and the control Q.  The known pair of UNIQUE-TABLE's pop-0308 (7 junctions) is located."""
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import plib as L  # noqa: E402
import static_job as SJ  # noqa: E402
from longrun import load_results  # noqa: E402
F = ['n', 'atlas', 'loose', 'key', 'distinctions', 'P1', 'P1+', 'P2', 'stratum', 'depth', 'Q']
_G = None


def graphs():
    global _G
    if _G is None:
        _G = {i: nx.convert_node_labels_to_integers(g) for i, g in SJ.atlas()}
    return _G


def stars_of(row):
    return SJ.arrangement(graphs()[row['atlas']], tuple(int(c) for c in row['loose']))


def flags(row):
    return {'P1': row['P1'] == 0, 'P1b': row['P1'] == 0 and row['stratum'] == 'b', 'D1': row['depth'] >= 1,
            'D2': row['depth'] >= 2, 'Q': row['Q'] == 0}


def bucket(rows):
    items = [(r, stars_of(r)) for r in rows]
    tabs = [L.table(s) for _, s in items]
    cols = [L.coloured(*t) for t in tabs]
    groups = []
    for i in range(len(items)):
        for g in groups:
            if L.iso(cols[g[0]], cols[i]):
                g.append(i)
                break
        else:
            groups.append([i])
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        sg, undecided = [], 0
        for i in g:
            placed = False
            for s in sg:
                v = L.states(items[s[0]][1], items[i][1], tabs[s[0]][0], tabs[i][0])
                if v == 'same':
                    s.append(i)
                    placed = True
                    break
                if v == 'undecided':
                    undecided += 1
            if not placed:
                sg.append([i])
        rec = {'size': len(g), 'state_groups': len(sg), 'undecided_tests': undecided, 'distinctions': rows[0]['distinctions']}
        if len(sg) >= 2:
            pairs = Counter()
            for x in range(len(sg)):
                for y in range(x + 1, len(sg)):
                    for i in sg[x]:
                        for j in sg[y]:
                            fi, fj = flags(items[i][0]), flags(items[j][0])
                            pairs['pairs'] += 1
                            for k in fi:
                                pairs[f'both_{k}'] += fi[k] and fj[k]
                                pairs[f'one_{k}'] += fi[k] != fj[k]
            rec['other_pairs'] = dict(pairs)
            rec['members'] = [{'row': items[i][0], 'state_group': next(n for n, s in enumerate(sg) if i in s),
                               'stars': [sorted(s) for s in items[i][1]]} for i in g][:12]
        out.append(rec)
    return out


def main(out_dir):
    recs = load_results(out_dir)
    rows = [dict(zip(F, r)) for c, rr in sorted(recs.items()) if rr['status'] == 'ok' for r in rr['result']['rows']]
    pop = {'arrangements': len(rows), 'by_n': dict(sorted(Counter(r['n'] for r in rows).items())),
           'by_stratum': dict(Counter(r['stratum'] for r in rows)),
           'P1': sum(r['P1'] == 0 for r in rows), 'P1_backed': sum(r['P1'] == 0 and r['stratum'] == 'b' for r in rows),
           'depth_ge_1': sum(r['depth'] >= 1 for r in rows), 'depth_ge_2': sum(r['depth'] >= 2 for r in rows),
           'Q': sum(r['Q'] == 0 for r in rows)}
    by = defaultdict(list)
    for r in rows:
        by[(r['key'], r['distinctions'])].append(r)
    work = [v for v in by.values() if len(v) >= 2]
    pop['tables_by_hash'] = len(by)
    pop['P1_tables_by_hash'] = len({k for k, v in by.items() if any(r['P1'] == 0 for r in v)})
    with Pool(8) as pool:
        res = [g for b in pool.imap_unordered(bucket, work, chunksize=4) for g in b]
    other = [g for g in res if g['state_groups'] >= 2]
    tot = Counter()
    for g in other:
        for k, v in g['other_pairs'].items():
            tot[k] += v
    # the known pair at 7 junctions
    known = None
    vr = json.loads((ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/verify_rivals.json').read_text())
    k7 = [x for x in vr if len(x['truth']) <= 7]
    if k7:
        t, rv = [frozenset(s) for s in k7[0]['truth']], [frozenset(s) for s in k7[0]['rival']]
        found = {'truth': None, 'rival': None}
        for g in other:
            for m in g['members']:
                st = [frozenset(s) for s in m['stars']]
                for name, ref in (('truth', t), ('rival', rv)):
                    if found[name] is None and len(st) == len(ref) and L.arrangement_iso(st, ref):
                        found[name] = (g['distinctions'], m['state_group'], m['row'])
        known = {'case': k7[0]['case'], 'found': found}
    summary = {'population': pop, 'table_groups_with_two_or_more': len(res),
               'same_states_only_groups': sum(1 for g in res if g['state_groups'] == 1),
               'other_states_groups': len(other), 'undecided_tests': sum(g['undecided_tests'] for g in res),
               'other_states_pairs': dict(tot), 'known_pair': known}
    dest = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'static_pairs.json').write_text(json.dumps({'summary': summary, 'other_states_groups': other}, indent=1, default=str))
    print(json.dumps(summary, indent=1, default=str))


if __name__ == '__main__':
    main(sys.argv[1])
