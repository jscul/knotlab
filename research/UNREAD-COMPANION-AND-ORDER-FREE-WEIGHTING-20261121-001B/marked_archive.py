"""Audit raw marked integer frequency tables and independently count each old marginal."""

from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = "ENTANGLEMENT-READ-20261120-001B"
FAMILY = OLD + "-E001_separated_readings"
ARCHIVE = ROOT / "artifacts" / OLD / FAMILY


def norm(values):
    return tuple(F(v, sum(values)) for v in values)


def tv(left, right):
    return sum(abs(a - b) for a, b in zip(norm(left), norm(right), strict=True)) / 2


def project(counts, marks, kept):
    positions = [marks.index(k) for k in kept]
    bins = [0] * (1 << len(kept))
    for word, count in zip(product((0, 1), repeat=len(marks)), counts, strict=True):
        slot = 0
        for j in positions:
            slot = 2 * slot + word[j]
        bins[slot] += count
    return bins


@cache
def inclusion_terms(n, rows):
    """Inclusion-exclusion of monochromatic old knots; members of a selected row must agree."""
    terms = Counter()
    for choice in range(1 << len(rows)):
        rep = list(range(n))
        for i, row in enumerate(rows):
            if (choice >> i) & 1:
                merged = {rep[k] for k in row}
                first = min(merged)
                rep = [first if p in merged else p for p in rep]
        terms[tuple(rep)] += (-1) ** choice.bit_count()
    return [(rep, len(set(rep)), v) for rep, v in sorted(terms.items()) if v]


@cache
def old_hist(n, rows, law, marks):
    if law == "nae":
        words = list(product((0, 1), repeat=len(marks)))
        hist = [0] * len(words)
        for rep, components, coeff in inclusion_terms(n, rows):
            address = tuple(rep[k] for k in marks)
            increment = coeff * (1 << (components - len(set(address))))
            for j, word in enumerate(words):
                if len(set(zip(address, word))) == len(set(address)):
                    hist[j] += increment
        assert all(v >= 0 for v in hist)
        return tuple(hist)
    hist = []
    equations = [(sum(1 << b for b in row), 0) for row in rows]
    for values in product((0, 1), repeat=len(marks)):
        basis = {}
        consistent = True
        for mask, value in equations + [(1 << j, v) for j, v in zip(marks, values)]:
            while mask:
                pivot = mask.bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = (mask, value)
                    break
                delta, offset = basis[pivot]
                mask, value = mask ^ delta, value ^ offset
            if not mask and value:
                consistent = False
                break
        hist.append(1 << (n - len(basis)) if consistent else 0)
    return tuple(hist)


def audit():
    with gzip.open(ARCHIVE / "exact_readings.json.gz", "rt") as f:
        prior = json.load(f)
    summary = json.loads((ARCHIVE / "summary.json").read_text())
    detail, identities, groups = {}, {}, Counter()
    stages, histograms = Counter(), Counter()
    old_tvs = {}
    ages, absent = Counter(), Counter()
    whole = {}
    for s in prior["sources"]:
        groups[s["group"]] += 1
        identities[s["name"]] = {
            "class": s["group"],
            "provenance": s["provenance"],
            "sizes": s["sizes"],
            "meetings": s["meetings"],
        }
        for law, pair in s["laws"].items():
            old, reached = pair
            assert old["age"] == 0 and reached["age"] == 1
            old_rows = tuple(map(tuple, old["supports"]))
            n = s["old_distinctions"]
            assert old_hist(n, old_rows, law, ()) == (old["complete_assignments"],)
            old_changed = []
            for stage in pair:
                stages[law, stage["age"], stage["status"]] += 1
                for category in ("external_pairs", "six_marks"):
                    for sl in stage[category]["slots"]:
                        age = stage["age"]
                        count_index = law, age, category
                        if sl["placement"] is None:
                            absent[count_index] += 1
                            continue
                        ages[count_index] += 1
                        histograms[law, age, sl["origin"]] += 1
                        if not age:
                            continue
                        res = sl["result"]
                        marks = res["mark_order"]
                        kept = tuple(v for v in marks if v < n)
                        original = list(old_hist(n, old_rows, law, kept))
                        key = "/".join(
                            (s["name"], law, category, sl["band"], sl["origin"])
                        )
                        assert key not in detail
                        current = {}
                        for arm, weighted in res["weightings"].items():
                            reduced = project(weighted["counts"], marks, kept)
                            rec = weighted["old_mark_check"]
                            assert (
                                list(kept) == rec["marks"]
                                and original == rec["start_counts"]
                            )
                            assert (
                                reduced == rec["grown_counts"]
                                and sum(weighted["counts"]) == weighted["total"]
                            )
                            assert [v > 0 for v in reduced] == [v > 0 for v in original]
                            change = tv(reduced, original)
                            assert change == F(*rec["mass_tv_from_start_u"])
                            old_tvs.setdefault((law, arm), []).append((change, key))
                            current[arm] = {
                                "marked_counts": weighted["counts"],
                                "integer_unit": weighted[
                                    "integer_units_per_unscaled_mass"
                                ],
                                "old_mark_counts": reduced,
                                "old_mark_TV_to_start": str(change),
                            }
                        before = tv(
                            current["U"]["old_mark_counts"],
                            current["L"]["old_mark_counts"],
                        )
                        complete_marked = tv(
                            current["U"]["marked_counts"], current["L"]["marked_counts"]
                        )
                        assert before == F(current["U"]["old_mark_TV_to_start"])
                        assert (
                            before <= complete_marked
                            and F(current["L"]["old_mark_TV_to_start"]) == 0
                        )
                        old_changed.append(bool(before))
                        detail[key] = {
                            "old_marks": kept,
                            "all_marks": marks,
                            "old_hist_independently_counted": original,
                            "current_marked_weights": current,
                            "selected": sl["placement"],
                            "eligible_in_slot": sl["eligible"],
                            "U_L_TV_old_marks": str(before),
                            "U_L_TV_all_marks": str(complete_marked),
                        }
            births = reached["growth"]["births"]
            only_unary = all(len(b["consumed"]) == 1 for b in births)
            if law == "parity":
                ext = 1 << sum(max(0, len(b["fresh"]) - 1) for b in births)
            elif only_unary:
                ext = 1
                for b in births:
                    ext *= (1 << len(b["fresh"])) - 1
            else:
                assert any(old_changed)
                ext = None
            if ext is not None:
                assert (
                    old["complete_assignments"] * ext == reached["complete_assignments"]
                )
                assert not any(old_changed)
            whole[s["name"] + "/" + law] = {
                "constant_fibre_size": ext,
                "full_word_U_equals_full_word_L": ext is not None,
                "certificate": (
                    "constant parity completions"
                    if law == "parity"
                    else "all births unary"
                    if only_unary
                    else "changed actual marginal"
                ),
                "initial_words": old["complete_assignments"],
                "grown_words": reached["complete_assignments"],
                "placements": len(old_changed),
                "old_mark_changes": sum(old_changed),
                "births": births,
            }
    tally = {}
    for oldrow in summary["old_marks_probability_change"]:
        k = oldrow["law"], oldrow["weighting"]
        vals = sorted(old_tvs[k])
        nonzero = [v for v in vals if v[0]]
        assert len(vals) == oldrow["measured"] and len(nonzero) == oldrow["changed"]
        assert [F(*x) for x in oldrow["tv_range"]] == [vals[0][0], vals[-1][0]]
        tally["/".join(k)] = {
            "placements": len(vals),
            "changed": len(nonzero),
            "unchanged": len(vals) - len(nonzero),
            "smallest_positive": [str(nonzero[0][0]), nonzero[0][1]]
            if nonzero
            else None,
            "greatest": [str(vals[-1][0]), vals[-1][1]],
            "zero_old_mark_placement_keys": [key for v, key in vals if not v],
        }

    def keys(counter):
        return {"/".join(map(str, k)): v for k, v in sorted(counter.items())}

    return {
        "source_roster_and_original_draws": identities,
        "source_group_counts": dict(sorted(groups.items())),
        "all_source_stages": keys(stages),
        "selected_placements_each_stage_and_width": keys(ages),
        "candidate_slots_left_unselected": keys(absent),
        "newborn_vs_old_only": keys(histograms),
        "TV_from_independently_counted_old_uniform": tally,
        "whole_word_comparison": whole,
        "all_first_grown_selected_integer_marked_weightings": detail,
    }
