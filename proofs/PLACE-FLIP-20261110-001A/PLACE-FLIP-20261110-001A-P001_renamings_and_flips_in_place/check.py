"""Checks for PLACE-FLIP-20261110-001A: renamings, transplants and flips in place.

1. Dust witnesses (L1). For each of the 84 dust witnesses of ticket B's census and the six found by hand (witnesses.json), a minimal
   change of values flipping each endpoint is found again by brute force over the board's allowed colourings, and its colouring is
   checked to be non-isomorphic to the old one as a coloured graph (networkx), independently of the census's automorphism code.
2. The switch (L3) on every witness: allowed, minimal, and joining two copies into one component.
3. A transplant (L4) in the first law with no mixed edge: a place of value 0 moved into an all-1 component by a finite rewiring.
4. Cascades and the fixed points (L5, L6). The type-level fixed point over T for all 90 laws, with no flippable value for the 31 laws
   with no mixed edge and law 48; the edge-level fixed point in the covers of the frozen boards' colourings (at most 200 per law),
   agreeing with every flip ticket B found within distance 2; and the joint fixed point (two changes on one tree), which finds
   exactly the laws the frozen covers find.

Usage: check.py
"""
import importlib.util
import itertools
import json
import os
import time
from collections import Counter

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLUG_B = 'PLACE-FLIP-20261110-001B-E001_flips_in_place'
FLIPS_PY = os.path.join(ROOT, 'experiments', 'PLACE-FLIP-20261110-001B', SLUG_B, 'flips.py')
FLIPS_JSON = os.path.join(ROOT, 'artifacts', 'PLACE-FLIP-20261110-001B', SLUG_B, 'flips.json')
KNOTS_JSON = os.path.join(ROOT, 'artifacts', 'BARE-NAMES-20261110-001B', 'BARE-NAMES-20261110-001B-E001_board_value_knots',
                          'knots.json')
OUT = os.path.join(HERE, 'result.json')

_spec = importlib.util.spec_from_file_location('flips', FLIPS_PY)
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)
kn = fl.kn


def coloured(adj, c):
    G = nx.Graph([(v, w) for v, nb in enumerate(adj) for w in nb])
    nx.set_node_attributes(G, {v: (c >> v) & 1 for v in range(len(adj))}, 'c')
    return G


def flips_independently(adj, c, x, S):
    """A minimal change of values flipping x whose colouring is not isomorphic to c, found by brute force; its size or None."""
    allowed = fl.allowed_colourings(adj, S)
    ds = sorted((c ^ a for a in allowed if ((c ^ a) >> x) & 1), key=lambda d: bin(d).count('1'))
    mins = []
    G0 = coloured(adj, c)
    for d in ds:
        if any(e & d == e for e in mins):
            continue
        mins.append(d)
        if not nx.is_isomorphic(G0, coloured(adj, c ^ d), node_match=lambda a, b: a['c'] == b['c']):
            return bin(d).count('1')
    return None


def cover_flips(adj, col, T):
    """L6, part 1: for each place u of B, whether s(u) flips by a finite change of values in the universal cover of (B, col)."""
    T = set(map(tuple, T))
    oe = [(p, x) for p in range(len(adj)) for x in adj[p]]
    G = {(p, x, 0, 0) for (p, x) in oe}
    changed = True
    while changed:
        changed = False
        for (p, x) in oe:
            kids = [y for y in adj[x] if y != p]
            for fp in (0, 1):
                for fx in (0, 1):
                    if (p, x, fp, fx) in G:
                        continue
                    opts = [[fy for fy in (0, 1) if (x, y, fx, fy) in G] for y in kids]
                    if any(not o for o in opts):
                        continue
                    for choice in itertools.product(*opts):
                        k = (col[p] ^ fp) + sum(col[y] ^ fy for y, fy in zip(kids, choice))
                        if (col[x] ^ fx, k) in T:
                            G.add((p, x, fp, fx))
                            changed = True
                            break
    res = []
    for u in range(len(adj)):
        opts = [[fy for fy in (0, 1) if (u, y, 1, fy) in G] for y in adj[u]]
        res.append(bool(all(opts)) and any((1 - col[u], sum(col[y] ^ fy for y, fy in zip(adj[u], ch))) in T
                                           for ch in itertools.product(*opts)))
    return res


def type_level(T):
    """L6, part 2: the values a for which some tree world lets a place of value a flip by a finite change of values."""
    T = set(map(tuple, T))
    acc = lambda k, c: k >= 1 if c == 1 else k <= 3
    states = [(cp, fp, cx, kx, fx) for cp in (0, 1) for fp in (0, 1) for (cx, kx) in T for fx in (0, 1) if acc(kx, cp)]
    G = {s for s in states if s[1] == 0 and s[4] == 0}

    def sums_for(cx, fx, n1, n0, src):
        ach = {b: sorted({b ^ fy for (cy, ky) in T if cy == b and acc(ky, cx) for fy in (0, 1) if src(cx, fx, b, ky, fy)})
               for b in (0, 1)}
        if (n1 and not ach[1]) or (n0 and not ach[0]):
            return set()
        sums = {0}
        for b, cnt in ((1, n1), (0, n0)):
            for _ in range(cnt):
                sums = {s0 + v for s0 in sums for v in ach[b]}
        return sums

    changed = True
    while changed:
        changed = False
        for s in states:
            if s in G:
                continue
            cp, fp, cx, kx, fx = s
            n1 = kx - cp
            if not 0 <= n1 <= 3:
                continue
            sums = sums_for(cx, fx, n1, 3 - n1, lambda *t: t in G)
            if any((cx ^ fx, (cp ^ fp) + s0) in T for s0 in sums):
                G.add(s)
                changed = True
    flippable = set()
    for (cu, ku) in T:
        sums = sums_for(cu, 1, ku, 4 - ku, lambda *t: t in G)
        if any((1 - cu, s0) in T for s0 in sums):
            flippable.add(cu)
    return sorted(flippable)


def joint_edge(T):
    """L6, part 3: is there a tree world with an edge {u, v} such that one finite change of values flips u and another flips v,
    both on the same old tree? A fixed point over child slots carrying both changes at once."""
    T = set(map(tuple, T))
    acc = lambda k, c: k >= 1 if c == 1 else k <= 3
    types = sorted(T)
    # child-slot state: (c_parent, (c_x,k_x), f_p, f_x, h_p, h_x)
    states = [(cp, t, fp, fx, hp, hx) for cp in (0, 1) for t in types if acc(t[1], cp)
              for fp in (0, 1) for fx in (0, 1) for hp in (0, 1) for hx in (0, 1)]
    G = {s for s in states if s[2] == s[3] == s[4] == s[5] == 0}

    def slot_options(cx, fx, hx):
        """For a child of x (x's old value cx, flips fx under F and hx under H): achievable (old, F-new, H-new) values."""
        opts = set()
        for (cy, ky) in types:
            if not acc(ky, cx):
                continue
            for fy in (0, 1):
                for hy in (0, 1):
                    if (cx, (cy, ky), fx, fy, hx, hy) in G:
                        opts.add((cy, cy ^ fy, cy ^ hy))
        return opts

    def sums(slots):
        out = {(0, 0, 0)}
        for opts in slots:
            out = {(a + o, b + f, c + h) for (a, b, c) in out for (o, f, h) in opts}
        return out

    changed = True
    while changed:
        changed = False
        for s in states:
            if s in G:
                continue
            cp, (cx, kx), fp, fx, hp, hx = s
            opts = slot_options(cx, fx, hx)
            if not opts:
                continue
            for (so, sf, sh) in sums([opts] * 3):
                if cp + so != kx:
                    continue
                if (cx ^ fx, (cp ^ fp) + sf) in T and (cx ^ hx, (cp ^ hp) + sh) in T:
                    G.add(s)
                    changed = True
                    break
    # the root edge u-v: change F flips u, change H flips v
    for (cu, ku) in types:
        for (cv, kv) in types:
            if not (acc(ku, cv) and acc(kv, cu)):
                continue
            for fv in (0, 1):
                for hu in (0, 1):
                    ou = slot_options(cu, 1, hu)
                    ov = slot_options(cv, fv, 1)
                    if not ou or not ov:
                        continue
                    su = sums([ou] * 3)
                    sv = sums([ov] * 3)
                    for (ao, af, ah) in su:
                        if cv + ao != ku:
                            continue
                        # u's star: under F (u flipped, v's F-flip fv), under H (u's H-flip hu, v flipped)
                        if (1 - cu, (cv ^ fv) + af) not in T or (cu ^ hu, (1 - cv) + ah) not in T:
                            continue
                        for (bo, bf, bh) in sv:
                            if cu + bo != kv:
                                continue
                            if (cv ^ fv, (1 - cu) + bf) in T and (1 - cv, (cu ^ hu) + bh) in T:
                                return True
    return False


def transplant_demo():
    """L4 in the first law with no mixed edge: u (value 0) leaves an all-0 copy of B0 and joins an all-1 copy of B1."""
    cen = json.load(open(KNOTS_JSON))
    m = min(int(k) for k, r in cen['laws'].items() if r.get('shape') == fl.NO_MIXED)
    S = kn.law(m)
    boards = fl.frozen_boards()
    B0 = next(adj for _, adj in boards if 0 in fl.allowed_colourings(adj, S))
    B1 = next(adj for _, adj in boards if (1 << len(adj)) - 1 in fl.allowed_colourings(adj, S))
    n0, n1 = len(B0), len(B1)
    adj = [set(nb) for nb in B0] + [set(w + n0 for w in nb) for nb in B1]
    col = [0] * n0 + [1] * n1
    assert kn.allowed_state([sorted(nb) for nb in adj], col, S)
    u = 0
    a, b, c, d = sorted(adj[u])
    new = [set(nb) for nb in adj]
    for y in (a, b, c, d):
        new[y].discard(u)
    new[u] = set()
    pairs = [(a, b), (c, d)] if b not in new[a] and d not in new[c] else [(a, c), (b, d)]
    for (p, q) in pairs:
        new[p].add(q)
        new[q].add(p)
    e1 = (n0, sorted(adj[n0])[0])
    e2 = next((x, y) for x in range(n0, n0 + n1) for y in sorted(adj[x]) if x not in e1 and y not in e1 and x < y)
    for (x, y) in (e1, e2):
        new[x].discard(y)
        new[y].discard(x)
        new[x].add(u)
        new[y].add(u)
        new[u] |= {x, y}
    col2 = list(col)
    col2[u] = 1
    ok = kn.allowed_state([sorted(nb) for nb in new], col2, S)
    sizes = lambda g: sorted(len(cc) for cc in nx.connected_components(nx.Graph([(v, w) for v, nb in enumerate(g) for w in nb])))
    return {'law': m, 'allowed': bool(ok), 'value_flipped': col2[u] != col[u],
            'component_sizes_before': sizes(adj), 'component_sizes_after': sizes(new),
            'pass': bool(ok and sizes(adj) != sizes(new))}


def main():
    t0 = time.time()
    pf = json.load(open(FLIPS_JSON))
    cen = json.load(open(KNOTS_JSON))
    boards = {name: adj for name, adj in fl.frozen_boards()}
    wit = json.load(open(os.path.join(HERE, 'witnesses.json')))['laws']
    res = {}
    # 1 and 2: dust witnesses
    rows, ok_all = [], True
    for r in pf['laws']:
        m = r['law']
        S = kn.law(m)
        d = r['dust']
        if d.get('native_in_place') and 'board' in d:
            adj, c, (u, v) = boards[d['board']], d['colouring'], d['edge']
        elif str(m) in wit:
            w = wit[str(m)]
            adj, c, (u, v) = w['adj'], w['colouring'], w['edge']
        elif d.get('native_in_place'):
            adj, c, (u, v) = boards[d['boards'][0]], 0, d['edge']
        else:
            rows.append([m, 'no witness'])
            ok_all = False
            continue
        n = len(adj)
        assert kn.allowed_state(adj, [(c >> x) & 1 for x in range(n)], S), m
        fu, fv = flips_independently(adj, c, u, S), flips_independently(adj, c, v, S)
        sw = fl.switch_check(adj, [(c >> x) & 1 for x in range(n)], S, u, v)
        good = bool(fu and fv and sw)
        ok_all = ok_all and good
        rows.append([m, good, fu, fv])
    res['1_2_dust_witnesses'] = {'laws': len(rows), 'all_native_in_place': ok_all,
                                 'by_hand': sorted(int(k) for k in wit), 'pass': ok_all and len(rows) == 90}
    print('dust', ok_all, round(time.time() - t0, 1), flush=True)
    # 3: transplant
    res['3_transplant'] = transplant_demo()
    # 4: fixed points
    tl_counts, tl_rigid = Counter(), []
    exact, consistent, joint = {}, True, {}
    fboards = fl.frozen_boards()
    census_tree = {r['law']: r['tree'] for r in pf['laws']}
    for m, r in sorted(((int(m), r) for m, r in cen['laws'].items() if r.get('is_knot'))):
        T = [tuple(t) for t in r['types']]
        tl = type_level(T)
        tl_counts[str(tl)] += 1
        joint[m] = joint_edge(T) if tl else False
        if not tl:
            tl_rigid.append(m)
        found = False
        if r['shape'] != fl.NO_MIXED and tl:
            worlds = 0
            for i, name, adj, allowed, c in fl.two_valued(fboards, kn.law(m), 60):
                worlds += 1
                col = [(c >> w) & 1 for w in range(len(adj))]
                fx = cover_flips(adj, col, T)
                if any(fx[u] and fx[v] for u in range(len(adj)) for v in adj[u]):
                    found = True
                    break
                if worlds >= 200:
                    break
        exact[m] = found
        ct = census_tree[m]
        if ct.get('native_in_place'):
            adj = boards[ct['board']]
            col = [(ct['colouring'] >> w) & 1 for w in range(len(adj))]
            fx = cover_flips(adj, col, T)
            if not (fx[ct['edge'][0]] and fx[ct['edge'][1]]):
                consistent = False
    no_mixed = [r['law'] for r in pf['laws'] if r['shape'] == fl.NO_MIXED]
    cascade_ok = all(m in tl_rigid for m in no_mixed + [48])
    res['4_fixed_points'] = {
        'type_level_flippable_values': dict(tl_counts), 'rigid_in_every_tree_world': len(tl_rigid),
        'rigid_laws': tl_rigid, 'cascade_laws_rigid': cascade_ok,
        'native_in_place_in_a_frozen_tree_world_exact': sorted(m for m, f in exact.items() if f),
        'census_within_distance_2': sorted(m for m, t in census_tree.items() if t.get('native_in_place')),
        'census_flips_confirmed': consistent,
        'native_in_place_in_some_tree_world_joint': sorted(m for m, f in joint.items() if f),
        'values_flip_but_never_both_ends': sorted(m for m, f in joint.items() if not f and m not in tl_rigid),
        'joint_agrees_with_frozen_covers': sorted(m for m, f in joint.items() if f) == sorted(m for m, f in exact.items() if f),
        'pass': bool(cascade_ok and consistent and sorted(m for m, f in joint.items() if f) == sorted(m for m, f in exact.items() if f))}
    res['pass'] = all(v['pass'] for v in res.values() if isinstance(v, dict))
    res['status'] = 'passed' if res['pass'] else 'failed'
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
    print(json.dumps({k: (v['pass'] if isinstance(v, dict) else v) for k, v in res.items()}))


if __name__ == '__main__':
    main()
