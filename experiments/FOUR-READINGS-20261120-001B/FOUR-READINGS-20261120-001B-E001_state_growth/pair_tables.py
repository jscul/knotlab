"""Named paired fixtures, exact disagreements, signed changes and replay."""
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

from model import (accepts, add, allowed, bits, build, growth, literal_counts, mask_of,
                   nae_counts, nae_separator, parity_bonds, parity_counts, width)

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def archive_switch():
    s,u,v,w,f,a,z,out = range(8)
    common = [(s,u),(s,v),*[(u,out)]*3,*[(v,out)]*3,*[(s,a)]*2,*[(a,z)]*2,*[(z,out)]*2]
    left = common + [(s,w)]*4 + [(w,out)]*3 + [(s,f)]*3 + [(f,out)]*4
    right = common + [(w,out)]*4 + [(s,w)]*3 + [(f,out)]*3 + [(s,f)]*4
    def original(endpoints):
        return tuple(tuple(i for i, pair in enumerate(endpoints) if h in pair) for h in range(out))
    return original(left), original(right), (u,), (w,f)


def seven():
    u,v,s,w,a,b,z = range(7)
    meetings = [(u,s),(v,s),(s,a),(a,z),(s,w),(w,b),(b,a)]
    left = build([p for p in meetings for _ in range(9)], [2,2,0,0,0,0,4])
    packet = left[z][-2:]
    right = tuple((*row,*packet) if h==w else row[:-2] if h==z else row
                  for h,row in enumerate(left))
    return left, right, (u,v), (w,z)


def loose_path(d):
    meetings = [(h,d+i+1) for i in range(d)
                for h in (i,i+1,i+1)]
    left = build(meetings, [2]*d+[1]+[0]*d)
    return left, add(left,{d}), (0,), (d,)


def structural(length, fixed_width):
    names = ['r','a','b','x','y']+['r'+str(i) for i in range(1,length+1)]
    tail = ['r', *names[5:]]
    pairs = [('r','a'),('r','b'),('a','b'),('a','x'),('a','y'),('b','x'),('b','y')]
    joins = []
    for u,v in pairs+list(zip(tail,tail[1:])):
        middle = 'w_'+u+'_'+v
        names.append(middle)
        joins.extend([(u,middle)]*2+[(v,middle)]*2)
    names.append('switch')
    joins.extend([('switch','x')]*2+[('switch','w_a_x')]*2)
    ids = {name:i for i,name in enumerate(names)}
    count = {'a':3,'b':3,'x':1,'y':1,'w_r_a':2,**dict.fromkeys(tail,2)}
    rows = build([(ids[u],ids[v]) for u,v in joins], [count.get(name,0) for name in names])
    left = add(rows,{ids['y']}) if fixed_width else rows
    right = add(rows,{ids['y'],ids['switch']})
    return left, right, (ids[tail[-1]],), (ids['x'],ids['y'])


def physical(control):
    rows = build([(i,(i+1)%6) for i in range(6)],[3]*6)
    shared, = set(rows[0]) & set(rows[5])
    cut = tuple(tuple(x for x in r if not(i==0 and x==shared)) for i,r in enumerate(rows))
    plus = add(rows,{5})
    if control == 'cut':
        return rows, cut, (1,), (0,5)
    if control == 'extra':
        return rows, plus, (1,), (5,)
    return cut, plus, (1,), (0,5)


def difference(left,right,receivers,senders):
    n0,n1 = width(left),width(right)
    m = min(n0,n1)
    assert all(tuple(left[i]) == tuple(right[i]) for i in receivers)
    receiver = set().union(*(left[i] for i in receivers)) & set(range(m))
    sender = set().union(*(left[i] for i in senders), *(right[i] for i in senders)) & set(range(m))
    measures = {}
    for law,reader in [('parity',parity_counts),('nae',nae_counts)]:
        n,d = reader(left)
        v,e = reader(right)
        groups = {k: [] for k in ['receiver_receiver','receiver_sender','receiver_other','other_other']}
        for ij in combinations(range(m),2):
            a,b = ij
            if a in receiver and b in receiver:
                group = 'receiver_receiver'
            elif (a in receiver and b in sender) or (b in receiver and a in sender):
                group = 'receiver_sender'
            elif a in receiver or b in receiver:
                group = 'receiver_other'
            else:
                group = 'other_other'
            groups[group].append(ij)

        def score(pairs, rate):
            def delta(ij):
                return (Fraction(e[ij],v)-Fraction(d[ij],n)) if rate else e[ij]-d[ij]
            changes = {ij: delta(ij) for ij in pairs if delta(ij)}
            if not changes:
                return {'changed':0, 'max_abs':'0', 'min_nonzero_abs':None}
            largest = max(abs(x) for x in changes.values())
            example = next(ij for ij,val in changes.items() if abs(val)==largest)
            return {'changed':len(changes),'min_nonzero_abs':str(min(abs(x) for x in changes.values())),
                    'max_abs':str(largest),'example_pair':example,'example_raw':[d[example],e[example]],
                    'example_rate':[str(Fraction(d[example],n)),str(Fraction(e[example],v))],
                    'example_signed_delta':str(changes[example])}

        measures[law] = {'solutions':[n,v],
            'classes':{k:{'denominator':len(pairs),'raw':score(pairs,False),'rate':score(pairs,True)}
                       for k,pairs in groups.items()},
            'D_lexicographic':[list(d.values()),list(e.values())]}
    return {'widths':[n0,n1],'rows':[left,right],'receivers':receivers,'senders':senders,
            'receiver_marks':sorted(receiver),'sender_common_marks':sorted(sender),
            'new_or_removed_pairs': [size*(size-1)//2-m*(m-1)//2 for size in (n0,n1)],
            'tables':measures}


def parity_separator(rows, other):
    n = width(rows)
    base = list(map(mask_of, rows))
    for j,target in enumerate(other):
        # Solve dot(source,s)=0 and dot(target,s)=1 by ordinary elimination.
        equations = [(x,0) for x in base] + [(mask_of(target),1)]
        basis = {}
        for x,b in equations:
            for col in sorted(basis, reverse=True):
                if x & 1<<col:
                    u,v = basis[col]
                    x,b = x^u,b^v
            if x:
                basis[x.bit_length()-1] = (x,b)
            elif b:
                break
        else:
            word = 0
            for col in sorted(basis):
                row,b = basis[col]
                if (row & word).bit_count()%2 != b:
                    word |= 1 << col
            assert accepts(rows,word,'parity') and not accepts(other,word,'parity')
            return {'violated_holder':j,'ones':list(bits(word))}
    return None


def both_pair_details(record, left, right, mark):
    for law,separator in [('nae',nae_separator),('parity',parity_separator)]:
        record['tables'][law]['separating_words'] = [separator(left,right),separator(right,left)]
        detail = []
        for arm in (left,right):
            status,births = growth(arm,law)
            assert status == 'births'
            match, = [f for p,f in births if p==mark]
            detail.append({'parents':mark,'fresh':match,'births':[[p,f] for p,f in births]})
        record['tables'][law]['marked_births'] = detail


def main():
    controls = [((0,1,2),), ((0,1,2),(0,1,2)),
                ((0,1,2),(0,3,4),(1,5,6),(2,7,8)), build([(0,1)]*2+[ (1,2)], [1,1,2])]
    for rows in controls:
        for law,count in [('nae',nae_counts),('parity',parity_counts)]:
            assert count(rows)==literal_counts(allowed(rows,law),width(rows))
    book = {}
    for label,source,mark in [('same_bonds',archive_switch,(1,3)),('seven_knots',seven,(0,1))]:
        a,b,r,s = source()
        result = difference(a,b,r,s)
        both_pair_details(result,a,b,mark)
        bonds_left,bonds_right = parity_bonds(a),parity_bonds(b)
        result['parity_bonds'] = [len(bonds_left),len(bonds_right),len(bonds_left^bonds_right)]
        book[label] = result
    assert book['same_bonds']['parity_bonds']==[55,55,0]
    assert [r['fresh'] for r in book['same_bonds']['tables']['parity']['marked_births']]==[2,3]
    assert [r['fresh'] for r in book['seven_knots']['tables']['nae']['marked_births']]==[2,1]
    for d in [2,3,5,8]:
        book['loose_path_'+str(d)] = difference(*loose_path(d))
    for length in [0,1]:
        for fixed, name in [(False,'add'),(True,'fixed')]:
            book[f'witness_{name}_{length+2}'] = difference(*structural(length,fixed))
    for name in ['cut','extra','cut_vs_extra']:
        book['cycle_'+name] = difference(*physical(name))
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'pair_tables.json').write_text(json.dumps(book,separators=(',',':'))+'\n')
    print('exact paired preparations:',len(book))


if __name__=='__main__':
    main()
