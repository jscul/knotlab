"""Rule R (a short knot pays the rest with shared distinctions) on full holdings, beside ordinary growth.

Frozen definitions: research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/preregistration.md; readings in deviations.md.

Recorded code reused read-only (imported by path, never changed):
  * experiments/ORDINARY-DYNAMICS-20261120-001A/.../end_operator.py (End, maximal_blocks, _proposals, proposals, step),
    used here as `EO`: the reference for groups, lookahead and the ordinary round;
  * experiments/REVIEW-LEADS-20261123-001A/.../lib.py (recorded sources, `p3_draws`, `grow`, `incidence_graph`,
    `passes`, `first_failing_stage`, `growth_kind`), used here as `lib`.

`Growth` keeps full holdings (which knot holds which distinction, with holder counts) and plays one complete round at a
time under rule "R" or rule "ordinary".  On a round with no short knot the two rules make the same groups, parents,
lookahead demand and fresh counts, except that R decides a parity closing by elimination over GF(2) on all old knots
instead of by the recorded shortcut (a sole birth); gate G checks that they agree on ordinary histories.

Groups are computed by `Groups`, an exact re-implementation of the recorded group rule that finds maximal groups on
classes of interchangeable knots (knots with the same witnessed sets; they enter every maximal group together) with
`networkx.find_cliques`.  The recorded pivot search is too slow on rounds with hundreds of sibling births.  In check
mode every round small enough is also computed by the recorded code and compared (gate G).
"""
import copy
import gzip
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUT = ROOT / "artifacts" / TICKET / HERE.name
LEADS = ROOT / "experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test"
sys.path.insert(0, str(LEADS))
import lib  # noqa: E402  (imports the recorded end_operator as lib.EO; never call lib.dump: its OUT is that ticket's)

EO = lib.EO
LAWS = ("parity", "nae")
CHECK_LIMIT = 400  # in check mode, rounds with at most this many births (or live knots) are also run by the recorded code


# ----------------------------------------------------------------------------------------------------------------------
# The group rule (exact; checked against end_operator).
# ----------------------------------------------------------------------------------------------------------------------
def maximal_blocks(blocks):
    """The value of end_operator.maximal_blocks: inclusion-maximal sets of size at least two, as sorted tuples, sorted."""
    cand = {frozenset(b) for b in blocks if len(b) >= 2}
    by_elem = defaultdict(list)
    for b in cand:
        for v in b:
            by_elem[v].append(b)
    kept = []
    for b in cand:
        v = min(b, key=lambda x: len(by_elem[x]))
        if any(b < o for o in by_elem[v]):
            continue
        kept.append(tuple(sorted(b)))
    return tuple(sorted(kept))


def _bits(m):
    while m:
        low = m & -m
        yield low.bit_length() - 1
        m ^= low


_BK = None
C_MIN = 64  # candidate classes above which the C search is used
USE_C = True  # the C search (bk.c) and the Python search are the same algorithm; gate G compares both


def _bk_lib():
    """Compile bk.c (once) into the artifact folder and load it."""
    global _BK
    if _BK is None:
        import ctypes
        import subprocess
        src = HERE / "bk.c"
        so = OUT / "build" / "bk.so"
        if not so.exists() or so.stat().st_mtime < src.stat().st_mtime:
            so.parent.mkdir(parents=True, exist_ok=True)
            tmp = so.with_suffix(f".{__import__('os').getpid()}.so")
            subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
            tmp.replace(so)
        lib_ = ctypes.CDLL(str(so))
        p = ctypes.c_void_p
        lib_.maximal_groups.argtypes = [ctypes.c_int, ctypes.c_int, p, p, p, p, p, p, ctypes.c_long, ctypes.c_long]
        lib_.maximal_groups.restype = ctypes.c_long
        _BK = lib_
    return _BK


def _maximal_groups_c(adj, ckeys, csize, bmask, limit=None):
    """adj: list of int bit sets over the m candidate classes; ckeys: witnessed sets of each; bmask: {set: bit set}.
    Returns the maximal unheld groups as lists of candidate positions, or None when there are more than `limit`."""
    import numpy as np
    m = len(adj)
    if m == 0:
        return []
    W = (m + 63) // 64
    def rows(ints):
        a = np.zeros((len(ints), W), dtype=np.uint64)
        for r, x in enumerate(ints):
            raw = x.to_bytes(W * 8, "little")
            a[r] = np.frombuffer(raw, dtype=np.uint64)
        return a
    blocks = sorted({bi for k in ckeys for bi in k})
    bpos = {bi: i for i, bi in enumerate(blocks)}
    A = rows(adj)
    B = rows([bmask[bi] for bi in blocks])
    keys = np.array([bpos[bi] for k in ckeys for bi in k], dtype=np.int32)
    koff = np.zeros(m + 1, dtype=np.int32)
    koff[1:] = np.cumsum([len(k) for k in ckeys])
    size = np.array(csize, dtype=np.int32)
    cap = 1 << 16
    lib_ = _bk_lib()
    while True:
        out = np.zeros(cap, dtype=np.int32)
        n = lib_.maximal_groups(m, W, A.ctypes.data, B.ctypes.data, keys.ctypes.data, koff.ctypes.data,
                                size.ctypes.data, out.ctypes.data, cap, -1 if limit is None else limit)
        if n == -3:
            return None
        if n == -1:
            cap *= 4
            continue
        assert n >= 0, "the C search failed to allocate"
        break
    res, i = [], 0
    while i < n:
        k = int(out[i])
        res.append([int(x) for x in out[i + 1:i + 1 + k]])
        i += 1 + k
    return res


class Groups:
    """The groups of an end (live knots `nodes`, maximal witnessed sets `blocks`): every inclusion-maximal set of at
    least three pairwise adjacent knots held by no one witnessed set, then every adjacent pair in none of them, in the
    recorded order (sorted large groups, then pairs in sorted order).

    Exact re-implementation of end_operator._proposals.  (i) Knots with the same witnessed sets are true twins (same
    closed neighbourhood), so a maximal group contains all or none of each class.  (ii) A class that lies in only one
    witnessed set is in no unheld group (every group through it lies inside that set), and an unheld maximal group of
    the other classes cannot be extended by such a class (it would then lie inside that set); so the unheld maximal
    groups are found among the classes with two or more witnessed sets, by a Bron-Kerbosch search with pivot on bit
    sets, pruned (as the recorded search is) when the knots still possible lie inside one witnessed set or number
    fewer than three.  (iii) Uncovered pairs are counted from each class's neighbourhood."""

    def __init__(self, nodes, blocks, limit=None):
        """With `limit`, the search stops once more than `limit` maximal unheld groups are found; then
        self.exceeded is True and nothing else is computed (the total number of groups is then above `limit`)."""
        self.exceeded = False
        nodes = sorted(nodes)
        member = {v: [] for v in nodes}
        for bi, b in enumerate(blocks):
            for v in b:
                member[v].append(bi)
        classes = {}
        for v in nodes:
            key = tuple(member[v])
            if key:
                classes.setdefault(key, []).append(v)
        self.keys = list(classes)
        self.members = [classes[k] for k in self.keys]
        self.blocks = blocks
        size = [len(m) for m in self.members]
        cand = [i for i, k in enumerate(self.keys) if len(k) >= 2]
        pos = {c: j for j, c in enumerate(cand)}
        bmask = defaultdict(int)
        for c in cand:
            for bi in self.keys[c]:
                bmask[bi] |= 1 << pos[c]
        adj = []
        for c in cand:
            m = 0
            for bi in self.keys[c]:
                m |= bmask[bi]
            adj.append(m & ~(1 << pos[c]))
        csize = [size[c] for c in cand]
        ckeys = [self.keys[c] for c in cand]

        def weight(m):
            w = 0
            for j in _bits(m):
                w += csize[j]
                if w >= 3:
                    return w
            return w

        def held(m):
            j = (m & -m).bit_length() - 1
            for bi in ckeys[j]:
                if m & ~bmask[bi] == 0:
                    return True
            return False

        big = []
        if USE_C and len(cand) > C_MIN:
            found = _maximal_groups_c(adj, ckeys, csize, bmask, limit)
            if found is None:
                self.exceeded = True
                return
            big = [sorted(cand[j] for j in c) for c in found]
            stack = []
        else:
            stack = [(0, (1 << len(cand)) - 1, 0)]
        while stack:
            r, p, x = stack.pop()
            rp = r | p
            if not rp or weight(rp) < 3 or held(rp):
                continue
            if not p:
                if not x:
                    big.append(sorted(cand[j] for j in _bits(r)))
                    if limit is not None and len(big) > limit:
                        self.exceeded = True
                        return
                continue
            best, pivot = -1, None
            for u in _bits(p | x):
                c = (p & adj[u]).bit_count()
                if c > best:
                    best, pivot = c, u
            for v in _bits(p & ~adj[pivot]):
                bit = 1 << v
                stack.append((r | bit, p & adj[v], x & adj[v]))
                p &= ~bit
                x |= bit
        self.big = big
        # closed neighbourhood and covered set of each class, as bit sets over all classes
        nclass = len(self.keys)
        allmask = defaultdict(int)
        for i, k in enumerate(self.keys):
            for bi in k:
                allmask[bi] |= 1 << i
        covmask = [0] * nclass
        self.in_big = [0] * nclass
        for c in big:
            m = 0
            for i in c:
                m |= 1 << i
            for i in c:
                covmask[i] |= m
                self.in_big[i] += 1
        multi_size = {i: s for i, s in enumerate(size) if s > 1}
        self.size = size
        self.unc = []  # per class: bit set of the classes of its uncovered neighbours (own class included if uncovered)
        self.unc_n = []  # the number of knots in it
        total_pairs2 = 0
        for i, k in enumerate(self.keys):
            nb = 0
            for bi in k:
                nb |= allmask[bi]
            nb &= ~covmask[i]
            n = nb.bit_count() + sum(s - 1 for j, s in multi_size.items() if (nb >> j) & 1)
            self.unc.append(nb)
            self.unc_n.append(n)
            own = size[i] if not self.in_big[i] else 0
            total_pairs2 += size[i] * n - own
        assert total_pairs2 % 2 == 0
        self.total = len(big) + total_pairs2 // 2

    def explicit(self):
        bigs = sorted(tuple(sorted(v for i in c for v in self.members[i])) for c in self.big)
        pairs = []
        for i, nb in enumerate(self.unc):
            srt = sorted(w for j in _bits(nb) for w in self.members[j])
            for v in self.members[i]:
                pairs.extend((v, w) for w in srt if w > v)
        pairs.sort()
        return tuple(bigs) + tuple(pairs)

    def counts(self):
        cnt = Counter()
        for i, n in enumerate(self.unc_n):
            own = 0 if self.in_big[i] else 1
            c = self.in_big[i] + n - own
            for v in self.members[i]:
                cnt[v] += c
        return cnt


# ----------------------------------------------------------------------------------------------------------------------
# GF(2) span of the old knots: rows with distinct leading bits (an echelon basis), distinctions as bits of an int.
# ----------------------------------------------------------------------------------------------------------------------
def mask(ds):
    m = 0
    for d in ds:
        m |= 1 << d
    return m


class Span:
    """Echelon rows over GF(2): every row has a distinct leading (highest) bit.  A vector is in the span exactly when
    repeated cancellation of its leading bit by the row with that leading bit reaches zero."""

    def __init__(self):
        self.rows = {}

    def _reduce(self, v):
        rows = self.rows
        while v:
            r = rows.get(v.bit_length() - 1)
            if r is None:
                return v
            v ^= r
        return 0

    def add(self, v):
        v = self._reduce(v)
        if v:
            self.rows[v.bit_length() - 1] = v

    def contains(self, v):
        return self._reduce(v) == 0


# ----------------------------------------------------------------------------------------------------------------------
# One round, planned on full holdings.
# ----------------------------------------------------------------------------------------------------------------------
class Round:
    __slots__ = ("status", "parents", "inputs", "paid", "fresh", "demand", "implied", "elim", "shortages",
                 "residual", "groups", "opens", "blocks", "next_capped")

    def __init__(self, status, **kw):
        self.status = status
        for k in self.__slots__[1:]:
            setattr(self, k, kw.get(k))


class Growth:
    """A structure under one law and one rule, grown one complete round at a time.

    rule: "R" or "ordinary".  convention: "O" (oldest allowed shared distinction) or "N" (newest); only used by R.
    check: on rounds small enough also run the recorded code on the same end and compare (gate G).
    elim_always: under ordinary growth also run the elimination test on every parity birth (gate G)."""

    def __init__(self, stars, law, rule="R", convention="O", check=False, elim_always=False, bound_next=True):
        assert law in LAWS and rule in ("R", "ordinary") and convention in ("O", "N")
        self.law, self.rule, self.convention, self.check = law, rule, convention, check
        self.bound_next = bound_next  # stop the lookahead once the next round is certain to be capped
        self.stars = [tuple(s) for s in stars]
        self.holders = defaultdict(list)
        for k, s in enumerate(self.stars):
            assert len(set(s)) == len(s), "a knot holds a distinction twice"
            for d in s:
                self.holders[d].append(k)
        self.loose = {}
        for k, s in enumerate(self.stars):
            row = [d for d in s if len(self.holders[d]) == 1]
            if row:
                self.loose[k] = row
        self.top = max(self.holders) + 1
        self.span = None
        if law == "parity" and (rule == "R" or elim_always):
            self.span = Span()
            for s in self.stars:
                self.span.add(mask(s))
        self.n_at = [len(self.stars)]
        self.rounds = []         # per completed round: dict summary
        self.outcome = None      # None while alive; 'closed', 'stall', 'residual_stall', 'cap', 'horizon'
        self.last = None         # the last Round planned (also a failed one)
        self.check_log = Counter()

    def clone(self):
        return copy.deepcopy(self)

    # -- the present end, read from full holdings ----------------------------------------------------------------------
    def present_end(self):
        """(opens, raw witnessed sets): every knot's set of live knots it shares a distinction with."""
        opens = {k: len(self.loose[k]) for k in sorted(self.loose)}
        blocks = defaultdict(set)
        for k in opens:
            for d in self.stars[k]:
                for j in self.holders[d]:
                    if j != k:
                        blocks[j].add(k)
        return opens, [tuple(sorted(b)) for b in blocks.values()]

    def max_holders(self):
        return max(len(h) for h in self.holders.values())

    # -- planning ------------------------------------------------------------------------------------------------------
    def plan(self, max_births=None):
        """Plan the next round (R: the convention decides every shared payment).  Returns a Round; nothing changes."""
        if not self.loose:
            return Round("closed")
        opens, raw = self.present_end()
        blocks = maximal_blocks(raw)
        gr = Groups(list(opens), blocks, limit=max_births)
        if gr.exceeded:  # more than max_births groups: the recorded rule caps (before any stall)
            return Round("cap")
        small = self.check and len(opens) <= CHECK_LIMIT and gr.total <= CHECK_LIMIT
        if small:
            end = EO.End(opens, tuple(raw))
            assert end.blocks == blocks, "maximal witnessed sets differ from the recorded"
        if max_births is not None and gr.total > max_births:
            if small:
                try:
                    EO._proposals(end, max_births)
                    raise AssertionError("cap differs from the recorded")
                except EO._Cap:
                    pass
            return Round("cap")
        multi = gr.explicit()
        if small:
            assert multi == EO._proposals(end, None), "groups differ from the recorded"
            self.check_log["groups_compared"] += 1
        used = Counter(v for row in multi for v in row)
        short = tuple((k, used[k] - n) for k, n in opens.items() if used[k] > n)
        if short and self.rule == "ordinary":
            return Round("stall", shortages=short, groups=multi, opens=opens, blocks=blocks)
        parents = multi + tuple((k,) for k, n in opens.items() for _ in range(max(0, n - used[k])))
        if max_births is not None and len(parents) > max_births:
            return Round("cap", shortages=short)
        # allocation: loose distinctions first (in birth order, last listed first, as lib.grow), then shared payments
        pool = {k: list(v) for k, v in self.loose.items()}
        shared = {k: [d for d in sorted(self.stars[k]) if len(self.holders[d]) >= 2] for k, _ in short}
        paid_by = defaultdict(set)
        inputs, paid, residual = [], [], Counter()
        for i, ps in enumerate(parents):
            row, prow = [], []
            for p in ps:
                if pool.get(p):
                    row.append(pool[p].pop())
                    prow.append(False)
                    continue
                others = [q for q in ps if q != p]
                allowed = [d for d in shared[p] if d not in paid_by[p]
                           and not any(q in others for q in self.holders[d])]
                if not allowed:
                    residual[p] += 1
                    row.append(None)
                    prow.append(None)
                    continue
                d = allowed[0] if self.convention == "O" else allowed[-1]
                paid_by[p].add(d)
                row.append(d)
                prow.append(True)
            inputs.append(tuple(row))
            paid.append(tuple(prow))
        assert not any(pool.values()), "a loose distinction was left unspent"
        if residual:
            return Round("residual_stall", shortages=short, residual=tuple(sorted(residual.items())),
                         parents=parents, groups=multi, opens=opens, blocks=blocks)
        room = None if (max_births is None or not self.bound_next) else max_births - len(parents)
        r = self._finish(parents, inputs, paid, short, multi, opens, blocks, room)
        if small and not short and not r.next_capped:
            self._compare_recorded(end, r)
        return r

    def _finish(self, parents, inputs, paid, short, multi, opens, blocks, room=None):
        """Fresh counts.  `room`: the most births the next round may have under the cap.  When the next round is
        certain to have more groups than that (so the recorded cap rule will not take it), the lookahead search
        stops: the round's fresh counts are then lower bounds max(3 - p, 1) and the history ends with a cap."""
        nb = len(parents)
        implied, elim = [], []
        for row in inputs:
            e = self.span.contains(mask(row)) if self.span is not None else None
            elim.append(e)
            if self.law != "parity":
                implied.append(False)
            elif self.rule == "ordinary":
                implied.append(nb == 1)
            else:
                implied.append(bool(e))
        demand = self._demand(parents, inputs, room, implied)
        capped = demand is None
        if capped:
            demand = (0,) * nb
        fresh = tuple(0 if imp else max(demand[i], 3 - len(ps), 1)
                      for i, (ps, imp) in enumerate(zip(parents, implied, strict=True)))
        return Round("extend", parents=parents, inputs=tuple(inputs), paid=tuple(paid), fresh=fresh,
                     demand=None if capped else demand, implied=tuple(implied), elim=tuple(elim), shortages=short,
                     groups=multi, opens=opens, blocks=blocks, next_capped=capped)

    def lookahead_blocks(self, inputs):
        """Births provisionally live with one opening; each knot (old, or a birth) witnesses the births it shares a
        distinction with.  Returns the raw witnessed sets."""
        takers = defaultdict(list)
        for i, row in enumerate(inputs):
            for d in row:
                takers[d].append(i)
        blocks = defaultdict(set)
        for d, bs in takers.items():
            for h in self.holders[d]:
                blocks[("old", h)].update(bs)
            if len(bs) > 1:
                for b in bs:
                    blocks[("new", b)].update(x for x in bs if x != b)
        return [tuple(sorted(b)) for b in blocks.values()]

    def _demand(self, parents, inputs, room=None, implied=None):
        raw = self.lookahead_blocks(inputs)
        blocks = maximal_blocks(raw)
        gr = Groups(range(len(parents)), blocks, limit=room)
        if gr.exceeded:
            # Every birth with a fresh distinction is live next round, and the next end's witnessed sets are these
            # (fresh distinctions are loose).  With every birth live, the lookahead groups are the next round's groups.
            if not any(implied):
                return None
            live = [i for i, imp in enumerate(implied) if not imp]
            keep = set(live)
            nxt = Groups(live, maximal_blocks([tuple(v for v in b if v in keep) for b in raw]), limit=room)
            if nxt.exceeded:
                return None
            gr = Groups(range(len(parents)), blocks)
        cnt = gr.counts()
        demand = tuple(cnt[i] for i in range(len(parents)))
        if self.check and len(parents) <= CHECK_LIMIT:
            la = EO.End(dict.fromkeys(range(len(parents)), 1), tuple(raw))
            assert la.blocks == blocks
            ref = Counter(v for row in EO.proposals(la) for v in row)
            assert demand == tuple(ref[i] for i in range(len(parents))), "lookahead demand differs from the recorded"
            self.check_log["lookaheads_compared"] += 1
        return demand

    def _compare_recorded(self, end, r):
        """Gate G, round by round: the recorded operator on the same end (a round with no short knot)."""
        turn = EO.step(end, self.law)
        self.check_log["rounds_compared"] += 1
        assert turn.status == "extend", turn.status
        if not (turn.parents == r.parents and turn.demand == r.demand):
            raise AssertionError("R and the recorded operator differ on a round with no short knot")
        if any(x for prow in r.paid for x in prow):
            raise AssertionError("a payment on a round with no short knot")
        if tuple(turn.fresh) != r.fresh:
            self.check_log["fresh_differ_by_closing_test"] += 1
        else:
            self.check_log["fresh_equal"] += 1

    # -- applying ------------------------------------------------------------------------------------------------------
    def apply(self, r, keep_payments=False):
        assert r.status == "extend"
        base = len(self.stars)
        pay_holders = None
        if keep_payments:  # round-start holders of every paid distinction, per birth and parent (None: loose)
            pay_holders = [[tuple(self.holders[d]) if x else None for d, x in zip(row, prow, strict=True)]
                           for row, prow in zip(r.inputs, r.paid, strict=True)]
        newloose = {}
        for i, (row, f) in enumerate(zip(r.inputs, r.fresh, strict=True)):
            made = tuple(range(self.top, self.top + f))
            self.top += f
            k = base + i
            star = tuple(row) + made
            assert len(set(star)) == len(star), "a newborn holds a distinction twice"
            self.stars.append(star)
            for d in star:
                self.holders[d].append(k)
            if made:
                newloose[k] = list(made)
        self.loose = newloose
        if self.span is not None:
            for s in self.stars[base:]:
                self.span.add(mask(s))
        self.n_at.append(len(self.stars))
        self.rounds.append({
            "births": len(r.parents),
            "parents": [list(p) for p in r.parents],
            "fresh": list(r.fresh),
            "paid_births": sum(1 for prow in r.paid if any(prow)),
            "payments": sum(1 for prow in r.paid for x in prow if x),
            "short_knots": len(r.shortages or ()),
            "implied": sum(map(bool, r.implied)),
            "elim_vs_shortcut": (None if r.elim[0] is None else
                                 sum(1 for e in r.elim if bool(e) != (len(r.parents) == 1))),
            "fresh_lower_bound": bool(r.next_capped),
        })
        if keep_payments:
            self.rounds[-1]["pay_holders"] = pay_holders
        if not self.loose:
            self.outcome = "closed"
        elif r.next_capped:
            self.outcome = "cap"

    def run(self, horizon, cap, keep_payments=False):
        while self.outcome is None and len(self.rounds) < horizon:
            r = self.plan(max_births=max(0, cap - len(self.stars)))
            self.last = r
            if r.status == "extend":
                self.apply(r, keep_payments)
                if self.outcome == "cap" and len(self.rounds) == horizon:
                    self.outcome = None  # the last round: no next round is planned, so the history ends at the horizon
            else:
                self.outcome = r.status
        if self.outcome is None:
            self.outcome = "horizon"
        return self

    # -- every allowed choice of one round (R) ----------------------------------------------------------------------
    def allowed_choices(self, r):
        """Every allowed payment choice of a planned round with short knots (r: a Round of status 'extend' or
        'residual_stall'; its parents are the engine's).  Per short knot: which of its births get a shared distinction
        (its loose ones go to the others), and an injective choice of allowed distinctions for those births.
        Returns [(knot, [choice {birth index: distinction}, ...]), ...]."""
        per_knot = []
        for k, excess in r.shortages:
            births = [i for i, ps in enumerate(r.parents) if k in ps]
            shared = [d for d in sorted(self.stars[k]) if len(self.holders[d]) >= 2]
            allowed = {i: {d for d in shared if not any(q != k and q in r.parents[i] for q in self.holders[d])}
                       for i in births}
            options = []
            for chosen in combinations(births, excess):
                for ds in permutations(shared, excess):
                    if all(d in allowed[i] for i, d in zip(chosen, ds)):
                        options.append(dict(zip(chosen, ds)))
            per_knot.append((k, options))
        return per_knot

    def plan_with(self, r, choice):
        """The round r with a full choice {knot: {birth index: distinction}}; the other births of each short knot take
        its loose distinctions in birth order (last listed first)."""
        pool = {k: list(v) for k, v in self.loose.items()}
        inputs, paid = [], []
        for i, ps in enumerate(r.parents):
            row, prow = [], []
            for p in ps:
                if p in choice and i in choice[p]:
                    row.append(choice[p][i])
                    prow.append(True)
                else:
                    row.append(pool[p].pop())
                    prow.append(False)
            inputs.append(tuple(row))
            paid.append(tuple(prow))
        assert not any(pool.values())
        return self._finish(r.parents, inputs, paid, r.shortages, r.groups, r.opens, r.blocks, None)

    def births_per_round(self):
        return [x["births"] for x in self.rounds]


def growth_kind_births(births):
    """stalled only with no birth at all; bounded: births per round never above the largest of the first four; growing."""
    if not births:
        return "stalled"
    return "bounded" if max(births) <= max(births[:4]) else "growing"


def recorded_growth_kind(g):
    """The recorded lib.growth_kind on this history (any stall outcome reads as stalled)."""
    outcome = "stall" if g.outcome in ("stall", "residual_stall") else g.outcome
    return lib.growth_kind({"births": [[None] * b for b in g.births_per_round()], "outcome": outcome})


def first_failing_step(g):
    return lib.first_failing_stage(g.stars, g.n_at)


def ordinary_reference(stars, law, horizon, cap):
    """The recorded ordinary driver (lib.grow) without a clock."""
    return lib.grow(stars, law, horizon, cap, time_limit=None)


def distinctions_at(stars, n):
    return len({d for s in stars[:n] for d in s})


def small_prefix(stars, n_at, law, limit=22):
    """Stars up to the stage after the last stage with at most `limit` distinctions (for test (a)), or None."""
    last = None
    for t in range(len(n_at)):
        if distinctions_at(stars, n_at[t]) <= limit:
            last = t
        else:
            break
    if last is None or len(n_at) < 2:
        return None
    end = min(last + 1, len(n_at) - 1)  # every stage small: the whole history
    return {"law": law, "n_at": list(n_at[:end + 1]), "stars": [list(s) for s in stars[:n_at[end]]]}


def dump(path, rows, mode="w"):
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, mode + "t") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def load(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]
