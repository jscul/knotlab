"""Check complete common-prefix assignments for every payment allocation.

All continuations in one arm share the same named old variables. New values in
different continuations may satisfy their own newborn constraints independently.
"""
from itertools import permutations, product
import json
from pysat.solvers import Minisat22

from by_deletion import ARCHIVE, HERE, build


def clauses(rows, law):
    for row in rows:
        if law == "nae":
            yield list(row)
            yield [-v for v in row]
        else:
            for bits in product((0, 1), repeat=len(row)):
                if sum(bits) % 2:
                    yield [-v if value else v for v, value in zip(row, bits, strict=True)]


def support(source, law, extra):
    record, levels = build(source, extra)
    h = record["first_common"]
    bank = h["fresh"]
    prefix = [*source, *(r["inputs"] + r["fresh"] for level in levels[:-1] for r in level)]
    top = max(d for row in prefix for d in row)
    # Prefix names are 0-based audit names. Every SAT literal is one-based.
    prefix_rows = [[1+d for d in row] for row in prefix]
    final = levels[-1]
    fresh_count = sum(len(r["fresh"]) for r in final)
    children = record["next_common"]
    routes = []
    encoded = list(clauses(prefix_rows, law))
    for j, order in enumerate(permutations(bank)):
        allocation = {r["knot"]: d for r,d in zip(children,order,strict=True)}
        paid = {d: k for k,d in allocation.items()}
        assert len(paid) == len(bank)
        routes.append(paid)
        for r in final:
            ins = r["inputs"].copy()
            if r["knot"] in allocation:
                ins[r["parents"].index(h["knot"])] = allocation[r["knot"]]
            new = [d + j*fresh_count for d in r["fresh"]]
            assert min(new) > top
            encoded.extend(clauses([[1+d for d in ins+new]],law))
    all_words = {}
    with Minisat22(bootstrap_with=encoded) as solver:
        for word in product((0,1),repeat=len(bank)):
            assumptions = [(1+d) * (1 if v else -1) for d,v in zip(bank,word,strict=True)]
            assert solver.solve(assumptions=assumptions)
            truth = {abs(lit):int(lit>0) for lit in solver.get_model()}
            assert all(any((truth[abs(lit)] == int(lit>0)) for lit in row) for row in encoded)
            key = ''.join(map(str,word))
            all_words[key] = ''.join(str(truth[d+1]) for d in range(top+1))
    return {"common_prefix_by_H_fresh_word":all_words,"last_prefix_id":top,
            "allocation_routes_from_each_H_distinction":routes,
            "full_funded_opportunities":len(final),"continuing_pure_members":record["pure_next"]}


if __name__ == "__main__":
    old = json.loads(ARCHIVE.read_text())["both_laws"]
    result = {law:{arm:support(source,law,bool(i)) for i,(arm,source) in
                   enumerate(zip(("base","extra"),entry["near_right_spare"]["sources"],strict=True))}
              for law,entry in old.items()}
    (HERE/"same_prefix.json").write_text(json.dumps(result,indent=2)+'\n')
    for law,arms in result.items():
        print(law, [(name,len(arm["common_prefix_by_H_fresh_word"]),
                     len(arm["allocation_routes_from_each_H_distinction"])) for name,arm in arms.items()])
