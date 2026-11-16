"""Bind the physical-piece oracle using the identical previous programs and a neutral record ordering."""
from collections import defaultdict
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1] / "experiments" / HERE.name / (HERE.name + "-E001_consumer_edits")
sys.path.insert(0, str(EXP))
from prepare import OUT, ROOT, read, sha, write


def main():
    target = OUT / "explicit-piece"
    target.mkdir(exist_ok=True)
    cases, grades = read(OUT / "public.json"), read(OUT / "grades.json")
    for case in cases:
        groups = defaultdict(list)
        for piece in case["pieces"]:
            groups[tuple(piece["inputs"])].append(piece)
        groups = {group:iter(sorted(pieces, key=lambda p: p["bit"])) for group,pieces in groups.items()}
        # Keep the group at every slot. Order only the two complementary records of each group.
        case["pieces"] = [next(groups[tuple(p["inputs"])]) for p in case["pieces"]]
        old = grades[case["id"]]["base"]
        physical = next(p for p in case["pieces"] if p["inputs"] == old["anchor"])
        if physical["bit"] != old["anchor_bit"]:
            raise ValueError("this rendering would not supply the original physical piece")
        # Only the recorded public-list index changed. Grade widths, truth, bit and all other data are identical.
        new_index = case["pieces"].index(physical)
        old["anchor_piece"] = grades[case["id"]]["anchor_piece"] = new_index
    design = read(OUT / "design.json")
    design["sources"].update({str(p.relative_to(ROOT)):sha(p) for p in
                              (Path(__file__).resolve(), HERE / "physical_oracle.md")})
    design.update(previous_binding=sha(OUT / "data-bound.json"), original_wire_first=len(cases))
    for name,value in (("design",design), ("public",cases), ("grades",grades), ("hints",read(OUT / "hints.json"))):
        write(target / (name+".json"), value)
    files = ("design.json","public.json","grades.json","hints.json")
    write(target / "data-bound.json",{name:sha(target/name) for name in files})


if __name__ == "__main__":
    main()
