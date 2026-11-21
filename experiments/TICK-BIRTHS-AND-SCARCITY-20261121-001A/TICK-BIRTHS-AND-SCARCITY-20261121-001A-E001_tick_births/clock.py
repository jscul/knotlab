"""Read one physical clock, its true parents, and its external pulses from the paid source."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, pairwise
from pathlib import Path
import gzip
import json

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name


def unique(values):
    item, = values
    return item


def canonical(word):
    word = tuple(word)
    return min(word, word[::-1])


def locations(word, part):
    length = len(part)
    target = canonical(part)
    return [i for i in range(len(word)-length+1) if canonical(word[i:i+length]) == target]


def maximum_c_run(cycle, marked):
    if all(v in marked for v in cycle):
        return None
    best = run = 0
    for v in cycle+cycle:
        run = run+1 if v in marked else 0
        best = max(best,run)
    return best


class World:
    def __init__(self, source):
        self.case = source['case']
        self.names = {int(i):role for role,i in source['live_roles'].items()}
        owners = defaultdict(list)
        for i,row in enumerate(source['original_stars']):
            for name in row:
                owners[name].append(i)
        assert all(len(at) in (1,2) for at in owners.values())
        self.loose = Counter(at[0] for at in owners.values() if len(at)==1)
        incident = defaultdict(lambda:defaultdict(list))
        for name,at in owners.items():
            if len(at)==2:
                a,b=at
                assert (a in self.loose) != (b in self.loose)
                spent,donor=(b,a) if a in self.loose else (a,b)
                incident[spent][donor].append(name)
        self.graph=nx.Graph()
        self.circuit=nx.Graph()
        self.counts={}
        self.witnesses={}
        for witness,by_donor in incident.items():
            a,b=by_donor
            assert not self.graph.has_edge(a,b)
            self.graph.add_edge(a,b)
            self.witnesses[frozenset((a,b))]=witness
            for v,u in ((a,b),(b,a)):
                self.counts[v,u]=len(by_donor[v])
            if min(self.counts[a,b],self.counts[b,a])>=3:
                self.circuit.add_edge(a,b)
        assert nx.is_connected(self.graph) and not any(nx.triangles(self.graph).values())
        self.marked={v for v in self.circuit if any(self.counts[v,x]==3 for x in self.circuit[v])}
        self.ports={v:tuple(sorted(self.circuit[v],key=lambda w:self.counts[v,w])) for v in self.circuit}
        assert all(len({self.counts[v,x] for x in arr})==len(arr) for v,arr in self.ports.items())
        self.funded=all(self.loose[v]>=self.graph.degree(v) for v in self.graph)
        def directed(left,right):
            return unique((a,b) for a,b in self.counts if (self.counts[a,b],self.counts[b,a])==(left,right))
        root,first=directed(1,9)
        self.X=self.Y=None
        if first not in self.circuit:
            x,y=directed(1,8); yy,entry=directed(1,10)
            assert x==first and yy==y
            self.X,self.Y=x,y
            self.prefix=(root,x,y,entry)
        else:
            self.prefix=(root,first)
        self.c0=self.prefix[-1]
        self.p=unique(v for v in self.circuit[self.c0] if self.circuit.degree(v)==10)
        self.h=unique(v for v in self.circuit if self.circuit.degree(v)==10 and v!=self.p)
        self.s2,b=directed(1,7)
        a=unique(v for v in self.circuit[b] if self.counts[v,b]==self.counts[b,v]==30)
        end,self.s1=directed(1,6)
        d=self.successor(b,a,1)
        e=self.successor(a,d,1)
        assert self.successor(d,e,1)==end
        self.sender=(b,a,d,e,end,self.s1,self.s2)
        self.sender_continues=self.graph.has_edge(self.s1,self.s2)
        self.signals={f'W{i}':self.sender[:i+1] for i in range(1,6)}
        self.signals['W1_at_next_sender_turn']=self.sender+self.sender[:2]
        if self.X is not None:
            self.signals['V']=(self.X,self.Y)
        self.orbits={}
        for direction in (1,-1):
            self.orbits[direction]=self.orbit(self.c0,self.p,direction)
        self.all_orbits=self.partition_orbits()

    def successor(self,a,b,direction):
        ordered=self.ports[b]
        return ordered[(ordered.index(a)+direction)%len(ordered)]

    def orbit(self,a,b,direction):
        start=(a,b);seq=[];seen=set()
        while (a,b) not in seen:
            seen.add((a,b));seq.append(a)
            a,b=b,self.successor(a,b,direction)
        assert (a,b)==start
        return tuple(seq)

    def partition_orbits(self):
        unseen={(u,v) for u in self.circuit for v in self.circuit[u]}
        result=[]
        while unseen:
            first=min(unseen)
            word=self.orbit(*first,1)
            states=set(pairwise(word+(word[0],)))
            assert len(states)==len(word) and states<=unseen
            unseen-=states
            result.append(word)
        return result

    def price(self,word):
        assert word and all(self.graph.has_edge(a,b) for a,b in pairwise(word))
        return 2+sum(self.graph.degree(v)-2 for v in word)

    def slots(self,word):
        # At each occurrence an unused incident direction attaches the next original to its support.
        # The short-lift theorem identifies these slots with distinct actual positive-cut groups.
        slots=[]
        for i,x in enumerate(word):
            used=set(word[max(0,i-1):i])|set(word[i+1:i+2])
            slots.extend((i,y) for y in sorted(set(self.graph[x])-used))
        assert len(set(slots))==len(slots)==self.price(word)
        return slots

    def nameword(self,word):
        return [self.names[x] for x in word]

    def dual_parent(self,word,with_slots=False):
        inside,outside=word[:-1],word[1:]
        assert len(word)>2 and canonical(inside)!=canonical(outside)
        # The selected input distinctions already exist on the parents; index their complete forecast.
        in_charge=(len(inside)-1,word[-1]);out_charge=(0,word[0])
        ins=self.slots(inside);outs=self.slots(outside)
        assert in_charge in ins and out_charge in outs
        record={'inside_grant':len(ins),'outside_grant':len(outs),'child_grant':self.price(word),
                'inside_charge':[in_charge[0],self.names[in_charge[1]]],
                'outside_charge':[out_charge[0],self.names[out_charge[1]]],
                'inside_slot_index':ins.index(in_charge),'outside_slot_index':outs.index(out_charge)}
        if with_slots:
            record['inside_all_charged_slots']=[[i,self.names[v]] for i,v in ins]
            record['outside_all_charged_slots']=[[i,self.names[v]] for i,v in outs]
        return record

    def prebirth(self,word,chosen):
        u,v=word[-2:]
        native=[]
        for dest in sorted(self.graph[v]):
            if dest==u:continue
            child=word+(dest,)
            native.append({'donor':self.names[dest],'witness':self.witnesses[frozenset((v,dest))],
                           'incoming_parent_price':self.price(child[1:]),'child_price':self.price(child),
                           'local_multiplicity':self.counts[v,dest],'circuit':self.circuit.has_edge(v,dest)})
        return {'inside':self.nameword(word),'tip':self.names[v],'previous':self.names[u],
                'incoming_witness':self.witnesses[frozenset((u,v))],'incoming_multiplicity':self.counts[v,u],
                'all_native_end_children':native,'ordered_ports':self.nameword(self.ports[v]),
                'selected':self.names[chosen],'payment':self.dual_parent(word+(chosen,),True),
                'contains_prior_p':self.p in word,'previous_p':max((i+1 for i,y in enumerate(word) if y==self.p),default=None)}

    def sender_record(self,packet):
        possible=all(self.graph.has_edge(a,b) for a,b in pairwise(packet))
        record={'roles':self.nameword(packet),'native_packet':possible,'birth_rank':len(packet) if possible else None}
        if possible:
            record.update({'whole_grant':self.price(packet),'parents_grants':[self.price(packet[:-1]),self.price(packet[1:])],
                           'parents':[self.nameword(packet[:-1]),self.nameword(packet[1:])]})
        return record

    def walk(self,direction):
        orbit=self.orbits[direction]
        longest=max(map(len,self.signals.values()))
        # Two full periods plus an overlap test every phase of every enrolled finite word.
        length=2*len(orbit)+longest+len(self.prefix)+1
        word=self.prefix[:-1]+tuple(orbit[i%len(orbit)] for i in range(length))
        assert word.count(self.prefix[0])==1
        p_times=[i+1 for i,v in enumerate(word) if v==self.p]
        tick_times=p_times[1:]
        pulses={}
        for label,packet in self.signals.items():
            hits=locations(word,packet)
            if not hits:
                pulses[label]=None;continue
            place=hits[0];n=place+len(packet);rec=word[:n]
            contains_inside=bool(locations(rec[:-1],packet))
            contains_outside=bool(locations(rec[1:],packet))
            assert not contains_inside and contains_outside
            right=rec[-len(packet):]
            approach='sender' if right==packet else 'reversed'
            pulses[label]={'size':n,'age':n-1,'send_size':len(packet),'delay':n-len(packet),
                           'arriving_at':self.names[rec[-1]],'incoming_from':self.names[rec[-2]],
                           'incoming_port':self.counts[rec[-1],rec[-2]],'orientation':approach,
                           'true_origin':self.names[rec[0]],'incoming_history':self.nameword(rec[1:]),
                           'signal_in_internal_parent':contains_inside,'signal_in_outside_parent':contains_outside,
                           'preceding_return':max((t for t in tick_times if t<=n),default=None),
                           'payment':self.dual_parent(rec)}
        window=None
        if pulses['W1'] and pulses['W2']:
            first,last=pulses['W1']['size'],pulses['W2']['size']
            assert first<=last  # W1 is an actual parent of W2.
            mid=[i for i in tick_times if first<i<=last]
            window={'first':first,'last':last,'turns':mid,'count':len(mid),'receipt_spacing':last-first,'send_spacing':1,
                    'bounded_by_real_previous_return':pulses['W1']['preceding_return'] is not None,'restored':first<last}
        phase=tuple(i for i,v in enumerate(orbit) if v==self.p)
        gaps=[b-a for a,b in pairwise(phase+(phase[0]+len(orbit),))]
        return {'orbit':self.nameword(orbit),'orbit_length':len(orbit),'p_phase':phase,'cyclic_gaps':gaps,
                'origin_sighting':p_times[0],'checked_to_rank':len(word),'observed_return_ranks':tick_times,
                'pulses':pulses,'interval':window},word

    def third_status(self,word):
        orbit=self.orbits[1]
        def in_pure(part):
            if not all(x in self.marked for x in part):return False
            occurrences=orbit*((len(part)+len(orbit)-1)//len(orbit)+1)
            return bool(locations(occurrences,part))
        mixed=(self.X is not None and word[:2]==(self.X,self.Y) and
               word[2:4]==(self.c0,self.p) and in_pure(word[2:]))
        return {'rank':len(word),'current_pure':in_pure(word),'current_mixed_prefix_third':mixed,
                'one_outside_origin':self.prefix[0] in word,'contains_members_of_both_circuit_kinds':
                bool(set(word)&self.marked) and bool((set(word)&set(self.circuit))-self.marked),
                'W1_in_payer':bool(locations(word,self.signals['W1'])),
                'V_in_payer':self.X is not None and bool(locations(word,self.signals['V']))}

    def unrestricted(self,first,last,circuit_only,physical_match=False):
        """All nonretracing end histories and one paid realization per attainable count."""
        seed=self.prefix+(self.p,)
        # The first p was seen at the last seed position. Store the total fresh count only
        # when matching actual prices at both registrations, with the target initial phase.
        actual_forward, _ = self.walk(1)
        target = {label:actual_forward['pulses'][label] for label in ('W1','W2')}
        phase = target['W1']['preceding_return']
        initial = (seed[-2],seed[-1],0,self.price(seed) if physical_match else 0)
        counts = {initial:(1,seed)}
        w1 = canonical(self.signals['W1'])
        w2 = canonical(self.signals['W2'])
        for rank in range(len(seed)+1,last+1):
            after = {}
            for (a,b,t,grant),(ways,one) in counts.items():
                neighbors = self.circuit[b] if circuit_only else self.graph[b]
                for v in neighbors:
                    if v==a or v==seed[0]:
                        continue
                    w1_now = canonical((b,v))==w1
                    w2_now = canonical((a,b,v))==w2
                    if (rank<=first and w1_now!=(rank==first)) or w2_now!=(rank==last):
                        continue
                    fresh = grant+self.graph.degree(v)-2 if physical_match else 0
                    if physical_match:
                        if rank==phase and v!=self.p or phase<rank<=first and v==self.p:
                            continue
                        event = target['W1'] if rank==first else target['W2'] if rank==last else None
                        if event and (self.names[v]!=event['arriving_at'] or self.names[b]!=event['incoming_from']
                                      or fresh!=event['payment']['child_grant']):
                            continue
                    state = (b,v,t+int(first<rank<=last and v==self.p),fresh)
                    previous = after.get(state)
                    after[state] = (ways,one+(v,)) if previous is None else (ways+previous[0],previous[1])
            counts=after
        totals=Counter()
        examples={}
        for (_,__,t,_grant),(ways,example) in counts.items():
            totals[t]+=ways
            examples.setdefault(t,self.nameword(example))
        return {'counts':{str(k):v for k,v in sorted(totals.items())},
                'one_actual_history_for_each_count':examples}

    def read(self):
        if not self.funded:
            return {'case':self.case,'funded':False,'shortages':{self.names[v]:[self.loose[v],self.graph.degree(v)]
                      for v in self.graph if self.loose[v]<self.graph.degree(v)},'receiving_time':None}
        forward,word=self.walk(1);reverse,_=self.walk(-1)
        forward['first_period_of_returns_after_startup']=[
            {'size':n,'outside_payer':self.third_status(word[1:n]),'payment':self.dual_parent(word[:n])}
            for n in forward['observed_return_ranks']
            if n<=forward['origin_sighting']+forward['orbit_length']]
        begin,end=forward['interval']['first'],forward['interval']['last']
        puremax=maximum_c_run(self.orbits[1],self.marked)
        actual_c_arcs=self.circuit.subgraph(self.marked)
        family={'pure_maximum':puremax,'unseeded_rotations':[{'size':len(cy),'max_c':maximum_c_run(cy,self.marked)} for cy in self.all_orbits],
                'unrestricted_c_original_cycles':[[self.names[v] for v in cyc] for cyc in nx.cycle_basis(actual_c_arcs)]}
        if self.X is not None:
            first_non_c=next((i for i,x in enumerate(self.orbits[1]) if x not in self.marked),None)
            family['mixed_prefix_maximum']=None if first_non_c is None else 2+first_non_c
        events=[]
        for n in range(begin+1,end+1):
            rec=word[:n]
            if rec[-1] not in (self.p,self.h):continue
            events.append({'size':n,'tick':rec[-1]==self.p,'payer':self.third_status(rec[1:]),
                           'options':self.prebirth(rec[:-1],rec[-1])})
        packet_data={label:self.sender_record(packet) for label,packet in self.signals.items()}
        return {'case':self.case,'funded':True,'source':packet_data,'sender_continues':self.sender_continues,
                'root':self.nameword(self.prefix),'physical_mark':self.names[self.p],
                'families':family,'forward':forward,'reverse':reverse,'events':events,
                'unrestricted_matched_end_ranks':{name:self.unrestricted(begin,end,t) for name,t in [('circuit',True),('whole_ordinary',False)]},
                'unrestricted_with_matched_initial_phase_ends_and_prices':{name:self.unrestricted(begin,end,t,True) for name,t in [('circuit',True),('whole_ordinary',False)]}}


def counterpart(origin,mate,word):
    inverse={role:v for v,role in mate.names.items()}
    names=origin.nameword(word)
    if not all(role in inverse for role in names):
        return {'same_physical_roles_available':False}
    translated=tuple(inverse[r] for r in names)
    a,b=translated[-2:]
    current=origin.counts[word[-1],word[-2]]
    coherent=all(mate.graph.has_edge(u,v) for u,v in pairwise(translated))
    prev=list(x for x in mate.circuit[b] if mate.counts[b,x]==current)
    return {'same_physical_roles_available':True,'same_whole_ordinary_history':coherent,
            'same_final_pair':mate.graph.has_edge(a,b),'same_prior_private_price':mate.price(translated) if coherent else None,
            'local_same_incoming_multiplicity':current,'actual_previous_at_corresponding_port':mate.nameword(prev),
            'p_native_option_on_same_donor_via_corresponding_port':bool(prev) and mate.graph.has_edge(b,mate.p) and mate.p!=prev[0],
            'p_selected_on_same_donor_via_corresponding_port':bool(prev) and mate.successor(prev[0],b,1)==mate.p,
            'h_native_option_on_same_donor_via_corresponding_port':bool(prev) and mate.graph.has_edge(b,mate.h) and mate.h!=prev[0]}


def pair_certificate(left,right,data):
    a,aw=left.walk(1);b,bw=right.walk(1)
    f,l=a['interval']['first'],a['interval']['last']
    n1=tuple(left.names[x] for x in aw);n2=tuple(right.names[x] for x in bw)
    different=next((i+1 for i,(x,y) in enumerate(zip(n1,n2)) if x!=y),None)
    critical={n for n in range(f+1,l+1) if aw[n-1] in (left.p,left.h) or bw[n-1] in (right.p,right.h)}
    if different is not None:critical.add(different)
    before=[]
    for n in sorted(critical):
        pa,pb=aw[:n-1],bw[:n-1]
        before.append({'rank':n,'same_previous_full_word':n1[:n-1]==n2[:n-1],
                       'left':left.prebirth(pa,aw[n-1]),'right':right.prebirth(pb,bw[n-1]),
                       'left_history_in_right':counterpart(left,right,pa),
                       'right_history_in_left':counterpart(right,left,pb),
                       'left_payer':left.third_status(aw[1:n]),'right_payer':right.third_status(bw[1:n])})
    prices={}
    for sig in ('W1','W2','W3','W4'):
        lrec=a['pulses'][sig];rrec=b['pulses'][sig]
        if not lrec or not rrec:
            prices[sig]=None;continue
        vecs=[]
        for world,rec in ((left,lrec),(right,rrec)):
            src=data[world.case]['source'][sig]
            vecs.append([src['whole_grant'],*src['parents_grants'],rec['payment']['inside_grant'],
                         rec['payment']['outside_grant'],rec['payment']['child_grant']])
        prices[sig]={'left':vecs[0],'right':vecs[1],'equal':vecs[0]==vecs[1],
                     'same_receiver_phase':lrec['preceding_return']==rrec['preceding_return'],
                     'same_arrival_orientation':lrec['orientation']==rrec['orientation'],
                     'same_actual_end_and_incoming_port':all(lrec[x]==rrec[x] for x in ('arriving_at','incoming_from','incoming_port'))}
    return {'cases':[left.case,right.case],'first_unequal_donor_rank':different,
            'common_tick_times':sorted(set(a['interval']['turns'])&set(b['interval']['turns'])),
            'prebirth':before,'signal_endpoint_fields':prices}


def bind(source,world,data):
    if not world.funded:
        return {'status':'unfunded','cases':world.case}
    mapping={}
    for law,native in source['laws'].items():
        first={frozenset(b['parents']):b for b in native['cuts'][0]['births']}
        second={frozenset(b['parents']):b for b in native['cuts'][1]['births']}
        assert {frozenset(p) for p in world.graph.edges}==set(first)
        histories={}
        for dx,mode in ((1,'forward'),(-1,'reverse')):
            reading,word=world.walk(dx)
            # Two complete rooted orbit copies plus the longest probe settle both recurrence and packet nonarrival.
            first_ids=[];second_ids=[]
            for i,(u,v) in enumerate(pairwise(word)):
                birth=first[frozenset((u,v))]
                assert birth['grant']==world.price(word[i:i+2])
                first_ids.append(birth['holder'])
            for i,(u,v) in enumerate(pairwise(first_ids)):
                birth=second[frozenset((u,v))]
                assert birth['grant']==world.price(word[i:i+3])
                second_ids.append(birth['holder'])
            histories[mode]={'roles':world.nameword(word),'all_true_rank_two':first_ids,'all_true_rank_three':second_ids}
        for name in ('W1','W2','W3','W4','W5','V'):
            packet=world.signals.get(name)
            if packet is None:continue
            fst=[first[frozenset((u,v))]['holder'] for u,v in pairwise(packet)]
            snd=[second[frozenset((u,v))]['holder'] for u,v in pairwise(fst)]
            histories[name]={'originals':world.nameword(packet),'all_true_rank_two':fst,'all_true_rank_three':snd}
        mapping[law]=histories
    assert mapping['parity']==mapping['nae']
    return {'case':world.case,'laws':sorted(mapping),'identical_literal_histories':mapping['parity']}


def dump(file,obj):
    raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n'
    file.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))


def main():
    physical=OUT/'physical.json.gz'
    source=json.loads(gzip.decompress(physical.read_bytes()))
    worlds={c['case']:World(c) for c in source['cases']}
    data={k:w.read() for k,w in worlds.items()}
    pairs=(('fast_lasting','slow_finite'),('fast_lasting','fast_finite'),('slow_lasting','slow_finite'),
           ('fast_lasting','slow_lasting'),('fast_finite','slow_finite'),('prefix_fast_lasting','prefix_slow_finite'),
           ('fast_lasting','sender_cut_fast_lasting'),('slow_finite','sender_cut_slow_finite'))
    cq=[pair_certificate(worlds[a],worlds[b],data) for a,b in pairs]
    dump(OUT/'clock.json.gz',{'physical_sha256':sha256(physical.read_bytes()).hexdigest(),'cases':data,'comparisons':cq})
    dump(OUT/'bound_histories.json.gz',{'cases':[bind(c,worlds[c['case']],data[c['case']]) for c in source['cases']]})
    for k,v in data.items():
        if v['funded']:
            w=v['forward']; print(k,'registered',w['interval'],'return offsets',w['p_phase'],'third maximum',v['families']['pure_maximum'])
        else:print(k,v['shortages'])


if __name__=='__main__':
    main()
