"""GROW-SMALL-20261119-001A pairing.  Run: .venv/bin/python -B pairs_grow.py runs/grow-small -> grow_pairs.json.
MEET-ONCE's amended pairing (pairs_meet2.examine), unchanged, on these stages:
- arrangement classes by exact isomorphism (stages regrown from their start and round; provenances kept);
- candidate groups: classes whose tables read to 8 are isomorphic (VF2 with Weisfeiler-Leman colours);
- states first on those tables (a junction-graph isomorphism, else every table isomorphism on twin classes by rank, cap 5,000);
- classes with other states escalated to tables read to 12, 16, ... and the full table, under a 1,800 s alarm per group: isomorphic
  full tables with other states is a collision with other states; a split is none; the alarm is undecided."""
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MO = ROOT / 'experiments/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet'
sys.path.insert(0, str(MO))
import pairs_meet2 as PM2  # noqa: E402  (brings MEET-ONCE's job.py as 'job')
_spec = importlib.util.spec_from_file_location('grow_small_job', HERE / 'job.py')
GJ = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = GJ
_spec.loader.exec_module(GJ)
L, SJ, PM = GJ.L, GJ.SJ, PM2.PM
F = ['n', 'atlas', 'loose', 'round', 'junctions', 'distinctions', 'max_shared', 'table_hash', 'arrangement_hash', 'kind', 'depth',
     'beyond_8']
_G = None


def stage_stars(row):
    global _G
    if _G is None:
        import networkx as nx
        _G = {i: nx.convert_node_labels_to_integers(g) for i, g in SJ.atlas()}
    start = SJ.arrangement(_G[row['atlas']], tuple(int(c) for c in row['loose']))
    return GJ.grow(start, row['round'])[row['round'] - 1]


def classes_of(rows):
    """Exact arrangement classes among rows sharing an arrangement hash."""
    items = [(r, stage_stars(r)) for r in rows]
    cls = []
    for r, st in items:
        for c in cls:
            if GJ.same_arrangement(c['stars_fs'], st):
                c['prov'].append((r['n'], r['atlas'], r['loose'], r['round']))
                break
        else:
            cls.append({'stars_fs': st, 'stars': [sorted(s) for s in st], 'prov': [(r['n'], r['atlas'], r['loose'], r['round'])],
                        'th': r['table_hash'], 'distinctions': r['distinctions'], 'junctions': r['junctions'], 'kind': r['kind'],
                        'depth': r['depth']})
    for c in cls:
        del c['stars_fs']
    return cls


def candidates(v):
    tabs = {id(c): PM.table_at([frozenset(s) for s in c['stars']], PM.J.HPOOL) for c in v}
    return [sub for sub in PM.group(v, lambda c: PM.coloured(*tabs[id(c)])) if len(sub) >= 2]


def main(out_dir):
    recs = PM.load_results(out_dir)
    rows, counts = [], Counter()
    for c, rr in sorted(recs.items()):
        if rr['status'] != 'ok':
            continue
        counts.update(rr['result']['counts'])
        rows += [dict(zip(F, x)) for x in rr['result']['rows']]
    out = {'cases': dict(Counter(rr['status'] for rr in recs.values())), 'counts': dict(counts), 'stages': len(rows),
           'stages_by_round': dict(Counter(r['round'] for r in rows)), 'stages_meeting_once': sum(r['max_shared'] < 2 for r in rows),
           'stages_by_kind': dict(Counter(r['kind'] for r in rows)), 'stages_by_depth': dict(Counter(r['depth'] for r in rows)),
           'stages_depth_below_round': sum(r['depth'] < r['round'] for r in rows), 'stages_beyond_8': sum(r['beyond_8'] for r in rows),
           'stages_by_start_size': dict(sorted(Counter(r['n'] for r in rows).items()))}
    by_a = defaultdict(list)
    for r in rows:
        by_a[r['arrangement_hash']].append(r)
    with Pool(8) as pool:
        cls = [c for cs in pool.imap_unordered(classes_of, by_a.values(), chunksize=16) for c in cs]
        out['arrangement_classes'] = len(cls)
        buckets = defaultdict(list)
        for c in cls:
            buckets[(c['th'], c['distinctions'])].append(c)
        work = [v for v in buckets.values() if len(v) >= 2]
        cand = [g for gs in pool.imap_unordered(candidates, work, chunksize=4) for g in gs]
        out['candidate_groups'] = len(cand)
        res = list(pool.imap_unordered(PM2.examine, cand))
    # the depth of each candidate group's classes (the examine records keep members in order)
    depth_of = {tuple(map(tuple, c['stars'])): c['depth'] for g in cand for c in g}
    for r in res:
        r['depths'] = [depth_of.get(tuple(map(tuple, m['stars']))) for m in r.get('members', [])]
    res.sort(key=lambda r: (r['distinctions'], r['junctions']))
    out['summary'] = {
        'candidate_groups': len(res),
        'same_states_collision_groups': sum(1 for r in res if r.get('same_states_collision')),
        'groups_with_other_state_groups': sum(1 for r in res if len(r.get('state_groups', [])) >= 2),
        'other_states_collisions': sum(1 for r in res if r.get('other_states_collision') and not r.get('states_undecided')),
        'full_table_collisions_with_states_undecided': sum(1 for r in res if r.get('other_states_collision') and r.get('states_undecided')),
        'other_states_split_by_escalation': sum(1 for r in res if r.get('other_states_collision') is False),
        'escalation_split_at_H': dict(Counter(r['escalated_to_H'] for r in res if r.get('other_states_collision') is False)),
        'states_undecided_groups': sum(1 for r in res if r.get('states_undecided')),
        'late_groups': sum(1 for r in res if r.get('undecided_late')),
        'tests_by_kind': dict(Counter('graph' if n == 0 else 'twin' for r in res for (_, _, v, n) in r.get('tests', []) if v == 'same')),
    }
    out['groups'] = res
    dest = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'grow_pairs.json').write_text(json.dumps(out, indent=1, default=list))
    print(json.dumps({k: v for k, v in out.items() if k != 'groups'}, indent=1, default=list))


if __name__ == '__main__':
    main(sys.argv[1])
