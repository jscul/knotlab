"""Test one three-parent birth against ordinary growth on the same thirty-knot start."""

import argparse
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
from itertools import product
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

from cuts_construction import joint
from cuts_reader import Incidence, bits, inspect, mask, normal, span
from replay_growth import ARMS, grow


HERE = Path(__file__).resolve().parent


def prepare():
    cases = json.loads((HERE / "construct_born.json").read_text())["preparations"]
    base = Incidence(tuple(map(tuple, next(iter(cases.values()))["source supports"])))
    labels = [mask(d for d, own in base.owners.items() if len(own) == 1 and k <= own[0] < k + 5)
              for k in (0, 5, 10)]
    rows = [list(row) for row in base.supports]
    chosen = (18, 23, 28)
    name = max(base.owners) + 1
    for a, b in combinations(chosen, 2):
        rows[a].append(name)
        rows[b].append(name)
        name += 1
    ports = []
    for k in chosen:
        ports.append(name)
        rows[k].append(name)
        name += 1
    return Incidence(tuple(map(tuple, rows))), labels, ports


def canonical(values):
    """Translate exactly the missing value triples into clauses and check the projected relation."""
    sys.path.insert(0, str(HERE.parents[2] / "tools"))
    from knotlab.cli import main
    absent = ["".join(word) for word in product("01", repeat=3) if "".join(word) not in values]
    if not absent:
        return {"image": "full three-distinction relation", "K1": False}
    clauses = [" ".join(("~" if bit == "1" else "") + name for bit, name in zip(word, "abc"))
               for word in absent]
    cnf = "; ".join(clauses)
    reply = StringIO()
    with redirect_stdout(reply):
        status = main(["check", "--cnf", cnf, "--loops", "a", "b", "--contact", "c", "--json"])
    assert status == 0
    return {"cnf of measured relation": cnf, "canonical checker": json.loads(reply.getvalue())}


def run(pilot):
    start = perf_counter()
    source, labels, ports = prepare()
    total = labels[0] ^ labels[1] ^ labels[2]
    answer = {"pilot": pilot, "preparation": "Start with the thirty-knot three-ring preparation. In each of its three four-step alternatives choose the middle knot. Introduce one shared distinction between each chosen pair and one new loose distinction at each chosen knot. Keep the original ten loose distinctions of each ring as its named parity.",
              "source supports": source.supports, "three additional loose distinctions": ports,
              "ring parities": [list(bits(f)) for f in labels],
              "ring total equals the three additional loose distinctions at source":
                  not normal(total ^ mask(ports), source.laws),
              "source": joint(source, labels), "growth": {}}
    for arm in (ARMS[:1] if pilot else ARMS):
        after, status = grow(source.supports, arm)
        assert status == "funded"
        stage = Incidence(after)
        births = stage.checks[len(source.supports):]
        triple = [b for b in births if (b & source.all_names) == mask(ports)]
        assert len(triple) == 1
        without = [c for c in stage.checks if c != triple[0]]
        generic = inspect(stage, source, source, include_carriers=True)
        ring_image = joint(stage, labels)
        listed, valid_knots = stage.reader_spaces()
        answer["growth"][arm] = {
            "stage supports": stage.supports,
            "three-parent birth": list(bits(triple[0])),
            "private fresh distinction count": (triple[0] & ~source.all_names).bit_count(),
            "listed supports": len(listed), "listed supports whose projections are parity knots": len(valid_knots),
            "ring image rank after dropping only the three-parent birth law":
                len(span(normal(c, span(without)) for c in labels)),
            "ring image with every law": ring_image, "knot test": canonical(ring_image["joint values"]),
            "generic frozen search": generic}
    answer["seconds"] = perf_counter() - start
    return answer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    result = run(args.pilot)
    filename = "cuts_three_pilot.json" if args.pilot else "cuts_three.json"
    (HERE / filename).write_text(json.dumps(result, indent=2) + "\n")
    print(filename, result["seconds"])
