"""Exactly 1,000 frozen smoke families; never starts the full census."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random

from reach_dp import HERE
from run_census import all_keys, dump, read_rows, run_tasks


def timings(rows):
    seconds = sorted(r["seconds"] for r in rows if r.get("seconds") is not None)
    return dict(families=len(rows), total_seconds=sum(seconds),
                mean_seconds=sum(seconds)/len(seconds) if seconds else None,
                median_seconds=seconds[len(seconds)//2] if seconds else None,
                max_seconds=max(seconds, default=None))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    keys = all_keys()
    selected = random.Random(1113).sample(keys, 1000)
    dump(HERE/"smoke_selection.json", dict(seed=1113, keys=selected))
    info = run_tasks(selected, HERE/"smoke_families.jsonl", args.workers)
    old_info = HERE/"smoke_run_info.json"
    if info["written"] or not old_info.exists():
        dump(old_info, info)
    else:
        info = json.loads(old_info.read_text())
    rows = read_rows(HERE/"smoke_families.jsonl")
    eligible = sorted(r["key"] for r in rows if not r.get("class", "").startswith("S") and r.get("alt_differs"))
    # Section 7 invokes section 5, with its sample ceiling reduced to 200.
    alt_selected = random.Random(20261113).sample(eligible, min(200, len(eligible)))
    dump(HERE/"smoke_alt_selection.json", dict(seed=20261113, eligible=len(eligible), keys=alt_selected))
    alt_info = run_tasks(alt_selected, HERE/"smoke_alt.jsonl", args.workers, ray="last")
    alt_rows = read_rows(HERE/"smoke_alt.jsonl")
    if not alt_info["written"] and (HERE/"smoke_summary.json").exists():
        previous = json.loads((HERE/"smoke_summary.json").read_text())
        if previous.get("alternative_families") == len(alt_rows):
            alt_info = previous.get("alternative_run_info", alt_info)
    by_class, by_size = defaultdict(list), defaultdict(list)
    for row in rows:
        by_class[row["class"]].append(row)
        size = max(row.get("main_block_size") or 0, row.get("s_block_size") or 0)
        by_size[str(size)].append(row)
    total_family_seconds = sum(r["seconds"] for r in rows)
    summary = dict(families=len(rows), distinct_population=len(keys), seed=1113,
                   class_counts=dict(Counter(r["class"] for r in rows)),
                   class_shares={c:len(rs)/len(rows) for c,rs in by_class.items()},
                   timings_by_class={c:timings(rs) for c,rs in sorted(by_class.items())},
                   timings_by_block_size={c:timings(rs) for c,rs in sorted(by_size.items(), key=lambda kv:int(kv[0]))},
                   block_size_definition="max(main distinctions, S distinctions); S absent contributes zero",
                   run_info=info, alternative_run_info=alt_info, alternative_eligible=len(eligible),
                   alternative_families=len(alt_rows), alternative_ambiguity=None,
                   maximum_family_peak_rss_bytes=max((r["peak_rss_bytes"] for r in rows), default=0),
                   projected_full_first_ray_seconds_on_4_workers=total_family_seconds/len(rows)*len(keys)/4,
                   projection_method="uniform family sample total family seconds / 1000 * population / 4; excludes G1 and alternative ray",
                   alternative_timings=timings(alt_rows))
    alt_class, alt_size = defaultdict(list), defaultdict(list)
    for row in alt_rows:
        alt_class[row["class"]].append(row)
        size = max(row.get("main_block_size") or 0, row.get("s_block_size") or 0)
        alt_size[str(size)].append(row)
    summary["alternative_timings_by_class"] = {c:timings(rs) for c,rs in sorted(alt_class.items())}
    summary["alternative_timings_by_block_size"] = {c:timings(rs) for c,rs in sorted(alt_size.items(), key=lambda kv:int(kv[0]))}
    if alt_rows:
        summary["projected_full_alt_seconds_on_4_workers"] = sum(r["seconds"] for r in alt_rows)/len(alt_rows)*3000/4
        summary["alternative_projection_limit"] = "uses all eligible smoke rows; full alternative sample is at most 3000"
    dump(HERE/"smoke_summary.json", summary)
    # Do not print class counts or shares from the smoke run.
    print(json.dumps(dict(families=len(rows), alternative_families=len(alt_rows),
                          wall_seconds=info["wall_seconds"], peak_rss_bytes=info["aggregate_peak_rss_bytes"])), flush=True)


if __name__ == "__main__":
    main()
