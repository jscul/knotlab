"""Re-run the frozen producer in scratch and compare its deterministic payloads."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parents[1]
FAMILY = RECORD.name + "-E001_drawings"
STUDY = ROOT / "experiments" / RECORD.name / FAMILY / "study.py"
ORIGINAL = ROOT / "artifacts" / RECORD.name / FAMILY


def reproduce():
    if not (ORIGINAL / "scored/release.json").is_file():
        raise ValueError("Replay requires the completed official score")
    count = 0
    with TemporaryDirectory(prefix="varied-letter-replay-") as temp:
        out = Path(temp)
        anchors = out / "anchors.jsonl"
        for command, phase, successor in (("train", "fit", "blind"), ("predict", "blind", "scored"),
                                           ("score", "scored", None)):
            subprocess.run([sys.executable, "-B", str(STUDY), command, "--out", str(out),
                            "--anchors", str(anchors)], check=True)
            release = out / phase / "release.json"
            reproduced = json.loads(release.read_bytes())["files"]
            archived = json.loads((ORIGINAL / phase / "release.json").read_bytes())["files"]
            if reproduced != archived:
                raise ValueError(f"Different payloads in {phase}")
            for name, expected in archived.items():
                for scope in (ORIGINAL, out):
                    if sha256((scope / phase / name).read_bytes()).hexdigest() != expected:
                        raise ValueError(f"File disagrees with {phase} release: {name}")
            count += len(archived)
            if successor:
                assert not (out / successor).exists()
                receipt = {"stage": phase, "sha256": sha256(release.read_bytes()).hexdigest(),
                           "utc": datetime.now(timezone.utc).isoformat(), "next_stage_absent": successor}
                with anchors.open("x" if phase == "fit" else "a") as stream:
                    stream.write(json.dumps(receipt) + "\n")
    return count


if __name__ == "__main__":
    print(f"All {reproduce()} deterministic payloads matched the original release bytes.")
