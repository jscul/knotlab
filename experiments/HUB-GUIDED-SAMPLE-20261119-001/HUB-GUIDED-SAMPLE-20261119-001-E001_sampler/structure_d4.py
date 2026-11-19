"""Convert a checked d4 decision circuit on the physical two-hub equations to an exact unranker."""
import argparse
from collections import defaultdict
import hashlib
import json
import random
from pathlib import Path

from structure_cnf import binary_closure_cnf
from structure_compile import Compiler
from structure_export import check_groups, physical_sites
from structure_rank import compress, load, save, unrank
from structure_union import bits, context, project, read_blocks


def parse(path):
    kind={}
    arcs=defaultdict(list)
    incoming=set()
    for line in path.open():
        fields=line.split()
        assert fields[-1]=="0"
        if fields[0] in ("a","o","t","f"):
            kind[int(fields[1])]=fields[0]
        else:
            i,target=map(int,fields[:2])
            positive,negative=0,0
            for lit in map(int,fields[2:-1]):
                if lit>0:
                    positive |= 1<<(lit-1)
                else:
                    negative |= 1<<(-lit-1)
            assert not positive&negative
            arcs[i].append((target,positive,negative))
            incoming.add(target)
    roots=set(kind)-incoming
    assert len(roots)==1
    return kind,arcs,roots.pop()


def convert(path,variables,physical):
    kinds,arcs,root=parse(path)
    memo={}
    engine=Compiler(1)
    aux_sum=physical
    physical_bits=(1<<physical)-1
    def literal(j):
        return engine.make((j,0,1))
    def smooth(node,free):
        if free:
            # Full CNF determines every auxiliary once its physical assignment is given.
            # A freely assignable auxiliary on a satisfiable branch would violate this.
            assert free & ~physical_bits == 0
            return engine.conjunction([node,*[engine.make((j,1,1)) for j in bits(free)]])
        return node
    def visit(i):
        if i in memo:
            return memo[i]
        kind=kinds[i]
        if kind in ("f","t"):
            answer=(int(kind=="t"),0,0,0)
        else:
            children=[]
            for target,pos,neg in arcs[i]:
                code,scope,mpos,mneg=visit(target)
                if code==0:
                    if kind=="a":
                        answer=(0,0,0,0)
                        memo[i]=answer
                        return answer
                    continue
                labels=pos|neg
                assert not scope & labels
                seq=[code,*[literal(j) for j in bits(pos&physical_bits)]]
                children.append((engine.conjunction(seq),scope|labels,mpos|pos,mneg|neg))
            if kind=="a":
                scope,ap,an=0,0,0
                components=[]
                for code,scope1,p1,n1 in children:
                    assert not scope&scope1
                    scope|=scope1
                    ap|=p1
                    an|=n1
                    components.append(code)
                answer=(engine.conjunction(components),scope,ap,an)
            elif not children:
                answer=(0,0,0,0)
            else:
                scope=0
                ap,an=children[0][2:]
                for j,(code,scope1,p1,n1) in enumerate(children):
                    scope|=scope1
                    for _,_,p2,n2 in children[:j]:
                        assert (p1&n2)|(n1&p2), "OR alternatives are not certified disjoint"
                    ap&=p1
                    an&=n1
                branches=[smooth(code,scope^scope1) for code,scope1,_,_ in children]
                code=branches[0]
                for extra in branches[1:]:
                    # The last mask position is purely internal and no physical row observes it.
                    code=engine.make((aux_sum,code,extra))
                answer=(code,scope,ap,an)
        memo[i]=answer
        return answer
    node,scope,_,_=visit(root)
    assert scope < 1<<variables
    node=smooth(node,((1<<variables)-1)^scope)
    return engine,node,len(memo)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage",type=Path)
    ap.add_argument("circuit",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--left",type=int,default=13)
    ap.add_argument("--right",type=int,default=4)
    ap.add_argument("--expected",type=int,required=True)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    n,blocks=read_blocks(args.stage)
    left,right,exclusions=context(blocks,args.left,args.right)
    columns,_,rows=project(exclusions,left)
    variables,clauses=binary_closure_cnf(rows,len(columns),True)
    engine,root,nodes_used=convert(args.circuit,variables,len(columns))
    assert engine.counts[root]==args.expected
    compact_root,nodes=compress(engine,root)
    sites=physical_sites(blocks,args.left,args.right,left,right,exclusions,columns)
    data=dict(n=n,coordinates=[*columns,-1],count=engine.counts[root],root=compact_root,nodes=nodes,sites=sites)
    save(args.output,data)
    rng=random.Random(413001975)
    ranks={0,data["count"]-1}
    for _ in range(14):
        ranks.add(rng.randrange(data["count"]))
    loaded=load(args.output)
    direct=check_groups(blocks,loaded,sorted(ranks),decode=unrank)
    record=dict(source_blocks=[args.left,args.right],input_variables=variables,input_clauses=len(clauses),
                physical_coordinates=len(columns),auxiliary_output_bit=len(columns),
                reachable_d4_nodes=nodes_used,output_nodes=len(nodes),induced_sites=len(sites),
                count=data["count"],direct_maximality_checks=direct,
                uncompressed_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                circuit_sha256=hashlib.sha256(args.circuit.read_bytes()).hexdigest(),
                stage_sha256=hashlib.sha256(args.stage.read_bytes()).hexdigest())
    if args.report:
        args.report.write_text(json.dumps(record,indent=2)+"\n")
    print({k:v for k,v in record.items() if k!='direct_maximality_checks'})

if __name__=="__main__":
    main()
