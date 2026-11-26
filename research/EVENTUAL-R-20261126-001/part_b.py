"""part_b.py: rule R read off the whole structure (README.md, part B; frozen in preregistration.md). Two values commute
exactly when some knot of the whole structure holds both. A birth takes only loose distinctions (`rival_growth.py`,
lines 71 and 81: a funded round consumes every loose distinction, one per parent), so a pair of distinctions is
settled once either is held twice (no later knot can hold it) or once both are held by one knot; it is open while both
are loose in different knots and growth goes on. A stalled or closed structure is the whole, and every pair is settled.
Sampled census starts (forbid.py's census, 7,075 starts of three to five knots, seed 20261128, uniform), ordinary growth
under parity on the canonical engine, up to ROUNDS rounds. Per start:
    B1  the first round with a settled pair of knots whose operators fail to commute (the whole's R then has no state
        making every knot definite, finally); at the end, the settled commuting, settled failing and open knot pairs
    B2  the flip formula: every change of a knot pair's commutation from one round to the next (R read off each round)
        is between two knots born in the earlier round, and its parity is the parity of their common children
    B3  the demand for a state as a prediction: at each round still growing, is there a choice of the open pairs that
        makes every knot pair commute (GF(2)), is it unique, and does the next round realise one
    B4  on the structures that close with commuting knots: a reader who signs products of knots by the GF(2) sum
        against the operator signs, on every read set (contradictions met), and laws gained from later layers
    part_b.py COUNT ROUNDS [--named]"""
import sys, json, random, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import ops, forbid, part_a            # noqa: E402


def grow(start, rounds):
    stages = [tuple(tuple(k) for k in start)]; births = []; end = 'growing'
    for r in range(1, rounds + 1):
        new, status, bs = forbid.grown(stages[-1], 'parity', 'ordinary')
        if status != 'funded':
            end = 'closed' if status == 'closed' else 'stalled'; break
        stages.append(tuple(tuple(k) for k in new)); births.append(bs)
    else:
        new, status, _ = forbid.grown(stages[-1], 'parity', 'ordinary')
        end = 'growing' if status == 'funded' else ('closed' if status == 'closed' else 'stalled')
    return stages, births, end


def pair_status(knots, final):
    """per knot pair: ('commute' | 'fail' | 'open', number of settled failing place pairs, list of open place pairs)"""
    h = ops.holders(knots); loose = {d for d, hs in h.items() if len(hs) == 1}; co = ops.coheld(knots)
    out = {}
    for u, v in itertools.combinations(range(len(knots)), 2):
        fail, open_ = 0, []
        for e in knots[u]:
            for f in knots[v]:
                if e == f or (min(e, f), max(e, f)) in co: continue
                if not final and e in loose and f in loose: open_.append((min(e, f), max(e, f)))
                else: fail += 1
        out[(u, v)] = ('open' if open_ else ('commute' if fail % 2 == 0 else 'fail'), fail, open_)
    return out


def born(stages, t):
    lo = len(stages[t - 1]) if t > 0 else 0
    return set(range(lo, len(stages[t])))


def study(stages, births, end):
    out = {'rounds': len(stages) - 1, 'end': end, 'knots': len(stages[-1])}
    final_at = len(stages) - 1 if end != 'growing' else None
    first_fail = None; ends = None
    for t, St in enumerate(stages):
        ps = pair_status([list(k) for k in St], final=(t == final_at))
        if first_fail is None and any(s[0] == 'fail' for s in ps.values()): first_fail = t
        if t == len(stages) - 1: ends = collections.Counter(s[0] for s in ps.values())
    out['B1 first round with a settled failing pair'] = first_fail
    out['B1 knot pairs at the end'] = dict(ends)
    # B2: commutation under R read off each round, round t against t + 1
    flips = collections.Counter()
    for t in range(len(stages) - 1):
        A, B = [list(k) for k in stages[t]], [list(k) for k in stages[t + 1]]
        def comm(knots, u, v):
            co = ops.coheld(knots)
            return sum(1 for e in knots[u] for f in knots[v] if e != f and (min(e, f), max(e, f)) not in co) % 2 == 0
        newest = born(stages, t)
        kids = collections.Counter()
        for b in births[t]:
            for u, v in itertools.combinations(sorted(b['parents']), 2): kids[(u, v)] += 1
        for u, v in itertools.combinations(range(len(A)), 2):
            changed = comm(A, u, v) != comm(B, u, v)
            predicted = u in newest and v in newest and kids[(u, v)] % 2 == 1
            flips['changes'] += changed; flips['changes predicted by the formula'] += changed and predicted
            flips['formula wrong'] += changed != predicted
    out['B2'] = dict(flips)
    # B3: the demand for a state at each round still growing
    b3 = []
    for t in range(len(stages) - 1):
        St = [list(k) for k in stages[t]]; ps = pair_status(St, final=False)
        opens = sorted({p for s in ps.values() for p in s[2]}); idx = {p: i for i, p in enumerate(opens)}
        rows = []
        for (u, v), (st, fail, op) in ps.items():
            r = 0
            for p in op: r ^= 1 << idx[p]
            rows.append((r, fail % 2))
        sol = ops.reduce_laws(rows)
        exists = not sol[1]
        rank = len(sol[0])
        # realised: an open pair fails to commute later unless the next round's births hold both
        co_next = ops.coheld([list(k) for k in stages[t + 1]])
        y = {p: int(p not in co_next) for p in opens}
        realised = all((sum(y[p] for p in op) + fail) % 2 == 0 for (st, fail, op) in ps.values())
        b3.append({'round': t, 'open pairs': len(opens), 'a choice exists': exists,
                   'unique': exists and rank == len(opens), 'next round realises one': realised})
    out['B3'] = b3
    # B4: closers whose knots commute
    if end == 'closed':
        F = [list(k) for k in stages[-1]]; m = 1 + max(d for k in F for d in k)
        vals = ops.realise(m, ops.rule_R(F, m)); K = ops.knot_ops(F, vals)
        if ops.r1(K):
            s, closed = ops.signs(F, K)
            b4 = collections.Counter()
            for P in ops.maximal_read_sets(F):
                a3 = ops.laws(F, vals, K, s, P, range(len(F)))
                if len(F) <= 12:
                    b4['GF(2) reader contradicted'] += part_a.rule_ii(F, s, P) != a3
                for t in range(len(stages) - 1):
                    use = range(len(stages[t])); Dt = {d for u in use for d in F[u]}
                    Q = tuple(sorted(set(P) & Dt))
                    if Q and ops.laws(F, vals, K, s, Q, use) != ops.laws(F, vals, K, s, Q, range(len(F))):
                        b4['laws gained from later layers'] += 1
            out['B4'] = {'forced sign': 'odd' if closed[0][1] else 'even', **b4}
        else:
            out['B4'] = 'knots do not commute'
    return out


if __name__ == '__main__':
    count, rounds = int(sys.argv[1]), int(sys.argv[2])
    if '--named' in sys.argv:
        named = {'ring of three, one loose each': ((0, 1, 2), (1, 3, 4), (3, 0, 5)),
                 'four mutually meeting knots, one loose each': ((0, 1, 2, 6), (0, 3, 4, 7), (1, 3, 5, 8), (2, 4, 5, 9)),
                 'one knot of three places': ((0, 1, 2),), 'one knot of four places': ((0, 1, 2, 3),),
                 'two knots of four and three places sharing one': ((0, 1, 2, 3), (0, 4, 5))}
        for name, start in named.items():
            print(json.dumps({'start': name, **study(*grow(start, rounds))}), flush=True)
        sys.exit()
    S = forbid.census(); picks = sorted(random.Random(20261128).sample(range(len(S)), count))
    for i in picks:
        print(json.dumps({'start': i, **study(*grow(forbid.supports_of(S[i]), rounds))}), flush=True)
