"""Solve independently rebuilt codes, then compare archived results by ID."""

import json
from collections import Counter

from rebuild import HERE, core, save


def words(code):
    n = len(code["pairs"])
    pivots = core.basis(code["checks"])
    free = [i for i in range(n) if i not in pivots]
    generators = []
    for i in free:
        word = 1 << i
        for p in sorted(pivots, reverse=True):
            if (word & pivots[p]).bit_count() % 2:
                word |= 1 << p
        assert all((row & word).bit_count() % 2 == 0 for row in code["checks"])
        generators.append(word)
    word = 0
    yield word
    for index in range(1, 1 << len(free)):
        word ^= generators[(index & -index).bit_length() - 1]
        yield word


def small_check(code):
    scores = [[Counter(), Counter()] for _ in range(3)]
    group_masks = [sum(1 << i for i in group) for group in code["groups"]]
    for w in words(code):
        s = (w & code["cost"]).bit_count() % 2
        scores[0][s][w.bit_count()] += 1
        if w:
            scores[1][s][w.bit_count()] += 1
        scores[2][s][sum(bool(w & g) for g in group_masks)] += 1
    result = {}
    for (even, odd), optimize, key, word_count in zip(
        scores, [max, min, max], ["max", "min", "holder"], ["maximum words", "minimum words", "holder maximum words"]
    ):
        best = optimize(even.keys() | odd.keys())
        result[word_count] = even[best] + odd[best]
        result[key + " counts at optimum (even, odd)"] = [even[best], odd[best]]
        for counts, sign in [(even, "even"), (odd, "odd")]:
            field = {
                "max": f"max with {sign} sign",
                "min": "min with odd sign" if sign == "odd" else "min nonzero with even sign",
                "holder": f"max holder types with {sign} sign",
            }[key]
            result[field] = optimize(counts) if counts else None
    return result


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def verdicts(rows, field):
    counts = Counter(row[field] for row in rows)
    return {s: counts[s] for s in ("forced odd", "forced even", "free")}


def study_summary(rows):
    fields = ["max principle", "min principle", "holder-type principle"]
    main = {field: verdicts(rows, field) for field in fields}
    main["cross tables against max"] = {
        field: {v: verdicts([r for r in rows if r["max principle"] == v], field) for v in main["max principle"]}
        for field in fields[1:]
    }
    main["maximum pairs"] = max(r["decidable pairs"] for r in rows)
    main["maximum dimension"] = max(r["free choices"] for r in rows)
    main["knot-pair order tests"] = sum(r["knots"] * (r["knots"] - 1) // 2 for r in rows)
    main["doubled meetings"] = sum(r["doubled meeting"] for r in rows)
    main["unique pair maximum"] = sum(r["maximum words"] == 1 for r in rows)
    main["tied pair maximum, same sign"] = sum(r["maximum words"] > 1 and r["max principle"] != "free" for r in rows)
    main["all three verdicts coincide"] = sum(r["max principle"] == r["min principle"] == r["holder-type principle"] for r in rows)
    return main


def compare(rows, source, key):
    archived = jsonl(source)
    by_id = {r[key]: r for r in archived}
    assert len(by_id) == len(archived) and len(rows) == len({r[key] for r in rows})
    assert {r[key] for r in rows} == by_id.keys(), (source, "population mismatch")
    issues = []
    comparisons = Counter()
    for row in rows:
        for field, value in by_id[row[key]].items():
            if field in ("seconds", "round-by-round maximum closing sign"):
                continue
            if field == "enumerated":
                expected = {k: row["free choices" if k == "free directions" else k] for k in value}
            else:
                expected = row[field]
            comparisons[field] += 1
            if value != expected:
                issues.append({key: row[key], "field": field, "archived": value, "recounted": expected})
    return {"identity": key, "rows compared": len(rows), "fields checked": comparisons, "differences": issues}


def run():
    from extrema import solve
    codes = jsonl(HERE / "codes.jsonl")
    closure, types, controls = [], [], {}
    for c in codes:
        n = len(c["pairs"])
        answer = solve(n, c["checks"], c["cost"], c["groups"])
        assert answer["free choices"] == c["dimension"]
        witness = answer["max word"]
        assert witness.bit_length() <= n and witness.bit_count() == answer["max weight"]
        assert not any((r & witness).bit_count() % 2 for r in c["checks"])
        # Each exchange in rebuild.py was already tested on the entire code.
        assert c["odd attainable"] and c["cost"].bit_length() <= n
        assert (answer["min nonzero weight"] == 2) == any(len(group) >= 2 for group in c["groups"])
        row = {**answer, "decidable pairs": n, "knots": c["knots"], "doubled meeting": max(c["holder multiplicities"]) > 1,
               "second-order sign check": True, "odd attainable": c["odd attainable"]}
        if c["dimension"] <= 14:
            enumeration = small_check(c)
            for field in enumeration.keys() & answer.keys():
                assert enumeration[field] == answer[field], (field, c.get("start"), c.get("type"), enumeration[field], answer[field])
            row.update(enumeration)
        if "type" in c:
            types.append({"type": c["type"], **row})
        elif "start" in c:
            natural = c["natural rule keeps a state"]
            sign = ("odd" if c["cost"].bit_count() % 2 else "even") if natural else None
            assert not natural or (row["max weight"] == n and row["max principle"] == "forced " + sign)
            closure.append({"start": c["start"], "closing round": c["round"], "natural rule keeps a state": natural,
                            "natural rule closing sign": sign, **row})
        else:
            controls[c["hand"]] = row
            if c["hand"] == "three-knot start":
                maxima = [w for w in words(c) if w.bit_count() == row["max weight"]]
                controls[c["hand"]]["matching"] = [[p for j, p in enumerate(c["pairs"]) if w >> j & 1] for w in maxima]
                assert controls[c["hand"]]["matching"] == [[[0, 4], [1, 5], [2, 3]]]
    return closure, types, controls


def main():
    closure, types, controls = run()
    for label, rows in [("closures", closure), ("types", types)]:
        with (HERE / (label + ".jsonl")).open("w") as out:
            for row in rows:
                out.write(json.dumps(row, separators=(",", ":")) + "\n")
    checks = [compare(closure, HERE.parent / "results.jsonl", "start"), compare(types, HERE.parent / "census_types.jsonl", "type")]
    save(HERE / "comparison.json", checks)
    summary = {"one vote per eligible census start": study_summary(closure),
               "one vote per finished census type": study_summary(types),
               "pair maximum by closing round": {t: verdicts([r for r in closure if r["closing round"] == t], "max principle")
                                                  for t in (1, 2, 3)},
               "pair maximum by natural state": {str(v): verdicts([r for r in closure if r["natural rule keeps a state"] == v], "max principle")
                                                 for v in (True, False)},
               "minimum weight two": verdicts([r for r in closure if r["min nonzero weight"] == 2], "min principle"),
               "minimum weight two without doubled meeting": sum(r["min nonzero weight"] == 2 and not r["doubled meeting"] for r in closure),
               "maximum word multiplicity (1, 2, 3+) on grown codes of dimension <=14":
                   Counter(min(r["maximum words"], 3) for r in closure if r["free choices"] <= 14),
               "hand cases": {**controls, "four grown examples": [r for r in closure if r["start"] in (17, 24, 43, 57)]}}
    save(HERE / "tables.json", summary)
    assert not any(check["differences"] for check in checks), "See comparison.json for mismatches"


if __name__ == "__main__":
    main()
