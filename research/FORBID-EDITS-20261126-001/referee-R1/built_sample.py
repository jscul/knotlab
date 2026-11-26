"""Count the two six-knot copies conditional on their one shared distinction."""
import argparse
import gzip
import json
import random
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
from time import perf_counter

from growth import grow

HERE = Path(__file__).resolve().parent
SEED = 2026112604


def value_masks(names):
    names = sorted(names)
    count = 1 << len(names)
    full = (1 << count)-1
    masks = {}
    for i, name in enumerate(names):
        run = 1 << i
        if run < 8:
            byte = sum(1 << j for j in range(8) if j & run)
            masks[name] = int.from_bytes(bytes([byte]) * (count//8), "little")
        else:
            period = bytes(run//8) + bytes([255]) * (run//8)
            masks[name] = int.from_bytes(period * (count//(2*run)), "little")
    return full, masks


def count_half(base, edited, births, link, mark, law):
    full, masks = value_masks(set().union(*edited))
    def passes(row):
        if law == "parity":
            odd = 0
            for b in row:
                odd ^= masks[b]
            return full ^ odd
        zeros = ones = full
        for b in row:
            zeros &= full ^ masks[b]
            ones &= masks[b]
        return full ^ (zeros | ones)

    kept = full
    for r in list(base) + list(edited):
        kept &= passes(r)
    survivors = kept
    zero_losses = []
    for b in births:
        if not b["f"]:
            legal = passes(b["inputs"])
            zero_losses.append((b["inputs"], (kept & (full ^ legal)).bit_count()))
            survivors &= legal
    classes = {1: survivors}
    for b in births:
        f = b["f"]
        if f == 0:
            continue
        if law == "parity":
            classes = {w * (1 << (f-1)): mask for w,mask in classes.items()}
        else:
            ok = passes(b["inputs"])
            next_classes = {}
            for w, mask in classes.items():
                for subset, ways in [(mask & ok, 1<<f), (mask & (full ^ ok), (1<<f)-1)]:
                    if subset:
                        wt = ways*w
                        next_classes[wt] = next_classes.get(wt,0) | subset
            classes = next_classes
    def hist(groups):
        return [[sum(w*(mask & (masks[link] if h else full^masks[link])
                              & (masks[mark] if v else full^masks[mark])).bit_count()
                     for w,mask in groups.items()) for v in (0,1)] for h in (0,1)]
    return {"old": hist({1:kept}), "S":hist({1:survivors}), "U":hist(classes)}, zero_losses


def evaluate(row):
    base = [tuple(s) for s in row["supports"]]
    n = len(base)//2
    rd = row["readers"]
    copies = [set().union(*base[:n]), set().union(*base[n:])]
    link, = copies[0] & copies[1]
    edit_start = 1 + max(copies[0] | copies[1])
    multiplicity = Counter(b for r in base for b in r)
    marks = [next(b for b in base[s[0]] if multiplicity[b] == 1) for s in rd]
    contexts = []
    e1 = row["kind of edit"] == "E1"
    for st in product(range(2), repeat=2):
        edited = list(base)
        for i,(setting, reader) in enumerate(zip(st,rd)):
            if setting or not e1:
                h = reader[0 if e1 else setting]
                edited[h] += (edit_start+i,)
        status, births = grow(edited, row["law"], row["arm"])
        key = "".join(map(str,st))
        assert status == row["status"][key]
        halves = [[],[]]
        for b in births:
            side = {p//n for p in b["parents"]}
            assert len(side) == 1, "cross-copy birth"
            halves[side.pop()].append(b)
        counts, added_counts, actual_zeros = [], [], []
        for i in range(2):
            sl = slice(i*n,(i+1)*n)
            hist, losses = count_half(base[sl],edited[sl],halves[i],link,marks[i],row["law"])
            counts.append(hist)
            if not e1:
                extra, _ = count_half(base[sl],edited[sl],halves[i],link,edit_start+i,row["law"])
                added_counts.append(extra)
            answer = {tuple(b["inputs"]) for b in halves[i] if any(p in rd[i] for p in b["parents"])
                      and not b["f"] and dict(losses)[b["inputs"]] > 0}
            actual_zeros.append(sorted(answer))
        def joined(w, sides=counts):
            return [[sum(sides[0][w][h][a]*sides[1][w][h][b] for h in (0,1))
                     for b in (0,1)] for a in (0,1)]
        def norm(t):
            return sum(map(sum,t))
        old, surviving = norm(joined("old")), norm(joined("S"))
        assert [surviving,old] == row["retained of old"][key]
        correlations = {}
        for w in ("S","U"):
            t = joined(w)
            correlations[w] = Fraction(t[0][0]+t[1][1]-t[0][1]-t[1][0],norm(t))
        added_correlations = {}
        for w in ("S","U") if not e1 else ():
            t = joined(w,added_counts)
            added_correlations[w] = Fraction(t[0][0]+t[1][1]-t[0][1]-t[1][0],norm(t))
        signatures = [tuple((b["parents"], b["inputs"], b["f"]) for b in half) for half in halves]
        # This checks sufficient conditions for every local value record to be unchanged.
        # Keep all the near side conditional on h. Check the far side's relative masses
        # for h=0,1 directly, since its total mass cancels in the normalization.
        far = [{w:Fraction(sum(c[w][1]),sum(map(sum,c[w]))) for w in ("S","U")} for c in counts]
        contexts.append((signatures,far,actual_zeros,correlations,added_correlations))
    compared = {}
    for w in ("U","S"):
        vals = [c[3][w] for c in contexts]
        assert list(map(str,vals)) == row[w]["correlations"]["fixed old value"]
        score = max(abs(sum(vals)-2*vi) for vi in vals)
        assert str(score) == row[w]["scores"]["fixed old value"]
        invariant = all(contexts[j][0][i] == contexts[j^(1<<i)][0][i] and
                        contexts[j][1][1-i][w] == contexts[j^(1<<i)][1][1-i][w]
                        for i in range(2) for j in range(4))
        if invariant:
            assert row[w]["record unchanged"]
        compared[w] = {"score":str(score),"correlations":list(map(str,vals)),
                       "proved full record unchanged":invariant}
        if not e1:
            extra = [c[4][w] for c in contexts]
            added_score = max(abs(sum(extra)-2*z) for z in extra)
            assert str(added_score) == row[w]["scores"]["added value"]
            compared[w]["added score"] = str(added_score)
    # Does an edit actually change an individually restrictive near zero-fresh birth?
    actual = [any(contexts[j][2][i] != contexts[j^(2>>i)][2][i] for j in range(4)) for i in range(2)]
    assert actual == row["forbidding changes with own setting"]
    return {"construction":row["built"],"edit":row["kind of edit"],"law":row["law"],"grant":row["arm"],
            "own restrictive birth changes":actual,**compared}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--save",type=Path)
    args = p.parse_args()
    start = perf_counter()
    out = []
    for edit,number,size in [("E1",81,6),("E2",2,2)]:
        picked = random.Random(SEED).sample(range(number),size)
        if edit == "E1" and 0 not in picked:
            picked.append(0)  # Archived maximum on the fixed old reading.
        if args.pilot:
            picked = picked[:1]
        with gzip.open(HERE.parent/("built_"+edit+".jsonl.gz"),"rt") as lines:
            for line in lines:
                r = json.loads(line)
                if r["built"] in picked:
                    out.append(evaluate(r))
    result = {"seed":SEED,"seconds":round(perf_counter()-start,3),"rows":out}
    if args.save:
        (HERE / args.save).write_text(json.dumps(result,indent=1)+"\n")
    print("rows",len(out),"seconds",result["seconds"])
