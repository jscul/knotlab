"""Independent count of the union signatures by exact sum-product elimination."""
import argparse
import json
from itertools import product
from functools import reduce
from operator import and_, or_
from pathlib import Path
from time import monotonic

import numpy as np

from structure_union import bits, context, irreducible, project, read_blocks, simple_union, transposed, variable_order


def constraints(rows, n):
    all_bits = (1 << n)-1
    supports = [[row for row in rows if row & (1 << i)] for i in range(n)]
    must = [reduce(and_, group, all_bits) if group else (1<<j) for j, group in enumerate(supports)]
    def maxima(mask):
        implied = reduce(or_, (must[i] ^ (1<<i) for i in bits(mask)), 0)
        return mask & ~implied
    out = []
    for j, group in enumerate(supports):
        necessary = maxima(must[j] ^ (1<<j))
        out.extend((j, 1 << bit) for bit in bits(necessary))
        # j can be true only when at least one whole support is contained in the selected mask.
        # Distribute OR of positive conjunctions into a list of positive clauses, assuming j.
        minimal = []
        for row in sorted(set(group), key=int.bit_count):
            if not any(old & row == old for old in minimal):
                minimal.append(row)
        choices = [tuple(bits(maxima(row & ~must[j]))) for row in minimal]
        clauses = {sum(1<<i for i in set(alternatives)) for alternatives in product(*choices)}
        kept = []
        for mask in sorted(clauses,key=lambda mask:(mask.bit_count(),mask)):
            if not any(old & mask == old for old in kept):
                kept.append(mask)
        out.extend((j, mask) for mask in kept)
    return out


class Width(Exception):
    pass


def count_signatures(rows, n, max_width):
    rules = constraints(rows, n)
    scopes = [(1 << j) | mask for j, mask in rules]
    original_order = variable_order(scopes, n)
    order = {v:i for i,v in enumerate(original_order)}
    buckets = [[] for _ in range(n)]
    unit = np.ones(1,dtype=np.uint64)
    for (j, other), scope in zip(rules, scopes):
        axes = tuple(sorted(order[x] for x in bits(scope)))
        factor = np.ones((2,) * len(axes), dtype=np.uint64)
        invalid = [0] * len(axes)
        invalid[axes.index(order[j])] = 1
        factor[tuple(invalid)] = 0
        buckets[axes[0]].append((axes, factor))
    max_int = int(np.iinfo(np.uint64).max)
    max_bag = 0
    cells = 0
    total = 1
    for i in range(n):
        factors = buckets[i]
        axes = tuple(sorted({i} | {j for scope, factor in factors for j in scope}))
        size = len(axes)-1
        max_bag = max(max_bag, size)
        if size > max_width:
            raise Width(size)
        cells += 1 << size
        # The trailing dimension of length one is expanded if this is a free variable.
        value = unit.reshape((1,) * len(axes))
        hi = 1
        for scope, factor in factors:
            local_upper = int(factor.max())
            if hi > 0 and local_upper > max_int // hi:
                value = value.astype(object)
            shape = tuple(2 if j in scope else 1 for j in axes)
            value = value * factor.reshape(shape)
            hi = int(value.max())
        if hi > max_int // 2:
            value = value.astype(object)
        # Sum over zero and one. Other unconstrained coordinates are represented by other factors.
        if value.shape[0] == 1:
            result = value[0] * 2
        else:
            result = value[0] + value[1]
        if len(axes) == 1:
            total *= int(result)
        else:
            buckets[axes[1]].append((axes[1:], result))
        buckets[i] = []
    return int(total), max_bag, cells


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", type=Path)
    ap.add_argument("--left", type=int,default=35)
    ap.add_argument("--right", type=int,default=0)
    ap.add_argument("--sizes", type=int,nargs="+",default=[75,85,95,100,105,110])
    ap.add_argument("--max-width", type=int,default=23)
    ap.add_argument("--controls", action='store_true')
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    if args.controls:
        for mask in range(512):
            table=[(mask>>(3*j))&7 for j in range(3)]
            physical=transposed(dict(enumerate(table)),list(range(3)))
            columns,_,rows=project(physical,list(range(3)))
            assert count_signatures(rows,len(columns),4)[0] == len(simple_union(table))
    n,bs=read_blocks(args.stage)
    left,_,physical=context(bs,args.left,args.right)
    all_dims=list(irreducible(physical))
    out=[]
    for k in args.sizes:
        start=monotonic()
        cols,_,rows=project(physical,left,all_dims[:k])
        row=dict(requested=k,projected_columns=len(cols))
        try:
            number, width, cells = count_signatures(rows,len(cols),args.max_width)
            row.update(count=number, width=width, sum_separator_cells=cells)
        except Width as exc:
            row.update(exceeded_width=int(exc.args[0]))
        row["seconds"]=monotonic()-start
        out.append(row)
        print(row, flush=True)
    if args.out:
        args.out.write_text(json.dumps(dict(blocks=[args.left,args.right],stage_sites=n,small_contexts_checked=512 if args.controls else 0,rows=out),indent=2)+"\n")


if __name__ == "__main__":
    main()
