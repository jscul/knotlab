"""Independent checks on the true-parent incidence used in the clock proofs."""
from collections import Counter
from itertools import combinations, product
import json


def distances(sets):
    n=len(sets)
    table=[[None]*n for _ in range(n)]
    for i in range(n):
        table[i][i]=0
        for j in range(i):
            if sets[i] & sets[j]:
                table[i][j]=table[j][i]=1
    for k in range(n):
        for i,j in product(range(n),repeat=2):
            if table[i][k] is None or table[k][j] is None:
                continue
            possible=table[i][k]+table[k][j]
            if table[i][j] is None or possible < table[i][j]:
                table[i][j]=possible
    return table


def audit_incidence():
    tables=pure_pairs=chosen_pairs=0
    rates=Counter()
    positive_examples={}
    for old,new in [(2,2),(3,3),(4,3),(3,4)]:
        for code in range(1 << (old*new)):
            parents=[{i for i in range(old) if code >> (j*old+i)&1} for j in range(new)]
            children=[{j for j in range(new) if i in parents[j]} for i in range(old)]
            if not all(parents) or not all(children):
                continue
            tables+=1
            before=distances(children)
            after=distances(parents)
            for x,y in combinations(range(new),2):
                parental=[before[i][j] for i,j in product(parents[x],parents[y]) if before[i][j] is not None]
                assert after[x][y] == (1+min(parental) if parental else None)
                if parents[x].isdisjoint(parents[y]) and parental:
                    pure_pairs+=1
            for i,j in combinations(range(old),2):
                if before[i][j] is None:
                    continue
                for x,y in product(children[i],children[j]):
                    diff=after[x][y] - before[i][j]
                    assert diff in (-1,0,1)
                    chosen_pairs+=1
                    rates[diff]+=1
                    if before[i][j]>0 and after[x][y]>0 and diff not in positive_examples:
                        positive_examples[diff]=dict(parents=[sorted(pool) for pool in parents],
                                                      old_pair=[i,j],new_pair=[x,y],
                                                      distances=[before[i][j],after[x][y]])
    return {"incidences_checked":tables,"all_parent_disjoint_pairs":pure_pairs,
            "chosen_parent_child_pairs":chosen_pairs,"change_counts":dict(rates),
            "examples_with_positive_separation":positive_examples}


def audit_offsets():
    examples={}
    for s in (4,8,12):
        p=2*s
        ticks=lambda t: max(0,(t+1)//p-1)
        for age_shift in (1,p,p+1):
            observed={ticks(t)-ticks(t-age_shift) for t in range(4*p+age_shift,8*p+age_shift)}
            quotient,rem=divmod(age_shift,p)
            assert observed==({quotient,quotient+1} if rem else {quotient})
            examples[f'{p}-step clock, origin shift {age_shift}']=sorted(observed)
    return examples


def audit_receiving_windows():
    """Real return words of the 21-knot source, with b1 at position zero."""
    runs=[]
    for neutral_count in (1,2):
        block=('v','r1','r2','r3')*neutral_count+('v','s','b0','t')
        spacing=len(block)
        def letter(i,period=None):
            symbol=block[(i+spacing-2)%spacing]
            if symbol=='b0' and (i==0 if period is None else i%period==0):
                return 'b1'
            return symbol
        def center(size):
            return tuple(letter(i) for i in range(-(size//2),(size+1)//2))
        for size in range(2*spacing,12*spacing):
            member=center(size)
            child=center(size+1)
            assert (child[:-1]==member) != (child[1:]==member)
            assert child.count('b1')==1
        for index in range(1,9):
            period=spacing*(index+1)
            size=2*period
            receipt=center(size)+('b1',)
            sent=tuple(letter(i,period) for i in range(1-period,period+1))
            assert receipt[:-1]==center(size) and receipt[1:]==sent
            assert sent[:period]==sent[period:] and sent[:period].count('b1')==1
            assert receipt!=center(size+1) and sent.count('b1')==2
            assert all(receipt[i]!=receipt[i+2] for i in range(len(receipt)-2))
            runs.append({"source_spacing":spacing,"release_index":index,"send_order":size-1,
                         "receiver_child_order":size,"sent_parent_in_next_receiver_member":False})
    return runs


if __name__=='__main__':
    print(json.dumps({"incidence":audit_incidence(),"established_clock_formula":audit_offsets(),
                      "centered_receiver":audit_receiving_windows()},indent=2))
