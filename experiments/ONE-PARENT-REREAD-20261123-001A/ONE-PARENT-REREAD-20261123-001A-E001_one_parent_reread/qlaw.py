"""Rule Q (a one-parent birth also takes a distinction its parent shares) on full holdings.

Frozen definitions: research/ONE-PARENT-REREAD-20261123-001A/preregistration.md ("Definitions (frozen)").  Readings
taken where the note leaves a choice are in deviations.md of this folder.

Recorded code reused read-only (imported by path, never changed):
  * ticket A of the re-read epic, `rlaw.py` (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law): class
    `Growth` (full holdings, groups read from full holdings by the exact `Groups` search, the lookahead `_demand`, the
    GF(2) elimination `Span`, `apply`, `run`).  Its sha256 is asserted at import.  `rlaw.USE_C = False`, so its C search is
    never built (into ticket A's artifact folder); the Python search is the same algorithm (ticket A deviations B1).
  * through rlaw: the recorded `end_operator` and the review-leads `lib.py` (sources, draws, driver, operator test).

`QGrowth` is a subclass of `rlaw.Growth`.  Two methods are COPIED from rlaw.Growth and changed, each marked:
  * `plan`: the groups, the cap and the stall exactly as rlaw.Growth.plan under rule "ordinary" (a short knot stalls the
    round; there is no rule R), then rule Q's allocation: each parent hands out its loose distinctions in birth order,
    the last listed first (as rlaw and the recorded wrapper do); a one-parent birth whose parent holds, at the start of
    the round, a distinction with two or more holders also takes one such distinction: convention O the smallest name,
    N the largest, or the distinction given for that birth by `choice` (census, round 1).  With `reread=False` no birth
    takes a shared distinction (ordinary growth on full holdings).
  * `_finish`: fresh counts max(D, 3 - i, 1) with i the number of INPUTS of the birth (rlaw counts parents, which is the
    same for every birth except a re-reading one, whose one parent gives two inputs).  D is rlaw's lookahead demand
    computed from the inputs, so the old holders of a re-read distinction witness the birth that took it (the round's
    new meetings are in the lookahead).  Under parity a birth gets no fresh distinction exactly when the GF(2) vector of
    what it takes is in the span of the old knots (rlaw's elimination test, as under its rule R).
"""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
ART = ROOT / 'artifacts' / TICKET / HERE.name
A_EXP = ROOT / 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law'
RLAW_SHA = '29aa3d9112d4a12b2d7970756c455e11dd3ed7abaef99b85daa64f4c4222d8f8'   # contract.json "inputs"

HORIZON, CAP = 12, 5000      # tests (a) and (b): "to 12 rounds or 5,000 knots"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


assert sha256(A_EXP / 'rlaw.py') == RLAW_SHA, 'rlaw.py differs from the engine named in the contract'
sys.path.insert(0, str(A_EXP))
import rlaw  # noqa: E402

rlaw.USE_C = False
lib = rlaw.lib
Round = rlaw.Round


class QGrowth(rlaw.Growth):
    """A structure under one law grown one complete round at a time under rule Q (or, with reread=False, ordinary
    growth on full holdings with the elimination closing test under parity).

    law: 'parity' (every knot even parity; closing by elimination) or 'nae' (no closing: every birth gets at least one
    fresh distinction).  convention: 'O' (oldest = smallest name) or 'N' (newest = largest name)."""

    def __init__(self, stars, law, convention='O', reread=True, bound_next=True):
        # rule 'R' in the parent only so that the GF(2) span is kept under parity and `_finish` would use elimination;
        # nothing of rule R is used (plan and _finish are replaced below).
        super().__init__(stars, law, rule='R', convention=convention, check=False, bound_next=bound_next)
        self.reread = reread
        self.n_founders = len(self.stars)
        self.holders_at = [self.max_holders()]   # largest number of holders at each stage (0 = the start)

    def shared_of(self, k):
        """The distinctions knot k holds that have two or more holders now (at the start of the round), by name."""
        return [d for d in sorted(self.stars[k]) if len(self.holders[d]) >= 2]

    # ---- COPIED from rlaw.Growth.plan and changed: no rule R; rule Q's allocation ------------------------------------
    def plan(self, max_births=None, choice=None):
        if not self.loose:
            return Round('closed')
        opens, raw = self.present_end()
        blocks = rlaw.maximal_blocks(raw)
        gr = rlaw.Groups(list(opens), blocks, limit=max_births)
        if gr.exceeded:  # more than max_births groups: the recorded rule caps (before any stall)
            return Round('cap')
        if max_births is not None and gr.total > max_births:
            return Round('cap')
        multi = gr.explicit()
        used = Counter(v for row in multi for v in row)
        short = tuple((k, used[k] - n) for k, n in opens.items() if used[k] > n)
        if short:  # rule Q: a shortage stalls the round as in ordinary growth
            return Round('stall', shortages=short, groups=multi, opens=opens, blocks=blocks)
        parents = multi + tuple((k,) for k, n in opens.items() for _ in range(max(0, n - used[k])))
        if max_births is not None and len(parents) > max_births:
            return Round('cap')
        pool = {k: list(v) for k, v in self.loose.items()}
        inputs, paid = [], []
        for i, ps in enumerate(parents):
            row = [pool[p].pop() for p in ps]          # loose distinctions, last listed first (rlaw, lib.grow)
            prow = [False] * len(row)
            if self.reread and len(ps) == 1:
                sh = self.shared_of(ps[0])
                if sh:
                    if choice is not None and i in choice:
                        d = choice[i]
                        assert d in sh, 'a chosen distinction is not shared by the parent'
                    else:
                        d = sh[0] if self.convention == 'O' else sh[-1]
                    row.append(d)
                    prow.append(True)
            inputs.append(tuple(row))
            paid.append(tuple(prow))
        assert not any(pool.values()), 'a loose distinction was left unspent'
        if choice is not None:
            assert set(choice) <= {i for i, prow in enumerate(paid) if any(prow)}, 'a choice for a birth that re-reads nothing'
        room = None if (max_births is None or not self.bound_next) else max_births - len(parents)
        return self._finish(parents, inputs, paid, (), multi, opens, blocks, room)

    # ---- COPIED from rlaw.Growth._finish and changed: 3 - (number of inputs) ------------------------------------------
    def _finish(self, parents, inputs, paid, short, multi, opens, blocks, room=None):
        nb = len(parents)
        implied, elim = [], []
        for row in inputs:
            e = self.span.contains(rlaw.mask(row)) if self.span is not None else None
            elim.append(e)
            implied.append(bool(e) if self.law == 'parity' else False)
        demand = self._demand(parents, inputs, room, implied)
        capped = demand is None
        if capped:
            demand = (0,) * nb
        fresh = tuple(0 if imp else max(demand[i], 3 - len(row), 1)
                      for i, (row, imp) in enumerate(zip(inputs, implied, strict=True)))
        return Round('extend', parents=parents, inputs=tuple(inputs), paid=tuple(paid), fresh=fresh,
                     demand=None if capped else demand, implied=tuple(implied), elim=tuple(elim), shortages=short,
                     groups=multi, opens=opens, blocks=blocks, next_capped=capped)

    def apply(self, r, keep_payments=False):
        rereads = [i for i, prow in enumerate(r.paid) if any(prow)]
        super().apply(r, keep_payments)
        rec = self.rounds[-1]
        rec['reread_births'] = len(rereads)
        rec['reread_fresh'] = dict(Counter(r.fresh[i] for i in rereads))
        rec['zero_fresh'] = sum(1 for f in r.fresh if f == 0)
        self.holders_at.append(self.max_holders())

    def reread_births_per_round(self):
        return [x['reread_births'] for x in self.rounds]


def run_ab(stars, law, conv, reread, horizon=HORIZON, cap=CAP, bound_next=False):
    """Tests (a) and (b): grow to `horizon` rounds or `cap` knots (rlaw.Growth.run, whose cap rule is the recorded one).
    Returns the QGrowth object; g.last is the last planned round (its shortages when the history stalled)."""
    return QGrowth(stars, law, conv, reread=reread, bound_next=bound_next).run(horizon, cap)


def history_summary(g):
    """The per-history record of tests (a) and (b)."""
    stall_short = None
    if g.outcome == 'stall':
        stall_short = [[int(k), int(x), bool(k >= g.n_founders)] for k, x in g.last.shortages]
    births = g.births_per_round()
    return dict(outcome=g.outcome, rounds=len(g.rounds), n_at=g.n_at, births=births,
                reread_births=g.reread_births_per_round(), holders_at=g.holders_at,
                max_holders=max(g.holders_at), zero_fresh=[x['zero_fresh'] for x in g.rounds],
                reread_fresh=[x['reread_fresh'] for x in g.rounds],
                fresh_lower_bound=[x['fresh_lower_bound'] for x in g.rounds],
                stall_shortages=stall_short,
                growth_kind=rlaw.recorded_growth_kind(g), growth_kind_births=rlaw.growth_kind_births(births),
                first_failing_step=rlaw.first_failing_step(g))


def reference_summary(stars, law, horizon=HORIZON, cap=CAP):
    """The recorded ordinary driver lib.grow (no clock), with the same record fields where they exist."""
    h = lib.grow(stars, law, horizon, cap, time_limit=None)
    holders = Counter()
    holders_at = []
    n_prev = 0
    for n in h['n_at']:
        for s in h['stars'][n_prev:n]:
            holders.update(s)
        holders_at.append(max(holders.values()))
        n_prev = n
    return h, dict(outcome=h['outcome'], rounds=h['steps'], n_at=h['n_at'], births=[len(s) for s in h['births']],
                   one_parent_births=[sum(1 for p, _ in s if p == 1) for s in h['births']],
                   holders_at=holders_at, max_holders=max(holders_at), growth_kind=lib.growth_kind(h),
                   growth_kind_births=rlaw.growth_kind_births([len(s) for s in h['births']]),
                   first_failing_step=lib.first_failing_stage(h['stars'], h['n_at']))


def stars_digest(stars):
    return hashlib.sha256(json.dumps([list(s) for s in stars], separators=(',', ':')).encode()).hexdigest()


def small_prefix(stars, n_at, limit=22):
    """Stars up to the stage after the last stage with at most `limit` distinctions (rlaw.small_prefix without a law)."""
    last = None
    for t in range(len(n_at)):
        if rlaw.distinctions_at(stars, n_at[t]) <= limit:
            last = t
        else:
            break
    if last is None or len(n_at) < 2:
        return None
    end = min(last + 1, len(n_at) - 1)
    return dict(n_at=list(n_at[:end + 1]), stars=[list(s) for s in stars[:n_at[end]]])


def dump(path, rows, mode='w'):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, mode + 't') as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(',', ':'), default=str) + '\n')


def load(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        return [json.loads(line) for line in f if line.strip()]
