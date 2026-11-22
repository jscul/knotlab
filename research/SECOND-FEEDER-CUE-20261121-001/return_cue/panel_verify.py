"""Verify comparison B with the pinned independent comparison A checker."""

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from types import ModuleType


HERE = Path(__file__).resolve().parent
FIRST = HERE.parent
FIRST_CHECKER = "49b58362a3f8cef07b705ab566ac8cb344b5599a978eef6903f6b8d5ac79f6f3"
FIRST_BANK = "777e6f04863a7d7e1a20b638714db875cf9da141e61bc029df55e6e9c3ed2a9a"
FOLDS = ("train", "mechanism", "survival")
MECHANISM_TAPES = 16
LAWS = ("parity", "nae")


def _bank():
    path = HERE / "bank.py"
    spec = spec_from_file_location("return_cue_verification_bank", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load the comparison B bank at {path}")
    bank = module_from_spec(spec)
    sys.modules[spec.name] = bank
    spec.loader.exec_module(bank)
    return bank


def _pinned(path, digest):
    payload = path.read_bytes()
    if sha256(payload).hexdigest() != digest:
        raise ValueError(f"{path} differs from the comparison A record")
    return payload


def _checker(bank):
    path = FIRST / "panel_verify.py"
    source = _pinned(path, FIRST_CHECKER)
    checker = ModuleType("comparison_a_independent_panel_checker")
    checker.__file__ = str(path)
    previous_bank = sys.modules.get("bank")
    sys.modules["bank"] = bank
    try:
        exec(compile(source, str(path), "exec"), vars(checker))
    finally:
        if previous_bank is None:
            del sys.modules["bank"]
        else:
            sys.modules["bank"] = previous_bank
    checker.HERE = HERE
    checker.select_starts = bank.select_starts
    checker.sample_pair = bank.sample_pair
    return checker


def _check_exclusions(first, second):
    first_keys = {row["source_key"] for fold in FOLDS for row in first["folds"][fold]}
    previous = set(first["excluded_keys"])
    selected = [row["source_key"] for fold in FOLDS for row in second["folds"][fold]]
    excluded = set(second["excluded_keys"])
    if len(first_keys) != 128 or not (previous | first_keys) <= excluded:
        raise ValueError("The comparison B lock omitted a required archived exclusion")
    if len(set(selected)) != len(selected) or not excluded.isdisjoint(selected):
        raise ValueError("The comparison B lock contains a repeated or excluded founder")
    return {
        "excluded_a_founders": len(first_keys),
        "excluded_predecessor_keys": len(previous),
        "comparison_b_founders": len(selected),
    }


def _check_selection(bank, manifest):
    for fold in FOLDS:
        starts = tuple(bank.select_starts(fold))
        keys = ("candidate_index", "source_key", "seed")
        selected = [tuple(getattr(start, key) for key in keys) for start in starts]
        locked = [tuple(row[key] for key in keys) for row in manifest["folds"][fold]]
        if selected != locked:
            raise ValueError(f"The executable comparison B {fold} bank differs from its lock")


def _check_cells(rows, bank, mechanism):
    expected = {
        (law, start["seed"], replicate): (
            start["source_key"],
            start["candidate_index"],
            bank.movement_tape("mechanism", start["source_key"], replicate),
        )
        for start in mechanism
        for law in LAWS
        for replicate in range(MECHANISM_TAPES)
    }
    seen = set()
    for row in rows:
        key = row["law"], row["seed"], row["replicate"]
        data = row["source_key"], row["candidate_index"], row["tape"]
        if key in seen or expected.get(key) != data or row["variant"] != "bank_renamed":
            raise ValueError(f"Incorrect or repeated comparison B terminal cell {key}")
        seen.add(key)
    if seen != expected.keys():
        raise ValueError("Comparison B terminal ledger omitted a locked mechanism cell")
    return len(seen)


def verify():
    first = json.loads(_pinned(FIRST / "bank.json", FIRST_BANK))
    payload = (HERE / "bank.json").read_bytes()
    second = json.loads(payload)
    exclusion_check = _check_exclusions(first, second)

    bank = _bank()
    checker = _checker(bank)
    _check_selection(bank, second)
    checked_cells = _check_cells(checker.read(HERE / "panel_runs.json.gz"), bank, second["folds"]["mechanism"])
    checker.verify()

    output = HERE / "panel_verified.json"
    result = json.loads(output.read_bytes())
    result.update(
        comparison="B",
        comparison_a_checker_sha256=FIRST_CHECKER,
        comparison_a_bank_sha256=FIRST_BANK,
        comparison_b_bank_sha256=sha256(payload).hexdigest(),
        bank_check={**exclusion_check, "verified_mechanism_cells": checked_cells},
    )
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["bank_check"]))


if __name__ == "__main__":
    verify()
