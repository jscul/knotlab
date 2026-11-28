"""Check the frozen text, census horizons, witnesses and earlier finished-type comparison."""
import argparse
from collections import Counter, defaultdict
from itertools import chain, combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ROOT = RESEARCH.parent
PREVIOUS = RESEARCH / "CELL-SIGN-20261127-001/referee-R1"
sys.path.insert(0, str(PREVIOUS))
# Earlier independent cross-pair referee's occurrence pairing and order tests.
import fixture_audit as paired
sys.path.insert(0, str(RESEARCH / "FORBID-EDITS-20261126-001"))
import forbid


def blob(ref, name):
    file = (STUDY / name).relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "show", f"{ref}:{file}"], cwd=ROOT)


def freeze():
    first, last = "dfa155dd8", "cb6e7cc082"
    before, after = [blob(ref, "README.md") for ref in (first, last)]
    return {
        "freeze": first, "close": last,
        "frozen README a verbatim prefix of closing README": after.startswith(before),
        "frozen lines": len(before.splitlines()), "added lines": len(after.splitlines())-len(before.splitlines()),
        "identical analysis source": blob(first, "evenorient.py") == blob(last, "evenorient.py"),
    }


def horizon(starts):
    short = [json.loads(line) for line in (STUDY / "census_starts.jsonl").read_text().splitlines()]
    by_round, outcomes, changed = Counter(), Counter(), []
    max_size, examined_rounds = 0, 0
    for index, start in enumerate(starts):
        state = forbid.supports_of(start)
        for t in range(11):
            frequency = Counter(chain.from_iterable(state))
            assert set(frequency.values()) <= {1, 2}
            if 1 not in frequency.values():
                status = "grown closed" if t else "initially closed"
                if t:
                    by_round[t] += 1
                break
            if t == 10:
                status = "at round limit"
                break
            new, status, _ = forbid.grown(state, "parity", "ordinary")
            if status == "stalled":
                break
            if len(new) > 3000:
                status = "at knot limit"
                break
            state = new
            max_size = max(len(state), max_size)
            examined_rounds += 1
        outcomes[status] += 1
        if (status == "grown closed") != (short[index]["outcome"] == "grown closed"):
            changed.append(index)
    return {"weighting": "one per roster start", "starts":len(starts), "outcomes":dict(outcomes),
            "positive-round closures by round":dict(by_round), "changes in closure membership from four rounds and forty knots":changed,
            "largest retained stage":max_size, "completed rounds":examined_rounds}


def attachment_audit():
    """Inspect every possible matching of repeated occurrences in the two saved samples."""
    out = []
    for name in ["extension", "second_sample"]:
        groups = defaultdict(list)
        for row in json.loads((STUDY / f"{name}_nonorientable_even.json").read_text()):
            groups[row["index"], row["whole"]].append(row)
        for (index, whole), rows in sorted(groups.items()):
            totals = Counter()
            for row in rows:
                cycles = row["cycles"]
                at = defaultdict(list)
                for i, cycle in enumerate(cycles):
                    for j in range(4):
                        u, v = cycle[j], cycle[(j+1) % 4]
                        at[tuple(sorted((u,v)))].append((i,j,u < v))
                for selected in product(*(paired.pairings(visits) for visits in at.values())):
                    result = paired.paired_reading(cycles, list(chain.from_iterable(selected)))
                    fields = ("orientable", "Euler count", "two-colourable", "sign", "components through attached cross pairs")
                    totals[tuple(result[k] for k in fields)] += 1
            out.append({"sample":name,"index":index,"eligibility":"whole" if whole else "birth",
                        "labelled choices":len(rows),"weighting":"one per labelled choice and pairing of its occurrences",
                        "columns":list(fields)+["count"], "outcomes":[[*k,n] for k,n in sorted(totals.items())]})
    return out


def finished_types():
    """Read each type's holdings directly; test embeddings of the three seven-pair representatives."""
    types = json.loads(paired.CENSUS.read_text())
    rows = [r for r in json.loads((PREVIOUS / "minimal_rows.json").read_text()) if r["population"]=="type"]
    classes = json.loads((STUDY / "abstract.json").read_text())["non-orientable even classes"]
    simple = [r for r in classes if r["doubled pairs"]==0]
    masks = []
    for r in simple:
        cells = r["cycles"]
        support = [tuple(sorted(p)) for a,c,b,d in cells for p in ((a,b),(c,d))]
        assert len(set(support))==len(support)
        # Counts of labelled cycle sets per distinct holding are uniform on the orbit.
        images = Counter(frozenset(tuple(sorted((g[x],g[y]))) for x,y in support) for g in permutations(range(7)))
        weights = {k: v*r["labelled copies"]//5040 for k,v in images.items()}
        assert all(5040*w==r["labelled copies"]*images[k] for k,w in weights.items())
        masks.append(weights)
    positives, strict_counts, achieved = [], Counter(), [0]*len(simple)
    seen = {r["type"]:r for r in rows if r["fewest strict readers"]}
    doubled = 0
    for i, t in enumerate(types):
        holding = frozenset(tuple(sorted(p)) for p in t["sharing"])
        doubled += len(holding) != len(t["sharing"])
        counts = [sum(n for s,n in tables.items() if s <= holding) if t["n"]==7 else 0 for tables in masks]
        for k, n in enumerate(counts):
            achieved[k] += n
        if i in seen:
            counts_by_size = seen[i]["minimal even by size and orientability"]
            bad = {size:int(values.get("nonorientable",0)) for size,values in counts_by_size.items()}
            assert sum(counts)==bad.get("7",0), (i,counts,bad)
            if sum(bad.values()):
                positives.append([i,t["n"],t["m"],sum(bad.values())])
            strict_counts.update(bad)
    return {"weighting":"one per finished type; each compatible labelled choice once within a type",
            "types":len(types),"with doubled meetings":doubled,"with a strict split":len(seen),
            "strict-split types with a nonorientable even through eight pairs":positives,
            "nonorientable even by size in earlier uncapped strict-split listings":dict(strict_counts),
            "seven-pair appearances of each simple representative across all types":achieved}


def five_knots():
    """List the missing-knot matchings for the five-pair case of Euler count zero."""
    options = []
    for k in range(5):
        a,b,c,d = sorted(set(range(5))-{k})
        options.append([((a,b),(c,d)),((a,c),(b,d)),((a,d),(b,c))])
    witnesses = []
    for row in product(*options):
        if len(set(chain.from_iterable(row))) != 10:
            continue
        for choices in product((0,1),repeat=4):
            flips = (0,*choices)
            counts=Counter()
            for ((a,b),(c,d)),flip in zip(row,flips):
                cyc=(a,c,b,d) if not flip else (a,d,b,c)
                counts.update(zip(cyc,cyc[1:]+cyc[:1]))
            if all(counts[u,v]==counts[v,u] for u,v in combinations(range(5),2)):
                witnesses.append({"matchings by omitted knot":row,"balancing reversals":flips})
                break
        else:
            raise AssertionError(row)
    return {"weighting":"one per labelled choice on five knots","choices":len(witnesses),"certificates":witnesses}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prefix",type=int,help="time a prefix of the longer growth census without writing")
    args = p.parse_args()
    starts = json.loads((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_text())
    t0 = time.monotonic()
    if args.prefix:
        print(horizon(starts[:args.prefix]), round(time.monotonic()-t0,2))
    else:
        result = {"freeze":freeze(), "longer census":horizon(starts), "pairing tests on saved choices":attachment_audit(),
                  "finished census types":finished_types(), "five-knot check":five_knots()}
        (HERE/"record_counts.json").write_text(json.dumps(result, indent=2)+"\n")
        print("Completed in",round(time.monotonic()-t0,2),"seconds")
