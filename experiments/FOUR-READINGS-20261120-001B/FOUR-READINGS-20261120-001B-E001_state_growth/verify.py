"""Positive integer reference counts by assigning physical distinctions directly."""
from fractions import Fraction
from itertools import combinations, product
import json

from model import ownership, parity_local, width
from pair_tables import OUT


class PhysicalCounter:
    """Process interchangeable distinctions together, retaining seen values at each holder."""

    def __init__(self, rows):
        self.rows = rows
        self.owner = {x:tuple(h) for x,h in ownership(rows).items()}
        self.marks = {}
        for x,h in self.owner.items():
            self.marks.setdefault(h,[]).append(x)
        remaining = set(self.marks)
        started = set()
        self.order = []
        while remaining:
            def cost(bundle):
                after = started.union(bundle)
                unfinished = {h for b in remaining-{bundle} for h in b}
                return len(after & unfinished),len(set(bundle)-started),bundle
            bundle = min(remaining,key=cost)
            started.update(bundle)
            remaining.remove(bundle)
            unfinished = {h for b in remaining for h in b}
            finished = set(bundle)-unfinished
            seen0 = sum(1<<(2*h) for h in bundle)
            done = sum(3<<(2*h) for h in finished)
            self.order.append((bundle,seen0,done))

    def count(self, pinned=None):
        pinned = pinned or {}
        values = {0:1}
        for bundle,seen0,done in self.order:
            marks = self.marks[bundle]
            held = [pinned[x] for x in marks if x in pinned]
            free = len(marks)-len(held)
            all0 = int(1 not in held)
            all1 = int(0 not in held)
            ways = ((seen0,all0), (seen0<<1,all1), (3*seen0,(1<<free)-all0-all1))
            next_values = {}
            for past,old in values.items():
                for seen,number in ways:
                    complete = seen|past
                    if number and complete & done == done:
                        key = complete & ~done
                        next_values[key] = next_values.get(key,0)+number*old
            values = next_values
        return values.get(0,0)

    def lawful(self):
        # Each local word is represented by its all-zero, all-one or mixed
        # pattern in each class of positions with the same other holder.
        count = 0
        for holder,row in enumerate(self.rows):
            groups = [part for b,part in self.marks.items() if holder in b]
            for types in product(*(range(2+(len(part)>1)) for part in groups)):
                if len(set(types))==1 and types[0] != 2:
                    continue
                pins = {}
                for part,t in zip(groups,types):
                    for k,x in enumerate(part):
                        pins[x] = int(k>0) if t==2 else t
                assert self.count(pins)>0
                count += 1
        return count


def verify_arm(rows,expected_total,expected_d,check_local):
    dp = PhysicalCounter(rows)
    assert dp.count()==expected_total
    cached = {}
    for (a,b),expected in zip(combinations(range(width(rows)),2),expected_d,strict=True):
        pair_type = tuple(sorted((dp.owner[a],dp.owner[b])))
        if pair_type not in cached:
            cached[pair_type] = 2*dp.count({a:0,b:1})
        assert cached[pair_type] == expected
    assert all(x==1 for x in parity_local(rows))
    return {'checked_pairs':len(expected_d),'separate_pair_types':len(cached),
            'local_nonconstant_types_checked':dp.lawful() if check_local else None}


def main():
    book = json.loads((OUT/'pair_tables.json').read_text())
    checks = {}
    for key,r in book.items():
        z = r['tables']['nae']
        checks[key] = [verify_arm(row,n,d,key in ('same_bonds','seven_knots')) for row,n,d
                       in zip(r['rows'],z['solutions'],z['D_lexicographic'],strict=True)]
        if key.startswith('loose_path'):
            d = int(key.split('_')[-1])
            a,b = z['solutions']
            assert (a,b)==(30*23**(d-1),66*23**(d-1))
            c = z['classes']
            assert c['receiver_receiver']['rate']['changed']==0
            assert c['receiver_other']['rate']['changed']==0
            assert c['receiver_sender']['rate']['changed']==9
            assert Fraction(c['receiver_sender']['rate']['max_abs']) == Fraction(3,55*23**(d-1))
    # A pinned, monochromatic seed star removes an actually allowed mark pattern.
    dp = PhysicalCounter(((0,1,2),))
    assert dp.count({0:0,1:0,2:0})==0 and dp.count({0:0,1:1,2:0})==1
    result = {'positive_physical_counts':checks,'mutant_local_word_rejected':True,
              'verified_common_table_cells_sum_over_arms':sum(v['checked_pairs'] for vv in checks.values() for v in vv)}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['verified_common_table_cells_sum_over_arms'])


if __name__=='__main__':
    main()
