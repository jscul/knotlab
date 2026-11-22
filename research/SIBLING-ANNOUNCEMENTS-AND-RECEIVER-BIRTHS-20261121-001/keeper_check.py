"""Rebuild which inputs the receivers pay and infer the old bit from their complete words."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import prod
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0,str(ROOT/"experiments"/ORIGINAL/(ORIGINAL+"-E001_ordinary")))
import end_operator


def trace(width, law):
    end = end_operator.from_stars([set(range(width))])
    turns = []
    for _ in range(5):
        t = end_operator.step(end,law)
        if t.status != "extend":
            break
        turns.append(t)
        end = t.end
    assert turns[0].parents == ((0,),)*width
    assert turns[0].fresh == (width-1,)*width
    assert set(turns[1].parents) == set(combinations(range(width),2))
    return turns


def mixed(row):
    return 0 in row and 1 in row


def source_completions(x):
    return [word for word in product(range(2),repeat=4)
            if mixed(word) and all(mixed((word[i],)+x[i]) for i in range(4))]


def inputs(edges, x):
    # Choose actual names by their receiving edge. The choice of a coherent renaming is free.
    return [(x[i][j-(j>i)],x[j][i]) for i,j in edges]


def count_word_guess(edges, fresh):
    """Price both an old-balanced preparation and uniform complete new words."""
    counters = defaultdict(Counter)
    selected = [(0,1),(1,2)]
    labels = tuple(product(range(2),repeat=3))
    outputs = tuple(product(range(2),repeat=fresh))
    scale = (2**fresh-1)*2**fresh
    for x in product(labels,repeat=4):
        old = Counter(word[0] for word in source_completions(x))
        payments = inputs(edges,x)
        choices = [[y for y in outputs if mixed(pair+y)] for pair in payments]
        counts = list(map(len,choices))
        all_extensions = prod(counts)
        for which in selected:
            j = edges.index(which)
            for orient, sources in old.items():
                for y in choices[j]:
                    records = {"full":payments[j]+y,"paid":payments[j],"fresh":y,"one":y[:1]}
                    for observation, key in records.items():
                        counters[which,"complete",observation][key,orient] += sources*(all_extensions//counts[j])
                        counters[which,"old",observation][key,orient] += sources*(scale//counts[j])
    for (which,mode,read),cnt in counters.items():
        keys={key for key,o in cnt}
        assert all(min(cnt[key,0],cnt[key,1])>0 for key in keys)
        good=sum(max(cnt[key,0],cnt[key,1]) for key in keys)
        total=sum(cnt.values())
        if mode=="old": assert total==scale*33614
        yield which,mode,read,Fraction(good,total),total if mode=="complete" else total//scale


def test_two_paid_children(edges):
    # Opposite inputs on every unobserved pair allow any future fresh values there.
    # Seek a mixed triple at every first child, for every assignment to the reported inputs.
    counted=0
    for size in (0,1,2):
        for bank in combinations(edges,size):
            unknown=[edge for edge in edges if edge not in bank]
            for observed in product(product(range(2),repeat=2),repeat=size):
                fixed=dict(zip(bank,observed))
                for bits in product(range(2),repeat=len(unknown)):
                    paid=fixed | {edge:(bit,1-bit) for edge,bit in zip(unknown,bits)}
                    rows=[[] for _ in range(4)]
                    for (i,j),(a,b) in paid.items():
                        rows[i].append(a)
                        rows[j].append(b)
                    if all(mixed(row) for row in rows):
                        break
                else:
                    raise AssertionError((bank,observed))
                counted+=1
    assert counted==265
    return counted


def test_focal_word(edges):
    # Orient the three nonfocal payments as a cycle, so each sibling gets both bits.
    checked=0
    for row in product(range(2),repeat=3):
        for old in product(range(2),repeat=4):
            if not mixed(old) or not mixed((old[0],)+row):
                continue
            paid={(0,i):(row[i-1],1-row[i-1]) for i in (1,2,3)}
            paid.update({(1,2):(0,1),(2,3):(0,1),(1,3):(1,0)})
            out=[[d] for d in old]
            for edge in edges:
                i,j=edge; a,b=paid[edge]
                assert a != b
                out[i].append(a)
                out[j].append(b)
            assert all(mixed(w) for w in out)
            checked+=1
    assert checked==98
    return checked


def test_sibling_bank(edges):
    # This actual third-cut child has parents 12, 13 and 23. Even hand it their six prior inputs.
    sib=[p for p in edges if 0 not in p]
    counted=0
    for old in product(range(2),repeat=4):
        if not mixed(old):
            continue
        for known in product(product(range(2),repeat=2),repeat=3):
            witness=dict(zip(sib,known))
            for j in (1,2,3):
                witness[0,j]=(old[j],1-old[j])
            words=[[v] for v in old]
            for (i,j),(a,b) in witness.items():
                words[i].append(a)
                words[j].append(b)
            assert all(mixed(w) for w in words)
            assert all(a!=b for edge,(a,b) in witness.items() if 0 in edge)
            counted+=1
    assert counted==896
    return counted


def parity_ports():
    # On this source an ordinary first-child word determines its spent input by parity.
    old = [w for w in product(range(2),repeat=6) if sum(w)%2==0]
    def spent(w):
        return tuple(w[2*k]^w[2*k+1] for k in range(3))
    def emitted(w):
        return (w[0]^w[2],w[1]^w[4],w[3]^w[5])
    fibers=defaultdict(list)
    for w in old:
        fibers[emitted(w)].append(w)
    assert len(old)==32 and len(fibers)==4
    assert all(len(words)==8 and all(len(set(bits))==2 for bits in zip(*words)) for words in fibers.values())
    for i,j in product((0,1),(2,3)):
        pairs=[]
        for w in old:
            v=list(w);v[i]^=1;v[j]^=1
            pairs.append((spent(w),spent(v)))
        assert sum(a==b for a,b in pairs)==0
        scores=[]
        for tag in product(range(2),repeat=3):
            score=sum((-1)**sum(t*(x^y) for t,x,y in zip(tag,a,b)) for a,b in pairs)
            scores.append(Fraction(score,len(old)))
        assert scores[0]==1 and Counter(scores)=={1:4,-1:4}
    print("Parity: 32 equally frequent first words, eight equally weighted character ports, four of each sign.")
    print("Every later parity word has eight first-word completions. Each original bit is free within each.")


def main():
    for width in (3,4):
        for law in ("parity","nae"):
            turns=trace(width,law)
            print("physical cuts",width,law,[(len(t.parents),tuple(sorted(set(t.fresh)))) for t in turns])
    t=trace(4,"nae"); edges=list(t[1].parents)
    assert t[1].fresh==(2,)*6
    sibling_group=tuple(k for k,p in enumerate(edges) if 0 not in p)
    idx=t[2].parents.index(sibling_group)
    assert t[2].fresh[idx]==1 and idx in t[3].parents[0]
    print("sibling-only recipient",sibling_group,"fresh grant",t[2].fresh[idx])
    print("universally compatible old payment patterns",test_two_paid_children(edges))
    print("compatible full original and focal words",test_focal_word(edges))
    print("old words compatible with every six-input sibling bank",test_sibling_bank(edges))
    parity_ports()
    for grant in (1,2):
        for which,mode,read,acc,den in count_word_guess(edges,grant):
            if mode=="old" and read=="full" and which==(0,1):
                assert acc==Fraction(4,7)
            if mode=="old" and read=="one" and which==(0,1):
                assert acc==Fraction(25 if grant==2 else 26,49)
            if mode=="complete":
                assert den=={1:385504,2:61954240}[grant]
            print("pair",which,"fresh grant",grant,mode,read,"best guess",acc,"words",den)


if __name__ == "__main__":
    main()
