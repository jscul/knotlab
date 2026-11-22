"""Recount B285's two registered pulses from the archived payer and mark records."""
import gzip
import json
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    with gzip.open(here.with_name(here.name + "B") / "receipts.json.gz", "rt") as stream:
        archive = json.load(stream)
    cases = {case["case"]: case for case in archive["cases"]}
    assert len(cases) == 14
    assert sum(case["funded"] for case in cases.values()) == 13
    assert not cases["p_shortage"]["funded"]
    for key in ("intact_s_break", "near_s_break"):
        assert not cases[key]["S_first"]["private"]
    keys = ["intact", "near", "intact_w_disabled", "near_w_enabled"]
    expected = [2, 1, 2, 1]
    for key, count in zip(keys, expected):
        case = cases[key]
        assert sum(r["chains"] for r in case["open_balance"]) == 32768
        assert all((r["p"], r["p_only"]) == (count, 1) for r in case["open_balance"])
        for order, bounds in (("S_first", (17, 31)), ("R_first", (18, 32))):
            read = case[order]
            receipts = [read["private"][i] for i in ("1", "2")]
            left, right = [v["rank"] for v in receipts]
            assert (left, right) == bounds
            for receipt in receipts:
                parents = receipt["physical_parents"]
                assert any(p["carries_pulse"] and not p["retains_O"] for p in parents)
                assert sum(p["selected_previous"] for p in parents) == 1
                assert not next(p for p in parents if p["selected_previous"])["carries_pulse"]
            assert sum(left < rank <= right for rank in read["turns"]) == count
            assert sum(left < rank <= right for rank in read["p_only_turns"]) == 1
        print(key, count, "inclusive returns and one single-addition return")
    for key, lasts in zip(keys, (True, False, False, True)):
        assert (cases[key]["third"]["max_rank"] is None) == lasts
    primary = [p for p in archive["whole_state_on_actual_originals"]
               if p["preparations"] == ["intact", "near"]]
    assert sorted(p["law"] for p in primary) == ["nae", "parity"]
    for pair in primary:
        assert pair["exact_projected_relations_equal"]
        assert all(s == {"originals": 16, "retained_names": 262, "entire_spent_factors": 18}
                   for s in pair["sources"])
    for prefix, earlier_states_match in (("m_", True), ("t_", False), ("neither_", False)):
        arms = [prefix + "intact", prefix + "near"]
        states = [p for p in archive["whole_state_on_actual_originals"] if p["preparations"] == arms]
        assert sorted(p["law"] for p in states) == ["nae", "parity"]
        assert all(p["exact_projected_relations_equal"] == earlier_states_match for p in states)
        assert [len(cases[k]["S_first"]["registered_interval"]["p"]) for k in arms] == [2, 1]
    for order, (before, after) in {"S_first": (6, 22), "R_first": (5, 21)}.items():
        match, = [p for p in archive["matched_comparisons"]
                  if (p["left"], p["right"], p["policy"]) == ("intact", "near", order)]
        assert match["private_boundary_field_match"] and match["complete_earlier_parent_and_grant_match"]
        assert match["first_difference_in_earlier_alternatives_at_parent"] == before
        assert match["first_difference_in_selected_advancement_at_child"] == after
    unchanged, switched = [cases[key]["S_first"]["critical"] for key in keys[:2]]
    assert unchanged["earlier"]["complete_parent_and_grant_sha256"] == switched["earlier"]["complete_parent_and_grant_sha256"]
    for fork in (unchanged, switched):
        assert fork["earlier"]["rooted_subsupports"] == 321
        assert len(fork["all_options"]) == 26
        assert sorted(v["grant"] for v in fork["selected_payments"]) == [26, 32, 33]
        assert fork["selected_grant"] == 33
    assert unchanged["selected_names"] == ["p", "wP"]
    assert switched["selected_names"] == ["h", "wH"]
    assert sum(v["current_third"] for v in unchanged["selected_payments"]) == 1
    assert sum(v["current_third"] for v in switched["selected_payments"]) == 0
    print("Recounted both private receipts, all permitted balanced orderings and the crossed controls.")


if __name__ == "__main__":
    main()
