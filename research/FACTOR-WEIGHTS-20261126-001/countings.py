"""countings.py: do the record's countings factor over readers no knot joins? (README.md, part A; frozen in
preregistration.md.) Census starts (forbid.py's census of 7,075 starts of three to five knots; COUNT drawn uniformly
with seed 20261129; kept when the grown structure has at most CAP distinctions), parity and not-all-equal, the three arms
of the canonical engine (ordinary, one fewer, arity floor), up to two rounds. Three weightings of the grown structure's
words:
    finish      every allowed word once (the record's counting from the finish)
    start       the start's allowed words equally weighted, each round dividing an old word's weight equally among its
                completions, renormalised at the end (the record's counting from the start, stages = rounds; TWO-COUNTINGS
                definitions 1.3-3.4)
    one stage   a control the record does not use: each start word's weight divided equally among all its finished
                completions at once (the whole growth as one stage)
The test (the advisor's): for every pair of distinctions a, b that no knot holds together and every assignment of the
rest, the two-by-two table W(a, b) has rank at most one (W(0,0) W(1,1) = W(0,1) W(1,0)), as a weighting that is a product
of one factor per knot must. Counted: pairs and assignments tested, and failures, per weighting.
    countings.py COUNT CAP"""
import sys, json, random, itertools
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import forbid            # noqa: E402


def law_ok(law, vals):
    if law == 'parity': return sum(vals) % 2 == 0
    return 0 < sum(vals) < len(vals)


def allowed_words(knots, D, law):
    out = []
    for v in itertools.product((0, 1), repeat=len(D)):
        w = dict(zip(D, v))
        if all(law_ok(law, [w[d] for d in k]) for k in knots): out.append(v)
    return out


def weightings(stages, rounds, law):
    D = sorted({d for k in stages[-1] for d in k}); pos = {d: i for i, d in enumerate(D)}
    final = allowed_words(stages[-1], D, law)
    finish = {w: Fraction(1) for w in final}
    d0 = sorted({d for k in stages[0] for d in k})
    start0 = allowed_words(stages[0], d0, law)
    # start: stage by stage
    weights = {tuple(zip(d0, v)): Fraction(1) for v in start0}
    for births in rounds:
        fresh = sorted({d for b in births for d in b['fresh']})
        new_knots = [tuple(b['inputs']) + tuple(b['fresh']) for b in births]
        nxt = {}
        for key, x in weights.items():
            w = dict(key); comps = []
            for v in itertools.product((0, 1), repeat=len(fresh)):
                w2 = dict(w); w2.update(zip(fresh, v))
                if all(law_ok(law, [w2[d] for d in k]) for k in new_knots): comps.append(tuple(sorted(w2.items())))
            for c in comps: nxt[c] = nxt.get(c, 0) + x / len(comps)
        weights = nxt
    start = {tuple(dict(k)[d] for d in D): x for k, x in weights.items()}
    # one stage: each start word divided among all its finished completions
    by_start = {}
    for w in final:
        key = tuple(w[pos[d]] for d in d0); by_start.setdefault(key, []).append(w)
    one = {w: Fraction(1, len(ws)) for ws in by_start.values() for w in ws}
    return D, {'finish': finish, 'start': start, 'one stage': one}


def factor_test(knots, D, W):
    held = set()
    for k in knots:
        for a, b in itertools.combinations(sorted(set(k)), 2): held.add((a, b))
    pairs = [(a, b) for a, b in itertools.combinations(D, 2) if (a, b) not in held]
    pos = {d: i for i, d in enumerate(D)}
    tested = failed = 0
    for a, b in pairs:
        ia, ib = pos[a], pos[b]; rest = {}
        for w, x in W.items():
            key = tuple(v for i, v in enumerate(w) if i not in (ia, ib))
            rest.setdefault(key, {})[(w[ia], w[ib])] = x
        for key, t in rest.items():
            g = lambda u, v: t.get((u, v), Fraction(0))
            tested += 1
            failed += g(0, 0) * g(1, 1) != g(0, 1) * g(1, 0)
    return len(pairs), tested, failed


def run(count, cap):
    S = forbid.census(); picks = random.Random(20261129).sample(range(len(S)), count)
    tally = {}
    for i in picks:
        start = forbid.supports_of(S[i])
        for law in ('parity', 'nae'):
            for arm in ('ordinary', 'one_fewer', 'arity_floor'):
                stages = [tuple(tuple(k) for k in start)]; rounds = []
                for r in range(2):
                    new, status, births = forbid.grown(stages[-1], law, arm)
                    if status != 'funded': break
                    stages.append(tuple(tuple(k) for k in new)); rounds.append(births)
                key = law + ' / ' + arm; t = tally.setdefault(key, {'growths': 0, 'over the cap or no round': 0})
                D = sorted({d for k in stages[-1] for d in k})
                if not rounds or len(D) > cap: t['over the cap or no round'] += 1; continue
                D, Ws = weightings(stages, rounds, law)
                t['growths'] += 1
                for name, W in Ws.items():
                    n, tested, failed = factor_test([list(k) for k in stages[-1]], D, W)
                    tt = t.setdefault(name, {'pairs': 0, 'tables tested': 0, 'tables that do not factor': 0, 'growths with one': 0})
                    tt['pairs'] += n; tt['tables tested'] += tested; tt['tables that do not factor'] += failed
                    tt['growths with one'] += failed > 0
    for k, v in tally.items(): print(json.dumps({k: v}))


if __name__ == '__main__':
    run(int(sys.argv[1]), int(sys.argv[2]))
