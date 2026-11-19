"""GROW-SMALL-20261119-001A, the positive control and the targeted test (the advisor's two first fixes).
- C0 (control): the 472 static other-states groups of PARENT-RULE part S (all their members), run through the same pairing
  (pairs_meet2.examine, as the stages are): every group must come back as a collision with other states, none undecided.
- T (targeted): every member of those groups grown one and two rounds; at each round the members that grew, as classes, through the
  same candidate grouping and pairing: do any stay one table with other states?
Run: .venv/bin/python -B targeted.py -> targeted.json."""
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pairs_grow as PG  # noqa: E402
GJ, L, PM2 = PG.GJ, PG.L, PG.PM2
SRC = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_pairs.json'


def as_class(stars, prov):
    return {'stars': [sorted(s) for s in stars], 'prov': [prov], 'distinctions': len(L.owners(stars)), 'junctions': len(stars)}


def control(g):
    cl = [as_class([frozenset(s) for s in m['stars']], m['row']['loose']) for m in g['members']]
    r = PM2.examine(cl)
    return {'other': bool(r.get('other_states_collision')), 'undecided': bool(r.get('states_undecided') or r.get('undecided_late')),
            'state_groups': len(r.get('state_groups', []))}


def targeted(g):
    out = {}
    grown = [GJ.grow([frozenset(s) for s in m['stars']]) for m in g['members']]
    for rnd in (1, 2):
        cl = []
        for k, st in enumerate(grown):
            if len(st) >= rnd:
                s = st[rnd - 1]
                if not any(L.arrangement_iso([frozenset(x) for x in c['stars']], s) for c in cl):
                    cl.append(as_class(s, k))
        rec = {'grew': len(cl)}
        if len(cl) >= 2:
            byd = {}
            for c in cl:
                byd.setdefault(c['distinctions'], []).append(c)
            res = []
            for v in byd.values():
                if len(v) >= 2:
                    for cand in PG.candidates(v):
                        res.append(PM2.examine(cand))
            rec['candidate_groups'] = len(res)
            rec['other'] = sum(1 for r in res if r.get('other_states_collision') and not r.get('states_undecided'))
            rec['same'] = sum(1 for r in res if r.get('same_states_collision'))
            rec['undecided'] = sum(1 for r in res if r.get('states_undecided') or r.get('undecided_late'))
        out[rnd] = rec
    return out


def main():
    groups = json.loads(SRC.read_text())['other_states_groups']
    with Pool(8) as pool:
        c0 = pool.map(control, groups, chunksize=4)
        t = pool.map(targeted, groups, chunksize=4)
    s = {'C0_groups': len(c0), 'C0_recovered_other': sum(x['other'] for x in c0), 'C0_undecided': sum(x['undecided'] for x in c0)}
    for rnd in (1, 2):
        tc = Counter()
        for x in t:
            r = x[rnd]
            tc['groups_with_two_grown'] += r['grew'] >= 2
            for k in ('candidate_groups', 'other', 'same', 'undecided'):
                tc[k] += r.get(k, 0)
        s[f'T_round_{rnd}'] = dict(tc)
    dest = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'targeted.json').write_text(json.dumps({'summary': s, 'control': c0, 'targeted': t}, indent=1))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main()
