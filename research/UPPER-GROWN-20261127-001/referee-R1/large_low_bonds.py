"""Count the actual one-word bonds on the two stages below eight in the local search."""
import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
from time import perf_counter

from large_controls import ActualStage
from large_search import candidates, clauses, members, stage_list


def check(idx, r, stage, limited):
    partial, _ = clauses(stage)
    edges, names = candidates(stage, partial)
    signs_by_carriers = defaultdict(set)
    for edge in edges:
        signed = sorted(names[i] for i in edge)
        carriers, values = zip(*signed)
        signs_by_carriers[carriers].add(values)
    entries = sorted(signs_by_carriers.items())
    selected = entries if limited is None else entries[:limited]
    source = ActualStage(stage)
    # Install every reading before timing so a prefix uses the final solver size.
    relevant = sorted({g for carriers,_ in entries for g in carriers})
    for g in relevant:
        source.agreement(g)
        source.agreement(g,1)
    begin = perf_counter()
    rejected = Counter()
    proper = Counter()
    in_bonds = set()
    for carriers, possible in selected:
        if len(possible) > 1:
            rejected['multiple structurally certified missing words'] += 1
            continue
        if not all(source.is_unread(g) for g in carriers):
            rejected['reading determined at one source knot'] += 1
            continue
        signs, = possible
        literals = [source.agreement(g) for g in carriers]
        missing = [word for word in product((0,1), repeat=3)
                   if not source.sat.solve(assumptions=[v if b else -v for v,b in zip(literals,word)])]
        assert signs in missing
        if missing == [signs]:
            proper[''.join(map(str,signs))] += 1
            in_bonds.update(carriers)
        else:
            rejected['additional missing words on source'] += 1
    word_seconds = perf_counter()-begin
    sensitive = 0
    checked_places = 0
    for m in sorted(in_bonds):
        for x in members(m):
            # Demand two full allowed source states differing at x alone.
            query=[-source.agreement(m),source.agreement(m,1)]
            query.extend(q for i,q in enumerate(source.same) if i != x)
            sensitive += source.sat.solve(assumptions=query)
            checked_places += 1
    source.sat.delete()
    assert len(selected) == sum(proper.values()) + sum(rejected.values())
    return {'start':idx, 'round':r,'source knots':len(stage),'distinctions':source.n,
            'candidate carrier triples':len(entries),'tested carrier triples':len(selected),
            'eligible one-word first bonds':sum(proper.values()),'by missing word in increasing carrier-mask order':proper,
            'rejected':rejected,'seconds querying words and unreadability':round(word_seconds,5),
            'distinct carriers in eligible bonds':len(in_bonds),
            'carrier-member incidences on these carriers':checked_places,
            'incidences with a single allowed raw flip changing the reading':sensitive,
            'seconds checking raw single flips':round(perf_counter()-begin-word_seconds,5)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    start=perf_counter()
    roster={(idx,r):s for idx,r,_,s in stage_list()}
    rows=[check(idx,r,roster[idx,r],args.limit) for idx,r in ((32,2),(2547,1))]
    args.output.write_text(json.dumps({'rows':rows,'seconds':round(perf_counter()-start,5)},indent=2)+'\n')


if __name__=='__main__':
    main()
