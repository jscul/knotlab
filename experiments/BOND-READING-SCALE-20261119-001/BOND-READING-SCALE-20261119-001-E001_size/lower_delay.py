"""Look for delayed obstructions to full pair tables in still-open small sources."""

import argparse
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from lower import (EXTEND_ROUND, ROOT, Arrangement, bond_readings, full_pair_extension, marked_maps,
                   mismatches, next_stage)
from lower_rollup import read_shards


def cut_pairs(exe, stage, kept):
    ends, adjacent, _ = stage.holder_graph()
    assert list(stage.labels) == list(range(len(stage.labels)))
    data = [f"{len(adjacent)} {len(stage.labels)} {kept}"]
    data.extend(f"{ends[x][0]} {ends[x][1]}" for x in stage.labels)
    result = subprocess.run([str(exe)], text=True, input="\n".join(data)+"\n", check=True, capture_output=True)
    values = [int(x) for x in result.stdout.split()]
    keys = list(combinations(range(kept), 2))
    assert len(values) == len(keys)
    return {key: None if value == -1 else value-1 for key, value in zip(keys, values)}


def replay(exe, row, depth_cap, junction_cap):
    source = Arrangement.parse(row["witness"]["current"])
    (_, pairs, triples), _, equations = bond_readings(source)
    count = len(source.labels)
    assert cut_pairs(exe, source, count) == pairs
    maps = [phi for phi in marked_maps(source, pairs, triples, 2)
            if not all(sum(source.label_bits[phi[x]] for x in s) in equations for s in source.stars)]
    stages, hits, changing_fresh = [source], [], []
    for _ in range(depth_cap):
        following = next_stage(stages[-1])
        if following is None or len(following.stars) > junction_cap or len(following.labels) > 128:
            break
        stages.append(following)
        later = cut_pairs(exe, following, len(following.labels))
        for phi in maps:
            fixed = {name: phi.get(name, name) for name in following.labels}
            if not mismatches(later, later, fixed):
                continue
            extension, old_entry = full_pair_extension(source, following, later, phi)
            case = {"permutation": sorted(phi.items()), "old_pair_differing": old_entry,
                    "depth": len(stages)-1}
            (changing_fresh if extension else hits).append(case)
    return {"source": [len(source.stars), count], "multiplicity": row["max_ordinary_meeting_multiplicity"],
            "old_maps": len(maps), "checked_stage_sizes": [(len(s.stars), len(s.labels)) for s in stages],
            "nonidentity_fresh_extension": changing_fresh, "failures": hits,
            "literal_stages": [[sorted(s) for s in stage.stars] for stage in stages] if hits else None}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("source", type=Path)
    cli.add_argument("--max-width", type=int, default=16)
    cli.add_argument("--future-depth", type=int, default=3)
    cli.add_argument("--future-junction-cap", type=int, default=21)
    args = cli.parse_args()
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    with tempfile.TemporaryDirectory(prefix="bond-lower-delay-") as d:
        exe = Path(d) / "cuts"
        subprocess.run(["c++", "-O3", "-std=c++20", str(Path(__file__).with_name("lower_delayed.cpp")), "-o", str(exe)], check=True)
        rows = [replay(exe, r, args.future_depth, args.future_junction_cap) for shard in read_shards(args.source)
                for r in shard["residual"] if r["current_width"] <= args.max_width
                and r["maps_by_outcome"].get("next_pair_extends_lifetime_open")]
    print(json.dumps({"maximum_source_width": args.max_width, "future_depth_cap": args.future_depth,
                      "future_ordinary_junction_cap": args.future_junction_cap, "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
