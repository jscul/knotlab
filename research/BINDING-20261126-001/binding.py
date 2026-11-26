"""binding.py OUT.jsonl: whether growth binds the facts no single knot reads.  BINDING-20261126-001 (a check by the
thread, not registered); README.md.

On each witness start (the layers referee's constructions with two, three and four such facts, its sampled ten-knot
start, and the seven-knot held-out start 7-239), rounds 1 to 4 of ordinary growth under parity, and two readings of a
small change (SHORT: every shortest allowed change through each distinction; UPTO5: every allowed change of at most five
distinctions), read:
    k            the dimension of the class labels (the facts the moves keep)
    joint rank   the dimension of the values a basis of labels takes together over the allowed states
    individually unread   the nonzero labels that no single knot's distinctions represent
    jointly unread        k less the dimension single knots' reads span
    rules        every rule the label values obey: for a basis f1..fk, the affine relations among them over the allowed
                 states (none when the joint rank is k), and for every triple of nonzero labels whether the relation on
                 their three values passes K1 to K3 (checked by the knot checker), and whether its third is the sum of
                 the first two as a label."""
import sys, os, json, itertools, collections, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'RECURSION-LEAD-20261126-001'))
sys.path.insert(0, str(ROOT / 'research' / 'LAYERS-20261126-001'))
import tower2 as T2
import multi_class as MC
LY = T2.LY; classes, forbid = LY.classes, LY.forbid
REF = ROOT / 'research/LAYERS-20261126-001/referee-R1'


def from_meetings(meetings, loose):
    knots = [[] for _ in loose]; d = 0
    for a, b in meetings: knots[a].append(d); knots[b].append(d); d += 1
    for k, l in enumerate(loose):
        for _ in range(l): knots[k].append(d); d += 1
    return tuple(tuple(k) for k in knots)


def witnesses():
    b = json.load(open(REF / 'built_search.json'))
    for i in (0, 17, 20):
        yield 'referee built %d (%d knots)' % (i, len(b[i]['source'])), tuple(tuple(k) for k in b[i]['source'])
    e = json.load(open(REF / 'extended_witness.json'))
    yield 'referee sampled %s' % e[0]['sample index'], tuple(tuple(k) for k in e[0]['start supports'])
    yield 'held out 7-239', forbid.supports_of(forbid.sampled(7, 300, 20261206 + 7)[239])


def labels_of(supports, moves, idx):
    """a basis of the class labels (functionals even on every move, modulo the knots' laws) and each knot's local span"""
    n = len(idx); rows = [sum(1 << idx[x] for x in r) for r in supports]
    Hperp = classes.nullspace(moves, n)
    basis = []; R = list(rows)
    for f in Hperp:
        if classes.rank(R + [f]) > classes.rank(R): R.append(f); basis.append(f)
    local = []
    for r in supports:
        ks = [idx[x] for x in r]
        mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
        local.append([sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))])
    return rows, basis, local


def read_stage(supports, moves, idx):
    n = len(idx); rows, basis, local = labels_of(supports, moves, idx); k = len(basis)
    Z = classes.nullspace(rows, n)
    M = [sum(((bin(f & z).count('1') % 2) << j) for j, z in enumerate(Z)) for f in basis]
    rR = classes.rank(rows)
    def readable_by_one(f):
        return any(classes.rank(rows + loc + [f]) == classes.rank(rows + loc) for loc in local)
    nonzero = []
    for c in range(1, 2 ** k):
        f = 0
        for j in range(k):
            if (c >> j) & 1: f ^= basis[j]
        nonzero.append((c, f))
    unread = [c for c, f in nonzero if not readable_by_one(f)]
    span = classes.rank(rows + [v for loc in local for v in loc]) - rR
    triples = collections.Counter()
    for (a, fa), (b, fb), (c, fc) in itertools.combinations(nonzero, 3):
        if a in unread and b in unread and c in unread:
            triples['three unread labels, the third the sum of two' if a ^ b == c else 'three unread labels, independent'] += 1
    return {'k': k, 'joint rank': classes.rank(M), 'individually unread': len(unread),
            'jointly unread': k - span_overlap(rows, basis, local),
            'triples of unread labels': dict(triples)}


def span_overlap(rows, basis, local):
    """the dimension of the labels that single knots' reads span"""
    rR = classes.rank(rows); allloc = [v for loc in local for v in loc]
    return classes.rank(rows + allloc) + classes.rank(rows + basis) - classes.rank(rows + allloc + basis) - rR


def check_parity_knot():
    """the knot checker on the relation of three labels that obey a + b + c = 0: K1 to K3"""
    cnf = 'a b ~c; a ~b c; ~a b c; ~a ~b ~c'
    out = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--loops', 'a', 'b', '--contact', 'c', '--json'],
                         capture_output=True, text=True, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'tools')))
    return out.stdout.strip()[:400]


if __name__ == '__main__':
    out = sys.argv[1]
    with open(out, 'w') as f:
        f.write(json.dumps({'knot checker on a + b + c = 0 over three label values': check_parity_knot()}) + '\n')
        for name, S in witnesses():
            rec = {'start': name, 'knots': len(S), 'rounds': []}
            st = S
            for t in range(0, 5):
                if t:
                    nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
                    if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
                    st = nxt
                nd = len({x for r in st for x in r})
                if nd > 400: rec['rounds'].append({'round': t, 'end': 'not read: %d distinctions' % nd}); break
                names, idx, short = MC.moves_of(st)
                _, idx2, up = T2.moves_upto(st, 5)
                rec['rounds'].append({'round': t, 'SHORT': read_stage(st, short, idx), 'UPTO5': read_stage(st, up, idx2)})
            f.write(json.dumps(rec) + '\n'); f.flush(); print(json.dumps(rec)[:600], flush=True)
