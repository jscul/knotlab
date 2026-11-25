"""The readings of BD2 4 to 6 on one item (a law, a start, a knot law): pairs of parts wholly apart after rounds s,
descent, the meeting round, the linking set, the strict and ancestral readings, the bars on Y, the course from X only,
the values used at X's births and attribution (ticket A's `wbc.first_difference`, imported unchanged), m, how many,
which at equal number, lasting, the four checks, the knot test as registered.  Readings: deviations.md (B n)."""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import hashlib
import itertools
import time
from collections import Counter, defaultdict

import networkx as nx
from networkx.algorithms import isomorphism as iso

import eng
import knots
import wbc

DESC = {(True, False): 'X only', (False, True): 'Y only', (True, True): 'both', (False, False): 'neither'}


def hkey(*parts):
    return hashlib.blake2b(repr(parts).encode(), digest_size=8).hexdigest()


def bitlist(B):
    out = []
    i = 0
    while B:
        if B & 1:
            out.append(i)
        B >>= 1
        i += 1
    return out


# ------------------------------------------------------------------------------------------------- answers (RD 3.2)
class Keys:
    """Answer keys of a run's knots and distinctions: start knots by order, start distinctions by name, a birth by
    (round, kind, parents' keys, offshoot index), fresh distinctions of answering births in order."""

    def __init__(self, run, base=None):
        S0 = run.snaps[0]
        if base is not None:
            nk = run.snaps[run.base_round].n_knots
            nd = run.snaps[run.base_round].n_distinctions
            self.k = base.k[:nk]
            self.d = base.d[:nd]
            start_t = run.base_round + 1
        else:
            self.k = ['s%d' % u for u in range(S0.n_knots)]
            self.d = ['d%d' % d for d in range(S0.n_distinctions)]
            start_t = 1
        for rec in run.recs[start_t - 1:]:
            t = rec['round']
            for b in rec['births']:
                pk = tuple(sorted(self.k[p] for p in b['parents']))
                k = hkey('b', t, b['kind'], pk, b['off_index'])
                assert len(self.k) == b['id']
                self.k.append(k)
                for i, d in enumerate(b['fresh']):
                    assert d == len(self.d)
                    self.d.append(hkey('f', k, i))


# --------------------------------------------------------------------------------------------------- descent
def desc_bits(run, s, member_part):
    """For every knot of the run's last structure: an integer whose bit i says 'descended from part i' (D 2.6 on
    FD 4.2 with this s): a member of part i after round s has bit i; a knot made after round s has the bits of its
    parents; every other knot made at or before round s has none."""
    S = run.snaps[-1]
    bits = [0] * S.n_knots
    for u, i in member_part.items():
        bits[u] = 1 << i
    for u in range(S.n_knots):
        if S.made[u] > s:
            B = 0
            for p in S.parents[u]:
                B |= bits[p]
            bits[u] = B
    return bits


class View:
    """One run seen for one pair (X = part i, Y = part j) after round s."""

    def __init__(self, run, keys, bits, i, j, s, X, Y):
        self.run, self.keys, self.bits, self.i, self.j, self.s = run, keys, bits, i, j, s
        self.X, self.Y = X, Y
        self.mi, self.mj = 1 << i, 1 << j

    def dx(self, u):
        return bool(self.bits[u] & self.mi)

    def dy(self, u):
        return bool(self.bits[u] & self.mj)

    def desc(self, u):
        return DESC[(bool(self.bits[u] & self.mi), bool(self.bits[u] & self.mj))]

    def xonly(self, u):
        return (self.bits[u] & self.mi) and not (self.bits[u] & self.mj)

    def kn(self, u, S):
        return (self.keys.k[u], self.desc(u), S.made[u] == 0)


# ------------------------------------------------------------------------------------------- meetings (RD 3.4)
def round_meetings(rec, bits):
    """{(a, b), a < b: set of how} for the parts that meet in this round (groups, demand groups, takes)."""
    found = defaultdict(set)
    for how, gs in (('group', rec['groups']), ('demand group', rec['demand'].groups if rec['demand'] else [])):
        seen = set()
        for g in gs:
            B = 0
            for u in g:
                B |= bits[u]
            if B & (B - 1) and B not in seen:
                seen.add(B)
                for a, b in itertools.combinations(bitlist(B), 2):
                    found[(a, b)].add(how)
    for b in rec['births']:
        if not b['takes']:
            continue
        Pb = 0
        for p in b['parents']:
            Pb |= bits[p]
        if not Pb:
            continue
        for d, hs in b['take_holders'].items():
            Hd = 0
            for w in hs:
                Hd |= bits[w]
            for a in bitlist(Pb):
                for c in bitlist(Hd):
                    if a != c:
                        found[(min(a, c), max(a, c))].add('take')
    return found


def first_meetings(run, s, bits):
    out = {}
    for t in range(s + 1, run.rounds_read + 1):
        rec = run.recs[t - 1]
        for k, how in round_meetings(rec, bits).items():
            if k not in out:
                out[k] = (t, sorted(how))
    return out


class RoundIndex:
    """Per round: the met sets of the roster and the demand roster with their union of descent bits, indexed by bit;
    and, for each common knot, its met sets (its met set at round t, in either roster)."""

    def __init__(self, rec, bits):
        self.by_bit = defaultdict(list)
        self.of_knot = defaultdict(list)
        for R in (rec['roster'], rec['demand']):
            if R is None:
                continue
            for M, ws in R.sc.items():
                B = 0
                for u in M:
                    B |= bits[u]
                ent = (B, M, ws)
                for w in ws:
                    self.of_knot[w].append(ent)
                if B & (B - 1):
                    for a in bitlist(B):
                        self.by_bit[a].append(ent)


def ancestor_bits(S):
    anc = [0] * S.n_knots
    for u in range(S.n_knots):
        A = 0
        for p in S.parents[u]:
            A |= anc[p] | (1 << p)
        anc[u] = A
    return anc


def linking(view, t, idx, anc):
    """BD2 5.2 to 5.6 at the meeting round t: the linking set (RD 3.5's set and the suppliers of cross takes), each
    knot with its round, parents, FD 5.7 class, linking distinctions with their holders; strict; FD 5.7's weaker
    class; the ancestral reading in both forms."""
    run = view.run
    S = run.snaps[t]
    rec = run.recs[t - 1]
    mi, mj = view.mi, view.mj
    bits = view.bits
    link = {}
    weak = False
    for B, M, ws in idx.by_bit.get(view.i, ()):
        if not (B & mj):
            continue
        if any(S.made[w] > 0 for w in ws):
            weak = True
        for w in ws:
            if S.made[w] <= t - 1:
                link.setdefault(w, set()).add('met set')
    for b in rec['births']:
        if not b['takes']:
            continue
        px = any(bits[p] & mi for p in b['parents'])
        py = any(bits[p] & mj for p in b['parents'])
        for d, hs in b['take_holders'].items():
            for w in hs:
                if (px and bits[w] & mj) or (py and bits[w] & mi):
                    link.setdefault(w, set()).add('supplier of a cross take')
    out = []
    xm, ym = set(view.X), set(view.Y)
    ancestral_any = False
    every_any = False
    for w in sorted(link):
        cls = None
        wb = 1 << w
        for B, M, ws in idx.of_knot.get(w, ()):
            if not (B & mi and B & mj):
                continue
            us = [u for u in M if bits[u] & mi and anc[u] & wb]
            vs = [v for v in M if bits[v] & mj and anc[v] & wb]
            for u in us:
                for v in vs:
                    if not (w in S.parents[u] and w in S.parents[v]):
                        cls = 'ancestral common knot'
                        break
                if cls:
                    break
            if cls:
                break
        if cls is None:
            cls = 'made, no ancestor of both' if S.made[w] > 0 else 'start knot, no recorded ancestor of both'
        every = all(anc[u] & wb for u in xm) and all(anc[v] & wb for v in ym)
        made_anc = cls == 'ancestral common knot' and S.made[w] > 0
        ancestral_any |= made_anc
        every_any |= made_anc and every
        ldist = []
        for d in S.places[w]:
            hs = S.holders[d]
            if any(bits[x] & (mi | mj) for x in hs):
                ldist.append({'d': d, 'first_holder_round': min(S.made[x] for x in hs),
                              'holders': [[x, S.made[x], view.desc(x), S.kind[x]] for x in hs]})
        out.append({'knot': w, 'made': S.made[w], 'kind': S.kind[w], 'parents': list(S.parents[w]),
                    'descent': view.desc(w), 'how': sorted(link[w]), 'class': cls,
                    'ancestral_made': made_anc, 'every_member_form': bool(made_anc and every),
                    'linking_distinctions': ldist,
                    'ancestry': sorted([x, S.made[x]] for x in bitlist(anc[w]))})
    strict = bool(out) and all(x['made'] > 0 for x in out)
    if not out:
        verdict = 'no linking knot'
    elif strict:
        verdict = 'only through made knots'
    else:
        verdict = 'through a start knot'
    start_holds = any(hh[1] == 0 for x in out for ld in x['linking_distinctions'] for hh in ld['holders'])
    return {'linking': out, 'strict': strict, 'link_verdict': verdict, 'weak_FD57': weak,
            'ancestral': bool(strict and ancestral_any), 'ancestral_every_member': bool(strict and every_any),
            'start_knot_holds_linking_distinction': start_holds}


# -------------------------------------------------------------------------------- the course from X only (RD 3.1)
def course(view, R):
    """The course from X only after round s through round R in ticket A's reduced form (W 10), with the answer keys
    of its nodes for the exact fast path (B 14).  None if the run did not read round R."""
    run = view.run
    if run.rounds_read < R:
        return None
    s = view.s
    S = run.snaps[R]
    nd_s = run.snaps[s].n_distinctions
    ks = [u for u in range(S.n_knots) if view.xonly(u)]
    kidx = {u: i for i, u in enumerate(ks)}
    dlab = {}
    dhold = defaultdict(list)
    for u in ks:
        for d in S.places[u]:
            dhold[d].append(kidx[u])
            if d not in dlab:
                if d < nd_s:
                    org = 'E'
                else:
                    org = 'FX' if view.xonly(S.maker[d]) else 'FO'
                dlab[d] = '%s:%d' % (org, 1 if S.barred[d] else 0)
    labels = []
    keys = []
    Kk, Kd = view.keys.k, view.keys.d
    for u in ks:
        cnts = []
        r0 = max(S.made[u], s)
        for r in range(r0, R + 1):
            hu, ku = run.snaps[r].hk(u)
            cnts.append('%d.%d' % (hu, ku))
        leafs = Counter(dlab[d] for d in S.places[u] if len(dhold[d]) == 1)
        rnd = s if S.made[u] <= s else S.made[u]
        labels.append('K|%d|%s|%d|%s|%s' % (rnd, S.kind[u], len(S.places[u]), ','.join(cnts),
                                           ','.join('%s*%d' % (k, v) for k, v in sorted(leafs.items()))))
        keys.append(Kk[u])
    edges = []
    for d in sorted(dhold):
        hs = dhold[d]
        if len(hs) >= 2:
            j = len(labels)
            labels.append('D|' + dlab[d])
            keys.append(Kd[d])
            for i in hs:
                edges.append((i, j, 'i'))
    for u in ks:
        for p in S.parents[u]:
            if p in kidx:
                edges.append((kidx[u], kidx[p], 'p'))
    return {'labels': labels, 'edges': edges, 'n_knots': len(ks), 'keys': keys}


def _keyed(c):
    lab = dict(zip(c['keys'], c['labels']))
    K = c['keys']
    ed = sorted((K[a], K[b], t) for a, b, t in c['edges'])
    return lab, ed


def same_course(c1, c2):
    """Exact: equal under the answer keys (an explicit isomorphism), else the invariant (different: not the same),
    else VF2 (ticket A's `wbc.same_course`)."""
    if c1['n_knots'] != c2['n_knots'] or len(c1['labels']) != len(c2['labels']) or \
            len(c1['edges']) != len(c2['edges']):
        return False
    if len(set(c1['keys'])) == len(c1['keys']) and len(set(c2['keys'])) == len(c2['keys']):
        if _keyed(c1) == _keyed(c2):
            return True
    if sorted(c1['labels']) != sorted(c2['labels']):
        return False
    if wbc.course_invariant(c1) != wbc.course_invariant(c2):
        return False
    return wbc.same_course(c1, c2)


def first_course_difference(vA, vB, s, last):
    """The first round R in s+1..last at which the courses through R differ (None: equal through last)."""
    for R in range(s + 1, last + 1):
        ca, cb = course(vA, R), course(vB, R)
        if not same_course(ca, cb):
            return R, ca, cb
    return None, course(vA, last), course(vB, last)


# ----------------------------------------------------------------------- the values used at X's births (RD 3.3)
def values(view, t):
    """Ticket A's entries (wbc RunState._analyse), for this pair's descent; the treatment's act includes SHORT-BY's
    count, and step 7 also holds the parent's owing o where the ration uses it (B 15)."""
    run = view.run
    rec = run.recs[t - 1]
    S = run.snaps[t]
    kk = view.keys.k
    dk = view.keys.d
    desc = view.desc
    made = S.made

    def kn(u):
        return (kk[u], desc(u), made[u] == 0)
    xo = [u for u in rec['members'] if view.xonly(u)]
    xos = set(xo)
    entries = []
    rankc = Counter()
    member_groups = defaultdict(list)
    for g in rec['groups']:
        for u in g:
            member_groups[u].append(g)
        if not xos.intersection(g):
            continue
        xk = tuple(sorted(kk[u] for u in g if u in xos))
        r = rankc[xk]
        rankc[xk] += 1
        entries.append({'step': 1, 'pos': ('g', xk, r), 'kind': 'group',
                        'value': (len(g), tuple(sorted(desc(u) for u in g))), 'part': [kn(u) for u in g]})
    for u in xo:
        co = sorted({v for g in member_groups[u] for v in g})
        entries.append({'step': 2, 'pos': ('m', kk[u]), 'kind': 'member',
                        'value': (rec['owe'].get(u, 0), u in rec['short']), 'part': [kn(v) for v in co]})
    for u in xo:
        co = sorted({v for g in member_groups[u] for v in g})
        entries.append({'step': 3, 'pos': ('a', kk[u]), 'kind': 'act', 'value': rec['act'][u],
                        'part': [kn(v) for v in co]})
    xb = [b for b in rec['births'] if any(p in xos for p in b['parents'])]
    DR = rec['demand']
    dgroups = defaultdict(list)
    if DR is not None:
        for g in DR.groups:
            for u in g:
                dgroups[u].append(g)
    S0 = run.snaps[t - 1]
    for b in xb:
        bk = kk[b['id']]
        entries.append({'step': 4, 'pos': ('b', bk), 'kind': 'birth',
                        'value': (b['kind'], tuple(sorted(kk[p] for p in b['parents'])),
                                  tuple(dk[d] for d in b['loose'])),
                        'part': [kn(p) for p in b['parents']],
                        'loose_from': [(dk[d], kn(p)) for p in b['parents'] for d in b['loose']
                                       if d in S0.places[p]]})
    for b in xb:
        bk = kk[b['id']]
        cands = [(dk[d], tuple(sorted(kk[w] for w in sup))) for d, sup in b['cands']]
        entries.append({'step': 5, 'pos': ('c', bk), 'kind': 'candidates',
                        'value': (tuple(sorted(cands)), tuple(sorted(dk[d] for d in b['takes']))),
                        'part': [(dk[d], [kn(w) for w in sup]) for d, sup in b['cands']],
                        'taken': [dk[d] for d in b['takes']]})
    for b in xb:
        bk = kk[b['id']]
        x = b['id']
        partners = sorted({v for g in dgroups.get(x, []) for v in g} - {x})
        entries.append({'step': 6, 'pos': ('D', bk), 'kind': 'demand',
                        'value': (b['D'], tuple(sorted(desc(v) for v in partners))),
                        'part': [kn(v) for v in partners]})
    for b in xb:
        bk = kk[b['id']]
        o = b['o'] if run.law.ration in eng.RATIONS_OWING else None
        entries.append({'step': 7, 'pos': ('f', bk), 'kind': 'fresh',
                        'value': (b['p'], b['implied'], b['f']) + ((o,) if o is not None else ()), 'part': []})
    entries.append({'step': 8, 'pos': ('w',), 'kind': 'roundwide', 'value': (rec['closing'], None), 'part': []})
    return entries


def attribution(vO, vA, s, last):
    """RD 4.3 via ticket A's `wbc.first_difference`: the first round s+1..last where the values used at X's births
    differ; entries in the order of the run with fewer of Y's members usable (vO, A = empty; B 16)."""
    for t in range(s + 1, last + 1):
        EO, EA = values(vO, t), values(vA, t)
        fd = wbc.first_difference(EO, EA)
        if fd is not None:
            fd['round'] = t
            fd2 = wbc.first_difference(EA, EO)
            fd['class_in_other_order'] = fd2['class'] if fd2 else None
            return fd
    return None


# ------------------------------------------------------------------------------------------------ the m reading
def birth_of(pos, t):
    if pos[0] == 'g':
        return (t, 'g') + tuple(pos[1])
    if pos[0] == 'w':
        return (t, 'w')
    return (t, pos[1])


def m_reading(views, classes, s, last, max_entries=400):
    """BD2 6.6 over the subsets' runs: P by courses; the input entries (positions whose values differ between two
    subsets with a differing part classed through the meeting); m, the least number of input entries at distinct
    births whose joint value refines P (searched up to 2; B 17)."""
    n = len(views)
    ncls = len(set(classes))
    if ncls == 1:
        return {'verdict': 'no difference', 'classes': 1, 'm': 0, 'entries': []}
    posval = defaultdict(lambda: [None] * n)
    posent = defaultdict(lambda: [None] * n)
    for vi, v in enumerate(views):
        for t in range(s + 1, last + 1):
            for e in values(v, t):
                key = (t, e['step'], repr(e['pos']))
                posval[key][vi] = e['value']
                posent[key][vi] = e
    inputs = []
    for key, vals in posval.items():
        if len(set(map(repr, vals))) < 2:
            continue
        ents = posent[key]
        through = False
        for a in range(n):
            for b in range(a + 1, n):
                if repr(vals[a]) == repr(vals[b]):
                    continue
                ea, eb = ents[a], ents[b]
                kind = (ea or eb)['kind']
                part = wbc.differing_part(ea, eb)
                if wbc.classify_part(kind, ea, eb, part) == 'through the meeting':
                    through = True
                    break
            if through:
                break
        if through:
            inputs.append(key)
    inputs.sort()

    def refines(keys_):
        seen = {}
        for vi in range(n):
            jv = tuple(repr(posval[k][vi]) for k in keys_)
            if jv in seen and seen[jv] != classes[vi]:
                return False
            seen.setdefault(jv, classes[vi])
        return True

    def induces(keys_):
        part_v = defaultdict(set)
        part_c = defaultdict(set)
        for vi in range(n):
            jv = tuple(repr(posval[k][vi]) for k in keys_)
            part_v[jv].add(vi)
            part_c[classes[vi]].add(vi)
        return sorted(map(sorted, part_v.values())) == sorted(map(sorted, part_c.values()))
    one = [k for k in inputs if refines([k])]
    if one:
        return {'verdict': 'handed in one value', 'm': 1, 'classes': ncls, 'n_input_entries': len(inputs),
                'entries': [list(k) for k in one[:10]], 'induces_exactly': [induces([k]) for k in one[:10]]}
    if len(inputs) <= max_entries:
        for a, b in itertools.combinations(inputs, 2):
            if birth_of(eval(a[2]), a[0]) == birth_of(eval(b[2]), b[0]):
                continue
            if refines([a, b]):
                return {'verdict': 'composed over several births', 'm': 2, 'classes': ncls,
                        'n_input_entries': len(inputs), 'entries': [list(a), list(b)]}
        m = '>=3' if refines(inputs) else 'not reached by the input entries'
    else:
        m = '>=2 (not searched further: %d input entries)' % len(inputs)
    return {'verdict': 'composed over several births', 'm': m, 'classes': ncls, 'n_input_entries': len(inputs),
            'entries': [list(k) for k in inputs[:10]]}


# ------------------------------------------------------------------------------------------- rosters the same
def xonly_roster(view, r):
    """The roster of the members descended from X only after round r: h, k and inclusion-maximal met sets."""
    run = view.run
    S = run.snaps[r]
    mem = [(u, h, k) for u, h, k in eng.live_members(S) if view.xonly(u)]
    G = eng.Guard(1000)
    R = eng.build_roster(S, mem, 'lasting', G)
    return R


def roster_graph(R):
    G = nx.Graph()
    for u in R.members:
        G.add_node(('m', u), l='m%d.%d' % (R.h[u], R.k[u]))
    for i, M in enumerate(R.maxsets):
        G.add_node(('M', i), l='M%d' % len(M))
        for u in M:
            G.add_edge(('M', i), ('m', u))
    return G


def rosters_same(R1, R2):
    if sorted((R1.h[u], R1.k[u]) for u in R1.members) != sorted((R2.h[u], R2.k[u]) for u in R2.members):
        return False
    if sorted(len(M) for M in R1.maxsets) != sorted(len(M) for M in R2.maxsets):
        return False
    g1, g2 = roster_graph(R1), roster_graph(R2)
    if nx.weisfeiler_lehman_graph_hash(g1, node_attr='l', iterations=4) != \
            nx.weisfeiler_lehman_graph_hash(g2, node_attr='l', iterations=4):
        return False
    return iso.GraphMatcher(g1, g2, node_match=iso.categorical_node_match('l', None)).is_isomorphic()


# --------------------------------------------------------------------------- the symmetry check (BD2 6.8, item 3)
class _Budget(Exception):
    pass


def _refine(adj, col):
    """Colour refinement to the stable colouring; colours are canonical integers (names of sorted signatures), so
    the colours of the two copies of the disjoint union are comparable."""
    ncls = len(set(col))
    while True:
        sig = [(col[v], tuple(sorted(col[w] for w in adj[v]))) for v in range(len(adj))]
        names = {x: i for i, x in enumerate(sorted(set(sig)))}
        new = [names[x] for x in sig]
        if len(names) == ncls:
            return new
        ncls = len(names)
        col = new


def symmetry_exchanging(S, X, Y, fixed, limit=2_000_000):
    """Whether the structure S (knots holding distinctions, with their bars) has a renaming of its knots and
    distinctions onto itself that exchanges the members of X with those of Y and fixes every knot in `fixed`
    (B 18).  Exact: individualisation and refinement on the disjoint union of the structure labelled one way and
    the other; each individualisation is one search node; 'undecided' past `limit` nodes; a found map is checked
    edge by edge."""
    if len(X) != len(Y):
        return {'answer': 'no', 'nodes': 0, 'why': 'sizes differ'}
    nodes = [('k', u) for u in range(S.n_knots)] + [('d', d) for d in range(S.n_distinctions) if S.holders[d]]
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    edges = [(idx[('k', u)], idx[('d', d)]) for d in range(S.n_distinctions) for u in S.holders[d]]
    adj = [[] for _ in range(2 * n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
        adj[n + a].append(n + b)
        adj[n + b].append(n + a)
    lab1, lab2 = {}, {}
    for v in nodes:
        lab1[v] = lab2[v] = 'k' if v[0] == 'k' else 'd%d' % S.barred[v[1]]
    for u in X:
        lab1[('k', u)], lab2[('k', u)] = 'X', 'Y'
    for u in Y:
        lab1[('k', u)], lab2[('k', u)] = 'Y', 'X'
    for i, w in enumerate(sorted(fixed)):
        lab1[('k', w)] = lab2[('k', w)] = 'L%d' % i
    names = {x: i for i, x in enumerate(sorted(set(lab1.values()) | set(lab2.values())))}
    col0 = [names[lab1[v]] for v in nodes] + [names[lab2[v]] for v in nodes]
    count = [0]
    eset = set(edges)

    def balanced(col):
        return Counter(col[:n]) == Counter(col[n:])

    def search(col):
        count[0] += 1
        if count[0] > limit:
            raise _Budget()
        col = _refine(adj, col)
        if not balanced(col):
            return False
        cls = defaultdict(list)
        for v in range(n):
            cls[col[v]].append(v)
        big = [c for c, vs in cls.items() if len(vs) > 1]
        if not big:
            where = {col[n + v]: v for v in range(n)}
            phi = [where[col[v]] for v in range(n)]
            return all(((phi[a], phi[b]) in eset) for a, b in edges)
        c = min(big, key=lambda c_: (len(cls[c_]), c_))
        v = cls[c][0]
        fresh = max(col) + 1
        for w in range(n, 2 * n):
            if col[w] != c:
                continue
            col2 = list(col)
            col2[v] = fresh
            col2[w] = fresh
            if search(col2):
                return True
        return False
    try:
        ok = search(col0)
    except _Budget:
        return {'answer': 'undecided', 'nodes': count[0]}
    return {'answer': 'yes' if ok else 'no', 'nodes': count[0]}


# -------------------------------------------------------------------------------------------------- knot tests
def kt_summary(out):
    return {'verdicts': out['verdicts'], 'n_fail': len(out['fails']), 'fails': out['fails'][:10],
            'n_disagree': len(out['disagree']), 'n_untested': len(out['untested'])}


def knot_test_full(run):
    return kt_summary(knots.test_run(run.snaps, run.law))


def knot_test_barred(run, s, full=False):
    """BD2 1.3 for a barred run or a lasting rerun: parity in full at its last round read; not-all-equal the knots
    born after round s, by FD 7's birth method alone, a verdict fixed at birth (B 19), after checking that every
    birth after round s received a fresh distinction (if one did not, in full).  full=True (runs P1 and U1): every
    knot at every round read, as run A."""
    R = run.rounds_read
    if full:
        if run.law.knot_law == 'parity':
            out = kt_summary(knots.test_run(run.snaps, run.law))
        else:
            out = birth_all(run)
        out['tested_in_full'] = True
        return out
    if run.law.knot_law == 'parity':
        return kt_summary(knots.test_run(run.snaps, run.law, rounds=[R]))
    S = run.snaps[R]
    nofresh = [u for u in range(S.n_knots) if S.made[u] > s and not any(S.maker[d] == u for d in S.places[u])]
    if nofresh:
        out = kt_summary(knots.test_run(run.snaps, run.law))
        out['tested_in_full'] = True
        return out
    fails, untested = [], []
    n = 0
    for u in range(S.n_knots):
        t = S.made[u]
        if t <= s:
            continue
        v = knots.birth_method(run.snaps[t - 1], run.snaps[t], u)
        if v is None:
            untested.append({'knot': u, 'places': len(S.places[u]), 'method': 'birth'})
            continue
        n += 1
        if not v:
            fails.append({'round': R, 'knot': u, 'places': len(S.places[u]), 'made': t, 'kind': S.kind[u],
                          'how': 'birth'})
    return {'verdicts': n, 'n_fail': len(fails), 'fails': fails[:10], 'n_disagree': 0, 'n_untested': len(untested)}


def birth_all(run):
    """Not-all-equal, every knot of a run at every round read (B 31): start knots directly at round 0, every other
    knot by FD 7's birth method, its verdict holding at every round from its birth (every birth fresh: checked);
    verdicts counted per knot per round, as knots.test_run counts them."""
    R = run.rounds_read
    S = run.snaps[R]
    nofresh = [u for u in range(S.n_knots) if S.made[u] > 0 and not any(S.maker[d] == u for d in S.places[u])]
    if nofresh:
        return kt_summary(knots.test_run(run.snaps, run.law))
    fails, untested = [], []
    n = 0
    start = knots.nae_direct(run.snaps[0], list(range(run.snaps[0].n_knots)))
    for u in range(S.n_knots):
        t = S.made[u]
        v = start[u] if t == 0 else knots.birth_method(run.snaps[t - 1], run.snaps[t], u)
        if v is None:
            untested.append({'knot': u, 'places': len(S.places[u]), 'method': 'birth'})
            continue
        n += R + 1 - t
        if not v:
            fails.append({'round': t, 'knot': u, 'places': len(S.places[u]), 'made': t, 'kind': S.kind[u],
                          'how': 'birth' if t else 'direct'})
    return {'verdicts': n, 'n_fail': len(fails), 'fails': fails[:10], 'n_disagree': 0, 'n_untested': len(untested)}
