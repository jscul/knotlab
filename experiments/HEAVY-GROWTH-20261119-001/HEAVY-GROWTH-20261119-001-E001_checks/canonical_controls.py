"""Check the literal allowed-state projection on every named initial junction."""
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys

from sources_span import labels, physical_words, row_span


def check(audit):
    catalog = {}
    answer = {}
    multiplicity = Counter()
    for name, source in sorted(audit["named_archive_starts"].items()):
        rows, _, _ = physical_words(source["sizes"], source["meetings"])
        span = row_span(rows)
        failures = []
        for i, support in enumerate(rows):
            sites = labels(support)
            words = [sum(1 << j for j, v in enumerate(sites) if word >> v & 1)
                     for word in span if word & ~support == 0]
            bad = tuple(x for x in range(1 << len(sites))
                        if any((x & word).bit_count() % 2 for word in words))
            key = len(sites), bad
            multiplicity[key] += 1
            if key not in catalog:
                variables = [f"x{j}" for j in range(len(sites))]
                clauses = [" ".join(("~" if x >> j & 1 else "") + v
                                    for j, v in enumerate(variables)) for x in bad]
                invocation = [sys.executable, "-B", "-m", "knotlab", "check",
                              "--cnf", ";".join(clauses), "--loops", *variables[:-1],
                              "--contact", variables[-1], "--json"]
                out = subprocess.check_output(invocation, env={**os.environ, "PYTHONPATH":"tools"})
                result = json.loads(out)
                assert len(result["allowed"]) == (1 << len(sites)) - len(bad)
                catalog[key] = result["is_knot"]
            if not catalog[key]:
                failures.append(i)
        assert failures == source["gate"]["K2_failed_junctions"]
        answer[name] = failures
    return dict(junctions=sum(multiplicity.values()), distinct_literal_truth_tables=len(catalog),
                failed_junctions=answer, erasure="forgetting")


if __name__ == "__main__":
    source, dest = map(Path,sys.argv[1:])
    result = check(json.loads(source.read_text()))
    dest.write_text(json.dumps(result,indent=2)+"\n")
    print(result)
