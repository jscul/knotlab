"""Part 8, the remainder (PR part 8; TD 10; R 10-11): projection on every structure of parts 2-4 (duplicates removed; part
3's own projections are in part3_signs.json), the canonical command on every knot of the 33 structures of at most 20
distinctions (the three named structures were checked early, part8_early_knots.json) and then on the finished
structures newly built in part 2 of at most 20 distinctions, in build order; new structures are not started after 20 min
of part 8's wall time."""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Pool

import knottest
import tc

A = tc.ART + '/'


def key(ks):
    return tuple(sorted(tc.kstr(tc.as_knot(k)) for k in ks))


def proj(job):
    tc.cap_memory()
    k, ks = job
    r = tc.project_test(ks)
    return k, r


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    early = json.load(open(A + 'part8_early_knots.json'))
    budget = 20 * 60 - early['wall_s']
    deadline = T0 + budget
    S = tc.load_structures()
    p2 = json.load(open(A + 'part2_lemma.json'))
    p4 = json.load(open(A + 'part4_examples.json'))
    labels = {}
    order_canon = []        # keys in the registered canonical order
    structs = {}

    def add(label, ks, canon):
        ks = [tc.as_knot(k) for k in ks]
        kk = key(ks)
        if kk not in structs:
            structs[kk] = ks
        labels.setdefault(kk, []).append(label)
        if canon and kk not in order_canon:
            order_canon.append(kk)
    for name, ks in S.items():
        add('structures.json: ' + name, ks, True)
    # part 2: finished structures in build order (canonical candidates), and starts / intermediate stages (projection)
    for it in p2['items']:
        r = it['result']
        for v in r['variants']:
            for ab, fin in v['finished'].items():
                add('part 2: %s | %s | %s' % (r['name'], v['label'], ab), [tc.parse_knot(x) for x in fin], True)
    import part2_lemma
    G1, R = part2_lemma.load_records()
    src_of = {'ONE-PARENT-REREAD uniform': G1, 'ONE-PARENT-REREAD mixed': G1, 'REREAD-BIRTHS rule R': R}
    for rec in p2['records']:
        v = rec['variants'][0]
        fins = v['finished']
        for ab, fin in fins.items():
            add('part 2: %s | %s' % (rec['name'], ab), [tc.parse_knot(x) for x in fin], True)
        raw = src_of[rec['record']['source']][rec['record']['index']]
        ks = [tc.parse_knot(x) for x in raw['knots']]
        nb = len(raw['births'][0])
        add('part 2 (the stage after the round): %s' % rec['name'], ks, False)
        add('part 2 (the start): %s' % rec['name'], ks[:len(ks) - nb], False)
    eight3 = [('odd', ('x1', 'x3', 's1')), ('odd', ('h1', 'h2', 'h3')), ('even', ('x2', 'h1', 'h2', 'h3')),
              ('even', ('y1', 'y3', 's1')), ('odd', ('k1', 'k2', 'k3')), ('even', ('y2', 'k1', 'k2', 'k3'))]
    add('part 2 (the start): the 8/3 case', eight3, False)
    for ex in p4['examples']:
        if 'all rows' in ex:
            for v in ex['all rows']['variants']:
                for ab, fin in v['finished'].items():
                    add('part 4: %s | %s' % (ex['example'], ab), [tc.parse_knot(x) for x in fin], False)
    keys = list(structs)
    print('unique structures', len(keys), 'canonical candidates', len(order_canon), flush=True)
    # projection on all
    t = time.time()
    with Pool(nproc) as pool:
        res = dict(pool.imap(proj, [(k, structs[k]) for k in keys], chunksize=8))
    wall_proj = round(time.time() - t, 1)
    print('projection done', wall_proj, flush=True)
    # canonical, in the registered order; reuse the early run's checks for the three named structures
    early_by = {key(r['structure'] and [tc.parse_knot(x) for x in r['structure']]): r for r in early['structures']}
    canon_done = {}
    for kk, r in early_by.items():
        canon_done[kk] = [k.get('canonical') for k in r['knots']]
    todo = [kk for kk in order_canon if kk not in canon_done and res[kk]['n_distinctions'] <= 20]
    print('canonical to run', len(todo), 'budget left (s)', round(deadline - time.time()), flush=True)
    t = time.time()
    from concurrent.futures import ThreadPoolExecutor

    def run_one(kk):
        if time.time() > deadline:
            return kk, None
        ks = structs[kk]
        return kk, [tc.canonical_check(ks, i) for i in range(len(ks))]
    n_cut = 0
    with ThreadPoolExecutor(max_workers=nproc) as ex:
        for kk, cr in ex.map(run_one, todo):
            if cr is None:
                n_cut += 1
                canon_done[kk] = 'canonical check not run (cut)'
                continue
            rr = res[kk]
            out = []
            for k, c in zip(rr['knots'], cr):
                if 'error' in c:
                    out.append({'error': c['error']})
                    continue
                agree = (c['allowed'] == k['induced'] and c['K1'] == k['K1'] and c['K2'] == k['K2']
                         and c['K3'] == k['K3'] and c['knot'] == k['whole'])
                out.append({'K1': c['K1'], 'K2': c['K2'], 'K3': c['K3'], 'knot': c['knot'],
                            'agrees with projection': agree})
            canon_done[kk] = out
    wall_canon = round(time.time() - t, 1)
    # attach
    structures = []
    for kk in keys:
        r = res[kk]
        c = canon_done.get(kk)
        if r['n_distinctions'] > 20:
            cstat = 'not run (more than 20 distinctions; projection only, as registered)'
        elif kk not in order_canon:
            cstat = 'not registered for the canonical command (projection only)'
        elif isinstance(c, str):
            cstat = c
        else:
            cstat = c
        for i, k in enumerate(r['knots']):
            k['canonical'] = cstat[i] if isinstance(cstat, list) else cstat
        structures.append({'labels': labels[kk], 'structure': [tc.kstr(x) for x in structs[kk]],
                           'n_knots': r['n_knots'], 'n_distinctions': r['n_distinctions'], 'n_states': r['n_states'],
                           'knots': r['knots']})
    n_canon_knots = sum(1 for s in structures for k in s['knots'] if isinstance(k['canonical'], dict)
                        and 'knot' in k['canonical'])
    disagree = [(s['labels'][0], k['knot']) for s in structures for k in s['knots'] if isinstance(k['canonical'], dict)
                and 'knot' in k['canonical'] and not k['canonical']['agrees with projection']]
    errors = [(s['labels'][0], k['knot']) for s in structures for k in s['knots'] if isinstance(k['canonical'], dict)
              and 'error' in k['canonical']]
    out = {'part': '8 (remainder)', 'unique structures': len(structures), 'structures': structures,
           'canonical candidates (registered order)': len(order_canon),
           'canonical structures cut': n_cut, 'canonical knots checked (this run)': n_canon_knots,
           'canonical knots checked early': early['knots checked'],
           'canonical disagreements with projection': disagree, 'canonical errors': errors,
           'wall_projection_s': wall_proj, 'wall_canonical_s': wall_canon, 'wall_s': round(time.time() - T0, 1),
           'processes': nproc, 'budget_s': round(budget)}
    tc.dump('part8_knots.json', out)
    print({k: v for k, v in out.items() if k != 'structures'})


if __name__ == '__main__':
    main()
