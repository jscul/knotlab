"""Literal, rooted receiver histories over the ordinary paid source. Read native.json.gz."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, pairwise
from pathlib import Path
import argparse
import gzip
import json
import os
import subprocess
import sys


HERE = Path(__file__).resolve().parent


def freeze(items=()):
    return frozenset(items)


def record_hash(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class World:
    def __init__(self, row, small=False):
        self.case = row['case']
        self.src = [freeze(a) for a in row['original_stars']]
        self.roles = row['live_roles']
        self.names = {v: k for k, v in self.roles.items()}
        self.originals = set(self.names)
        owners = defaultdict(list)
        for v, names in enumerate(self.src):
            for name in names:
                owners[name].append(v)
        self.loose = {v: sorted(i for i in self.src[v] if len(owners[i]) == 1)
                      for v in self.originals}
        sides = {}
        for j, names in enumerate(self.src):
            if not names or j in self.originals:
                continue
            side = defaultdict(list)
            for i in names:
                v, = set(owners[i]) - {j}
                assert v in self.originals
                side[v].append(i)
            sides[j] = dict(side)
        self.sides = sides
        self.port = {}
        group_witness = {}
        high_at = defaultdict(list)
        for j, side in sides.items():
            high = [v for v in side if len(side[v]) >= 3]
            if len(high) == 2:
                a, b = high
                high_at[a].append(b)
                high_at[b].append(a)
                group_witness[freeze((a, b))] = j
            if len(side) == 2:
                a, b = side
            elif len(high) != 2:
                raise ValueError('unreadable physical high sides')
            else:
                a, b = high
            self.port[a, b] = len(side[a])
            self.port[b, a] = len(side[b])
        if not small:
            def anchor(left, right):
                return [ab for ab, n in self.port.items()
                        if n == left and self.port[ab[::-1]] == right]
            (self.H, self.c0), = anchor(1, 11)
            (h, self.S), = anchor(1, 13)
            (self.O, other_h), = anchor(1, 17)
            assert h == other_h == self.H
            self.circuit = {v: sorted(neighbors, key=lambda u: self.port[v, u])
                            for v, neighbors in high_at.items()}
            for v, ns in self.circuit.items():
                assert len(set(self.port[v, i] for i in ns)) == len(ns)
            self.p, = [w for w in self.circuit[self.c0] if len(self.circuit[w]) == 8]
            self.r = self.cycle(self.c0, self.p)
            self.q = next(v for v in self.r if len(self.circuit[v]) == 4)
            self.strict = self.corridor({2})
            self.wide = self.corridor({2, 6})
            assert self.wide[1]
        self.inc = defaultdict(list)
        self.parts = {}
        self.lifts = {}
        self.rank_tables = {}
        self.next = {}
        self.prev = {}
        self.gates = {}
        self.gate_of = {}
        all_rows_used = set()
        # At both sites the high port has widths 3 and 9. Other high p/h
        # ports of width 9 can be distinguished by the full eight-port head.
        for case_gate in row['gates'].values():
            a, b = case_gate['tail'], case_gate['head']
            j = group_witness[freeze((a, b))]
            common = sides[j]
            assert self.port[a, b] == 3 and self.port[b, a] == 9
            remaining = set(common) - {a, b}
            z = next(iter(remaining), None)
            assert len(remaining) <= 1 and (z is None or len(common[z]) == 1)
            around = {}
            for endpoint in (a, b):
                around[endpoint] = {next(iter(set(x) - {endpoint})): k for k, x in sides.items()
                                     if len(x) == 2 and endpoint in x and len(x[endpoint]) == 1}
            both = set(around[a]) & set(around[b])
            w = next(iter(both), None)
            assert len(both) <= 1
            assert (z, w) == (case_gate['z'], case_gate['w'])
            triples = [[a, b, w]] if w is not None else [[a, b]]
            if z is not None:
                triples.extend([[a, z], [b, z]])
            site = -j-1
            pts = {v for group in triples for v in group}
            table = {freeze(): 0, **{freeze([v]): 1 for v in pts}}
            table.update({freeze(group): 2 for group in triples})
            if z is not None:
                table[freeze(pts)] = 3
            self.add_block(site, pts, table)
            all_rows_used.add(j)
            qualified = False
            if w is not None:
                aw, bw = around[a][w], around[b][w]
                qualified = len(sides[aw][w]) == len(sides[bw][w]) == 2
                all_rows_used.update([aw, bw])
            self.gates[site] = (a, b, w, z, qualified)
            self.gate_of[freeze([a, b])] = site
        for j, side in sides.items():
            if j in all_rows_used:
                continue
            a, b = side
            self.add_pair(-j-1, a, b)
        # All w are supplied two actual private names for just one original
        # joint service. Values after the third auxiliary point are unnecessary
        # in this finite audit; the proof supplies every further unary step.
        virtual = max(self.originals) + 1
        cell = min(self.parts) - 1
        for _, _, w, _, _ in self.gates.values():
            if w is None:
                continue
            assert len(self.loose[w]) == 2
            v = w
            for k in range(5):
                self.names[virtual] = self.names[w] + '~' + str(k+1)
                self.add_pair(cell, v, virtual)
                v, virtual, cell = virtual, virtual+1, cell-1
        self.raw_cuts = {}
        for law, native in row['laws'].items():
            cuts = native['cuts']
            if cuts[0]['status'] == 'stall':
                continue
            self.raw_cuts[law] = [{freeze(x['parents']): x for x in cut['births']}
                                  for cut in cuts[:2]]
        self.prices = {}
        self._members = {}
        self._ext = {}
        self._par = {}
        self._js = {}
        self._thirds = {}
        self._classes = {}

    def cycle(self, a, b):
        start, trace = (a, b), []
        visited = set()
        while (a,b) not in visited:
            visited.add((a,b))
            trace.append(a)
            ns = self.circuit[b]
            a,b = b,ns[(ns.index(a)+1) % len(ns)]
        assert (a,b) == start
        return tuple(trace)

    def corridor(self, eligible):
        def choices(v):
            return [w for (u, w), side in self.port.items()
                    if u == v and side in eligible and self.port[w, v] == 4]
        seen, v = [], self.S
        while v not in seen:
            seen.append(v)
            ns = choices(v)
            if len(ns) != 1 or len(choices(ns[0])) != 1:
                return tuple(seen), False
            v = ns[0]
        assert v == self.S
        return tuple(seen), True

    def add_block(self, j, pts, table):
        self.parts[j] = sorted(pts)
        self.rank_tables[j] = table
        for v in pts:
            self.inc[v].append(j)
        for a, b in combinations(pts, 2):
            self.lifts[freeze([a, b])] = j
        for s, r in table.items():
            self.next[j, s] = tuple(freeze(t-s) for t, q in table.items() if s < t and q == r+1)
            self.prev[j, s] = tuple(freeze(s-t) for t, q in table.items() if t < s and q == r-1)

    def add_pair(self, j, a, b):
        self.add_block(j, {a, b}, {freeze(): 0, freeze([a]): 1, freeze([b]): 1, freeze([a, b]): 2})

    @staticmethod
    def center(a, j):
        return a[:-1] if len(a) > 1 and a[-2] == j else a+(j,)

    @staticmethod
    def point(c, v):
        return c[:-1] if c[-2] == v else c+(v,)

    def adjacent(self, a, v):
        j = self.lifts[freeze([a[-1], v])]
        return self.point(self.center(a, j), v)

    def extend_word(self, begin, word):
        a, support, tips = begin, {begin}, []
        for v in word:
            j = self.lifts[freeze([a[-1], v])]
            c = self.center(a, j)
            b = self.point(c, v)
            assert len(b) > len(a)
            if j in self.gates:
                u, t, w, _, _ = self.gates[j]
                if w is not None and {a[-1], v} == {u, t}:
                    support.add(self.point(c, w))
            support.add(b)
            tips.append(b)
            a = b
        return support, tips

    def from_words(self, r, s, root=True):
        key = (r, s, root)
        if key not in self._members:
            h = self.adjacent((self.O,), self.H) if root else (self.H,)
            rw = tuple(self.r[i % len(self.r)] for i in range(r))
            sw = tuple(self.wide[0][i % len(self.wide[0])] for i in range(s))
            rs, rt = self.extend_word(h, rw)
            ss, st = self.extend_word(h, sw)
            D = freeze(rs | ss | ({(self.O,)} if root else set()))
            assert self.rank(D) == 1 + int(root) + r + s
            self._members[key] = D, (rt[-1] if rt else h), (st[-1] if st else h)
        return self._members[key]

    def cells(self, D):
        cells = defaultdict(set)
        for a in D:
            for j in self.inc[a[-1]]:
                cells[self.center(a, j)].add(a[-1])
        return cells

    def rank(self, D):
        groups = set()
        for a in D:
            for j in self.inc[a[-1]]:
                if j in self.gates and self.gates[j][2] == a[-1]:
                    c = self.center(a, j)
                    x, y = self.gates[j][:2]
                    if self.point(c, x) in D and self.point(c, y) in D:
                        groups.add(c)
        return len(D)-len(groups)

    def options(self, D):
        if D not in self._ext:
            changes = []
            for c, pts in self.cells(D).items():
                for ds in self.next[c[-1], freeze(pts)]:
                    delta = freeze(self.point(c,v) for v in ds)
                    changes.append(delta)
            assert len(changes) == len(set(changes))
            self._ext[D] = tuple(sorted(changes, key=sorted))
            self.prices[D] = len(changes)
        return self._ext[D]

    def price(self, D):
        if D not in self.prices:
            self.prices[D] = sum(len(self.next[c[-1],freeze(pts)]) for c,pts in self.cells(D).items())
        return self.prices[D]

    def parents(self, D):
        if D not in self._par:
            cells = self.cells(D)
            used = Counter()
            for c, pts in cells.items():
                if len(pts) >= 2:
                    used.update(self.point(c,v) for v in pts)
            parents = set()
            for c, pts in cells.items():
                if len(pts) < 2:
                    continue
                for ds in self.prev[c[-1], freeze(pts)]:
                    delta = freeze(self.point(c,v) for v in ds)
                    if any(used[a] > 1 for a in delta):
                        continue
                    parent = D - delta
                    if any(a[-1] in self.originals for a in parent):
                        parents.add(parent)
            self._par[D] = tuple(sorted(parents, key=lambda x: sorted(D-x)))
        return self._par[D]

    def address(self, a):
        if a not in self._js:
            self._js[a] = '/'.join(self.names[v] for v in a[::2]) + (
                '/+' if len(a) % 2 == 0 else '')
        return self._js[a]

    def ids(self, D):
        return sorted(self.address(a) for a in D)

    def third_limits(self):
        if not any(g[2] is not None for g in self.gates.values()):
            return None, None, False
        bad_r = None
        for i in range(1,len(self.r)+2):
            a, b = self.r[(i-1)%len(self.r)], self.r[i%len(self.r)]
            j = self.gate_of.get(freeze((a,b)))
            if j is not None and not self.gates[j][4]:
                bad_r = i
                break
        return bad_r, None if self.strict[1] else len(self.strict[0]), True

    def third_cap(self):
        rm, sm, exists = self.third_limits()
        if not exists: return 0
        if rm is None and sm is None: return None
        m = min(x for x in (rm, sm) if x is not None)
        return 1 + min(m+1, rm if rm is not None else m+1) + min(m+1, sm if sm is not None else m+1)

    def third_candidates(self, n):
        if n not in self._thirds:
            rm, sm, exists = self.third_limits()
            out = set()
            if exists:
                for r in range(max(0,(n-1)//2-1), (n-1)//2+3):
                    s = n-r-1
                    if s >= 0 and abs(r-s) <= 1 and (rm is None or r<=rm) and (sm is None or s<=sm):
                        out.add(self.from_words(r,s,False)[0])
            self._thirds[n] = out
        return self._thirds[n]

    @staticmethod
    def rebase(D, root):
        def one(a):
            i=0
            while i<min(len(root),len(a)) and root[i]==a[i]: i+=1
            return root[i-1:][::-1]+a[i:]
        return freeze(one(a) for a in D)

    def is_third(self, D):
        # Establish membership at the parent's own cut before examining its child.
        models = self.third_candidates(self.rank(D))
        return bool(models) and any(self.rebase(D,h) in models for h in D if h[-1] == self.H)

    def class_id(self, D):
        if D not in self._classes:
            anchor = min(a[-1] for a in D if a[-1] in self.originals)
            rooted = min(self.ids(self.rebase(D, a)) for a in D if a[-1] == anchor)
            self._classes[D] = record_hash(rooted)
        return self._classes[D]

    def payment(self, old, child, classify=False):
        delta = child-old
        options = self.options(old)
        assert delta in options
        out = {'removed': self.ids(delta), 'grant': len(options),
               'chosen_slot_in_this_rooting': options.index(delta), 'retains_O': (self.O,) in old}
        if classify:
            out['current_third'] = self.is_third(old)
            out['paid_name_parent_child'] = [self.class_id(old), self.class_id(child)]
        return out

    def bindings(self, D, detailed=False):
        first = set()
        for c, pts in self.cells(D).items():
            for selected, r in self.rank_tables[c[-1]].items():
                if r == 2 and selected<=pts:
                    first.add(freeze(self.point(c,v) for v in selected))
        second = set()
        for x in first:
            second.update(x|ds for ds in self.options(x) if ds <= D)
        by_law = {}
        for law, (one,two) in self.raw_cuts.items():
            bound = {}
            physical = {}
            def literal(part,birth):
                if detailed:
                    physical[self.class_id(part)] = {k:birth[k] for k in ('holder','parents','consumed_names','fresh_names','grant')}
            for x in first:
                input_set = freeze(a[-1] for a in x if a[-1] in self.originals)
                paid = one[input_set]
                assert paid['grant'] == self.price(x)
                bound[x] = paid['holder']
                literal(x,paid)
            ids = []
            for x in second:
                pax = self.parents(x)
                inp = freeze(bound[p] for p in pax)
                paid = two[inp]
                assert len(inp)==len(pax) and paid['grant']==self.price(x)
                ids.append(paid['holder'])
                literal(x,paid)
            by_law[law] = {'rank_2': sorted(bound.values()), 'rank_3': sorted(ids)}
            if detailed: by_law[law]['native_ancestral_classes'] = physical
        assert by_law['nae'] == by_law['parity']
        return by_law['parity']

    def earlier(self, D):
        # Complete deletion ancestry with the same physical rooted name coding
        # across the two preparations, and all distinct literal original IDs.
        seen, todo, records = set(), [D], []
        leaves = set()
        histogram = Counter()
        while todo:
            x = todo.pop()
            if x in seen: continue
            seen.add(x)
            payers = self.parents(x)
            histogram[self.rank(x)] += 1
            if not payers:
                assert len(x)==1
                leaves.update(a[-1] for a in x)
            records.append([self.ids(x), self.price(x), sorted(self.ids(x-p) for p in payers)])
            todo.extend(payers)
        assert leaves=={a[-1] for a in D}
        return {'rooted_subsupports':len(seen), 'counts_by_rank':dict(sorted(histogram.items())),
                'actual_original_ids':sorted(leaves), 'actual_original_labels':sorted(self.names[i] for i in leaves),
                'complete_parent_and_grant_sha256':record_hash(sorted(records)),
                'canonical_subhistory_records':sorted(records),
                'all_name_count':len(set().union(*(self.src[i] for i in leaves))),
                'literal_two_cuts':self.bindings(D,detailed=True)}

    def pulse(self, j, wide=False):
        loop, ok = self.wide if wide else self.strict
        if not ok:return None
        return tuple(loop[k%len(loop)] for k in range(j*len(loop)+1))

    def has_word(self, D, word):
        if word is None:return False
        for a in D:
            if a[-1] != word[0]:continue
            at=a
            for v in word[1:]:
                at = self.adjacent(at,v)
                if at not in D:break
            else:return True
        return False

    def receipt(self,D,Y,word):
        assert self.has_word(Y,word) and not self.has_word(D,word)
        parents=[]
        for par in self.parents(Y):
            paid=self.payment(par,Y)
            paid['selected_previous']=par==D
            paid['carries_pulse']=self.has_word(par,word)
            parents.append(paid)
        assert any(x['selected_previous'] for x in parents)
        assert any(not x['retains_O'] and x['carries_pulse'] for x in parents)
        return {'rank':self.rank(Y),'grant':self.price(Y),'physical_parents':parents,
                'all_O_parents_first':all(not x['carries_pulse'] for x in parents if x['retains_O']),
                'earliest_on_selected_chain':True}

    def all_options(self,D,tip):
        rows=[]
        for delta in self.options(D):
            Y = D|delta
            all_paid = []
            for P in self.parents(Y):
                q = self.payment(P,Y,classify=True)
                q['selected_previous'] = P==D
                all_paid.append(q)
            assert any(q['selected_previous'] for q in all_paid)
            tip_p = self.lifts.get(freeze([tip[-1],self.p]))
            p = self.point(self.center(tip,tip_p),self.p) if tip_p is not None else None
            rows.append({'added':self.ids(delta),'donors_added':sorted(self.names[a[-1]] for a in delta),
                         'prior_tip_to_p':p in delta,'p_only':p in delta and len(delta)==1,
                         'grant':self.price(Y),'parents':all_paid})
        return rows

    def source_pulses(self):
        out={}
        for j in range(1,5):
            private = self.pulse(j)
            wider = self.pulse(j,True)
            expected = tuple(self.roles['S'+str(i%7)] for i in range(7*j+1))
            missing=[i for i,(a,b) in enumerate(pairwise(expected),1) if freeze((a,b)) not in self.lifts]
            row={'missing_private_meetings':missing,'wider_size':len(wider)}
            if private:
                assert expected==private and not missing
                points,_=self.extend_word((private[0],),private[1:])
                D=freeze(points)
                row.update(rank=self.rank(D),grant=self.price(D),true_parents=[self.payment(p,D) for p in self.parents(D)],
                           closing_occurrence=self.ids([max(points,key=len)])[0], native=self.bindings(D))
            else: assert missing
            out[str(j)]=row
        return out

    def direct_strong(self):
        if not self.strict[1]:return None
        out={}
        for j in range(1,5):
            word=self.pulse(j)
            D=self.from_words(0,len(word)-1)[0];Y=self.from_words(0,len(word))[0]
            hit=self.receipt(D,Y,word)
            assert hit['all_O_parents_first']
            out[str(j)]=hit
        return out

    def chain(self,tie):
        first=None
        marked=[]
        p_only=[]
        pulses={}
        shams={}
        critical=None
        prefix_options=[{'rank':1,'options':sorted(self.ids(x) for x in self.options(freeze([(self.O,)]))),
                         'chosen':[self.address(self.adjacent((self.O,),self.H))]}]
        q_ranks=[]
        r=s=0
        for _ in range(2*(len(self.wide[0])*4+2)):
            D, tip, _ = self.from_words(r,s)
            grow_s=s<r or (s==r and tie=='S')
            if grow_s:s+=1
            else:r+=1
            Y, rt, st=self.from_words(r,s)
            added=Y-D
            rank=self.rank(Y)
            if r<=10 and s<=10:
                prefix_options.append({'rank':rank-1,'options':sorted(self.ids(x) for x in self.options(D)),
                                       'chosen':self.ids(added)})
            assert added in self.options(D) and D in self.parents(Y)
            if not grow_s and rt[-1]==self.q and self.is_third(Y-{(self.O,)}):
                q_ranks.append(rank-1)
            if not grow_s and rt[-1]==self.p:
                if first is not None:
                    marked.append(rank)
                    if len(added)==1:p_only.append(rank)
                else:first=rank
            if not grow_s and r==10:
                critical={'rank':rank,'r':r,'s':s,'previous_grant':self.price(D),
                          'selected_change':self.ids(added),'selected_grant':self.price(Y),
                          'selected_names':sorted(self.names[a[-1]] for a in added),'tip':self.address(tip),
                          'preceding':self.ids(D),'all_options':self.all_options(D,tip),
                          'selected_payments':[self.payment(P,Y,True) for P in self.parents(Y)],
                          'incoming_prior_loose_inventory':[
                              {'parent_class':self.class_id(P),'loose_name_children':sorted(self.class_id(P|delta) for delta in self.options(P))}
                              for P in self.parents(Y) if (self.O,) not in P],
                          'earlier':self.earlier(D), 'native_parts':self.bindings(Y)}
            if not grow_s:continue
            for wide, records in ((False,pulses),(True,shams)):
                for j in range(1,5):
                    w=self.pulse(j,wide)
                    if not w or len(w)!=s: continue
                    hit=self.receipt(D,Y,w)
                    hit.update(send_size=len(w),receiver_end=self.names[st[-1]],signal_end=self.names[w[-1]],
                               signal_incoming=self.names[w[-2]],receiver_incoming=self.names[st[-3]],
                               receiver_port=self.port[st[-1],st[-3]],last_p=marked[-1] if marked else None,
                               delay=rank-len(w),native_parts=self.bindings(Y))
                    records[str(j)]=hit
        def interval(rows):
            if not rows:return None
            a,b=rows['1']['rank'],rows['2']['rank']
            return {'bounds':[a,b], 'p':[x for x in marked if a<x<=b], 'p_only':[x for x in p_only if a<x<=b],
                    'send_spacing':rows['2']['send_size']-rows['1']['send_size'],'receipt_spacing':b-a}
        traversed = self.gate_of.get(freeze(self.r[8:10]))
        first_ternary = (2+2*10-int(tie=='R')) if traversed in self.gates and self.gates[traversed][2] is not None else None
        repeated_ternaries = [i for i in range(1, len(self.r)+1)
                              if (j := self.gate_of.get(freeze((self.r[i-1], self.r[i%len(self.r)])))) is not None
                              and self.gates[j][2] is not None]
        assert (first_ternary is None) == (not repeated_ternaries)
        strict_read={'complete_original_binary_crossing_to_second_private_pulse': bool(pulses) and first_ternary is None,
                     'first_inadmissible_circuit_birth_rank': first_ternary,
                     'first_private_receipt_before_original_three':bool(pulses and (not first_ternary or pulses['1']['rank']<first_ternary)),
                     'all_later_births_require_exactly_two_parents':bool(pulses) and
                         all(len(p['physical_parents'])==2 for p in pulses.values())}
        return {'tie':tie,'startup':first,'thin_reader':strict_read,'turns':marked,'p_only_turns':p_only,'q_occurrences_in_third':q_ranks,
                'private':pulses,'registered_interval':interval(pulses),'wide':shams,'wide_interval':interval(shams),
                'critical':critical,'earlier_admitted_options':prefix_options}

    def balanced(self):
        if not self.strict[1]:return None
        s1,s2=map(len,[self.pulse(1),self.pulse(2)])
        states={(0,0,None,0,0):1}
        ends=Counter()
        while states:
            nxt=Counter()
            for (r,s,first,turns,one),n in states.items():
                for dr,ds in ((1,0),(0,1)):
                    rr,ss=r+dr,s+ds
                    if abs(rr-ss)>1:continue
                    a=2+rr+ss
                    start=a if ds and ss==s1 else first
                    added=self.from_words(rr,ss)[0]-self.from_words(r,s)[0]
                    scored=int(bool(first and dr and self.r[(rr-1)%len(self.r)]==self.p))
                    t=turns+scored;u=one+int(scored and len(added)==1)
                    if ds and ss==s2:
                        ends[start,a,t,u]+=n
                    else:
                        nxt[rr,ss,start,t,u]+=n
            states=nxt
        return [{'first':a,'second':b,'p':t,'p_only':u,'chains':n} for (a,b,t,u),n in sorted(ends.items())]

    def run(self):
        if not self.raw_cuts: return {'case':self.case,'funded':False}
        rm,sm,exists=self.third_limits()
        third={'founding_w_test_exists':exists,'max_r':rm,'max_s':sm,'max_rank':self.third_cap(),
               'r_period':len(self.r),'q_per_r_period':self.r.count(self.q)}
        for r in range(1,2*len(self.r)+1):
            if self.r[(r-1)%len(self.r)]==self.q:
                third.setdefault('balanced_q_even',[]).append({'r':r,'rank':1+2*r,
                              'qualifies':self.from_words(r,r,False)[0] in self.third_candidates(1+2*r)})
        return {'case':self.case,'funded':True,'source_pulses':self.source_pulses(),'third':third,
                'r_period':len(self.r),'p_per_r_period':self.r.count(self.p),'S_first':self.chain('S'),
                'R_first':self.chain('R'),'open_balance':self.balanced(),'direct_strong':self.direct_strong()}




def test_small(record):
    world = World(record, small=True)
    source = {world.class_id(freeze([(v,)])):(freeze([(v,)]),v) for v in world.originals}
    results = {}
    for law, native in record['laws'].items():
        previous = source
        layers = []
        for cut in native['cuts']:
            physical = {freeze(x['parents']):x for x in cut['births']}
            predicted = {}
            for old, _ in previous.values():
                for delta in world.options(old):
                    member = old | delta
                    predicted.setdefault(world.class_id(member),member)
            archived = {}
            evidence = []
            for identity, member in predicted.items():
                parents = world.parents(member)
                real_ids = freeze(previous[world.class_id(p)][1] for p in parents)
                birth = physical[real_ids]
                assert len(real_ids)==len(parents)
                assert birth['grant']==world.price(member)
                archived[identity]=(member,birth['holder'])
                evidence.append([birth['holder'],sorted(real_ids),birth['grant'],identity])
            assert len(predicted)==len(physical)==len(set(row[0] for row in evidence))
            layers.append({'rank':world.rank(next(iter(predicted.values()))),'matched':len(evidence),
                           'physical_and_support_bindings':sorted(evidence)})
            previous = archived
        results[law]=layers
    assert results['parity']==results['nae']
    return {'mode':record['case'], 'layers_per_law':results['parity']}


def comparisons(cases):
    by_name = {c['case']:c for c in cases}
    pairs = [('intact','near'),('intact','intact_w_disabled'),('near','near_w_enabled'),
             ('intact','remote'),('intact_s_break','near_s_break'),('m_intact','m_near'),
             ('t_intact','t_near'),('neither_intact','neither_near')]
    rows = []
    for left, right in pairs:
        for policy in ('S_first','R_first'):
            a, b = by_name[left][policy], by_name[right][policy]
            c, e = a['critical'], b['critical']
            ao, bo = ({tuple(o['added']):o for o in entry['all_options']} for entry in (c,e))
            def names_and_groups(entry):
                groups = []
                for o in entry['all_options']:
                    charged = [p['paid_name_parent_child'] for p in o['parents']]
                    assert len({tuple(x) for x in charged})==len(charged)
                    for p in o['parents']:
                        if p['current_third']:
                            groups.append([o['added'],p['paid_name_parent_child'],p['grant']])
                return groups
            def boundaries(scope):
                return [[h['rank'],h['grant'],sorted([p['grant'] for p in h['physical_parents']]),
                         h['receiver_end'],h['receiver_incoming'],h['receiver_port']] for h in scope['private'].values()]
            assert c['earlier']['canonical_subhistory_records']==e['earlier']['canonical_subhistory_records']
            assert c['earlier']['complete_parent_and_grant_sha256']==e['earlier']['complete_parent_and_grant_sha256']
            assert boundaries(a)==boundaries(b)
            one = c['earlier']['literal_two_cuts']['native_ancestral_classes']
            two = e['earlier']['literal_two_cuts']['native_ancestral_classes']
            assert one.keys()==two.keys()
            original_input_names_match = all(one[i]['consumed_names']==two[i]['consumed_names']
                 for i in one if one[i]['holder'] in c['earlier']['literal_two_cuts']['rank_2'])
            if left=='intact' and right=='near': assert one==two
            for entry in (c,e):
                for payer in entry['incoming_prior_loose_inventory']:
                    assert len(payer['loose_name_children'])==len(set(payer['loose_name_children']))
                    incoming,=[v for v in entry['selected_payments'] if not v['retains_O']]
                    assert incoming['paid_name_parent_child'][0]==payer['parent_class']
                    assert incoming['paid_name_parent_child'][1] in payer['loose_name_children']
                    assert incoming['grant']==len(payer['loose_name_children'])
            prefix = zip(a['earlier_admitted_options'],b['earlier_admitted_options'],strict=True)
            old_options = []
            selected = []
            for old, new in prefix:
                assert old['rank']==new['rank']
                if old['options']!=new['options']:old_options.append(old['rank'])
                if old['chosen']!=new['chosen']:selected.append(old['rank']+1)
            rows.append({'left':left, 'right':right, 'policy':policy,
                         'complete_earlier_parent_and_grant_match':True,
                         'original_ids_one_common_reference':c['earlier']['actual_original_ids'],
                         'private_boundaries_fields':boundaries(a),'private_boundary_field_match':True,
                         'native_first_two_earlier_classes':len(one),'literal_first_two_earlier_rows_identical':one==two,
                         'literal_original_input_names_on_used_histories_identical':original_input_names_match,
                         'common_prebirth_options':len(ao.keys() & bo.keys()),
                         'first_difference_in_earlier_alternatives_at_parent':min(old_options,default=None),
                         'first_difference_in_selected_advancement_at_child':min(selected,default=None),
                         'only_left':sorted(ao.keys()-bo.keys()), 'only_right':sorted(bo.keys()-ao.keys()),
                         'qualified_physical_payments_left':names_and_groups(c),
                         'qualified_physical_payments_right':names_and_groups(e),
                         'distinct_p_options':[sum('p' in row['donors_added'] for row in opt.values()) for opt in (ao,bo)],
                         'bounds_and_repeated_p':[z['registered_interval'] for z in (a,b)],
                         'wider_intervals':[z['wide_interval'] for z in (a,b)]})
    return rows



def compact_earlier(rows):
    # Every displayed digest refers to one full sorted receipt. Verify exact
    # table equality before sharing storage across formally distinct starts.
    tables = {}
    for row in rows:
        if not row['funded']: continue
        for arm in ('S_first','R_first'):
            history = row[arm]['critical']['earlier']
            key = history['complete_parent_and_grant_sha256']
            records = history.pop('canonical_subhistory_records')
            assert tables.setdefault(key,records)==records
    return tables


def bind_whole_state(rows, source):
    results = {v['case']:v for v in rows}
    physical = {v['case']:v for v in source['cases']}
    checks = []
    for pair in source['projected_state_comparisons']:
        keys = [k for k in pair['grades'] if k.startswith('selected') or k=='same_donor_ids_control']
        key, = keys
        grade = pair['grades'][key]
        for law, table in grade['laws'].items():
            sides = []
            for side in ('first','second'):
                case = pair[side]
                earlier = results[case]['S_first']['critical']['earlier']
                projected = table[side]
                ids = earlier['actual_original_ids']
                assert projected['occupied_original_donors']==ids
                names = set().union(*(physical[case]['original_stars'][v] for v in ids))
                assert sorted(names)==projected['projected_name_ids']
                assert len(names)==earlier['all_name_count']
                sides.append({'originals':len(ids), 'retained_names':len(names), 'entire_spent_factors':len(projected['spent_factors'])})
            checks.append({'preparations':[pair['first'],pair['second']], 'law':law, 'sources':sides,
                           'exact_projected_relations_equal':table['equal']})
    return checks


def check_literal_knot(src):
    g=src['gates']['P']
    witness=g['small_witnesses'][0]
    indices=src['original_stars'][witness]
    assert len(indices)==3
    names=['d'+str(i) for i in indices]
    results={}
    for law in ('parity','nae'):
        denied = [x for x in range(8) if (x.bit_count()%2==1 if law=='parity' else x in (0,7))]
        clauses=[' '.join(('~' if (x>>j)&1 else '')+v for j,v in enumerate(names)) for x in denied]
        env=dict(os.environ,PYTHONPATH=str(HERE.parents[1]/'tools'))
        run=subprocess.run([sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),
            '--loops',*names[:2],'--contact',names[2],'--json'],env=env,check=True,capture_output=True,text=True)
        result=json.loads(run.stdout)
        assert result['is_knot'] and result['binding'] and result['invisible_in_parts'] and result['coexistence']
        results[law]=result
    return {'original_spent_holder':witness,'actual_name_ids':indices,'canonical_readings':results}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--case')
    args=ap.parse_args()
    with gzip.open(HERE/'native.json.gz','rt') as f:
        obj=json.load(f)
    rows=[]
    for src in obj['cases']:
        if args.case and args.case!=src['case']: continue
        world=World(src)
        rows.append(world.run())
    if args.case:
        print(json.dumps(rows[0],sort_keys=True))
    else:
        contrasts=comparisons(rows)
        earlier=compact_earlier(rows)
        out={'schema':'B285-actual-receiver-v1','native_sha256':sha256((HERE/'native.json.gz').read_bytes()).hexdigest(),
             'later_loose_name_convention':'A name is identified by its physical parent and its unique possible child. The listed ordinal is in the displayed rooting; the (parent,child) identity is independent of that rooting.',
             'shared_law_output':'All rank-two and rank-three subhistories were matched to both native rosters; the proof supplies the same later supports and grants under parity and not-all-equal.',
             'cases':rows,'matched_comparisons':contrasts,'exact_earlier_parent_and_grant_tables':earlier,
             'complete_small_native_map':[test_small(c) for c in obj['calibrations']],
             'whole_state_on_actual_originals':bind_whole_state(rows,obj),
             'literal_canonical_knot_check':check_literal_knot(obj['cases'][0])}
        data=gzip.compress((json.dumps(out,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
        (HERE/'receipts.json.gz').write_bytes(data)
        print(len(rows),'preparations',len(data),'compressed bytes',sha256(data).hexdigest())


if __name__=='__main__':
    main()
