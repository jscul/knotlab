"""Exact first-branch interface powers in the committed one-definition sample."""
from collections import Counter
import argparse
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"
OUT = ROOT / "artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census"


def bits(word, indices):
    return sum(((word >> var) & 1) << slot for slot, var in enumerate(indices))


def allowed_local_words(definition):
    ports, own, calls = definition
    assert ports == 3
    assert all(len(args) == len(set(args)) == 3 for _, args in calls)
    children = [args for kind, args in calls if kind == "SELF"]
    knots = [args for kind, args in calls if kind == "K"]
    assert children and len(children) + len(knots) == len(calls)
    passthrough = any(set(args) == {0, 1, 2} for args in children)
    # The usual limit retains the knot on the ports of a pass-through
    # definition, and it retains each child call with its own fresh locals.
    if passthrough:
        knots.append([0, 1, 2])
    candidates = [(word, [bits(word, args) for args in children])
                  for word in range(1 << (ports + own))
                  if all(bits(word, args) not in (0, 7) for args in knots)]
    while True:
        enabled = {word & 7 for word, _ in candidates}
        reduced = [(word, args) for word, args in candidates if all(s in enabled for s in args)]
        if len(reduced) == len(candidates):
            return enabled, reduced, passthrough, len(children)
        candidates = reduced


def power_data(allowed, words):
    transition = {(word & 7, args[0]) for word, args in words}
    assert {p for p, _ in transition} == allowed
    power = frozenset(transition)
    seen = {}
    rectangular = full = None
    while power not in seen:
        step = len(seen) + 1
        seen[power] = step
        left = {p for p, _ in power}
        right = {q for _, q in power}
        if rectangular is None and len(power) == len(left) * len(right):
            rectangular = step
        if full is None and len(power) == len(allowed) ** 2:
            full = step
        power = frozenset((p, q) for p, mid in power for other, q in transition if mid == other)
    return transition, rectangular, full, seen[power], len(seen) + 1 - seen[power]


def analyze():
    cases, counts, source_hashes = [], Counter(), {}
    for path in sorted(SOURCE.glob("sample_*.jsonl.gz")):
        source_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with gzip.open(path, "rt") as stream:
            for line, text in enumerate(stream, 1):
                raw = json.loads(text)
                if "limit_only" not in raw:
                    assert set(raw) == {"kind", "tries"}
                    continue
                counts["source_rows"] += 1
                if not raw["limit_only"] or len(raw["defs"]) != 1:
                    continue
                counts["one_definition_bottomless_only_candidates"] += 1
                definition = raw["defs"][0]
                allowed, words, passthrough, children = allowed_local_words(definition)
                if not allowed:
                    counts["empty_usual_limit"] += 1
                    continue
                relation, rectangular, full, start, period = power_data(allowed, words)
                cases.append(dict(file=path.name, line=line, first_dead=raw["first_dead"],
                                  own=definition[1], children=children, passthrough=passthrough,
                                  allowed=sorted(allowed), transition=sorted(relation),
                                  rectangular=rectangular, full=full,
                                  power_period_start=start, power_period=period))
    def hist(field):
        return dict(Counter(str(row[field]) for row in cases))
    return dict(source_files=source_hashes, exclusions=counts, eligible=len(cases),
                rectangular_powers=hist("rectangular"), full_powers=hist("full"),
                power_periods=hist("power_period"), rows=cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the audited per-case tables")
    args = parser.parse_args()
    data = analyze()
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "port_tables.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    print(json.dumps({k:v for k,v in data.items() if k not in ("source_files","rows")}, indent=2))


if __name__ == "__main__":
    main()
