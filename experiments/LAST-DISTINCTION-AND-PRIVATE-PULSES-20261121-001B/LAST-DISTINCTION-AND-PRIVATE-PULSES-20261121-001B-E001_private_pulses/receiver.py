"""Reconstruct the scoped receivers from actual donor/name incidence. No outcome table is an input."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, pairwise
from pathlib import Path
import gzip
import json

import networkx as nx


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class World:
    def __init__(self, record):
        self.case = record['case']
        self._carrier_cache = {}
        self.stars = [frozenset(v) for v in record['original_stars']]
        self.names = {i:k for k,i in record['live_roles'].items()}
        self.role = record['live_roles']
        owners = defaultdict(list)
        for i, row in enumerate(self.stars):
            for x in row:
                owners[x].append(i)
        self.loose = {i:sorted(x for x in row if len(owners[x])==1)
                      for i,row in enumerate(self.stars) if any(len(owners[x])==1 for x in row)}
        assert set(self.loose)==set(self.names)
        self.g = nx.Graph()
        self.g.add_nodes_from(self.loose)
        self.port = {}
        self.witness = {}
        for w,row in enumerate(self.stars):
            if w in self.loose or not row:
                continue
            sides=defaultdict(list)
            for x in row:
                others=set(owners[x])-{w}
                assert len(others)==1
                sides[others.pop()].append(x)
            assert len(sides)==2
            a,b=sorted(sides)
            assert not self.g.has_edge(a,b)
            self.g.add_edge(a,b)
            self.witness[frozenset((a,b))]=w
            self.port[a,b]=frozenset(sides[a])
            self.port[b,a]=frozenset(sides[b])
        assert nx.transitivity(self.g)==0
        self.funded=all(len(self.loose[i])==self.g.degree(i) for i in self.g)
        def anchor(a,b):
            return [(i,j) for i,j in self.port if self.count(i,j)==a and self.count(j,i)==b]
        h_c=anchor(1,11);h_s=anchor(1,13);o_h=anchor(1,17)
        assert len(h_c)==len(h_s)==1 and h_c[0][0]==h_s[0][0]
        self.H,self.c0=h_c[0];_,self.S=h_s[0]
        self.O=o_h[0][0] if o_h else None
        assert self.O is None or o_h==[(self.O,self.H)]
        self.circuit={v:sorted((u for u in self.g[v] if min(self.count(v,u),self.count(u,v))>=3),
                               key=lambda u:self.count(v,u)) for v in self.g}
        self.cmark={v for v in self.g if any(self.count(v,u)==3 for u in self.circuit[v])}
        self.p,=[v for v in self.circuit[self.c0] if len(self.circuit[v])==8]
        self.orbit=self.cycle(self.c0,self.p)
        self.q=next(v for v in self.orbit if len(self.circuit[v])==4)
        self.strict=self.corridor({2})
        self.broad=self.corridor({2,6})
        assert self.broad[1] and self.broad[0][0]==self.S
        self.src_rank_ids={}
        if self.funded:
            for law,native in record['laws'].items():
                one={frozenset(x['parents']):x for x in native['cuts'][0]['births']}
                two={frozenset(x['parents']):x for x in native['cuts'][1]['births']}
                assert set(one)==set(self.witness)
                self.src_rank_ids[law]=(one,two)

    def count(self,a,b):
        return len(self.port[a,b])

    def name(self,v):
        return self.names[v]

    def labels(self,word):
        return [self.name(v) for v in word]

    def cycle(self,a,b):
        first=(a,b);seen=set();out=[]
        while (a,b) not in seen:
            seen.add((a,b));out.append(a)
            options=self.circuit[b]
            assert len({self.count(b,v) for v in options})==len(options)
            a,b=b,options[(options.index(a)+1)%len(options)]
        assert (a,b)==first
        return tuple(out)

    def corridor(self,amounts):
        def nexts(v):
            return [u for u in self.g[v] if self.count(v,u) in amounts and self.count(u,v)==4]
        sequence=[];current=self.S
        while current not in sequence:
            sequence.append(current)
            after=nexts(current)
            if len(after)!=1 or len(nexts(after[0]))!=1:
                return tuple(sequence),False
            current=after[0]
        assert current==self.S
        return tuple(sequence),True

    @staticmethod
    def rep(orbit,length):
        return tuple(orbit[i%len(orbit)] for i in range(length))

    def r(self,n):
        return self.rep(self.orbit,n)

    def s(self,n):
        return self.rep(self.broad[0],n)

    @staticmethod
    def along(start,roles):
        a=start
        out=[]
        for v in roles:
            assert len(a)<2 or a[-2]!=v
            a=a+(v,);out.append(a)
        return out

    def branched(self,r,s,origin=True):
        if origin:
            assert self.O is not None
            h=(self.O,self.H);nodes={(self.O,),h}
        else:
            h=(self.H,);nodes={h}
        ra=self.along(h,self.r(r));sa=self.along(h,self.s(s))
        return frozenset(nodes|set(ra)|set(sa)),ra,sa

    def adjacent(self,addr,v):
        assert self.g.has_edge(addr[-1],v)
        return addr[:-1] if len(addr)>1 and addr[-2]==v else addr+(v,)

    def child_slots(self,D):
        return [(a,u,self.adjacent(a,u)) for a in sorted(D) for u in sorted(self.g[a[-1]])
                if self.adjacent(a,u) not in D]

    def price(self,D):
        return 2+sum(self.g.degree(a[-1])-2 for a in D)

    def leaves(self,D):
        return sorted(a for a in D if sum(self.adjacent(a,u) in D for u in self.g[a[-1]])==1)

    def encode(self,a):
        return '/'.join(self.labels(a))

    def footprint(self,D):
        return sorted(self.encode(a) for a in D)

    def discharge(self,D,full=False):
        if len(D)==1:return []
        out=[]
        for a in self.leaves(D):
            old=D-{a}
            b,=[self.adjacent(a,u) for u in self.g[a[-1]] if self.adjacent(a,u) in old]
            slots=self.child_slots(old)
            ix=next(i for i,(site,v,new) in enumerate(slots) if site==b and new==a)
            assert len(slots)==self.price(old) and len({new for _,_,new in slots})==len(slots)
            record={'deleted':self.encode(a),'removed_donor':self.name(a[-1]),'grant':self.price(old),
                    'slot':[self.encode(b),self.name(a[-1])],'slot_index':ix,
                    'retains_O':self.O is not None and (self.O,) in old}
            if full:
                record['all_slots']=[[self.encode(site),self.name(v)] for site,v,_ in slots]
            out.append((old,record))
        return out

    def groups(self,D,tip):
        rows=[]
        for a,u,new in self.child_slots(D):
            Y=D|{new}
            rows.append({'site':self.encode(a),'to':self.name(u),'attached_at_receiver_tip':a==tip,
                         'registered_p_option':a==tip and u==self.p,'new_p_at_another_site':a!=tip and u==self.p,
                         'witness':self.witness[frozenset((a[-1],u))],
                         'grant':self.price(Y),'all_true_parent_grants':sorted(row['grant'] for _,row in self.discharge(Y))})
        assert len(rows)==self.price(D)
        return rows

    def pulse(self,j,broad=False):
        orbit,ok=self.broad if broad else self.strict
        if not ok:return None
        return self.rep(orbit,j*len(orbit)+1)

    def packet_nodes(self,D,word):
        if not word:return []
        hits=[]
        for a in sorted(D):
            if a[-1]!=word[0]:continue
            length=[a];at=a
            for v in word[1:]:
                if not self.g.has_edge(at[-1],v):break
                at=self.adjacent(at,v)
                if at not in D:break
                length.append(at)
            if len(length)==len(word):hits.append(tuple(length))
        return hits

    def charge_record(self,D,old,packet):
        hits=self.packet_nodes(D,packet)
        rows=[]
        for par,x in self.discharge(D):
            x['packet_occurrences']=len(self.packet_nodes(par,packet))
            x['selected_previous']=par==old
            rows.append(x)
        return {'rank':len(D),'grant':self.price(D),'packet_occurrences':len(hits),'parents':rows,
                'selected_first':bool(hits) and not self.packet_nodes(old,packet),
                'all_O_parents_first':bool(hits) and all(not x['packet_occurrences'] for x in rows if x['retains_O']),
                'O_free_paying_incoming':any(x['packet_occurrences'] for x in rows if not x['retains_O'])}

    def span_path(self,word):
        assert word and all(self.g.has_edge(a,b) for a,b in pairwise(word))
        return frozenset({(word[0],),*self.along((word[0],),word[1:])})

    def slot_bind(self,D):
        pairs={}
        triples={}
        for law,(one,two) in self.src_rank_ids.items():
            buys={}
            for a in D:
                for v in self.g[a[-1]]:
                    b=self.adjacent(a,v)
                    if b in D and a<b:
                        x=one[frozenset((a[-1],b[-1]))]
                        assert x['grant']==self.price({a,b})
                        buys[frozenset((a,b))]=x['holder']
            tr=[]
            for b in sorted(D):
                n=sorted(self.adjacent(b,v) for v in self.g[b[-1]] if self.adjacent(b,v) in D)
                for a,c in combinations(n,2):
                    x=two[frozenset((buys[frozenset((a,b))],buys[frozenset((b,c))]))]
                    assert x['grant']==self.price({a,b,c})
                    tr.append(x['holder'])
            pairs[law]=sorted(buys.values());triples[law]=sorted(tr)
        assert pairs['parity']==pairs['nae'] and triples['parity']==triples['nae']
        return {'pairs':pairs['parity'],'triples':triples['parity']}

    def cap(self):
        rmax=next((i for i,v in enumerate(self.orbit) if v not in self.cmark),None)
        smax=None if self.strict[1] else len(self.strict[0])
        if rmax is None and smax is None:return None,{'r':None,'s':None}
        m=min(k for k in (rmax,smax) if k is not None)
        r=min(m+1,rmax) if rmax is not None else m+1
        s=min(m+1,smax) if smax is not None else m+1
        return 1+r+s,{'r':r,'s':s}

    def third(self,r,s):
        return (abs(r-s)<=1 and all(v in self.cmark for v in self.r(r)) and
                (self.strict[1] or s<=len(self.strict[0])) and
                self.s(s)==(self.rep(self.strict[0],s) if self.strict[1] else self.strict[0][:s]))

    def sender_data(self):
        ans={}
        literal=tuple(self.role['S'+str(i)] for i in range(7))
        for j in range(1,5):
            word=self.pulse(j)
            enrolled=self.rep(literal,7*j+1)
            native=all(self.g.has_edge(a,b) for a,b in pairwise(enrolled))
            x={'enrolled_literal_native':native,'mixed_return_size':len(self.pulse(j,True)),
               'broken_private_steps':[i+1 for i,(a,b) in enumerate(pairwise(enrolled)) if not self.g.has_edge(a,b)]}
            if word is not None:
                assert word==enrolled and native
                D=self.span_path(word)
                x.update(rank=len(D),originals=self.labels(word),grant=self.price(D),
                         parents=[row for _,row in self.discharge(D,full=True)],native_parts=self.slot_bind(D))
                closing_pair=(self.role['S3'],self.role['S4'])
                x['private_exchange_witness_traversal_edges']=[i+1 for i,edge in enumerate(pairwise(word))
                                                              if edge==closing_pair]
                x['sender_root_and_closing_lift']=[self.encode(min(D,key=len)),self.encode(max(D,key=len))]
                if j==1:
                    tip=max(D,key=len)
                    x['paid_departures_after_first_private_turn']=[g for g in self.groups(D,tip) if g['attached_at_receiver_tip']]
            else:assert not native
            ans['U'+str(j)]=x
        for k in (2,3):
            D=self.span_path(literal[:k])
            ans['partial_size_'+str(k)]={'native':True,'grant':self.price(D),'native_parts':self.slot_bind(D)}
        return ans

    def chain(self,tie):
        r=s=0
        marked=[];third_q=[];pfirst=None;qfirst=None
        pulses={};shams={};critical=[]
        for _ in range(2*(4*len(self.broad[0])+3)):
            choose_s=s<r or (s==r and tie=='S')
            D,ra,sa=self.branched(r,s)
            if choose_s:s+=1
            else:r+=1
            Y,ry,sy=self.branched(r,s)
            new,=Y-D
            if not choose_s and new[-1]==self.p:
                if pfirst is None:pfirst=len(Y)
                else:marked.append(len(Y))
            if not choose_s and new[-1]==self.q and self.third(r,s):
                if qfirst is None:qfirst=len(Y)-1
                else:third_q.append(len(Y)-1)
            if not choose_s and r in (6,10,14):
                P=Y-{(self.O,)}
                assert P in [a for a,_ in self.discharge(Y)]
                critical.append({'rank':len(Y),'r':r,'s':s,'selected':self.name(new[-1]),
                    'registered_p':new[-1]==self.p,'current_third':self.third(r,s),
                    'membership_before_birth_at_rank':len(P),'third_globally_extinct_before_birth':
                    self.cap()[0] is not None and len(P)>self.cap()[0],
                    'prior_r_tip':self.name(ra[-1][-1]),'previous_all_p':list(marked[:-1] if new[-1]==self.p else marked),
                    'prior_support':self.footprint(D),'prior_grant':self.price(D),'child_grant':self.price(Y),
                    'all_true_payments':[x for _,x in self.discharge(Y,full=True)],
                    'all_funded_options':self.groups(D,ra[-1]),
                    'native_parts':self.slot_bind(Y)})
            if not choose_s:continue
            for mixed,storage in ((False,pulses),(True,shams)):
                for j in range(1,5):
                    word=self.pulse(j,mixed)
                    if word is None or len(word)!=s:continue
                    row=self.charge_record(Y,D,word)
                    assert row['selected_first'] and row['O_free_paying_incoming']
                    row.update(r=r,s=s,send_size=len(word),delay=len(Y)-len(word),
                               source_end=self.name(word[-1]),source_incoming=self.name(word[-2]),
                               pulse_orientation='private direction' if not mixed else 'corridor direction',
                               actual_arrival_end=self.name(new[-1]),incoming_port=self.count(new[-1],new[-2]),
                               last_p_rank=marked[-1] if marked else None,
                               latest_q_turn_from_H=third_q[-1] if third_q else None,
                               cross_ancestor_bindings=self.slot_bind(Y))
                    for par in row['parents']:
                        if par['selected_previous'] or not par['retains_O']:continue
                        assert par['removed_donor']==self.name(ry[-1][-1])
                        rr,ss=r-1,s
                        par['in_same_fixed_receiver']=0<=ss-rr<=1 if tie=='S' else 0<=rr-ss<=1
                        par['in_open_balanced_receiver']=abs(ss-rr)<=1
                    storage[str(j)]=row
        def interval(out):
            if '1' not in out or '2' not in out:return None
            first,last=out['1']['rank'],out['2']['rank']
            turns=[n for n in marked if first<n<=last]
            return {'first':first,'second':last,'turns':turns,'count':len(turns),
                    'emission_spacing':out['2']['send_size']-out['1']['send_size'],'receipt_spacing':last-first}
        return {'tie':tie,'startup_p':pfirst,'all_p_turns_checked':marked,'all_registered_q_turns_checked':third_q,
                'pulses':pulses,'interval':interval(pulses),'mixed_returns':shams,'mixed_interval':interval(shams),
                'r_period':len(self.orbit),'p_per_ordinary_steps':[self.orbit.count(self.p),2*len(self.orbit)],
                'critical_options':critical,'typed_receiver_stops_after_s':None if self.strict[1] else len(self.strict[0])}

    def balanced(self):
        if not self.strict[1]:return None
        first_s=len(self.pulse(1));last_s=len(self.pulse(2))
        # The unit counted is a chain of physical one-point additions. Distinct chains can converge.
        states={(0,0,None,0):1};totals=Counter()
        while states:
            later=Counter()
            for (r,s,first,ticks),n in states.items():
                for dr,ds in [(1,0),(0,1)]:
                    rr,ss=r+dr,s+ds
                    if abs(rr-ss)>1:continue
                    rank=2+rr+ss
                    start=rank if ds and ss==first_s else first
                    count=ticks+int(bool(dr and first and self.r(rr)[-1]==self.p))
                    if ds and ss==last_s:
                        totals[start,rank,count]+=n
                    else:later[rr,ss,start,count]+=n
            states=later
        return {'unit':'chains of actual one-point additions from O,H',
                'all_endpoint_pairs':[{'first_rank':a,'last_rank':b,'p_turns':t,'chains':n}
                                      for (a,b,t),n in sorted(totals.items())],
                'chains':sum(totals.values()),'distinct_endpoint_support_pairs':len({(a,b) for a,b,_ in totals}),
                'fixed_S_first_ranks':{str(t):n for (a,b,t),n in totals.items() if a==1+2*first_s and b==1+2*last_s}}

    def saturated(self):
        if not self.strict[1]:return None
        r=len(self.pulse(1))-1;s=len(self.pulse(1))
        I,_,_=self.branched(r,s)
        last={};ticks=[];first_rank=len(I)
        for v in range(s+1,len(self.pulse(2))+1):
            Y,_,_=self.branched(r,v)
            last=self.charge_record(Y,I,self.pulse(2))
            added,=Y-I
            if added[-1]==self.p:ticks.append(len(Y))
            I=Y
        final_rank=len(I);s=len(self.pulse(2));first_later=None
        while first_later is None or r<s:
            if r>=s:s+=1
            else:r+=1
            Y,_,_=self.branched(r,s)
            added,=Y-I
            assert I in [par for par,_ in self.discharge(Y)]
            if added[-1]==self.p and first_later is None:first_later=len(Y)
            I=Y
        return {'receipt_ranks':[first_rank,final_rank],'send_spacing':len(self.pulse(2))-len(self.pulse(1)),
                'turns':ticks,'second':last,'resumes_after_catching_up':r==s,
                'first_later_r_return_rank':first_later}

    def strong(self):
        if not self.strict[1]:return None
        out={}
        for j in range(1,5):
            w=self.pulse(j)
            dist=min(nx.shortest_path_length(self.g,self.O,v) for v in set(w))
            records=[]
            for i,v in enumerate(w):
                if nx.shortest_path_length(self.g,self.O,v)!=dist:continue
                for route in nx.all_shortest_paths(self.g,self.O,v):
                    D=set(self.span_path(tuple(route)));at=tuple(route)
                    D.update(self.along(at,reversed(w[:i])));D.update(self.along(at,w[i+1:]))
                    D=frozenset(D)
                    info=self.charge_record(D,frozenset(),w)
                    assert info['all_O_parents_first'] and len(D)==len(w)+dist
                    records.append({'attach_at_occurrence':i,'route':self.labels(route),
                                    'support':self.footprint(D),'history':info})
            assert len({tuple(x['support']) for x in records})==len(records)
            out[str(j)]={'minimum_size':len(w)+dist,'rooted_classes':len(records),'all_minima':records}
        res={}
        for laps in (0,1):
            base=(self.O,self.H)
            if laps:
                base=base+self.r(len(self.orbit)+1)+(self.H,)
            walk=base+self.pulse(2)+(self.H,)+self.r(len(self.orbit)+1)
            assert all(self.g.has_edge(v,w) for v,w in pairwise(walk))
            assert all(walk[i]!=walk[i+2] for i in range(len(walk)-2))
            p=[i+1 for i,v in enumerate(walk) if v==self.p][1:]
            pulses=[]
            for j in (1,2):
                w=self.pulse(j);hits=[]
                for n in range(2,len(walk)+1):
                    D=self.span_path(walk[:n]);I=self.span_path(walk[:n-1])
                    if self.packet_nodes(D,w) and not self.packet_nodes(I,w):
                        record=self.charge_record(D,I,w);hits.append(record)
                assert len(hits)==1 and hits[0]['all_O_parents_first'] and hits[0]['O_free_paying_incoming']
                pulses+=hits
            f,l=[x['rank'] for x in pulses]
            res['prior_clock_lap' if laps else 'direct']={'path':self.labels(walk),'pulses':pulses,
                  'p_before':[z for z in p if z<=f],'p_inside':[z for z in p if f<z<=l],
                  'p_after':[z for z in p if z>l],'native_parts':self.slot_bind(self.span_path(walk))}
        return {'global':out,'one_chain':res}

    def carrier(self,D):
        if D in self._carrier_cache:
            return self._carrier_cache[D]
        pending=[D];seen={D};rows=[];parents={}
        while pending:
            node=pending.pop()
            leaves=self.leaves(node) if len(node)>1 else ()
            rows.append([self.footprint(node),self.price(node),sorted(self.encode(a) for a in leaves)])
            parents[node]=[node-{a} for a in leaves]
            for a in leaves:
                earlier=node-{a}
                if earlier not in seen:seen.add(earlier);pending.append(earlier)
        canonical={}
        native={}
        for node in sorted(seen,key=len):
            adj={a:[] for a in node}
            for a in node:
                if a[:-1] in node:
                    adj[a].append(a[:-1]);adj[a[:-1]].append(a)
            def describe(a,previous):
                return (self.name(a[-1]),tuple(sorted(describe(v,a) for v in adj[a] if v!=previous)))
            # A translation of the same native member preserves the original-label tree at a root.
            lowest=min(self.name(a[-1]) for a in node)
            key=digest(min(describe(a,None) for a in node if self.name(a[-1])==lowest))
            canonical[node]=key
            pp=sorted(canonical[old] for old in parents[node])
            assert len(set(pp))==len(pp)
            record=[len(node),self.price(node),pp]
            assert key not in native or native[key]==record
            native[key]=record
        result={'all_connected_ancestors':len(rows),'rooted_support_parent_price_digest':digest(sorted(rows)),
                'distinct_native_members':len(native),'native_members_parents_and_prices_digest':digest(native),
                'distinct_native_members_by_rank':dict(sorted(Counter(x[0] for x in native.values()).items()))}
        self._carrier_cache[D]=result
        return result

    def primitive(self,D):
        rows={}
        for v in {a[-1] for a in D}:
            row=[]
            for u in self.g[v]:
                row.append({'peer':self.name(u),'own_side':sorted(self.port[v,u]),'peer_side':sorted(self.port[u,v]),
                            'spent':self.witness[frozenset((v,u))]})
            rows[self.name(v)]={'held':sorted(self.stars[v]),'degree':self.g.degree(v),'loose':self.loose[v],
                                'incident_ports':sorted(row,key=lambda x:x['peer'])}
        return rows

    def summary(self):
        if not self.funded:
            return {'funded':False,'owe_more_than_supply':{self.name(i):[len(self.loose[i]),self.g.degree(i)]
                   for i in self.g if len(self.loose[i])<self.g.degree(i)},'duration':None}
        maximum,extent=self.cap()
        third={'last_rank':maximum,'attained_arm_lengths':extent,'q':self.name(self.q),
               'r_word':self.labels(self.orbit),'unrestricted_c_cycle':
                   [[self.name(v) for v in row] for row in nx.cycle_basis(self.g.subgraph(self.cmark))]}
        if maximum is not None:
            r,s=extent['r'],extent['s'];assert self.third(r,s) and 1+r+s==maximum
        phase={'funded':True,'private_orbit':self.labels(self.strict[0]),'sender_continues':self.strict[1],
               'broad_orbit':self.labels(self.broad[0]),'third':third,'sender':self.sender_data(),
               'receiver_entrance':self.O is not None}
        if self.O is None:return phase
        phase.update({tie:self.chain(tie) for tie in ['S','R']})
        phase.update(balanced=self.balanced(),equal_spacing=self.saturated(),strong=self.strong())
        return phase


def compare(left,right,readings):
    evidence={}
    for tie in ('S','R'):
        rows=[]
        for i in (1,2):
            a=readings[left.case][tie]['critical_options'][i]
            b=readings[right.case][tie]['critical_options'][i]
            D,_,_=left.branched(a['r']-1,a['s'])
            E,_,_=right.branched(b['r']-1,b['s'])
            pre_l=left.primitive(D);pre_r=right.primitive(E)
            common=set(pre_l)&set(pre_r)
            changes={k for k in common if pre_l[k]['incident_ports']!=pre_r[k]['incident_ports']}
            def roster(x):
                return {(g['site'],g['to']) for g in x['all_funded_options']}
            def carried_own(ar):
                return sorted((len(u['own_side']),tuple(u['own_side'])) for u in ar['incident_ports'])
            order_l=left.carrier(D);order_r=right.carrier(E)
            rows.append({'rank':a['rank'],'previous_rank':len(D),'same_previous_occurrences':a['prior_support']==b['prior_support'],
                         'same_current_grant':a['prior_grant']==b['prior_grant'],
                         'native_rooted_ancestry':[order_l,order_r],
                         'same_ancestral_groups_and_grants':order_l==order_r,
                         'same_original_held_names_and_loose':set(pre_l)==set(pre_r) and
                           all(pre_l[k]['held']==pre_r[k]['held'] and pre_l[k]['loose']==pre_r[k]['loose'] for k in common),
                         'same_own_port_name_multisets_and_degrees':set(pre_l)==set(pre_r) and all(
                           carried_own(pre_l[k])==carried_own(pre_r[k]) and pre_l[k]['degree']==pre_r[k]['degree'] for k in common),
                         'same_primitive_exterior_incidence':set(pre_l)==set(pre_r) and not changes,
                         'differences_at_common_originals':{k:[pre_l[k]['incident_ports'],pre_r[k]['incident_ports']] for k in sorted(changes)},
                         'available_options':[len(roster(a)),len(roster(b))],
                         'left_only_incidents':sorted(roster(a)-roster(b)),'right_only_incidents':sorted(roster(b)-roster(a)),
                         'tick_options':[[g['to'] for g in c['all_funded_options'] if g['attached_at_receiver_tip']] for c in (a,b)],
                         'current_marked_third_at_selected_child':[a['current_third'],b['current_third']],
                         'stored_past_internal_slot_match':order_l==order_r,
                         'anywhere_p_additions':[[x['site'] for x in c['all_funded_options'] if x['to']==w.name(w.p)]
                                                 for c,w in [(a,left),(b,right)]],
                         'selected_parent_grants':[[v['grant'] for v in c['all_true_payments']] for c in (a,b)],
                         'selected_child_grants':[a['child_grant'],b['child_grant']]})
        signals={}
        for j in ('1','2','3','4'):
            aa=readings[left.case][tie]['pulses'].get(j);bb=readings[right.case][tie]['pulses'].get(j)
            if not aa or not bb:continue
            vals=[]
            for w,x in ((left,aa),(right,bb)):
                s=readings[w.case]['sender']['U'+j]
                vals.append({'pulses':[s['grant'],*[z['grant'] for z in s['parents']]],
                             'receipt':[*(z['grant'] for z in x['parents']),x['grant']],
                             'phase':x['last_p_rank'],'arrival':[x['rank'],x['actual_arrival_end'],x['incoming_port']]})
            signals[j]={'vectors':vals,'match':vals[0]==vals[1]}
        evidence[tie]={'critical':rows,'paired_endpoint_fields':signals}
    return evidence


def state_projection(world,owned_names):
    constraints=[r for i,r in enumerate(world.stars) if i not in world.loose and r and r<=set(owned_names)]
    out={}
    for law in ('parity','nae'):
        admitted=0;veto=None
        for value in range(1<<len(owned_names)):
            assignment={k:(value>>i)&1 for i,k in enumerate(owned_names)}
            rows=[[assignment[k] for k in r] for r in constraints]
            ok=all(sum(row)%2==0 for row in rows) if law=='parity' else all(min(row)!=max(row) for row in rows)
            admitted+=ok
            if not ok and veto is None:veto=[assignment[k] for k in owned_names]
        out[law]={'allowed':admitted,'a_forbidden_row':veto}
    return {'entire_spent_rows_on_names':[sorted(r) for r in constraints],'law':out}


def main():
    original=DATA/'physical.json.gz'
    data=json.loads(gzip.decompress(original.read_bytes()))
    worlds={row['case']:World(row) for row in data['cases']}
    readings={k:w.summary() for k,w in worlds.items()}
    pairs=(('intact','near'),('intact','remote'),('near','near_retag'),('near','near_remote'),
           ('remote','near_remote'),('intact','near_retag'))
    price_pairs={a+'__'+b:compare(worlds[a],worlds[b],readings) for a,b in pairs}
    base=worlds['intact']
    sw=base.witness[frozenset((base.role['c8'],base.p))]
    names=sorted(base.stars[sw])
    assert len(names)==12
    result={'physical_sha256':sha256(original.read_bytes()).hexdigest(),'cases':readings,'comparisons':price_pairs,
            'twelve_original_names':names,'projection':{key:state_projection(worlds[key],names) for key in ('intact','near','remote')}}
    dest=DATA/'receipts.json.gz'
    dest.write_bytes(gzip.compress(json.dumps(result,sort_keys=True,separators=(',',':')).encode()+b'\n',compresslevel=9,mtime=0))
    for name,case in readings.items():
        print(name,'funded',case['funded'],'clock',case.get('S',{}).get('interval'),'third',case.get('third',{}).get('last_rank'))
    print('compressed',dest.stat().st_size,'sha256',sha256(dest.read_bytes()).hexdigest())


if __name__=='__main__':
    main()
