"""The populations P1 and P2 (pre-registration, "Populations"; deviations.md, items 1-7).

  p2_lineages()     for each of the twenty pairs, the reference structure after each round 1..R2 (P2), with the rounds
                    1..rounds_checked marked as P1's reference rounds.
  serial_runs()     the 27 registered runs of R3 of the one-birth-at-a-time study, seeds 0..19 replayed; each distinct
                    state after a birth, with its predecessor state in the order (for identity links).

Everything is rebuilt from the earlier study's modules and the reference engine; nothing is read from their outputs
except gate.json (the twenty pairs) and the stored runs (to check the replay).
"""
from __future__ import annotations

import json
import random
import re

import pfh_common as PC
from pfh_struct import Struct

E = PC.E
P2_MAX_ROUNDS = 12
P2_MAX_KNOTS = 2000


def p2_lineage(start, fam, rounds_checked):
    """Structures after rounds 1..R2 of one pair, as engine structures (copies).  R2: the first round after which the
    structure has more than 2,000 knots, or 12; earlier if the growth has stopped (deviations.md, item 7)."""
    law = PC.ref_law(fam)
    S = PC.start_struct(start)
    start_S = S.copy()
    out = []
    events = []
    for t in range(1, P2_MAX_ROUNDS + 1):
        S, rec = E.round_step(S, law)
        out.append(S.copy())
        events.append({'round': t, 'knots': S.n_knots, 'births': rec['n_births'], 'stalled': rec['stalled'],
                       'jammed': rec['jammed'], 'stopped': rec['stopped']})
        if rec['stalled'] or rec['jammed']:
            raise RuntimeError('%s %s stalls or jams at round %d' % (start, fam, t))
        if S.n_knots > P2_MAX_KNOTS or rec['stopped']:
            break
    return start_S, out, events


def serial_configs():
    import lr_configs as K
    cfgs = []
    for row, start, fam, cuts in K.TABLE:
        for r in cuts:
            cfgs.append(('%s__r%d__R3' % (row, r), start, tuple(fam), r))
    for row, start, fam, r in K.BEYOND:
        cfgs.append(('%s__R3' % row, start, tuple(fam), r))
    return cfgs


def _slug(s):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', s).strip('_')


class SerialRun:
    """One registered run of R3: its reference and the distinct states after every birth of seeds 0..19.

    states: list of dicts {key: (I, Bar), extra: None or (B, f), pred: index of the predecessor state or -1 for the
    initial state, seeds: [(seed, birth number)]}."""

    def __init__(self, cid, start, fam, r, n_seeds=20):
        import lr_laws as L
        import lr_reference as RF
        from lr_search import Runner
        self.cid, self.start, self.fam, self.r = cid, start, fam, r
        ref = RF.RefData(PC.LRC.start_stars(start), fam[0], fam[1], r)
        self.ref = ref
        law = L.make_law(ref, 'R3')
        run = Runner(ref, law)
        stored = json.loads((PC.LR_ART / 'runs' / (_slug(cid) + '.json')).read_text())
        st_orders = {o['seed']: o for o in stored['sampled']['orders']}
        I0, Bar0, st0, mm = run.start_key()
        if mm:
            raise RuntimeError('mismatch at the start')
        self.initial = (I0, Bar0)
        self.states = []
        index = {}
        self.replay = []
        for s in range(n_seeds):
            rng = random.Random(s)
            o = run.run_order(lambda A: A[rng.randrange(len(A))])
            so = st_orders[s]
            same = (o['outcome'] == so['outcome'] and o['births'] == so['births'])
            self.replay.append({'seed': s, 'outcome': o['outcome'], 'births': o['births'], 'matches_stored': same})
            if not same:
                raise RuntimeError('%s seed %d: replay differs from the stored run' % (cid, s))
            I, Bar = I0, Bar0
            pred = -1
            nb = 0
            evs = o['events']
            k = 0
            while k < len(evs):
                ev = evs[k]
                if ev[0] != 'birth':
                    raise AssertionError('barring before a birth in the events')
                nb += 1
                B, fa, c = tuple(ev[1]), ev[2], ev[3]
                extra = None
                if c is None:
                    extra = (B, fa)
                else:
                    I |= 1 << c
                k += 1
                while k < len(evs) and evs[k][0] == 'barring':
                    if not evs[k][2]:
                        raise AssertionError('a mismatching barring in an R3 order')
                    Bar |= 1 << evs[k][1]
                    k += 1
                key = (I, Bar, extra)
                if key not in index:
                    index[key] = len(self.states)
                    self.states.append({'key': (I, Bar), 'extra': extra, 'pred': pred, 'seeds': []})
                i = index[key]
                self.states[i]['seeds'].append((s, nb))
                if self.states[i]['pred'] != pred:
                    # the same state reached from two predecessors: keep the first; identity links are added for
                    # every predecessor through 'preds'
                    self.states[i].setdefault('preds', set()).add(pred)
                pred = i
                if extra is not None:
                    break

    def struct(self, i):
        st = self.states[i]
        I, Bar = st['key']
        return Struct.induced(self.ref.S, I, Bar, self.ref.n_start, extra=st['extra'],
                              label='%s state %d' % (self.cid, i))

    def initial_struct(self):
        I, Bar = self.initial
        return Struct.induced(self.ref.S, I, Bar, self.ref.n_start, label='%s initial state' % self.cid)

    def preds(self, i):
        st = self.states[i]
        out = {st['pred']}
        out |= st.get('preds', set())
        return sorted(out)
