"""Pre-run checks of stream and release guards on temporary synthetic data."""

import argparse
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from panel_census import digest, require
from synthetic import source_module


def verify(producer):
    sys.path.insert(0, str(producer.resolve()))
    try:
        study = source_module(producer / "study.py")
    finally:
        sys.path.pop(0)

    rejected = []

    def reject(name, action, *args):
        try:
            action(*args)
        except (ValueError, FileExistsError, FileNotFoundError):
            rejected.append(name)
        else:
            raise ValueError(f"Phase I/O accepted {name}")

    with TemporaryDirectory(prefix="phase-io-", dir=Path(__file__).resolve().parent) as tmp:
        folder = Path(tmp)
        study.FAMILY = folder
        valid = {"pixels": "0" * 64}
        valid["id"] = digest(valid["pixels"].encode("ascii"))
        cases = {
            "metadata": [{**valid, "style": "E"}], "pixel type": [{**valid, "pixels": [0] * 64}],
            "invalid digit": [{**valid, "pixels": "2" + "0" * 63}], "invalid length": [{**valid, "pixels": "0" * 63}],
            "bad digest": [{**valid, "id": "0" * 64}], "duplicated bitmap": [valid, valid],
        }
        for name, body in cases.items():
            path = folder / (name + ".jsonl")
            study.save_lines(path, body)
            reject(name, study.public_rows, path)

        valid_path = folder / "valid.jsonl"
        study.save_lines(valid_path, [valid])
        require(study.public_rows(valid_path) == [valid], "Producer rejected valid fixture")
        reject("stream overwrite", study.save_lines, valid_path, [])

        contract = folder / "contract.json"
        study.save(contract, {"synthetic": True})
        fit = study.open_phase(folder, "fit")
        reject("phase overwrite", study.open_phase, folder, "fit")
        reject("missing fit release", study.check_release, fit)
        output = fit / "holding.json"
        study.save(output, {"initial": []})
        study.release(fit, {}, monotonic(), {"study": "synthetic"})
        study.check_release(fit)

        def inadmissible(*args):
            raise AssertionError(f"Scorer tried opening frozen streams before blind release: {args}")

        study.validate_inputs = inadmissible
        reject("early score before test-key access", study.score, folder)
        output.write_text("changed")
        reject("altered checkpoint", study.check_release, fit)

    return {"synthetic_phase_mutations_rejected": rejected, "actual_fit_and_score_called": False}


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("producer", type=Path)
    print(json.dumps(verify(arguments.parse_args().producer), indent=2, sort_keys=True))
