"""Exhaust the two-copy, one-input link test on the selected rule."""
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import sys


FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
PREVIOUS = "BRANCH-DEPTH-20261112-001C"
sys.path.insert(0, str(next((ROOT / "experiments" / PREVIOUS).glob("*_port_census"))))
from census import SOURCE, allowed_local_words, bits


def is_ternary_bond(rows):
    return (0 < len(rows) < 8
            and all((1-a, 1-b, 1-c) in rows for a, b, c in rows)
            and all(len({(word[i], word[j]) for word in rows}) == 4
                    for i, j in combinations(range(3), 2)))


def classify(words, outgoing):
    """Keep each full incoming tuple until the two-bit tables are compared."""
    ports = sorted({w & 7 for w in words})
    candidates = []
    for top in range(3):
        for out_slot, output in enumerate(outgoing):
            if output < 3:
                continue
            for helper in range(3, 7):
                if helper == output:
                    continue
                by_port = defaultdict(set)
                triples = set()
                for w in words:
                    pair = (w >> output & 1, w >> helper & 1)
                    by_port[w & 7].add(pair)
                    triples.add((w >> top & 1, *pair))
                marginal = is_ternary_bond(triples)
                conflicts = [(p, q) for p, q in combinations(ports, 2)
                             if ((p ^ q) >> top & 1) == 0 and by_port[p] != by_port[q]]
                candidates.append(dict(top=top, out_slot=out_slot, output=output, helper=helper,
                                       marginal_bond=marginal, uniform=not conflicts,
                                       conflict=list(conflicts[0]) if conflicts else None,
                                       triple_table=sorted(triples)))
    return candidates


def main():
    with gzip.open(SOURCE / "sample_0.jsonl.gz", "rt") as source:
        definition, = next(json.loads(line)["defs"] for n, line in enumerate(source, 1) if n == 4710)
    allowed, first_words, _, _ = allowed_local_words(definition)
    assert allowed == set(range(8)) and definition[1] == 2
    first = next(args for kind, args in definition[2] if kind == "SELF")
    second_names = first + [5, 6]
    outgoing = [second_names[i] for i in first]
    allowed_words = {w for w, _ in first_words}
    words = [w for w in range(128)
             if w & 31 in allowed_words and bits(w, second_names) in allowed_words]
    candidates = classify(words, outgoing)
    # With every other value free, imposing just NAE on the tested triple
    # must give that exact same six-state table over either full-input fiber.
    positive = [w for w in range(128) if bits(w, (0, 5, 6)) not in (0, 7)]
    assert any(c["top"] == 0 and c["output"] == 5 and c["helper"] == 6
               and c["marginal_bond"] and c["uniform"] for c in classify(positive, outgoing))
    assert not any(c["marginal_bond"] for c in classify(range(128), outgoing))
    genuine = [c for c in candidates if c["marginal_bond"] and c["uniform"]]
    carries = [[physical_name, slot] for slot, physical_name in enumerate(outgoing) if physical_name < 3]
    result = dict(sample_file="sample_0.jsonl.gz", line=4710,
                  variables=["a", "b", "c", "x0", "y0", "x1", "y1"],
                  incoming_words=sorted(allowed), final_ports=outgoing,
                  before_constraints=128, assignments=len(words),
                  assignments_by_input=dict(sorted(Counter(w & 7 for w in words).items())),
                  candidates=len(candidates), marginal_bonds=sum(c["marginal_bond"] for c in candidates),
                  uniform_tables=sum(c["uniform"] for c in candidates), genuine_links=len(genuine),
                  literal_carries=carries, tests=candidates)
    out = ROOT / "artifacts" / FAMILY.parent.name / FAMILY.name / "result.json"
    result_text = json.dumps(result, indent=2) + "\n"
    if sys.argv[1:] == ["--write"]:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result_text)
    elif sys.argv[1:] or out.read_text() != result_text:
        raise SystemExit("result mismatch or unexpected argument")
    print({key: result[key] for key in ("assignments", "final_ports", "candidates", "marginal_bonds",
                                         "uniform_tables", "genuine_links", "literal_carries")})


if __name__ == "__main__":
    main()
