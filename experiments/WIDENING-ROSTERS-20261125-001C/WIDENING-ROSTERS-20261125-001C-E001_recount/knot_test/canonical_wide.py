"""Canonical K1–K3 on every exact relation class, including wide holdings."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import canonical
from projection import Projection


def wide_check(projection):
    expected = projection.report()
    if not expected["eligible_arity"]:
        return {"projection": projection.spec(), "status": "ineligible_arity", **expected}
    names = [f"d{i}" for i in range(projection.width)]
    arguments = [
        "check", "--cnf", canonical.exact_cnf(projection, names), "--loops", *names[:-1],
        "--contact", names[-1], "--json",
    ]
    run = subprocess.run(
        [sys.executable, "-B", str(HERE / "wide_cli.py")],
        input=json.dumps(arguments), capture_output=True, text=True, check=True,
        cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")),
    )
    receipt = json.loads(run.stdout)
    observed = {
        sum((value == "1") << i for i, value in enumerate(word)) for word in receipt["allowed"]
    }
    if (
        receipt["variables"] != names
        or receipt["erasure"] != "forgetting"
        or len(observed) != expected["allowed_count"]
        or any(not projection.allows(word) for word in observed)
        or any(receipt[key] != expected[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot"))
    ):
        raise ValueError(f"canonical checker disagrees on {projection.spec()}")
    return {"projection": projection.spec(), "status": "checked", **receipt}


def setup(params):
    digest = hashlib.sha256()
    for file in ("canonical.py", "wide_cli.py"):
        digest.update((HERE / file).read_bytes())
    if digest.hexdigest() != params["adapter_sha256"]:
        raise ValueError("canonical checker adapter source digest mismatch")
    canonical.setup(params)


def cases():
    yield from canonical.cases()


def run(case_id, spec):
    projection = Projection.from_spec(spec)
    if canonical.relation_key(projection) != case_id:
        raise ValueError("canonical relation case digest mismatch")
    return wide_check(projection)
