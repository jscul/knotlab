"""Certify the final longest-pair ordinary routes from the reached age-six stage."""

from collections import Counter
from hashlib import file_digest, sha256
import gzip
import json
from pathlib import Path

from routes import OUT as PREVIOUS, breadth, incidence
import sources


HERE = Path(__file__).resolve().parent
OUT = PREVIOUS.with_name("last_routes.json")
CONTROLS = (("J1", "0"), ("J1", "1"), ("T8", "0"), ("T8", "1"), ("T8", "2"), ("T8", "3"))


def digest(path):
    with path.open("rb") as file:
        return file_digest(file, "sha256").hexdigest()


def archive_stage(archive, case, code, age):
    record = archive["cases"][case]
    mask = record["assignments"][code]["activity_mask"]
    return record["activity_geometries"][mask]["stages"][str(age)]


def age_six(spec, occupied):
    ancestry = []
    birth_ages = []
    for age, frame in sources.generate(spec, occupied, 6):
        if age == 0:
            ancestry = [{knot} for knot in range(len(frame["stars"]))]
            birth_ages = [0] * len(ancestry)
            continue
        for knot in frame["born"]:
            assert knot == len(ancestry)
            ancestry.append(set.union(*(ancestry[p] for p in frame["parent_sets"][knot])))
            birth_ages.append(age)
    assert age == 6 and len(ancestry) == len(frame["stars"])
    return frame, ancestry, birth_ages


def end_scan(stars, spec):
    graph, nodes, _ = incidence(stars)
    e0, e15 = (nodes[spec["roles"]["anchors"][i]] for i in (0, 15))
    da, wa, _ = breadth(graph, (e0,), count=True)
    db, wb, _ = breadth(graph, (e15,), count=True)
    assert da[e15] == db[e0] == 30 and wa[e15] == wb[e0]
    return da, db, wa, wb, wa[e15]


def exclusive_ancestry(origins, spec):
    roles = spec["roles"]
    background = set(roles["background"])
    return [sorted(origins.intersection(set(ring) - background)) for ring in roles["rings"]]


def proposed(spec, occupied, archive, case, code, literal_control):
    old, ancestry, birth_ages = age_six(spec, occupied)
    prior = archive_stage(archive, case, code, 6)
    assert prior["knots"] == len(old["stars"]) and prior["distinctions"] == old["distinction_count"]
    assert not any(set(old["occupied"]).intersection(old["stars"][knot]) for knot in old["live"])
    da, db, wa, wb, before = end_scan(old["stars"], spec)
    assert before == prior["pairs"][14]["routes"]
    assert (prior["pairs"][14]["i"], prior["pairs"][14]["j"]) == (0, 15)

    # Request only a complete roster and its funding. Do not realize this plan.
    plan = sources.growth.plan_round(old["stars"], old["occupied"], ("P", "V"), caps=None)
    assert plan.status == "extend" and not plan.details["implied_closure"]
    allocation = sources.growth.literal_allocation(plan)
    required = Counter(p for birth in plan.births for p in birth.parents)
    assert required == Counter({p: len(loose) for p, loose in plan.stage.loose.items()})
    used = set()
    for birth, spent in zip(plan.births, allocation, strict=True):
        assert not birth.active and birth.action == "P" and birth.fresh >= birth.demand
        assert len(birth.parents) == len(set(birth.parents)) == len(spent)
        assert all(birth_ages[p] == 6 for p in birth.parents)
        for p, bit in zip(birth.parents, spent, strict=True):
            assert bit in plan.stage.loose[p] and bit not in used
            used.add(bit)
    assert used == {bit for loose in plan.stage.loose.values() for bit in loose}

    eligible = []
    for knot, (birth, spent) in enumerate(zip(plan.births, allocation, strict=True), start=len(ancestry)):
        from_first = [[p, bit, wa[p]] for p, bit in zip(birth.parents, spent, strict=True) if da[p] == 13]
        from_last = [[p, bit, wb[p]] for p, bit in zip(birth.parents, spent, strict=True) if db[p] == 13]
        if not from_first or not from_last:
            continue
        assert not {row[0] for row in from_first} & {row[0] for row in from_last}
        assert min(da[p] for p in birth.parents) == min(db[p] for p in birth.parents) == 13
        origins = set.union(*(ancestry[p] for p in birth.parents))
        contributions = sum(row[2] for row in from_first) * sum(row[2] for row in from_last)
        eligible.append({"prospective_knot_id": knot, "parents": birth.parents,
                         "eligible_parent_spent_distinction_ways_first": from_first,
                         "eligible_parent_spent_distinction_ways_last": from_last,
                         "source_ancestry": sorted(origins), "exclusive_ring_ancestry": exclusive_ancestry(origins, spec),
                         "new_routes": contributions})

    added = sum(group["new_routes"] for group in eligible)
    width = len(plan.stage.names) + sum(birth.fresh for birth in plan.births)
    total_knots = len(plan.stage.stars) + len(plan.births)
    capped = sources.growth.plan_round(old["stars"], old["occupied"], ("P", "V"), caps=sources.DEFAULT_CAPS)
    record = {"age_six_ordinary_routes": before, "new_age_seven_routes": added, "complete_count": before+added,
              "new_routes_through_exclusive_ring_ancestry": sum(group["new_routes"] for group in eligible
                                                                if any(group["exclusive_ring_ancestry"])),
              "projected_age_seven": {"births": len(plan.births), "knots": total_knots, "distinctions": width,
                                     "spent_once": len(used), "funded_parents": len(required),
                                     "materialization_status_under_caps": capped.status},
              "eligible_groups": eligible}
    if literal_control:
        assert capped.status == "extend"
        frame = sources.growth.realize_round(capped)
        assert len(frame["stars"]) == total_knots and frame["distinction_count"] == width
        x, y, wx, wy, literal = end_scan(frame["stars"], spec)
        literal_inc = {knot: wx[knot]*wy[knot] for knot in frame["born"] if x[knot] == y[knot] == 15}
        assert literal_inc == {group["prospective_knot_id"]: group["new_routes"] for group in eligible}
        assert literal == before+added == archive_stage(archive, case, code, 7)["pairs"][14]["routes"]
        record["literal_replay"] = {"age_seven_routes": literal,
                                    "new_midpoint_contributions": literal_inc, "agrees": True}
    else:
        assert capped.status == "distinction_cap" and capped.details["planned_total_distinctions"] == width
        assert capped.details["planned_total_knots"] == total_knots and capped.details["planned_new_knots"] == len(plan.births)
    return record


def main():
    with gzip.open(PREVIOUS, "rt") as file:
        archive = json.load(file)
    specs = sources.cases()
    def score(case, code, literal):
        spec = specs[case]
        return proposed(spec, sources.loads(spec)[code], archive, case, code, literal)
    receipt = {"target": {"source": "T4", "load": "0", **score("T4", "0", False)},
               "controls": {f"{case}/{code}": score(case, code, True) for case, code in CONTROLS},
               "source_sha256": digest(Path(__file__).resolve()), "previous_routes_sha256": digest(PREVIOUS),
               "sources_sha256": digest(HERE/"sources.py"),
               "plan_sha256": sha256(Path(sources.growth.__file__).read_bytes()).hexdigest(),
               "followup_design_sha256": digest(sources.ROOT/"research"/HERE.parent.name/"last_route_design.md")}
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["target"], flush=True)


if __name__ == "__main__":
    main()
