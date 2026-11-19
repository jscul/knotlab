"""Replay the successor's aggregation from exact numerator products and literal physical groups."""

from decimal import Decimal, localcontext
from datetime import datetime
from fractions import Fraction
import gzip
import json
from math import prod
from pathlib import Path
import sys

from anneal_checks import PhysicalCheck


def truth_rounded(q):
    with localcontext() as ctx:
        ctx.prec = 14
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def main():
    artifact, roster, target = map(Path, sys.argv[1:])
    lock = json.loads((artifact / "anneal_precision_lock.json").read_text())
    first = json.loads((artifact / "anneal_lock.json").read_text())
    data = json.loads((artifact / "anneal_precision.json").read_text())
    with gzip.open(artifact / data['physical_sample_file'], "rt") as src:
        physical = json.load(src)
    graph = PhysicalCheck(roster)
    previous = {s+j for arm in first["arms"].values() for s in arm["island_base_seeds"] for j in range(32)}
    seen, profiles = set(), []
    arms = {k:[] for k in lock["checkpoints"]}
    counts = {key:0 for key in ("13+4","35+0")}
    maxima = []
    assert len(data["raw"]) == len(physical) == 24
    for b, islands in enumerate(data["raw"]):
        assert len(islands) == 512
        accumulated = 0
        local_maximum = 0
        for index, row in enumerate(islands):
            name = lock["island_base_seeds"][b] + index
            assert row["seed"] == name and name not in seen and name not in previous
            seen.add(name)
            assert row["initial_rows"] == row["resample_denominator"] == 128
            assert row["exact_initial_mass"] == ["1988324131679583","1"]
            factors = row["resample_numerators"]
            assert all(512 < f <= 1024 for f in factors)
            assert 128 <= row["final_mass"] <= 512
            factor = Fraction(1988324131679583 * prod(factors), 128 ** (1+len(factors)))
            weight = factor * row["final_mass"]
            for mark,mass in row["marked_final_mass"].items():
                assert 0 <= mass <= row["final_mass"]
                counts[mark] += int(mass > 0)
            accumulated += weight
            local_maximum = max(local_maximum, weight)
            if index == 0:
                p = physical[b]
                assert p["seed"] == name and Fraction(*map(int,p["island_weight"])) == weight
                profiles.append(dict(seed=name, **graph.validate(p["sampled_actual_live_ids"][0])))
            n = index + 1
            if n in arms:
                mean = accumulated / n
                assert mean == Fraction(*map(int,data["exact_C_batch_means"][b][str(n)]))
                arms[n].append(mean+1039)
        maxima.append(local_maximum)
    result = {}
    for n, values in arms.items():
        ordered = sorted(values)
        # n_batches=24 gives interpolation index 23/40 at the bottom,
        # hence the mirror interpolation between the greatest two at the top.
        q025 = (17*ordered[0] + 23*ordered[1]) / 40
        q975 = (17*ordered[-1] + 23*ordered[-2]) / 40
        assert abs(float(q975/q025) - data["checkpoints"][str(n)]["births"]["central95_ratio"]) < 1e-12
        result[n] = dict(mean=truth_rounded(sum(values)/24), empirical_central_95=[truth_rounded(q025),truth_rounded(q975)],
                         ratio=truth_rounded(q975/q025), below_ten=bool(q975 < 10*q025))
    assert result[512]["below_ten"] == data["gate_below_ten"]
    output = dict(independent_integer_product_check=True,distinct_disjoint_island_seeds=len(seen),checkpoints=result,
                  single_island_maximum=truth_rounded(max(maxima)),nonzero_marked_islands=counts,
                  physical_original_stage_maximality=profiles)
    run_dir = roster.parent / "anneal-precision-primary"
    if (run_dir / "state.json").exists():
        state = json.loads((run_dir / "state.json").read_text())
        with (run_dir / "results.jsonl").open() as stream:
            attempts = [json.loads(line) for line in stream]
        assert state["complete"] and sum(r["status"] == "ok" for r in attempts) == 384
        finished = max(datetime.fromisoformat(r["finished_at"]) for r in attempts)
        elapsed = (finished - datetime.fromisoformat(state["started"])).total_seconds()
        output["resource"] = dict(actual_shards=384,worker_count=16,elapsed_seconds=elapsed,
                                  maximum_worker_RSS_MiB=max(r["peak_rss_mb"] for r in attempts),
                                  runner_reported_peak_RSS_MiB=state["peak_rss_mb"],
                                  successful_attempts=sum(r["status"]=="ok" for r in attempts),
                                  total_attempts=len(attempts))
    with target.open("x") as stream:
        json.dump(output,stream,indent=2)
        stream.write("\n")
    print(json.dumps({k:output[k] for k in ("distinct_disjoint_island_seeds","checkpoints","single_island_maximum",
                                           "nonzero_marked_islands")},indent=2))


if __name__ == "__main__":
    main()
