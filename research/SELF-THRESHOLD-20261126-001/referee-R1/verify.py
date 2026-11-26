"""Verify the threshold sample, cross-law comparisons, and the counterexample controls."""
import json
from collections import Counter

from archive import HERE, audit, draws


def read(name):
    return json.loads((HERE / name).read_text())


def check():
    archived = read("archive.json")
    selections = read("draws.json")
    samples = [json.loads(s) for s in (HERE / "samples.jsonl").read_text().splitlines()]
    for name in ("census", "linked"):
        assert json.loads(json.dumps(audit(name))) == archived[name]
        assert json.loads(json.dumps(draws(name))) == selections[name]
        selected = [r for r in samples if r["panel"] == name]
        expected = set(tuple(p) for group in selections[name].values() for p in group)
        assert len(selected) == len(expected)
        assert {tuple(r["pair"]) for r in selected} == expected
        for r in selected:
            laws = r["laws"]
            assert all(not d["differences"] for d in laws.values())
            for law, other in ([("HALF","CAP-3")] if name=="census" else
                                [("HALF","CAP-3"), ("PLACES","PLACES-JOINS"), ("ORD","PLACES-OFFSHOOTS")]):
                left,right = laws[law],laws[other]
                if name=="census" and not any(c["heard"] for c in left["changes"]):
                    continue
                assert left["baseline"]["digest"] == right["baseline"]["digest"]
                assert len(left["changes"]) == len(right["changes"])
                for a,b in zip(left["changes"],right["changes"]):
                    if name=="linked" or a["heard"]:
                        assert (a["after"],a["knot"],a["post_mark"]["digest"]) == (
                            b["after"],b["knot"],b["post_mark"]["digest"])
        print(f"{name}: {len(selected)} pairs, {sum(len(r['laws']) for r in selected)} complete law records agree")
        allocation = read(f"allocation_{name}.json")["rows"]
        for row in allocation:
            if row["hearings"]:
                assert row["baseline"] is None and all(h["half_split_on_changed_history"] is None
                                                        for h in row["hearings"])
        changes = sum(bool(row["any_half_split"]) for row in allocation)
        n_hearing = sum(len(row["hearings"]) for row in allocation)
        assert (changes, n_hearing) == ((173,6) if name=="census" else (0,124))
        print(f"{changes}/{len(allocation)} pairs differ in allocation; all {n_hearing} hearing histories agree")
    cases = read("reading.json")
    for k, first in (("four",13),("fund_five",None),("give_five_three",13),("four_half",None),
                     ("three",13),("any_four",13),("only_four",None),("restore_three",None)):
        m=cases[k]["marks"][0]
        assert m["heard"]==first and m["end"]==14
    assert len({cases[k]["marks"][0]["descent"] for k in ("four","fund_five","give_five_three","four_half")})==1
    assert all(m["own_counts"]==[82,83] and m["heard"]==9 for m in cases["minimum"]["marks"])
    assert len(cases["minimum"]["marks"])==3
    assert [r["next_births"] for r in read("later.json")["rows"]]==[[375,1723],[376,1742],[376,1742]]
    controls = read("census_controls.json")["controls"]
    counts = Counter(x["law"] for x in controls if x["heard"])
    assert counts == {"cap":6,"offshoot":6} and all(x["end"] == 12 for x in controls)
    print("The matched allocation controls and three round-24 continuations agree.")
    from parity import load, recount
    old, old_jobs = load("stale")
    new, new_jobs = load("renewed")
    assert json.loads(json.dumps(recount(old, new, old_jobs, new_jobs))) == read("parity_archive.json")
    records = read("parity_sample.json")["results"] + read("parity_diagnostic.json")["results"]
    assert len(records) == len({str(r["key"]) for r in records}) == 9
    assert all(not any(r["archive differences"].values()) for r in records)
    marks = [p for r in records for p in r["placements"]]
    assert all(p["stale"]["heard"] == p["renewed"]["heard"] for p in marks)
    assert Counter(p["renewed"]["heard"] for p in marks) == {None:9,4:10,5:15}
    assert sum(p["first funding discrepancy"] is not None for p in marks) == 5
    print("All 4,844 parity readings agree; 34 regrown marks match both archives.")


if __name__=="__main__":
    check()
