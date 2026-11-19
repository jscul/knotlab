"""Replay the marked equation-span census on the archived meet-once population."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = Path("GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds")
BASELINE = ROOT / "artifacts" / ARCHIVE / "census_results.json"
THRESHOLD = ROOT / "artifacts" / ARCHIVE / "reach_bound_threshold.json"
CPP = HERE / "carry_census.cpp"
SHARD = 96
CURRENT_LIMIT = 16
METHODS = (
    "fixed", "pooled_pair_certificate", "exact_pair_certificate", "pooled_triple_certificate",
    "exact_triple_certificate", "noncarrying_exact_triple_group",
)
EXISTENCE_METHODS = (*METHODS[:3], "triple_existence_certificate", "noncarrying_triple_existence_group")


def load(path):
    return json.loads(path.read_bytes())


def native(binary, *args, text):
    return subprocess.run([binary, *map(str, args)], input=text, text=True, capture_output=True, check=True).stdout


def setup(params):
    global binary, roster, roster_digest, reading
    binary = params["engine"]
    reading = params.get("reading", "minimum")
    assert reading in ("minimum", "existence")
    external = Path(params["roster"]).read_bytes()
    roster_digest = sha256(external).hexdigest()
    (baseline_inputs,) = load(BASELINE)["inputs"]
    assert roster_digest == baseline_inputs["roster_sha256"], "this is a different starting roster"
    assert baseline_inputs["starting_widths"] == [3, 15]
    assert baseline_inputs["current_site_cap"] == CURRENT_LIMIT
    all_rows = external.decode("ascii").splitlines()
    assert len(all_rows) == baseline_inputs["starts"]
    roster = [(i, line) for i, line in enumerate(all_rows) if line.split()[2] == "1"]


def cases():
    for start in range(0, len(roster), SHARD):
        yield f"carry-{start // SHARD:04d}", [start, min(start + SHARD, len(roster))]


def run(case_id, payload):
    start, stop = payload
    inputs = "".join(f"{index} {line}\n" for index, line in roster[start:stop])
    mode = "audit-existence" if reading == "existence" else "audit"
    result = [json.loads(line) for line in native(binary, mode, CURRENT_LIMIT, text=inputs).splitlines()]
    assert sum(row["counts"]["starts"] for row in result if "origin" in row) == stop - start, case_id
    return result


def prepare(folder):
    folder.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-B", str(ROOT / "experiments" / ARCHIVE / "census.py"),
                    "prepare", str(folder), "--width", "15"], check=True)
    target = folder / "carry_census"
    subprocess.run(["c++", "-std=c++20", "-O3", "-Wno-return-type", str(CPP), "-o", str(target)], check=True)
    print(target)


def closure(generators, width):
    identity = tuple(range(width))
    group = {identity}
    frontier = [identity]
    while frontier:
        left = frontier.pop()
        for right in generators:
            image = tuple(left[i] for i in right)
            if image not in group:
                group.add(image)
                frontier.append(image)
    return group


def literal_reference(rows, engine, source_image=None):
    # The archived Python reference obtains support-minimal parity words
    # directly, then lists every pair-table map without a stabilizer chain.
    archive_path = str(ROOT / "experiments" / ARCHIVE)
    if archive_path not in sys.path:
        sys.path.insert(0, archive_path)
    from readings import all_mappings, bond_readings
    from verify import Arrangement

    current = Arrangement.parse(rows)
    (_, pairs, triples), bonds, span = bond_readings(current)
    labels = list(current.labels)
    assert labels == list(range(len(labels)))
    fixed = set().union(*(current.stars[j] for j in current.live))
    native_input = "\n".join([str(len(rows)), *(" ".join(map(str, (len(row), *row))) for row in rows)]) + "\n"
    answer = json.loads(native(engine, "literal", text=native_input))
    names = answer["current_names_to_literal_names"]
    movable_count = answer["movable"]
    assert set(names[movable_count:]) == fixed and set(names) == set(labels)
    for table, key, count in ((pairs, "pair_K", 2), (triples, "triple_K", 3)):
        scalar = [table[tuple(sorted(xs))] for xs in combinations(names, count)]
        assert answer[key] == [9999 if value is None else value + 1 for value in scalar]

    def equation_mismatch(image):
        for row in current.stars:
            support = sorted(image[x] for x in row)
            if sum(current.label_bits[y] for y in support) not in span:
                return {"support": sorted(row), "image": support}
        return None

    def first_triple_mismatch(image, existence=False):
        for names, value in triples.items():
            renamed = tuple(sorted(image[x] for x in names))
            target = triples[renamed]
            matches = (value is None) == (target is None) if existence else value == target
            if not matches:
                return {"triple": names, "image": renamed, "bond_distances": [value, target]}
        return None

    pair_group = {
        tuple(image[x] for x in labels) for image in all_mappings(labels, pairs, fixed)
    }
    triple_group = {image for image in pair_group if first_triple_mismatch(image) is None}
    existence_group = {image for image in pair_group if first_triple_mismatch(image, existence=True) is None}

    def original_image(permutation):
        mapped = list(labels)
        for b, target in enumerate(permutation):
            mapped[names[b]] = names[target]
        return tuple(mapped)

    reports = {}
    for name, expected in (("pair", pair_group), ("existence", existence_group), ("triple", triple_group)):
        representatives = [original_image(p) for p in answer[f"{name}_representatives"]]
        assert closure(representatives, len(labels)) == expected
        assert sum(equation_mismatch(p) is not None for p in representatives) == answer[f"noncarrying_{name}_generators"]
        noncarrying = sorted(p for p in expected if equation_mismatch(p) is not None)
        reports[name] = {"isometries": len(expected), "noncarrying_isometries": len(noncarrying),
                         "first_noncarrying_isometry": noncarrying[0] if noncarrying else None}

    # Grade all flips independently from columns of the literal equations.
    owners = {x: current.owners[x] for x in labels}
    flips = [(x, y) for x, y in combinations(labels, 2) if owners[x] == owners[y]]
    assert all({x, y} <= fixed for x, y in flips)
    result = {"junctions": len(rows), "width": len(labels), "bonds": len(bonds), "span_words": len(span),
              "pair_entries": len(pairs), "triple_entries": len(triples), "positive_flips_fixed": len(flips),
              "census_method": answer["census_method"], "groups": reports}
    if source_image is not None:
        source_image = tuple(source_image)
        assert source_image in pair_group
        result["specified_map"] = {"image": source_image, "preserves_pairs": True,
                                   "first_triple_mismatch": first_triple_mismatch(source_image),
                                   "first_triple_existence_mismatch": first_triple_mismatch(source_image, existence=True),
                                   "equation_mismatch": equation_mismatch(source_image)}
    return result


def archived_controls(engine):
    cases = []
    for stage in load(BASELINE)["stages"]:
        if "witness" in stage:
            record = stage["witness"]
            width = len(set().union(*map(set, record["current"])))
            partial = record["old_movable_permutation"]
            cases.append((f"starting_census_w{stage['key'][0]}_age{stage['key'][4]}", BASELINE,
                          record["current"], partial + list(range(len(partial), width))))
    for record in load(THRESHOLD)["joint_minimum_audit"]["failing_allocations"]:
        partial = record["old_movable_permutation"]
        cases.append((f"joint_minimum_{record['allocation_index']}", THRESHOLD,
                      record["current"], partial + list(range(len(partial), 23))))
    cases.append(("parallel_fixed_distinctions", None, [[0, 1, 2], [0, 3, 4]], None))
    assert len(cases) == 6
    result = {}
    for name, source, rows, image in cases:
        result[name] = literal_reference(rows, engine, image)
        if source is not None:
            result[name]["source"] = str(source.relative_to(ROOT))
            result[name]["source_sha256"] = sha256(source.read_bytes()).hexdigest()
            assert result[name]["specified_map"]["equation_mismatch"] is not None
    return result


def residual_controls(engine, result):
    sys.path.insert(0, str(ROOT / "experiments" / ARCHIVE))
    from census import literal_stages, production_law
    from reach_bound import same_arrangement, verifier

    law, reference = production_law(), verifier()
    checked = []
    existence = result["triple_reading"] == "existence"
    rows = result["existence_counterexamples"][:1] if existence else result["full_triple_cases"]
    for case in rows:
        label = "existence_counterexample" if existence else "full_triple_case"
        index, age = case[label]
        names = case["current_names_to_growth_names"]
        literal = literal_stages(law, case["start"], age)[-1]
        rebased = [[names[x] for x in row] for row in case["current"]]
        # The independent grower may name equivalent loose distinctions in a
        # different order. Compare exact junction incidence up to renaming.
        independent = reference.Arrangement.parse([list(row) for row in literal])
        assert same_arrangement(independent, reference.Arrangement.parse(rebased)), (index, age)
        partial = case["noncarrying_movable_permutation"]
        image = partial + list(range(len(partial), len(names))) if partial else None
        audit = literal_reference(case["current"], engine, image)
        assert bool(audit["groups"]["existence" if existence else "triple"]["noncarrying_isometries"]) == bool(partial)
        assert audit["groups"]["pair"]["noncarrying_isometries"] > 0
        if existence:
            check = audit["specified_map"]
            assert check["first_triple_existence_mismatch"] is None
            assert check["equation_mismatch"] is not None
        else:
            assert audit["census_method"]["exact_triple_generators_examined"] == case["stabilizer_generators"]
        checked.append({"case": [index, age], **audit})
    return checked


def smallest_growth_trace(old_engine, result):
    sys.path.insert(0, str(ROOT / "experiments" / ARCHIVE))
    from census import holders, literal_stages, literal_table, production_law

    first = result["existence_counterexamples"][0]
    stage = first["current"]
    incidence = holders(stage)
    old_width = len(incidence)
    partial = first["noncarrying_movable_permutation"]
    image = partial + list(range(len(partial), old_width))
    anchors = {owners[0]: name for name, owners in enumerate(incidence) if len(owners) == 1}
    parents = {
        j: sorted(next(i for i in incidence[name] if i != j) for name in stage[j] if name != wire)
        for j, wire in anchors.items()
    }
    assert len(anchors) == 2
    first_parent_set, second_parent_set = map(set, parents.values())
    assert first_parent_set.isdisjoint(second_parent_set)
    assert not first_parent_set.intersection(anchors) and not second_parent_set.intersection(anchors)
    families = anchors.copy()
    trace = []
    for age, rows in enumerate(literal_stages(production_law(), stage, 3)):
        table = literal_table(old_engine, rows)
        width = len(holders(rows))
        transported = image + list(range(old_width, width))
        assert all(value == table[tuple(sorted((transported[a], transported[b])))] for (a, b), value in table.items())
        if age:
            for j, row in enumerate(rows[len(previous):], start=len(previous)):
                routes = {families[incidence[name][0]] for name in row if name < len(incidence)}
                assert len(routes) == 1
                families[j] = routes.pop()
        incidence = holders(rows)
        previous = rows
        trace.append({"rounds_after_observation": age, "junctions": len(rows), "width": width,
                      "pair_entries_checked": len(table), "permutes_all_pair_readings_fixing_fresh": True})
    return {"case": first["existence_counterexample"], "anchors_by_junction": anchors,
            "old_neighbors_by_anchor_junction": parents, "trace": trace}


def add_stage_counts(counter, extra):
    for key, value in extra.items():
        if key == "max_current_width":
            counter[key] = max(value, counter[key])
        else:
            counter[key] += value


def merge(runner_out):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    job = load(runner_out / "job.json")
    setup(job["params"])
    existence = reading == "existence"
    label = "existence_counterexample" if existence else "full_triple_case"
    blocks = load_results(runner_out)
    expected = {name for name, _ in cases()}
    assert set(blocks) == expected
    assert all(block["status"] == "ok" for block in blocks.values())
    origins, stages = defaultdict(Counter), defaultdict(Counter)
    residuals = []
    for name in sorted(blocks):
        for row in blocks[name]["result"]:
            if "origin" in row:
                origins[tuple(row["origin"])].update(row["counts"])
            elif "stage" in row:
                add_stage_counts(stages[tuple(row["stage"])], row["counts"])
            else:
                assert label in row
                residuals.append(row)

    baseline = load(BASELINE)
    expected_origins = {tuple(row["key"][:3]): row["counts"] for row in baseline["origins"] if row["key"][3]}
    expected_stages = {tuple(row["key"][:3] + row["key"][4:]): row["counts"]["stages"]
                       for row in baseline["stages"] if row["key"][3]}
    assert dict(origins) == expected_origins
    assert {key: count["stages"] for key, count in stages.items()} == expected_stages
    methods = EXISTENCE_METHODS if existence else METHODS
    assert all(count["stages"] == sum(count[k] for k in methods) for count in stages.values())
    by_age, total = defaultdict(Counter), Counter()
    for (_, _, _, age, _), count in sorted(stages.items()):
        add_stage_counts(by_age[age], count)
        add_stage_counts(total, count)
    assert len({tuple(c[label]) for c in residuals}) == len(residuals)
    bad = "noncarrying_triple_existence" if existence else "noncarrying_exact_triple"
    assert sum(c["noncarrying_generators"] for c in residuals) == total[f"{bad}_generators"]
    assert sum(bool(c["noncarrying_movable_permutation"]) for c in residuals) == total[f"{bad}_group"]
    if not existence:
        assert len(residuals) == total["exact_triple_certificate"] + total["noncarrying_exact_triple_group"]
        assert sum(c["stabilizer_generators"] for c in residuals) == total["exact_triple_generators_examined"]
    residuals.sort(key=lambda c: (len(c["current"]), len(c["current_names_to_growth_names"]), c[label]))
    residual_key = "existence_counterexamples" if existence else "full_triple_cases"
    result = {"freeze": "324a407ca", "baseline": str(BASELINE.relative_to(ROOT)),
              "baseline_sha256": sha256(BASELINE.read_bytes()).hexdigest(), "roster_sha256": roster_digest,
              "starting_widths": [3, 15], "current_junction_cap": CURRENT_LIMIT, "valid_shards": len(blocks),
              "admissible_starts": sum(row["starts"] for row in origins.values()),
              "summary": dict(total), "stages_by_age": dict(sorted(by_age.items())),
              "ungraded_stages": 0, "triple_reading": reading, residual_key: residuals,
              "noncarrying_witnesses": [c[label] for c in residuals if c["noncarrying_movable_permutation"]],
              "stages": [{"key": key, "counts": value} for key, value in sorted(stages.items())]}
    return result


def save(result, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", dir=destination.parent, delete=False) as pending:
        json.dump(result, pending, indent=2)
        pending.write("\n")
        temporary = Path(pending.name)
    temporary.replace(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    methods = parser.add_subparsers(dest="mode", required=True)
    methods.add_parser("prepare").add_argument("folder", type=Path)
    methods.add_parser("controls").add_argument("engine", type=Path)
    residuals = methods.add_parser("residuals")
    residuals.add_argument("engine", type=Path)
    residuals.add_argument("summary", type=Path)
    trace = methods.add_parser("trace")
    trace.add_argument("archived_engine", type=Path)
    trace.add_argument("existence_summary", type=Path)
    collect = methods.add_parser("collect")
    collect.add_argument("runner_out", type=Path)
    collect.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.folder)
    elif args.mode == "controls":
        print(json.dumps(archived_controls(args.engine), indent=2))
    elif args.mode == "residuals":
        print(json.dumps(residual_controls(args.engine, load(args.summary)), indent=2))
    elif args.mode == "trace":
        print(json.dumps(smallest_growth_trace(args.archived_engine, load(args.existence_summary)), indent=2))
    else:
        result = merge(args.runner_out)
        save(result, args.output)


if __name__ == "__main__":
    main()
