"""The birth-by-birth law: a move is one birth, and everything is read again after every move.

Ticket RING-IN-BALANCE-20261123-001C, written from the frozen definitions.

  1. Groups of the present roster as in step 1 of the round, with every knot allowed as a common
     knot (ANY) or only dead knots (DEAD). A group is open when no knot already made has all of its
     members among its parents.
  2. WAIT: a member in more open groups than h(u) is short and makes nothing. FIRST-COME: no member
     is short.
  3. Join moves: the open groups with no short member (FIRST-COME: every open group). Offshoot move:
     a member that is not short and holds more usable loose distinctions than the open groups without
     a short member that contain it (FIRST-COME: h(u) more than the open groups containing it).
  4. Fresh: RATION-3, max(3, 3 - p); PRESENT-ORD, max(d, 3 - p, 1) with d the open groups containing
     the new knot right after its birth, the new knot counted as a member before it receives anything.
     Closing exception (parity): a move that takes every loose distinction of the structure receives
     none.
  5. Generation: 0 for start knots, one more than the greatest of the parents for a new knot; a move's
     generation is the greatest generation of its parents. Orders: UNIFORM among all moves;
     BY-GENERATION among the moves of least generation with joins first (BG-JOINS), offshoots first
     (BG-OFFSHOOTS) or uniformly (BG-UNIFORM).
  Jammed at generation g: no move of generation g or less and some member of generation g or less short.

The roster is kept by parts; after a move only the parts that hold a knot whose met set changed,
the parents and the new knot are rebuilt (selfcheck_bbb.py compares this with a full recomputation).
"""

import copy
import random
from collections import Counter, defaultdict

import growth as g
import iso

INF = float("inf")
ORDERS = ["BG-JOINS", "BG-OFFSHOOTS", "BG-UNIFORM", "UNIFORM"]


class IndexedSet:
    __slots__ = ("items", "pos")

    def __init__(self):
        self.items = []
        self.pos = {}

    def add(self, x):
        if x in self.pos:
            raise AssertionError(("duplicate move", x))
        self.pos[x] = len(self.items)
        self.items.append(x)

    def remove(self, x):
        i = self.pos.pop(x)
        last = self.items.pop()
        if i < len(self.items):
            self.items[i] = last
            self.pos[last] = i

    def __len__(self):
        return len(self.items)

    def pick(self, rng):
        return self.items[rng.randrange(len(self.items))]


class PartState:
    __slots__ = ("pid", "members", "fam", "groups", "open", "short", "moves", "cnt")


class BBB:
    def __init__(self, start, rule="DEAD", ration="RATION-3", shortness="WAIT", order="BG-OFFSHOOTS",
                 seed=0, run_id="C2", check_start_copy=True):
        assert rule in ("ANY", "DEAD") and ration in ("RATION-3", "PRESENT-ORD")
        assert shortness in ("WAIT", "FIRST-COME") and order in ORDERS
        self.start, self.rule, self.ration, self.shortness, self.order, self.seed = start, rule, ration, shortness, order, seed
        self.S = g.make_start(start)
        self.rng = random.Random(g.seed_int(run_id, start, rule, ration, shortness, order, seed))
        self.check_start_copy = check_start_copy
        self.moves_made = 0
        self.made_by_gen = defaultdict(Counter)   # move generation -> Counter of 'J', 'O'
        self.joins = []                           # [move index, move generation, parents, least parent generation]
        self.jam_first = {}
        self.copies = []                          # parts the same as the start's roster (run's rule)
        self.copies_any = []                      # ... the same as the start's roster read with ANY
        self.end = None
        S = self.S
        self._compute_metc()
        mem = set(S.members)
        fam = set(self.metc.values())
        self.start_size = len(mem)
        self.start_h = sorted(S.h(u) for u in mem)
        self.start_graph = g.roster_graph(S, mem, fam)
        self.start_hash = iso.graph_hash(self.start_graph)
        self.start_graph_any = g.roster_graph(S, mem, g.roster_family(S, mem))
        self.start_hash_any = iso.graph_hash(self.start_graph_any)
        self._build_all()

    def _compute_metc(self):
        self.metc = {}
        for x in range(self.S.nknots()):
            m = self._met(x)
            if m:
                self.metc[x] = m

    def _build_all(self):
        self.part_of = {}
        self.parts = {}
        self.next_pid = 0
        self.reg_all = IndexedSet()
        self.reg = defaultdict(IndexedSet)        # (generation, 'J' or 'O') -> moves
        self.move_gen_count = Counter()
        self.short_gen_count = Counter()
        for comp in self._partition(set(self.S.members)):
            self._build(comp)

    @classmethod
    def recomputed(cls, b):
        """A fresh computation of every met set, part, group and move on b's present structure."""
        r = cls.__new__(cls)
        r.S, r.rule, r.shortness, r.check_start_copy = b.S, b.rule, b.shortness, False
        r._compute_metc()
        r._build_all()
        return r

    # ------------------------------------------------------------------ roster bookkeeping
    def eligible(self, x):
        if self.rule == "ANY":
            return True
        return x not in self.S.members and self.S.nbar[x] == 0

    def _met(self, x):
        if not self.eligible(x):
            return None
        mem = self.S.members
        ys = [y for y in self.S.nbrs[x] if y in mem]
        return frozenset(ys) if len(ys) >= 2 else None

    def _partition(self, U):
        par = {u: u for u in U}

        def find(u):
            while par[u] != u:
                par[u] = par[par[u]]
                u = par[u]
            return u

        S = self.S
        for u in U:
            for x in S.nbrs[u]:
                M = self.metc.get(x)
                if M:
                    for y in M:
                        if y not in par:
                            raise AssertionError(("met set leaves the rebuilt region", x, M))
                        a, b = find(u), find(y)
                        if a != b:
                            par[a] = b
        comps = defaultdict(set)
        for u in U:
            comps[find(u)].add(u)
        return sorted((frozenset(c) for c in comps.values()), key=min)

    def _is_open(self, G):
        S = self.S
        u0 = min(G, key=lambda u: (len(S.children[u]), u))
        for c in S.children[u0]:
            if G.issubset(S.parents[c]):
                return False
        return True

    def _build(self, members):
        S = self.S
        fam = set()
        for u in members:
            for x in S.nbrs[u]:
                M = self.metc.get(x)
                if M is not None:
                    fam.add(M)
        groups = g.compute_groups(fam)
        opn = [G for G in groups if self._is_open(G)]
        cnt = Counter()
        for G in opn:
            for u in G:
                cnt[u] += 1
        if self.shortness == "WAIT":
            short = frozenset(u for u in members if cnt[u] > S.h(u))
        else:
            short = frozenset()
        joins = [G for G in opn if not (G & short)]
        cj = Counter()
        for G in joins:
            for u in G:
                cj[u] += 1
        offs = [u for u in sorted(members) if u not in short and S.h(u) > cj[u]]
        moves = [(("J", tuple(sorted(G))), max(S.gen[u] for u in G)) for G in joins]
        moves += [(("O", (u,)), S.gen[u]) for u in offs]
        P = PartState()
        P.pid = self.next_pid
        self.next_pid += 1
        P.members, P.fam, P.groups, P.open, P.short, P.moves, P.cnt = frozenset(members), fam, groups, opn, short, moves, cnt
        self.parts[P.pid] = P
        for u in members:
            self.part_of[u] = P.pid
        for key, gen in moves:
            self.reg_all.add(key)
            self.reg[(gen, key[0])].add(key)
            self.move_gen_count[gen] += 1
        for u in short:
            self.short_gen_count[S.gen[u]] += 1
        if self.check_start_copy:
            self._check_copy(P)
        return P

    def _drop(self, pid):
        P = self.parts.pop(pid)
        S = self.S
        for key, gen in P.moves:
            self.reg_all.remove(key)
            self.reg[(gen, key[0])].remove(key)
            self.move_gen_count[gen] -= 1
            if not self.move_gen_count[gen]:
                del self.move_gen_count[gen]
        for u in P.short:
            gu = S.gen[u]
            self.short_gen_count[gu] -= 1
            if not self.short_gen_count[gu]:
                del self.short_gen_count[gu]
        for u in P.members:
            if self.part_of.get(u) == pid:
                del self.part_of[u]

    def _update(self, c, P):
        S = self.S
        changed = {c} | set(P)
        for p in P:
            changed |= S.nbrs[p]
        touched = set(P)
        touched.add(c)
        for x in changed:
            old = self.metc.pop(x, None)
            if old:
                touched |= old
            new = self._met(x)
            if new:
                self.metc[x] = new
                touched |= new
        pids = sorted({self.part_of[m] for m in touched if m in self.part_of})
        U = set()
        for pid in pids:
            U |= self.parts[pid].members
            self._drop(pid)
        U |= touched
        U = {m for m in U if m in S.members}
        for comp in self._partition(U):
            self._build(comp)

    def _check_copy(self, P):
        S = self.S
        if len(P.members) != self.start_size or min(P.members) < S.n_start:
            return
        if sorted(S.h(u) for u in P.members) != self.start_h or not g.past_start(S, P.members):
            return
        gr = g.roster_graph(S, P.members, P.fam)
        hh = iso.graph_hash(gr)
        rec = {"move": self.moves_made, "generations": sorted(Counter(S.gen[u] for u in P.members).items())}
        if hh == self.start_hash and iso.isomorphism(gr, self.start_graph) is not None:
            self.copies.append(rec)
        if self.rule != "ANY" and hh == self.start_hash_any and iso.isomorphism(gr, self.start_graph_any) is not None:
            self.copies_any.append(rec)

    # ------------------------------------------------------------------ moves
    def least_move_gen(self):
        return min(self.move_gen_count) if self.move_gen_count else INF

    def least_short_gen(self):
        return min(self.short_gen_count) if self.short_gen_count else INF

    def jam_check(self):
        gm, gs = self.least_move_gen(), self.least_short_gen()
        if gs < gm:
            hi = gm if gm != INF else gs + 1
            for gg in range(gs, hi):
                if gg not in self.jam_first:
                    self.jam_first[gg] = {"move": self.moves_made, "made_J": self.made_by_gen[gg]["J"],
                                          "made_O": self.made_by_gen[gg]["O"], "no_move_at_all": gm == INF}
        return gm

    def moves_of_gen(self, gm):
        J = self.reg.get((gm, "J"))
        O = self.reg.get((gm, "O"))
        return (list(J.items) if J else []) + (list(O.items) if O else [])

    def choose(self, gm):
        if self.order == "UNIFORM":
            return self.reg_all.pick(self.rng)
        J = self.reg.get((gm, "J"))
        O = self.reg.get((gm, "O"))
        nJ = len(J) if J else 0
        nO = len(O) if O else 0
        if self.order == "BG-JOINS":
            return (J if nJ else O).pick(self.rng)
        if self.order == "BG-OFFSHOOTS":
            return (O if nO else J).pick(self.rng)
        i = self.rng.randrange(nJ + nO)
        return J.items[i] if i < nJ else O.items[i - nJ]

    def apply(self, key):
        S = self.S
        kind, P = key
        assert key in self.reg_all.pos, key
        gen_move = max(S.gen[u] for u in P)
        self.moves_made += 1
        self.made_by_gen[gen_move][kind] += 1
        if kind == "J":
            self.joins.append([self.moves_made, gen_move, len(P), min(S.gen[u] for u in P)])
        c = S.birth(P)
        p = len(P)
        if S.loose_total == 0:                 # closing exception (parity): takes every loose distinction
            f = 0
            self._update(c, P)
        elif self.ration == "RATION-3":
            f = max(3, 3 - p)
            S.give_fresh(c, f, 0)
            self._update(c, P)
        else:                                   # PRESENT-ORD
            S.members.add(c)                    # counted as a member before it receives anything
            self._update(c, P)
            part = self.parts[self.part_of[c]]
            d = sum(1 for G in part.open if c in G)
            f = max(d, 3 - p, 1)
            S.give_fresh(c, f, 0)
            pid = self.part_of[c]
            mem = self.parts[pid].members
            self._drop(pid)
            self._build(mem)
        return c, f

    def run(self, max_moves=600, max_knots=4000):
        while True:
            gm = self.jam_check()
            if self.moves_made >= max_moves:
                self.end = "moves"
                break
            if self.S.nknots() >= max_knots:
                self.end = "knots"
                break
            if gm == INF:
                self.end = "stopped" if not self.S.members else "jammed"
                break
            self.apply(self.choose(gm))
        return self.end

    # ------------------------------------------------------------------ description
    def describe(self):
        S = self.S
        lines = []
        for u in sorted(S.members):
            P = self.parts[self.part_of[u]]
            og = [sorted(G) for G in P.open if u in G]
            lines.append(f"    member {u:3d}  gen {S.gen[u]}  h {S.h(u)}  open groups {og}  "
                         f"{'SHORT' if u in P.short else ''}")
        gm = self.least_move_gen()
        mv = sorted(self.moves_of_gen(gm)) if gm != INF else []
        lines.append(f"    least move generation {gm}; its moves: {mv}")
        return lines

    def summary(self):
        S = self.S
        return {
            "start": self.start, "rule": self.rule, "order": self.order, "seed": self.seed, "end": self.end,
            "moves": self.moves_made, "knots": S.nknots(),
            "made_by_gen": {str(k): dict(v) for k, v in sorted(self.made_by_gen.items())},
            "joins": self.joins,
            "jam_first": {str(k): v for k, v in sorted(self.jam_first.items())},
            "start_copies": self.copies[:20], "start_copies_n": len(self.copies),
            "start_copies_any_reading": self.copies_any[:20], "start_copies_any_reading_n": len(self.copies_any),
        }


# ---------------------------------------------------------------------- C3: every order
def state_graph(b):
    S = b.S
    return g.structure_graph(S, range(S.nknots()), lambda k: S.gen[k])


def outcome(b):
    S = b.S
    gm, gs = b.least_move_gen(), b.least_short_gen()
    gens = Counter(S.gen)
    g2_multi = sum(1 for k in range(S.nknots()) if S.gen[k] == 2 and len(S.parents[k]) >= 2)
    g1_multi = sum(1 for k in range(S.nknots()) if S.gen[k] == 1 and len(S.parents[k]) >= 2)
    return {"jam_at_gen1": gs <= 1 < gm, "least_short_gen": gs if gs != INF else None,
            "least_move_gen": gm if gm != INF else None,
            "gen0_moves": gens[1], "gen0_joins": g1_multi,
            "gen1_moves": gens[2], "gen1_joins": g2_multi}


def every_order(start="D2(4,3)", rule="DEAD", max_gen=1):
    root = BBB(start, rule, "RATION-3", "WAIT", "BG-UNIFORM", check_start_copy=False)
    classes = defaultdict(list)
    nodes = []

    def visit(b):
        gr = state_graph(b)
        h = iso.graph_hash(gr)
        for gr2, nid in classes[h]:
            if iso.isomorphism(gr, gr2) is not None:
                return nid
        nid = len(nodes)
        nodes.append(None)
        classes[h].append((gr, nid))
        gm = b.least_move_gen()
        if gm == INF or gm > max_gen:
            nodes[nid] = {"terminal": True, "outcome": outcome(b), "orders": 1, "knots": b.S.nknots()}
        else:
            kids = []
            for key in sorted(b.moves_of_gen(gm)):
                b2 = copy.deepcopy(b)
                b2.apply(key)
                kids.append(visit(b2))
            nodes[nid] = {"terminal": False, "children": kids, "move_gen": gm,
                          "orders": sum(nodes[k]["orders"] for k in kids), "knots": b.S.nknots()}
        return nid

    visit(root)
    return nodes
