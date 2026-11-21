"""Rebuild the enrolled pulse comparison from its original donor witnesses.

Each later occurrence is identified by its nonretracing route from the receiver
origin. Removing any leaf gives a true parent under the funded-pair theorem.
The finite checks use all those parents, whichever continuation the clock reads.
"""
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path
import gzip
import json
from audit_last_spend import input_words


def circuit(side):
    repeated = {1, 5, 9, 13}
    return [("p" if side == "c" else "h") if j in repeated else
            ("q" if side == "c" else "k") if j in {3, 7} else side + str(j)
            for j in range(20)]


def original(near=False, remote=False, retag=False, broken=False, erase=False, short=False, physical=False):
    contacts, sides, living = {}, {}, defaultdict(set)
    next_name = 0

    def contact(key, a, b, i, j):
        nonlocal next_name
        first = tuple(range(next_name, next_name + i))
        second = tuple(range(next_name + i, next_name + i + j))
        next_name += i + j
        living[a].update(first)
        living[b].update(second)
        sides[key] = [(a, first), (b, second)]

    for c in ("c", "u"):
        row = circuit(c)
        pattern = [3 if c == "c" else 5, 6, 7, 8, 9, 10, 11, 12]
        def size(j, outgoing):
            name = row[j]
            if name in ("p", "h", "q", "k"):
                return pattern[2 * row[:j].count(name) + int(outgoing)]
            return (3 if c == "c" else 5) if outgoing else 4
        for j in range(20):
            k = (j + 1) % 20
            contact((c, j), row[j], row[k], size(j, True), size(k, False))
    for j in range(4):
        row = ("O","O1","O2","O3")
        contact(("O",j), row[j], row[(j+1)%4], 1, 2)
    for key, a, b, i, j in (
            ("origin","O","H",1,17), ("clock","H","c0",1,11), ("sender","H","S0",1,13),
            ("join","c18","u18",1,2), ("reserve","O1","V0",1,15)):
        if key=="origin" and erase:
            continue
        contact(key,a,b,i,j)
    for key, cost in (("S",2),("V",6)):
        for j in range(7):
            contact((key,j),key+str(j),key+str((j+1)%7),cost,4)
    old = tuple(x for _, names in sides[("c",8)] for x in names)
    def switch(a,b):
        sides[a][1],sides[b][1] = sides[b][1],sides[a][1]
    for i in ([8,10] if near else []) + ([15,17] if remote else []):
        switch(("c",i),("u",i))
    if broken:
        switch(("S",3),("V",3))
    for key, pair in sides.items():
        if retag and isinstance(key,tuple) and key[0] in {"c","u"}:
            for i, (a, names) in enumerate(pair):
                if len(names) == 5:
                    living[a].difference_update(names[-2:])
                    pair[i]=(a,names[:-2])
        (a,ia),(b,ib)=pair
        assert a!=b and (a,b) not in contacts
        contacts[a,b]=(len(ia),len(ib))
        contacts[b,a]=(len(ib),len(ia))
    held=[]
    for a, names in living.items():
        number=sum(k==a for k,_ in contacts)-int(short and a=="p")
        held.append(sorted(names)+list(range(next_name,next_name+number)))
        next_name+=number
    held += [list(x+y) for (_,x),(_,y) in sides.values()]
    if physical:
        return held, list(living)
    return contacts, held, old


def reader_course(contacts, length=35):
    row=["c0","p"]
    while len(row)<length:
        prev, here=row[-2:]
        eligible=sorted((cost,other) for (a,other),(cost,mate) in contacts.items()
                        if a==here and min(cost,mate)>=3)
        available=[b for _,b in eligible]
        row.append(available[(available.index(prev)+1)%len(available)])
    return row


def sender_course(contacts, strict, size):
    row=["S0"]
    for _ in range(size-1):
        choices=[b for (a,b),pair in contacts.items() if a==row[-1] and
                 pair in ([(2,4)] if strict else [(2,4),(6,4)])]
        if strict:
            choices=[b for b in choices if any(a==b and pair==(2,4)
                                                for (a,_),pair in contacts.items())]
        if not choices: break
        assert len(choices)==1
        row.append(choices[0])
    return row


def support(routings):
    result = set()
    for branch in routings:
        assert len(branch)>0
        result.update(tuple(branch[:i]) for i in range(1,len(branch)+1))
    return result


def parents(shape):
    adj=defaultdict(set)
    for child in shape:
        if child[:-1] in shape:
            adj[child].add(child[:-1]);adj[child[:-1]].add(child)
    return [shape-{leaf} for leaf in shape if len(adj[leaf])==1]


def packet_occurrences(shape, word):
    """Count embeddings identified by the original directed sender word."""
    adj=defaultdict(set)
    for child in shape:
        if child[:-1] in shape:
            adj[child].add(child[:-1]);adj[child[:-1]].add(child)
    runs=[(a,) for a in shape if a[-1]==word[0]]
    for name in word[1:]:
        runs=[walk+(n,) for walk in runs for n in adj[walk[-1]]
              if n[-1]==name and n not in walk]
    return runs


def inclusion_referee(shape, word):
    pars=parents(shape)
    with_origin=[p for p in pars if ("O",) in p]
    outside=[p for p in pars if ("O",) not in p]
    return (len(packet_occurrences(shape,word)),
            sum(bool(packet_occurrences(p,word)) for p in with_origin), len(with_origin),
            sum(bool(packet_occurrences(p,word)) for p in outside), len(outside))


def earliest_shapes(j):
    sender=["S"+str(i%7) for i in range(7*j+1)]
    shapes=set()
    for k in range(0,len(sender),7):
        roots=["O","H"]
        shapes.add(frozenset(support([roots+sender[k:],roots+list(reversed(sender[:k+1]))])))
    for y in shapes:
        nr,carry,old,paid,_=inclusion_referee(y,sender)
        assert nr==1 and len(y)==7*j+3 and carry==0 and old>=1 and paid>0
    return len(shapes)


def balanced(s_course, r_course):
    """Enumerate both ties from O,H until the second private return forms."""
    stages={(0,0,None,0):1}
    results=Counter()
    while stages:
        following=Counter()
        for (s,r,first,ticks),count in stages.items():
            for ds,dr in ((1,0),(0,1)):
                a,b=s+ds,r+dr
                if abs(a-b)>1:continue
                if ds and a>len(s_course):continue
                next_ticks=ticks+int(first is not None and dr==1 and r_course[b-1]=="p")
                at=2+a+b
                if ds and a==15:
                    results[first,at,next_ticks]+=count
                else:
                    begin=at if ds and a==8 else first
                    following[a,b,begin,next_ticks]+=count
        stages=following
    return results


def strong_running(contacts):
    row=reader_course(contacts,70)
    period=row.index("c0",1)
    lead=["O","H"]+row[:period+1]+["H"]
    path=lead+sender_course(contacts,False,15)+["H","c0","p"]
    for a,b in pairwise(path):assert (a,b) in contacts
    assert all(path[i]!=path[i-2] for i in range(2,len(path)))
    seen=[]
    for j in (1,2):
        size=len(lead)+1+7*j
        y=support([path[:size]])
        w=sender_course(contacts,True,1+7*j)
        assert inclusion_referee(y,w)==(1,0,1,1,1)
        seen.append(size)
    assert "p" in path[:seen[0]] and "p" not in path[seen[0]:seen[1]] and path[-1]=="p"
    return seen


def comparison_at_changed_tick():
    """Read every available addition before applying the fixed clock policy."""
    c, _, _ = original()
    near, _, _ = original(near=True)
    remote, _, _ = original(remote=True)
    rows = {}
    past = None
    for name, system in (("intact", c), ("near", near), ("remote", remote)):
        s, r = sender_course(system, True, 10), reader_course(system, 40)
        here = support([["O","H"]+s, ["O","H"]+r[:9]])
        if past is None:past=here
        assert here == past
        def menu(shape):
            return {v+(b,) for v in shape for a,b in system if a==v[-1]
                    and (len(v)==1 or b!=v[-2]) and v+(b,) not in shape}
        def price(shape):
            return 2+sum(sum(a==v[-1] for a,b in system)-2 for v in shape)
        options=menu(here)
        assert len(options)==price(here)
        rooted_tip=tuple(["O","H"]+r[:9])
        before=sorted(v[-1] for v in options if v[:-1]==rooted_tip)
        actual=rooted_tip+(r[9],)
        assert actual in options
        child=here | {actual}
        charges=[]
        for old in parents(child):
            # The leaf O may be deleted; its two-way parent relation with H
            # still contributes to the demand of that translated support.
            charges.append(price(old))
        rows[name]=(options, price(here), sorted(charges),price(child),before)
    assert rows["intact"][1:4] == rows["near"][1:4]
    assert rows["intact"][0] != rows["near"][0]
    assert rows["intact"]==rows["remote"]
    assert rows["intact"][-1]==["p"] and rows["near"][-1]==["h"]
    return (len(rows["intact"][0]),len(rows["intact"][0]-rows["near"][0]),
            rows["intact"][2],rows["intact"][3])


def third_lifetime(system):
    course=reader_course(system,82)
    from_seed=[any(a==v and price==3 and other>=3 for (a,b),(price,other) in system.items())
               for v in course]
    period=next(i for i in range(1,len(course)-1) if course[i:i+2]==course[:2])
    if all(from_seed[:period]):return None
    permitted=from_seed.index(False)
    return 1+permitted+(permitted+1)


def physical_cuts(flags):
    from audit_serial_traces import sharing, raw_groups
    holders, labels = original(**flags, physical=True)
    _, neighbors, loose = sharing(holders)
    born = {i for i,names in enumerate(loose) if names}
    assert born == set(range(len(labels)))
    groups = raw_groups(neighbors, born)
    hist = {i:frozenset([tag]) for i,tag in enumerate(labels)}
    next_name=max(max(h) for h in holders)+1
    counts=[]
    shape=frozenset(("O","H","c0","S0"))
    meets=[]
    for cut in range(1,4):
        debt=Counter(p for group in groups for p in group)
        lacking=[labels[p] for p in born if len(loose[p])<debt[p]]
        if lacking:
            assert cut==1 and flags.get("short") and lacking==["p"]
            return counts,0
        assert all(len(loose[p]) == debt[p] for p in born)
        unused={p:iter(sorted(loose[p])) for p in born}
        rows=sorted([sorted(g) for g in groups])
        start=len(holders)
        for parents_of_child in rows:
            args=[next(unused[p]) for p in parents_of_child]
            child=len(holders)
            hist[child]=frozenset.union(*(hist[p] for p in parents_of_child))
            if cut==3 and hist[child]==shape:
                meets.append({hist[p] for p in parents_of_child})
            holders.append(args)
        born=set(range(start,len(holders)))
        counts.append((len(rows),sum(len(row)==3 for row in rows)))
        _,neighbors,_=sharing(holders)
        groups=raw_groups(neighbors,born)
        demand=Counter(p for g in groups for p in g)
        for child in sorted(born):
            grant=max(demand[child],3-len(holders[child]),1)
            assert grant==demand[child]
            holders[child]=holders[child]+list(range(next_name,next_name+grant))
            next_name+=grant
        _,_,loose=sharing(holders)
    if not flags.get("erase"):
        assert meets==[{shape-{end} for end in ("O","c0","S0")}]
    else:
        assert not meets
    return counts,len(meets)


def count_physical_preparations(literal):
    rows=[{},{"near":True},{"remote":True},{"near":True,"retag":True},
          {"near":True,"remote":True},{"broken":True},{"near":True,"broken":True},
          {"erase":True},{"short":True}]
    counts=[physical_cuts(flags) for flags in rows]
    assert all(len(cuts)==3 for cuts,_ in counts[:-1]) and not counts[-1][0]
    normal=counts[0][0]
    assert all(cuts==normal for cuts,_ in counts[:7])
    labels=("intact","near","remote","near_retag","near_remote","intact_s_break",
            "near_s_break","o_erased","p_shortage")
    for label,(cuts,_) in zip(labels,counts):
        for data in literal[label]["laws"].values():
            observed=[len(cut["births"]) for cut in data["cuts"]]
            assert observed == ([number for number,_ in cuts[:2]] if cuts else [0])
    print("From actual loose names, three complete ordinary cuts (births, three-parent births):",
          normal,"on seven connected sources, and",counts[7][0],"after origin erasure.")
    print("The first three-ended O/H clock birth has its three deletion parents in all seven cases."
          " The ninth start is short of its first cut.")


def check():
    home=Path(__file__).resolve().parent
    archive=home.parents[1]/"artifacts"/(home.name+"B")/(home.name+"B-E001_private_pulses")
    def read(name):
        return json.loads(gzip.decompress((archive/name).read_bytes()))
    recorded=read("receipts.json.gz")
    count_physical_preparations({x["case"]:x for x in read("physical.json.gz")["cases"]})
    print('Common prebirth options, changed partners, three parent grants and child grant:',
          comparison_at_changed_tick())
    base,base_states,bond=original()
    near,near_states,equal_names=original(near=True)
    assert bond==equal_names and len(bond)==12
    for law in ("parity","nae"):
        projected=input_words(base_states,bond,law),input_words(near_states,bond,law)
        assert projected==(2048 if law=="parity" else 4094,4096)
        assert projected==tuple(recorded["projection"][n]["law"][law]["allowed"]
                                for n in ("intact","near"))
        print(law,"allowed readings on the same twelve names before and after the near exchange",projected)
    for j in range(1,5):
        measured=recorded["cases"]["intact"]["strong"]["global"][str(j)]
        assert earliest_shapes(j)==j+1==measured["rooted_classes"]
        assert measured["minimum_size"]==7*j+3
    print("Minimum all-origin receipts, sizes 10, 17, 24, 31 with 2, 3, 4, 5 distinct rooted supports.")
    for title,args in [("intact",{}),("near",{"near":True}),("remote",{"remote":True}),
                       ("near retagged",{"near":True,"retag":True}),
                       ("near and remote",{"near":True,"remote":True})]:
        c,_,_=original(**args)
        lifetime=third_lifetime(c)
        assert lifetime==({"intact":None,"near":20,"remote":34,"near retagged":None,"near and remote":20}[title])
        moves=reader_course(c,61);pulse=sender_course(c,True,30)
        accepted=balanced(pulse,moves)
        identifier={"near retagged":"near_retag","near and remote":"near_remote"}.get(title,title)
        record=recorded["cases"][identifier]
        assert lifetime==record["third"]["last_rank"]
        assert { (v["first_rank"],v["last_rank"],v["p_turns"]):v["chains"]
                 for v in record["balanced"]["all_endpoint_pairs"] }==dict(accepted)
        want=1 if args.get("near") else 2
        assert set(accepted)=={(a,b,want) for a in (17,18) for b in (31,32)}
        assert set(accepted.values())=={8192}
        for j, r in ((1,7),(2,14)):
            word=pulse[:7*j+1]
            y=support([["O","H"]+word,["O","H"]+moves[:r]])
            assert inclusion_referee(y,word)==(1,1,2,1,1)
            event=record["S"]["pulses"][str(j)]
            assert event["selected_first"] and event["O_free_paying_incoming"]
            assert not event["all_O_parents_first"]
        strong=strong_running(c)
        turns=[2+2*n for n in range(8,15) if moves[n-1]=="p"]
        assert turns==record["S"]["interval"]["turns"]
        checked=record["strong"]["one_chain"]["prior_clock_lap"]["pulses"]
        assert [v["rank"] for v in checked[:2]]==strong and all(v["all_O_parents_first"] for v in checked[:2])
        print(title,"balanced first-pair histories",sum(accepted.values()),"primary tick sizes",turns,
              "strong receipts on a previously turning clock",strong,"third last size",lifetime)
    for near_switch in (False,True):
        c,_,_=original(near=near_switch,broken=True)
        assert len(sender_course(c,True,30))<8
        assert len(sender_course(c,False,30))==30 and reader_course(c,61).count("p")>=2
    print("Private break removes both enrolled pulses; the independent intake and p course continue.")


if __name__=="__main__":
    check()
