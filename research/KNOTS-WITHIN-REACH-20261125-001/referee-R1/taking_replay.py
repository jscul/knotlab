"""Small complete rounds with taking, including an exact six-knot parity witness.

Uses the referee's group finder for a supplied roster. All take choices, parity
closure, step lengths, and allowed-state projections below are built here.
"""
import argparse
import hashlib
import heapq
import itertools
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from regrow_engine import Roster
from taking_tables import HERE, stream

ROOT = HERE.parents[2]
TICKET = ROOT / "research" / (HERE.parent.name + "A")


def bits(places):
    return sum(1 << d for d in places)


def reduce_rule(x, basis):
    for p in sorted(basis, reverse=True):
        if x & (1 << p):
            x ^= basis[p]
    return x


def relation_basis(rows):
    basis = {}
    for x in rows:
        rest = reduce_rule(x, basis)
        if rest:
            basis[rest.bit_length()-1] = rest
    return basis


class SmallRounds:
    def __init__(self, stars, row):
        self.places = [set(s) for s in stars]
        self.parents = [() for _ in stars]
        self.barred = set()
        self.knot_law = row["knot_law"]
        self.law = int(row["law"][1:])
        seed = "|".join(["KWR", row["start"], row["law"], self.knot_law, row["seed"]])
        self.rand = random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest(), "big"))

    def meetings(self):
        return [{v for v, other in enumerate(self.places) if v != u and star & other}
                for u, star in enumerate(self.places)]

    def step(self):
        freq = Counter(d for s in self.places for d in s)
        eligible = {d for d,n in freq.items() if n>=2}
        loose = {u:sorted(s-eligible-self.barred) for u,s in enumerate(self.places)}
        members = {u for u,ds in loose.items() if ds}
        old_meets = self.meetings()
        groups = Roster.read(old_meets,members).groups()
        owing = Counter(u for group in groups for u in group)
        short = {u for u in members if owing[u] > len(loose[u])}
        for u in short:
            self.barred.update(loose[u])
        births = [g for g in groups if not short.intersection(g)]
        children = Counter(u for group in births for u in group)
        for u in sorted(members-short):
            births.extend([(u,)] * (len(loose[u])-children[u]))
        if not births:
            return 0,0
        all_inputs = []
        takes = 0
        for group in births:
            given = {loose[u].pop(0) for u in group}
            owned = set.union(*(self.places[u] for u in group))
            mode = (self.law-1)%4
            if self.law>=9:
                for u in group:
                    older = self.parents[u]
                    candidates = self.places[u] & eligible
                    if older:
                        candidates &= set.union(*(self.places[v] for v in older))
                    if candidates:
                        given.add(min(candidates))
            else:
                candidates = set()
                if mode==0 and len(group)==1:
                    candidates = owned & eligible
                elif mode==1:
                    common = set.intersection(*(old_meets[u] for u in group))
                    candidates = {d for v in common for d in self.places[v]} & eligible - owned
                elif mode in (2,3) and len(group)==1:
                    older = self.parents[group[0]]
                    if mode==3:
                        older = {a for v in older for a in self.parents[v]}
                    candidates = {d for v in older for d in self.places[v]} & eligible - owned
                if candidates:
                    given.add(self.rand.choice(sorted(candidates)))
            takes += len(given) - len(group)
            all_inputs.append(given)
        base = relation_basis(map(bits,self.places))
        first = len(self.places)
        self.parents.extend(births)
        self.places.extend(all_inputs)
        groups = Roster.read(self.meetings(),set(range(first,len(self.places)))).groups()
        demand = Counter(v for group in groups for v in group)
        nxt = max(freq)+1
        for u in range(first,len(self.places)):
            given = self.places[u]
            fresh = max(1,3-len(given))
            if self.law in (1,2,3,4,9):
                fresh = min(3,max(fresh,demand[u]))
            if self.knot_law=="parity" and reduce_rule(bits(given),base)==0:
                fresh=0
            given.update(range(nxt,nxt+fresh))
            nxt+=fresh
        return len(births),takes

    def step_readings(self,sources):
        by_place = {}
        for u,star in enumerate(self.places):
            for d in star:
                by_place.setdefault(d,[]).append(u)
        hist=Counter(map(len,by_place.values()))
        count=len(self.places)
        costs={k:[{} for _ in range(count)] for k in ("hs","hs_two_holders","weighted","ps")}
        for holders in by_place.values():
            price=len(holders)-1
            for a,b in itertools.combinations(holders,2):
                for u,v in [(a,b),(b,a)]:
                    costs["hs"][u][v]=1
                    costs["weighted"][u][v]=min(costs["weighted"][u].get(v,price),price)
                    if price==1:
                        costs["hs_two_holders"][u][v]=1
        for u, parents in enumerate(self.parents):
            for v in parents:
                costs["ps"][u][v]=costs["ps"][v][u]=1
        readings={"holders_hist":{str(n):freq for n,freq in hist.items()}}
        for kind,connections in costs.items():
            maxima=[]
            for c in range(sources):
                found={}
                pending=[(0,c)]
                while pending:
                    dist,u=heapq.heappop(pending)
                    if u in found:
                        continue
                    found[u]=dist
                    for v,price in connections[u].items():
                        if v not in found:
                            heapq.heappush(pending,(dist+price,v))
                maxima.append(max(found.values()))
            readings[kind]=maxima
        return readings


def exact_witness(places):
    masks=[bits(s) for s in places]
    n=max(d for s in places for d in s)+1
    allowed=[x for x in range(1<<n) if all((x&m).bit_count()%2==0 for m in masks)]
    counts=Counter(d for s in places for d in s)
    loose=[d for d in sorted(counts) if counts[d]==1]
    rules=[list(ds) for k in range(1,len(loose)+1) for ds in itertools.combinations(loose,k)
           if all((x&bits(ds)).bit_count()%2==0 for x in allowed)]
    checks=[]
    for star in places[-2:]:
        cols=sorted(star)
        projected=sorted({tuple((x>>d)&1 for d in cols) for x in allowed})
        names=[f"d{d}" for d in cols]
        clauses=[" ".join("~"+name if bit else name for name,bit in zip(names,row))
                 for row in itertools.product((0,1),repeat=len(cols)) if row not in projected]
        proc=subprocess.run([sys.executable,"-B","-m","knotlab","check","--cnf","; ".join(clauses),
                             "--loops",*names[:-1],"--contact",names[-1],"--json"],cwd=ROOT,text=True,
                             env={**os.environ,"PYTHONPATH":"tools"},capture_output=True,check=True)
        checks.append({"places":cols,"projection":projected,"verification":json.loads(proc.stdout)})
    return {"places":[sorted(s) for s in places],"number allowed":len(allowed),"loose":loose,
            "nonzero parity rules on loose":rules,"new knots":checks}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    args=p.parse_args()
    start=time.perf_counter()
    census=json.loads((TICKET/"census_starts.json").read_text())
    # Round one covers every three- and four-knot input. On the first four
    # such starts and the minimum witness start, extend through round three.
    panel=set(range(4,8))|{60}
    result=Counter()
    witnesses={}
    errors=[]
    for row in stream("run4",None):
        name=row["start"]
        if not name.startswith("census:"):
            continue
        idx=int(name.split(":")[1])
        if args.pilot and idx not in {4,60}:
            continue
        stars=census[idx]["stars"]
        g=SmallRounds(stars,row)
        result["start-law-seed-knot law rows"]+=1
        for t in range(1,(3 if idx in panel else 1)+1):
            births,takes=g.step()
            observed=row["births"][t-1] if t<=len(row["births"]) else 0
            if observed!=births:
                errors.append([name,row["law"],row["knot_law"],row["seed"],t,"births",births,observed])
                break
            if not births:
                result["terminations checked"]+=1
                break
            check={"takes":takes==row["takes_per_round"][t-1],
                   "steps and holders":g.step_readings(len(stars))==row["reads"][str(t)]["steps"]}
            result["grown stages"]+=1
            for kind,ok in check.items():
                if not ok:
                    errors.append([name,row["law"],row["knot_law"],row["seed"],t,kind])
            if idx==60 and t==1 and row["law"]=="T2" and row["knot_law"]=="parity":
                witnesses[row["seed"]]=exact_witness(g.places)
    print(result,"differences",len(errors),"seconds",round(time.perf_counter()-start,3))
    if errors:
        print(errors[:5])
    if not args.pilot:
        (HERE/"taking_replay.json").write_text(json.dumps(
            {"coverage":result,"differences":errors,"literal witnesses":witnesses},indent=2)+"\n")


if __name__=="__main__":
    main()
