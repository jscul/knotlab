"""Count a toy fixture against the choices in the pinned site component."""

import argparse
from collections import Counter
import itertools
import json
from pathlib import Path


PATTERNS = ("ring", "copier", "source")
JOINS = ("meeting", "share")
STEPS = (1, 2, 3)
RATIONS = ("ORD", "CAP-3", "FLOOR1")
TREATMENTS = ("CANCEL-WAIT", "CANCEL-RETIRE", "CANCEL-OFFSHOOT")
RETIRE = (None, 2, 4, 6)
CASE_KEYS = ("first", "second", "steps", "join", "ration", "treatment", "retireAfter")
COLUMNS = (
    "knots", "short", "madeFirst", "madeSecond", "madeBoth", "madeOther",
    "membersFirst", "membersSecond", "joined", "kept", "joinedSecond", "keptSecond",
)
DEFAULT = ("copier", "copier", 1, "share", "ORD", "CANCEL-WAIT", None)


def audit(fixture, full_menu):
    values = list(itertools.product(PATTERNS, (*PATTERNS, "stub"), STEPS, JOINS))
    start_keys = {"|".join(map(str, key)) for key in values}
    menu = {(*key, *choice) for key in values for choice in itertools.product(RATIONS, TREATMENTS, RETIRE)}
    keys = [tuple(case[name] for name in CASE_KEYS) for case in fixture["cases"]]
    assert set(fixture["starts"]) == start_keys
    assert len(keys) == len(set(keys)) and set(keys) <= menu
    assert fixture["knots"] == 450 and fixture["rounds"] == 12
    assert tuple(fixture["columns"]) == COLUMNS

    fixture_cases = Counter()
    fixture_rounds = Counter()
    retirement_followed_by_drawn_round = Counter()
    horizons = Counter()
    default = None
    for key, case in zip(keys, fixture["cases"], strict=True):
        first, second, steps, join, _ration, _treatment, retire = key
        rounds = case["rounds"]
        fixture_cases[retire] += 1
        fixture_rounds[retire] += len(rounds)
        if retire is not None and len(rounds) > retire:
            retirement_followed_by_drawn_round[retire] += 1
        horizons[len(rounds)] += 1
        assert len(rounds) <= fixture["rounds"]

        before = len(fixture["starts"]["|".join(map(str, (first, second, steps, join)))])
        for row in rounds:
            assert len(row) == len(COLUMNS)
            assert all(type(count) is int and count >= 0 for count in row)
            read = dict(zip(COLUMNS, row, strict=True))
            made = sum(read[name] for name in ("madeFirst", "madeSecond", "madeBoth", "madeOther"))
            assert before < read["knots"] <= fixture["knots"]
            assert read["knots"] - before == made
            assert read["kept"] <= read["joined"] and read["keptSecond"] <= read["joinedSecond"]
            assert read["membersFirst"] + read["membersSecond"] <= before
            assert read["short"] <= before
            before = read["knots"]

        if key == DEFAULT:
            default = [dict(zip(COLUMNS, row, strict=True)) for row in rounds]
    assert default is not None
    closure_cases = {
        key for key in menu if key[-1] is None or (key[2] == 1 and key[5] == "CANCEL-WAIT" and key[-1] in (2, 4))
    }
    assert set(keys) == (menu if full_menu else closure_cases)

    def labelled(counts):
        return {"never" if at is None else str(at): counts[at] for at in RETIRE}

    menu_cases = Counter(key[-1] for key in menu)
    return {
        "joined_starts": len(start_keys),
        "case_keys": list(CASE_KEYS),
        "menu_cases": len(menu),
        "fixture_cases": len(keys),
        "fixture_rounds": sum(fixture_rounds.values()),
        "menu_cases_by_retire_after": labelled(menu_cases),
        "fixture_cases_by_retire_after": labelled(fixture_cases),
        "fixture_rounds_by_retire_after": labelled(fixture_rounds),
        "retirement_followed_by_drawn_round": {
            str(at): retirement_followed_by_drawn_round[at] for at in RETIRE[1:]
        },
        "uncovered_cases_by_retire_after": labelled(menu_cases - fixture_cases),
        "cases_by_drawn_rounds": dict(sorted(horizons.items())),
        "fields_per_round": list(COLUMNS),
        "field_checks": len(COLUMNS) * sum(fixture_rounds.values()),
        "default_case": dict(zip(CASE_KEYS, DEFAULT, strict=True)),
        "default_rounds": default,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--full-menu", action="store_true")
    args = parser.parse_args()
    with args.fixture.open() as source:
        fixture = json.load(source)
    print(json.dumps(audit(fixture, args.full_menu), indent=2))


if __name__ == "__main__":
    main()
