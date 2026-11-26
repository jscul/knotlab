"""Check the earlier archived tables and the obstruction for fixed parity rules."""

import gzip
import json
from fractions import Fraction
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    family = here.name + "-E001_four_settings"
    receipt = here.parents[1] / "artifacts" / here.name / family / "results.json"
    replay = json.loads(receipt.read_text())
    prior = here.parent / "KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A"
    with gzip.open(prior / "observations.json.gz", "rt") as stream:
        archive = json.load(stream)["all_seven_question_tables"]["frames"]["parity_even_fixed"]

    for change, field in (("change+90", "born_numerators"), ("change", "unturned_numerators")):
        records = [row for row in archive["records"] if row["questions"] == ["read", change]]
        assert len(records) == 1
        seen = set()
        for old in records[0]["rows"]:
            setting = "".join(map(str, old["setting"]))
            assert setting not in seen
            seen.add(setting)
            old_row = old["outcomes_little_endian"]
            for word, new in zip(replay["setting_and_outcome_order"], replay[field][setting], strict=True):
                # The old receipt uses detector A as the least significant outcome bit.
                assert Fraction(old_row[int(word[::-1], 2)]) == Fraction(new, replay["probability_denominator"])
        assert seen == set(replay["setting_and_outcome_order"])
        print(f"Archived {change} comparison matched all 64 probabilities.")

    relation = {
        setting + word
        for setting, parity in replay["required_outcome_parity"].items()
        for word in replay["setting_and_outcome_order"]
        if word.count("1") % 2 == parity
    }
    witness = ("000000", "011001", "101001")
    total = "".join(str(sum(map(int, column)) % 2) for column in zip(*witness))
    assert len(relation) == 16 and all(state in relation for state in witness)
    assert total == "110000" and total not in relation
    print("Three allowed setting/outcome words sum to excluded 110000.")


if __name__ == "__main__":
    main()
