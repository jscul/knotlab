"""The thread's confirming checks for the probe (in place of a registered study):
(a) every one of the 23 starts regrown under the ordinary count with a second engine (lr_core.own_round, ORD with STALL), and the
    members, their one-step relation and the counts recomputed from scratch, at rounds 10, 15 and 20, against the probe's records;
(b) the reach study's own knot test (run 3's routine, unchanged: the start knots and a seeded sample of 200 made knots, under
    not-all-equal by two methods and under parity by two methods) on every probe run of the 23 starts under four laws."""
import sys, os, json, gzip, collections, time
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
X = ROOT + '/experiments/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach'
sys.dont_write_bytecode = True
sys.path.insert(0, X)
sys.path.insert(0, ROOT + '/experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round')

def second(args):
    idx, rounds_list = args
    import lr_core
    cs = json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))
    S = lr_core.Str([list(s) for s in cs[idx]['stars']])
    out = {}
    for t in range(1, max(rounds_list) + 1):
        rec = lr_core.own_round(S, 'ORD', 'STALL')
        if rec.get('stalled'): break
        if t in rounds_list:
            members = [u for u in range(len(S.places)) if S.usable(u)]
            met = collections.defaultdict(set)
            for u in members:
                for d in S.places[u]:
                    for w in S.holders[d]:
                        if w != u: met[w].add(u)
            adj = {u: set() for u in members}
            for w, M in met.items():
                if len(M) >= 2:
                    for a in M: adj[a] |= M - {a}
            nb = collections.Counter(len(adj[u]) for u in members)
            env = []
            for s in members:
                dist = {s: 0}; fr = [s]; counts = [1]
                while fr:
                    nx_ = []
                    for a in fr:
                        for b in adj[a]:
                            if b not in dist: dist[b] = dist[a] + 1; nx_.append(b)
                    if nx_: counts.append(counts[-1] + len(nx_))
                    fr = nx_
                env = [max(env[r] if r < len(env) else (env[-1] if env else 0), counts[r] if r < len(counts) else counts[-1]) for r in range(max(len(env), len(counts)))]
            out[t] = {'knots': len(S.places), 'members': len(members), 'neighbours': {str(k): v for k, v in sorted(nb.items())}, 'env': env[:30]}
    return idx, out

def ktest_item(it):
    import kwr, run3
    kwr.cap_memory(6)
    return run3.run_item(it)

if __name__ == '__main__':
    what = sys.argv[1]
    fast = [int(s.split(':')[1]) for s in json.load(open(os.path.join(HERE, 'fast_starts.json')))['L0 fast']]
    if what == 'second':
        probe = {}
        for l in gzip.open(os.path.join(HERE, 'probe_runs.jsonl.gz'), 'rt'):
            d = json.loads(l)
            if d['law'] == 'L0' and d['knot law'] == 'nae': probe[int(d['start'].split(':')[1])] = d
        t0 = time.time(); res = []
        with mp.Pool(6) as pool:
            for idx, out in pool.imap_unordered(second, [(i, (10, 15, 20)) for i in fast]):
                for t, o in out.items():
                    st = next((s for s in probe[idx]['stages'] if s['round'] == t), None)
                    if st is None: continue
                    pe = st['greatest count at each r (first 30)']
                    full = st['sources'] == st['of members in the part']
                    ok = (o['knots'] == st['knots'] and o['members'] == st['members'] and
                          (not full or (o['neighbours'] == {str(k): v for k, v in st['neighbours within one step, by count of members'].items()} and o['env'][:len(pe)] == pe[:len(o['env'])])))
                    res.append({'start': idx, 'round': t, 'knots': o['knots'], 'members': o['members'], 'every member read by the probe': full, 'equal': bool(ok)})
        json.dump(res, open(os.path.join(HERE, 'confirm_second.json'), 'w'), indent=1)
        print(len(res), 'stages;', sum(r['equal'] for r in res), 'equal;', round(time.time() - t0, 1), 's;', 'sampled by the probe:', sum(not r['every member read by the probe'] for r in res))
        print([ (r['start'], r['round']) for r in res if not r['equal']])
    else:
        laws = sys.argv[2].split(',')
        its = [{'item': k, 'source': 'probe', 'start': 'census:%d' % i, 'law': l, 'rounds': 40} for k, (i, l) in enumerate((i, l) for i in fast for l in laws)]
        t0 = time.time(); recs = []
        with mp.Pool(6, maxtasksperchild=20) as pool:
            for rec in pool.imap_unordered(ktest_item, its):
                recs.append(rec)
        recs.sort(key=lambda r: r['item'])
        json.dump(recs, open(os.path.join(HERE, 'confirm_ktest.json'), 'w'), indent=1)
        tn = sum(r['nae']['tested'] for r in recs); fn = sum(len(r['nae']['fails']) for r in recs); dn = sum(r['nae']['disagree'] for r in recs); un = sum(r['nae']['untested'] for r in recs)
        tp = sum(r['parity']['tested'] for r in recs); fp = sum(len(r['parity']['fails']) for r in recs); dp = sum(r['parity']['disagree'] for r in recs)
        print(len(recs), 'runs;', 'not-all-equal: tested', tn, 'failing', fn, 'untested', un, 'methods disagreeing', dn, '| parity: tested', tp, 'failing', fp, 'methods disagreeing', dp, '|', round(time.time() - t0, 1), 's')
        print('parity closing rounds:', collections.Counter(str(r['parity']['closing_round']) for r in recs))
