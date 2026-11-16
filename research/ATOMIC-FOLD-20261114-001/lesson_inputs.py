"""Instantiate the six local input bits from the archived signed rules of Lesson 4.7."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "FOLD-TRANSFER-20261114-001"
RECORD = ROOT / "artifacts" / SOURCE / (SOURCE + "-E001_hidden_reads")


def allowed_states(source):
    points, signs = source["points_by_knot"], source["held_signs"]
    rows = []
    for state in product((0, 1), repeat=8):
        for i, triple in enumerate(points):
            values = {state[point] ^ signs[3 * i + j] for j, point in enumerate(triple)}
            if len(values) == 1:
                break
        else:
            rows.append(state)
    return rows


def local_masks(source):
    rows = allowed_states(source)
    if len(rows) != 8:
        raise ValueError("Unexpected number of allowed eight-bit states")
    masks = []
    for u, v, read, required in product((0, 1), (0, 1), (5, 6), (0, 1)):
        witnesses = {s[0] for s in rows if (s[1], s[4], s[read]) == (u, v, required)}
        # The two input readings were produced by separate earlier code.
        old_table = source["tables"][str(read)]
        expected = {h for h in (0, 1) if int(old_table[4*h + 2*u + v]) == required}
        if witnesses != expected:
            raise ValueError((source["seed"], u, v, read, required))
        masks.append(sum(1 << h for h in witnesses))
    return masks


def world_weights():
    manifest = json.loads((RECORD / "result.json").read_text())
    raw = (RECORD / "results.jsonl").read_bytes()
    if sha256(raw).hexdigest() != manifest["raw_sha256"]:
        raise ValueError("Archived raw source digest mismatch")
    source_case = next(r for line in raw.splitlines()
                       if (r := json.loads(line))["case"] == "source" and r["status"] == "ok")
    by_seed = {s["seed"]: local_masks(s) for s in source_case["result"]["sources"]}
    if set(by_seed) != {9000, 9001, 9002, 9003}:
        raise ValueError("Expected the four pre-existing source seeds")
    counts = Counter()
    for a, b, c in combinations(sorted(by_seed), 3):
        for x, y, z in product(by_seed[a], by_seed[b], by_seed[c]):
            counts[x | (y << 2) | (z << 4)] += 1
    return counts, {
        "source_raw_sha256": manifest["raw_sha256"],
        "source_mask_counts": {k: dict(sorted(Counter(v).items())) for k, v in by_seed.items()},
        "triples_of_sources": 4, "instances": sum(counts.values()), "distinct_worlds": len(counts),
    }


if __name__ == "__main__":
    counts, summary = world_weights()
    print(json.dumps(summary, indent=2))
