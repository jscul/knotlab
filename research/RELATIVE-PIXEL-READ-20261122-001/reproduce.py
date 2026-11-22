"""Replay all deterministic payloads in scratch after the official score is released."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from custody import ARCHIVE, RECORD, witness


def reproduce():
    if not (ARCHIVE / "scored/release.json").is_file():
        raise ValueError("Official score has not been released")
    study = RECORD.parents[1] / "experiments" / RECORD.name / ARCHIVE.name / "study.py"
    count = 0
    with TemporaryDirectory(prefix="relative-pixel-replay-") as scratch:
        out = Path(scratch)
        anchors = out / "anchors.jsonl"
        for command, stage in (("sense", "sense"), ("train", "fit"), ("diagnose", "pair"),
                               ("predict", "blind"), ("score", "scored")):
            subprocess.run([sys.executable, "-B", str(study), command, "--out", str(out),
                            "--anchors", str(anchors)], check=True)
            original = json.loads((ARCHIVE / stage / "release.json").read_bytes())["files"]
            replay = json.loads((out / stage / "release.json").read_bytes())["files"]
            if replay != original:
                raise ValueError(f"Changed payload hashes at {stage}")
            for name, expected in original.items():
                for location in (ARCHIVE, out):
                    if sha256((location / stage / name).read_bytes()).hexdigest() != expected:
                        raise ValueError(f"Unexpected bytes in {stage}/{name}")
            count += len(original)
            if stage in ("fit", "blind"):
                witness(out, anchors, stage)
    return count


if __name__ == "__main__":
    print(f"All {reproduce()} deterministic payloads match the official run.")
