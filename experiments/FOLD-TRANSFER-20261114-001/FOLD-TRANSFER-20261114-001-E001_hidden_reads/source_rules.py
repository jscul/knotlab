"""Recover held source laws and read their externally specified interfaces."""

import json
import os
import sys
from collections import Counter
from itertools import product
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "FOLD-TRANSFER-20261114-001"
LEGACY = ROOT / "proofs/LEARN-PARITY-20261111-001A/LEARN-PARITY-20261111-001A-P001_learning_parity"
INPUTS = (0, 1, 4)
READS = (5, 6)
SEEDS = range(9000, 9004)


def read_interface(triples, signs):
    """Project all allowed eight-bit states onto three inputs and two reads."""
    observed = {x: set() for x in product((0, 1), repeat=3)}
    allowed = 0
    for state in product((0, 1), repeat=8):
        for i, triple in enumerate(triples):
            a, b, c = (state[p] ^ signs[3 * i + side] for side, p in enumerate(triple))
            if a == b == c:
                break
        else:
            allowed += 1
            inputs = tuple(state[p] for p in INPUTS)
            observed[inputs].add(tuple(state[p] for p in READS))

    if any(len(values) != 1 for values in observed.values()):
        raise ValueError(f"At least one input has a missing or ambiguous read: {observed}")
    outputs = [next(iter(values)) for values in observed.values()]
    table5, table6 = ("".join(str(pair[i]) for pair in outputs) for i in range(2))
    # With uniform inputs, choose the most frequent second output for each first output.
    counts = Counter(outputs)
    best = sum(max(counts[first, second] for second in (0, 1)) for first in (0, 1))
    witness = next((
        [format(i, "03b"), format(j, "03b")]
        for i, a in enumerate(outputs) for j, b in enumerate(outputs[:i])
        if a[0] == b[0] and a[1] != b[1]
    ), None)
    return {
        "allowed_source_states": allowed,
        "tables": {"5": table5, "6": table6},
        "input_classes": {"5": len(set(table5)), "6": len(set(table6)), "both": len(counts)},
        "best_correct_of_eight_predicting_6_from_5": best,
        "same_5_different_6_inputs": witness,
    }


def replay_sources():
    """Observe the two post-search reads in the original, unchanged first write."""
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Run with PYTHONHASHSEED=0 as in the source experiment")
    sys.path.insert(0, str(LEGACY))
    import parity_lib

    archived = json.loads((LEGACY / "result.json").read_text())["checks"]
    from hashlib import sha256

    for path, expected in archived["0 dependencies bound by hash"]["info"].items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Changed source dependency: {path}")
    sources = []
    read_map = parity_lib.L3.read_map3
    for seed in SEEDS:
        source = parity_lib.t1()
        archive_row = archived["rows"][f"T1 run {seed - 9000}"][0]
        snapshots = []

        def capture(pattern, signs, ports):
            snapshots.append(list(signs))
            return read_map(pattern, signs, ports)

        with patch.object(parity_lib.L3, "read_map3", side_effect=capture):
            rows = parity_lib.run(source, [archive_row["target"]], seed)
        if rows != [archive_row] or len(snapshots) != 2:
            raise ValueError(f"First stop and disturbance for seed {seed} did not replay: {rows}")
        stopped, held = snapshots
        interface = read_interface(source.K.pt, held)
        if interface["tables"]["5"] != archive_row["map after the disturbance"]:
            raise ValueError(f"Independent source enumeration disagrees at seed {seed}")
        sources.append({
            "seed": seed, "points_by_knot": source.K.pt, "stop_signs": stopped,
            "held_signs": held, "first_write": archive_row, **interface,
        })
    return sources
