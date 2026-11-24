"""The reference: ticket A's engine of RING-IN-BALANCE-20261123-001, imported unchanged (LR section 4).

It is loaded from its own path under a private module name; nothing in it is edited.  This module runs it
on a start under a law, finds the last round R for a cutoff r, and extracts, for every reference knot, the
data the comparison needs: parents, fresh count (places less parents), round of birth, children, h0 and,
for start knots, which start knots they meet.  Laws read the run's structure only; the round of birth is used
only by the comparison (the cutoff, the outcome tests).
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REF_PATH = ROOT / 'experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py'
REF_SHA256 = '2c6eac5645658a2992d54c63205156f22c45489ef0bd5eea0c8b5fcee2917671'


def _load():
    data = REF_PATH.read_bytes()
    h = hashlib.sha256(data).hexdigest()
    if h != REF_SHA256:
        raise RuntimeError('reference engine changed: %s' % h)
    spec = importlib.util.spec_from_file_location('ring_in_balance_A_engine', REF_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


E = _load()


def ref_law(ration, treatment):
    return E.Law(ration=ration, treatment=treatment)


def part_all_short(S):
    """Members of the reference's live roster that lie in a part all of whose members are short."""
    roster = E.live_roster(S)
    out = set()
    for i, P in enumerate(roster.parts):
        groups = E.roster_groups(roster, i)
        owe = defaultdict(int)
        for g in groups:
            for u in g:
                owe[u] += 1
        if all(owe[u] > roster.h[u] for u in P):
            out.update(P)
    return roster, out


class RefData:
    """Reference knots through the last round R of a cutoff r."""

    def __init__(self, stars, ration, treatment, r, max_rounds=40):
        self.stars = stars
        self.ration, self.treatment, self.r = ration, treatment, r
        law = ref_law(ration, treatment)
        S = E.from_stars(stars)
        self.n_start = S.n_knots
        start = S.copy()
        records = []
        R = None
        end_event = None
        for t in range(1, max_rounds + 1):
            S, rec = E.round_step(S, law)
            records.append(rec)
            if rec.get('stalled') or rec.get('jammed') or rec.get('stopped'):
                end_event = end_event or {'event': [k for k in ('stalled', 'jammed', 'stopped') if rec.get(k)][0],
                                          'round': t}
            if t < r:
                continue
            roster, allshort = part_all_short(S)
            if all(S.made[u] > r or u in allshort for u in roster.members):
                R = t
                break
            if rec.get('stalled'):
                R = t
                break
        if R is None:
            raise RuntimeError('no last round within %d rounds' % max_rounds)
        self.R = R
        self.end_event = end_event
        self.records = records
        self.S = S
        N = S.n_knots
        self.N = N
        self.par = [tuple(sorted(S.parents[x])) for x in range(N)]
        self.born = [S.made[x] for x in range(N)]
        self.fresh = [len(S.places[x]) - len(S.parents[x]) for x in range(N)]
        self.par_mask = [sum(1 << p for p in self.par[x]) for x in range(N)]
        ch = [0] * N
        for x in range(N):
            for p in self.par[x]:
                ch[p] |= 1 << x
        self.chi_mask = ch
        # h0 (LR 1.1): places less parents; for a start knot, places not shared with another start knot
        h0 = list(self.fresh)
        start_nbr = [0] * N
        for u in range(self.n_start):
            loose = 0
            for d in start.places[u]:
                hs = start.holders[d]
                if len(hs) == 1:
                    loose += 1
                else:
                    for w in hs:
                        if w != u:
                            start_nbr[u] |= 1 << w
            h0[u] = loose
        self.h0 = h0
        self.start_nbr = start_nbr
        self.start_mask = (1 << self.n_start) - 1
        self.places = [len(S.places[x]) for x in range(N)]
        # barred distinctions held in the reference, and retirements (barred, no children)
        self.ref_barred = [sum(1 for d in S.places[x] if len(S.holders[d]) == 1 and S.barred[d]) for x in range(N)]
        self.retires = [self.ref_barred[x] > 0 and ch[x] == 0 for x in range(N)]
        by_par = defaultdict(list)
        for x in range(self.n_start, N):
            by_par[self.par[x]].append(x)
        self.by_par = {k: sorted(v) for k, v in by_par.items()}
        self.by_par_mask = {k: sum(1 << x for x in v) for k, v in self.by_par.items()}
        # who waited in the reference, and when
        self.waited = defaultdict(list)
        for rec in records:
            for u in rec.get('waiting', []):
                self.waited[u].append(rec['round'])
        self.closing_knots = [x for x in range(self.n_start, N) if self.fresh[x] == 0]
        # births within round r: reference knots whose parents were all born by round r
        self.within = [x for x in range(self.n_start, N) if all(self.born[p] <= r for p in self.par[x])]

    def summary(self):
        return {'R': self.R, 'r': self.r, 'n_start': self.n_start, 'n_knots': self.N,
                'births_within_r': len(self.within), 'end_event': self.end_event,
                'closing_knots': self.closing_knots,
                'retirements': [x for x in range(self.N) if self.retires[x]],
                'births_per_round': [rec['n_births'] for rec in self.records]}
