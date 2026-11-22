"""Adversarial execution checks with temporary releases and synthetic pixels."""

import argparse
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from reference import (ARMS, LAWS, calibrate_conditions, committee, counts, digest, equivalent,
                       expected_checkpoint_digests, fit_reference, fitted_physical_archive, require)


def module_at(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage_mutations(study):
    rejections = []

    def reject(name, call, *args, **kwargs):
        try:
            call(*args, **kwargs)
        except (ValueError, FileExistsError, FileNotFoundError):
            rejections.append(name)
        else:
            raise ValueError(f"Producer accepted {name}")

    with TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix="verify-stage-") as temporary:
        root = Path(temporary)
        study.FAMILY = root
        study.save(root / "contract.json", {"synthetic": True})
        bitmap = "0" * 64
        standard = {"id": digest(bitmap.encode("ascii")), "pixels": bitmap}
        fixtures = {"extra provenance": [{**standard, "turn": 2}],
                    "bad pixel type": [{**standard, "pixels": [0] * 64}],
                    "bad pixel digit": [{**standard, "pixels": "2" + "0" * 63}],
                    "bad length": [{**standard, "pixels": "0" * 63}],
                    "duplicate id": [standard, standard],
                    "undigested pixels": [{**standard, "id": "0" * 64}]}
        for named, rows in fixtures.items():
            data = b"\n".join(json.dumps(row).encode("ascii") for row in rows)
            reject(named, study.public_rows, data)
        require(study.public_rows(json.dumps(standard).encode("ascii")) == [standard], "Synthetic row rejected")

        fit = study.open_phase(root, "fit")
        reject("existing fit phase", study.open_phase, root, "fit")
        reject("incomplete fit release", study.check_release, fit)
        for filename in sorted(study.STAGE_FILES["fit"]):
            study.save(fit / filename, {"test": filename})
        study.release(fit, {}, monotonic(), {})
        study.check_release(fit)
        reject("overwrite checkpoint", study.save, fit / "diagnostics.json", {})

        authority = root / "authorization-placeholder"
        anchors = root / "anchors.jsonl"
        study.preflight = lambda: ({}, authority)
        study.check_fit = lambda *args: {}
        study.source_digest = lambda *args: "query-sha"

        def forbidden(*args):
            raise AssertionError(f"Opened inputs or keys before accepting the blind seal: {args}")

        study.source_bytes = forbidden
        reject("early score before blind release", study.score, root, anchors=anchors)
        blind = study.open_phase(root, "blind")
        for filename in study.STAGE_FILES["blind"]:
            study.save(blind / filename, {"test": filename})
        study.release(blind, {"fitted_state_release": study.digest(fit / "release.json"), "queries": "query-sha"},
                      monotonic(), {})
        reject("score opening data without external anchor", study.score, root, anchors=anchors)
        early = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        rows = [{"stage": "fit", "sha256": study.digest(fit / "release.json"), "next_stage_absent": "blind", "utc": early},
                {"stage": "blind", "sha256": study.digest(blind / "release.json"), "next_stage_absent": "scored",
                 "utc": datetime.now(timezone.utc).isoformat()}]
        study.save_lines(anchors, rows)
        reject("backdated anchor", study.check_anchors, root, "blind", anchors)
        changed = blind / "predictions.jsonl"
        changed.write_text("modified only in synthetic scratch")
        reject("changed blind output", study.check_release, blind)

    return rejections


def cross_fixture(study, learner):
    pixels = ("0" * 64, "1" * 64, "1" + "0" * 63, "11" + "0" * 62, "0" * 62 + "11")
    acquisition = {"narrow": [counts(pixels[0])] * 32 + [counts(pixels[1])] * 32,
                   "varied": [counts(pixels[2])] * 32 + [counts(pixels[3])] * 32}
    targets = [0] * 32 + [1] * 32
    fitted = {arm: {convention: fit_reference(acquisition[arm], [bit ^ (convention == "opposite") for bit in targets])
                    for convention in ("ordinary", "opposite")} for arm in ARMS}
    require(fitted["narrow"]["ordinary"]["masks"] != fitted["varied"]["ordinary"]["masks"], "Synthetic arms do not differ")
    checkpoints = {f"{arm}-{law}-{version}": fitted_physical_archive(law, fitted[arm][version])
                   for arm, law, version in product(ARMS, LAWS, ("ordinary", "opposite"))}
    actual, details, interventions, orders = {}, {}, {}, {}
    for arm, law in product(ARMS, LAWS):
        study.record_actions([tuple(map(int, row)) for row in pixels], arm, law, learner.KnotLearner, checkpoints,
                             learner.PARTITION_COUNT, actual, details, interventions, orders)
    expected = {f"{arm}-{law}-{condition}": [committee(counts(row), groups)[0] for row in pixels]
                for arm, conditions in calibrate_conditions(fitted).items()
                for law, (condition, groups) in product(LAWS, conditions.items())}
    require(equivalent(actual, expected), "Synthetic crossed reads differ")
    require({key: row["sha256"] for key, row in interventions.items()} == expected_checkpoint_digests(fitted),
            "Synthetic crossed recipients changed state outside the intervention")
    return {"synthetic_pixels": len(pixels), "intervention_states": len(interventions),
            "complete_anchor_stage_chain_required": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    parser.add_argument("prior_learner", type=Path)
    args = parser.parse_args()
    source = module_at(args.producer / "study.py")
    previous = module_at(args.prior_learner)
    print(json.dumps({"phase_mutations_rejected": stage_mutations(source), "crossed_memory": cross_fixture(source, previous)},
                     indent=2, sort_keys=True))
