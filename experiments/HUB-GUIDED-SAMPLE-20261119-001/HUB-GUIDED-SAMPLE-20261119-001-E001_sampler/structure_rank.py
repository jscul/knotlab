"""Portable exact mixed-radix unranker for physical maximal groups of an induced stage."""
import argparse
import base64
import gzip
import hashlib
import io
import json
import random
import zlib
from pathlib import Path

from structure_compile import compiled
from structure_export import check_groups, physical_sites
from structure_union import context, irreducible, project, read_blocks


def compress(engine, root):
    ids={0:0,1:1}
    rows=[(0,-2),(1,-3)]
    def visit(i):
        if i not in ids:
            row=engine.nodes[i]
            children=tuple(visit(c) for c in row[1:])
            ids[i]=len(rows)
            rows.append((engine.counts[i],row[0],*children))
        return ids[i]
    return visit(root),rows


def load(path):
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt") as stream:
        return parse_ranker(stream)


def load_bundled(path, name):
    record=json.loads(path.read_text())[name]
    data=zlib.decompress(base64.b64decode(record["deflate_base64"],validate=True))
    assert hashlib.sha256(data).hexdigest()==record["sha256"]
    assert len(data)==record["uncompressed_bytes"]
    return parse_ranker(io.StringIO(data.decode("ascii")))


def parse_ranker(stream):
    cursor=iter(stream)
    marker,n,k,t,h,root,total=next(cursor).split()
    assert marker=="DNNF1"
    n,k,t,h,root,total=map(int,(n,k,t,h,root,total))
    columns=list(map(int,next(cursor).split()))
    assert len(columns)==k
    nodes=[tuple(map(int,next(cursor).split())) for _ in range(t)]
    sites=[]
    for _ in range(h):
        v,side,*pieces=map(int,next(cursor).split())
        assert len(pieces)==(k+63)//64
        sites.append((v,side,sum(m<<(64*i) for i,m in enumerate(pieces))))
    assert next(cursor,None) is None
    return dict(n=n,coordinates=columns,root=root,count=total,nodes=nodes,sites=sites)


def save(path,data):
    k=len(data["coordinates"])
    with path.open("w") as stream:
        print("DNNF1",data["n"],k,len(data["nodes"]),len(data["sites"]),data["root"],data["count"],file=stream)
        print(*data["coordinates"],file=stream)
        for node in data["nodes"]:
            print(*node,file=stream)
        for v,side,mask in data["sites"]:
            print(v,side,*((mask>>(64*j)) & ((1<<64)-1) for j in range((k+63)//64)),file=stream)


def unrank(data,rank):
    assert 0<=rank<data["count"]
    nodes=data["nodes"]
    def take(i,r):
        count,kind,*children=nodes[i]
        assert 0<=r<count
        if kind==-3:
            return 0
        if kind>=0:
            low,high=children
            boundary=nodes[low][0]
            if r<boundary:
                return take(low,r)
            return (1<<kind) | take(high,r-boundary)
        assert kind==-1
        mask=0
        for child in children:
            r,digit=divmod(r,nodes[child][0])
            mask |= take(child,digit)
        assert r==0
        return mask
    mask=take(data["root"],rank)
    return [v for v,side,w in data["sites"] if ((w&mask)==0 if side else (w&~mask)==0)]


def build(path,left_id,right_id,k,limit):
    n,blocks=read_blocks(path)
    left,right,exclusions=context(blocks,left_id,right_id)
    selected=list(irreducible(exclusions))[:k]
    coordinates,_,rows=project(exclusions,left,selected)
    engine,root=compiled(rows,len(coordinates),limit)
    compact_root,nodes=compress(engine,root)
    sites=physical_sites(blocks,left_id,right_id,left,right,exclusions,coordinates)
    return blocks,dict(n=n,sites=sites,nodes=nodes,root=compact_root,
                       coordinates=coordinates,count=engine.counts[root],
                       calls=engine.calls)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--report",type=Path)
    ap.add_argument("--left",default=35,type=int)
    ap.add_argument("--right",default=0,type=int)
    ap.add_argument("--k",default=120,type=int)
    ap.add_argument("--cap",default=600000,type=int)
    args=ap.parse_args()
    blocks,data=build(args.stage,args.left,args.right,args.k,args.cap)
    save(args.output,data)
    target=load(args.output)
    rng=random.Random(81073102)
    ranks={0,data["count"]-1}
    for _ in range(12):
        ranks.add(rng.randrange(data["count"]))
    for r in ranks:
        assert unrank(data,r)==unrank(target,r)
    checks=check_groups(blocks,target,sorted(ranks),decode=unrank)
    report=dict(blocks=[args.left,args.right],requested_sparse_coordinates=args.k,
                stage_sha256=hashlib.sha256(args.stage.read_bytes()).hexdigest(),
                source_sites=data["n"],induced_sites=len(data["sites"]),coordinates=len(data["coordinates"]),
                nodes=len(data["nodes"]),decisions=data["calls"],count=data["count"],
                direct_maximality_checks=checks,filename=args.output.name,
                uncompressed_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    if args.report:
        args.report.write_text(json.dumps(report,indent=2)+"\n")
    print({k:v for k,v in report.items() if k!="direct_maximality_checks"})


if __name__=="__main__":
    main()
