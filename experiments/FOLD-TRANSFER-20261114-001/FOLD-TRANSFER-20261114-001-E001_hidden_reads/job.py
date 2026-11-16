"""Exact transfer on two to four joined copies. Run directly to verify the saved panel."""

import hashlib
import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

from source_rules import HERE, LEGACY, READS, ROOT, TICKET, replay_sources

NOTE = ROOT / "research" / TICKET
OUT = ROOT / "artifacts" / TICKET / HERE.name
sys.path.insert(0, str(NOTE))
from whole_pattern import plain_table_tree, raw_table


def predict_table(sources, reads):
    """Evaluate the table selected at each supplied join, in binary input order."""
    local = [source["tables"][str(read)] for source, read in zip(sources, reads, strict=True)]
    output = []
    for x in product((0, 1), repeat=2 * len(local) + 1):
        bit = x[0]
        for i, table in enumerate(local):
            address = 4 * bit + 2 * x[2 * i + 1] + x[2 * i + 2]
            bit = int(table[address])
        output.append(str(bit))
    return "".join(output)


class QueryLearner:
    """Keep all library functions consistent with the bits the task has returned."""

    def __init__(self, candidates):
        self.tables = sorted(set(candidates))
        self.masks = [
            sum((value == "1") << i for i, value in enumerate(column))
            for column in zip(*self.tables, strict=True)
        ]

    def identify(self, ask):
        possible = (1 << len(self.tables)) - 1
        transcript = []
        while (count := possible.bit_count()) > 1:
            def balance(index):
                ones = (possible & self.masks[index]).bit_count()
                return min(ones, count - ones)

            row = max(range(len(self.masks)), key=balance)
            label = ask(row)
            if label not in (0, 1):
                raise ValueError(f"Nonbinary output at {row}: {label}")
            possible &= self.masks[row] if label else ~self.masks[row]
            if not possible:
                raise ValueError("No candidate agrees with the requested labels")
            transcript.append((row, label, possible.bit_count()))
        return self.tables[possible.bit_length() - 1], transcript


def run_panel(sources):
    depth = len(sources)
    recipes = list(product(READS, repeat=depth))
    candidate_tables = {reads: predict_table(sources, reads) for reads in recipes}
    learner = QueryLearner(candidate_tables.values())
    plain = plain_table_tree(candidate_tables.values())
    rows = []
    for reads in recipes:
        actual = raw_table(sources, reads)
        if not set(actual) <= {"0", "1"}:
            raise ValueError(f"Raw system has a missing or ambiguous output: {reads}")
        selected, transcript = learner.identify(lambda i: int(actual[i]))
        asked = {i for i, _, _ in transcript}
        wrong = [i for i, (a, b) in enumerate(zip(selected, actual, strict=True)) if a != b]
        if candidate_tables[reads] != actual or wrong:
            raise ValueError(f"Raw and transferred outputs disagree for {reads}: {wrong[:8]}")
        if [(i, b) for i, b, _ in transcript] != plain[actual]:
            raise ValueError(f"Plain full-table learner disagrees for {reads}")
        # An outside-family target can return exactly the same queried labels.
        changed = next(i for i in range(len(actual)) if i not in asked)
        mutant = actual[:changed] + str(1 - int(actual[changed])) + actual[changed + 1:]
        other, mutant_transcript = learner.identify(lambda i: int(mutant[i]))
        if (mutant in learner.tables or mutant_transcript != transcript
                or sum(x != y for x, y in zip(other, mutant, strict=True)) != 1):
            raise ValueError("Out-of-family control failed")
        parity_disagreements = sum(int(bit) != i.bit_count() % 2 for i, bit in enumerate(actual))
        rows.append({
            "reads": list(reads), "oracle_table": actual, "queries": transcript,
            "unqueried_inputs": len(actual) - len(asked), "held_out_errors": len(wrong),
            "outside_family_flipped_row": changed, "outside_family_held_out_errors": 1,
            "errors_of_ordinary_xor": parity_disagreements,
        })

    source5 = sources[0]["tables"]["5"]
    damaged = dict(sources[0], tables={**sources[0]["tables"], "5": str(1 - int(source5[0])) + source5[1:]})
    primary = candidate_tables[(5,) * depth]
    corrupted = predict_table([damaged, *sources[1:]], (5,) * depth)
    mutation_errors = sum(a != b for a, b in zip(primary, corrupted, strict=True))
    if not mutation_errors or rows[0]["errors_of_ordinary_xor"]:
        raise ValueError("Wrong-entry control or known-wiring XOR comparison failed")

    split = raw_table(sources, (5,) * depth, sever_after=0)
    if set(split) != {"u"}:
        raise ValueError("Splitting the shared distinction did not free every terminal output")
    return {
        "copies": depth, "distinct_functions": len(learner.tables),
        "external_inputs": len(primary), "candidate_input_evaluations": len(recipes) * len(primary),
        "binary_lower_bound_on_worst_queries": (len(learner.tables) - 1).bit_length(),
        "query_count_histogram": dict(sorted(Counter(str(len(r["queries"])) for r in rows).items())),
        "split_join_ambiguous_inputs": split.count("u"), "wrong_source_entry_errors": mutation_errors,
        "held_out_predictions": sum(r["unqueried_inputs"] for r in rows), "targets": rows,
    }


def setup(params):
    global sources
    sources = replay_sources()


def cases():
    yield "source", 0
    for depth in (2, 3, 4):
        yield f"copies-{depth}", depth


def run(case_id, payload):
    if case_id == "source":
        files = [Path(__file__), HERE / "source_rules.py", NOTE / "whole_pattern.py",
                 NOTE / "preregistration.md", HERE / "contract.json", LEGACY / "result.json"]
        return {
            "sources": sources,
            "sha256": {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
        }
    return run_panel(sources[:payload])


def verify_saved():
    records = [json.loads(line) for line in (OUT / "results.jsonl").read_text().splitlines()]
    saved = {r["case"]: r for r in records}
    setup({})
    for case_id, payload in cases():
        fresh = json.loads(json.dumps(run(case_id, payload)))
        if saved[case_id]["status"] != "ok" or saved[case_id]["result"] != fresh:
            raise ValueError(f"Saved result did not reproduce: {case_id}")
        if payload:
            print(f"{payload} copies: {fresh['distinct_functions']} functions, "
                  f"query histogram {fresh['query_count_histogram']}, "
                  f"{fresh['held_out_predictions']} correct unqueried outputs")
        else:
            print("Four first-target stops, post-disturbance laws and file digests reproduced.")


if __name__ == "__main__":
    verify_saved()
