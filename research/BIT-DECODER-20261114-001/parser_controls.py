"""Post-freeze diagnostic for ambiguity in the finite shared binary-parser grammar."""
from itertools import product
import json

import wirings


def binary(table, first, second, full):
    # Use truth-table position 2*first+second. All 16 functions are present.
    pos = first & second
    signs = ((~first & ~second) & full, (~first & second), (first & ~second), pos)
    out = 0
    for key, term in enumerate(signs):
        if (table >> key) & 1:
            out |= term
    return out


def candidates(training, tests, masks):
    width = len(masks)
    full = (1 << width) - 1
    raw_cols = [sum((n >> k & 1) << j for j, n in enumerate(masks)) for k in range(9)]
    def questions(items):
        out = {}
        for _,w,_ in items:
            columns = list(zip(*(wirings.truth(w,n) for n in masks)))
            for port,col in enumerate(columns):
                out[w[port]] = sum(x << i for i,x in enumerate(col))
        return tuple(out.items())

    seen,held=questions(training),questions(tests)
    clauses={row for q,_ in seen+held for row in q}
    accepted=[]
    for literal, row, ri in product(range(16),range(16),range(2)):
        pins={p:binary(literal,raw_cols[abs(p)-1],full*int(p<0),full) for p in range(-9,10) if p}
        terms={}
        for clause in clauses:
            val=full*ri
            for p in clause:
                val=binary(row,val,pins[p],full)
            terms[clause]=val
        def reconstruct(q,table,initial):
            val=full*initial
            for term in q:
                val=binary(table,val,terms[term],full)
            return val
        for question,qi in product(range(16),range(2)):
            if any(reconstruct(q,question,qi)!=truth for q,truth in seen):
                continue
            accepted.append((literal,row,question,ri,qi,all(reconstruct(q,question,qi)==truth for q,truth in held)))
    return {'grammar_size':16**3*4,'training_perfect_settings':len(accepted),
            'also_correct_on_named_held_panel_with_all_source_bits':sum(a[-1] for a in accepted),
            'mask_count':len(masks),'unique_training_ports':len(seen),'unique_held_ports':len(held)}


def run():
    train, held = wirings.training_panel(),wirings.held_panel()
    tests=[r for r in held if r[2]['family']=='exactly_one']
    masks=tuple(n for n in range(512) if n.bit_count()%2==0)
    return {name:candidates(rows,tests,masks) for name,rows in (
        ('any_only',[v for v in train if v[2]['family']=='any']),('varied',train))}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
