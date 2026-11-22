#!/usr/bin/env python3
"""Independent finite-panel census and result replay for the letter experiment."""

import argparse
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


GLYPHS = {
    ("S", "L"): ("100", "100", "111"),
    ("S", "T"): ("111", "010", "010"),
    ("W", "L"): ("1000", "1111"),
    ("W", "T"): ("1111", "0100"),
}
CONDITIONS = {"train": 64, "familiar": 64, "position": 72, "orientation": 128, "combined": 72}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def digest(data):
    return sha256(data).hexdigest()


def unique_fields(pairs):
    fields = dict(pairs)
    require(len(fields) == len(pairs), "Duplicate JSON field")
    return fields


def load_json(data):
    return json.loads(data, object_pairs_hook=unique_fields)


def read_jsonl(data):
    return [load_json(line) for line in data.splitlines()]


def render(glyph, row, col, turns):
    rotated = glyph
    for _ in range(turns):
        rotated = tuple(map("".join, zip(*reversed(rotated), strict=True)))

    padded = ["0" * 8 for _ in range(8)]
    for offset, line in enumerate(rotated):
        padded[row + offset] = "0" * col + line + "0" * (8 - col - len(line))
    rendered = "".join(padded)
    require(len(rendered) == 64 and rendered.count("1") == 5, "Clipped or malformed fixture")
    return rendered


def partition(style, row, col, turns):
    # The held congruence is equivalently row == col modulo three.
    new_anchor = row % 3 == col % 3
    new_orientation = turns >= 2
    if new_anchor and new_orientation:
        return "combined"
    if new_anchor:
        return "position"
    if new_orientation:
        return "orientation"
    seen_style = "W" if (row ^ col ^ turns) & 1 else "S"
    return "train" if style == seen_style else "familiar"


def independent_panel():
    examples = {}
    for (style, label), row, col, turns in product(GLYPHS, range(5), range(5), range(4)):
        pixels = render(GLYPHS[style, label], row, col, turns)
        identity = digest(pixels.encode("ascii"))
        require(identity not in examples, "Repeated bitmap or digest")
        examples[identity] = {
            "pixels": pixels,
            "label": label,
            "condition": partition(style, row, col, turns),
            "style": style,
            "row": row,
            "col": col,
            "q": turns,
        }
    return examples


def expected_files(examples):
    groups = {}
    for filename, keyname, train in (
        ("train.jsonl", "training_key.jsonl", True),
        ("queries.jsonl", "scorer_key.jsonl", False),
    ):
        selected = sorted(
            key for key, example in examples.items() if (example["condition"] == "train") == train
        )
        groups[keyname] = [
            {"id": key, **{name: value for name, value in examples[key].items() if name != "pixels"}}
            for key in selected
        ]
        salt = f"pixel-letters-20261122-v1-{'train' if train else 'query'}:"
        groups[filename] = sorted(
            ({"id": key, "pixels": examples[key]["pixels"]} for key in selected),
            key=lambda row: (digest((salt + row["pixels"]).encode("ascii")), row["id"]),
        )
    return groups


def compare_rows(expected, observed):
    require(observed.keys() == expected.keys(), "Missing or additional panel streams")
    for filename, rows in expected.items():
        require(len(observed[filename]) == len(rows), f"{filename}: wrong row count")
        for index, (actual, wanted) in enumerate(zip(observed[filename], rows, strict=True)):
            require(equal_json_values(actual, wanted), f"{filename}: mismatch on line {index + 1}")


def equal_json_values(actual, expected):
    # JSON equality distinguishes true from 1, unlike Python equality.
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def challenge_census(expected):
    mutations = {
        "query metadata": ("queries.jsonl", {**expected["queries.jsonl"][0], "label": "L"}),
        "query digit": ("queries.jsonl", {**expected["queries.jsonl"][0], "pixels": "2" + "0" * 63}),
        "query identity": ("queries.jsonl", {**expected["queries.jsonl"][0], "id": "wrong"}),
        "boolean-or-integer confusion": ("scorer_key.jsonl", {**expected["scorer_key.jsonl"][0], "q": True}),
    }
    rejected = []
    for name, (filename, replacement) in mutations.items():
        changed = {**expected, filename: [replacement, *expected[filename][1:]]}
        try:
            compare_rows(expected, changed)
        except ValueError:
            rejected.append(name)

    for name, changed in (
        ("query reversal", {**expected, "queries.jsonl": list(reversed(expected["queries.jsonl"]))}),
        ("query truncation", {**expected, "queries.jsonl": expected["queries.jsonl"][:-1]}),
    ):
        try:
            compare_rows(expected, changed)
        except ValueError:
            rejected.append(name)

    try:
        load_json('{"pixels":"0","pixels":"1"}')
    except ValueError:
        rejected.append("duplicate JSON field")
    require(len(rejected) == 7, "A corrupted census input was accepted")
    return rejected


def census(panel_dir):
    examples = independent_panel()
    expected = expected_files(examples)
    actual = {name: (panel_dir / name).read_bytes() for name in expected}
    compare_rows(expected, {name: read_jsonl(data) for name, data in actual.items()})

    manifest = load_json((panel_dir / "manifest.json").read_bytes())
    require(manifest["files"].keys() == expected.keys(), "Wrong manifest stream roster")
    for name, data in actual.items():
        wanted = {"rows": len(expected[name]), "sha256": digest(data)}
        require(equal_json_values(manifest["files"][name], wanted), f"Wrong manifest binding: {name}")
    generator = manifest["generator"]
    require(generator["path"] == "../panel.py", "Unexpected bound generator path")
    require(digest((panel_dir.parent / "panel.py").read_bytes()) == generator["sha256"], "Wrong generator digest")

    label_counts = Counter((row["condition"], row["label"]) for row in examples.values())
    expected_counts = {name: {"L": count // 2, "T": count // 2} for name, count in CONDITIONS.items()}
    require(label_counts == Counter({(name, label): count for name, counts in expected_counts.items()
                                     for label, count in counts.items()}), "Wrong split or class census")
    require(manifest["counts"] == expected_counts, "Wrong label counts in manifest")
    pairs = Counter(
        (row["condition"], row["style"], row["q"], row["row"], row["col"])
        for row in examples.values()
    )
    require(set(pairs.values()) == {2}, "Class pair mismatch within pose and style")

    by_style_q = Counter((row["condition"], row["style"], row["q"]) for row in examples.values())
    return {
        "unique_bitmaps": len(examples),
        "counts_by_label": expected_counts,
        "counts_by_style_and_orientation": {
            name: {style: [by_style_q[name, style, turns] for turns in range(4)] for style in ("S", "W")}
            for name in CONDITIONS
        },
        "paired_labels_per_pose_and_style": len(pairs),
        "verified_stream_digests": {name: digest(data) for name, data in actual.items()},
        "rejected_census_mutations": challenge_census(expected),
    }


def local_census(pixels):
    """Count row-major words by indexing an explicitly padded bitmap."""
    require(len(pixels) == 64 and set(pixels) <= {"0", "1"}, "Invalid bitmap")
    padded = ["0" * 10, *("0" + pixels[offset:offset + 8] + "0" for offset in range(0, 64, 8)), "0" * 10]
    counts = Counter(
        int(padded[row][col:col + 2] + padded[row + 1][col:col + 2], 2)
        for row, col in product(range(9), repeat=2)
    )
    return tuple(counts[pattern] for pattern in range(16))


def source_module(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_preparations(producer_dir):
    learner = source_module(producer_dir / "learner.py")
    ordinary = source_module(producer_dir / "conventional.py")
    triple_space = set(product(range(2), repeat=3))
    pair_space = set(product(range(2), repeat=2))
    expected_support = {
        "parity": triple_space - {(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)},
        "nae": triple_space - {(0, 0, 0), (1, 1, 1)},
    }
    expected_preparations = {"parity": ((1, 1, 0), (0, 1, 1)), "nae": ((1, 1, 0), (0, 0, 1))}
    for law, words in expected_support.items():
        require(0 < len(words) < len(triple_space), f"{law}: K1 or K3 failure")
        for forgotten in range(3):
            projection = {word[:forgotten] + word[forgotten + 1:] for word in words}
            require(projection == pair_space, f"{law}: K2 failure")
        require(learner.OPEN_RELATIONS[law] == words, f"{law}: producer relation mismatch")
        accepted = set()
        for word in triple_space:
            try:
                accepted.add(learner._admit_holding(law, *word))
            except ValueError:
                continue
        require(accepted == words, f"{law}: executable open relation differs")
        for pair in pair_space:
            completions = {candidate[2] for candidate in words if candidate[:2] == pair}
            try:
                completed = learner._admit_holding(law, *pair)
            except ValueError:
                require(len(completions) != 1, f"{law}: rejected a uniquely completed pair")
            else:
                require(completions == {completed[2]}, f"{law}: admitted a nonunique read")
        for bit, word in enumerate(expected_preparations[law]):
            completions = {candidate[2] for candidate in words if candidate[:2] == word[:2]}
            require(completions == {bit}, f"{law}: prepared word must force one read")
            require(learner._admit_word(law, *word[:2]) == word, f"{law}: wrong prepared word")

    # Blank, an interior singleton, every corner singleton and one mixed stencil.
    stencils = [(), (27,), (0,), (7,), (56,), (63,), (0, 1, 8, 27, 63)]
    for stencil in stencils:
        pixels = "".join("1" if index in stencil else "0" for index in range(64))
        read = tuple(map(int, pixels))
        expected = local_census(pixels)
        require(sum(expected) == 81, "Independent local count omitted a padded window")
        if len(stencil) == 1:
            require(expected == tuple(77 if i == 0 else int(i in {1, 2, 4, 8}) for i in range(16)),
                    "One lit bit must occur once in each local position")
        require(learner.pattern_counts(read) == expected, f"Knot local counts for stencil {stencil}")
        require(tuple(ordinary.histogram(read)) == expected, f"Numeric local counts for stencil {stencil}")

    rejected = []
    for law in expected_support:
        blank = learner.KnotLearner(law, training_limit=64).export_memory()
        require(learner.KnotLearner.from_memory(blank).export_memory() == blank, f"{law}: neutral round trip")
        broken_words = [list(bank) for bank in blank["words"]]
        broken_words[0][0] = "111" + broken_words[0][0][3:]
        bad_count = [list(bank) for bank in blank["words"]]
        one_word = "".join(map(str, expected_preparations[law][1]))
        bad_count[0][0] = one_word + bad_count[0][0][3:]
        for name, mutation in (
            ("unlawful prepared word", {**blank, "words": broken_words}),
            ("impossible count total", {**blank, "words": bad_count}),
            ("provenance field", {**blank, "label": "L"}),
            ("boolean training budget", {**blank, "training_limit": True}),
        ):
            try:
                learner.KnotLearner.from_memory(mutation)
            except ValueError:
                rejected.append(f"{law}: {name}")
            else:
                raise ValueError(f"{law}: accepted {name}")

    return {
        "K1_K2_K3": {law: {"allowed": len(words), "projection_counts": [4, 4, 4]}
                     for law, words in expected_support.items()},
        "forced_prepared_words": expected_preparations,
        "executable_admission_cases": 24,
        "synthetic_stencils_checked": len(stencils),
        "physical_memory_mutations_rejected": rejected,
    }


def verify_phase_io(producer_dir):
    sys.path.insert(0, str(producer_dir.resolve()))
    try:
        study = source_module(producer_dir / "study.py")
    finally:
        sys.path.pop(0)

    rejected = []

    def reject(name, operation, *args):
        try:
            operation(*args)
        except (ValueError, FileExistsError, FileNotFoundError):
            rejected.append(name)
        else:
            raise ValueError(f"Producer accepted {name}")

    with TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix="phase-io-") as scratch:
        directory = Path(scratch)
        producer_model = study.FAMILY
        study.FAMILY = directory
        valid_bits = "0" * 64
        valid = {"id": digest(valid_bits.encode("ascii")), "pixels": valid_bits}

        def check_records(name, records):
            path = directory / (name + ".jsonl")
            study.write_rows(path, records)
            reject(name, study.public_rows, path)

        study.write_rows(directory / "valid.jsonl", [valid])
        require(study.public_rows(directory / "valid.jsonl") == [valid], "Valid pixel fixture failed")
        check_records("extra learner-facing provenance", [{**valid, "q": 0}])
        check_records("invalid pixel digit", [{**valid, "pixels": "2" + "0" * 63}])
        check_records("malformed raw length", [{**valid, "pixels": "0" * 63}])
        check_records("inconsistent bitmap digest", [{**valid, "id": "0" * 64}])
        check_records("duplicate bitmap", [valid, valid])
        reject("overwrite raw stream", study.write_rows, directory / "valid.jsonl", [])

        contract = directory / "contract.json"
        study.write_json(contract, {"synthetic": True})
        fit = study.phase_dir(directory, "fit")
        reject("reopen fit directory", study.phase_dir, directory, "fit")
        reject("absent fit release", study.check_release, fit)
        study.write_json(fit / "blank.json", {"synthetic": "initial"})
        study.release(fit, ["blank.json"], {}, 0, {})
        receipt = study.check_release(fit)
        (fit / "blank.json").write_text("replaced")
        reject("alter sealed checkpoint", study.check_release, fit)
        study.bind(contract, receipt["contract_sha256"])
        contract.write_text("different")
        reject("alter frozen contract", study.check_release, fit)
        study.FAMILY = producer_model

    return {"producer_io_mutations_rejected": rejected, "train_or_score_invoked": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    parser.add_argument("--check-preparations", action="store_true")
    parser.add_argument("--check-phase-io", action="store_true")
    args = parser.parse_args()
    report = census(args.panel)
    if args.check_preparations:
        report["preparations"] = verify_preparations(args.panel.parent)
    if args.check_phase_io:
        report["phase_io"] = verify_phase_io(args.panel.parent)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
