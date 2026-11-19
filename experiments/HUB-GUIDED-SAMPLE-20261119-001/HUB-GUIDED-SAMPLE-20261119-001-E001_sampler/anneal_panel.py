"""Frozen full-core prefix panels for the shared runner. Every row is an independent batch."""

from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anneal_bank import read_bdd, write_bank


ROSTER_SHA256 = "049ad2aa85d55619a9e9c97dfd7ed33f6bb0d929d665af56f071b13f8fbd1102"
CORE_SHA256 = "299d8b0ad9f8e8bee951762d6b95ce65a7617094fb58a88dccb6b7eae0309739"
ROOT = {}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def base_seed(panel_tag):
    name = f"HUB-GUIDED-SAMPLE-20261119-001.prefix-islands.v1.{panel_tag}"
    return int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")


def setup(params):
    folder = Path(params["inputs"])
    executable = Path(params["binary"])
    roster = folder / "start-03-age08.txt"
    core = folder / "structure_full35_0.txt"
    if (digest(roster), digest(core), digest(executable)) != (ROSTER_SHA256, CORE_SHA256, params["binary_sha256"]):
        raise ValueError("a frozen input or the executable changed")
    ROOT.update(core=read_bdd(core), roster=roster, binary=executable, arm=params["arm"])


def cases():
    arm = ROOT["arm"]
    if arm not in ("primary", "sensitivity", "smoke"):
        raise ValueError("unknown arm")
    primary = arm != "sensitivity"
    order = "degree-up" if primary else "random"
    order_seed = 73121 if primary else 954013
    tag = 424900 if arm == "smoke" else 202611197840 if primary else 202611198840
    for rep in range(2 if arm == "smoke" else 24):
        yield str(rep), dict(tag=tag + rep, seed=base_seed(tag + rep), order=order,
                             order_seed=order_seed, population=128, islands=2 if arm == "smoke" else 32)


def run(case_id, payload):
    roster = ROOT["roster"]
    args = [ROOT["binary"], roster, payload["order"], payload["order_seed"], payload["population"],
            payload["seed"], payload["islands"], 0, 0, 0, 0, "/dev/stdin"]
    env = dict(os.environ, ANNEAL_PROFILE_COUNT="1", ANNEAL_PROFILE_ISLANDS="1", ANNEAL_MARK_BLOCKS="13+4,35+0")
    with tempfile.TemporaryFile(mode="w+t") as output:
        with subprocess.Popen(list(map(str, args)), stdin=subprocess.PIPE, stdout=output, env=env, text=True) as proc:
            write_bank(proc.stdin, *ROOT["core"], payload["population"], payload["islands"], payload["seed"], True)
            proc.stdin.close()
            if proc.wait():
                raise ValueError(f"prefix sampler exited with status {proc.returncode}")
        output.seek(0)
        prefix, *islands = map(json.loads, output)
    if len(islands) != payload["islands"] or prefix["seeded_prefix_classes"] != 9092:
        raise ValueError("missing or unexpected stage")
    for i, data in enumerate(islands):
        if data["seed"] != payload["seed"] + i or len(data["physical_draws"]) != int(i == 0):
            raise ValueError("unexpected sample seed or physical group count")
        if not all(0 <= x <= data["final_mass"] for x in data["marked_final_mass"].values()):
            raise ValueError("invalid marked population counts")
    return dict(panel=payload, graph=prefix, islands=islands)


def normalizer(row):
    n, d = map(int, row["exact_initial_mass"])
    scale = Fraction(n, d * row["initial_rows"])
    for value in row["resample_numerators"]:
        scale *= Fraction(value, row["resample_denominator"])
    return scale


def distribution(values):
    ordered = sorted(values)
    def quantile(p):
        z = (len(ordered) - 1) * p
        i = int(z)
        return ordered[i] + (z - i) * (ordered[min(i + 1, len(ordered) - 1)] - ordered[i])
    lo, hi = quantile(Fraction(1, 40)), quantile(Fraction(39, 40))
    total = sum(ordered)
    return dict(n=len(values), mean=float(total / len(values)), median=float(quantile(Fraction(1, 2))),
                minimum=float(ordered[0]), maximum=float(ordered[-1]), central95=[float(lo), float(hi)],
                central95_ratio=float(hi / lo) if lo else None, largest_share=float(ordered[-1] / total) if total else None,
                nonzero=sum(x > 0 for x in values))


def report(directory, artifact, physical):
    import gzip
    from collections import defaultdict

    scripts = Path(__file__).resolve().parents[3] / "scripts"
    sys.path.insert(0, str(scripts))
    from longrun import load_results

    rows = load_results(directory)
    if len(rows) != 24 or any(x["status"] != "ok" for x in rows.values()):
        raise ValueError("report requires 24 completed independent batches")
    batches, marked = [], defaultdict(list)
    raw, profiles, all_draws = [], [], []
    for k in range(24):
        outcome = rows[str(k)]["result"]
        batch = []
        sector = defaultdict(list)
        for j, island in enumerate(outcome["islands"]):
            scale = normalizer(island)
            weight = scale * island["final_mass"]
            batch.append(weight)
            for name, count in island["marked_final_mass"].items():
                sector[name].append(scale * count)
            names = island.pop("physical_draws")
            if names:
                profiles.append(dict(batch=k, island=j, seed=island["seed"], sampled_actual_live_ids=names,
                                     island_weight=[str(weight.numerator), str(weight.denominator)]))
        batches.append(sum(batch) / len(batch))
        for name, counts in sector.items():
            marked[name].append(sum(counts) / len(counts))
        all_draws.extend(batch)
        raw.append(outcome)
    means = [dict(value=[str(v.numerator), str(v.denominator)],
                  marked={m: [str(values[i].numerator), str(values[i].denominator)] for m, values in marked.items()})
             for i, v in enumerate(batches)]
    results = dict(schema=1, roster_sha256=ROSTER_SHA256, core_sha256=CORE_SHA256,
                   batches=distribution(batches), islands=distribution(all_draws),
                   marked={m: distribution(v) for m, v in marked.items()}, exact_batch_means=means,
                   physical_sample_file=physical.name, raw=raw)
    with artifact.open("x") as dest:
        json.dump(results, dest, separators=(",", ":"))
        dest.write("\n")
    with gzip.open(physical, "xt") as dest:
        json.dump(profiles, dest, separators=(",", ":"))
        dest.write("\n")
    print(json.dumps({k:results[k] for k in ("batches","islands","marked")}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("anneal_panel.py RUN_DIR JSON_OUTPUT GZIP_PHYSICAL_OUTPUT")
    report(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]))
