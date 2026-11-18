"""Independent primal-space audit of the mixed-output finite interval."""

import argparse
import importlib.util
import json
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1]
EARLIER = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001B"
           / "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen")
SEPARATOR = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001D"
             / "VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse")
SCRATCH = Path("/var/tmp/presp-interval-ERF-20261118")
CONTROL_COUNTS = {
    18: {6: 89, 7: 1609, 8: 1797},
    19: {7: 1740, 8: 5355, 9: 1096},
    20: {7: 1216, 8: 10198, 9: 8000},
}
RESIDUAL_COUNTS = {21: 0, 22: 4, 23: 12, 24: 31, 25: 67, 26: 197}
UINT64 = (1 << 64) - 1


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def width_engine(oracle, width):
    oracle.WIDTH = oracle.INFINITY = width
    oracle.PAIRS = tuple(combinations(range(width), 2))


def active_bits(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def mask(names):
    return sum(1 << i for i in names)


def rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            high = vector.bit_length() - 1
            if high not in pivots:
                pivots[high] = vector
                break
            vector ^= pivots[high]
    return len(pivots)


def primal_columns(checks, width):
    """Express every distinction in terms of a basis for allowed states."""
    pivots = {}
    for check in checks:
        row = mask(check)
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
        assert row
    free = [i for i in range(width) if i not in pivots]
    columns = [0] * width
    for position, name in enumerate(free):
        columns[name] = 1 << position
    for i in sorted(pivots):
        for other in active_bits(pivots[i] ^ (1 << i)):
            columns[i] ^= columns[other]
    return columns


def dependent_supports(columns):
    """Build the kernel of the primal columns, recording original names."""
    pivots = {}
    words = [0]
    for i, column in enumerate(columns):
        lifting = 1 << i
        while column:
            high = column.bit_length() - 1
            if high not in pivots:
                pivots[high] = (column, lifting)
                break
            other, old_lifting = pivots[high]
            column ^= other
            lifting ^= old_lifting
        if not column:
            words.extend(lifting ^ word for word in words[:])
    return words


def scalar_minima(checks, width):
    columns = primal_columns(checks, width)
    words = dependent_supports(columns)
    assert len(words) == 1 << len(checks) and len(set(words)) == len(words)
    assert all(mask(check) in words for check in checks)
    table = [bytearray([width] * width) for _ in range(width)]
    for i in range(width):
        table[i][i] = 0
    circuits = 0
    for word in words[1:]:
        support = tuple(active_bits(word))
        assert len(support) >= 3
        # XOR of all these columns is zero. Rank one less than the support
        # size makes this the only dependence, so every proper set is free.
        if rank(columns[i] for i in support[:-1]) != len(support) - 1:
            continue
        circuits += 1
        for a, b in combinations(support, 2):
            if len(support) - 1 < table[a][b]:
                table[a][b] = table[b][a] = len(support) - 1
    return tuple(map(bytes, table)), circuits


def permissions(checks):
    owners = {name: [i for i, check in enumerate(checks) if name in check]
              for name in sorted(set().union(*checks))}
    neighbors = [set() for _ in checks]
    for holders in owners.values():
        assert len(holders) in (1, 2)
        if len(holders) == 2:
            a, b = holders
            neighbors[a].add(b)
            neighbors[b].add(a)
    legal = set()
    for triple in combinations((i for i, holders in owners.items() if len(holders) == 1), 3):
        parents = tuple(owners[name][0] for name in triple)
        if len(set(parents)) != 3:
            continue
        first, second, third = (neighbors[site] for site in parents)
        if first & second and first & third and second & third and not first & second & third:
            legal.add(triple)
    return legal


def replay_history(checks, history):
    """Replay actual distinction names from the ternary seed."""
    owners = {}
    neighbors = [set() for _ in checks]
    assert sorted(history) == list(range(len(checks)))
    for depth, site in enumerate(history):
        used = tuple(i for i in checks[site] if i in owners)
        fresh = tuple(i for i in checks[site] if i not in owners)
        assert all(len(owners[i]) == 1 for i in used)
        parents = tuple(owners[i][0] for i in used)
        assert len(set(parents)) == len(parents)
        if depth == 0:
            assert not parents and len(fresh) == 3
        else:
            assert 1 <= len(parents) <= 3 and len(fresh) in (2, 3)
            assert all(neighbors[a] & neighbors[b] for a, b in combinations(parents, 2))
            if len(parents) == 3:
                assert not set.intersection(*(neighbors[i] for i in parents))
        for parent in parents:
            neighbors[parent].add(site)
            neighbors[site].add(parent)
        for i in checks[site]:
            owners.setdefault(i, []).append(site)


def decode(record, width):
    size = record[0]
    assert len(record) == 1 + 2 * size
    neighbors = record[1:1 + size]
    loose = record[1 + size:]
    checks = [[] for _ in range(size)]
    name = 0
    for i, row in enumerate(neighbors):
        assert 0 <= row < (1 << size) and not (row >> i & 1)
        for j in active_bits(row):
            assert neighbors[j] >> i & 1
            if i < j:
                checks[i].append(name)
                checks[j].append(name)
                name += 1
    for i, count in enumerate(loose):
        assert 0 <= count <= 3
        checks[i].extend(range(name, name + count))
        name += count
    assert name == width
    assert all(3 <= len(support) <= 6 for support in checks)
    return checks, neighbors


def check_record(record, width, oracle):
    checks, neighbors = decode(record, width)
    history = oracle.reverse.legal_history(tuple(neighbors), tuple(map(len, checks)))
    assert history, (width, record)
    replay_history(checks, history)
    table, circuits = scalar_minima(checks, width)
    menu = permissions(checks)
    width_engine(oracle, width)
    other, other_bonds, _ = oracle.bond_table(checks)
    assert table == other and circuits == len(other_bonds)
    assert menu == oracle.triple_menu(checks)
    twins = oracle.interchangeable(table)
    table_label, group, _ = oracle.canonical(table, twins)
    marks, partial = oracle.marked_orbits(table, twins, menu, group)
    marked_conflict = (oracle.partial_orbit_witness(table, twins, menu, marks, partial)
                       if partial else None)
    return {"record": record, "history": history, "bonds": circuits,
            "pair_table_sha256": sha256(b"".join(table)).hexdigest(), "legal_triples": sorted(menu),
            "scalar_canonical_form_sha256": sha256(table_label).hexdigest(),
            "exact_group_order": group, "legal_marked_orbits": len(marks), "marked_conflict": marked_conflict,
            "bond_distance_counts": dict(sorted(Counter(table[i][j] for i, j in combinations(range(width), 2)).items()))}


def read_population(path, width, oracle):
    digest = sha256()
    counts = Counter()
    first_by_size = {}
    first_positive = None
    count = 0
    before = path.stat()
    with path.open("rb") as source:
        for index, raw in enumerate(source):
            digest.update(raw)
            size = int(raw.split(None, 1)[0])
            assert 2 * (size - 1) <= width - 3 <= 3 * (size - 1)
            counts[size] += 1
            first_by_size.setdefault(size, index)
            if first_positive is None:
                record = [int(item) for item in raw.split()]
                nearby = record[1:size + 1]
                loose_holders = [i for i, count in enumerate(record[size + 1:]) if count]
                if any(nearby[a] & nearby[b] and nearby[a] & nearby[c] and nearby[b] & nearby[c]
                       and not nearby[a] & nearby[b] & nearby[c]
                       for a, b, c in combinations(loose_holders, 3)):
                    first_positive = index
            count = index + 1
    assert count
    sample_indices = {0, count - 1, *first_by_size.values()}
    assert first_positive is not None
    sample_indices.add(first_positive)
    for sequence in range(4):
        key = f"marked-triple-audit-{width}-{sequence}".encode()
        sample_indices.add(int.from_bytes(sha256(key).digest(), "big") % count)
    samples = {}
    with path.open("rb") as source:
        for index, raw in enumerate(source):
            if index in sample_indices:
                samples[index] = check_record([int(item) for item in raw.split()], width, oracle)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    assert samples.keys() == sample_indices
    assert samples[first_positive]["legal_triples"]
    if width in CONTROL_COUNTS:
        assert counts == CONTROL_COUNTS[width]
    return {"width": width, "population_sha256": digest.hexdigest(), "presentations": count,
            "provenance_population": path.name, "by_junction_count": dict(sorted(counts.items())),
            "first_triple_bearing_sample": first_positive,
            "archived_counts_match": width in CONTROL_COUNTS, "samples": samples}


def apply_mapping(triple, mapping):
    return tuple(sorted(mapping[i] for i in triple))


def controls():
    accepted_path = EARLIER / "reverse.json"
    accepted = json.loads(accepted_path.read_text())["positive_and_mutant"]
    checks = accepted["checks"]
    menu = permissions(checks)
    assert sorted(menu) == [tuple(triple) for triple in accepted["legal_triples"]]
    table, circuits = scalar_minima(checks, 19)
    assert circuits == accepted["bond_count"]
    replay_history(checks, tuple(range(len(checks))))
    rename = tuple(reversed(range(len(table))))
    renamed_checks = [tuple(rename[i] for i in check) for check in checks]
    other, _ = scalar_minima(renamed_checks, 19)
    assert all(table[i][j] == other[rename[i]][rename[j]] for i, j in combinations(range(19), 2))
    assert {apply_mapping(triple, rename) for triple in menu} == permissions(renamed_checks)

    mutant = accepted["same_count_negative"]
    deleted = tuple(mutant["removed_legal_triple"])
    inserted = tuple(mutant["inserted_illegal_triple"])
    mapping = dict(mutant["detected_legal_to_illegal_in_mutant"]["permutation"])
    assert deleted in menu and inserted not in menu
    corrupt = (menu - {deleted}) | {inserted}
    assert len(corrupt) == len(menu)
    kept = tuple(mutant["detected_legal_to_illegal_in_mutant"]["from"])
    assert all(table[i][j] == table[mapping[i]][mapping[j]] for i, j in combinations(range(19), 2))
    assert kept in corrupt and apply_mapping(kept, mapping) == deleted and deleted not in corrupt

    near_path = SEPARATOR / "continuation.json"
    near = json.loads(near_path.read_text())["matched_retained_rows_control"]
    left, right = near["left"], near["right"]
    assert left["checks"] == right["checks"] and left["width"] == right["width"] == 22
    checked_junctions = tuple(left["checks"][str(i)] for i in range(len(left["checks"])))
    actual = permissions(checked_junctions)
    before, after = (tuple(item["marked"]) for item in (left, right))
    assert before in actual and after not in actual
    replay_history(checked_junctions, tuple(range(len(checked_junctions))))
    larger, _ = scalar_minima(checked_junctions, 22)
    map_22 = dict(near["retained_row_preserving_map"])
    assert apply_mapping(before, map_22) == after
    seen = [(i, j) for i, j in combinations(range(22), 2) if i in before or j in before]
    assert all(larger[i][j] == larger[map_22[i]][map_22[j]] for i, j in seen)
    different = [(i, j) for i, j in combinations(range(22), 2) if larger[i][j] != larger[map_22[i]][map_22[j]]]
    assert different
    oracle = import_file("audit_accepted_exact", EARLIER / "check_reverse.py")
    width_engine(oracle, 22)
    twins = oracle.interchangeable(larger)
    assert oracle.canonical(larger, twins, before)[0] != oracle.canonical(larger, twins, after)[0]
    return {"width_19": {"bonds": circuits, "legal_triples": len(menu), "arbitrary_renaming_ok": True,
                         "wrong_menu_rejected": {"same_size": len(corrupt), "from": kept, "to": deleted}},
            "width_22": {"marked_rows_match_pairs": len(seen), "outside_pairs_changed": len(different),
                         "exact_marked_match_rejected": True},
            "accepted_nineteen_sha256": sha256(accepted_path.read_bytes()).hexdigest(),
            "accepted_twenty_two_sha256": sha256(near_path.read_bytes()).hexdigest()}


def verify_witness(found, oracle):
    width = found["width"]
    operands = [tuple(found[f"{side}_mark"]) for side in ("left", "right")]
    mapping = found["left_to_right_bit_map"]
    assert sorted(mapping) == list(range(width))
    assert apply_mapping(operands[0], mapping) == operands[1]
    tables = []
    samples = []
    for side, mark in zip(("left", "right"), operands, strict=True):
        record = list(map(int, found[f"{side}_source"].split()))
        sample = check_record(record, width, oracle)
        assert (mark in sample["legal_triples"]) == found[f"{side}_legal"]
        tables.append(scalar_minima(decode(record, width)[0], width)[0])
        samples.append(sample)
    assert found["left_legal"] != found["right_legal"]
    assert all(tables[0][i][j] == tables[1][mapping[i]][mapping[j]]
               for i, j in combinations(range(width), 2))
    return {"witness": found, "physical_replays": samples, "pairs_verified": width * (width - 1) // 2}


def cross_check_grader(grader, populations):
    reports = {}
    with TemporaryDirectory(prefix="prespatial-finite-table-check-") as temp:
        scratch = Path(temp)
        for width_text, population in sorted(populations.items()):
            width = int(width_text)
            samples = list(population["samples"].values())
            source = scratch / f"sample{width}.txt"
            source.write_text("".join(" ".join(map(str, item["record"])) + "\n" for item in samples))
            dump = scratch / f"dump{width}.jsonl"
            checked = run([str(grader.resolve()), str(source), "--force-exact", "--expected-width",
                           str(width), "--dump", str(dump)], capture_output=True, check=True, text=True)
            summary = json.loads(checked.stdout)
            assert summary["status"] == "complete" and summary["loaded"] == summary["measured"] == len(samples)
            assert summary["witness"] is None
            pairs_checked = 0
            lines = set()
            for raw in dump.read_text().splitlines():
                row = json.loads(raw)
                assert row["line"] not in lines
                lines.add(row["line"])
                sample = samples[row["line"] - 1]
                record = list(map(int, row["source"].split()))
                assert record == sample["record"] and row["width"] == width
                checks, _ = decode(record, width)
                exact, _ = scalar_minima(checks, width)
                entries = [exact[i][j] for i, j in combinations(range(width), 2)]
                assert entries == [width if value == 255 else value for value in row["upper"]]
                assert sorted(permissions(checks)) == [tuple(triple) for triple in row["legal"]]
                pairs_checked += len(entries)
            assert lines == set(range(1, len(samples) + 1))
            assert pairs_checked == len(samples) * width * (width - 1) // 2
            reports[width] = {"records": len(samples), "pairs": pairs_checked,
                              "legal_triples": summary["legal_triple_occurrences"],
                              "full_exact_sample_cross_pairs": summary["cross_pairs_submitted_to_exact_search"]}
    return reports


def producer_profile_conflict(table, menu):
    """Check that an exact self case has a real mixed producer profile."""
    def mix(word):
        word = ((word ^ (word >> 30)) * 0xBF58476D1CE4E5B9) & UINT64
        word = ((word ^ (word >> 27)) * 0x94D049BB133111EB) & UINT64
        return word ^ (word >> 31)

    width = len(table)
    rows = tuple(tuple(255 if value == width else value for value in row) for row in table)
    salts = tuple(mix((0x9E3779B97F4A7C15 * (i + 1)) & UINT64) for i in range(256))
    first = [sum(salts[value] for value in row) & UINT64 for row in rows]
    color = [(mix(first[i] ^ 0xB492B66FBE98F273)
              + sum(mix(first[j] ^ salts[value]) for j, value in enumerate(row))) & UINT64
             for i, row in enumerate(rows)]
    palette = {value: i for i, value in enumerate(sorted(set(color)))}
    ranks = [palette[value] for value in color]

    def profile(triple):
        a, b, c = triple
        return tuple(sorted(((ranks[a], rows[b][c]), (ranks[b], rows[a][c]), (ranks[c], rows[a][b]))))

    positive = {profile(triple): triple for triple in sorted(menu)}
    for triple in combinations(range(width), 3):
        key = profile(triple)
        if triple not in menu and key in positive:
            return {"legal": positive[key], "forbidden": triple}
    raise AssertionError("A residual record must have a mixed marked profile")


def mutant_menu(table, menu, forbidden, oracle):
    twins = oracle.interchangeable(table)
    _, group, _ = oracle.canonical(table, twins)
    old = {}
    for triple in sorted(menu):
        key, _, ordering = oracle.canonical(table, twins, triple)
        if key not in old:
            old[key] = (triple, ordering)
            continue
        origin, before = old[key]
        changed = (menu - {triple}) | {forbidden}
        assert len(changed) == len(menu)
        mapping = oracle.table_map(table, table, before, ordering)
        assert origin in changed and apply_mapping(origin, mapping) == triple and triple not in changed
        _, partial = oracle.marked_orbits(table, twins, changed, group)
        assert key in partial
        return {"kept_legal": origin, "removed_legal": triple, "inserted_forbidden": forbidden,
                "same_cardinality": len(changed), "actual_isometry": sorted(mapping.items())}
    return None


def check_residuals(source_rows, oracle, source_digest):
    rows = sorted(source_rows, key=lambda item: (item["width"], item["line"]))
    counts = Counter(item["width"] for item in rows)
    assert counts == {width: count for width, count in RESIDUAL_COUNTS.items() if count}
    assert len({(item["width"], item["line"]) for item in rows}) == len(rows)
    assert len({(item["width"], item["source"]) for item in rows}) == len(rows)
    evidence = []
    negative = None
    for item in rows:
        width = item["width"]
        record = list(map(int, item["source"].split()))
        exact = check_record(record, width, oracle)
        assert exact["marked_conflict"] is None, item
        assert len(exact["legal_triples"]) == item["legal_triples"] > 0
        checks, _ = decode(record, width)
        table, _ = scalar_minima(checks, width)
        menu = set(exact["legal_triples"])
        mix_pair = producer_profile_conflict(table, menu)
        if negative is None:
            negative = mutant_menu(table, menu, mix_pair["forbidden"], oracle)
            if negative is not None:
                negative.update(width=width, line=item["line"])
        evidence.append({**item, "history": exact["history"], "pair_table_sha256": exact["pair_table_sha256"],
                         "exact_group_order": exact["exact_group_order"],
                         "legal_marked_orbits": exact["legal_marked_orbits"], "mixed_profile_witness": mix_pair})
    assert negative
    return {"source_sha256": source_digest, "by_width": RESIDUAL_COUNTS,
            "records": evidence, "same_cardinality_negative_control": negative}


def verify_residual_lines(source_rows, directory):
    for width, count in RESIDUAL_COUNTS.items():
        if not count:
            continue
        expected = {item["line"]: item["source"].encode() for item in source_rows if item["width"] == width}
        assert len(expected) == count
        with (directory / f"width{width}.txt").open("rb") as source:
            for line, raw in enumerate(source, start=1):
                if line in expected:
                    assert raw.rstrip() == expected.pop(line)
                    if not expected:
                        break
        assert not expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population-dir", type=Path, default=SCRATCH)
    parser.add_argument("--width", type=int, nargs="*", default=())
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--grader", type=Path)
    parser.add_argument("--witness", type=Path)
    parser.add_argument("--residuals", type=Path)
    args = parser.parse_args()
    result = {"controls": controls(), "populations": {}}
    oracle = import_file("audit_accepted_orbits", EARLIER / "check_reverse.py")
    if args.replay:
        prior = json.loads(args.replay.read_text())
        assert prior["controls"] == json.loads(json.dumps(result["controls"]))
        for width, population in prior["populations"].items():
            for sample in population["samples"].values():
                actual = check_record(sample["record"], int(width), oracle)
                assert sample == json.loads(json.dumps(actual))
        result["populations"] = prior["populations"]
        if "producer_sample_cross_check" in prior:
            result["producer_sample_cross_check"] = prior["producer_sample_cross_check"]
        if "opposing_example" in prior:
            result["opposing_example"] = verify_witness(prior["opposing_example"]["witness"], oracle)
        if "exact_self_residuals" in prior and args.residuals is None:
            cache = prior["exact_self_residuals"]
            keys = ("width", "line", "source", "legal_triples", "exact_generators_checked")
            rows = [{key: item[key] for key in keys} for item in cache["records"]]
            result["exact_self_residuals"] = check_residuals(rows, oracle, cache["source_sha256"])
    for width in args.width:
        result["populations"][str(width)] = read_population(args.population_dir / f"width{width}.txt", width, oracle)
    if args.grader:
        assert result["populations"]
        result["producer_sample_cross_check"] = cross_check_grader(args.grader, result["populations"])
    if args.witness:
        result["opposing_example"] = verify_witness(json.loads(args.witness.read_text())["witness"], oracle)
    if args.residuals:
        raw = args.residuals.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines()]
        verify_residual_lines(rows, args.population_dir)
        result["exact_self_residuals"] = check_residuals(rows, oracle, sha256(raw).hexdigest())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
