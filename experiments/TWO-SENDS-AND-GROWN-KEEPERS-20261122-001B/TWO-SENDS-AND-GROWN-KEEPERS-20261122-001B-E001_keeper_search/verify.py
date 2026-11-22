"""Reconcile independent physical codes, port denominators and the 64 focal cells."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TICKET="TWO-SENDS-AND-GROWN-KEEPERS-20261122-001B"
OUT=ROOT/"artifacts"/TICKET/HERE.name
RESEARCH=ROOT/"research"/TICKET


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    with gzip.open(path,"rt") as fp:
        return json.load(fp)


def reversed_bits(word):
    return ((word&1)<<2)|(word&2)|(word>>2)


def verify():
    source=read(OUT/"census.json.gz")
    writer=read(OUT/"writer_control.json.gz")
    bindings=source["inputs_sha256"] | writer["source_sha256"]
    for name,digest in bindings.items():
        assert sha(ROOT/name)==digest,(name,digest)
    probability_pairs=0
    matrix_pairs=0
    control_counts={}
    for law in ("parity","nae"):
        census=next(row for row in source["records"] if row["source"]=="D-s3-p4-k1" and row["law"]==law)
        control=writer["laws"][law]
        assert control["actual_first_turn"]["reached"]==census["stages"][1]["holdings"]
        m=64 if law=="parity" else 222
        completions=4**4*2 if law=="parity" else 7**4*3
        ready_old=8 if law=="parity" else 16
        ready=Fraction(ready_old,m)
        assert control["complete_population"]==m*completions==census["stages"][1]["uniform_complete_stage_words"]
        scenario=control["scenarios"]["both_guarded_offers"]
        for name in ("uniform_complete","chronological"):
            readouts=scenario["readout"][name]["scored_policies"]
            for label in ("supplied_ready_then_terminal","terminal_only"):
                counts=readouts[label]["right_wrong_and_false_indication_per_original_launch"]
                assert Fraction(counts["right"])==ready
                assert Fraction(counts["wrong"])==(0 if label=="supplied_ready_then_terminal" else ready)
            for terminal in ("zero","one"):
                at_terminal=scenario["focal_ports"][name]["terminal_only"][terminal]
                for parent_tag,ind_tag in (("retained","positive"),("ordinary_diagonal","ordinary_diagonal"),
                                           ("copied_first_focal_bit","first_focal_name_copied_and_held"),
                                           ("returned_focal_bit","same_copy_coherently_returned")):
                    ours=source["native_unconditional_readout"][law]["decline_conditional"][parent_tag]
                    independent=writer["conditional_focal_state_library"][at_terminal["states"][ind_tag]]
                    # The entire terminal-only distribution keeps the two u values equally.
                    for i in range(8):
                        for j in range(8):
                            x,y=reversed_bits(i),reversed_bits(j)
                            assert ours["Z_or_X_settings_by_outcomes"][i][j]==independent["conditional_probabilities"][x][y]
                            assert ours["Gram"][i][j]==independent["conditional_gram"][x][y]
                            probability_pairs+=1
                            matrix_pairs+=1
                hr=scenario["focal_ports"][name]["supplied_ready_then_terminal"][terminal]
                assert Fraction(hr["original_launch_probability"])==ready/2
        control_counts[law]={"source_words":m,"completion_multiplier":completions,
                             "both_signs_each_ready_word_count":ready_old*completions//2,
                             "each_authenticated_sign_per_launch":str(ready/2),"unaided_accuracy":"1/2"}
    names=[HERE/"identity.json",HERE/"contract.json",HERE/"census.py",HERE/"writer_control.py",Path(__file__),
           OUT/"census.json.gz",OUT/"census_summary.json",OUT/"writer_control.json.gz",
           RESEARCH/"design_candidate.md",RESEARCH/"design_candidate_2.md",RESEARCH/"preregistration.md",
           RESEARCH/"advisor_receipt.json"]
    return {"ticket":TICKET,"status":"Completed","scientific_referee":"pending",
            "cross_implementation_probability_cells":probability_pairs,
            "cross_implementation_density_matrix_cells":matrix_pairs,"matched_positive_control":control_counts,
            "independent_design":source["inputs_sha256"][str((RESEARCH/"preregistration.md").relative_to(ROOT))],
            "file_sha256":{str(p.relative_to(ROOT)):sha(p) for p in names}}


if __name__=="__main__":
    arg=ArgumentParser()
    group=arg.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    opts=arg.parse_args()
    result=json.dumps(verify(),indent=2,sort_keys=True)+"\n"
    path=OUT/"replay_receipt.json"
    if opts.write:path.write_text(result)
    elif result!=path.read_text():raise SystemExit("Integration receipt differs")
    print(sha(path),path.name)
