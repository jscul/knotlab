"""Recount both split minima on rebuilt_inputs.jsonl, then compare by roster ID."""

from collections import Counter, defaultdict
from io import StringIO
from itertools import combinations, product
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from split_search import ReaderSearch, any_split, split_choices


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent


def read_rows(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream]


def score(row):
    if row["strict_min"] is not None:
        return "strict"
    return "neither" if row["general_min"] is None else "only_general"


def verify(input_row, witness, strict):
    if witness is None:
        return
    readers = [set(g) for g in witness["readers"]]
    failure = {tuple(sorted(p)) for p in witness["failing_pairs"]}
    allowed = {tuple(sorted(p)) for p in input_row["pairs"]}
    assert failure and failure <= allowed
    assert all(a.isdisjoint(b) for a, b in combinations(readers, 2))
    assert set.union(*readers) == {d for p in failure for d in p}
    supports = input_row["supports"]
    for group in readers:
        assert all(len(group.intersection(knot)) <= 1 for knot in supports)
        if strict:
            assert len(group) == 2 and tuple(sorted(group)) in failure
    assert all(any(a in g and b in g for g in readers) for a, b in failure)
    for one, other in combinations(supports, 2):
        assert sum(tuple(sorted((a, b))) in failure for a, b in product(one, other)) % 2 == 0
    # Sorting the given product into distinction-label order makes one exchange
    # per inversion. Only an exchange of a declared failing pair changes its sign.
    concatenated = [d for knot in supports for d in knot]
    exchanges = sum(
        (right, left) in failure
        for index, left in enumerate(concatenated)
        for right in concatenated[index + 1:]
        if left > right
    )
    assert exchanges % 2 == 1


def archive():
    birth = {r["start"]: r for r in read_rows(STUDY / "results.jsonl")}
    whole = {i: r for i, r in birth.items() if "whole: general" in r}
    losses = {r["start"]: r for r in read_rows(STUDY / "whole_only.jsonl")}
    assert not whole.keys() & losses.keys()
    whole.update(losses)
    types = {r["type"]: r for r in read_rows(STUDY / "census_types.jsonl")}
    fixtures = json.loads((STUDY / "fixtures.json").read_text())
    # The three-knot start is archived as the first positive census row.
    fixtures["ring of three's closure"] = birth[17]
    return {"birth": birth, "whole": whole, "type": types, "fixture": fixtures}


def published_comparisons(result, original):
    whole = result["population"] == "whole"
    prefix = "whole: " if whole else ""
    checks = {
        prefix + "strict": result["strict_min"] is not None,
        prefix + "fewest strict readers": result["strict_min"],
        prefix + "general": result["general_min"] is not None,
    }
    if not whole:
        checks["fewest readers"] = result["general_min"]
    if "closing round" in original:
        checks["closing round"] = result["round"]
    if "knots" in original:
        checks["knots"] = result["knots"]
    if "largest knot" in original:
        checks["largest knot"] = result["largest_knot"]
    if "choices" in result:
        answer = result["choices"]
        checks.update({
            "strict odd choices": answer["strict_odd_choices"],
            "strict sizes": answer["strict_sizes"],
            "odd choices with a split": answer["odd_choices_with_a_split"],
            "their group sizes": answer["failing_group_sizes"],
        })
    return checks


def forced_fixture_queries(input_row):
    """Check forcing each possible pair against exhaustive local failure patterns."""
    tested = 0
    supports, pairs = input_row["supports"], input_row["pairs"]
    for pair in pairs:
        search = ReaderSearch(supports, pairs, required=[pair])
        possibilities = split_choices(search)
        search.free_data.cache_clear()
        for strict, field in [(True, "strict_odd_choices"), (False, "odd_choices_with_a_split")]:
            witness = any_split(supports, pairs, required=[pair], strict=strict)
            assert (witness is not None) == bool(possibilities[field])
            if witness is not None:
                verify(input_row, witness, strict)
                assert pair in witness["failing_pairs"]
            tested += 1
    return tested


def main():
    inputs = read_rows(HERE / "rebuilt_inputs.jsonl")
    originals = archive()
    assert {(r["population"], r["key"]) for r in inputs} == {
        (pop, key) for pop, group in originals.items() for key in group
    }
    assert len({(r["population"], r["key"]) for r in inputs}) == len(inputs)
    results = {}
    mismatches = []
    fields = defaultdict(Counter)
    with StringIO() as out:
        for inputs_row in inputs:
            pop, key = inputs_row["population"], inputs_row["key"]
            search = ReaderSearch(inputs_row["supports"], inputs_row["pairs"])
            assert search.checks == inputs_row["checks"] and search.cost == inputs_row["cost"]
            strict = search.minimum(True)
            general = search.minimum(False, strict)
            result = {
                "population": pop, "key": key, "round": inputs_row["round"],
                "knots": len(inputs_row["supports"]), "largest_knot": max(map(len, inputs_row["supports"])),
                "distinctions": len(search.labels), "decidable_pairs": len(search.pairs),
                "strict_min": None if strict is None else len(strict[1]),
                "general_min": None if general is None else len(general[1]),
                "strict_witness": search.render(strict), "general_witness": search.render(general),
            }
            for kind in ["strict", "general"]:
                witness = result[kind + "_witness"]
                verify(inputs_row, witness, strict=kind == "strict")
                assert (witness is None) == (result[kind + "_min"] is None)
                if witness:
                    assert len(witness["readers"]) == result[kind + "_min"]
            if pop == "fixture" or (pop in ("birth", "type") and inputs_row["dimension"] <= 14):
                answer = split_choices(search)
                assert min(answer["strict_sizes"], default=None) == result["strict_min"]
                layouts = answer["one_minimum_layout_per_word_sizes"]
                assert min(map(len, layouts), default=None) == result["general_min"]
                result["choices"] = answer
            search.free_data.cache_clear()
            original = originals[pop][key]
            checks = published_comparisons(result, original)
            differences = {f: {"recorded": original[f], "recount": v} for f, v in checks.items() if original[f] != v}
            if differences:
                mismatches.append({"population": pop, "key": key, "differences": differences})
            fields[pop].update(checks.keys())
            result["archived_fields_agree"] = not differences
            results[pop, key] = result
            out.write(json.dumps(result, separators=(",", ":")) + "\n")
        rows_text = out.getvalue()

    summary = {
        "input": "rebuilt_inputs.jsonl, one row per positive birth start, eligible later whole start, finished type or fixture",
        "conventions": (
            "key is the zero-based census start or finished type index, or the fixture description. "
            "The listed knots determine the sign order. Pairs are unordered original distinction labels. "
            "Every active distinction appears in a failing pair. A reader may combine disjoint failing groups "
            "when no knot holds two of its distinctions. The number of readers is minimized over all odd words."
        ),
        "search": (
            "Branch on leaving a distinction unused or assigning its whole reader, exhaustively testing subsets "
            "of the remaining distinctions with disjoint holders. An exact binary elimination relaxation discards "
            "infeasible branches. Strict groups have size two. The upper bound is the number of distinctions "
            "divided by two and rounded down. A smaller budget is tested until infeasible. Small-code checks "
            "enumerate only combinations of permitted local failure patterns, deduplicating equal pair sets."
        ),
        "weighting": {
            "birth": "one vote per census start attaining odd with birth choices",
            "whole": "one vote per later census start attaining odd with whole choices",
            "type": "one vote per finished census type",
            "fixture": "one vote per hand case, with the closed and grown ring of five distinct",
        },
        "by_population": {},
        "fields_compared": fields,
        "published_field_differences": mismatches,
    }
    for pop in originals:
        data = [r for (p, _), r in results.items() if p == pop]
        summary["by_population"][pop] = {
            "rows": len(data),
            "split": Counter(map(score, data)),
            "strict_minima": Counter(r["strict_min"] for r in data if r["strict_min"] is not None),
            "general_minima": Counter(r["general_min"] for r in data if r["general_min"] is not None),
            "general_fewer_than_strict": sum(r["strict_min"] is not None and r["general_min"] < r["strict_min"] for r in data),
            "largest_structural_reader_bound": max(r["distinctions"] // 2 for r in data),
            "records_with_split_choice_counts": sum("choices" in r for r in data),
            "positive_witnesses_checked": {
                kind: sum(r[kind + "_witness"] is not None for r in data)
                for kind in ("strict", "general")
            },
        }
    birth = [r for (pop, _), r in results.items() if pop == "birth"]
    for field in ["round", "largest_knot"]:
        summary["birth_by_" + field] = {
            v: Counter(score(r) for r in birth if r[field] == v) for v in sorted({r[field] for r in birth})
        }
    later = [r for r in birth if r["round"] > 1]
    summary["later_birth_and_whole"] = {
        "birth_rows": len(later),
        "matching_existence": sum(score(r) == score(results["whole", r["key"]]) for r in later),
        "strict_minimum_differences": [r["key"] for r in later if r["strict_min"] != results["whole", r["key"]]["strict_min"]],
        "general_minimum_differences": [r["key"] for r in later if r["general_min"] != results["whole", r["key"]]["general_min"]],
        "whole_with_no_odd_birth_choice": Counter(
            score(r) for (p, key), r in results.items() if p == "whole" and ("birth", key) not in results
        ),
        "archived_comparison": "The archive gives whole strict minima and whole general existence. The comparison of general minima is additional.",
    }
    paired_inputs = {(r["population"], r["key"]): r for r in inputs}
    changed = []
    for key in summary["later_birth_and_whole"]["general_minimum_differences"]:
        rows = {"key": key}
        for pop in ("birth", "whole"):
            counted = results[pop, key]
            raw = paired_inputs[pop, key]
            search = ReaderSearch(raw["supports"], raw["pairs"])
            answer = split_choices(search)
            search.free_data.cache_clear()
            counts = answer["word_counts_by_minimum_readers"]
            assert min(counts) == counted["general_min"]
            rows[pop] = {"minimum_readers": min(counts), "split_words_by_minimum_readers": counts}
        changed.append(rows)
    summary["later_birth_and_whole"]["changed_minima_rechecked_by_local_failure_patterns"] = changed
    summary["small_codes"] = {
        "published_records": sum("enumeration agrees" in r for pop in ["birth", "type", "fixture"] for k, r in originals[pop].items()
                                 if (pop, k) != ("fixture", "ring of three's closure")),
        "added_hand_case": "The three-knot start also has an explicit hand row here. The study retained it among the birth rows.",
        "unreported_minimum_layout_ties": "One minimum partition per odd word contributing to a split is used in the auxiliary reader-size shapes. The original comparison uses all distinct sizes of the forced failing groups.",
    }
    summary["forced_pair_queries_checked_on_fixtures"] = sum(
        forced_fixture_queries(r) for r in inputs if r["population"] == "fixture"
    )
    with TemporaryDirectory(dir=HERE) as scratch:
        for name, content in [("split_rows.jsonl", rows_text), ("split_counts.json", json.dumps(summary, indent=2) + "\n")]:
            temporary = Path(scratch) / name
            temporary.write_text(content)
            temporary.replace(HERE / name)
    print(f"Rows {len(results)}, recorded-field discrepancies {len(mismatches)}", flush=True)


if __name__ == "__main__":
    main()
