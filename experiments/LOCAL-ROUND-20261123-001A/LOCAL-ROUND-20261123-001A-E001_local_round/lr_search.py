"""The comparison of LR section 4: the map m, match and mismatch, the cutoff, the outcomes, the memo key and
the three kinds of order (every order breadth-first over memo keys; sampled, seeds 0-199; x-last).

A run's knot is named by its image under m (a reference knot id).  A state is the memo key: the set I of
images (start knots included) and the set Bar of barred images, packed in one integer I | Bar << N.  A birth
(B, f) is made by the closing bit (LR 2.4.3) and matched to the least-numbered reference knot, not yet an
image, with parents B and that fresh count; if there is none the birth is a mismatch and the order ends.
After every birth (and at the start) every allowed barring is made before the next birth (deviations.md
item 7), each matched against the reference.
"""
from __future__ import annotations

import random
import resource
import time

from lr_laws import State, bits


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class Runner:
    def __init__(self, ref, law):
        self.ref = ref
        self.law = law
        self.N = ref.N
        self.full = (1 << ref.N) - 1
        self.closing_events = []     # (births so far, B, matched reference knot or None)
        self.n_closing = 0
        self.n_closing_matched_none = 0

    # ---------------------------------------------------------------- one step
    def state(self, I, Bar):
        return State(self.ref, I, Bar)

    def close(self, I, Bar, st=None):
        """Make every allowed barring (all at once, then read again) until none is allowed."""
        if st is None:
            st = State(self.ref, I, Bar)
        if not self.law.barrings_possible:
            return I, Bar, st, None
        while True:
            bars = [x for x in self.law.barrings(st) if not (Bar >> x) & 1]
            if not bars:
                return I, Bar, st, None
            for x in bars:
                if not self.ref.retires[x]:
                    return I, Bar, st, ('barring', x)
            for x in bars:
                Bar |= 1 << x
            st = State(self.ref, I, Bar)

    def birth(self, st, B, f):
        """LR 2.4: take one usable distinction from each knot of B; the closing bit; the match."""
        closing = (st.loose - len(B)) == 0
        fa = 0 if closing else f
        c = None
        for x in self.ref.by_par.get(B, ()):
            if not (st.I >> x) & 1 and self.ref.fresh[x] == fa:
                c = x
                break
        return c, closing, fa

    def allowed(self, st):
        A = self.law.allowed(st)
        seen = {}
        for B, f in A:
            if B in seen and seen[B] != f:
                raise AssertionError('one parent set allowed with two fresh counts')
            seen[B] = f
        return sorted(seen.items())

    def classify(self, st):
        """No birth within round r is allowed: matches through round r, or underbuilds (LR section 4)."""
        ref = self.ref
        I = st.I
        missing = [c for c in ref.within if not (I >> c) & 1 and (ref.par_mask[c] & ~I) == 0]
        unbarred = [x for x in bits(I) if ref.born[x] <= ref.r and ref.retires[x] and not (st.Bar >> x) & 1]
        kind = 'match' if not missing and not unbarred else 'underbuild'
        return kind, missing, unbarred

    def start_key(self):
        I0 = self.ref.start_mask
        I, Bar, st, mm = self.close(I0, 0)
        return I, Bar, st, mm

    # ---------------------------------------------------------------- every order
    def every_order(self, cap_keys, time_budget, mismatch_examples=200, stop_at_first_mismatch=False):
        t0 = time.time()
        N = self.N
        full = self.full
        I, Bar, st, mm = self.start_key()
        res = {'kind': 'every order', 'cap_keys': cap_keys, 'time_budget_s': time_budget}
        orders = {'match': 0, 'underbuild': 0, 'mismatch': 0}
        terminal_keys = {'match': 0, 'underbuild': 0}
        mismatch_edges = 0
        examples = []
        keys = 1
        level_sizes = [1]
        if mm:
            res.update({'finished': True, 'least_n': 0, 'least_exact': True, 'mismatch_edges': 1,
                        'examples': [{'parent_key': [I, Bar], 'event': list(mm)}], 'keys': 1,
                        'searched_to_births': 0, 'orders': {'mismatch': 1}, 'seconds': 0})
            return res
        level = {I | (Bar << N): 1}
        n = 0
        stopped = None
        first_mm_level = None
        underbuild_example = None
        while level:
            nxt = {}
            mm_here = 0
            count = 0
            for key, cnt in level.items():
                count += 1
                if (count & 1023) == 0 and time.time() - t0 > time_budget:
                    stopped = 'time'
                    break
                I = key & full
                Bar = key >> N
                st = State(self.ref, I, Bar)
                A = self.allowed(st)
                if not A:
                    kind, missing, unbarred = self.classify(st)
                    orders[kind] += cnt
                    terminal_keys[kind] += 1
                    if kind == 'underbuild' and underbuild_example is None:
                        underbuild_example = {'key': [I, Bar], 'births': n, 'missing': missing[:20],
                                              'unbarred': unbarred[:20]}
                    continue
                for B, f in A:
                    c, closing, fa = self.birth(st, B, f)
                    if closing:
                        self.n_closing += 1
                        if c is not None and self.ref.fresh[c] == 0:
                            self.n_closing_matched_none += 1
                        if len(self.closing_events) < 50:
                            self.closing_events.append({'births_before': n, 'parents': list(B), 'matched': c})
                    if c is None:
                        mm_here += 1
                        orders['mismatch'] += cnt
                        if len(examples) < mismatch_examples:
                            examples.append({'parent_key': [I, Bar], 'event': ['birth', list(B), fa],
                                             'births': n + 1})
                        continue
                    I2, Bar2, st2, mmb = self.close(I | (1 << c), Bar)
                    if mmb:
                        mm_here += 1
                        orders['mismatch'] += cnt
                        if len(examples) < mismatch_examples:
                            examples.append({'parent_key': [I, Bar], 'event': ['birth then barring', list(B), fa,
                                                                               mmb[1]], 'births': n + 1})
                        continue
                    k2 = I2 | (Bar2 << N)
                    nxt[k2] = nxt.get(k2, 0) + cnt
            mismatch_edges += mm_here
            if stopped:
                if mm_here and first_mm_level is None:
                    # every order was searched to n births with no mismatch, so n + 1 is the least
                    first_mm_level = n + 1
                break
            if mm_here and first_mm_level is None:
                first_mm_level = n + 1
            if first_mm_level is not None and stop_at_first_mismatch:
                stopped = 'first mismatch level complete'
                n += 1
                break
            if not nxt:
                level = nxt
                n += 1
                break
            keys += len(nxt)
            level_sizes.append(len(nxt))
            level = nxt
            n += 1
            if keys > cap_keys:
                stopped = 'key cap'
                break
            if time.time() - t0 > time_budget:
                stopped = 'time'
                break
        finished = stopped in (None, 'first mismatch level complete')
        res.update({
            'finished': finished, 'stopped': stopped,
            'searched_to_births': (first_mm_level if stopped == 'first mismatch level complete' else len(level_sizes) - 1),
            'least_n': first_mm_level, 'least_exact': first_mm_level is not None,
            'keys': keys, 'level_sizes': level_sizes, 'max_level': max(level_sizes),
            'mismatch_edges': mismatch_edges, 'orders': {k: str(v) for k, v in orders.items()},
            'orders_complete': stopped is None,
            'terminal_keys': terminal_keys, 'examples': examples, 'underbuild_example': underbuild_example,
            'closing_firings': self.n_closing, 'closing_matched_none': self.n_closing_matched_none,
            'closing_events': self.closing_events[:20],
            'seconds': round(time.time() - t0, 2), 'peak_rss_mb': round(peak_rss_mb(), 1)})
        return res

    # ---------------------------------------------------------------- one order
    def run_order(self, chooser, record=True):
        """Run one maximal order; chooser(A) picks the next birth from the sorted allowed list."""
        I, Bar, st, mm = self.start_key()
        events = []
        closing = []
        if mm:
            return {'outcome': 'mismatch', 'births': 0, 'events': [['barring', mm[1], False]], 'closing': []}
        n = 0
        while True:
            A = self.allowed(st)
            if not A:
                kind, missing, unbarred = self.classify(st)
                out = {'outcome': kind, 'births': n, 'closing': closing}
                if kind == 'underbuild':
                    out['missing'] = missing[:20]
                    out['unbarred'] = unbarred[:20]
                if record:
                    out['events'] = events
                return out
            B, f = chooser(A)
            c, cl, fa = self.birth(st, B, f)
            n += 1
            if cl:
                closing.append({'birth': n, 'parents': list(B), 'matched': c,
                                'matched_received_none': c is not None and self.ref.fresh[c] == 0})
            events.append(['birth', list(B), fa, c])
            if c is None:
                out = {'outcome': 'mismatch', 'births': n, 'closing': closing, 'mismatch': ['birth', list(B), fa]}
                if record:
                    out['events'] = events
                return out
            bar_before = Bar
            I, Bar, st, mmb = self.close(I | (1 << c), Bar)
            for x in bits(Bar & ~bar_before):
                events.append(['barring', x, True])
            if mmb:
                events.append(['barring', mmb[1], False])
                out = {'outcome': 'mismatch', 'births': n, 'closing': closing, 'mismatch': ['barring', mmb[1]]}
                if record:
                    out['events'] = events
                return out

    def sampled(self, seeds):
        outs = []
        for s in seeds:
            rng = random.Random(s)
            o = self.run_order(lambda A: A[rng.randrange(len(A))])
            o['seed'] = s
            outs.append(o)
        return outs

    def xlast(self, seed=0):
        outs = []
        xs = [x for x in range(self.N) if self.ref.born[x] <= 1]
        for x in xs:
            rng = random.Random(seed)

            def choose(A, x=x, rng=rng):
                A2 = [a for a in A if x not in a[0]]
                L = A2 if A2 else A
                return L[rng.randrange(len(L))]
            o = self.run_order(choose)
            o['x'] = x
            outs.append(o)
        return outs

    # ---------------------------------------------------------------- reconstruct and list
    def path_to(self, tI, tBar):
        """An order reaching the key (tI, tBar): a search restricted to births whose image lies in tI."""
        fail = set()
        I0, Bar0, st0, mm = self.start_key()

        def dfs(I, Bar, st, path):
            if I == tI and Bar == tBar:
                return path
            key = (I, Bar)
            if key in fail:
                return None
            for B, f in self.allowed(st):
                c, cl, fa = self.birth(st, B, f)
                if c is None or not (tI >> c) & 1:
                    continue
                I2, Bar2, st2, mmb = self.close(I | (1 << c), Bar)
                if mmb or (Bar2 & ~tBar):
                    continue
                r = dfs(I2, Bar2, st2, path + [B])
                if r is not None:
                    return r
            fail.add(key)
            return None
        return dfs(I0, Bar0, st0, [])

    def listing(self, order):
        """Replay an order (a list of parent sets, as images) birth by birth: each birth with its run number,
        its parents (run numbers and images), its fresh count and the reference knot it matches or fails to
        match; each barring with its match."""
        ref = self.ref
        I, Bar, st, mm = self.start_key()
        run_no = {x: x for x in range(ref.n_start)}
        nxt = ref.n_start
        rows = []
        for x in bits(Bar):
            rows.append({'barring': run_no[x], 'image': x, 'matches': True})
        if mm:
            rows.append({'barring': mm[1], 'image': mm[1], 'matches': False})
            return rows
        for i, B in enumerate(order):
            A = dict(self.allowed(st))
            if B not in A:
                rows.append({'birth': i + 1, 'parents_images': list(B), 'allowed': False})
                return rows
            c, cl, fa = self.birth(st, B, A[B])
            row = {'birth': i + 1, 'run_knot': nxt, 'parents_run': [run_no[b] for b in B],
                   'parents_images': list(B), 'fresh': fa, 'closing_bit': cl,
                   'matches_reference_knot': c,
                   'reference_round': ref.born[c] if c is not None else None,
                   'kind': 'join' if len(B) > 1 else 'offshoot'}
            if c is None:
                row['reference_children_with_these_parents'] = [
                    {'knot': x, 'fresh': ref.fresh[x], 'round': ref.born[x], 'already_image': bool((I >> x) & 1)}
                    for x in ref.by_par.get(B, ())]
                rows.append(row)
                return rows
            rows.append(row)
            run_no[c] = nxt
            nxt += 1
            bar_before = Bar
            I, Bar, st, mmb = self.close(I | (1 << c), Bar)
            for x in bits(Bar & ~bar_before):
                rows.append({'barring': run_no[x], 'image': x, 'matches': True})
            if mmb:
                rows.append({'barring': run_no.get(mmb[1]), 'image': mmb[1], 'matches': False})
                return rows
        return rows
