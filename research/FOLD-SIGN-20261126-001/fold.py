"""fold.py: the frozen test of FOLD-SIGN-20261126-001 (README.md, part B). Ordinary growth, one round at a time, with
the record of parents kept; the end read as a labelled multigraph (knots with their loose counts, shared distinctions as
edges, multiplicity kept); its renamings (automorphisms acting on knots; those that fix every knot act trivially and are
not counted); the reading (the start knots and the record of who was made from whom) and its images under the renamings.
Per end:
    Q1  every renaming that keeps the reading is an even permutation of knots (the relative sign is well defined)
    Q2  some renaming that changes the reading is odd
    Q3  some such odd renaming exchanges two disjoint parts that share no distinction (a sign across a split)

    fold.py run LAW ROUNDS I0 I1     census starts I0..I1-1 (forbid.py's census), a JSON line per start and round
    fold.py lone LAW ROUNDS          the lone four-place knot"""
import sys, json, collections, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import forbid
sys.path.insert(0, str(HERE.parent / 'SHORT-AGAIN-20261126-001'))
import ring_line
eng = ring_line.eng
import networkx as nx
from networkx.algorithms import isomorphism

CAP = 200000            # renamings enumerated at most; an end with more is reported as not run
ENGINE = 'canonical' if '--canonical' in sys.argv else 'fold'      # the engine is a scaffold, swapped


def multigraph(supports, barred=frozenset()):
    held = forbid.holders(supports)
    G = nx.Graph()
    for i, row in enumerate(supports):
        G.add_node(i, loose=(sum(1 for d in row if len(held[d]) == 1 and d not in barred),
                             sum(1 for d in row if d in barred)))
    for d, hs in held.items():
        if len(hs) == 2:
            a, b = hs
            if G.has_edge(a, b): G[a][b]['m'] += 1
            else: G.add_edge(a, b, m=1)
    return G


def renamings(G):
    gm = isomorphism.GraphMatcher(G, G, node_match=lambda a, b: a['loose'] == b['loose'], edge_match=lambda a, b: a['m'] == b['m'])
    out = []
    for m in gm.isomorphisms_iter():
        out.append(m)
        if len(out) > CAP: return None
    return out


def sign(perm):
    seen, s = set(), 1
    for a in perm:
        if a in seen: continue
        n, b = 0, a
        while b not in seen:
            seen.add(b); b = perm[b]; n += 1
        if n % 2 == 0: s = -s
    return s


def image(reading, m):
    start, parent = reading
    return frozenset(m[a] for a in start), frozenset((m[c], m[p]) for c, p in parent)


def exchange_across(G, m):
    """does m exchange two disjoint, separated sets of knots (A <-> B, no shared distinction between A and B)?"""
    moved = [a for a in m if m[a] != a]
    if not moved or any(m[m[a]] != a for a in moved): return False
    comps = [set(c) for c in nx.connected_components(G.subgraph(moved))]
    for A in comps:
        B = {m[a] for a in A}
        if not (A & B) and not any(G.has_edge(a, b) for a in A for b in B): return True
    return False


def grow(supports, law, rounds):
    """ordinary growth on the engine of the recent line (eng.play_round, a short knot waits; FOLD_ENGINE) or on the
    canonical engine of the 20 November studies (forbid.grown: one short knot stalls the round); yields (round,
    supports, barred distinctions, reading) after each round"""
    if ENGINE == 'canonical':
        stage, parent, start = tuple(supports), set(), frozenset(range(len(supports)))
        for r in range(1, rounds + 1):
            new, status, births = forbid.grown(stage, law, 'ordinary')
            if status != 'funded': return
            for b in births:
                for p in b['parents']: parent.add((b['knot'], p))
            stage = new
            yield r, stage, frozenset(), (start, frozenset(parent))
        return
    S = eng.from_stars([list(r) for r in supports]); L = eng.Law('ORD', 'CANCEL-WAIT', None, law); G = eng.Guard(4)
    for r in range(1, rounds + 1):
        T = S.copy()
        try: rec = eng.play_round(T, L, G)
        except eng.GuardStop: return
        if not rec['births']: return
        S = T
        stage = tuple(tuple(p) for p in S.places)
        parent = frozenset((k, p) for k in range(S.n_knots) for p in S.parents[k])
        barred = frozenset(d for d in range(len(S.barred)) if S.barred[d])
        yield r, stage, barred, (frozenset(range(S.n_start)), parent)


def read(supports, law, rounds):
    out = []
    for r, stage, barred, reading in grow(supports, law, rounds):
        G = multigraph(stage, barred)
        R = renamings(G)
        if R is None:
            out.append({'round': r, 'knots': len(stage), 'not run': 'more than %d renamings' % CAP}); continue
        keep = [m for m in R if image(reading, m) == reading]
        change = [m for m in R if image(reading, m) != reading]
        odd_change = [m for m in change if sign([m[i] for i in range(len(stage))]) < 0]
        out.append({'round': r, 'knots': len(stage), 'renamings': len(R), 'keep the reading': len(keep),
                    'Q1 well defined': all(sign([m[i] for i in range(len(stage))]) > 0 for m in keep),
                    'readings': len(R) // len(keep), 'Q2 odd change': bool(odd_change),
                    'Q3 across a split': any(exchange_across(G, m) for m in odd_change)})
    return out


if __name__ == '__main__':
    law, rounds = sys.argv[2], int(sys.argv[3])
    if sys.argv[1] == 'lone':
        print(json.dumps({'start': 'lone four-place knot', 'rows': read(((0, 1, 2, 3),), law, rounds)}))
    else:
        S = forbid.census()
        for i in range(int(sys.argv[4]), min(int(sys.argv[5]), len(S))):
            print(json.dumps({'start': i, 'rows': read(forbid.supports_of(S[i]), law, rounds)}), flush=True)
