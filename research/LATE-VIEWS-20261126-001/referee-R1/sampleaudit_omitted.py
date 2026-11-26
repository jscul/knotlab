"""Check the two sharing-cell starts outside the frozen samples in round one."""

from argparse import ArgumentParser
import json
from resource import RUSAGE_SELF, getrusage
from time import perf_counter

from map_predict import evaluate
from regrow import grow
from sampleaudit import HERE, RESEARCH, read_rows


def main(pilot):
    start = perf_counter()
    sample = json.loads((HERE / "sampleaudit.json").read_text())
    omitted = sample["admission and overlaps with prior work"]["accepted starts with cells sharing a knot"]["outside current samples"]
    inspected = sorted(omitted)[:1] if pilot else sorted(omitted)
    result = []
    for law in ("nae", "parity"):
        archive = RESEARCH / "LAST-MERGE-20261126-001" / f"grown_fresh_{law}.jsonl.gz"
        older = {str(row["index"]): row for row in read_rows(archive) if str(row["index"]) in inspected}
        for index in inspected:
            first_round = grow(omitted[index]["holdings"], 1, law, trace_rounds=1)
            assert len(first_round["rows"]) == 1
            actual = first_round["rows"][0]
            original = evaluate(omitted[index]["holdings"], 1, law, "frozen")["rows"][0]
            revised = evaluate(omitted[index]["holdings"], 1, law, "graded")["rows"][0]
            if index in older:
                assert omitted[index]["holdings"] == older[index]["stars"] and actual == older[index]["rows"][0]
            result.append({"census index": int(index), "knot law": law,
                           "cells": omitted[index]["cells"], "earlier last-fall archive match": index in older,
                           "observed round one": actual, "direct birth witness": first_round["traces"][0],
                           "frozen reading from the start": original, "post hoc reading from the start": revised,
                           "readings that differ from direct growth": {
                               "frozen": [read for read in ("n", "sig0", "sig1") if original[read] != actual[read]],
                               "post hoc": [read for read in ("n", "sig0", "sig1") if revised[read] != actual[read]]}})
    return {"scope": "referee round-one follow-up outside the frozen denominator",
            "method": "Used the independent finite-map and direct-growth checks from this folder. Only round one was run here.",
            "cases": result, "seconds": round(perf_counter() - start, 3),
            "peak resident KiB": getrusage(RUSAGE_SELF).ru_maxrss}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    options = parser.parse_args()
    result = main(options.pilot)
    path = HERE / ("sampleaudit_omitted_pilot.json" if options.pilot else "sampleaudit_omitted.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path.name, result["seconds"], result["peak resident KiB"])
