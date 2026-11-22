"""Verify the frozen four-name meter archive in either repository layout."""

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path


EPIC = "SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001"
ARCHIVE_SHA256 = "f1818ba9e54e8a4336c42e0b809823ca96071cc292b3dbad70c6edbc11c8614e"
CHECKER = "tools/knotlab/knots.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    root = parser.parse_args().repository.resolve()
    study = root / "research" / (EPIC + "B")
    archive = (study / "two_shared_evidence.json.gz").read_bytes()
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("The frozen meter archive differs from its recorded checksum.")
    archived_json = gzip.decompress(archive)
    expected_checker = json.loads(archived_json)["source_sha256"][CHECKER]

    sys.path.insert(0, str(study))
    from two_shared_replay import build

    replay = build()
    if replay["source_sha256"][CHECKER] != expected_checker:
        # Public knotlab renames the guide in this one docstring. Accept only
        # the substitution that reconstructs the entire archived checker.
        public_title = b"See INTUITIONS.md for the intuition this formalizes."
        source_title = b"See docs/" + b"KNOT_" + b"INTUITION.md for the intuition this formalizes."
        checker = (root / CHECKER).read_bytes()
        if checker.count(public_title) != 1:
            raise ValueError("The recorded guide-title substitution is absent.")
        recovered = checker.replace(public_title, source_title, 1)
        if hashlib.sha256(recovered).hexdigest() != expected_checker:
            raise ValueError("The checker differs beyond its published guide title.")
        replay["source_sha256"][CHECKER] = expected_checker

    replay_json = (json.dumps(replay, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if replay_json != archived_json:
        raise ValueError("The recomputed source bindings or scientific records differ.")
    print(f"Verified all {replay['summary']['instrument_settings']} instrument settings "
          f"and the complete frozen archive {ARCHIVE_SHA256}.")


if __name__ == "__main__":
    main()
