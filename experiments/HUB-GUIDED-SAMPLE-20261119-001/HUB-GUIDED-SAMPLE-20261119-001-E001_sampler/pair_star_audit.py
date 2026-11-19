"""Exhaustive small literal checks for the pair-star maximal-set identity."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import pair_star


def names(mask):
    while mask:
        bit = mask & -mask
        mask ^= bit
        yield bit.bit_length()-1


def bits(items):
    return sum(1 << u for u in items)


def literal_graph(h, edges, support):
    """Build the literal simple graph, before any projection or completion."""
    n = h+len(edges)
    rows = [0]*n
    high = set(range(h))
    for u,v in combinations(range(n),2):
        if v in high:
            adjacent = True
        elif u in high:
            adjacent = bool(support[v-h] & (1 << u))
        else:
            adjacent = any(p in edges[v-h] for p in edges[u-h])
        if adjacent:
            rows[u] |= 1 << v
            rows[v] |= 1 << u
    return rows


def literal_maxima(rows, universe):
    maximal = set()
    selected = universe
    while selected:
        allowed = universe ^ selected
        for u in names(selected):
            if selected & ~(rows[u] | (1 << u)):
                break
            allowed &= rows[u]
        else:
            if not allowed:
                maximal.add(selected)
        selected = (selected-1) & universe
    return maximal


def observed_terms(k, h, edges, support):
    """Classify separately enumerated local and global literal maximal sets."""
    high = (1 << h)-1
    rows = literal_graph(h,edges,support)
    true_global = literal_maxima(rows,(1 << len(rows))-1)
    stars = [[j for j,edge in enumerate(edges) if v in edge] for v in range(k)]
    local = [literal_maxima(rows, high | bits(h+j for j in star)) for star in stars]
    assert all(pair_star.intersection_count({support[j] for j in star},high) == len(groups)
               for star,groups in zip(stars,local,strict=True))
    occurrences = Counter(g for one in local for g in one)
    star_union = occurrences.keys()
    missed = true_global - star_union
    bad = star_union - true_global

    def low_size(group):
        return (group >> h).bit_count()

    assert all(low_size(g) == 3 for g in missed)
    assert all(low_size(g) <= 2 for g in bad)
    assert all(occurrences[g] == 1 for g in star_union if low_size(g) >= 2)
    assert all(occurrences[g] == 2 for g in true_global & star_union if low_size(g) == 1)
    assert all(occurrences[g] == 1 for g in bad if low_size(g) == 1)
    measured = {"sum_local_maxima":sum(map(len,local)), "local_zero":occurrences[high],
                "global_zero":int(high in true_global),
                "singleton_deduction":sum(1 for g in star_union if low_size(g) == 1),
                "extendible_two_member_corners":sum(low_size(g) == 2 for g in bad),
                "three_distinct_pairs":len(missed), "maximal_groups":len(true_global)}

    # Independently evaluate the support conditions used in the producer's correction.
    def via(v, target):
        return sum(support[i] & target == target for i in stars[v])

    triangles = []
    positions = {edge:i for i,edge in enumerate(edges)}
    for u,v,w in combinations(range(k),3):
        if all(e in positions for e in ((u,v),(u,w),(v,w))):
            triangles.append((u,v,w))
    corners = 0
    for t in triangles:
        for middle in t:
            u,v = [a for a in t if a != middle]
            p = positions[tuple(sorted((middle,u)))]
            q = positions[tuple(sorted((middle,v)))]
            opposite = positions[u,v]
            target = support[p] & support[q]
            corners += (support[opposite] & target == target and via(middle,target) == 2)
    corrections = {"local_zero":sum(via(v,high) == 0 for v in range(k)),
                   "global_zero":int(all(v != high for v in support)),
                   "singleton_deduction":sum(via(u,support[j]) == 1 or via(v,support[j]) == 1
                                             for j,(u,v) in enumerate(edges)),
                   "extendible_two_member_corners":corners, "three_distinct_pairs":len(triangles)}
    assert all(measured[key] == value for key,value in corrections.items()), (k,h,edges,support,measured,corrections)
    assert arithmetic(measured) == measured["maximal_groups"]
    return measured


def arithmetic(d):
    return (d["sum_local_maxima"]-d["local_zero"]+d["global_zero"]-d["singleton_deduction"]
            -d["extendible_two_member_corners"]+d["three_distinct_pairs"])


def arbitrary_supports(k, h):
    possible = list(combinations(range(k),2))
    exercised = Counter()
    first_witness = {}
    cases = 0
    for assignment in product(range(-1,1 << h),repeat=len(possible)):
        edges = [edge for edge, value in zip(possible,assignment,strict=True) if value >= 0]
        support = [value for value in assignment if value >= 0]
        terms = observed_terms(k,h,edges,support)
        cases += 1
        for field in ("local_zero","global_zero","singleton_deduction","extendible_two_member_corners","three_distinct_pairs"):
            if terms[field]:
                exercised[field] += 1
                if field not in first_witness:
                    mutated = arithmetic(terms | {field:0})
                    assert mutated != terms["maximal_groups"]
                    first_witness[field] = {"edges":edges,"high_support_masks":support,"maxima":terms["maximal_groups"],
                                            "nonzero_term":terms[field],"wrong_answer_when_omitted":mutated}
    assert cases == ((1 << h)+1)**len(possible)
    return {"block_names":k,"high_names":h,"assignment_count":cases,
            "nonzero_term_coverage":dict(exercised),"wrong_term_mutations_detected":first_witness}


class InMemoryStage:
    def __init__(self, memberships, k):
        self.at = memberships
        self.n = len(memberships)
        self.blocks = [bits(u for u,m in enumerate(memberships) if b in m) for b in range(k)]

    def hood(self, signature):
        group = 0
        for b in signature:
            group |= self.blocks[b]
        return group


def incidence_controls(tmp):
    literal_files = []
    counted = Counter()
    for k in (3,4):
        possible = tuple(combinations(range(k),2))
        highs = [b for size in range(3,k+1) for b in combinations(range(k),size)]
        for h in (1,2,3):
            for memberships in product(highs,repeat=h):
                for low_mask in range(1 << len(possible)):
                    lows = [possible[e] for e in names(low_mask)]
                    support = [bits(i for i,s in enumerate(memberships) if any(p in s for p in edge)) for edge in lows]
                    literal = observed_terms(k,h,lows,support)
                    fixture = InMemoryStage(list(memberships)+lows,k)
                    with patch.object(pair_star,"Stage",lambda _name:fixture):
                        measured = pair_star.solve(None)
                    assert all(measured[key] == value for key,value in literal.items())
                    counted[k,h] += 1
                    if (len(literal_files) < 12 and all(b.bit_count() >= 2 for b in fixture.blocks) and
                        all(a & b not in {a,b} for a,b in combinations(fixture.blocks,2))):
                        literal_files.append((fixture,literal))
    for i,(fixture,literal) in enumerate(literal_files):
        file = tmp/f"pair-star-audit-{i}.txt"
        file.write_text(f"{fixture.n} {len(fixture.blocks)}\n" + "".join(" ".join(map(str,names(b)))+"\n" for b in fixture.blocks))
        measured = pair_star.solve(file)
        assert all(measured[key] == value for key,value in literal.items())
    return {"labelled_block_incidence_cases": [[k,h,count] for (k,h),count in sorted(counted.items())],
            "actual_text_parser_fixtures":len(literal_files)}


def archived_check(source):
    record = json.loads(source.read_text())
    assert record["live"] == record["high_junctions"]+record["pair_junctions"]
    assert sum(record["local_maxima_hist"].values()) == record["blocks"]
    assert sum(int(value)*frequency for value,frequency in record["local_maxima_hist"].items()) == record["sum_local_maxima"]
    assert arithmetic(record) == record["maximal_groups"] == 251282
    return {"archived_result_sha256":sha256(source.read_bytes()).hexdigest(),"reconciled_raw_count":record["maximal_groups"],
            "scope":"arithmetic cross-check only; no duplicate global enumeration or birth correction"}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("archived",type=Path)
    cli.add_argument("output",type=Path)
    args = cli.parse_args()
    with tempfile.TemporaryDirectory(prefix="pair-star-audit-") as folder:
        applied = incidence_controls(Path(folder))
    result = {"arbitrary_high_support": [arbitrary_supports(k,h) for k,h in [(3,3),(4,2),(5,1)]],
              "unchanged_producer":applied,"archived_output":archived_check(args.archived)}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
