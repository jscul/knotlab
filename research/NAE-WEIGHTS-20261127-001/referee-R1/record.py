"""Verify freeze order, predecessor records and the archived inputs to the referee check."""
import hashlib
import json
from pathlib import Path
import resource
import subprocess
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PYTHON = ROOT / ".venv/bin/python"
EPIC = HERE.parent.name
FREEZE = "dbbadef7b0"
CLOSURE = "deb18e53b7"
STUDY = HERE.parent.relative_to(ROOT)
QUERIES = [
    "correlation knot trees steps apart not all equal mixed arity holder separation marked pairs arrival",
    "signed counts ring of four reader far edit mean signs",
    "four point cumulant separated pairs not all equal",
    "present uniform weighting old marked pair extensions not all equal",
    "weightings factor listed rules counting from finish fixed history",
]


def run(*args):
    if args[0] == "git":
        args = ("git", "-c", "core.packedGitWindowSize=32m", "-c", "core.packedGitLimit=64m", *args[1:])
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


def at(commit, path):
    return run("git", "show", f"{commit}:{path}")


def search(query, limit):
    args = [PYTHON, "-B", "scripts/track.py", "objects", query, "--until", "2026-11-27",
            "--exclude", EPIC, "--limit", str(limit), "--json"]
    rows = json.loads(run(*args))
    return {k: [r["id"] for r in values] for k, values in rows.items() if values}



def check_projected_supports():
    # Match the canonical checker's inputs to the actual projected rows first.
    cases = json.loads((HERE / "joint.json").read_text())["quartets with identical proper marginal tables"]
    case, = (c for c in cases.values() if len(c["knots"]) == 14)
    def check(cnf, loops, contact):
        raw = run("env", "PYTHONPATH=tools", PYTHON, "-B", "-m", "knotlab", "check",
                  "--cnf", cnf, "--loops", *loops, "--contact", contact, "--json")
        return json.loads(raw)
    local = check("A B C; ~A ~B ~C", ["A","B"], "C")
    for rows in case["conditional rows for each knot in listed order"]:
        assert sorted(r[0] for r in rows if r[1] > 0) == local["allowed"]
    full = check("A ~A", ["A","B","C"], "D")
    for reading in case["readings"]:
        counts = reading["complete joint counts in binary integer order"]
        assert [format(i,"04b") for i,n in enumerate(counts) if n > 0] == full["allowed"]
    assert local["is_knot"] and not full["binding"]
    return {"each of fourteen listed rules": local, "each four-distinction reading": full}



def main():
    resource.setrlimit(resource.RLIMIT_AS, (1024**3,) * 2)
    start = perf_counter()
    search(QUERIES[0], 8)
    print(f"One-query pilot {perf_counter()-start:.3f}s for five queries", flush=True)
    queries = {q: search(q,8) for q in QUERIES}
    files = [
        "research/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/tree_delays.md",
        "research/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/samples.md",
        "research/TWO-COUNTINGS-20261125-001A/results.md",
        "research/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001B/results.md",
        "research/DISTANCE-ORDER-20261117-001/referee-R1/report.md",
        "research/CUMULANT-DIST-20261118-001/referee-R1/report.md",
        "research/SIGNED-COUNT-20261126-001/README.md",
        "research/SIGNED-COUNT-20261126-001/referee-R1/report.md",
        "research/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001/decision.md",
        "research/FACTOR-WEIGHTS-20261126-001/decision.md",
        "research/ONE-STATEMENT-20261127-001/advisor/answer_nae.md",
        "research/BINDING-20261126-001/referee-R1/report.md",
    ]
    prior = {p:hash_bytes(at(FREEZE,p)) for p in files}
    study_code, data = STUDY / "weights.py", STUDY / "weights.json"
    archive = "research/FORBID-EDITS-20261126-001/starts.json"
    frozen = sorted(run("git","ls-tree","--name-only",f"{FREEZE}:{STUDY}").decode().splitlines())
    closed = sorted(run("git","ls-tree","--name-only",f"{CLOSURE}:{STUDY}").decode().splitlines())
    run("git","merge-base","--is-ancestor",FREEZE,CLOSURE)
    results = dict(freeze=FREEZE,closure=CLOSURE,folder_at_freeze=frozen,folder_at_closure=closed,
                   same_source=at(FREEZE,study_code)==at(CLOSURE,study_code)==(ROOT/study_code).read_bytes(),
                   same_output=at(CLOSURE,data)==(ROOT/data).read_bytes(),
                   same_roster=at(FREEZE,archive)==(ROOT/archive).read_bytes(),
                   source_hash=hash_bytes(at(FREEZE,study_code)), output_hash=hash_bytes(at(CLOSURE,data)),
                   roster_hash=hash_bytes(at(FREEZE,archive)), prior_files_at_freeze=prior,
                   index_queries=queries, projected_supports=check_projected_supports())
    assert results['same_source'] and results['same_output'] and results['same_roster']
    assert 'weights.json' not in frozen and 'weights.json' in closed
    (HERE/"record.json").write_text(json.dumps(results,indent=2)+"\n")


if __name__ == "__main__":
    main()
