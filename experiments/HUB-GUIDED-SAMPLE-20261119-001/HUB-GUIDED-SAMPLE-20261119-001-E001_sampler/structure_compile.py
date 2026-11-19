"""Compile the two-block trace constraints to decomposable and/or decisions."""
import argparse
import json
from pathlib import Path
from time import monotonic

from structure_eliminate import constraints
from structure_union import bits, context, irreducible, project, read_blocks, simple_union, transposed


def simplify(rules, ones, zeros):
    while True:
        positive_unit, negative_unit = 0, 0
        remaining = set()
        for neg, pos in rules:
            if zeros & neg or ones & pos:
                continue
            neg &= ~ones
            pos &= ~zeros
            both = neg | pos
            if not both:
                return None
            if both & (both-1) == 0:
                negative_unit |= neg
                positive_unit |= pos
            else:
                remaining.add((neg,pos))
        if not (positive_unit | negative_unit):
            return sorted(remaining), ones, zeros
        ones |= positive_unit
        zeros |= negative_unit
        if ones & zeros:
            return None
        rules = remaining


def groups(rules):
    parts = []
    for neg, pos in rules:
        current = neg | pos
        found = []
        for part in parts:
            if part & current:
                current |= part
            else:
                found.append(part)
        found.append(current)
        parts = found
    return parts


class Compiler:
    def __init__(self, cap):
        # 0 is false, 1 true. Literals, free bits, and decisions share type B.
        # B rows are (variable, off, on); A rows are (-1, child1,...,childK).
        self.nodes=[(-2,),(-3,)]
        self.counts=[0,1]
        self.ident={}
        self.cache={}
        self.cap=cap
        self.calls=0

    def make(self,node):
        if node in self.ident:
            return self.ident[node]
        index=len(self.nodes)
        self.ident[node]=index
        self.nodes.append(node)
        if node[0]>=0:
            total=self.counts[node[1]]+self.counts[node[2]]
        else:
            total=1
            for child in node[1:]:
                total*=self.counts[child]
        self.counts.append(total)
        return index

    def conjunction(self,children):
        if 0 in children:
            return 0
        subs=sorted(c for c in children if c!=1)
        if not subs:
            return 1
        if len(subs)==1:
            return subs[0]
        return self.make((-1,*subs))

    def solve(self,rules,scope,ones=0,zeros=0):
        self.calls+=1
        if self.calls > self.cap:
            raise OverflowError("decision cap")
        outcome=simplify(rules,ones,zeros)
        if outcome is None:
            return 0
        rest,ones,zeros=outcome
        assert ones & zeros == 0
        forced=[self.make((i,0,1)) for i in bits(ones)]
        forced.extend(self.make((i,1,0)) for i in bits(zeros))
        components=groups(rest)
        used=ones|zeros
        for part in components:
            used|=part
        assert used & ~scope==0
        forced.extend(self.make((i,1,1)) for i in bits(scope & ~used))
        if not rest:
            return self.conjunction(forced)
        if len(components)>1:
            for part in components:
                subset=[row for row in rest if (row[0]|row[1])&part]
                forced.append(self.core(subset,part))
        else:
            forced.append(self.core(rest,components[0]))
        return self.conjunction(forced)

    def core(self,rules,scope):
        key=tuple(rules)
        if key in self.cache:
            return self.cache[key]
        scores={}
        for neg,pos in rules:
            mask=neg|pos
            weight=2**(-min(8,mask.bit_count()))
            for i in bits(mask):
                s=scores.setdefault(i,[0.,0.])
                s[int(bool(pos&(1<<i)))]+=weight
        i=max(scores,key=lambda v:(scores[v][0]*scores[v][1]+0.05*sum(scores[v]),-v))
        pivot=1<<i
        # Branching on a distinguished variable; its literal is stored only in the outer B node.
        def side(value):
            new=[]
            for neg,pos in rules:
                if (pos if value else neg)&pivot:
                    continue
                new.append((neg & ~pivot,pos & ~pivot))
            return self.solve(new,scope^pivot)
        lo=side(False)
        hi=side(True)
        root=self.make((i,lo,hi))
        self.cache[key]=root
        return root

    def decode(self,node,rank):
        assert 0<=rank<self.counts[node]
        if node==1:
            return 0
        rule=self.nodes[node]
        if rule[0]>=0:
            i,lo,hi=rule
            if rank<self.counts[lo]:
                return self.decode(lo,rank)
            return (1<<i) | self.decode(hi,rank-self.counts[lo])
        mask=0
        for child in rule[1:]:
            rank,digit=divmod(rank,self.counts[child])
            mask |= self.decode(child,digit)
        assert rank==0
        return mask


def compiled(rows,k,cap):
    rules=[(1<<j,pos) for j,pos in constraints(rows,k)]
    engine=Compiler(cap)
    root=engine.solve(rules,(1<<k)-1)
    return engine,root


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage",type=Path)
    ap.add_argument("--left",type=int,default=35)
    ap.add_argument("--right",type=int,default=0)
    ap.add_argument("--sizes",type=int,nargs="+",default=[85,105,110])
    ap.add_argument("--controls",action="store_true")
    ap.add_argument("--cap",type=int,default=200000)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    if args.controls:
        for raw in range(512):
            table=[(raw>>(3*j))&7 for j in range(3)]
            phys=transposed(dict(enumerate(table)),list(range(3)))
            cols,_,rows=project(phys,list(range(3)))
            e,r=compiled(rows,len(cols),200000)
            answers={e.decode(r,i) for i in range(e.counts[r])}
            assert answers==simple_union(rows)
    _,bs=read_blocks(args.stage);left,_,physical=context(bs,args.left,args.right)
    chosen=list(irreducible(physical))
    output=[]
    for k in args.sizes:
        start=monotonic()
        cols,_,rows=project(physical,left,chosen[:k])
        record=dict(requested=k,coordinates=len(cols),decision_cap=args.cap)
        try:
            e,r=compiled(rows,len(cols),args.cap)
            record.update(count=e.counts[r], decisions=e.calls,nodes=len(e.nodes))
        except OverflowError:
            record["capped"]=True
        record["seconds"]=monotonic()-start
        output.append(record)
        print(record,flush=True)
    if args.out:
        args.out.write_text(json.dumps(output,indent=2)+"\n")


if __name__=="__main__":
    main()
