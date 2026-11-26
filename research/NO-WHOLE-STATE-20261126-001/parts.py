"""parts.py: patterns with no state of the whole, read part by part (README.md, part A). A pattern is a set of parity
knots (each a set of distinctions with a parity, 0 even or 1 odd); a context is the set of distinctions the readers read
together under one choice of settings. The PART of a context is a scaffold, read in two forms:
    closed   the knots lying wholly within the context's read distinctions
    open     the knots touching them, every distinction they hold that is not read summed over
and its weighting is the count of the part's allowed states, each counted once (equal weight within the part). Read per
pattern: whether the whole has an allowed state; each context's table; whether every context's part has an allowed
state; agreement on overlaps (each set of distinctions read in two contexts has the same distribution in both: no
signalling); and the score of the game the pattern encodes.

    parts.py      the three-reader pattern, the nine-distinction square, and a two-reader pattern of 3-place knots"""
import itertools, json
from fractions import Fraction


def allowed(knots, names):
    """allowed assignments of `names` (a list) under the knots, as a dict word -> count over unread distinctions"""
    out = {}
    others = sorted({d for k, _ in knots for d in k} - set(names))
    for vals in itertools.product((0, 1), repeat=len(names)):
        a = dict(zip(names, vals)); n = 0
        for rest in itertools.product((0, 1), repeat=len(others)):
            b = dict(a); b.update(zip(others, rest))
            if all(sum(b[d] for d in k) % 2 == p for k, p in knots): n += 1
        if n: out[vals] = n
    return out


def part(pattern, read, form):
    if form == 'closed': return [(k, p) for k, p in pattern if set(k) <= set(read)]
    return [(k, p) for k, p in pattern if set(k) & set(read)]


def table(pattern, read, form):
    t = allowed(part(pattern, read, form), list(read))
    tot = sum(t.values())
    return {w: Fraction(c, tot) for w, c in t.items()} if tot else {}


def marginal(t, read, keep):
    out = {}
    for w, p in t.items():
        k = tuple(w[read.index(d)] for d in keep); out[k] = out.get(k, 0) + p
    return out


def check(name, pattern, contexts, score, form):
    names = sorted({d for k, _ in pattern for d in k})
    whole = allowed(pattern, names)
    T = {c: table(pattern, list(read), form) for c, read in contexts.items()}
    every_part = all(T[c] for c in contexts)
    agree = True
    for (c1, r1), (c2, r2) in itertools.combinations(contexts.items(), 2):
        common = sorted(set(r1) & set(r2))
        if common and T[c1] and T[c2] and marginal(T[c1], list(r1), common) != marginal(T[c2], list(r2), common): agree = False
    return {'pattern': name, 'part': form, 'whole has an allowed state': bool(whole), 'every part allowed': every_part,
            'overlaps agree (no signalling)': agree, 'score': str(score(T, contexts)) if every_part else None}


def ghz():
    # readers A, B, C, settings 0/1; distinction (reader, setting); the four parity knots of the three-reader argument
    knots = [((('A', 0), ('B', 0), ('C', 0)), 0), ((('A', 0), ('B', 1), ('C', 1)), 1),
             ((('A', 1), ('B', 0), ('C', 1)), 1), ((('A', 1), ('B', 1), ('C', 0)), 1)]
    contexts = {s: [('A', s[0]), ('B', s[1]), ('C', s[2])] for s in itertools.product((0, 1), repeat=3)}
    def win(T, contexts):
        target = {(0, 0, 0): 0, (0, 1, 1): 1, (1, 0, 1): 1, (1, 1, 0): 1}
        return sum(sum(p for w, p in T[s].items() if sum(w) % 2 == t) for s, t in target.items()) / 4
    return knots, contexts, win


def square():
    # nine distinctions (i, j); rows even; columns 0 and 1 even, column 2 odd (the literature's magic square)
    knots = [(tuple((i, j) for j in range(3)), 0) for i in range(3)] + [(tuple((i, j) for i in range(3)), 1 if j == 2 else 0) for j in range(3)]
    contexts = {(i, j): sorted(set((i, k) for k in range(3)) | set((k, j) for k in range(3))) for i in range(3) for j in range(3)}
    def win(T, contexts):
        tot = 0
        for (i, j), t in T.items():
            read = contexts[(i, j)]
            for w, p in t.items():
                a = {d: w[read.index(d)] for d in read}
                row = sum(a[(i, k)] for k in range(3)) % 2 == 0
                col = sum(a[(k, j)] for k in range(3)) % 2 == (1 if j == 2 else 0)
                if row and col: tot += p                     # the shared cell is one distinction, so it agrees by itself
        return tot / 9
    return knots, contexts, win


def two_reader():
    # Alice reads a pair (a_x, a'_x) and reports its parity; Bob reads one distinction b_y; one 3-place knot per setting
    # pair, odd at 11: out_A + out_B = x y
    knots = [((('a', x), ('a2', x), ('b', y)), x & y) for x in (0, 1) for y in (0, 1)]
    contexts = {(x, y): [('a', x), ('a2', x), ('b', y)] for x in (0, 1) for y in (0, 1)}
    def chsh(T, contexts):
        E = {}
        for (x, y), t in T.items():
            E[(x, y)] = sum(p * (1 if (w[0] ^ w[1]) == w[2] else -1) for w, p in t.items())
        return E[(0, 0)] + E[(0, 1)] + E[(1, 0)] - E[(1, 1)]
    return knots, contexts, chsh


if __name__ == '__main__':
    for name, make in (('three readers', ghz), ('nine-distinction square', square), ('two readers, 3-place knots', two_reader)):
        k, c, s = make()
        for form in ('closed', 'open'):
            print(json.dumps(check(name, k, c, s, form)))
