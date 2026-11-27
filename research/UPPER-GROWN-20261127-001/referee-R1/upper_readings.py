"""Seek upper readings on a connected family of four lower clauses with six disjoint carriers."""
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path
from time import perf_counter
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent
sys.path.insert(0, str(RESEARCH/'NAE-LAYER-20261127-001'/'referee-R1'))
from growth_rule import supports_of, advance


def columns(n):
    bits = 1 << n
    all_states = (1 << bits) - 1
    # Alternating blocks of zeros and ones in assignment order.
    return all_states, [((all_states // ((1 << (1 << i)) + 1)) << (1 << i)) for i in range(n)]


def agree(carrier, cols, universe):
    first, *rest = carrier
    acc = universe
    for other in rest:
        acc &= ~(cols[first] ^ cols[other])
    return acc


def words(allowed, bits):
    cells = [allowed]
    for x in bits:
        cells = [s for cell in cells for s in (cell & ~x, cell & x)]
    return [i for i, s in enumerate(cells) if s]


def get_clauses(knots):
    n = max(max(k) for k in knots) + 1
    universe, cols = columns(n)
    law = [universe ^ agree(k, cols, universe) for k in knots]
    states = universe
    for x in law:
        states &= x
    fixes = []
    for k in knots:
        cells = [states]
        for v in k:
            cells = [s for cell in cells for s in [cell & cols[v], cell & ~cols[v]] if s]
        fixes.append(cells)
    reads = {}
    for size in (2,3):
        for c in combinations(range(n), size):
            yes = agree(c, cols, universe)
            if all(any(cell & yes and cell & ~yes for cell in fix) for fix in fixes):
                reads[sum(1 << x for x in c)] = yes
    keys = sorted(reads)
    true = [reads[k] & states for k in keys]
    pairs = defaultdict(set)
    triples = []
    for i, a in enumerate(keys):
        for j in range(i+1, len(keys)):
            b = keys[j]
            if a & b:
                continue
            ab = a | b
            subset = true[i] & true[j]
            if not subset:
                continue
            for k in range(j+1,len(keys)):
                c = keys[k]
                if ab & c or subset & true[k]:
                    continue
                triple = a,b,c
                if len(words(states,[reads[v] for v in triple])) != 7:
                    continue
                triples.append(triple)
                for p,q,r in ((a,b,c),(a,c,b),(b,c,a)):
                    pairs[p,q].add(r)
    return states, law, reads, triples, pairs


def four_clauses(triples,pairs):
    by_one = defaultdict(list)
    for x,y,z in triples:
        for a,b,c in ((x,y,z),(y,x,z),(z,x,y)):
            by_one[a].append((b,c))
    for a, others in by_one.items():
        # Take the smallest mask as the shared reading, for one visit per pattern.
        for i,(b,c) in enumerate(others):
            if min(b,c) <= a:
                continue
            for d,e in others[i+1:]:
                if (b|c) & (d|e) or min(d,e) <= a:
                    continue
                union = a|b|c|d|e
                for u,v in ((d,e),(e,d)):
                    p = pairs.get(tuple(sorted((b,u))))
                    q = pairs.get(tuple(sorted((c,v))))
                    if p and q:
                        for f in sorted(p&q):
                            if f > a and not f & union:
                                yield ((a,f),(b,v),(c,u)), ((a,b,c),(a,d,e),(b,u,f),(c,v,f))


def rectangles(triples, pairs):
    by_pair = defaultdict(list)
    for (a,b), endings in pairs.items():
        for c,d in combinations(sorted(endings), 2):
            if c & d == 0:
                by_pair[c,d].append((a,b))
    for (c,d), partners in by_pair.items():
        for i,(a,b) in enumerate(partners):
            for e,f in partners[i+1:]:
                if (a|b) & (e|f):
                    continue
                for x,y in ((e,f),(f,e)):
                    # Both of the first two pairs may supply the AND reading.
                    yield ((a,x),(b,y),(c,d)),((a,b,c),(a,b,d),(e,f,c),(e,f,d))


def inspect(knots, start_n, require_birth, pattern):
    begin = perf_counter()
    states,law,reads,triples,pairs = get_clauses(knots)
    n = max(max(k) for k in knots)+1
    universe, cols = columns(n)
    row = dict(source_knots=len(knots), distinctions=n, single_clauses_missing_111=len(triples))
    attempts = 0
    finder = rectangles if pattern == "pairs" else four_clauses
    for groups, clauses in finder(triples,pairs):
        for first in range(3):
            attempts += 1
            upper = [(reads[a]&reads[b]) if i==first else (reads[a]|reads[b]) for i,(a,b) in enumerate(groups)]
            if words(states,upper) != list(range(7)):
                continue
            missing = upper[0] & upper[1] & upper[2]
            after = []
            for drop in range(len(law)):
                restored = missing
                for j,x in enumerate(law):
                    if j != drop:
                        restored &= x
                after.append(restored.bit_count())
            if require_birth and not any(after[start_n:]):
                continue
            fmt = lambda mask:[j for j in range(n) if (mask>>j)&1]
            order = [x for group in groups for x in group]
            idx = {x:i for i,x in enumerate(order)}
            physical_upper = [states]
            for bit in upper:
                physical_upper = [s for cell in physical_upper for s in (cell&~bit,cell&bit)]
            lower_words = words(states,[reads[x] for x in order])
            xuniv,xc = columns(6)
            lower_laws = [~(xc[idx[a]] & xc[idx[b]] & xc[idx[c]]) & xuniv for a,b,c in clauses]
            xupper = [xc[2*i]&xc[2*i+1] if i==first else xc[2*i]|xc[2*i+1] for i in range(3)]
            def abstract_image(drop):
                s=xuniv
                for i,ll in enumerate(lower_laws):
                    if i!=drop:
                        s &= ll
                return words(s,xupper)
            if abstract_image(-1) != list(range(7)):
                continue
            assert all(abstract_image(j)==list(range(8)) for j in range(4))
            # Every upper reading must vary in at least one fix of each lower bond on the actual stage.
            mixed = []
            for clause in clauses:
                cells=[states]
                for x in clause:
                    cells=[s for cell in cells for s in (cell&reads[x],cell&~reads[x]) if s]
                mixed.append([sum(bool(s&u) and bool(s&~u) for s in cells) for u in upper])
            if not all(min(rr)>0 for rr in mixed):
                continue
            sens = [[(states & ~cols[j] & (states >> (1<<j)) & (reads[x] ^ (reads[x] >> (1<<j)))).bit_count() for j in fmt(x)] for x in order]
            if not all(min(rr)>0 for rr in sens):
                continue
            row['witness'] = dict(knots=knots,source_laws=start_n,carriers=[fmt(x) for x in order],and_pair=first,
                lower_clauses_missing_111=[[idx[x] for x in cc] for cc in clauses],lower_words=[format(x,'06b') for x in lower_words],
                upper_word_counts=[s.bit_count() for s in physical_upper],restorations_by_dropped_source_law=after,
                abstract_upper_after_each_lower_deletion=[abstract_image(j) for j in range(4)],upper_mixed_fixes=mixed,
                carrier_single_flips=sens)
            break
        if 'witness' in row:
            break
    row.update(upper_choices_tried=attempts,seconds=perf_counter()-begin)
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target',choices=['grown','closed'])
    parser.add_argument('--pattern',choices=['four','pairs'],default='four')
    parser.add_argument('--limit',type=int,required=True)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    source=json.loads((RESEARCH/'FORBID-EDITS-20261126-001'/'starts.json').read_text())
    tests=[]
    if args.target == 'closed':
        for i,line in enumerate((HERE.parent/'out'/'cubic_10.jsonl').open()):
            record=json.loads(line)
            knots=tuple(tuple(i for i,e in enumerate(record['links']) if k in e) for k in range(10))
            tests.append((i+1,0,knots,10))
    else:
        stages=[]
        for path in sorted((HERE.parent/'out').glob('census_*')):
            for line in path.open():
                row=json.loads(line)
                for rr in row['rounds'][1:]:
                    if 12<=rr['distinctions']<=15 and rr['bonds']>=8:
                        stages.append((-rr['bonds'],int(row['start'].split()[1]),rr['round']))
        for _,i,r in sorted(stages)[:args.limit]:
            knots=supports_of(source[i])
            k=len(knots)
            for _ in range(r):
                step=advance(knots)
                assert step.status=='funded'
                knots=step.supports
            tests.append((i,r,knots,k))
    rows=[]
    for i,r,s,k in tests[:args.limit]:
        row=inspect(s,k,args.target=='grown',args.pattern)
        row.update(archive_number=i,round=r)
        rows.append(row)
        print(i,r,row['single_clauses_missing_111'],row['upper_choices_tried'],bool(row.get('witness')),round(row['seconds'],3),flush=True)
        if row.get('witness'):
            break
    if not args.pilot:
        (HERE/f'upper_{args.pattern}_{args.target}.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':
    main()
