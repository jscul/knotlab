"""classes2.py: the advisor's checks on the class map (README.md, "Checks"). Under parity, for a structure:
    moves by bounded search (sets of up to MAX_W distinctions, so dimensions beyond full enumeration can be read):
        for each distinction, the shortest allowed changes through it (the motion study's choice), and as a second
        choice of move the shortest allowed changes overall (every allowed change of the least size)
    classes under each choice; dim (S0 + H)/H against dim S/H (S0: allowed changes with no loose distinction), the part
        of the class a value renaming keeping every loose value can change
    whether the class can be read inside one knot: some set of one knot's places whose parity is the same on every move
        but not on every allowed change
    after one round of growth (canonical engine), whether the old classes stay classes of the grown structure: the grown
        moves, projected on the old distinctions, lie in the old H

    classes2.py rings | census FILE     (census: the start indices listed in FILE, one JSON list)"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classes
forbid = classes.forbid
MAX_W = 6


def setup(supports, pin_loose):
    names = sorted({d for r in supports for d in r}); idx = {d: i for i, d in enumerate(names)}; n = len(names)
    held = forbid.holders(supports)
    loose = [idx[d] for d in names if len(held[d]) == 1]
    rows = [sum(1 << idx[d] for d in r) for r in supports]
    if pin_loose: rows += [1 << i for i in loose]
    return names, idx, n, held, loose, rows


def allowed(t, rows):
    return all(bin(t & r).count('1') % 2 == 0 for r in rows)


def short_moves(n, rows, through):
    """all allowed changes of least size through each distinction (through=True) or of least size overall: by full
    enumeration of S where its dimension is at most classes.MAX_DIM, otherwise by search up to MAX_W; returns (moves,
    distinctions with no allowed change found)"""
    B = classes.nullspace(rows, n)
    if len(B) <= classes.MAX_DIM:
        np = classes.np
        W = classes.span_words(B)[1:]; pc = classes.popcount(W); found = {}
        for i in range(n):
            m = (W >> np.uint64(i)) & np.uint64(1)
            if not m.any(): continue
            w = int(pc[m == 1].min()); found[i] = (w, [int(v) for v in W[(m == 1) & (pc == w)]])
        missing = [i for i in range(n) if i not in found]
        if through: return {t for w, h in found.values() for t in h}, missing
        least = min((w for w, h in found.values()), default=None)
        return {t for w, h in found.values() if w == least for t in h}, missing
    found, missing = {}, []
    for d in range(n):
        for w in range(1, MAX_W + 1):
            hits = [t for rest in itertools.combinations([e for e in range(n) if e != d], w - 1)
                    for t in [(1 << d) | sum(1 << e for e in rest)] if allowed(t, rows)]
            if hits: found[d] = (w, hits); break
        else: missing.append(d)
    if through: return {t for w, h in found.values() for t in h}, missing
    least = min((w for w, h in found.values()), default=None)
    return {t for w, h in found.values() if w == least for t in h}, missing


def analyse(supports, pin_loose=False):
    names, idx, n, held, loose, rows = setup(supports, pin_loose)
    B = classes.nullspace(rows, n); dS = len(B)
    out = {'distinctions': n, 'dim S': dS}
    for label, through in (('shortest through each distinction', True), ('shortest overall', False)):
        M, missing = short_moves(n, rows, through)
        dH = classes.rank(list(M))
        lmask = sum(1 << i for i in loose)
        # S0 = allowed changes with zero loose part: a basis from the nullspace with loose pinned
        S0 = classes.nullspace(rows + [1 << i for i in loose], n)
        dS0H = classes.rank(list(M) + S0) - dH
        rec = {'dim H': dH, 'classes': 2 ** (dS - dH), 'dim (S0+H)/H': dS0H, 'dim S/H': dS - dH,
               'distinctions with no short change': len(missing)}
        if through:
            # readable inside one knot: a subset of a knot's places with even parity on every move, odd on some allowed change
            Hperp_ok = lambda z: all(bin(z & t).count('1') % 2 == 0 for t in M)
            Sperp = lambda z: all(bin(z & b).count('1') % 2 == 0 for b in B)
            one = False
            for r in rows[:len(supports)]:
                bits = [i for i in range(n) if (r >> i) & 1]
                for k in range(1, len(bits) + 1):
                    for sub in itertools.combinations(bits, k):
                        z = sum(1 << i for i in sub)
                        if Hperp_ok(z) and not Sperp(z): one = True; break
                    if one: break
                if one: break
            rec['the class read inside one knot'] = one
            rec['_moves'] = M
        out[label] = rec
    return out, names


def survives(supports):
    """after one round: do the grown moves (shortest through each distinction), projected on the old distinctions, lie in
    the old H?"""
    old, onames = analyse(supports)
    st, status, births = forbid.grown(supports, 'parity', 'ordinary')
    if status != 'funded': return old, None
    new, gnames = analyse(st)
    Hold = old['shortest through each distinction']['_moves']
    gidx = {d: k for k, d in enumerate(gnames)}
    proj = []
    for t in new['shortest through each distinction']['_moves']:
        p = 0
        for k, d in enumerate(onames):
            if (t >> gidx[d]) & 1: p |= 1 << k
        proj.append(p)
    keep = classes.rank(list(Hold) + proj) == classes.rank(list(Hold))
    return old, (new, keep)


def clean(a):
    return {k: ({kk: vv for kk, vv in v.items() if kk != '_moves'} if isinstance(v, dict) else v) for k, v in a.items()}


def read(name, supports):
    old, grown = survives(supports)
    out = {'structure': name, 'start': clean(old)}
    if grown is None: out['after one round'] = 'no round'
    else: out['after one round'] = clean(grown[0]); out['old classes kept by the grown moves'] = grown[1]
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'rings':
        for n in range(3, 13):
            print(json.dumps(read('ring n=%d loose=2' % n, classes.ring(n, 2))), flush=True)
    else:
        S = forbid.census()
        for i in json.load(open(sys.argv[2])):
            print(json.dumps(read('census %d' % i, forbid.supports_of(S[i]))), flush=True)
