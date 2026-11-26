"""Check parity implication directly on two connected three-knot controls.

Two live knots each share two distinctions with the same dead holder. The two
examples vary only whether each live knot has a second loose distinction.
"""

import argparse
from itertools import product
import json
from pathlib import Path
import resource
import time

from growth import Roster, grow


def measure(extra):
    holdings = [[0, 1, 4], [2, 3, 5], [0, 1, 2, 3]]
    if extra:
        holdings[0].append(6)
        holdings[1].append(7)
    states = [bits for bits in product((0, 1), repeat=8 if extra else 6)
              if all(sum(bits[d] for d in places) % 2 == 0 for places in holdings)]
    roster = Roster.from_holdings(holdings)
    observed = {}
    for law in ("parity", "nae"):
        trace = grow(roster, 1, law)
        group, = [b for b in trace.rows[0] if len(b.parents) == 2]
        observed[law] = {"one-round end": trace.end, "births in round one": len(trace.rows[0]),
                         "parents of the join": [trace.start[p] for p in group.parents],
                         "fresh distinctions of the join": group.fresh}
    read = {bits[4] ^ bits[5] for bits in states}
    return {"holdings": holdings, "loose before birth": sorted(d for d in range(8 if extra else 6)
                                                              if sum(d in h for h in holdings) == 1),
            "old distinctions taken by the join": [4, 5], "allowed parity states of the start": len(states),
            "possible parities of the old distinctions taken": sorted(read),
            "even parity on taken distinctions implied by the start": read == {0},
            "every live knot parents the join": set(observed["parity"]["parents of the join"]) == roster.loose.keys(),
            "growth": observed}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("pilot", "both"))
    mode = parser.parse_args().mode
    resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))
    begin = time.monotonic()
    cases = [measure(False)] if mode == "pilot" else [measure(False), measure(True)]
    result = {"cases": cases, "seconds": time.monotonic() - begin,
              "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if mode == "both":
        Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
