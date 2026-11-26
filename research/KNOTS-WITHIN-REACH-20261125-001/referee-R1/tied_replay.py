"""Regrow every published parity tie through its recorded round (up to ten)."""
import argparse
import itertools
import json
import time
from collections import Counter

from taking_replay import SmallRounds, bits, reduce_rule, relation_basis, TICKET
from taking_tables import stream, HERE
from stage_parity import rank


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--limit",type=int)
    args=p.parse_args()
    census=json.loads((TICKET/"census_starts.json").read_text())
    named=json.loads((TICKET/"named_starts.json").read_text())["named_starts"]
    counts=Counter()
    disagreements=[]
    start=time.perf_counter()
    for row in stream("run4",None):
        stages={int(t):v for t,v in row["tied"].items() if int(t)<=10}
        if not stages:
            continue
        if args.limit is not None and counts["runs"]>=args.limit:
            break
        counts["runs"]+=1
        key=row["start"]
        stars=census[int(key.split(":")[1])]["stars"] if key.startswith("census:") else named[key]
        g=SmallRounds(stars,row)
        for t in range(1,max(stages)+1):
            births,_=g.step()
            assert births==row["births"][t-1] and len(g.places)==row["knots_per_round"][t], (key,row["law"],row["seed"],t,len(g.places),row["knots_per_round"][t])
            if t not in stages:
                continue
            counts["positive stages"]+=1
            freq=Counter(d for s in g.places for d in s)
            loose={d:u for u,s in enumerate(g.places) for d in s if freq[d]==1}
            masks=list(map(bits,g.places))
            basis=relation_basis(masks)
            def passes(u):
                return len(g.places[u])>=3 and len(basis)-rank(m & ~masks[u] for m in masks)==1
            pairs=set()
            for a,b in itertools.combinations(sorted(loose),2):
                if loose[a]==loose[b] or reduce_rule((1<<a)|(1<<b),basis):
                    continue
                counts["distinct-holder equal pairs"]+=1
                if passes(loose[a]) and passes(loose[b]):
                    pairs.add((a,b))
            recorded={tuple(sorted((r["a"],r["b"]))) for r in stages[t]["rows"] if all(r["pass"])}
            if pairs!=recorded:
                disagreements.append([key,row["law"],row["seed"],t,len(pairs),len(recorded)])
            counts["pairs whose two holders both pass including arity"]+=len(pairs)
    print("seconds",round(time.perf_counter()-start,3),counts,"disagreements",len(disagreements))
    if args.limit is None:
        (HERE/"tied_replay.json").write_text(json.dumps({"counts":counts,"disagreements":disagreements},indent=2)+"\n")


if __name__=="__main__":
    main()
