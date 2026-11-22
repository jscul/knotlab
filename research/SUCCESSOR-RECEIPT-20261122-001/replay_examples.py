"""Extract the paired continuous histories cited in the report from their full-word archive."""
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TICKET = HERE.name + "A"
DATA, = (ROOT / "artifacts" / TICKET).glob("*/alternate.json.gz")


def read(word, marks):
    return "".join(str(word >> n & 1) for n in marks)


def main():
    with gzip.open(DATA, "rt") as f:
        record = json.load(f)
    sel = record["later_source_enrollment"]["selected"]
    assert (sel["H"], sel["K"], sel["G"]) == (631, 632, 1595)
    original = json.loads((HERE / "later_source_joint.json").read_text())
    replay = {"selection_for_the_auditor": sel, "full_states_in": str(DATA.relative_to(ROOT)),
              "cases": {}}
    for law, probes in (("parity", [("000", 0), ("100", 1)]), ("nae", [("100", 0), ("000", 1)])):
        first = original[law]["original_source_interventions"]
        replay["cases"][law] = {"original_sender_late_request": {
            "same_first_receipt": first["first_receipt_word"],
            "transposition_occurred": first["realized_undo"],
            "holding_after_either_actual_course": first["common_local_G_word"],
            "parity_constraints_violated_by_proposal": first["requested_undo_refused_by_these_holders"]}}
        course = record["courses"][law]["intact"]
        g, = [b for b in course["fourth"]["births"] if b["holder"] == sel["G"]]
        control = record["later_source_controls"][law]
        examples = control["modes"]["calibrated"]["whole_paired_examples"]
        both = []
        for w, h in probes:
            e, = [r for r in examples if (r["W"], r["h"]) == (w, h)]
            prefix = int(e["common_cut_three_state"], 16)
            assert read(prefix, (1754, 1755, 1756)) == w
            assert read(prefix, (sel["paid_h"],)) == str(h)
            assert read(prefix, (sel["paid_q"], sel["spare_q"])) == "01"
            pair = {}
            for act, v in (("I", 0), ("T", 1)):
                path = e["arms"][act]
                at_offer, birth, finish = (int(path[k], 16) for k in ("cut_three_after", "cut_four_after", "cut_five_after"))
                assert at_offer == (prefix if not v else prefix ^ ((1 << sel["paid_q"]) | (1 << sel["spare_q"])))
                received = read(birth, (sel["paid_h"], sel["paid_q"]))
                assert received == str(h) + str(v)
                assert received == read(finish, (sel["paid_h"], sel["paid_q"]))
                young = read(birth, g["fresh_names"])
                assert young == read(finish, g["fresh_names"])
                pair["exchange" if v else "keep"] = {"anonymous_incoming": "".join(sorted(received)),
                    "own_word": young, "own_local_sharing_birth_and_finish": control["G_own_finish"]["coholder_samples"]}
            both.append({"earlier_three_bit_word_for_auditor": w, "first_bit_at_H": int(w[0]), "H_paid_forward": h,
                         "common_whole_prefix_sha256_of_saved_hex": sha256(e["common_cut_three_state"].encode()).hexdigest(),
                         "same_prefix_later_alternatives": pair})
        replay["cases"][law]["prepared_different_sender"] = both
    (HERE / "decisive_replay.json").write_text(json.dumps(replay, indent=2) + "\n")


if __name__ == "__main__":
    main()

