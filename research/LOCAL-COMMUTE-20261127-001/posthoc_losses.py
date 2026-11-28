"""posthoc_losses.py (post hoc, after the frozen run): the closures where whole choices attain odd and birth choices do
not (P3'), and the random birth rule's closing signs. For each lost closure: the closing knot's places and parents,
whether its parents lie in different blocks, the pairs the birth rule forbids (two distinctions born in the same round,
both loose then, taken by different births of the next round), their birth round, and whether every odd whole choice
uses one of them (by construction it must). Also: under the round-by-round random birth rule (P5), the share of runs that
close odd at closures where birth choices attain odd, against one half (a nonzero linear functional on the choices is
odd on exactly half of them).
    posthoc_losses.py            reads results.jsonl, writes posthoc_losses.json
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "research" / "FORBID-EDITS-20261126-001"))
import forbid  # noqa: E402
import local_commute as lc  # noqa: E402


def main():
    rows = [json.loads(line) for line in (HERE / "results.jsonl").read_text().splitlines()]
    starts = forbid.starts()
    lost = [r for r in rows if r["end"] == "closed" and not r.get("closed at round 0")
            and r["whole choices attain odd"] and not r["birth choices attain odd"]]
    cases = []
    tally = collections.Counter()
    for r in lost:
        stages, births, _ = lc.grow(forbid.supports_of(starts[r["start"]]), 4, 40)
        st = lc.Structure(stages, births)
        forbidden = [p for p in st.unheld if p not in st.local]
        rounds = sorted({st.dround[a] for a, b in forbidden})
        closing = births[-1][0]
        case = {"start": r["start"], "closing round": r["closing round"], "knots": r["knots"],
                "closing knot places": len(stages[-1][-1]), "closing knot parents": len(closing["parents"]),
                "three parents in one block": r["three parents in one block"],
                "forbidden pairs": len(forbidden), "their birth rounds": rounds}
        cases.append(case)
        tally[(case["closing round"], case["closing knot places"], tuple(rounds))] += 1
    sampled = [r for r in rows if r.get("random local rule runs") and r["end"] == "closed"
               and not r.get("closed at round 0")]
    odd_where_attainable = [0, 0]
    odd_where_not = [0, 0]
    for r in sampled:
        signs = [x[1] for x in r["random local rule runs"] if x[0] == "kept"]
        target = odd_where_attainable if r["birth choices attain odd"] else odd_where_not
        target[0] += sum(s == "odd" for s in signs)
        target[1] += len(signs)
    out = {"lost closures": len(cases),
           "by (closing round, closing knot places, birth rounds of the forbidden pairs)":
               {str(k): v for k, v in sorted(tally.items())},
           "random birth rule: odd runs where birth choices attain odd (odd, runs)": odd_where_attainable,
           "random birth rule: odd runs where they do not (odd, runs)": odd_where_not,
           "cases": cases}
    (HERE / "posthoc_losses.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "cases"}, indent=1))


if __name__ == "__main__":
    main()
