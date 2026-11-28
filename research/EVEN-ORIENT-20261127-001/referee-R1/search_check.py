"""Reproduce the declared searches at the freeze, at closure, and in the current index."""
import argparse
import json
from pathlib import Path
import shlex
import sqlite3
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import track


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser()
    track.objects_arguments(parser)
    readme = (HERE.parent / "README.md").read_text()
    section = track.prior_work_section(readme)
    commands = track.prior_work_commands(section)
    evidence = []
    for ref in ("dfa155dd8", "cb6e7cc082", "current"):
        con = sqlite3.connect(":memory:")
        db = "research/tracking.db"
        con.deserialize((ROOT/db).read_bytes() if ref == "current" else git("show", f"{ref}:{db}"))
        con.row_factory = sqlite3.Row
        for command in commands:
            args = parser.parse_args(shlex.split(command)[2:])
            hits = [r["epic"] for r in track.search_objects(args, con=con)["index"][:3]]
            evidence.append({"index":ref, "query":args.query, "first three":hits,
                             "missing from prior-work section":[k for k in hits if f"`{k}`" not in section]})
        con.close()
    query = "fourfold coverage parity balanced orientations irreducible choices quadrangulations census larger sampled starts"
    args = parser.parse_args([query,"--until","2026-11-27","--exclude",HERE.parent.name])
    hits = track.search_objects(args)["index"]
    terms = r"K_\{?3,4|quadrangulat|fourfold coverage"
    files = git("grep","-il","-E",terms,"dfa155dd8^","--","research/**/*.md","docs/KNOT_INTUITION.md",
                "publication/knotlab/INTUITIONS.md").decode().splitlines()
    gate = track.objects_gate(HERE.parent / "README.md")
    result = {"objects-gate current":gate, "historical top three":evidence, "additional query":query,
              "additional query results":[[r["epic"],r["record"]] for r in hits],
              "pre-freeze full-text query":terms, "pre-freeze matching files":files}
    (HERE/"search_counts.json").write_text(json.dumps(result,indent=2)+"\n")
    for row in evidence:
        print(row["index"],row["first three"],row["missing from prior-work section"])


if __name__ == "__main__":
    main()
