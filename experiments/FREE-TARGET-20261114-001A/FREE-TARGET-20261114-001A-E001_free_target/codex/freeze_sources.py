"""Freeze hashes of the job, its helpers, reused repository code, and inputs."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import json
import platform
import sys
from types import ModuleType

import inputs


def main():
    paths = inputs.load_paths()
    import bounded
    import witness_check
    import pysat
    import numpy
    files = set(inputs.HERE.glob("*.py"))
    # The reused census loads some modules by spec without registering them
    # in sys.modules. Follow its module references as well as normal imports.
    pending, visited = [paths], set()
    while pending:
        module = pending.pop()
        if id(module) in visited:
            continue
        visited.add(id(module))
        name = getattr(module, "__file__", None)
        if not name:
            continue
        path = inputs.Path(name).resolve()
        if not path.is_relative_to(inputs.ROOT) or ".venv" in path.parts:
            continue
        if path.suffix == ".py":
            files.add(path)
        pending.extend(value for value in vars(module).values() if isinstance(value, ModuleType))
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name:
            path = inputs.Path(name).resolve()
            if path.suffix == ".py" and path.is_relative_to(inputs.ROOT) and ".venv" not in path.parts:
                files.add(path)
    files.add(inputs.ROOT / "scripts/longrun.py")
    for path in files:
        ast.parse(path.read_text(), filename=str(path))
    files.update((inputs.POPULATION, inputs.CENSUS_FILE, inputs.SAMPLE / "G.jsonl", inputs.SAMPLE / "phase2.jsonl"))
    files.add(inputs.ROOT / "docs/tooling/shared-runner.md")
    for filename in ("preregistration.md", "codex_spec.md"):
        files.add(inputs.ROOT / "research/FREE-TARGET-20261114-001" / filename)
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    interpreter=sys.executable, python=platform.python_version(),
                    numpy=numpy.__version__, pysat=pysat.__version__,
                    sha256={str(path.relative_to(inputs.ROOT)): inputs.digest(path) for path in sorted(files)},
                    bytecode_disabled=sys.dont_write_bytecode)
    (inputs.HERE / "source_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(files=len(files), interpreter=manifest["interpreter"],
                          bytecode_disabled=manifest["bytecode_disabled"])))


if __name__ == "__main__":
    main()
