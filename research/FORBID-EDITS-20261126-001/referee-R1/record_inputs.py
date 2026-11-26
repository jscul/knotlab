"""Check the declared reader record on scored rows with loss and an unchanged stored record."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
from random import Random
from time import perf_counter
import json

from literal import TruthTable, archive_rows, bits_of, meeting_pattern, ordered_unique, setting_inputs
from growth import grow

HERE = Path(__file__).resolve().parent
SEED = 2026112606


def views(row):
    base = tuple(map(tuple, row["supports"]))
    readers = row["readers"]
    law = row["law"]
    first = max(bits_of(base))+1
    previous = {}
    change = {}
    for st in product(range(2), repeat=len(readers)):
        ed, _ = setting_inputs(base, first, readers, st, row["kind of edit"])
        tab = TruthTable(bits_of(ed))
        _, births = grow(ed,law,row["arm"])
        births.sort(key=meeting_pattern)
        surviving = tab.conjunction(base+ed,law)
        for b in births:
            if not b["f"]:
                surviving &= tab.allows(b["inputs"],law)
        assert surviving.bit_count() == row["retained of old"]["".join(map(str,st))][0]
        cells = {1:surviving}
        if law == "nae":
            for b in births:
                q = 1 << b["f"]
                if q == 1:
                    continue
                z,o = tab.all_equal(b["inputs"])
                equal = z | o
                nxt = {}
                for w,m in cells.items():
                    for mult,mask in [(q-1,m & equal),(q,m & (tab.all ^ equal))]:
                        if mask:
                            nxt[w*mult] = nxt.get(w*mult,0) | mask
                cells = nxt
        for i,rd in enumerate(readers):
            local = [b for b in births if set(b["parents"]).intersection(rd)]
            shape = tuple(map(meeting_pattern, local))
            bits = ordered_unique([d for h in rd for d in ed[h]]+[d for b in local for d in b["inputs"]])
            for w in ("U","S"):
                if not row[w]["record unchanged"] or w in change:
                    continue
                weights = cells if w == "U" else {1:surviving}
                masses = Counter()
                for mult, states in weights.items():
                    masses.update({v:mult*n for v,n in tab.histogram(states,bits).items()})
                total = masses.total()
                key = (w,i,st[i])
                if key not in previous:
                    previous[key] = shape,st,total,masses
                    continue
                initial,s,n,ref = previous[key]
                assert initial == shape
                for v in ref.keys() | masses.keys():
                    if ref[v]*total != masses[v]*n:
                        change[w] = {"reader":i,"settings":[s,st],"old distinctions":bits,"values":v,
                                     "probabilities":[str(Fraction(ref[v],n)),str(Fraction(masses[v],total))]}
                        break
    return change


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--save",type=Path)
    args = p.parse_args()
    start = perf_counter()
    rng = Random(SEED)
    out = {}
    for g in ("tables5","xrun","shared"):
        pool = []
        for f in sorted(HERE.parent.glob(g+"_*.jsonl.gz")):
            for line,r in archive_rows(f):
                if r["kind"] == ("shared birth, read" if g=="shared" else "read") and r["forbids somewhere"] and any(
                        r[w]["record unchanged"] for w in ("S","U")):
                    pool.append((f.name,line,r))
        rng.shuffle(pool)
        counts = Counter()
        differences = []
        for f,line,r in (pool[:5] if args.pilot else pool):
            delta = views(r)
            counts["rows"] += 1
            for w in ("U","S"):
                counts[w+" stored unchanged"] += r[w]["record unchanged"]
                counts[w+" newly changed"] += w in delta
            if delta:
                differences.append({"file":f,"line":line,"start":r["start"],"readers":r["readers"],"differences":delta})
        out[g] = {"counts":counts,"differences":differences}
        print(g,counts)
    if args.save:
        (HERE/args.save).write_text(json.dumps(out,indent=1)+"\n")
    print("seconds",round(perf_counter()-start,3))
