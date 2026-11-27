"""Distinguish birth laws in a sufficient holder from birth laws essential on the complete grown stage."""

import argparse
from collections import Counter
import json
from time import perf_counter

from census_replay import HERE, StageReader, advance, inputs, local_candidates, read_rows


def check_stage(supports, old, witness):
    counts = Counter()
    seen = set()
    reader = StageReader(supports)
    for C, H, missing in local_candidates(supports, 4):
        if C in seen:
            continue
        seen.add(C)
        if reader.image(C) != missing or any(reader.reads(c) for c in C):
            continue
        views = [reader.view(c)[0] for c in C]
        essential = []
        for knot in H:
            selectors = [var if k != knot else -var for k, var in enumerate(reader.selectors)]
            for w in range(8):
                if missing & (1 << w):
                    required = [v if w & (4 >> j) else -v for j, v in enumerate(views)]
                    if reader.solver.solve(assumptions=selectors + required):
                        essential.append(knot)
                        break
        # A law outside H cannot be essential. H alone already gives the same image.
        facts = {
            "accepted": True,
            "every holder law essential on whole stage": tuple(essential) == H,
            "every law of stage essential": len(essential) == len(supports),
            "birth among the chosen holders": max(H) >= old,
            "birth essential on whole stage": any(k >= old for k in essential),
            "birth among holders but no birth essential on whole stage": max(H) >= old and all(k < old for k in essential),
        }
        for label, holds in facts.items():
            counts[label] += holds
            if holds and label not in witness:
                witness[label] = dict(supports=supports, carriers=C, holder=H, whole_stage_essential=essential,
                                      first_birth=old, missing=[format(w,"03b") for w in range(8) if missing & (1 << w)])
    reader.close()
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranks", type=int, nargs="+")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    start = perf_counter()
    archive = inputs()
    raw = read_rows("census_nae_[0-9].jsonl")
    counts, starts, witness = Counter(), Counter(), {}
    rows, funded = [], 0
    ranks = args.ranks or sorted(raw)
    for rank in ranks:
        S = archive[rank]
        grown = advance(S)
        if grown.status == "funded":
            funded += 1
            W = {}
            record = check_stage(grown.supports, len(S), W)
            assert record["accepted"] == raw[rank]["round 1"]["bonds"]
            assert record["birth among the chosen holders"] == raw[rank]["round 1"]["with a birth among the holders"]
            counts.update(record)
            starts.update(label for label, n in record.items() if n)
            for label, example in W.items():
                witness.setdefault(label, dict(archive_rank=rank, **example))
            rows.append([rank, dict(record)])
    data = dict(funded=funded, stages=len(ranks), bonds=counts, starts=starts, witnesses=witness,
                by_funded_start=rows, elapsed_seconds=round(perf_counter()-start, 4))
    (HERE / args.out).write_text(json.dumps(data, separators=(",", ":")) + "\n")
    print(json.dumps({k:v for k,v in data.items() if k not in ("witnesses","by_funded_start")},indent=1))


if __name__ == "__main__":
    main()
