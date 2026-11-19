"""Test the exact first failed order on unshielded, two-hub parity cores."""
from itertools import permutations
from math import gcd
from pathlib import Path
import argparse
import json
import subprocess
import tempfile

def canonical(rows):
    used=0
    for mask in rows:
        used |= mask >> 1
    weak=[1<<v for v in range(1,used.bit_length()+1) if used&(1<<(v-1))]
    options=[]
    for perm in permutations(weak):
        converted=tuple(sorted((mask&1) + sum(1<<(i+1) for i,bit in enumerate(perm) if mask&bit)
                               for mask in rows))
        options.append(converted)
    return min(options)

def patterns(high):
    previous={()}
    all_rows=[]
    for order in range(1,high+1):
        new=set()
        for old in previous:
            used=max((x.bit_length()-1 for x in old),default=0)
            for middle in range(len(old)+1):
                for outer in range(used+2):
                    trial=list(old) if middle<len(old) else [*old,0]
                    if trial[middle] & (1<<outer):
                        continue
                    trial[middle] |= 1<<outer
                    new.add(canonical(trial))
        all_rows.extend((order,max(x.bit_length()-1 for x in shape),shape) for shape in sorted(new))
        previous=new
    return all_rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--max-order',type=int,default=5)
    parser.add_argument('--weak',type=int,default=8)
    parser.add_argument('--per-hub',type=int,default=12)
    parser.add_argument('--spoke-weight',type=int,default=12)
    parser.add_argument('--anchor-weight',type=int,default=1)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    shapes=patterns(args.max_order)
    items=[(t,s,l,h) for t in range(2,args.weak+1) for s in range(2,args.per_hub+1)
           for l in range(1,args.spoke_weight+1) for h in range(1,args.anchor_weight+1)
           if gcd(l,h)==1 and s*l>=3]
    inputs=[str(len(shapes)),*(' '.join(map(str,[r,u,len(xs),*xs])) for r,u,xs in shapes),
            *(' '.join(map(str,x)) for x in items)]
    with tempfile.TemporaryDirectory(prefix='bond-static-exact-') as tmp:
        exe=Path(tmp)/'screen'
        subprocess.run(['c++','-std=c++20','-O3',str(Path(__file__).with_suffix('.cpp')),'-o',str(exe)],check=True)
        out=subprocess.run([exe],input='\n'.join(inputs)+'\n',text=True,capture_output=True,check=True)
    family=[list(map(int,row.split())) for row in out.stdout.splitlines()]
    assert [row[:4] for row in family]==[list(v) for v in items]
    bounds=[]
    for r in range(2,args.max_order+1):
        valid=[]
        for t,s,l,h,fail,_ in family:
            if fail and fail<=r:
                continue
            J=t+2*s+4
            # The growing end replaces ONE name at a fixed weak-anchor bundle.
            n=2*s*(t*h+l)+5
            valid.append((J,n,t,s,l,h))
        bounds.append(dict(r=r,valid=len(valid),least_j_then_n=min(valid,default=None),
                           least_n_then_j=min(valid,key=lambda x:(x[1],x[0]),default=None)))
    args.output.write_text(json.dumps(dict(max_order=args.max_order,bounds=[args.weak,args.per_hub,args.spoke_weight,args.anchor_weight],
        canonical_patterns_by_order={r:sum(k==r for k,_,_ in shapes) for r in range(1,args.max_order+1)},
        rows=bounds,parameter_count=len(items),populations=family),separators=(',',':'))+'\n')

if __name__=='__main__':
    main()
