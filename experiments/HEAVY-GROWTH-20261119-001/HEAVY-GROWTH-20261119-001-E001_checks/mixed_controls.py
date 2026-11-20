"""Compare every certified pair to direct growth on small labelled block rosters."""
from collections import Counter
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import json
import sys

from mixed_turns import run


def check():
    rows = Counter()
    with TemporaryDirectory() as td:
        base = Path(td)
        name = base / "start-00-age01"
        for width in range(2, 5):
            options = [s for k in range(2, width + 1)
                       for s in combinations(range(width), k)]
            seen = set()
            for mask in range(1, 1 << len(options)):
                groups = [frozenset(s) for i, s in enumerate(options) if mask >> i & 1]
                maxima = tuple(sorted(tuple(sorted(g)) for g in groups
                                      if all(not g < other for other in groups)))
                if maxima in seen:
                    continue
                seen.add(maxima)
                degrees = [len(set().union(*(set(g) for g in maxima if v in g)) - {v})
                           for v in range(width)]
                if not all(degrees):
                    continue
                with name.with_suffix(".txt").open("w") as output:
                    print(width, len(maxima), file=output)
                    for g in maxima:
                        print(*g, file=output)
                for suffix, vector in (("degrees", degrees), ("parents", [[0, 1]] * width)):
                    with gzip.open(name.with_suffix(f".{suffix}.json.gz"), "wt") as output:
                        json.dump(vector, output)
                r = run(base, 0, 1, width, width, 100, 100, width, 100, True, True)
                rows["rosters"] += 1
                rows["children"] += r["verified_children"]
                rows["certified_residuals"] += r["verified_residual_pairs"]
                rows[f"width_{width}"] += 1
    return dict(rows)


if __name__ == "__main__":
    result = check()
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
    print(result)
