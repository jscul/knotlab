"""Check each distinct exact relation with the unmodified knotlab CLI."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))

from longrun import load_results
from projection import Projection


def clause_excluding(names, word):
    return " ".join(f"~{name}" if word & (1 << i) else name for i, name in enumerate(names))


def exact_cnf(projection, names):
    if projection.kind == "nae":
        return "\n".join((" ".join(names), " ".join(f"~{name}" for name in names)))
    if projection.kind == "even_groups":
        clauses = []
        for mask in projection.data:
            group = [name for i, name in enumerate(names) if mask & (1 << i)]
            clauses.extend(
                clause_excluding(group, word)
                for word in range(1 << len(group)) if word.bit_count() % 2
            )
    else:
        allowed = set(projection.data)
        clauses = [
            clause_excluding(names, word)
            for word in range(1 << projection.width) if word not in allowed
        ]
    return "\n".join(clauses)


def canonical_check(projection):
    expected = projection.report()
    if not expected["eligible_arity"]:
        return {"projection": projection.spec(), "status": "ineligible_arity", **expected}
    names = [f"d{i}" for i in range(projection.width)]
    arguments = [
        "check", "--cnf", exact_cnf(projection, names), "--loops", *names[:-1],
        "--contact", names[-1], "--json",
    ]
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    if len(arguments[2].encode()) < 120_000:
        command = [sys.executable, "-B", "-m", "knotlab", *arguments]
        stdin = None
    else:
        # Pass large arguments to the same CLI through stdin to avoid the OS
        # per-argument size limit. The CLI and its algorithms are unchanged.
        command = [
            sys.executable, "-B", "-c",
            "import json, runpy, sys; sys.argv = ['knotlab'] + json.load(sys.stdin); "
            "runpy.run_module('knotlab', run_name='__main__')",
        ]
        stdin = json.dumps(arguments)
    run = subprocess.run(
        command, input=stdin, capture_output=True, text=True, check=True, cwd=ROOT, env=env,
    )
    result = json.loads(run.stdout)
    actual = {
        sum((value == "1") << i for i, value in enumerate(word)) for word in result["allowed"]
    }
    if (
        result["variables"] != names
        or result["erasure"] != "forgetting"
        or len(actual) != expected["allowed_count"]
        or any(not projection.allows(word) for word in actual)
        or any(result[key] != expected[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot"))
    ):
        raise ValueError(f"canonical checker disagrees on {projection.spec()}")
    return {"projection": projection.spec(), "status": "checked", **result}


def relation_key(projection):
    return hashlib.sha256(json.dumps(projection.spec(), sort_keys=True).encode()).hexdigest()


def setup(params):
    global CHECKS
    source_paths = [HERE / "projection.py"] + [
        ROOT / "tools" / "knotlab" / module
        for module in ("__main__.py", "cli.py", "knots.py", "relations.py")
    ]
    digest = hashlib.sha256()
    for path in source_paths:
        digest.update(path.read_bytes())
    if digest.hexdigest() != params["source_sha256"]:
        raise ValueError("projection or canonical CLI source digest mismatch")
    CHECKS = {}
    for record in load_results(Path(params["certificates"])).values():
        if record["status"] != "ok":
            continue
        for stage in record["result"]["stages"]:
            for row in stage["relations"]:
                projection = Projection.from_spec(row["projection"])
                CHECKS[relation_key(projection)] = row["projection"]


def cases():
    for key, spec in sorted(CHECKS.items()):
        yield key, spec


def run(case_id, spec):
    projection = Projection.from_spec(spec)
    if relation_key(projection) != case_id:
        raise ValueError("canonical relation case digest mismatch")
    return canonical_check(projection)
