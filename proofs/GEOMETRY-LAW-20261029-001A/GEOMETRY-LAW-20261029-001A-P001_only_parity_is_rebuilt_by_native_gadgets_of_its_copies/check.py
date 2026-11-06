"""Checks for GEOMETRY-LAW-20261029-001A-P001 (only parity is rebuilt by native gadgets of its own copies).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the 34 three-bit knots (complements of nonempty independent sets of the 3-cube) and their types: no wire face (atoms and
    not-all-equal type), two excluded tuples at distance two (exactly one place with a strong value), three excluded tuples (every
    place has exactly one strong value), parity
  2 symmetry: every three-bit knot's coordinate symmetry group contains a transposition, hence lies inside no rotation group of a
    cyclic order; the four-bit knots whose symmetry group lies inside the rotations of some cyclic order are counted
  3 exhaustively over native gadgets of 3 and 5 copies (connected, loopless, three legs, every shape, every placement): parity is
    rebuilt by every gadget; every other knot excludes at most the bound of its type (0, 1, 2; and at most 1 unless a copy carries two
    legs), never as many as the knot, and is never rebuilt; the bounds are attained; every arrow of the flow knot -> knot decreases
    the number of excluded tuples
  4 the structure used in the proof, for every excluded leg tuple found in 3: the gadget graph is a cactus, every cycle is an odd wire
    cycle once third slots take their forced values, and both sides of every bridge contain a leg
  5 random native gadgets of 7, 9 and 11 copies, every knot: the same bounds
  6 controls that must fire: with self-gluing allowed (one copy glued to itself, not native) some non-parity knot is rebuilt; the
    hub relation all-equal {000, 111}, which is not co-independent, is rebuilt by native gadgets; a mutated bound (at most one for
    three excluded tuples) is violated
Run: python3 -B check.py [--write]   (standard library only)"""
import hashlib, itertools, json, os, random, sys, time
from collections import Counter, defaultdict

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1200], flush=True)


# ---------------------------------------------------------------- relations
def cube(n):
    return list(itertools.product((0, 1), repeat=n))


def knots(n):
    """complements of nonempty independent sets of the n-cube"""
    S = cube(n)
    res = []
    def grow(start, E):
        if E:
            res.append(frozenset(s for s in S if s not in E))
        for i in range(start, len(S)):
            s = S[i]
            if all(sum(a != b for a, b in zip(s, e)) >= 2 for e in E):
                grow(i + 1, E + [s])
    grow(0, [])
    return res


def permute(K, p):
    """place i of the result carries place p[i] of K"""
    return frozenset(tuple(s[p[i]] for i in range(len(p))) for s in K)


def stabilizer(K, n):
    return [p for p in itertools.permutations(range(n)) if permute(K, p) == K]


def placements(K, n):
    return sorted({permute(K, p) for p in itertools.permutations(range(n))}, key=sorted)


def excluded(K, n):
    return sorted(set(cube(n)) - K)


def strong_values(K):
    """for each place k, the values v whose face x_k = v is a wire (two excluded pairs)"""
    E = excluded(K, 3)
    return [[v for v in (0, 1) if sum(1 for e in E if e[k] == v) == 2] for k in range(3)]


def kind(K):
    E = excluded(K, 3)
    if len(E) == 4:
        return "parity"
    if len(E) == 3:
        return "three excluded"
    if len(E) == 2 and sum(a != b for a, b in zip(*E)) == 2:
        return "two excluded at distance two"
    return "no wire face"


BOUND = {"no wire face": 0, "two excluded at distance two": 1, "three excluded": 2}


# ---------------------------------------------------------------- gadgets
def canon(m, edges, legs):
    """canonical form of a multigraph on copies 0..m-1 with leg counts; edges as sorted pairs"""
    best = None
    for p in itertools.permutations(range(m)):
        e = tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges))
        l = tuple(legs[p.index(v)] for v in range(m))
        key = (l, e)
        if best is None or key < best:
            best = key
    return best


def matchings(items):
    if not items:
        yield []
        return
    a = items[0]
    for j in range(1, len(items)):
        for m in matchings(items[1:j] + items[j + 1:]):
            yield [(a, items[j])] + m


def connected(m, edges):
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return len(seen) == m


def gadget_shapes(m, k, loops=False):
    """all connected gadgets with m copies and k legs up to isomorphism, as (legs per copy, internal edges)"""
    shapes = {}
    for combo in itertools.combinations_with_replacement(range(m), k):
        cnt = Counter(combo)
        if max(cnt.values()) > 3:
            continue
        legs = [cnt[v] for v in range(m)]
        slots = [(v, s) for v in range(m) for s in range(legs[v], 3)]
        for mt in matchings(slots):
            if not loops and any(a[0] == b[0] for a, b in mt):
                continue
            edges = [(a[0], b[0]) for a, b in mt]
            if m > 1 and not connected(m, edges):
                continue
            key = canon(m, edges, legs)
            if key not in shapes:
                shapes[key] = (legs, mt)
    return list(shapes.values())


class Net:
    """a gadget with its slot structure: copies 0..m-1, slot (v, s); legs first"""
    def __init__(self, m, legs, mt):
        self.m, self.legs, self.mt = m, legs, mt
        self.var = {}
        k = 0
        self.leg_slots = []
        for v in range(m):
            for s in range(legs[v]):
                self.var[(v, s)] = k; self.leg_slots.append((v, s)); k += 1
        self.nlegs = k
        for a, b in mt:
            self.var[a] = self.var[b] = k; k += 1
        self.nvars = k
        self.copy_vars = [tuple(self.var[(v, s)] for s in range(3)) for v in range(m)]

    def satisfiable(self, rels, fixed):
        """fixed: dict var -> value; backtracking over the rest"""
        order = [x for x in range(self.nvars) if x not in fixed]
        val = dict(fixed)
        cons = [(self.copy_vars[v], rels[v]) for v in range(self.m)]
        watch = defaultdict(list)
        for i, (vs, _) in enumerate(cons):
            for x in vs:
                watch[x].append(i)
        def ok_now(x):
            for i in watch[x]:
                vs, R = cons[i]
                if all(y in val for y in vs) and tuple(val[y] for y in vs) not in R:
                    return False
            return True
        for i, (vs, R) in enumerate(cons):
            if all(y in val for y in vs) and tuple(val[y] for y in vs) not in R:
                return False
        def rec(j):
            if j == len(order):
                return True
            x = order[j]
            for b in (0, 1):
                val[x] = b
                if ok_now(x) and rec(j + 1):
                    return True
            del val[x]
            return False
        return rec(0)

    def leg_relation(self, rels):
        return frozenset(l for l in cube(self.nlegs) if self.satisfiable(rels, dict(enumerate(l))))


def leg_tuple_index(net):
    """legs in order (copy, slot); the relation is on that order"""
    return net.leg_slots


# ---------------------------------------------------------------- structure (cactus, odd wire cycles, legs beyond bridges)
def structure_ok(net, rels, l):
    m, mt = net.m, net.mt
    edges = list(range(len(mt)))
    ends = [(a[0], b[0]) for a, b in mt]
    # bridges: edge e is a bridge iff removing it disconnects
    def comps(skip):
        adj = defaultdict(list)
        for j, (a, b) in enumerate(ends):
            if j != skip:
                adj[a].append(b); adj[b].append(a)
        comp = {}
        for s in range(m):
            if s in comp:
                continue
            comp[s] = s; st = [s]
            while st:
                u = st.pop()
                for w in adj[u]:
                    if w not in comp:
                        comp[w] = s; st.append(w)
        return comp
    bridges = [j for j in edges if len(set(comps(j).values())) > 1]
    nonbridge_deg = Counter()
    for j in edges:
        if j not in bridges:
            a, b = ends[j]; nonbridge_deg[a] += 1; nonbridge_deg[b] += 1
    cactus = all(d <= 2 for d in nonbridge_deg.values())
    # legs on both sides of every bridge, and forced values: each side allows exactly one value, opposite
    forced, sides_ok = {}, True
    for j in bridges:
        comp = comps(j)
        a, b = ends[j]
        for side_root, other in ((a, b), (b, a)):
            side = {v for v in range(m) if comp[v] == comp[side_root]}
            if not any(net.legs[v] for v in side):
                sides_ok = False
            # allowed values of the bridge seen from this side: solve the side with the bridge free
            sub = SideNet(net, side, j)
            allowed = [x for x in (0, 1) if sub.sat(rels, l, x)]
            forced[(j, side_root)] = allowed
        if not (len(forced[(j, a)]) == 1 and len(forced[(j, b)]) == 1 and forced[(j, a)] != forced[(j, b)]):
            sides_ok = False
    # cycles: blocks that are cycles; for each, faces on the two cycle slots must be wires, odd number unequal
    nb = [j for j in edges if j not in bridges]
    adj = defaultdict(list)
    for j in nb:
        a, b = ends[j]; adj[a].append((b, j)); adj[b].append((a, j))
    seen_e, cycles_ok = set(), True
    for j0 in nb:
        if j0 in seen_e:
            continue
        # walk the cycle containing j0 (every vertex has non-bridge degree 2 in a cactus)
        cyc, (u, w) = [j0], ends[j0]
        prev, cur = j0, w
        while cur != u:
            nxt = [(x, jj) for (x, jj) in adj[cur] if jj != prev]
            if len(nxt) != 1:
                return False
            x, jj = nxt[0]; cyc.append(jj); prev, cur = jj, x
        seen_e.update(cyc)
        parity = 0
        for v in {ends[jj][0] for jj in cyc} | {ends[jj][1] for jj in cyc}:
            slots = [(v, s) for s in range(3)]
            cyc_slots = [sl for sl in slots if sl in net.var and net.var[sl] >= net.nlegs and
                         (net.var[sl] - net.nlegs) in cyc]
            if len(cyc_slots) == 1 and ends[cyc[0]] == (v, v):
                return False
            third = [sl for sl in slots if sl not in cyc_slots]
            if len(cyc_slots) != 2 or len(third) != 1:
                return False
            t = third[0]; tv = net.var[t]
            if tv < net.nlegs:
                tval = l[tv]
            else:
                j = tv - net.nlegs
                if j not in bridges:
                    return False
                a, b = ends[j]
                far = b if a == v else a
                tval = forced[(j, far)][0] if len(forced[(j, far)]) == 1 else None
                if tval is None:
                    return False
            R = rels[v]
            pos = [s for (vv, s) in cyc_slots]
            tpos = t[1]
            face = set()
            for x in (0, 1):
                for y in (0, 1):
                    tup = [None] * 3
                    tup[pos[0]], tup[pos[1]], tup[tpos] = x, y, tval
                    if tuple(tup) in R:
                        face.add((x, y))
            if face == {(0, 0), (1, 1)}:
                pass
            elif face == {(0, 1), (1, 0)}:
                parity ^= 1
            else:
                cycles_ok = False
        if parity != 1:
            cycles_ok = False
    return cactus and sides_ok and cycles_ok


class SideNet:
    """the side of bridge j containing the copies `side`, with the bridge as a free variable"""
    def __init__(self, net, side, j):
        self.net, self.side, self.j = net, side, j

    def sat(self, rels, l, x):
        net = self.net
        fixed = {i: l[i] for i in range(net.nlegs) if net.leg_slots[i][0] in self.side}
        fixed[net.nlegs + self.j] = x
        # restrict to the side's copies
        cons = [(net.copy_vars[v], rels[v]) for v in self.side]
        vars_ = sorted({y for vs, _ in cons for y in vs} - set(fixed))
        val = dict(fixed)
        def check():
            return all(tuple(val[y] for y in vs) in R for vs, R in cons if all(y in val for y in vs))
        def rec(k):
            if not check():
                return False
            if k == len(vars_):
                return True
            for b in (0, 1):
                val[vars_[k]] = b
                if rec(k + 1):
                    return True
            del val[vars_[k]]
            return False
        return rec(0)


# ---------------------------------------------------------------- run
def main(write):
    # 0 dependencies
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})

    K34 = knots(3)
    types = Counter(kind(K) for K in K34)
    sv_ok = True
    for K in K34:
        sv = strong_values(K)
        t = kind(K)
        counts = [len(x) for x in sv]
        if t == "parity":
            sv_ok &= counts == [2, 2, 2]
        elif t == "three excluded":
            sv_ok &= counts == [1, 1, 1]
        elif t == "two excluded at distance two":
            sv_ok &= sorted(counts) == [0, 0, 1]
        else:
            sv_ok &= counts == [0, 0, 0]
    report("1 knots and types", len(K34) == 34 and dict(types) == {"no wire face": 12, "two excluded at distance two": 12,
                                                                    "three excluded": 8, "parity": 2} and sv_ok,
           {"knots": len(K34), "types": dict(types), "strong values as stated": sv_ok})

    # 2 symmetry and orientation
    stabs3 = Counter()
    transposition_in_all = True
    for K in K34:
        st = stabilizer(K, 3)
        stabs3[len(st)] += 1
        transposition_in_all &= any(sum(p[i] != i for i in range(3)) == 2 for p in st)
    def rotations(cyc):
        n = len(cyc)
        rots = []
        for r in range(n):
            p = [None] * n
            for i in range(n):
                p[cyc[i]] = cyc[(i + r) % n]
            rots.append(tuple(p))
        return set(rots)
    cyc3 = [c for c in itertools.permutations(range(3)) if c[0] == 0]
    orient3 = sum(1 for K in K34 if any(set(stabilizer(K, 3)) <= rotations(c) for c in cyc3))
    K4 = knots(4)
    cyc4 = [c for c in itertools.permutations(range(4)) if c[0] == 0]
    stab4 = Counter()
    orient4, orient4_trivial = 0, 0
    for K in K4:
        st = stabilizer(K, 4)
        stab4[len(st)] += 1
        if any(set(st) <= rotations(c) for c in cyc4):
            orient4 += 1
            orient4_trivial += len(st) == 1
    out_orient = {"three-bit stabilizer sizes": dict(stabs3), "every three-bit stabilizer has a transposition": transposition_in_all,
                  "three-bit knots that orient a vertex": orient3, "four-bit knots": len(K4),
                  "four-bit stabilizer sizes": dict(sorted(stab4.items())),
                  "four-bit knots that orient a vertex": orient4, "of which trivial symmetry": orient4_trivial}
    report("2 symmetry and orientation", transposition_in_all and orient3 == 0 and dict(stabs3) == {6: 7, 2: 27}
           and len(K4) == 742 and orient4 > 0, out_orient)
    ORIENT4 = orient4

    # 3 exhaustive census, m = 3 and 5
    census = {}
    worst = Counter()
    rebuilt_nonparity, parity_ok, two_leg_rule, decrease = [], True, True, True
    arrows = defaultdict(set)
    excluded_cases = []
    index = {}
    for i, K in enumerate(K34):
        for P in placements(K, 3):
            index[P] = i
    for m in (3, 5):
        shapes = gadget_shapes(m, 3)
        census[m] = len(shapes)
        for legs, mt in shapes:
            net = Net(m, legs, mt)
            two_legs = max(legs) >= 2
            for i, K in enumerate(K34):
                t = kind(K)
                P = placements(K, 3)
                for choice in itertools.product(P, repeat=m):
                    R = net.leg_relation(choice)
                    ex = 8 - len(R)
                    if t == "parity":
                        parity_ok &= R in index and index[R] == i
                        continue
                    worst[(t, two_legs)] = max(worst[(t, two_legs)], ex)
                    if R in index:
                        if index[R] == i:
                            rebuilt_nonparity.append((m, i))
                        arrows[i].add(index[R])
                        decrease &= len(excluded(K34[index[R]], 3)) < len(excluded(K, 3))
                    if ex >= len(excluded(K, 3)) or ex > BOUND[t] or (not two_legs and ex > 1):
                        two_leg_rule = False
                    if ex:
                        for l in set(cube(3)) - R:
                            excluded_cases.append((m, legs, mt, choice, l))
    attained = {f"{t}, {'a copy with two legs' if tl else 'legs on distinct copies'}": v for (t, tl), v in sorted(worst.items())}
    # longest chain in the flow
    def depth(i):
        return 1 + max((depth(j) for j in arrows[i]), default=0)
    longest = max(depth(i) for i in range(34) if kind(K34[i]) != "parity")
    report("3 exhaustive census (3 and 5 copies)",
           parity_ok and not rebuilt_nonparity and two_leg_rule and decrease
           and all(max(worst[(t, True)], worst[(t, False)]) == b for t, b in BOUND.items()),
           {"gadget shapes": census, "parity rebuilt by every gadget": parity_ok, "non-parity rebuilt": rebuilt_nonparity,
            "bounds hold": two_leg_rule, "largest excluded count attained": attained,
            "flow arrows decrease excluded count": decrease,
            "flow": {i: sorted(v) for i, v in sorted(arrows.items())},
            "longest chain of constrained levels": longest})

    # 4 structure behind every excluded tuple
    struct_bad = []
    for (m, legs, mt, choice, l) in excluded_cases:
        net = Net(m, legs, mt)
        if not structure_ok(net, choice, l):
            struct_bad.append((m, legs, l))
    report("4 cactus, odd wire cycles, legs beyond bridges", not struct_bad and len(excluded_cases) > 0,
           {"excluded tuples examined": len(excluded_cases), "violations": struct_bad[:5]})

    # 5 random larger gadgets
    rng = random.Random(20261029)
    rand_bad, rand_n, rand_max = [], 0, Counter()
    for m in (7, 9, 11):
        made = 0
        while made < 60:
            combo = sorted(rng.choice(range(m)) for _ in range(3))
            cnt = Counter(combo)
            legs = [cnt[v] for v in range(m)]
            slots = [(v, s) for v in range(m) for s in range(legs[v], 3)]
            rng.shuffle(slots)
            mt = [(slots[2 * i], slots[2 * i + 1]) for i in range(len(slots) // 2)]
            if any(a[0] == b[0] for a, b in mt) or not connected(m, [(a[0], b[0]) for a, b in mt]):
                continue
            made += 1
            net = Net(m, legs, mt)
            for i, K in enumerate(K34):
                t = kind(K)
                P = placements(K, 3)
                choice = [rng.choice(P) for _ in range(m)]
                R = net.leg_relation(choice)
                ex = 8 - len(R)
                rand_n += 1
                if t == "parity":
                    if not (R in index and index[R] == i):
                        rand_bad.append((m, i, "parity"))
                    continue
                rand_max[t] = max(rand_max[t], ex)
                if ex >= len(excluded(K, 3)) or ex > BOUND[t] or (max(legs) < 2 and ex > 1):
                    rand_bad.append((m, i, ex))
    report("5 random gadgets of 7, 9 and 11 copies", not rand_bad,
           {"evaluations": rand_n, "violations": rand_bad[:5], "largest excluded count seen": dict(rand_max)})

    # 6 controls
    fired = {}
    loop_rebuilt = set()
    for m in (3,):
        for legs, mt in gadget_shapes(m, 3, loops=True):
            if not any(a[0] == b[0] for a, b in mt):
                continue
            net = Net(m, legs, mt)
            for i, K in enumerate(K34):
                if kind(K) == "parity":
                    continue
                for choice in itertools.product(placements(K, 3), repeat=m):
                    R = net.leg_relation(choice)
                    if R in index and index[R] == i:
                        loop_rebuilt.add(i)
    fired["self-gluing rebuilds a non-parity knot"] = sorted(loop_rebuilt)
    AE = frozenset({(0, 0, 0), (1, 1, 1)})
    ae_rebuilt = 0
    for legs, mt in gadget_shapes(3, 3):
        net = Net(3, legs, mt)
        if net.leg_relation([AE] * 3) == AE:
            ae_rebuilt += 1
    fired["all-equal rebuilt by native gadgets (shapes of 3 copies)"] = ae_rebuilt
    fired["mutated bound 'at most one for three excluded' violated"] = worst[("three excluded", True)] > 1
    report("6 controls fire", bool(loop_rebuilt) and ae_rebuilt > 0 and worst[("three excluded", True)] > 1, fired)

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status,
                   "checks": {"ok": ok_all, **out}, "seconds": round(time.time() - T0, 1),
                   "orienting four-bit knots": ORIENT4},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
