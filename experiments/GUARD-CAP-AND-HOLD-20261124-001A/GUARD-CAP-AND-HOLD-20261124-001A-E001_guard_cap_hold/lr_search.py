"""The comparison of LR section 4, with GCH section 2 (the match with the barred count) and section 3 items 6-7
(the last round R, the match by earliest round): match and mismatch, the cutoff, the outcomes, the memo key and the
three kinds of order (every order breadth-first over memo keys; sampled, seeds 0-199; x-last).

A run's knot is named by its image under m (a reference knot id).  A state is the memo key: the set I of images
(start knots included) and the set Bar of barred images, packed in one integer I | Bar << N.  A birth (B, f, u)
is made by the closing bit (LR 2.4.3) and matched to the reference knot, not yet an image, with parents B, fresh
count f and f - u places barred at birth, born in the earliest round, and among those the least-numbered; if there
is none the birth is a mismatch and the order ends.  After every birth (and at the start) every allowed barring is
made before the next birth, each matched against the reference.

Every-order searches have no time budget: the only bound is the key cap, checked when a breadth-first level is
complete (so a search can pass its cap by up to one level).
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
        self.closing_events = []
        self.n_closing = 0
        self.n_closing_matched_none = 0

    # ---------------------------------------------------------------- one step
    def state(self, I, Bar):
        return State(self.ref, I, Bar)

    def barring_matches(self, x, I):
        """A barring of x matches when m(x) retires in the reference (deviations.md item 11): under RELEASE such a
        knot has no children; under HOLD every reference child of m(x) must already be an image."""
        ref = self.ref
        return ref.retires[x] and (ref.chi_mask[x] & ~I) == 0

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
                if not self.barring_matches(x, I):
                    return I, Bar, st, ('barring', x)
            for x in bars:
                Bar |= 1 << x
            st = State(self.ref, I, Bar)

    def birth(self, st, B, f, u):
        """LR 2.4: take one usable distinction from each knot of B; the closing bit; the match (GCH 2, 3 item 7)."""
        closing = (st.loose - len(B)) == 0
        if closing:
            f, u = 0, 0
        c = None
        for x in self.ref.by_pfb.get((B, f, f - u), ()):
            if not (st.I >> x) & 1:
                c = x
                break
        return c, closing, f, u

    def allowed(self, st):
        return sorted(set(self.law.allowed3(st)))

    def classify(self, st, explain=False):
        """No birth within round r is allowed: matches through round r, or underbuilds (LR section 4)."""
        ref = self.ref
        I = st.I
        missing = [c for c in ref.within if not (I >> c) & 1 and (ref.par_mask[c] & ~I) == 0]
        unbarred = [x for x in bits(I) if ref.born[x] <= ref.r and ref.retires[x] and not (st.Bar >> x) & 1]
        kind = 'match' if not missing and not unbarred else 'underbuild'
        why = None
        if explain and kind == 'underbuild':
            if missing:
                first = min(missing, key=lambda c: (ref.born[c], c))
                why = {'first_never_made': first, 'first_never_made_round': ref.born[first],
                       'n_never_made': len(missing), 'why': self.law.explain(st, first)}
            else:
                why = {'retirements_not_made': unbarred}
        return kind, missing, unbarred, why

    def start_key(self):
        I0 = self.ref.start_mask
        return self.close(I0, 0)

    # ---------------------------------------------------------------- every order
    def every_order(self, cap_keys, mismatch_examples=200, underbuild_examples=20):
        t0 = time.time()
        N = self.N
        full = self.full
        I, Bar, st, mm = self.start_key()
        res = {'kind': 'every order', 'cap_keys': cap_keys, 'time_budget_s': None}
        orders = {'match': 0, 'underbuild': 0, 'mismatch': 0}
        terminal_keys = {'match': 0, 'underbuild': 0}
        mismatch_edges = 0
        examples = []
        underbuilds = []
        under_reasons = {}
        keys = 1
        level_sizes = [1]
        if mm:
            res.update({'finished': True, 'least_n': 0, 'least_exact': True, 'mismatch_edges': 1,
                        'examples': [{'parent_key': [I, Bar], 'event': list(mm), 'births': 0}], 'keys': 1,
                        'searched_to_births': 0, 'level_sizes': [1], 'orders': {'mismatch': '1'},
                        'terminal_keys': terminal_keys, 'underbuild_examples': [], 'underbuild_reasons': {},
                        'seconds': 0, 'stopped': None, 'orders_complete': True, 'max_level': 1,
                        'closing_firings': 0, 'closing_matched_none': 0, 'closing_events': [],
                        'peak_rss_mb': round(peak_rss_mb(), 1)})
            return res
        level = {I | (Bar << N): 1}
        n = 0
        stopped = None
        first_mm_level = None
        while level:
            nxt = {}
            mm_here = 0
            for key, cnt in level.items():
                I = key & full
                Bar = key >> N
                st = State(self.ref, I, Bar)
                A = self.allowed(st)
                if not A:
                    kind, missing, unbarred, why = self.classify(st, explain=True)
                    orders[kind] += cnt
                    terminal_keys[kind] += 1
                    if kind == 'underbuild':
                        r = why['why'].get('reason') if why and 'why' in why else 'retirement not made'
                        k2 = '%s | first never made: %s' % (r, why.get('first_never_made') if why else None)
                        under_reasons[k2] = under_reasons.get(k2, 0) + 1
                        if len(underbuilds) < underbuild_examples:
                            underbuilds.append({'key': [hex(I), hex(Bar)], 'births': n, 'why': why,
                                                'missing': missing[:20], 'unbarred': unbarred[:20]})
                    continue
                for B, f, u in A:
                    c, closing, fa, ua = self.birth(st, B, f, u)
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
                            examples.append({'parent_key': [I, Bar], 'event': ['birth', list(B), fa, ua],
                                             'births': n + 1})
                        continue
                    I2, Bar2, st2, mmb = self.close(I | (1 << c), Bar)
                    if mmb:
                        mm_here += 1
                        orders['mismatch'] += cnt
                        if len(examples) < mismatch_examples:
                            examples.append({'parent_key': [I, Bar], 'event': ['birth then barring', list(B), fa, ua,
                                                                               mmb[1]], 'births': n + 1})
                        continue
                    k2 = I2 | (Bar2 << N)
                    nxt[k2] = nxt.get(k2, 0) + cnt
            mismatch_edges += mm_here
            if mm_here and first_mm_level is None:
                first_mm_level = n + 1
            if not nxt:
                level = nxt
                break
            keys += len(nxt)
            level_sizes.append(len(nxt))
            level = nxt
            n += 1
            if keys > cap_keys:
                stopped = 'key cap'
                break
        finished = stopped is None
        res.update({
            'finished': finished, 'stopped': stopped,
            'searched_to_births': len(level_sizes) - 1,
            'least_n': first_mm_level, 'least_exact': first_mm_level is not None,
            'keys': keys, 'level_sizes': level_sizes, 'max_level': max(level_sizes),
            'mismatch_edges': mismatch_edges, 'orders': {k: str(v) for k, v in orders.items()},
            'orders_complete': finished,
            'terminal_keys': terminal_keys, 'examples': examples, 'underbuild_examples': underbuilds,
            'underbuild_reasons': under_reasons,
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
                kind, missing, unbarred, why = self.classify(st, explain=True)
                out = {'outcome': kind, 'births': n, 'closing': closing}
                if kind == 'underbuild':
                    out['missing'] = missing[:20]
                    out['unbarred'] = unbarred[:20]
                    out['why'] = why
                if record:
                    out['events'] = events
                return out
            B, f, u = chooser(A)
            c, cl, fa, ua = self.birth(st, B, f, u)
            n += 1
            if cl:
                closing.append({'birth': n, 'parents': list(B), 'matched': c,
                                'matched_received_none': c is not None and self.ref.fresh[c] == 0})
            events.append(['birth', list(B), fa, ua, c])
            if c is None:
                out = {'outcome': 'mismatch', 'births': n, 'closing': closing,
                       'mismatch': ['birth', list(B), fa, ua]}
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
        """An order reaching the key (tI, tBar): a search restricted to births whose image lies in tI.  Returns a
        list of births (B, f, u)."""
        fail = set()
        I0, Bar0, st0, mm = self.start_key()

        def dfs(I, Bar, st, path):
            if I == tI and Bar == tBar:
                return path
            key = (I, Bar)
            if key in fail:
                return None
            for B, f, u in self.allowed(st):
                c, cl, fa, ua = self.birth(st, B, f, u)
                if c is None or not (tI >> c) & 1:
                    continue
                I2, Bar2, st2, mmb = self.close(I | (1 << c), Bar)
                if mmb or (Bar2 & ~tBar):
                    continue
                r = dfs(I2, Bar2, st2, path + [(B, f, u)])
                if r is not None:
                    return r
            fail.add(key)
            return None
        return dfs(I0, Bar0, st0, [])

    def listing(self, order):
        """Replay an order (a list of births (B, f, u) or of parent sets, as images) birth by birth: each birth
        with its run number, its parents (run numbers and images), its fresh count, its barred count and the
        reference knot it matches or fails to match; each barring with its match."""
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
        for i, item in enumerate(order):
            A = self.allowed(st)
            if len(item) == 3 and isinstance(item[0], tuple):
                B, f, u = item
                hit = (B, f, u) in A
            else:
                B = tuple(item)
                opts = [a for a in A if a[0] == B]
                hit = bool(opts)
                if hit:
                    _, f, u = opts[0]
            if not hit:
                rows.append({'birth': i + 1, 'parents_images': list(B), 'allowed': False,
                             'allowed_now': [[list(a[0]), a[1], a[2]] for a in A][:40]})
                return rows
            c, cl, fa, ua = self.birth(st, B, f, u)
            row = {'birth': i + 1, 'run_knot': nxt, 'parents_run': [run_no[b] for b in B],
                   'parents_images': list(B), 'fresh': fa, 'usable_fresh': ua, 'barred_at_birth': fa - ua,
                   'closing_bit': cl, 'matches_reference_knot': c,
                   'reference_round': ref.born[c] if c is not None else None,
                   'kind': 'join' if len(B) > 1 else 'offshoot'}
            if c is None:
                row['reference_children_with_these_parents'] = [
                    {'knot': x, 'fresh': ref.fresh[x], 'barred_at_birth': ref.barred0[x], 'round': ref.born[x],
                     'already_image': bool((I >> x) & 1)} for x in ref.by_par.get(B, ())]
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
