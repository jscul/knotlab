"""built.py OUT.jsonl: the advisor's built start of 14 knots and its controls.  BUILT-BINDING-20261126-001; README.md.

Three rings of four knots a_i, b_i, c_i, d_i (i = 1, 2, 3), each ring sharing one distinction between neighbours; b_i and
d_i hold two loose distinctions each; a_i shares t_i with a joining knot J and c_i shares u_i with a second joining knot
K; J holds t_1, t_2, t_3 and v, K holds u_1, u_2, u_3 and v.  31 distinctions.  The ring facts z_i are the parities of
each ring's four shared distinctions.  Variants: 'base'; 'no v' (J and K share nothing); 'J loose' (J holds one loose
distinction more).

On rounds 0 to 3 of ordinary growth under parity, under both readings of a small change (SHORT: every shortest allowed
change through each distinction; UPTO5: every allowed change of at most five distinctions), read:
    z_i        whether each ring fact is a class label (even on every move, not fixed by the laws) and read by no
               single knot; which tuples of their values occur on the allowed states (laws read as even: an odd
               constant moves the set of tuples, not its shape), by linear algebra and by a solver call per tuple
    B          the binding study's space (forced.read) and its frozen judge (every element split into
               distinction-disjoint cycles; a binding is a split into three or more cycles, each a label no single
               knot reads), under each reading
    classes    binding.read_stage: the number of class labels and of labels no single knot reads"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BINDING-20261126-001'))
import binding as BD, forced as FD, split as SP
classes, forbid, MC, T2 = BD.classes, BD.forbid, BD.MC, BD.T2
from pysat.solvers import Minisat22


def build(variant='base'):
    """the knots in the order a_1 b_1 c_1 d_1, a_2 ..., J, K; returns (supports, ring distinctions per ring)"""
    d = itertools.count()
    knots = [[] for _ in range(14)]
    J, K = 12, 13
    rings = []
    for i in range(3):
        a, b, c, e = 4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3
        ring = []
        for p, q in ((a, b), (b, c), (c, e), (e, a)):
            x = next(d); knots[p].append(x); knots[q].append(x); ring.append(x)
        rings.append(ring)
        for k in (b, e):
            for _ in range(2): knots[k].append(next(d))
        t = next(d); knots[a].append(t); knots[J].append(t)
        u = next(d); knots[c].append(u); knots[K].append(u)
    if variant != 'no v':
        v = next(d); knots[J].append(v); knots[K].append(v)
    if variant in ("J loose", "J two loose"):
        knots[J].append(next(d))
    if variant == 'J two loose':
        knots[J].append(next(d))
    return tuple(tuple(k) for k in knots), rings


def tuples_linear(st, cars):
    """which tuples of the carriers' values occur on the allowed states (even laws): an affine image"""
    names = sorted({x for r in st for x in r}); idx = {x: i for i, x in enumerate(names)}; n = len(names)
    rows = [sum(1 << idx[x] for x in r) for r in st]
    Z = classes.nullspace(rows, n)
    f = [sum(1 << idx[x] for x in c) for c in cars]
    gens = [tuple(bin(fi & z).count('1') % 2 for fi in f) for z in Z]   # the image of the space of solutions
    occ = {tuple(0 for _ in f)}
    for g in gens:
        occ |= {tuple((a + b) % 2 for a, b in zip(o, g)) for o in occ}
    return sorted(occ)


def tuples_solver(st, cars):
    names = sorted({x for r in st for x in r}); idx = {x: i + 1 for i, x in enumerate(names)}
    out = []
    for vals in itertools.product((0, 1), repeat=len(cars)):
        s = Minisat22(); top = [len(names)]
        def xor_eq(vs, val):
            acc = vs[0]
            for y in vs[1:]:
                top[0] += 1; z = top[0]
                s.add_clause([-z, acc, y]); s.add_clause([-z, -acc, -y]); s.add_clause([z, -acc, y]); s.add_clause([z, acc, -y])
                acc = z
            s.add_clause([acc] if val else [-acc])
        for r in st: xor_eq([idx[x] for x in r], 0)
        for c, val in zip(cars, vals): xor_eq([idx[x] for x in c], val)
        if s.solve(): out.append(vals)
        s.delete()
    return out


def facts(st, cars, moves, idx):
    """for each carrier: a class label? read by no single knot?"""
    n = len(idx); rows = [sum(1 << idx[x] for x in r) for r in st]
    Z = classes.nullspace(rows, n)
    local = []
    for r in st:
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        local.append([sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))])
    out = []
    for c in cars:
        f = sum(1 << idx[x] for x in c)
        label = all(bin(f & m).count('1') % 2 == 0 for m in moves) and any(bin(f & z).count('1') % 2 for z in Z)
        unread = not any(classes.rank(rows + loc + [f]) == classes.rank(rows + loc) for loc in local)
        out.append({'label': label, 'read by no single knot': unread})
    return out


def judge(st, moves, idx_moves):
    """the binding study's frozen judge (judge.judge_all) with the moves of either reading"""
    names, idx, holders, rows, Z, B, _, _ = SP.stage_data(st)
    assert idx == idx_moves
    if not B: return {'dim B': 0, 'bindings': []}
    local = []
    for r in st:
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        local.append([sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))])
    def label(f): return all(bin(f & m).count('1') % 2 == 0 for m in moves) and any(bin(f & z).count('1') % 2 for z in Z)
    def unread(f): return not any(classes.rank(rows + loc + [f]) == classes.rank(rows + loc) for loc in local)
    k = min(len(B), 10); found = []; parts_max = 0
    for c in range(1, 2 ** k):
        v = 0
        for j in range(k):
            if (c >> j) & 1: v ^= B[j]
        cyc = SP.cycles_in(v, names, holders); m = 0
        for P in SP.partitions(v, cyc):
            m += 1; parts_max = max(parts_max, len(P))
            if len(P) >= 3 and all(label(x) and unread(x) for x in P):
                found.append({'size': bin(v).count('1'), 'parts': len(P),
                              'parts as distinctions': [[names[i] for i in range(len(names)) if (x >> i) & 1] for x in P]})
                break
            if m > 5000: break
    return {'dim B': len(B), 'elements read': 2 ** k - 1, 'most cycles in a split': parts_max, 'bindings': found}


def read(st, cars, start_knots):
    names, idx, short = MC.moves_of(st)
    _, idx2, up = T2.moves_upto(st, 5)
    lin = tuples_linear(st, cars); sol = tuples_solver(st, cars)
    assert [tuple(x) for x in lin] == [tuple(x) for x in sol], (lin, sol)
    forced_sum = len(lin) == 2 ** (len(cars) - 1) and all(
        len({tuple(o[j] for j in range(len(cars)) if j != i) for o in lin}) == 2 ** (len(cars) - 1) for i in range(len(cars)))
    return {'tuples of the ring facts': len(lin), 'of': 2 ** len(cars),
            'one parity rule, every proper part free': forced_sum,
            'the rule': 'z1 + z2 + z3 = %d' % (sum(lin[0]) % 2) if forced_sum else None,
            'B': FD.read(st, start_knots),
            'SHORT': {'ring facts': facts(st, cars, short, idx), 'classes': BD.read_stage(st, short, idx),
                      'judge': judge(st, short, idx)},
            'UPTO5': {'ring facts': facts(st, cars, up, idx2), 'classes': BD.read_stage(st, up, idx2),
                      'judge': judge(st, up, idx2)}}


if __name__ == '__main__':
    out = sys.argv[1]; variants = sys.argv[2:] or ['base', 'no v', 'J loose']
    with open(out, 'w') as f:
        for var in variants:
            S, rings = build(var)
            rec = {'variant': var, 'knots': len(S), 'distinctions': len({x for r in S for x in r}), 'rounds': []}
            st = S
            for t in range(0, 4):
                if t:
                    nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
                    if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
                    st = nxt
                nd = len({x for r in st for x in r})
                if nd > 400: rec['rounds'].append({'round': t, 'end': 'not read: %d distinctions' % nd}); break
                r = read(st, rings, len(S)); r['round'] = t; r['distinctions'] = nd; rec['rounds'].append(r)
                print(var, t, nd, json.dumps({k: r[k] for k in ('tuples of the ring facts', 'one parity rule, every proper part free')}),
                      'B', r['B']['dim B'], 'SHORT', r['SHORT']['ring facts'], r['SHORT']['classes']['k'], len(r['SHORT']['judge']['bindings']),
                      'UPTO5', r['UPTO5']['ring facts'], r['UPTO5']['classes']['k'], len(r['UPTO5']['judge']['bindings']), flush=True)
            f.write(json.dumps(rec) + '\n'); f.flush()
