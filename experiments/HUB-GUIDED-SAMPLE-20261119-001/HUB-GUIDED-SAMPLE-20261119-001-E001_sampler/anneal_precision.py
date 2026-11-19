"""Prespecified 512-island count using direct core decoding and the existing shared runner."""

from fractions import Fraction
import gzip
import json
import os
from pathlib import Path
from random import Random
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anneal_panel import digest, distribution, normalizer


LOCK_SHA = "c5320a146a96fd0b21b158111a4b857a6e1f66290e6424ffe8ef305eb15592ea"
S = {}


def rank_stream(seed, count, islands, population=128):
    out = []
    for r in range(islands):
        rng = Random(f"anneal.initial-prefix.{seed + r}")
        for i in range(population):
            out.append(str((i * count + rng.randrange(count)) // population))
    return "\n".join(out) + "\n"


def setup(params):
    path = Path(params["inputs"])
    lock = Path(params["lock"])
    if digest(lock) != LOCK_SHA:
        raise ValueError("different scientific design")
    spec = json.loads(lock.read_text())
    native = Path(params["binary"])
    roster, core = path / "start-03-age08.txt", path / "structure_full35_0.txt"
    if (digest(native), digest(roster), digest(core)) != (
            params["binary_sha256"], spec["stage_sha256"], spec["core_sha256"]):
        raise ValueError("inconsistent binary or inputs")
    S.update(native=native, roster=roster, core=core, spec=spec, mode=params["mode"])


def cases():
    if S["mode"] == "smoke":
        for i in range(2):
            yield f"pilot.{i}", dict(batch=i, offset=0, seed=451000 + 4*i, islands=4)
    elif S["mode"] == "primary":
        for offset in range(0, 512, 32):
            for batch, base in enumerate(S["spec"]["island_base_seeds"]):
                yield f"{batch}.{offset}", dict(batch=batch, offset=offset, seed=base+offset, islands=32)
    else:
        raise ValueError("unknown run")


def run(case_id, payload):
    population, n, seed = 128, payload["islands"], payload["seed"]
    spec = S["spec"]
    command = [S["native"], S["roster"], S["core"], spec["arm"], spec["order_seed"], population, seed, n]
    env = dict(os.environ, ANNEAL_PROFILE_COUNT="1", ANNEAL_PROFILE_ISLANDS=str(int(payload["offset"] == 0)),
               ANNEAL_MARK_BLOCKS="13+4,35+0")
    process = subprocess.run(list(map(str, command)), env=env, input=rank_stream(seed, spec["normalizer"], n),
                             capture_output=True, text=True, check=True)
    header, *rows = map(json.loads, process.stdout.splitlines())
    if header != dict(literal=28065, classes=25654, seeded_prefix_classes=9092,
                      induced_groups=spec["normalizer"], population=128) or len(rows) != n:
        raise ValueError("inconsistent input or island count")
    compact = []
    for i, row in enumerate(rows):
        if row["seed"] != seed+i or len(row["physical_draws"]) != int(i == 0 and payload["offset"] == 0):
            raise ValueError("inconsistent seed or physical draw")
        compact.append({field:row[field] for field in ("seed","exact_initial_mass","initial_rows","resample_denominator",
                       "final_mass","resample_numerators","marked_final_mass","physical_draws")})
    return dict(config=payload, islands=compact)


def report(run_dir, destination, physical):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
    from longrun import load_results
    from collections import defaultdict

    runs = load_results(run_dir)
    if len(runs) != 384 or not all(r["status"] == "ok" for r in runs.values()):
        raise ValueError("the 384 fixed shards must all finish successfully")
    checkpoints = {k:[] for k in (64,256,512)}
    named = {k:defaultdict(list) for k in checkpoints}
    raw, means, profiles = [], [], []
    for b in range(24):
        islands = [r for o in range(0,512,32) for r in runs[f"{b}.{o}"]["result"]["islands"]]
        assert len(islands) == 512
        values, sub = [], defaultdict(list)
        for i, island in enumerate(islands):
            scale = normalizer(island)
            weight = scale * island["final_mass"]
            values.append(weight)
            for label,mass in island["marked_final_mass"].items():
                sub[label].append(scale * mass)
            profile = island.pop("physical_draws")
            if profile:
                assert i == 0
                profiles.append(dict(batch=b, island=i, seed=island["seed"], sampled_actual_live_ids=profile,
                                     island_weight=[str(weight.numerator),str(weight.denominator)]))
        for k in checkpoints:
            checkpoints[k].append(sum(values[:k]) / k)
            for label, parts in sub.items():
                named[k][label].append(sum(parts[:k]) / k)
        raw.append(islands)
        means.append({str(k):[str(checkpoints[k][-1].numerator),str(checkpoints[k][-1].denominator)] for k in checkpoints})
    output = dict(schema=1, lock_sha256=LOCK_SHA, exact_birth_correction=1039,
                  checkpoints={str(k):dict(maximal_sets=distribution(c),births=distribution([v+1039 for v in c]),
                              marked={label:distribution(z) for label,z in named[k].items()})
                              for k,c in checkpoints.items()},
                  decision_checkpoint=512, exact_C_batch_means=means, raw=raw,
                  physical_sample_file=physical.name)
    from anneal_gate import quantile
    actual = sorted(v+1039 for v in checkpoints[512])
    output["gate_below_ten"] = quantile(actual, Fraction(39,40)) < 10 * quantile(actual, Fraction(1,40))
    with destination.open("x") as stream:
        json.dump(output,stream,separators=(",",":"))
        stream.write("\n")
    with gzip.open(physical, "xt") as stream:
        json.dump(profiles,stream,separators=(",",":"))
        stream.write("\n")
    print(json.dumps(dict(checkpoints=output["checkpoints"],gate=output["gate_below_ten"]),indent=2))


if __name__ == "__main__":
    report(sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]))
