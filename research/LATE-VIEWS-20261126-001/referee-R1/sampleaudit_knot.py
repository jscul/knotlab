"""Emit arguments for testing a projected starting parity rule with knotlab check."""

from argparse import ArgumentParser
from itertools import product
import json

from sampleaudit import HERE, STUDY, archive_name, read_rows


def project(stars, knot):
    holding = stars[knot]
    target = sum(1 << place for place in holding)
    span = {0}
    for row in stars:
        mask = sum(1 << place for place in row)
        span |= {restriction ^ mask for restriction in span}
    supported = {restriction for restriction in span if not restriction & ~target}
    independent, covered = [], {0}
    for restriction in sorted(supported, key=lambda r: (r.bit_count(), r)):
        if restriction in covered:
            continue
        part = [place for place in holding if restriction & (1 << place)]
        independent.append(part)
        covered |= {prior ^ restriction for prior in covered}
    assert covered == supported
    clauses = []
    for part in independent:
        for signs in product((0, 1), repeat=len(part)):
            if sum(signs) % 2:
                clauses.append(" ".join(("~" if sign else "") + f"x{place}" for sign, place in zip(signs, part, strict=True)))
    return {"visible distinctions": holding, "independent even parities": independent,
            "cnf": "; ".join(clauses)}


def select(panel):
    audit = json.loads((HERE / "sampleaudit.json").read_text())
    failing = audit["admission and overlaps with prior work"]["sample starting admission"][panel]["parity"]["excluded"]
    assert len(failing) == 1
    index, rules = failing[0]["index"], failing[0]["rules failing K2"]
    assert len(rules) == 1
    knot = rules[0]
    stars = next(row["stars"] for row in read_rows(STUDY / archive_name(panel, "parity")) if row["index"] == index)
    projected = project(stars, knot)
    visible = projected["visible distinctions"]
    arguments = ["--cnf", projected["cnf"], "--loops", *(f"x{i}" for i in visible[:-1]),
                 "--contact", f"x{visible[-1]}", "--json"]
    return {"sample": panel, "archive index": index, "starting rule in stored order": knot,
            "holdings": stars, **projected, "arguments": arguments}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("panel", choices=("uniform", "grow7"))
    parser.add_argument("--args", action="store_true", help="emit one argument per line")
    opts = parser.parse_args()
    audit = select(opts.panel)
    if opts.args:
        print("\n".join(audit["arguments"]))
    else:
        destination = HERE / f"sampleaudit_knot_{opts.panel}_input.json"
        destination.write_text(json.dumps(audit, indent=2) + "\n")
        print(destination.name)
