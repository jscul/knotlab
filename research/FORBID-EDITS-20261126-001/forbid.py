"""forbid.py: free edits under joins that forbid.  The census of FORBID-EDITS-20261126-001 (README.md, part B).

Growth, the two forbidding laws and the exact counts are the earlier studies' own code: one round of the canonical
engine with the fresh count cut by A129 (one fewer) or A130 (the arity floor), or not cut (the ordinary count), from
FORBIDDING-JOIN-20261120-001B; exact counts of allowed states under the equal weighting of states (U) and of surviving
old states with their completions sharing each one's weight (S, the earlier 'L' restricted to survivors), from
ENTANGLEMENT-READ-20261120-001B and FORBIDDING-JOIN-20261120-001B.

    forbid.py starts                 count the census starts
    forbid.py run KIND I0 I1         KIND in E1, E2, M1 (three readers, E1 edits); starts I0..I1-1, a JSON line each
    forbid.py count KIND I0 I1       the structural pre-count: kinds and forbidding flags, no tables
    ... --extension                  on the extension's sampled starts of 6, 7 and 8 knots (sampled())
    ... --shared                     the addendum: also read placements where a birth has parents of two readers"""
import sys, json, itertools, collections
from fractions import Fraction
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / 'experiments'
FJ = EXP / 'FORBIDDING-JOIN-20261120-001B' / 'FORBIDDING-JOIN-20261120-001B-E001_free_readings'
ER = EXP / 'ENTANGLEMENT-READ-20261120-001B' / 'ENTANGLEMENT-READ-20261120-001B-E001_separated_readings'
sys.path.insert(0, str(ER)); sys.path.insert(0, str(FJ))


def load(path, name):
    spec = spec_from_file_location(name, path); module = module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module); return module


precedent = load(ER / 'run.py', 'entanglement_predecessor')
ENGINE = precedent.canonical
from counts import StageCounts  # noqa: E402
from rival_growth import grow  # noqa: E402

ARMS = ('ordinary', 'one_fewer', 'arity_floor')          # the control, A129, A130
LAWS = ('nae', 'parity')
MAX_KNOTS, MAX_DISTINCTIONS = 5, 12
SHARED = '--shared' in sys.argv          # the addendum: read placements with a birth of two readers too (a contact)


# ---------------------------------------------------------------- the census of starts

def connected(n, edges):
    adj = {i: set() for i in range(n)}
    for a, b in edges: adj[a].add(b); adj[b].add(a)
    seen, todo = {0}, [0]
    while todo:
        for j in adj[todo.pop()] - seen: seen.add(j); todo.append(j)
    return len(seen) == n


def canonical(n, mult, loose):
    """the least relabelling of (multiplicity on each pair, loose counts)"""
    best = None
    for perm in itertools.permutations(range(n)):
        m = tuple(sorted((min(perm[a], perm[b]), max(perm[a], perm[b]), k) for (a, b), k in mult.items()))
        l = tuple(loose[perm.index(i)] for i in range(n))
        key = (m, l)
        if best is None or key < best: best = key
    return best


def starts():
    """each start once up to relabelling: n knots, shared multiplicities 1 or 2 on a connected set of pairs, loose 0-2,
    at least three places a knot, at most MAX_DISTINCTIONS distinctions"""
    out = []
    for n in range(3, MAX_KNOTS + 1):
        pairs = list(itertools.combinations(range(n), 2))
        seen = set()
        for k in range(n - 1, len(pairs) + 1):
            for edges in itertools.combinations(pairs, k):
                if k > MAX_DISTINCTIONS or not connected(n, edges): continue
                for ms in itertools.product((1, 2), repeat=k):
                    if sum(ms) > MAX_DISTINCTIONS: continue
                    mult = dict(zip(edges, ms))
                    shared = [sum(m for (a, b), m in mult.items() if i in (a, b)) for i in range(n)]
                    for loose in itertools.product((0, 1, 2), repeat=n):
                        if sum(ms) + sum(loose) > MAX_DISTINCTIONS: continue
                        if any(s + l < 3 for s, l in zip(shared, loose)): continue
                        key = canonical(n, mult, loose)
                        if key in seen: continue
                        seen.add(key); out.append((n, key[0], key[1]))
    return out


def supports_of(start):
    n, mult, loose = start
    rows, nxt = [[] for _ in range(n)], 0
    for a, b, k in mult:
        for _ in range(k): rows[a].append(nxt); rows[b].append(nxt); nxt += 1
    for i in range(n):
        for _ in range(loose[i]): rows[i].append(nxt); nxt += 1
    return tuple(tuple(r) for r in rows)


# ---------------------------------------------------------------- growth and records

def holders(supports):
    h = collections.defaultdict(list)
    for i, row in enumerate(supports):
        for d in row: h[d].append(i)
    return h


def meets(supports, a, b):
    return bool(set(supports[a]) & set(supports[b]))


def edit(base, adds):
    """adds: (holder, new distinction) pairs, one more loose distinction at each holder"""
    out = [list(r) for r in base]
    for h, d in adds: out[h].append(d)
    return tuple(tuple(r) for r in out)


def grown(edited, law, arm):
    stage, info = grow(edited, law, arm, ENGINE)
    if stage is None: return edited, info['status'], []
    return stage, 'funded', info['births']


def record_roles(edited, stage, births, own):
    """a reader's complete record: the values of its holders' distinctions (in their order) and of the fresh
    distinctions of births with one of its holders as a parent, with those births' shapes"""
    bits = [d for h in own for d in edited[h]]
    shape = []
    for b in sorted(births, key=lambda r: (r['parents'], r['inputs'])):
        if set(b['parents']) & set(own):
            shape.append((tuple(b['parents']), tuple(b['inputs']), b['f']))
            bits += list(b['fresh'])
    return list(dict.fromkeys(bits)), tuple(shape)       # a distinction both holders hold is read once


def distribution(counter, bits, weighting):
    """exact distribution of the values of `bits` (a dict word -> Fraction) under U or S"""
    if weighting == 'U':
        mass = counter.histogram(tuple(bits), 'U')[0]
    else:
        mass, _ = counter.histogram(tuple(bits), 'L')
    tot = sum(mass)
    return {w: Fraction(m, tot) for w, m in enumerate(mass) if m}


def bit(word, i, width):
    return (word >> (width - 1 - i)) & 1


# ---------------------------------------------------------------- one placement

def placement(base, readers, kind, law, arm, tables=True):
    """readers: one tuple of holders a reader.  The preparation's states are the start's allowed states, lifted
    through the edits: the start's knots stay in force beside the edited ones (WHOLE-STAGE's primary population), so an
    edit alone moves no weight and only growth can.  Returns the placement's kind, its flags and (with tables) the
    tables and records."""
    first = 1 + max(d for r in base for d in r)
    k = len(readers)
    held = holders(base)
    marks = [next((d for d in base[rd[0]] if len(held[d]) == 1), None) for rd in readers]
    if any(m is None for m in marks): return {'kind': 'not read', 'why': 'a reader holder has no loose distinction to read'}
    owner = {h: i for i, rd in enumerate(readers) for h in rd}
    res, shapes, zsets = {}, {}, {}
    shared_here = False
    for st in itertools.product((0, 1), repeat=k):
        adds = []
        for i, (s, rd) in enumerate(zip(st, readers)):
            if kind in ('E1', 'M1'):
                if s: adds.append((rd[0], first + i))
            else:
                adds.append((rd[s], first + i))
        ed = edit(base, adds)
        stage, status, births = grown(ed, law, arm)
        sides = [sorted({owner[p] for p in b['parents'] if p in owner}) for b in births]
        if any(len(x) > 1 for x in sides) and not SHARED: return {'kind': 'shared birth'}
        shared_here = shared_here or any(len(x) > 1 for x in sides)
        counter = StageCounts(law, base + ed, base + stage)
        old = StageCounts(law, base + ed, base + ed).total()
        if counter.total() == 0: return {'kind': 'no allowed state', 'setting': st}
        zero = [x[0] if len(x) == 1 else 'shared' if x else 'middle' for b, x in zip(births, sides) if b['f'] == 0]
        res[st] = {'status': status, 'births': len(births), 'zero-fresh births by side': dict(collections.Counter(map(str, zero))),
                   'retained': counter.retained(), 'old': old}
        zsets[st] = [frozenset((tuple(b['parents']), tuple(b['inputs'])) for b, x in zip(births, sides) if b['f'] == 0 and i in x)
                     for i in range(k)]
        shapes[st] = (status, frozenset((tuple(b['parents']), tuple(b['inputs']), b['f']) for b, x in zip(births, sides) if not x))
        if tables:
            rec = [record_roles(ed, stage, births, rd) for rd in readers]
            reads = list(marks) + ([first + i for i in range(k)] if kind == 'E2' else [])
            res[st]['reads'] = {w: distribution(counter, reads, w) for w in ('U', 'S')}
            res[st]['records'] = {w: [(rec[i][1], distribution(counter, rec[i][0], w)) for i in range(k)] for w in ('U', 'S')}
            res[st]['width'] = len(reads)
    zsets = {st: z for st, z in zsets.items()}
    dependent = []
    for i in range(k):
        dep = False
        for st in res:
            if st[i] == 0:
                st1 = st[:i] + (1,) + st[i + 1:]
                if zsets[st][i] != zsets[st1][i] and (res[st]['retained'] < res[st]['old'] or res[st1]['retained'] < res[st1]['old']):
                    dep = True
        dependent.append(dep)
    forbids = {st: t['retained'] < t['old'] for st, t in res.items()}
    own_zero = {st: [str(i) in t['zero-fresh births by side'] for i in range(k)] for st, t in res.items()}
    two_sided = any(forbids[st] and all(own_zero[st]) for st in res)
    one_sided = any(forbids[st] and any(own_zero[st]) for st in res)
    splits = len(set(shapes.values())) == 1
    return {'kind': 'shared birth, read' if shared_here else 'read', 'tables': res, 'forbids somewhere': any(forbids.values()), 'one-sided forbidding': one_sided,
            'two-sided forbidding': two_sided, 'splits': splits,
            'forbidding changes with own setting': dependent, 'on every side': all(dependent)}


def chsh(tables, w, ia, ib, width):
    """largest CHSH over the eight sign conventions, reading positions ia (Alice) and ib (Bob)"""
    E = {}
    for st, t in tables.items():
        E[st] = sum(p * (1 if bit(word, ia, width) == bit(word, ib, width) else -1) for word, p in t['reads'][w].items())
    best = Fraction(0)
    for signs in itertools.product((1, -1), repeat=4):
        if signs.count(-1) % 2:
            best = max(best, signs[0] * E[0, 0] + signs[1] * E[0, 1] + signs[2] * E[1, 0] + signs[3] * E[1, 1])
    return best, E


def mermin(tables, w, width, pos):
    scored = {(0, 0, 0): 0, (0, 1, 1): 1, (1, 0, 1): 1, (1, 1, 0): 1}
    best = Fraction(0)
    for r in itertools.product((0, 1), repeat=6):
        win = Fraction(0)
        for st, target in scored.items():
            for word, p in tables[st]['reads'][w].items():
                par = sum(bit(word, pos[i], width) ^ r[2 * i + st[i]] for i in range(3)) & 1
                if par == target: win += p
        best = max(best, win / 4)
    return best


def marginal(dist, keep, width):
    out = collections.Counter()
    for word, p in dist.items(): out[tuple(bit(word, i, width) for i in keep)] += p
    return dict(out)


def checks(tables, k, w, width):
    """single values and complete records: unchanged by every far setting?"""
    single, full = True, True
    for i in range(k):
        groups = collections.defaultdict(list)
        for st, t in tables.items(): groups[st[i]].append(st)
        for own, sts in groups.items():
            m = [marginal(tables[s]['reads'][w], [i] + ([k + i] if width > k else []), width) for s in sts]
            if any(x != m[0] for x in m): single = False
            r = [tables[s]['records'][w][i] for s in sts]
            if any(x != r[0] for x in r): full = False
    return single, full


def read_start(idx, start, kind, tables=True):
    base = supports_of(start)
    n = start[0]
    out = []
    size = 1 if kind in ('E1', 'M1') else 2
    k = 3 if kind == 'M1' else 2
    seen = set()
    choices = list(itertools.permutations(range(n), size * k))
    if kind == 'E2' and n > MAX_KNOTS:                  # the extension: the first 80 reader choices of a shuffled order
        import random
        random.Random(SAMPLE_SEED + idx).shuffle(choices)
    for chosen in choices:
        if kind == 'E2' and n > MAX_KNOTS and len(seen) >= 80: break
        readers = tuple(tuple(chosen[i * size:(i + 1) * size]) for i in range(k))
        key = tuple(sorted(readers))
        if key in seen: continue
        seen.add(key)
        if any(meets(base, a, b) for i in range(k) for j in range(i + 1, k) for a in readers[i] for b in readers[j]): continue
        for law in LAWS:
            for arm in ARMS:
                p = placement(base, readers, kind, law, arm, tables)
                row = {'start': idx, 'n': n, 'supports': base, 'readers': readers, 'kind of edit': kind, 'law': law, 'arm': arm}
                row.update({a: b for a, b in p.items() if a != 'tables'})
                if p['kind'] in ('read', 'shared birth, read'):
                    T = p['tables']
                    row['status'] = {''.join(map(str, s)): t['status'] for s, t in T.items()}
                    row['retained of old'] = {''.join(map(str, s)): [t['retained'], t['old']] for s, t in T.items()}
                    row['zero-fresh births'] = {''.join(map(str, s)): t['zero-fresh births by side'] for s, t in T.items()}
                    if tables:
                        width = next(iter(T.values()))['width']
                        for w in ('U', 'S'):
                            single, full = checks(T, k, w, width)
                            if k == 2:
                                scores = {'fixed old value': chsh(T, w, 0, 1, width)[0]}
                                if kind == 'E2': scores['added value'] = chsh(T, w, 2, 3, width)[0]
                            else:
                                scores = {'fixed old value': mermin(T, w, width, (0, 1, 2))}
                            row[w] = {'scores': {a: str(b) for a, b in scores.items()}, 'single unchanged': single, 'record unchanged': full}
                out.append(row)
    return out


def sampled(n, count, seed, p_meet=1 / 3, max_distinctions=18):
    """the extension's weighting: each pair of n knots meets with probability p_meet, multiplicity 1 or 2 equally,
    loose counts 0, 1 or 2 equally; a draw is kept when connected, every knot has three places and there are at most
    max_distinctions distinctions; draws with replacement, labelled"""
    import random
    rng, out = random.Random(seed), []
    pairs = list(itertools.combinations(range(n), 2))
    while len(out) < count:
        edges = [pr for pr in pairs if rng.random() < p_meet]
        mult = {pr: rng.choice((1, 2)) for pr in edges}
        loose = tuple(rng.choice((0, 1, 2)) for _ in range(n))
        shared = [sum(m for (a, b), m in mult.items() if i in (a, b)) for i in range(n)]
        if not connected(n, edges) or any(s + l < 3 for s, l in zip(shared, loose)): continue
        if sum(mult.values()) + sum(loose) > max_distinctions: continue
        out.append((n, tuple(sorted((a, b, m) for (a, b), m in mult.items())), loose))
    return out


SAMPLE_SEED, SAMPLE_COUNT, SAMPLE_SIZES = 20261126, 1000, (6, 7, 8)


def extension():
    return [s for n in SAMPLE_SIZES for s in sampled(n, SAMPLE_COUNT, SAMPLE_SEED + n)]


def census():
    p = Path(__file__).resolve().parent / 'starts.json'
    if p.exists(): return [(n, tuple(tuple(e) for e in m), tuple(l)) for n, m, l in json.loads(p.read_text())]
    S = starts(); p.write_text(json.dumps(S)); return S


if __name__ == '__main__':
    S = extension() if '--extension' in sys.argv else census()
    if sys.argv[1] == 'starts':
        print(len(S), collections.Counter(s[0] for s in S))
    else:
        kind, i0, i1 = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        chosen = range(i0, min(i1, len(S)))
        if '--starts' in sys.argv:                       # an explicit list of start indices, one JSON list in a file
            chosen = [i for i in json.loads(Path(sys.argv[sys.argv.index('--starts') + 1]).read_text()) if i0 <= i < i1]
        for idx in chosen:
            for row in read_start(idx, S[idx], kind, sys.argv[1] == 'run'):
                print(json.dumps(row), flush=True)
