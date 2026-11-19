"""Frozen two-block prefix extension on the thirteen other unread histories."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import prod
from pathlib import Path
from random import Random
import subprocess
import sys
import tarfile
from tempfile import NamedTemporaryFile, TemporaryDirectory

from birth_corrections import correction
from group_profile import Stage, members, pack
from stages import DEFAULT, ARTIFACTS, HERE, ROOT, digest, write_at


SEED = 202611238000
ORDER_SEED = 73121
POPULATION = 128
REPLICATES = 16
OUTSIDERS = 14
NEAR = ("start-02", "start-05", "start-08")
SOURCE = "NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/sequential.cpp"
WORK = DEFAULT / "prefix-targets"
INPUTS = None
ONLY = ()
EXCLUDE = ()


def build(work):
    """Freeze the actual three source files used by both index widths."""
    folder = work / "engine"
    folder.mkdir(parents=True, exist_ok=True)
    shared = {name: (HERE / name).read_text() for name in ("anneal.cpp", "anneal_prefix.hpp")}
    reference = (ROOT / "experiments" / SOURCE).read_text()
    include = f'"../../{SOURCE}"'
    assert shared["anneal.cpp"].count(include) == 1 and reference.count("using Id = std::uint16_t;") == 1
    snapshot = {**shared, "sequential.cpp": reference}
    builds = {}
    for bits in (16, 32):
        target = folder / str(bits)
        target.mkdir(exist_ok=True)
        (target / "anneal.cpp").write_text(shared["anneal.cpp"].replace(include, '"sequential.cpp"'))
        (target / "anneal_prefix.hpp").write_text(shared["anneal_prefix.hpp"])
        source = reference.replace("using Id = std::uint16_t;", f"using Id = std::uint{bits}_t;")
        (target / "sequential.cpp").write_text(source)
        binary = target / "anneal"
        subprocess.run(["c++", "-O3", "-march=native", "-std=c++20", "-Wno-return-type",
                        str(target / "anneal.cpp"), "-o", str(binary)], check=True)
        subprocess.run([binary, "--self-test"], check=True, stdout=subprocess.DEVNULL)
        builds[str(bits)] = digest(binary)
    result = {"source_sha256": {name: sha256(content.encode()).hexdigest() for name, content in snapshot.items()},
              "binary_sha256": builds}
    write_at(folder / "build.json", lambda f: json.dump(result, f, sort_keys=True, indent=2))
    return result


def true_twins(stage):
    """Compare full closed neighborhoods in every candidate hash bucket."""
    known = {}
    buckets = defaultdict(list)
    labels = []
    representatives = []
    for u, profile in enumerate(stage.at):
        if profile in known:
            labels.append(known[profile])
            continue
        closed = stage.hood(profile) if profile else 1 << u
        key = (closed.bit_count(), hash(closed))
        for i in buckets[key]:
            v = representatives[i]
            other = stage.hood(stage.at[v]) if stage.at[v] else 1 << v
            if closed == other:
                break
        else:
            i = len(representatives)
            representatives.append(u)
            buckets[key].append(i)
        if profile:
            known[profile] = i
        labels.append(i)
    return labels, representatives


def export_quotient(stage, output):
    labels, representatives = true_twins(stage)
    n = len(representatives)
    blocks = sorted({pack((labels[v] for v in members(bl)), n) for bl in stage.blocks},
                    key=lambda m: (-m.bit_count(), m))
    largest = []
    for block in blocks:
        if block.bit_count() < 2:
            break
        if not any(block & v == block for v in largest):
            largest.append(block)

    def put(f):
        print(n, len(largest), file=f)
        for block in largest:
            print(" ".join(map(str, members(block))), file=f)

    fingerprint = write_at(output, put)
    path = output.with_suffix(".map.json.gz")
    mapping = write_at(path, lambda f: json.dump(labels, f, separators=(",", ":")), compressed=True)
    return n, {"literal": stage.n, "quotient": n, "quotient_blocks": len(largest),
               "roster_sha256": fingerprint, "literal_to_quotient_sha256": mapping,
               "quotient_file": output.name, "map_file": path.name,
               "twin_class_multiplicities": dict(sorted(Counter(Counter(labels).values()).items()))}


def prefix_ranker(stage, cap=OUTSIDERS):
    # Reduction and ties are deterministic in the quotient names.
    block = stage.blocks[0] if stage.blocks else 1
    other = next((b for b in stage.blocks[1:] if b & ~block), 0)
    inside = tuple(members(block))
    outsiders, exclusions, distinct = [], [], set()
    for u in members(other & ~block):
        miss = block & ~stage.hood(stage.at[u])
        if miss not in distinct:
            distinct.add(miss)
            outsiders.append(u)
            exclusions.append(miss)
        if len(outsiders) == cap:
            break

    width = (stage.n + 7) // 8
    packed = [m.to_bytes(width, "little") for m in exclusions]
    patterns = {}
    inside_types = []
    for u in inside:
        signature = sum(((data[u >> 3] >> (u & 7)) & 1) << j for j, data in enumerate(packed))
        position = patterns.setdefault(signature, len(patterns))
        inside_types.append(1 << position)
    excluded = [sum(1 << j for sig, j in patterns.items() if (sig >> i) & 1) for i in range(len(outsiders))]
    unions = {0}
    for mask in excluded:
        unions.update({previous | mask for previous in unions})
    ordered = sorted(unions)

    def decode(rank):
        union = ordered[rank]
        retained = [u for u, kind in zip(inside, inside_types, strict=True) if not (kind & union)]
        retained.extend(u for u, mask in zip(outsiders, excluded, strict=True) if mask & union == mask)
        return retained

    prefix = (*inside, *outsiders)
    metadata = {"largest_block": len(inside), "second_block": other.bit_count(), "outsiders": outsiders,
                "initial_joint_roster_size": len(prefix), "inside_exclusion_classes": len(patterns),
                "exact_initial_maximal_cliques": len(ordered)}
    return prefix, len(ordered), decode, metadata


def write_bank(path, prefix, count, decode, seed):
    def write(f):
        print(len(prefix), *prefix, file=f)
        for rep in range(REPLICATES):
            rng = Random(f"hub-two-block-prefix-v1:{seed + rep}")
            print(count, 1, file=f)
            for _ in range(POPULATION):
                clique = decode(rng.randrange(count))
                print(len(clique), " ".join(map(str, clique)), file=f)
    return write_at(path, write)


def estimate(row):
    numerator, denominator = map(int, row["exact_initial_mass"])
    size = row["resample_denominator"]
    factors = row["resample_numerators"]
    return Fraction(numerator * row["final_mass"] * prod(factors), denominator * size**(1 + len(factors)))


def quantile(rows, q):
    ordered = sorted(rows)
    rank = (len(ordered) - 1) * q
    i = rank.numerator // rank.denominator
    fraction = rank - i
    return ordered[i] if not fraction else ordered[i] + fraction * (ordered[i + 1] - ordered[i])


def report_number(x):
    if abs(x) < 10**250 and (not x or abs(x) > Fraction(1, 10**250)):
        return format(float(x), ".10g")
    from decimal import Decimal, localcontext
    with localcontext() as context:
        context.prec = 10
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def panel_stats(values):
    lo = quantile(values, Fraction(1, 40))
    hi = quantile(values, Fraction(39, 40))
    return {"mean": report_number(sum(values) / len(values)),
            "empirical_central_95": [report_number(x) for x in (lo, hi)],
            "empirical_factor": None if lo <= 0 else report_number(hi / lo),
            "nonpositive": sum(x <= 0 for x in values), "replicates": len(values)}


def setup(params):
    global WORK, INPUTS, ONLY, EXCLUDE
    WORK = Path(params.get("work", WORK))
    INPUTS = Path(params.get("inputs", DEFAULT))
    ONLY = tuple(filter(None, params.get("only", "").split(",")))
    EXCLUDE = tuple(filter(None, params.get("exclude", "").split(",")))


def all_cases():
    directory = INPUTS or DEFAULT
    data = json.loads((directory / "index.json").read_text())
    targets = {r["case"]: r for r in data["stages"] if r["role"] == "first_unread" and r["case"] != "start-03"}
    assert len(targets) == 13
    for case in (*NEAR, *(k for k in sorted(targets) if k not in NEAR)):
        yield case, targets[case]


def cases():
    yield from ((case, row) for case, row in all_cases() if (not ONLY or case in ONLY) and case not in EXCLUDE)


def run(case, meta, *, control_seed=None):
    directory = INPUTS or DEFAULT
    literal = directory / meta["files"]["blocks"]["name"]
    assert digest(literal) == meta["files"]["blocks"]["sha256"]
    path = WORK / f"{case}-age{meta['age']:02d}"
    path.mkdir(parents=True, exist_ok=True)
    quotient_file = path / "quotient.txt"
    classes, quotient = export_quotient(Stage(literal), quotient_file)
    # Drop method-local row caches before allocating the native graph.
    Stage.hood.cache_clear()
    prefix, count, decode, ranker = prefix_ranker(Stage(quotient_file))
    seed = control_seed if control_seed is not None else SEED + 64 * int(case[-2:])
    bank = path / "bank.txt"
    bank_hash = write_bank(bank, prefix, count, decode, seed)
    Stage.hood.cache_clear()
    known_births = None
    if control_seed is not None:
        known = meta["truth"]
        known_births = known["births"]
        correction_term = meta["exact_offshoots"] - known["held_maximal_cliques"] - meta["isolated"]
        audit = {"raw_maximum_to_birth_term": correction_term, "easy_residual_pairs": 0,
                 "nontrivial_candidate_pairs": 0, "exact_residual": known["residual_pairs"],
                 "held": known["held_maximal_cliques"], "isolated": meta["isolated"], "offshoots": meta["exact_offshoots"]}
        assert known["raw_maximal_cliques"] + correction_term + known["residual_pairs"] == known_births
    elif case in NEAR:
        near = json.loads((ARTIFACTS / "near_block_02.json").read_text())
        assert near["exact_count"]["next_births"] == 1061953
        assert near["exact_count"]["raw_maximal_cliques"] == 1061954
        known_births = near["exact_count"]["next_births"]
        audit = {"raw_maximum_to_birth_term": -1, "easy_residual_pairs": 0,
                 "nontrivial_candidate_pairs": 0, "exact_residual": 0, "held": 1, "isolated": 0, "offshoots": 0}
    else:
        audit = correction(directory, literal.stem, draws=0, batches=0)
        Stage.hood.cache_clear()
    width = 16 if classes <= 65535 else 32
    binary = WORK / "engine" / str(width) / "anneal"
    arguments = [binary, quotient_file, "degree-up", str(ORDER_SEED), str(POPULATION), str(seed),
                 str(REPLICATES), "0", "0", "0", "0", bank]
    raw = path / "raw.jsonl"
    errors = path / "native.stderr"
    fields = {"case": case, "age": meta["age"], "target_round": meta["target_round"], "seed": seed,
              "input_sha256": digest(literal), "quotient": quotient, "ranker": ranker, "bank_sha256": bank_hash,
              "integer_id_width": width, "population": POPULATION, "replicates_requested": REPLICATES,
              "birth_correction": audit}
    write_at(path / "settings.json", lambda f: json.dump(fields, f, indent=2, sort_keys=True))
    with raw.open("w") as out, errors.open("w") as err:
        process = subprocess.run(arguments, stdout=out, stderr=err, check=False)
    log = [json.loads(s) for s in raw.read_text().splitlines()]
    if process.returncode or len(log) != REPLICATES + 1:
        return {**fields, "status": "native_incomplete", "exit": process.returncode,
                "rows_read": max(0, len(log) - 1), "partial_native_rows": log,
                "native_stderr": errors.read_text()[-2000:]}
    header, *observations = log
    return summarize(fields, header, observations, known_births)


def summarize(fields, header, observations, known_births=None):
    classes = fields["quotient"]["quotient"]
    prefix = fields["ranker"]["initial_joint_roster_size"]
    assert header["classes"] == classes and header["limit"] == classes and header["seeded_prefix_classes"] == prefix
    seed = fields["seed"]
    assert [r["seed"] for r in observations] == list(range(seed, seed + REPLICATES))
    assert all(r["resample_denominator"] == POPULATION
               and r["exact_initial_mass"] == [str(fields["ranker"]["exact_initial_maximal_cliques"]), "1"]
               for r in observations)
    audit = fields["birth_correction"]
    values = list(map(estimate, observations))
    constant = audit["raw_maximum_to_birth_term"]
    fixed = audit["exact_residual"]
    low = constant + (audit["easy_residual_pairs"] if fixed is None else fixed)
    high = low + (audit["nontrivial_candidate_pairs"] if fixed is None else 0)
    summary = {"raw_maximal_cliques": panel_stats(values),
               "corrected_births_with_residual_lower": panel_stats([v + low for v in values]),
               "corrected_births_with_residual_upper": panel_stats([v + high for v in values]),
               "additive_correction_interval": [low, high], "exact_birth_truth": known_births}
    if known_births is not None:
        truth = Fraction(known_births)
        errors = [v + low - truth for v in values]
        summary["relative_mean_error_on_exact_case"] = report_number(sum(errors) / (len(errors) * truth))
        summary["exact_truth_inside_empirical_range"] = min(values) + low <= truth <= max(values) + low
    return {**fields, "status": "complete", "header": header, "observations": observations, "summary": summary}


def calibration_panels(output):
    stages = json.loads(((INPUTS or DEFAULT) / "index.json").read_text())["stages"]
    results = []
    for tag in ("start-03", "start-04"):
        meta = next(row for row in stages if row["case"] == tag and row["age"] == 7)
        results.append(run(tag, meta, control_seed=202611239100 + int(tag[-2:])))
    assert all(row["status"] == "complete" for row in results)
    write_at(output, lambda f: json.dump(results, f, indent=2, sort_keys=True))
    return {row["case"]: row["summary"] for row in results}


def controls(inputs, work):
    with TemporaryDirectory(prefix="prespatial-prefix-control-") as temporary:
        scratch = Path(temporary)
        tiny = scratch / "twins.txt"
        tiny.write_text("3 3\n0 1\n0 2\n1 2\n")
        assert true_twins(Stage(tiny)) == ([0, 0, 0], [0])
        literal = Stage(inputs / "partner-3-age00.txt")
        path = scratch / "control.txt"
        n, _ = export_quotient(literal, path)
        prefix, count, decode, _ = prefix_ranker(Stage(path))
        assert n == 6 and len(prefix) <= 6
        hood = [literal.hood(literal.at[v]) for v in range(n)]
        prefix_mask = sum(1 << u for u in prefix)
        brute = set()
        word = prefix_mask
        while word:
            common = prefix_mask
            for v in members(word):
                common &= hood[v]
            if common == word:
                brute.add(word)
            word = (word - 1) & prefix_mask
        assert len(brute) == count == len({sum(1 << v for v in decode(i)) for i in range(count)})
        assert brute == {sum(1 << v for v in decode(i)) for i in range(count)}
        bank = scratch / "control-bank.txt"
        write_bank(bank, prefix, count, decode, 7)
        readings = []
        for width in (16, 32):
            binary = work / "engine" / str(width) / "anneal"
            process = subprocess.run([binary, path, "degree-up", str(ORDER_SEED), str(POPULATION), "7",
                                      str(REPLICATES), "0", "0", "0", "0", bank],
                                     text=True, capture_output=True, check=True)
            rows = list(map(json.loads, process.stdout.splitlines()))
            assert len(rows) == 1 + REPLICATES and rows[0]["classes"] == n
            readings.append([estimate(row) for row in rows[1:]])
        assert readings[0] == readings[1]
    return {"true_twins_with_different_incidence_signatures": True, "all_prefix_cliques_compared": count,
            "order_three_control_known_full_maximal_cliques": 8,
            "both_integer_widths_match": True, "order_three_control_path_summary": panel_stats(readings[0])}


def exact_residual_record(row, total):
    case = row["case"]
    number = case[-2:]
    literal = ARTIFACTS / f"literal_residual{number}.json"
    cover = ARTIFACTS / f"cover_pairs{number}.json"
    special = ARTIFACTS / "pair_star_residual_start01.json"
    if literal.is_file():
        cert = json.loads(literal.read_text())
        assert cert["candidate_pairs"] == total
        assert cert["candidate_pairs"] - cert["covered_pairs"] == cert["residual_count"]
        return cert["residual_count"], literal
    if cover.is_file():
        cert = json.loads(cover.read_text())
        assert cert["inspected_candidate_pairs"] == total and cert["live"] == row["quotient"]["literal"]
        return cert["residual_pairs"], cover
    if case == "start-01" and special.is_file():
        cert = json.loads(special.read_text())
        assert cert["input_sha256"] == row["input_sha256"] and cert["candidate_pairs"] == total
        assert cert["candidate_pairs"] - cert["covered_candidate_pairs"] == cert["residual_pairs"]
        return cert["residual_pairs"], special
    return None, None


def add_birth_panel(row, pairs):
    if row["status"] != "complete":
        return
    values = list(map(estimate, row["observations"]))
    correction = row["birth_correction"]
    constant = correction["raw_maximum_to_birth_term"]
    if correction["exact_residual"] is not None:
        residual = [Fraction(correction["exact_residual"])] * len(values)
        schedule = {"source": "exhaustive residual", "residual": correction["exact_residual"],
                    "file": "near_block_02.json", "sha256": digest(ARTIFACTS / "near_block_02.json")}
    else:
        assert all(pairs[k] == correction[k] for k in ("held", "isolated", "offshoots", "easy_residual_pairs",
                                                        "nontrivial_candidate_pairs", "total_candidate_pairs"))
        fixed, certificate = exact_residual_record(row, pairs["total_candidate_pairs"])
        if fixed is None:
            fixed = pairs.get("exact_residual")
        if fixed is not None:
            residual = [Fraction(fixed)] * len(values)
            certificate = certificate or ARTIFACTS / "pair_corrections.json"
            schedule = {"source": "exhaustive residual", "residual": fixed,
                        "file": certificate.name, "sha256": digest(certificate)}
        else:
            hits = pairs["hits"][:len(values)]
            assert len(hits) == len(values)
            pair_seed, count_seed = pairs["base_seed"], row["seed"]
            assert pair_seed + len(hits) <= count_seed or count_seed + len(hits) <= pair_seed
            size = pairs["samples_per_replicate"]
            residual = [Fraction(pairs["easy_residual_pairs"]) + Fraction(pairs["nontrivial_candidate_pairs"] * hit, size)
                        for hit in hits] if size else [Fraction(pairs["easy_residual_pairs"])] * len(values)
            schedule = {"source": "first sixteen independent residual-pair batches", "samples_per_batch": size,
                        "independent_base_seed": pairs["base_seed"], "hits": hits,
                        "easy_residual_pairs": pairs["easy_residual_pairs"],
                        "residual_frame": pairs["nontrivial_candidate_pairs"]}
    exact_births = [raw + constant + pair for raw, pair in zip(values, residual, strict=True)]
    row["summary"]["birth_panel"] = panel_stats(exact_births)
    row["summary"]["residual_schedule"] = schedule


def archive_mapping_receipts(path, cases):
    """Keep only exact mappers and the compiled source inputs in the durable archive."""
    source_files = [(name, WORK / "engine" / str(width) / name)
                    for width in (16, 32) for name in ("anneal.cpp", "anneal_prefix.hpp", "sequential.cpp")]
    entries = [(f"engine/{p.parent.name}/{name}", p) for name, p in source_files]
    entries.append(("engine/build.json", WORK / "engine" / "build.json"))
    for name in ("anneal_entry_adapter.cpp", "prefix_targets_parallel.cpp"):
        source = WORK / "engine" / "32" / name
        if source.is_file():
            entries.append((f"engine/32/{name}", source))
    for case, meta in sorted(cases.items()):
        stem = f"{case}-age{meta['age']:02d}"
        mapping = WORK / stem / "quotient.map.json.gz"
        if mapping.is_file():
            entries.append((f"maps/{stem}.json.gz", mapping))
    with NamedTemporaryFile(dir=path.parent, prefix="prefix_inputs_pending_", delete=False) as raw:
        pending = Path(raw.name)
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream:
            with tarfile.open(fileobj=stream, mode="w|") as archive:
                for name, source in entries:
                    info = tarfile.TarInfo(name)
                    info.size = source.stat().st_size
                    with source.open("rb") as f:
                        archive.addfile(info, f)
    pending.replace(path)
    return {"file": path.name, "sha256": digest(path), "entries": [name for name, _ in entries]}


def continued_wide(path):
    continuation = path / "continuation.json"
    if not continuation.is_file():
        return None
    plan = json.loads(continuation.read_text())
    fields = plan["metadata"]
    first, past = plan["start_offset"], plan["submit_end_offset"]
    assert past == REPLICATES and len(plan["serial_observations"]) == first
    assert digest(path / "raw.jsonl") == plan["serial_sha256"]
    assert digest(path / "bank.txt") == fields["bank_sha256"]
    assert digest(path / "quotient.txt") == fields["quotient"]["roster_sha256"]
    base = fields["seed"]
    inherited = plan.get("earlier_parallel_batches", [])
    verified = {}
    for batch in inherited:
        for row in batch["accepted_receipts"]:
            seed = row["seed"]
            assert base + first <= seed < base + past and seed not in verified
            verified[seed] = row["sha256"]
    now = []
    for index in range(first, past):
        receipt = path / "continuation" / f"seed-{base+index}.jsonl"
        if base + index in verified:
            assert receipt.is_file() and digest(receipt) == verified[base + index]
        if not receipt.is_file():
            continue
        row = json.loads(receipt.read_text())
        assert row["seed"] == base + index
        now.append(row)
    report = {"sequential_replicates_retained": first, "parallel_replicates_retained": len(now),
              "planned_parallel_workers_reading_one_graph": plan["parallel_processes"],
              "identical_weight_protocol_control": plan["check"], "serial_sha256": plan["serial_sha256"],
              "earlier_parallel_batches": inherited}
    replay = path / "retained_replay.json"
    if replay.is_file():
        check = json.loads(replay.read_text())
        assert check["binary_sha256"] == plan["check"]["binary_sha256"]
        assert set(check["exactly_reproduced_retained_seeds"]) == verified.keys() | set(range(base, base + first))
        report["retained_receipt_replay"] = check
    observations = plan["serial_observations"] + now
    if len(observations) < REPLICATES:
        return {**fields, "status": "continuation_in_progress", "partial_native_rows": observations,
                "execution": report}
    return {**summarize(fields, plan["header"], observations), "execution": report}


def collect(run_dirs, output):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    records = {}
    for run_dir in run_dirs:
        previous = load_results(run_dir)
        assert not (records.keys() & previous.keys()), "An independent panel cannot repeat a history"
        records.update(previous)
    expected = dict(all_cases())
    assert set(records) <= set(expected)
    correction_path = ARTIFACTS / "pair_corrections.json"
    independent = {item["stage"]: item for item in json.loads(correction_path.read_text())["targets"]}
    rows = []
    for case, meta in expected.items():
        result = records.get(case)
        path = WORK / f"{case}-age{meta['age']:02d}"
        continuation = continued_wide(path) if case == "start-14" else None
        if continuation is not None:
            add_birth_panel(continuation, independent[f"{case}-age{meta['age']:02d}"])
            rows.append(continuation)
        elif result is not None and result["status"] == "ok":
            row = {**result["result"], "seconds": result["seconds"], "peak_rss_mb": result["peak_rss_mb"]}
            add_birth_panel(row, independent[f"{case}-age{meta['age']:02d}"])
            rows.append(row)
        else:
            partial = path / "raw.jsonl"
            readable = []
            if partial.exists():
                for line in partial.read_text().splitlines():
                    try:
                        readable.append(json.loads(line))
                    except ValueError:
                        break
            rows.append({"case": case, "age": meta["age"], "target_round": meta["target_round"],
                         "status": (("in_progress" if partial.exists() else "pending") if result is None else result["status"]),
                         "prepared_inputs": json.loads((path / "settings.json").read_text())
                         if (path / "settings.json").exists() else None,
                         "partial_native_rows": readable})
    report = {"design": {"order": "degree-up", "order_seed": ORDER_SEED,
                         "first_seed_formula": "202611238000 + 64 * history number", "outsider_cap": OUTSIDERS,
                         "population": POPULATION, "independent_replicates_per_case": REPLICATES,
                         "spacing": 0, "sweeps": 0},
              "engine": json.loads((WORK / "engine" / "build.json").read_text()), "targets": rows,
              "independent_pair_correction_sha256": digest(correction_path),
              "exact_checks": controls(INPUTS or DEFAULT, WORK)}
    if output == ARTIFACTS / "prefix_targets.json":
        report["mapped_inputs"] = archive_mapping_receipts(output.with_name("prefix_targets_inputs.tar.gz"), expected)
    write_at(output, lambda f: json.dump(report, f, indent=2, sort_keys=True))
    return {r["case"]: {"status": r["status"], "summary": r.get("summary")} for r in rows}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, default=WORK)
    parser.add_argument("--inputs", type=Path, default=DEFAULT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("compile")
    sub.add_parser("controls")
    calibrated = sub.add_parser("calibrate")
    calibrated.add_argument("--output", type=Path, default=ARTIFACTS / "prefix_targets_controls.json")
    one = sub.add_parser("one")
    one.add_argument("case")
    merge = sub.add_parser("collect")
    merge.add_argument("run_dir", type=Path, nargs="+")
    merge.add_argument("--output", type=Path, default=ARTIFACTS / "prefix_targets.json")
    args = parser.parse_args()
    setup({"work": args.work, "inputs": args.inputs})
    if args.command == "compile":
        output = build(WORK)
    elif args.command == "controls":
        output = controls(INPUTS, WORK)
    elif args.command == "calibrate":
        output = calibration_panels(args.output)
    elif args.command == "one":
        output = run(args.case, dict(cases())[args.case])
    else:
        output = collect(args.run_dir, args.output)
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
