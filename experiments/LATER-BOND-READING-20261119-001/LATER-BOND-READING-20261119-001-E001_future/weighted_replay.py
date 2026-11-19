"""Check exact core readings independently and replay the small changing-cost grafts."""

import argparse
import json
from pathlib import Path
import sys

from weighted_core import ARCHIVE, changed, contains_all, literal_virtual_control, rows_from_weights, xor_bonds


def graft(rows, price):
    """Build disjoint live families attached through the two exhausted terminals."""
    rows = [list(row) for row in rows]
    next_name = 1 + max(x for row in rows for x in row)

    def site():
        rows.append([])
        return len(rows)-1

    def attach(first, second, copies=1):
        nonlocal next_name
        for _ in range(copies):
            rows[first].append(next_name)
            if second is not None:
                rows[second].append(next_name)
            next_name += 1

    if price == 2:
        relay = site()
        both, first, second = site(), site(), site()
        attach(0, relay)
        attach(0, both)
        attach(relay, both)
        attach(0, first, 2)
        attach(relay, second, 2)
        attach(both, None, 2)
        attach(first, None)
        attach(second, None)
    elif price == 3:
        for _ in range(3):
            j = site()
            attach(0, j)
            attach(j, None, 2)
    else:
        raise ValueError("this replay uses the two- and three-place exterior gadgets")
    other = site()
    attach(1, other, price)
    attach(other, None, price)
    return rows


def literal_growth(start):
    sys.path.insert(0, str(ARCHIVE))
    from census import production_law
    from reach_bound import verifier

    v = verifier()
    previous = v.Arrangement.parse(start)
    assert v.start_audit(previous)["census_open_legal"]
    law = production_law()
    growth = law.from_junctions(start)
    stages = [start]
    records = []
    for _ in range(2):
        assert growth.step(law.gf2(law.F.fewest), None)["new"]
        assert growth.implied_mismatch == 0
        stage = [sorted(row) for row in growth.bits_of]
        current = v.Arrangement.parse(stage)
        records.append(v.round_replay(previous, current))
        stages.append(stage)
        previous = current
    return stages, records


def external_separator(stars, core_width):
    exterior = [[name for name in row if name >= core_width] for row in stars]
    proxy = 1 + max(name for row in exterior for name in row)
    assert exterior[0] and exterior[1]
    exterior[0].append(proxy)
    exterior[1].append(proxy)
    bonds = xor_bonds([row for row in exterior if row])
    return contains_all(bonds, [proxy]) - 1


def literal_graft(case, falls_on_triples):
    rows, width = rows_from_weights(case["n"], case["weights"])
    price = case["lambda"]
    stages, records = literal_growth(graft(rows, price))
    measurements = []
    for stars in stages[1:]:
        labels = set().union(*map(set, stars))
        counts = {x: sum(x in row for row in stars) for x in labels}
        live = [row for row in stars if any(counts[x] == 1 for x in row)]
        fixed = sorted({x for row in live for x in row})
        assert min(fixed) >= width
        image = case["image"] + list(range(width, len(labels)))
        bonds = xor_bonds(stars)
        exterior = external_separator(stars, width)
        measurements.append({
            "junctions": len(stars), "distinctions": len(labels), "exterior_minimum": exterior,
            "fixed_live_distinctions": fixed, "literal_bonds": len(bonds),
            "all_pairs": changed(bonds, len(labels), image, 2),
            "all_triples": changed(bonds, len(labels), image, 3),
            "core_pairs": changed(bonds, width, image, 2),
            "core_triples": changed(bonds, width, image, 3),
        })
    assert [row["exterior_minimum"] for row in measurements] == [price, 1]
    if falls_on_triples:
        assert measurements[0]["all_pairs"]["changed"] == measurements[0]["all_triples"]["changed"] == 0
        assert measurements[1]["core_triples"]["changed"] > 0
    else:
        assert measurements[0]["all_pairs"]["changed"] == 0
        assert measurements[0]["all_triples"]["changed"] > 0
        assert measurements[1]["core_pairs"]["changed"] > 0
    return {"case": case, "stages": stages, "independent_rounds": records, "measurements": measurements}


def calibration():
    # The literature's diamond, matching the earlier pair-only example.
    case = {"n": 4, "width": 5, "weights": [0, 1, 1, 1, 1, 1], "image": [2, 1, 0, 3, 4]}
    return [literal_graft({**case, "lambda": price}, False) for price in (2, 3)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    scanned = json.loads(args.summary.read_bytes())
    controls = []
    for panel in scanned:
        if witness := panel["first_unrefined_separator_example"]:
            controls.append({"witness": witness, "literal": literal_virtual_control(witness)})
    examples = []
    for panel in scanned:
        for case in panel["breaking_examples"]:
            item = {"case": case, "literal": literal_virtual_control(case)}
            if case["lambda"] in (2, 3):
                item["growth"] = literal_graft(case, True)
            examples.append(item)
    data = {"changing_price_controls": calibration(), "unrefined_controls": controls, "breaking_examples": examples}
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
