"""Freeze code/input digests without copying the read-only source material."""
from __future__ import annotations

import ast
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-existing", type=Path,
                        help="preserve the prior manifest at this CODEX path before refreezing")
    args = parser.parse_args()
    target = HERE / "source_manifest.json"
    if target.exists():
        if args.archive_existing is None:
            raise FileExistsError("source manifest already frozen; preserve its evidence")
        backup = inputs.permitted(HERE / args.archive_existing)
        if backup.exists():
            raise FileExistsError("previous-manifest archive already exists")
        backup.write_bytes(target.read_bytes())
    for source in HERE.glob("*.py"):
        ast.parse(source.read_text(), filename=str(source))
    import brute
    import direct
    brute._language()
    direct._search_module()
    sources = inputs.source_hashes()
    explicit = [inputs.ROOT / "research/CENSUS-FORGET-20261114-001/referee-R1/codex/target_inventory.py",
                inputs.ROOT / "research/CENSUS-FORGET-20261114-001/referee-R1/codex/direct_other_targets.py",
                brute.INPUT, direct.SOURCE]
    for source in list(HERE.glob("*.py")) + explicit:
        sources[str(source.relative_to(inputs.ROOT))] = inputs.digest(source)
    for module in tuple(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            source = Path(filename).resolve()
            if source.suffix == ".py" and source.is_relative_to(inputs.ROOT) and ".venv" not in source.parts:
                sources[str(source.relative_to(inputs.ROOT))] = inputs.digest(source)
    result = dict(schema_version=1, purpose="CARRY frozen implementation handoff; no input copies",
                  specification="preregistration addendum A1-A8, resolved 2026-11-14",
                  sha256=dict(sorted(sources.items())), python=sys.version,
                  population_families=5964, population_draws=6028)
    inputs.dump(target, result)
    print(json.dumps(dict(files=len(sources), manifest=str(target))))


if __name__ == "__main__":
    main()
