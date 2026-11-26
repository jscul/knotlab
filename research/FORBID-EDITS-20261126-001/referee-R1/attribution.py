"""Compare each reader's actual forbidden prepared assignments when its own edit changes."""
import argparse
import gzip
import json
import random
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from time import perf_counter

from built_sample import value_masks
from growth import grow

HERE = Path(__file__).resolve().parent
SEED = 2026112603


def classify(r, shared=False):
    base = list(map(tuple,r["supports"]))
    readers = r["readers"]
    k = len(readers)
    first = max(map(max,base))+1
    names = set(range(first+k))
    full, masks = value_masks(names)
    def ok(held):
        if r["law"] == "nae":
            same_one = same_zero = full
            for d in held:
                same_one &= masks[d]
                same_zero &= full ^ masks[d]
            return full ^ (same_zero | same_one)
        odd = 0
        for d in held:
            odd ^= masks[d]
        return full ^ odd

    kept = full
    for held in base:
        kept &= ok(held)
    # Keep the same assignment names at all settings. A NAE edit adds a
    # free bit under the kept preparation. Both parity equations force it to zero.
    if r["law"] == "parity":
        for i in range(k):
            kept &= full ^ masks[first+i]
    loss_by_reader = {}
    shared_only, private_only = {}, {}
    differences = []
    for st in product(range(2), repeat=k):
        ed = base.copy()
        absent = 0
        for i,(s,own) in enumerate(zip(st, readers)):
            if r["kind of edit"] == "E2" or s:
                h = own[s] if r["kind of edit"] == "E2" else own[0]
                ed[h] += (first+i,)
            else:
                absent += 1
        status,births = grow(ed,r["law"],r["arm"])
        key = "".join(map(str,st))
        assert r["status"][key] == status
        lost = [0]*(k+1)
        joint = [0]*k
        private = [0]*k
        for b in births:
            owners = [i for i,rd in enumerate(readers) if set(b["parents"]).intersection(rd)]
            assert shared or len(owners) <= 1
            if not b["f"]:
                missing = kept & (full ^ ok(b["inputs"]))
                for i in (owners or [k]):
                    lost[i] |= missing
                    if i < k:
                        (joint if len(owners)>1 else private)[i] |= missing
        survived = kept
        for l in lost:
            survived &= full ^ l
        pad = 1 << (absent if r["law"] == "nae" else 0)
        actual = [survived.bit_count()//pad,kept.bit_count()//pad]
        if actual != r["retained of old"][key]:
            differences.append([key,actual,r["retained of old"][key]])
        loss_by_reader[st] = lost[:k]
        shared_only[st],private_only[st] = joint,private
    def changes(by_setting):
        return [any(l[i] != by_setting[st[:i]+(1,)+st[i+1:]][i]
                    for st,l in by_setting.items() if not st[i]) for i in range(k)]
    return changes(loss_by_reader), differences, changes(shared_only), changes(private_only)


def main(pilot,save,shared):
    strata = defaultdict(list)
    for group in (("shared",) if shared else ("tables5", "xcount")):
        for f in sorted(HERE.parent.glob(group+"_*.jsonl.gz")):
            with gzip.open(f,"rt") as stream:
                for row in map(json.loads,stream):
                    if row["kind"] == ("shared birth, read" if shared else "read") and row["forbids somewhere"]:
                        strata[(group,row["kind of edit"],row["law"],row["arm"])].append(row)
    rng = random.Random(SEED)
    result = {}
    for stratum,rows in sorted(strata.items()):
        rng.shuffle(rows)
        counts = Counter()
        mismatch = []
        for r in (rows[:1] if pilot else rows):
            dep, wrong_counts, joint, private = classify(r,shared)
            if shared:
                counts["shared only all"] += all(joint)
                counts["private only all"] += all(private)
            counts["rows"] += 1
            counts["semantic any"] += any(dep)
            counts["semantic two or more"] += sum(dep) >= 2
            counts["semantic all"] += all(dep)
            if wrong_counts or dep != r["forbidding changes with own setting"]:
                mismatch.append({"start":r["start"],"readers":r["readers"],"recorded":r["forbidding changes with own setting"],
                                 "semantic":dep,"count differences":wrong_counts})
        result[" ".join(stratum)] = {"counts":counts,"differences":mismatch}
    if save:
        (HERE/save).write_text(json.dumps(result,indent=1)+"\n")
    print("rows",sum(b["counts"]["rows"] for b in result.values()),
          "disagreements",sum(len(b["differences"]) for b in result.values()))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--shared",action="store_true")
    p.add_argument("--save",type=Path)
    args = p.parse_args()
    start = perf_counter()
    main(args.pilot,args.save,args.shared)
    print("seconds",round(perf_counter()-start,3))
