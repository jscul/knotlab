"""R8, the renamed starts, sampled (PC, "Runs", order 5; Lemma C-S1 at 8 rounds): each start of three and four knots
(the 219, in census order; dev 28) and each of its five renamings of R7, under the 42 laws, parity, the take-by-take
weighting, sample index 0, seed suffix |R8|<renaming> (|R8|none for the start itself); growths and pairs only.  For
each law and renaming, the share of growths with a pair, start against renamed start, two-sided Fisher exact at level
0.05/210; and one test for each renaming pooled over the 42 laws, at 0.05/5.  Writes R8.jsonl.gz and R8.json."""
import argparse
import multiprocessing as mp
import os
import random
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
from study import log  # noqa: E402

RENAMINGS = ('none', 'reversed', 'perm', 'shift', 'knots', 'distinctions')


def rename(stars, sid, how):
    """Dev 30: a renaming of the start's knots (their order) and of its distinctions (their labels)."""
    n = len(stars)
    labels = sorted({d for st in stars for d in st})
    L = len(labels)
    kperm = list(range(n))
    lmap = {l: l for l in labels}
    if how == 'none':
        pass
    elif how == 'reversed':
        kperm = kperm[::-1]
        lmap = {labels[j]: labels[L - 1 - j] for j in range(L)}
    elif how == 'perm':
        rnd = random.Random('C|rename|%s|perm' % sid)
        rnd.shuffle(kperm)
        p = labels[:]
        rnd.shuffle(p)
        lmap = {labels[j]: p[j] for j in range(L)}
    elif how == 'shift':
        lmap = {labels[j]: labels[(j + 1) % L] for j in range(L)}
    elif how == 'knots':
        random.Random('C|rename|%s|knots' % sid).shuffle(kperm)
    elif how == 'distinctions':
        p = labels[:]
        random.Random('C|rename|%s|distinctions' % sid).shuffle(p)
        lmap = {labels[j]: p[j] for j in range(L)}
    else:
        raise ValueError(how)
    return [[lmap[d] for d in stars[kperm[i]]] for i in range(n)]


def job(args):
    idx, how, law = args
    st = mcc.census()[idx]
    spec = mcc.Spec.from_name(law)
    stars = rename(st['stars'], st['id'], how)
    base = mcc.base_seed(st['id'], spec, 0) + '|R8|' + how
    t0 = time.time()
    try:
        g = mcc.Growth(stars, spec, st['id'], 0, base=base)
        prs = g.pairs()
    except MemoryError:
        return {'index': idx, 'start': st['id'], 'renaming': how, 'law': law, 'error': 'memory'}
    has = any(v[1] > 0 for v in prs.values())
    return {'index': idx, 'start': st['id'], 'renaming': how, 'law': law, 'seed': g.seed, 'rounds': g.G.R,
            'stop': g.G.stop, 'knots': g.G.knots(), 'has_pair': has, 'pairs_by_s': {s: v[1] for s, v in prs.items()},
            'set_aside_parity': st['set_aside_parity'], 'sec': round(time.time() - t0, 3)}


def analyse(rows):
    laws = [s.name() for s in mcc.family_both('parity')]
    out = {}
    for subset, keep in (('starts read', lambda r: True), ('starts read, not set aside', lambda r: not r['set_aside_parity'])):
        cnt = defaultdict(lambda: [0, 0])
        for r in rows:
            if 'error' in r or not keep(r):
                continue
            c = cnt[(r['law'], r['renaming'])]
            c[0] += int(r['has_pair'])
            c[1] += 1
        tests = []
        rej = 0
        nstarts = len({r['index'] for r in rows if 'error' not in r and keep(r)})
        for law in laws:
            a = cnt[(law, 'none')]
            for how in RENAMINGS[1:]:
                b = cnt[(law, how)]
                p = mcc.fisher_two(a[0], a[1], b[0], b[1])
                tests.append({'law': law, 'renaming': how, 'start': a, 'renamed': b, 'p': p,
                              'rejected': p <= 0.05 / 210})
                rej += int(p <= 0.05 / 210)
        pooled = []
        for how in RENAMINGS[1:]:
            a = [sum(cnt[(law, 'none')][0] for law in laws), sum(cnt[(law, 'none')][1] for law in laws)]
            b = [sum(cnt[(law, how)][0] for law in laws), sum(cnt[(law, how)][1] for law in laws)]
            p = mcc.fisher_two(a[0], a[1], b[0], b[1])
            pooled.append({'renaming': how, 'start': a, 'renamed': b, 'p': p, 'rejected': p <= 0.05 / 5})
        out[subset] = {'starts': nstarts, 'tests': tests, 'rejections': rej, 'pooled': pooled,
                       'pooled_rejections': sum(x['rejected'] for x in pooled),
                       'smallest p': min(t['p'] for t in tests)}
    out['errors'] = [r for r in rows if 'error' in r]
    out['stops'] = dict((k, sum(1 for r in rows if r.get('stop') == k)) for k in ('knots', 'guard', 'residual_stall'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--analyse-only', action='store_true')
    ap.add_argument('--starts', type=int, default=219, help='a prefix of the 219 in census order (dev 49)')
    a = ap.parse_args()
    if not a.analyse_only:
        C = mcc.census()
        idxs = [i for i, s in enumerate(C) if s['n'] in (3, 4)]
        assert len(idxs) == 219
        idxs = idxs[:a.starts]
        laws = [s.name() for s in mcc.family_both('parity')]
        jobs = [(i, how, law) for i in idxs for how in RENAMINGS for law in laws]
        log('R8', len(jobs), 'growths')
        w = study.JsonLines('R8.jsonl.gz')
        t0 = time.time()
        ctx = mp.get_context('fork')
        with ctx.Pool(a.procs, initializer=study.cap_memory) as pool:
            for k, r in enumerate(pool.imap_unordered(job, jobs, chunksize=4), 1):
                w.write(r)
                if k % 5000 == 0:
                    w.flush()
                    log('R8 %d/%d %.0f s' % (k, len(jobs), time.time() - t0))
        w.close()
        log('R8 done in', round(time.time() - t0, 1), 's')
    rows = study.read_jsonl('R8.jsonl.gz')
    res = analyse(rows)
    res['growths'] = len(rows)
    study.write_json('R8.json', res)
    log('R8', {k: (v['rejections'], v['pooled_rejections']) for k, v in res.items() if isinstance(v, dict) and
               'rejections' in v})


if __name__ == '__main__':
    main()
