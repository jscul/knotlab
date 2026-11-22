"""Check release isolation using only temporary artificial phase artifacts."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from synthetic_tree import module_at
from tree_oracle import digest, require


def verify(source):
    phase = module_at(source / "study.py")
    rejected = []

    def reject(description, action, *args):
        try:
            action(*args)
        except (ValueError, FileNotFoundError, FileExistsError):
            rejected.append(description)
        else:
            raise ValueError(f"Accepted {description}")

    raw = "0" * 64
    safe = {"id": digest(raw.encode()), "pixels": raw}
    fixtures = {
        "forbidden row metadata": [{**safe, "label": "L"}], "malformed bitmap type": [{**safe, "pixels": [0] * 64}],
        "bad length": [{**safe, "pixels": raw[:-1]}], "bad digit": [{**safe, "pixels": "2" + raw[1:]}],
        "wrong identity": [{**safe, "id": "0" * 64}], "duplicate bitmap identity": [safe, safe],
    }
    for failure, rows in fixtures.items():
        data = "\n".join(json.dumps(row) for row in rows).encode("ascii")
        reject(failure, phase.io.public_rows, data)
    require(phase.io.public_rows(json.dumps(safe).encode("ascii")) == [safe], "Malformed synthetic fixture acceptance")

    with TemporaryDirectory(prefix="sealed-phase-", dir=Path(__file__).resolve().parent) as scratch:
        tree = Path(scratch)
        phase.FAMILY = tree
        phase.PANEL = tree / "panel"
        proposal = tree / "contract.json"
        proposal.write_text('{}')
        authority = tree / "approval.json"
        authority.write_text('{}')
        contract = {}
        anchors = tree / "external.jsonl"
        phase.preflight = lambda: (contract, authority)
        phase.io.source_digest = lambda _, path: digest(str(path.name).encode())

        def touch_forbidden(*args):
            raise AssertionError(f"Opened inputs before release and anchor guards completed: {args}")

        phase.io.source_bytes = touch_forbidden
        phase.score = touch_forbidden
        phase.implementations = touch_forbidden
        reject("early score before any upstream phases", phase.run, "scored", tree, anchors)
        reject("fit before the public sense release", phase.run, "fit", tree, anchors)

        now = datetime.now(timezone.utc) - timedelta(minutes=3)
        fixture_phases = ("sense", "fit", "pair", "blind")
        for step, name in enumerate(fixture_phases):
            folder = phase.io.open_phase(tree, name)
            for filename in phase.FILES[name]:
                phase.io.save(folder / filename, {"synthetic": filename})
            phase.io.save(folder / "release.json", {"contract": phase.io.digest(proposal),
                "parents": phase.parents(tree, name, contract, authority),
                "files": {name: phase.io.digest(folder / name) for name in phase.FILES[name]},
                "utc": (now + timedelta(seconds=3 * step)).isoformat()})
        phase.check_upstream(tree, "scored", contract, authority)
        reject("early score without externally anchored blind actions", phase.run, "scored", tree, anchors)
        reject("diagnose without external fit commitment", phase.run, "pair", tree, anchors)
        rows = []
        for name, successor, offset in (("fit", "pair", 4), ("blind", "scored", 10)):
            rows.append({"stage": name, "sha256": phase.io.digest(tree / name / "release.json"),
                         "next_stage_absent": successor, "utc": (now + timedelta(seconds=offset)).isoformat()})
        phase.io.save_lines(anchors, rows)
        phase.check_anchors(tree, "scored", anchors)
        bad = tree / "bad_anchors.jsonl"
        phase.io.save_lines(bad, [{**rows[0], "utc": now.isoformat()}, rows[1]])
        reject("backdated fit commitment", phase.check_anchors, tree, "scored", bad)

        (tree / "blind/predictions.jsonl").write_text("mutated scratch")
        reject("score with modified blind prediction bytes", phase.run, "scored", tree, anchors)
        reject("overwrite a phase directory", phase.io.open_phase, tree, "blind")
        reject("overwrite released model words", phase.io.save, tree / "fit/diagnostics.json", {})
    return {"synthetic_invalid_inputs_rejected": rejected, "fresh_and_public_pair_features_read": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    print(json.dumps(verify(parser.parse_args().producer), indent=2, sort_keys=True))
