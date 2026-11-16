"""Exact direct-fact library optimum for the fixed even-input split tree."""
from itertools import combinations
from math import comb


def search():
    # A dual of odd weight detects failure to span (1,1,1).
    obligations = [(y,d) for y in range(8) for d in (1,2,4,7)]
    candidates = []
    for support in range(1,8):
        for setting in range(8):
            if setting & ~support:
                continue
            coverage = sum(1 << j for j,(y,d) in enumerate(obligations)
                           if y & support == setting and (support & d).bit_count()%2)
            candidates.append((support,setting,coverage))
    target = (1 << len(obligations))-1
    certificate = {}
    min_citations = 100
    for size in range(7):
        eligible = 0
        for chosen in combinations(candidates,size):
            covered = 0
            for _,_,bitset in chosen:
                covered |= bitset
            if covered != target:
                continue
            eligible += 1
            length = 0
            for y in range(8):
                avail = {support for support,setting,_ in chosen if y & support == setting}
                if 7 in avail:
                    length += 1
                elif any((7 ^ u) in avail for u in avail):
                    length += 2
                else:
                    length += 3
            min_citations = min(min_citations,length)
        certificate[str(size)] = {"subsets":comb(26,size),"spanning_libraries":eligible}
    if len(candidates)!=26 or any(certificate[str(k)]["spanning_libraries"] for k in range(6)):
        raise AssertionError("unexpected smaller full-case direct-fact library")
    if not certificate["6"]["spanning_libraries"]:
        raise AssertionError("no six-fact witness")
    return {"candidate_maximal_guards":26,"tested_sizes":certificate,
            "minimum_rich_facts":6,"minimum_rich_citations_among_size_six":min_citations}


if __name__ == "__main__":
    import json
    print(json.dumps(search(),sort_keys=True))
