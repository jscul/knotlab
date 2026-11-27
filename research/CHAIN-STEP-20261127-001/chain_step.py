"""chain_step.py OUT.jsonl [--sample K --seed S] [--chunk I/C] [--rounds R] [--converse-upto F]: chains of eight and
the step one layer up, round by round.  CHAIN-STEP-20261127-001; README.md.

For each sampled census start (outside the samples of UPPER-GROWN and FOUR-CLAUSE, their pilots and start 420), at
rounds 0..R of ordinary growth:
  chains     the number of chains of eight three-place knots (chains.py; capped at 1,000)
  mapped     for at most three chains: the bare chain's pattern carried onto the chain (its six agreements on the
             chain's own distinctions) and checked on the whole stage by a solver: the four lower triples each miss
             exactly their triple, no lower reading is read at a knot, the three upper relations take seven words with
             every pair free, and every one of the chain's eight laws is needed
  converse   on stages of rounds 1 and 2 with at most F distinctions: the full four-clause search (FOUR-CLAUSE's
             fourclause.py), whether a step occurs, and whether the stage has a chain"""
import sys, json, random, time, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'FOUR-CLAUSE-20261127-001')); sys.path.insert(0, str(HERE.parent / 'UPPER-GROWN-20261127-001'))
import chains as CH, fourclause as FC, boxes as BX
from pysat.solvers import Minisat22
RB = BX.RB

# the bare chain of eight, knot i = (2i, 2i+1, 2i+2): its one pattern (post/chain_replay.json of FOUR-CLAUSE), in the
# order A0, A1, B0, B1, C0, C1 of fourclause.find_patterns, each with forbidden value 1
BARE = [[3, 4, 5], [11, 12, 13], [0, 1, 10], [6, 15, 16], [7, 8, 9], [2, 14]]


def chain_labels(sup, ch):
    """map the bare chain's distinctions 0..16 to the stage's: 2i+2 is shared by chain knots i and i+1, 2i+1 is knot i's
    own middle distinction, 0 and 16 the end knots' other own distinctions"""
    lab = {}
    for i in range(7):
        sh = set(sup[ch[i]]) & set(sup[ch[i + 1]]); assert len(sh) == 1; lab[2 * i + 2] = sh.pop()
    for i in range(8):
        own = [x for x in sup[ch[i]] if x not in lab.values()]
        if i == 0: lab[0], lab[1] = own
        elif i == 7: lab[15], lab[16] = own
        else: lab[2 * i + 1] = own[0]
    return lab


def check_mapped(sup, ch):
    lab = chain_labels(sup, ch); C = [[lab[x] for x in c] for c in BARE]
    names = sorted({x for r in sup for x in r}); var = {x: i + 1 for i, x in enumerate(names)}; top = [len(names)]
    def fresh():
        top[0] += 1; return top[0]
    def laws(vmap, skip=None):
        cl = []
        for q, r in enumerate(sup):
            if q == skip: continue
            v = [vmap[x] for x in r]; cl += [v, [-u for u in v]]
        return cl
    def agree(xs, cl):
        r = fresh()
        for x in xs[1:]: cl.extend([[-r, -xs[0], x], [-r, xs[0], -x]])
        cl.extend([[r] + [-x for x in xs], [r] + list(xs)]); return r
    def build(skip=None):
        cl = laws(var, skip); R = [agree([var[x] for x in c], cl) for c in C]
        U = []
        for both in range(3):
            us = []
            for i in range(3):
                a, b = R[2 * i], R[2 * i + 1]; u = fresh()
                if i == both: cl.extend([[-u, a], [-u, b], [u, -a, -b]])
                else: cl.extend([[-u, a, b], [u, -a], [u, -b]])
                us.append(u)
            U.append(us)
        return cl, R, U
    cl, R, U = build(); s = Minisat22(bootstrap_with=cl); rec = {}
    lower = [(0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4)]
    rec['lower triples miss exactly their triple'] = all(
        [not s.solve(assumptions=[R[t] if w else -R[t] for t, w in zip(tr, ws)]) for ws in itertools.product((0, 1), repeat=3)]
        == [ws == (1, 1, 1) for ws in itertools.product((0, 1), repeat=3)] for tr in lower)
    up = []
    for us in U:
        words = [s.solve(assumptions=[u if w else -u for u, w in zip(us, ws)]) for ws in itertools.product((0, 1), repeat=3)]
        free = all(any(s.solve(assumptions=[us[i] if a else -us[i], us[j] if b else -us[j]]) for _ in [0])
                   for i, j in ((0, 1), (0, 2), (1, 2)) for a in (0, 1) for b in (0, 1))
        up.append({'upper words': sum(words), 'pairs free': free})
    s.delete()
    rec['upper'] = up
    need = []
    for q in ch:
        cl2, R2, U2 = build(skip=q); s2 = Minisat22(bootstrap_with=cl2)
        need.append(all(s2.solve(assumptions=list(us)) for us in U2)); s2.delete()
    rec['every chain law needed'] = all(need)
    # no lower reading read at a knot: two allowed states equal on the knot's values, the reading different
    var2 = {x: fresh() for x in names}; cl3 = laws(var) + laws(var2)
    r1 = [agree([var[x] for x in c], cl3) for c in C]; r2 = [agree([var2[x] for x in c], cl3) for c in C]
    s3 = Minisat22(bootstrap_with=cl3); read = False
    for r in sup:
        same = []
        for x in r:
            e = fresh(); same.append(e); s3.add_clause([-e, -var[x], var2[x]]); s3.add_clause([-e, var[x], -var2[x]])
        for a, b in zip(r1, r2):
            if not s3.solve(assumptions=same + [a, -b]): read = True; break
        if read: break
    s3.delete(); rec['no lower reading read at a knot'] = not read
    rec['a step'] = (rec['lower triples miss exactly their triple'] and rec['no lower reading read at a knot'] and
                     all(u['upper words'] == 7 and u['pairs free'] for u in up))
    return rec


if __name__ == '__main__':
    out = sys.argv[1]; args = sys.argv[2:]
    get = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    K, seed, R, conv = get('--sample', 1000), get('--seed', 20261131), get('--rounds', 6), get('--converse-upto', 19)
    starts = RB.forbid.census(); allidx = list(range(len(starts)))
    pil = set(random.Random(1).sample(allidx, 10))
    ug = set(random.Random(20261128).sample([i for i in allidx if i not in pil], 1000))
    used = pil | ug | {420}
    fc = set(random.Random(20261130).sample([i for i in allidx if i not in used], 600))
    pool = [i for i in allidx if i not in used | fc]
    order = sorted(random.Random(seed).sample(pool, K))
    if '--chunk' in args:
        ci, cn = map(int, args[args.index('--chunk') + 1].split('/')); order = order[ci::cn]
    with open(out, 'w') as f:
        for i in order:
            t0 = time.time(); S = RB.forbid.supports_of(starts[i]); rec = {'start': 'census %d' % i, 'rounds': []}
            for t, (sup, born) in enumerate(RB.stages(S, 'nae', R)):
                ch = list(CH.chains(sup, 8, 1000))
                row = {'round': t, 'knots': len(sup), 'distinctions': len({x for k in sup for x in k}), 'chains': len(ch)}
                if ch: row['mapped'] = [check_mapped(sup, c) for c in ch[:3]]
                if t in (1, 2) and row['distinctions'] <= conv:
                    st = RB.Stage(sup, 'nae'); b = RB.bonds(st, 'agree', born=born)['bonds']; P = FC.find_patterns(b)
                    rel = [r for p in P[:60] for r in FC.read_pattern(st, p, len(S))]
                    row['converse'] = {'patterns': len(P), 'steps': sum(1 for r in rel if len(r['upper words']) < 8 and r['pairs free'] and not r['an upper reading read at one lower bond'])}
                rec['rounds'].append(row)
            rec['seconds'] = round(time.time() - t0, 1); f.write(json.dumps(rec) + '\n'); f.flush()
