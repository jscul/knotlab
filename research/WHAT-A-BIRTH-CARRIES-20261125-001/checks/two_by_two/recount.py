"""A second count for the probe, with none of ticket B's course reading: for one part X with three or more partners,
bar every subset of three of its partners, and for each run list, round by round, the knots descended from X only with
their numbers of places (a signature of X's course that uses only the growth and the descent bits)."""
import sys, json, itertools, collections
import tbt
from tbt import eng, read, View, ROOT
def sig(run, bits, i, s):
    S = run.S; out = []
    for t in range(s + 1, run.rounds_read + 1):
        ks = [u for u in range(S.n_knots) if S.made[u] == t and bits[u] == (1 << i)]
        out.append((t, len(ks), tuple(sorted(collections.Counter(len(S.places[u]) for u in ks).items()))))
    return tuple(out)
spec = json.loads(sys.argv[1])
st = json.load(open(ROOT + '/research/WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json'))
if spec['start'].startswith('census:'):
    stars = json.load(open(ROOT + '/research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'))[int(spec['start'].split(':')[1])]['stars']
else:
    stars = st['extra']['stars'] if spec['start'] == st['extra']['name'] else st['stars'][spec['start']]
law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
s = 4
runA = eng.Run(law, stars=stars, rounds=7); keysA = read.Keys(runA)
R_s = runA.recs[s]['roster']
parts = eng.roster_parts(R_s) if R_s.parts is None else R_s.parts
member_part = {u: i for i, P in enumerate(parts) for u in P}
cls_parts = eng.classes_of_parts(runA.snaps[s], parts)
bitsA = read.desc_bits(runA, s, member_part)
meetA = read.first_meetings(runA, s, bitsA)
strict = collections.defaultdict(dict); cache = {}
for (i, j), (t, how) in meetA.items():
    if cls_parts[i] == cls_parts[j]: continue
    for a, b in ((i, j), (j, i)):
        v = View(runA, keysA, bitsA, a, b, s, parts[a], parts[b])
        if t not in cache: cache[t] = (read.RoundIndex(runA.recs[t - 1], bitsA), read.ancestor_bits(runA.snaps[t]))
        if read.linking(v, t, cache[t][0], cache[t][1])['strict']: strict[a][b] = t
res = collections.Counter(); shown = 0
for i in sorted(strict):
    ps = sorted(strict[i])
    if len(ps) < 3: continue
    ps = ps[:3]
    sigs = {}
    for r in range(4):
        for sub in itertools.combinations(ps, r):
            if not sub: run, bits = runA, bitsA
            else:
                run = eng.Run(law, base=runA, base_round=s, bar=[u for p in sub for u in parts[p]], rounds=7)
                bits = read.desc_bits(run, s, member_part)
            sigs[sub] = sig(run, bits, i, s)
    by_n = collections.defaultdict(set)
    for sub, g in sigs.items(): by_n[len(sub)].add(g)
    same_within = all(len(v) == 1 for v in by_n.values())
    distinct_across = len({next(iter(v)) for v in by_n.values()}) if same_within else None
    res[(len(strict[i]), same_within, distinct_across)] += 1
    if shown < 1:
        shown += 1
        for n in sorted(by_n): print('  barred', n, '->', sorted(by_n[n])[0])
    if sum(res.values()) >= 12: break
print(spec['start'], spec['ration'], {str(k): v for k, v in res.items()}, '(partners of X, same signature for every choice of which, number of distinct signatures over 0..3 barred)')
