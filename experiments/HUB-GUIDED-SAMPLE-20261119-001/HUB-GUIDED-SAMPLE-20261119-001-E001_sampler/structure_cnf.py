"""Unique-extension CNF for the maximal groups of a physical two-hub context."""
import argparse
import hashlib
from functools import reduce
from operator import and_, or_
from pathlib import Path

from structure_union import bits, context, irreducible, minimum_rows_by_column, project, read_blocks


def binary_closure_cnf(rows, n, reduce_implications):
    grouped = minimum_rows_by_column(rows,n) if reduce_implications else [
        [m for m in rows if m & (1<<j)] for j in range(n)]
    if reduce_implications:
        must=[reduce(and_, available) if available else 1<<j for j,available in enumerate(grouped)]
        def maxima(m):
            implied=reduce(or_,(must[j] ^ (1<<j) for j in bits(m)),0)
            return m & ~implied
    else:
        must=[1<<j for j in range(n)]
        maxima=lambda mask: mask
    aux={m: n+i+1 for i,m in enumerate(rows)}
    clauses=[]
    for j in range(n):
        for k in bits(maxima(must[j]^(1<<j))):
            clauses.append([-(j+1),k+1])
        clauses.append([-(j+1),*(aux[m] for m in grouped[j])])
    for m,y in aux.items():
        minimal=list(bits(maxima(m)))
        clauses.extend([[-y,j+1] for j in minimal])
        clauses.append([y,*(-(j+1)for j in minimal)])
    return n+len(aux),clauses


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage",type=Path)
    ap.add_argument("dimacs",type=Path)
    ap.add_argument("--left",type=int,default=13)
    ap.add_argument("--right",type=int,default=4)
    ap.add_argument("--k",type=int,default=1000000)
    ap.add_argument("--literal",action="store_true")
    args=ap.parse_args()
    _,bs=read_blocks(args.stage)
    left,right,physical=context(bs,args.left,args.right)
    cols,_,rows=project(physical,left,list(irreducible(physical))[:args.k])
    n,clauses=binary_closure_cnf(rows,len(cols),not args.literal)
    with args.dimacs.open("w")as stream:
        print("p cnf",n,len(clauses),file=stream)
        for clause in clauses:
            print(*clause,0,file=stream)
    print(n,len(clauses),hashlib.sha256(args.dimacs.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
