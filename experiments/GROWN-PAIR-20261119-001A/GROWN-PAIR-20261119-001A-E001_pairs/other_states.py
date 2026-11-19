"""After pairs2.py (not a prediction): the grown-grown table groups whose grown classes fall into two or more state groups, examined:
lineage (do the grown classes come from the same start?), the census's own next stages compared by exact table isomorphism (not
only by hash), whether junctions meet at most once, and three examples.  Run: .venv/bin/python -B other_states.py runs/grown-pair
-> other_states.json beside the artifacts."""
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import pairs2 as P2  # noqa: E402
from longrun import load_results  # noqa: E402

BY_PROV = {}


def examine(classes):
    out = []
    for tg in P2.group(classes, lambda c: P2.coloured_table([frozenset(s) for s in c['stars']])):
        grown = [c for c in tg if any(r > 0 for _, r in c['prov'])]
        if len(grown) < 2:
            continue
        sg = P2.group(grown, lambda c: P2.coloured_table([frozenset(s) for s in c['stars']], True))
        if len(sg) < 2:
            continue
        reps = [s[0] for s in sg]
        starts = [{i for i, r in c['prov'] if r > 0} for c in reps]
        same_lineage = any(starts[a] & starts[b] for a in range(len(reps)) for b in range(a + 1, len(reps)))
        nxt = []
        for c in reps:
            i, r = next((i, r) for i, r in c['prov'] if r > 0)
            n = BY_PROV.get((i, r + 1))
            nxt.append(n)
        cmp = None
        if all(nxt):
            gs = [P2.coloured_table([frozenset(s) for s in n['stars']]) for n in nxt]
            cmp = all(P2.iso(gs[0], g) for g in gs[1:])
            if cmp:
                cs = [P2.coloured_table([frozenset(s) for s in n['stars']], True) for n in nxt]
                cmp_states = all(P2.iso(cs[0], g) for g in cs[1:])
            else:
                cmp_states = None
        else:
            cmp_states = None
        out.append({'distinctions': tg[0]['distinctions'], 'state_groups': len(sg), 'same_lineage': same_lineage,
                    'meet_once': [c['meet_once'] for c in reps],
                    'next_tables_isomorphic': cmp, 'next_states_agree': cmp_states,
                    'next_present': [bool(n) for n in nxt],
                    'reps': [{'stars': c['stars'], 'prov': c['prov'][:3], 'junctions': c['junctions']} for c in reps[:2]]})
    return out


def init(by_prov):
    global BY_PROV
    BY_PROV = by_prov


def main(out_dir):
    recs = load_results(out_dir)
    stages = [st for c, r in sorted(recs.items()) if r['status'] == 'ok' for st in r['result']['stages']]
    by_prov = {(st['index'], st['round']): {'stars': st['stars']} for st in stages}
    by_ahash = defaultdict(list)
    for st in stages:
        by_ahash[st['arrangement_hash']].append(st)
    classes = []
    for h, sts in by_ahash.items():
        for members in P2.group(sts, P2._inc):
            st = members[0]
            classes.append({'stars': st['stars'], 'prov': [(m['index'], m['round']) for m in members],
                            'thash': st['table_hash'], 'distinctions': st['distinctions'], 'junctions': st['junctions'],
                            'meet_once': st['max_shared'] < 2})
    buckets = defaultdict(list)
    for c in classes:
        buckets[c['thash']].append(c)
    work = [v for v in buckets.values() if sum(1 for c in v if any(r > 0 for _, r in c['prov'])) >= 2]
    with Pool(10, initializer=init, initargs=(by_prov,)) as pool:
        groups = [g for res in pool.imap_unordered(examine, work, chunksize=4) for g in res]
    s = {'groups': len(groups), 'same_lineage': sum(g['same_lineage'] for g in groups),
         'all_meet_once': sum(all(g['meet_once']) for g in groups),
         'next_stage_comparison': dict(Counter(('missing' if g['next_tables_isomorphic'] is None else
                                                ('next tables isomorphic' if g['next_tables_isomorphic'] else 'next tables differ'))
                                               for g in groups)),
         'next_states_when_tables_isomorphic': dict(Counter(g['next_states_agree'] for g in groups if g['next_tables_isomorphic'])),
         'by_distinctions': dict(sorted(Counter(g['distinctions'] for g in groups).items()))}
    dest = ROOT / 'artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs'
    (dest / 'other_states.json').write_text(json.dumps({**s, 'group_list': groups}, indent=1, default=list))
    print(json.dumps(s, indent=1))
    for g in groups[:3]:
        print(json.dumps(g, default=list)[:1500])


if __name__ == '__main__':
    main(sys.argv[1])
