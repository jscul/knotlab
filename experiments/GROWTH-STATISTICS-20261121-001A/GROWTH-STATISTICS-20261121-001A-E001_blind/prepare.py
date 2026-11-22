"""Read a frozen, custodian-only draw and prepare title-free observations."""

import argparse
import hashlib
import hmac
import json
import os
import platform
import random
import resource
import secrets
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import scipy
import pysat

from bonds import CycleBonds, NAEBonds
from sources import ROOT, cubic_pattern, distances, fold_pattern, load_record, planar_pattern


HERE = Path(__file__).resolve().parent
RADII = (8, 12, 18, 26)
SHAPE_RADII = (14, 23, 37)
FAMILIES = ("cubic", "pinwheel", "periodic", "bounded")
CLASSES = {
    "cubic": {"meeting_dimension": 3, "bond_dimension": 3, "shape": None, "bounded_bond": False},
    "pinwheel": {"meeting_dimension": 2, "bond_dimension": 2, "shape": "round", "bounded_bond": False},
    "periodic": {"meeting_dimension": 2, "bond_dimension": 2, "shape": "polygonal", "bounded_bond": False},
    "bounded": {"meeting_dimension": 2, "bond_dimension": None, "shape": None, "bounded_bond": True},
}
DEPTHS = {"cubic": 50, "pinwheel": 8, "periodic": 16}
ARTIFACT = ROOT / "artifacts" / HERE.parent.name / HERE.name
READER = ROOT / "research" / "GROWTH-STATISTICS-20261121-001" / "blind_reader.py"


def derive(seed, *labels):
    return hmac.digest(seed, "\x00".join(map(str, labels)).encode(), "sha256")


def random_stream(seed, *labels):
    return random.Random(derive(seed, *labels))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value, private=False):
    mode = 0o600 if private else 0o644
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode), "w") as output:
        json.dump(value, output, ensure_ascii=True, allow_nan=False, indent=None if path.name == "packet.json" else 2)
        output.write("\n")


def materialize(family):
    if family == "cubic":
        pattern, _ = cubic_pattern(DEPTHS[family])
        return pattern
    if family == "bounded":
        return fold_pattern(max(RADII) + 10, 2 * max(RADII) + 18)
    return planar_pattern(family, DEPTHS[family])


def select_roots(pattern, cycle, rng, main_radii=RADII, shape_radii=SHAPE_RADII, count=3):
    margins = distances(pattern.meeting, pattern.truncated)
    required = max(main_radii if cycle is None else (*main_radii, *shape_radii)) + 2
    eligible = [i for i in range(len(pattern.meeting)) if margins.get(i, 0) > required]
    if cycle is not None and eligible:
        depth = {i: min(margins[i], *(cycle.margin[v] for v in cycle.edges[i])) for i in eligible}
        best = max(depth.values())
        eligible = [i for i in eligible if 5 * depth[i] >= 4 * best]
    ordered = rng.sample(eligible, len(eligible))
    roots = []
    for candidate in ordered:
        if all(candidate not in nearby for _, nearby in roots):
            roots.append((candidate, distances(pattern.meeting, [candidate], limit=7)))
            if len(roots) == count:
                return [i for i, _ in roots], margins, len(eligible)
    raise ValueError(f"The fixed root eligibility allowed only {len(roots)} of {count} roots")


def knot_reading(pattern, root):
    def neighbors(knot):
        return {other for distinction in pattern.knots[knot] for other in pattern.owners[distinction]} - {knot}

    result = []
    for center in pattern.owners[root]:
        near = neighbors(center)
        neighbors_of = {knot: neighbors(knot) for knot in near}
        zero_degrees = dict.fromkeys(near, 0)
        shared_counts = Counter()
        adjacent_pairs = 0
        for a, b in combinations(sorted(near), 2):
            shared_count = len((neighbors_of[a] & neighbors_of[b]) - {center})
            shared_counts[shared_count] += 1
            adjacent_pairs += b in neighbors_of[a]
            if shared_count == 0:
                zero_degrees[a] += 1
                zero_degrees[b] += 1
        result.append([len(near), adjacent_pairs, [list(item) for item in sorted(shared_counts.items())],
                       sorted(zero_degrees.values())])
    return sorted(result)


def main_observations(pattern, root, cycle, nae, radii):
    reached = distances(pattern.meeting, [root], limit=max(radii))
    histogram = Counter(reached.values())
    counts = [[r, sum(count for steps, count in histogram.items() if steps <= r)] for r in radii]
    short = cycle.short_bonds(root) if cycle is not None else ()
    witnesses, details = [], []
    for radius in radii:
        began = time.perf_counter()
        tally = Counter()
        found = []
        for target, steps in reached.items():
            if steps != radius:
                continue
            certificate = None
            if nae is not None:
                status, certificate = nae.query(pattern, root, target)
            elif cycle is not None:
                helpers = set(pattern.meeting[root]) | set(pattern.meeting[target])
                candidate = next((support for support in short if target in support and
                                  set(support) - {root, target} <= helpers), None)
                status, certificate = ("certified", {"support": candidate}) if candidate else ("absent", None)
            else:
                # A size-at-most-four cut bond has a chain of at most three elementary squares
                # between its two distinctions. A square takes at most two meeting steps.
                status = "absent" if steps > 6 else "unresolved"
            tally[status] += 1
            if certificate is not None:
                found.append({"target": target, **certificate})
        queried = histogram[radius]
        witnesses.append([radius, queried, tally["certified"]])
        details.append({"r": radius, "queried": queried, "certified": tally["certified"],
                        "absent_in_candidate_family": tally["absent"], "unresolved": tally["unresolved"],
                        "proofs": found, "wall_seconds": time.perf_counter() - began})
    return {"counts": counts, "witnesses": witnesses, "local": knot_reading(pattern, root)}, details


def choose_shape(pattern, root, radius, rng):
    depths = distances(pattern.meeting, [root], limit=radius)
    annulus = sorted(i for i, d in depths.items() if 3 * d >= 2 * radius)
    if len(annulus) < 12:
        return [], len(annulus)
    order = rng.sample(annulus, len(annulus))
    priority = {i: k for k, i in enumerate(order)}
    selected = [order[0]]
    spread = dict.fromkeys(annulus, 2 * radius + 1)
    while len(selected) < 4:
        steps = distances(pattern.meeting, [selected[-1]], limit=2 * radius)
        for candidate in annulus:
            spread[candidate] = min(spread[candidate], steps[candidate])
        selected.append(max(annulus, key=lambda i: (spread[i], -priority[i])))
    selected.extend(rng.sample([i for i in annulus if i not in selected], 8))
    rng.shuffle(selected)
    return selected, len(annulus)


def shape_scale(pattern, cycle, depths, root, radius, rng):
    began = time.perf_counter()
    selected, size = choose_shape(pattern, root, radius, rng)
    details = {"r": radius, "annulus": size, "selected": selected, "pairs": [], "attempted": 0, "fallbacks": 0}
    if selected:
        cropped, mapping = cycle.crop(root, 3 * radius)
        meeting = [[0] * 12 for _ in selected]
        bond = [[0] * 12 for _ in selected]
        searches = {i: distances(pattern.meeting, [i], limit=2 * radius) for i in selected}
        for i, j in combinations(range(len(selected)), 2):
            first, second = selected[i], selected[j]
            steps = searches[first][second]
            exact_steps = steps <= depths[first] + depths[second]
            bond_count = cropped.exact(mapping[first], mapping[second]) if first in mapping and second in mapping else None
            if bond_count is None:
                details["fallbacks"] += 1
                bond_count = cycle.exact(first, second)
            meeting[i][j] = meeting[j][i] = steps if exact_steps else None
            bond[i][j] = bond[j][i] = bond_count
            details["pairs"].append([i, j, meeting[i][j], bond_count])
        details["attempted"] = len(details["pairs"])
        if any(value is None for row in meeting for value in row):
            meeting = None
        if any(value is None for row in bond for value in row):
            bond = None
        for matrix in (meeting, bond):
            if matrix is None:
                continue
            for i, j, k in combinations(range(12), 3):
                a, b, c = sorted((matrix[i][j], matrix[i][k], matrix[j][k]))
                if a <= 0 or c > a + b:
                    raise ValueError("A shape channel did not define a metric")
    else:
        bond = meeting = None
    details["wall_seconds"] = time.perf_counter() - began
    details["meeting_complete"] = meeting is not None
    details["bond_complete"] = bond is not None
    return [radius, bond, meeting], details


def collect(draw, checkpoint_directory):
    packet = {"main": [], "shape": []}
    custody = {}
    for family in FAMILIES:
        start = time.perf_counter()
        pattern = materialize(family)
        cycle = CycleBonds.from_pattern(pattern) if pattern.segments is not None else None
        roots, depths, eligible = select_roots(pattern, cycle, random_stream(draw, "roots", family))
        nae = NAEBonds(max(RADII), random_stream(draw, "periodic states")) if family == "bounded" else None
        family_custody = {"eligibles": eligible, "setup_wall_seconds": time.perf_counter() - start,
                          "source_distinctions": len(pattern.meeting), "roots": []}
        for index, root in enumerate(roots):
            main_id = derive(draw, "id", "main", family, index).hex()[:16]
            main, resolution = main_observations(pattern, root, cycle, nae, RADII)
            main_packet_row = {"id": main_id, **main}
            packet["main"].append(main_packet_row)
            row = {"main_id": main_id, "root": root, "target": CLASSES[family],
                   "source_frontier_steps": depths[root], "witness_attempts": resolution}
            shape_packet_row = None
            if cycle is not None:
                shape_id = derive(draw, "id", "shape", family, index).hex()[:16]
                scales = []
                scale_details = []
                for radius in SHAPE_RADII:
                    reading, detail = shape_scale(pattern, cycle, depths, root, radius,
                                                  random_stream(draw, "shape sample", family, index, radius))
                    scales.append(reading)
                    scale_details.append(detail)
                shape_packet_row = {"id": shape_id, "scales": scales}
                packet["shape"].append(shape_packet_row)
                row.update(shape_id=shape_id, shape_attempts=scale_details)
            family_custody["roots"].append(row)
            write_json(checkpoint_directory / f"root-{main_id}.json", {
                "source": family, "main": main_packet_row, "shape": shape_packet_row, "custody": row,
            }, private=True)
        if nae is not None:
            nae.solver.delete()
        custody[family] = family_custody

    # A failed reading masks the entire same-scale channel, independently of hidden label.
    for index in range(len(SHAPE_RADII)):
        for channel in (1, 2):
            if any(row["scales"][index][channel] is None for row in packet["shape"]):
                for row in packet["shape"]:
                    row["scales"][index][channel] = None
    for panel in packet:
        random_stream(draw, "packet order", panel).shuffle(packet[panel])
    if len({row["id"] for panel in packet.values() for row in panel}) != 18:
        raise ValueError("Anonymous identifiers must be unique and the roster must be complete")
    return packet, custody


def check_frozen():
    freeze_path = HERE / "freeze.json"
    freeze = json.loads(freeze_path.read_text())
    if not all(digest(ROOT / file) == expected for file, expected in freeze["sha256"].items()):
        raise ValueError("A frozen program, contract, or source has changed")
    return digest(freeze_path)


def summarize(packet):
    measure = load_record("fixed_observation_summary", READER).measure_matrix
    shape = []
    for row in packet["shape"]:
        scales = []
        for r, bond, meeting in row["scales"]:
            metrics = ({key: value for key, value in measure(matrix).items() if key not in {"round", "polygonal"}}
                       for matrix in (bond, meeting))
            scales.append([r, *metrics])
        shape.append({"id": row["id"], "scales": scales})
    return {"main": packet["main"], "shape": shape}


def commit_draw(directory):
    freeze = check_frozen()
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    secret = secrets.token_bytes(32)
    secret_path = directory / "seed.bin"
    with os.fdopen(os.open(secret_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb") as handle:
        handle.write(secret)
    commitment = {"freeze_sha256": freeze, "seed_sha256": hashlib.sha256(secret).hexdigest()}
    write_json(directory / "commitment.json", commitment)


def generate(draw_directory, output, authorization):
    freeze = check_frozen()
    commitment_path = draw_directory / "commitment.json"
    commitment = json.loads(commitment_path.read_text())
    approval = json.loads(authorization.read_text())
    bindings = {(authorization.parent / item["path"]).resolve(): item["sha256"]
                for item in approval["input_digests"]}
    if (approval["verdict"] != "PASS" or approval["gate"] != "run_authorization"
            or approval["tier"] not in ("R1", "R2")
            or approval["experiment_id"] != "GROWTH-STATISTICS-20261121-001A-E001"
            or bindings.get(HERE / "freeze.json") != freeze
            or bindings.get(commitment_path) != digest(commitment_path)
            or not all(path.is_file() and digest(path) == expected for path, expected in bindings.items())):
        raise ValueError("The exact frozen preparation and draw need R1 clearance")
    secret = (draw_directory / "seed.bin").read_bytes()
    if (len(secret) != 32 or hashlib.sha256(secret).hexdigest() != commitment["seed_sha256"]
            or freeze != commitment["freeze_sha256"]):
        raise ValueError("The held-back draw no longer matches its commitment")
    memory_limit = resource.getrlimit(resource.RLIMIT_AS)[0]
    cpu_limit = resource.getrlimit(resource.RLIMIT_CPU)[0]
    if (not 0 < memory_limit <= 2_000_000 * 1024 or not 0 < cpu_limit <= 475
            or any(os.environ.get(key) != "1" for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"))):
        raise ValueError("Apply the frozen address-space, CPU and thread caps")
    if (platform.python_version(), np.__version__, scipy.__version__, pysat.__version__) != (
            "3.13.3", "2.3.2", "1.18.1", "1.9.dev15"):
        raise ValueError("A numerical library or interpreter changed since freeze")
    output.mkdir(parents=True, exist_ok=False)
    private = output / "custody"
    private.mkdir(mode=0o700)
    checkpoints = private / "checkpoints"
    checkpoints.mkdir(mode=0o700)
    begin = time.perf_counter()
    cpu = time.process_time()
    receiver = None
    try:
        packet, custody = collect(secret, checkpoints)
        write_json(private / "measurements.json", custody, private=True)
        write_json(output / "summary.json", summarize(packet))
        receiver = output / "packet.json"
        write_json(receiver, packet)
    except BaseException as error:
        write_json(private / "failure.json", {"error": repr(error)}, private=True)
        raise
    finally:
        write_json(private / "runtime.json", {
            "wall_seconds": time.perf_counter() - begin,
            "cpu_seconds": time.process_time() - cpu,
            "process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "pysat": pysat.__version__, "system": platform.system(), "machine": platform.machine(),
            "argv": sys.argv, "authorization_sha256": digest(authorization),
            "packet_sha256": digest(receiver) if receiver is not None and receiver.is_file() else None,
            "limits": {"soft_address_space_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
                       "soft_cpu_seconds": resource.getrlimit(resource.RLIMIT_CPU)[0]},
        }, private=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    commitment = commands.add_parser("commit")
    commitment.add_argument("--draw-directory", type=Path, default=ARTIFACT / "draw")
    run = commands.add_parser("generate")
    run.add_argument("--draw-directory", type=Path, default=ARTIFACT / "draw")
    run.add_argument("--output", type=Path, default=ARTIFACT / "run")
    run.add_argument("--authorization", required=True, type=Path)
    args = cli.parse_args()
    draw = args.draw_directory.resolve()
    if args.command == "commit":
        commit_draw(draw)
    else:
        generate(draw, args.output.resolve(), args.authorization.resolve())


if __name__ == "__main__":
    main()
