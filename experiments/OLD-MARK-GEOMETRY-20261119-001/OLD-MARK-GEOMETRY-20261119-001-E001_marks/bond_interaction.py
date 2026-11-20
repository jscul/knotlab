"""Bound later two-load interactions on old pairs spanning both attachments."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path

from bond_age_two import solve_frame
from bond_distances import OUTPUT, Wiring, bitset, reached
from bond_later import PinFlow, initial_rows
import sources
import world_ring_distance_dp as partitions


STRADDLING = ((3, 8), (3, 7), (4, 7), (2, 9))
FLOW_LIMIT = 1500
SECONDS_PER_FRAME = 14


def nearby_witnesses(wire, pair, left, right, known, local, path, background, seams):
    """Try the original interval with previously verified local pieces substituted."""
    table = {tuple(row[:2]): bitset(local["witnesses"][row[4]]["knots"]) for row in local["pairs"]}
    options = {known, bitset(background[left + 1:right + 1])}
    for seam in seams:
        index = background.index(seam)
        adjacent = tuple(sorted(path[index - 1:index + 1]))
        crossing = tuple(sorted((path[index - 2], path[index + 1])))
        local_old = bitset(background[index - 1:index + 2])
        added = set()
        for mask in options:
            if mask & (1 << seam):
                added.add(mask | table[adjacent])
            if mask & local_old == local_old:
                added.add((mask & ~local_old) | table[crossing])
        options |= added
    ranked = []
    for mask in options:
        if not all(((mask >> u) ^ (mask >> v)) & 1 for u, v in map(wire.edge.__getitem__, pair)):
            continue
        outside = wire.full ^ mask
        if (reached(mask & -mask, mask, wire.neighbors) == mask and
                reached(1 << wire.exterior, outside, wire.neighbors) == outside):
            ranked.append((len(wire.witness(mask, pair)["distinctions"]), mask))
    return min(ranked)[1]


def two_ring_case(spec, initial, later):
    path = spec["roles"]["anchors"]
    background = spec["roles"]["background"]
    seams = spec["roles"]["seams"]
    receiver = background.index(seams[1])
    indices = [(i, j + receiver - 8) for i, j in STRADDLING]
    marks = [tuple(sorted((path[i], path[j]))) for i, j in indices]
    all_arms = {}
    for code, occupied in sources.loads(spec).items():
        source_seeds = initial_rows(initial, occupied)
        seeds = {pair: source_seeds[pair] for pair in marks}
        stages = {}
        for age, frame in sources.generate(spec, occupied, 4):
            if age < 2:
                continue
            wire = Wiring(frame["stars"])
            local = later[code]["frames"][str(age)]
            for (i, j), pair in zip(indices, marks, strict=True):
                seeds[pair] = nearby_witnesses(wire, pair, i, j, seeds[pair], local, path, background, seams)
            separated = solve_frame(wire, marks, seeds, None, SECONDS_PER_FRAME)
            table = {tuple(row[:2]): row[2:] for row in separated["pairs"]}
            caps = {tuple(row[:2]): row[2] for row in separated["caps"]}
            flow = PinFlow(wire) if caps else None
            readings = []
            for (i, j), pair in zip(indices, marks, strict=True):
                if pair in table:
                    value, proof, transitions = table[pair]
                    witness = separated["witnesses"][proof]
                    lo = hi = value
                    computation = {"method": "separator", "transitions": transitions}
                else:
                    lo, hi, _, witness, runs = flow.solve(pair, seeds[pair], FLOW_LIMIT)
                    computation = {"method": "integer flow", "relaxations": runs,
                                   "separator_cap": caps[pair]}
                seeds[pair] = bitset(witness["knots"])
                readings.append({"marks": list(pair), "indices": [i, j],
                                 "bounds": [lo, hi], "witness": witness, **computation})
            stages[str(age)] = {"knots": wire.n, "distinctions": len(wire.edge),
                                "tested_width": separated["tested_width"], "readings": readings}
            print(spec["id"], code, age, [(read["indices"], read["bounds"]) for read in readings], flush=True)
        all_arms[code] = stages
    interaction = {}
    for age in all_arms["0"]:
        rows = []
        for i, pair in enumerate(indices):
            (q0, q1), (a0, a1), (b0, b1), (c0, c1) = [
                all_arms[arm][age]["readings"][i]["bounds"] for arm in ("0", "1", "2", "3")]
            bounds = [c0 - a1 - b1 + q0, c1 - a0 - b0 + q1]
            rows.append({"indices": list(pair), "interaction_bounds": bounds,
                         "nonzero": bounds[1] < 0 or bounds[0] > 0})
        interaction[age] = rows
    return {"arms": all_arms, "interactions": interaction}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=("T4", "T8"), default=["T4"])
    parser.add_argument("--first", type=Path, default=OUTPUT / "bond_first.json")
    parser.add_argument("--later", type=Path, default=OUTPUT / "bond_later.json")
    parser.add_argument("--out", type=Path, default=OUTPUT / "bond_interaction.json")
    args = parser.parse_args()
    partitions.WIDTH_LIMIT = 14
    earlier = args.first.read_bytes()
    nearby = args.later.read_bytes()
    read = json.loads(earlier)["cases"]
    local = json.loads(nearby)["cases"]
    result = {case: two_ring_case(sources.cases()[case], read[case], local[case]) for case in args.cases}
    args.out.write_text(json.dumps({"schema": 1, "unit": "bond size minus one",
                                    "first_sha256": sha256(earlier).hexdigest(),
                                    "named_sha256": sha256(nearby).hexdigest(),
                                    "flow_limit_per_query": FLOW_LIMIT,
                                    "separator_width_ceiling": partitions.WIDTH_LIMIT,
                                    "separator_seconds_per_frame": SECONDS_PER_FRAME,
                                    "cases": result}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
