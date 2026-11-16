"""Referee R1 (MARK-RATE-20261116-001), item 1: Lemma S's closure, empirically, with richer markings than the study's gate.

For ~30 small-orbit census descriptions with r0 = 0, at depth N (default 9): random orbits O (levels 1..6) and random markings of
1..8 marks spread over several levels (on O itself, its parent level, nearby levels, deep below, anywhere allowed). The actual
signatures are computed by MY SAT oracle on MY explicit P_N (knots with their placing address, my builder):
  up     marks outside O's proper subtree (O itself allowed), knots placed outside O's subtree;   must lie in marks.U[t]
  below  marks strictly below O, knots placed at O or below;                                        must lie in marks.below(t)
  down   marks in O's subtree with O itself, knots placed at O or below;                            must lie in marks.D[t]
(each when nonempty). The cuts of Theorem M's test are checked too: with no marks, every full state's value on O lies in the
step's image of marks.Ufree (ran), its value on O's parent orbit lies in dom (extends through the step to a feasible child), and
the unmarked up signature lies in Ufree. Families, Ufree and the step come from marks.py (CALLED AS THE THING UNDER TEST); its types
and children are first checked identical to my own block DP's, so element orders agree.
Usage: referee_signatures.py OUT.json N per_description first:last"""
import gzip
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
from pysat.solvers import Cadical195

ROOT = Path('/home/jscul/p-vs-np-contact-first')
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/referee-R1'))
sys.path.insert(0, str(ROOT / 'research/BLOCK-REACH-20261116-001/referee-R1'))
from referee_pattern import Aut, hid  # noqa: E402  (mine)
from referee_blocks import Blocks  # noqa: E402  (mine)
from referee_window_sat import placed_knots  # noqa: E402  (mine)

sys.path.insert(0, str(ROOT / 'research/MARK-RATE-20261116-001'))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from marks import Marks  # noqa: E402  (under test)
from window_tree import WindowTree  # noqa: E402  (under test, input of Marks)

CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'


def lvl(h):
    return (h + 1).bit_length() - 1


def addr(h):
    n = lvl(h)
    return h - (1 << n) + 1, n


def projection(knots, orbit_h, marks):
    """Assignments of the orbit (bit i = orbit_h[i]) consistent with the knots (heap-id rows) and marks {heap id: value}."""
    vid = {}
    for h in list(orbit_h) + list(marks):
        vid.setdefault(h, len(vid) + 1)
    cls = []
    for row in knots:
        lits = [vid.setdefault(int(h), len(vid) + 1) for h in row]
        cls.append(lits)
        cls.append([-l for l in lits])
    pin = [vid[h] if b else -vid[h] for h, b in marks.items()]
    out = set()
    with Cadical195(bootstrap_with=cls) as S:
        for p in range(1 << len(orbit_h)):
            if S.solve(assumptions=pin + [vid[h] if (p >> i) & 1 else -vid[h] for i, h in enumerate(orbit_h)]):
                out.add(p)
    return frozenset(out)


def main():
    out_path, N, per = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    a, b = (int(x) for x in sys.argv[4].split(':'))
    rows = json.load(open(ROOT / 'research/MARK-RATE-20261116-001/census_marks.json'))['rows']
    keys = {}
    for line in gzip.open(CENSUS, 'rt'):
        r = json.loads(line)
        if r['case'] in rows:
            keys[r['case']] = r['key']
    rng = random.Random(9090 + N)
    want = [('cyclic r=2 pass', 10, lambda v: v['name'] == 'ruler' and v['cyclic'] and v['r'] == 2 and v['no_skip'] is True),
            ('cyclic r=2 fail', 6, lambda v: v['name'] == 'ruler' and v['cyclic'] and v['r'] == 2 and v['no_skip'] is False),
            ('cyclic r=3 fail', 3, lambda v: v['name'] == 'ruler' and v['cyclic'] and v['r'] == 3 and v['no_skip'] is False),
            ('acyclic r=1 pass', 4, lambda v: v['name'] == 'ruler' and not v['cyclic'] and v['r'] == 1 and v['no_skip'] is True),
            ('acyclic r=2 fail', 3, lambda v: v['name'] == 'ruler' and not v['cyclic'] and v['r'] == 2 and v['no_skip'] is False),
            ('half-rate fail', 4, lambda v: v['name'] == 'half-rate' and v['no_skip'] is False)]
    pick = []
    for nm, k, f in want:
        cs = sorted(c for c, v in rows.items() if f(v) and v['seconds'] <= 20)
        pick += [(nm, c) for c in rng.sample(cs, min(k, len(cs)))]
    pick = pick[a:b]
    res, missing, cutbad = {}, [], []
    tally = dict(up=0, below=0, down=0, empty=0, cut_checks=0, marks_hist={}, proper={'up': 0, 'below': 0, 'down': 0},
                 distinct={'up': set(), 'below': set(), 'down': set()})
    t0 = time.time()
    for nm, cid in pick:
        key = keys[cid]
        tree = WindowTree(key)
        mk = Marks(tree)
        B = Blocks(key)
        enc = lambda T: tuple(tuple((i, tuple(sec)) for i, sec in row) for row in T)
        assert [enc(T) for T in tree.types] == [enc(T) for T in B.types]
        assert [[(c, list(p)) for c, p in ch] for ch in tree.children] == [[(c, list(p)) for c, p in ch] for ch in B.kids]
        A = Aut(key)
        KV = [placed_knots(A, n, N) for n in range(N + 1)]
        # explicit orbits per level: (type, addresses in element order, parent index, child index)
        levels = [[(0, [0], None, None)]]
        for n in range(N):
            nxt = []
            for pi, (t, ad, _, _) in enumerate(levels[n]):
                for ci, (c, pos) in enumerate(B.kids[t]):
                    nxt.append((c, [2 * ad[p // 2] + p % 2 for p in pos], pi, ci))
            levels.append(nxt)
        below_cache = {}
        nmarks = []
        for w in range(per):
            ell = rng.randint(1, 6)
            oi = rng.randrange(len(levels[ell]))
            t, O, pi, ci = levels[ell][oi]
            Oset = set(O)
            Oh = [hid(x, ell) for x in O]

            def under(h, strict):
                y, n = addr(h)
                if n < ell or (strict and n == ell):
                    return False
                return (y >> (n - ell)) in Oset
            K_out = np.concatenate([K[~np.isin(V >> (n - ell), O)] if n >= ell else K for n, (K, V) in enumerate(KV)])
            K_in = np.concatenate([K[np.isin(V >> (n - ell), O)] for n, (K, V) in enumerate(KV) if n >= ell])
            K_all = np.concatenate([K for K, _ in KV])
            nv = (1 << (N + 1)) - 1

            def pick_marks(pools, weights, k):
                m = {}
                for _ in range(k):
                    pool = rng.choices(pools, weights)[0]
                    if pool:
                        m[rng.choice(pool)] = rng.getrandbits(1)
                return m
            # up marks
            own = list(Oh)
            par = [hid(x, ell - 1) for x in levels[ell - 1][pi][1]]
            near = [h for h in range((1 << max(0, ell - 2)) - 1, (1 << (min(N, ell + 3) + 1)) - 1) if not under(h, True)]
            anyw = [h for h in range(nv) if not under(h, True)]
            mu = pick_marks([own, par, near, anyw], [0.25, 0.2, 0.35, 0.2], rng.randint(1, 8))
            X = projection(K_out.tolist(), Oh, mu)
            tally['up'] += 1
            if X and len(X) < (1 << len(Oh)):
                tally['proper']['up'] += 1
            tally['distinct']['up'].add((cid, t, X))
            nmarks.append(len(mu))
            if not X:
                tally['empty'] += 1
            elif X not in mk.U[t]:
                missing.append(dict(kind='up', case=cid, level=ell, orbit=Oh, marks=mu, sig=sorted(X)))
            # below marks: strictly under O
            ch1 = [h for h in range((1 << (ell + 1)) - 1, (1 << (ell + 2)) - 1) if under(h, True)]
            ch2 = [h for h in range((1 << (ell + 2)) - 1, (1 << (ell + 3)) - 1) if ell + 2 <= N and under(h, True)]
            deep = [h for h in range((1 << (ell + 3)) - 1, nv) if under(h, True)]
            mb = pick_marks([ch1, ch2, deep], [0.4, 0.35, 0.25], rng.randint(1, 8))
            Y = projection(K_in.tolist(), Oh, mb)
            if t not in below_cache:
                below_cache[t] = mk.below(t)
            tally['below'] += 1
            if Y and len(Y) < (1 << len(Oh)):
                tally['proper']['below'] += 1
            tally['distinct']['below'].add((cid, t, Y))
            nmarks.append(len(mb))
            if not Y:
                tally['empty'] += 1
            elif Y not in below_cache[t]:
                missing.append(dict(kind='below', case=cid, level=ell, orbit=Oh, marks=mb, sig=sorted(Y)))
            # down marks: below marks plus pins on O
            md = dict(mb)
            for h in rng.sample(Oh, rng.randint(1, len(Oh))):
                md[h] = rng.getrandbits(1)
            Z = projection(K_in.tolist(), Oh, md)
            tally['down'] += 1
            if Z and len(Z) < (1 << len(Oh)):
                tally['proper']['down'] += 1
            tally['distinct']['down'].add((cid, t, Z))
            if not Z:
                tally['empty'] += 1
            elif Z not in mk.D[t]:
                missing.append(dict(kind='down', case=cid, level=ell, orbit=Oh, marks=md, sig=sorted(Z)))
            # cuts, no marks
            tp, P, _, _ = levels[ell - 1][pi]
            Ph = [hid(x, ell - 1) for x in P]
            c, T = mk.step(tp, ci)
            assert c == t
            dom = {x for x, y in T if y in mk.Fc[c]}
            ran = {y for x, y in T if x in mk.Ufree[tp]}
            fullO = projection(K_all.tolist(), Oh, {})
            fullP = projection(K_all.tolist(), Ph, {})
            upfree = projection(K_out.tolist(), Oh, {})
            tally['cut_checks'] += 1
            if not (fullO <= ran and fullP <= dom and upfree <= set(mk.Ufree[t]) and upfree in mk.U[t]):
                cutbad.append(dict(case=cid, level=ell, orbit=Oh, fullO=sorted(fullO), ran=sorted(ran), fullP=sorted(fullP),
                                   dom=sorted(dom), upfree=sorted(upfree), Ufree=sorted(mk.Ufree[t])))
        for k_ in nmarks:
            tally['marks_hist'][k_] = tally['marks_hist'].get(k_, 0) + 1
        res[cid] = dict(cls=nm, types=len(tree.types), U_family_sizes=[len(u) for u in mk.U])
        print(cid[:12], nm, 'checked', tally['up'], tally['below'], tally['down'], 'empty', tally['empty'], 'missing', len(missing),
              'cut problems', len(cutbad), '%.0fs' % (time.time() - t0), flush=True)
        json.dump(dict(N=N, tally=dict(tally, distinct={k: len(v) for k, v in tally['distinct'].items()}), missing=missing, cut_problems=cutbad, cases=res, seconds=time.time() - t0),
                  open(out_path, 'w'), indent=0)
    print('done', len(res), dict(tally, distinct={k: len(v) for k, v in tally['distinct'].items()}), 'missing', len(missing), 'cut problems', len(cutbad))


if __name__ == '__main__':
    main()
