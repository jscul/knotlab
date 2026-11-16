"""Materialize one frozen PARENT-FOLD reserve in neutral explicit-piece order.

Training: python3 -B make_panels.py train
Blind: python3 -B make_panels.py blind --model-file PATH --model-sha256 HEX
The supervisor charges the complete generator process, including startup and exit.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "PAIR-PROOF-20261115-001"
OUT = ROOT / "artifacts" / TICKET / HERE.name
PRIOR = ROOT / "artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/explicit-piece"
GEN = ROOT / "research/PARENT-FOLD-20261115-001/panels.py"
GEN_SHA = "e65d04034b31d9f2fd73007ace699c58a63b6669a2a12d82425c4c68450b0b78"
FROZEN = {
    "contract.json": "46ed0452262fcc8b03eff401ff1d70bf118d7a9d0cbf50af1fcc325b27eb26cd",
    "identity.json": "b7d26c8f140249cc151c1b216f9efe70e7b6360adab9cfa570a2a4e40a6c4db3",
}
PRIOR_FILES = {
    "public.json": "7dddbcf0d2e86c18376c2f46f25150b26e50d6c6c6f5039837937077e281e150",
    "grades.json": "095518e925494ae2723858e9a70241c19cc6cea454696914d8a135bf55422bac",
}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"


def _verified(path, expected):
    data = path.read_bytes()
    if _sha(data) != expected:
        raise ValueError(f"Frozen hash differs for {path}")
    return data


def _release(args):
    for name, expected in FROZEN.items():
        _verified(HERE / name, expected)
    _verified(GEN, GEN_SHA)
    if args.split == "train":
        if args.model_file or args.model_sha256:
            raise ValueError("Training is opened by the frozen contract alone")
        return None
    digest = args.model_sha256
    if not digest or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Blind generation requires the saved model's full lowercase SHA-256")
    if not args.model_file:
        raise ValueError("Blind generation requires the saved E002 model file")
    path = Path(args.model_file).resolve()
    _verified(path, digest)
    train = json.loads((OUT / "train/origin.json").read_bytes())
    if train["split"] != "train" or train["contract_sha256"] != FROZEN["contract.json"]:
        raise ValueError("Cannot bind blind to the training receipt for this contract")
    return {"file": os.path.relpath(path, ROOT), "sha256": digest,
            "training_origin_sha256": _sha((OUT / "train/origin.json").read_bytes())}


def _render(public, grades):
    # Public ordering uses only the input triple and the existing physical bit address.
    for case in public:
        by_inputs = defaultdict(list)
        for piece in case["pieces"]:
            by_inputs[tuple(piece["inputs"])].append(piece)
        by_inputs = {key: iter(sorted(pieces, key=lambda p: p["bit"])) for key, pieces in by_inputs.items()}
        case["pieces"] = [next(by_inputs[tuple(p["inputs"])]) for p in case["pieces"]]
    for case in public:
        g = grades[case["id"]]
        base = g["base"]
        index = next(i for i, p in enumerate(case["pieces"]) if p["inputs"] == base["anchor"])
        if case["pieces"][index]["bit"] != base["anchor_bit"]:
            raise AssertionError("Neutral public ordering did not expose the original physical bit first")
        g["anchor_piece"] = base["anchor_piece"] = index


def _physical(p, edit=None):
    # This deliberately coarse public invariant ignores raw names, NAND pin
    # order, output order and topologically legal gate reindexings. Matching
    # hashes are not an isomorphism proof; disjoint hashes rule out isomorphism.
    n = p["n"]
    stamps = [b"R"] * n + [b"F", b"T"]
    for k, (a, b) in enumerate(p["gates"]):
        if edit and edit["gate"] == k + n + 2:
            a, b = (edit["to"], b) if edit["pin"] == 0 else (a, edit["to"])
        source = sorted((stamps[a], stamps[b]))
        stamps.append(hashlib.sha256(b"N" + b"".join(v.ljust(32, b"\0") for v in source)).digest())
    def series(indices):
        return b"".join(sorted(stamps[i] for i in indices))
    gates = n + 2
    pre = gates + p["upstream_count"]
    return _sha(b"|".join((str(n).encode(), series(range(gates, pre)), series(range(pre, len(stamps))),
                           series(p["frontier"]), series(p["outputs"]))))


def _families(public, grades):
    physical, consumer, truth = set(), set(), set()
    parent_ids, edit_ids = set(), set()
    for p in public:
        g = grades[p["id"]]
        consumer.add(g["structure"])
        truth.update(g["truth_families"])
        physical.update(_physical(p, e) for e in (None, *p["edits"]))
        parent_ids.add(p["id"])
        edit_ids.update(e["id"] for e in p["edits"])
    return dict(physical=physical, downstream=consumer, truth=truth, parent_ids=parent_ids, edit_ids=edit_ids)


def _load_prior(directory, files):
    p, g = (json.loads(_verified(directory / name, files[name])) for name in ("public.json", "grades.json"))
    return _families(p, g)


def _exclusive_data(path, packed):
    try:
        with path.open("xb") as f:
            f.write(packed)
            f.flush()
            os.fsync(f.fileno())
    except FileExistsError:
        if path.read_bytes() != packed:
            raise ValueError(f"Will not replace unequal existing data at {path}")


def _produce(args):
    model = _release(args)
    start = time.time_ns()
    spec = importlib.util.spec_from_file_location("_frozen_parent_panels", GEN)
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    arities, seeds, domain = gen.PLAN[args.split]
    print(f"Generating {args.split} only, frontier sizes {arities}, seeds {seeds}", file=sys.stderr, flush=True)
    public, grades = gen.build(args.split)
    _render(public, grades)
    counts = Counter()
    for i, p in enumerate(public, 1):
        g = grades[p["id"]]
        gen._audit_parent(p, g)
        counts[g["m"], g["seed"], g["operation"], g["stratum"]] += 1
        if any(int(key[:8], 16) % 3 != domain for key in (g["structure"], *g["truth_families"])):
            raise AssertionError("Public truth or consumer family outside the frozen split")
        if i % 12 == 0:
            print(f"Verified {i}/{len(public)} {args.split} parents", file=sys.stderr, flush=True)
    expected = {(m, s, op, form) for m in arities for s in seeds
                for op in ("fold", "mux") for form in ("direct", "masked")}
    if set(counts) != expected or set(counts.values()) != {1}:
        raise AssertionError("Unexpected seed/size/operation/control balance")
    current = _families(public, grades)
    if (len(public), len(current["parent_ids"]), len(current["edit_ids"]),
            len(current["downstream"]), len(current["truth"])) != (36, 36, 72, 36, 108):
        raise AssertionError("Panel extents or distinct logical families differ from the frozen plan")
    earlier = {"E001": _load_prior(PRIOR, PRIOR_FILES)}
    if args.split == "blind":
        origin = json.loads((OUT / "train/origin.json").read_bytes())
        earlier["train"] = _load_prior(OUT / "train", origin["files"])
    cross = {}
    for split, historical in earlier.items():
        cross[split] = {k: len(t & historical[k]) for k, t in current.items()}
        if any(cross[split].values()):
            raise AssertionError(f"Freshness check failed against {split}: {cross[split]}")
    destination = OUT / args.split
    destination.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, obj in (("public.json", public), ("grades.json", grades)):
        packed = _encoded(obj)
        _exclusive_data(destination / name, packed)
        files[name] = _sha(packed)
    return {
        "split": args.split, "artifact_id": "PAIR-PROOF-20261115-001-E002",
        "contract_sha256": FROZEN["contract.json"], "identity_sha256": FROZEN["identity.json"],
        "preparer_sha256": _sha(Path(__file__).read_bytes()), "generator_sha256": GEN_SHA,
        "generator_dependencies": {name: _sha((ROOT / name).read_bytes()) for name in gen.SOURCE_DEPENDENCIES},
        "previous_explicit_piece_inputs": PRIOR_FILES, "model": model, "files": files,
        "frontier_sizes": arities, "raw_sizes": [m + 2 for m in arities], "seeds": seeds,
        "fingerprint_domain": domain, "domain_modulus": 3, "parents": len(public), "edits": 2 * len(public),
        "proposal_parents": sum(g["trial"] for g in grades.values()),
        "families": {k: len(v) for k, v in current.items()}, "cross_split_intersections": cross,
        "global_triple_labels": sum(len(s["candidate_classes"]) for g in grades.values()
                                    for s in (g["base"], *g["edits"].values())),
        "rendering": "Within each inputs triple's existing public slots, physical bit number ascending.",
        "checks": "Each public raw circuit, both raw edits, local bits, exact triple labels and unchanged source grade "
                  "verified by the frozen scalar audit. Only the two private anchor list positions are updated.",
        "generation_start_unix_ns": start,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", choices=("train", "blind"))
    parser.add_argument("--model-file")
    parser.add_argument("--model-sha256")
    parser.add_argument("--produce", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.produce:
        print(json.dumps(_produce(args), sort_keys=True))
        return
    model = _release(args)
    receipt = OUT / args.split / "origin.json"
    if receipt.exists():
        old = json.loads(receipt.read_bytes())
        if old["model"] != model or old["preparer_sha256"] != _sha(Path(__file__).read_bytes()):
            raise ValueError(f"Different preparation already occupies {receipt}")
        for name, expected in old["files"].items():
            _verified(receipt.parent / name, expected)
        print(json.dumps(old, sort_keys=True))
        return
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:], "--produce"]
    start = time.perf_counter_ns()
    child = subprocess.run(argv, check=True, stdout=subprocess.PIPE)
    spent = resource.getrusage(resource.RUSAGE_CHILDREN)
    row = json.loads(child.stdout)
    row["worker_cpu_ns"] = round((spent.ru_utime + spent.ru_stime) * 1e9)
    row["worker_user_cpu_ns"] = round(spent.ru_utime * 1e9)
    row["worker_system_cpu_ns"] = round(spent.ru_stime * 1e9)
    row["generation_wall_ns"] = time.perf_counter_ns() - start
    row["completed_unix_ns"] = time.time_ns()
    row["supervisor_cpu_ns_to_receipt"] = time.process_time_ns()
    row["cpu_ns"] = row["worker_cpu_ns"] + row["supervisor_cpu_ns_to_receipt"]
    row["charge_scope"] = ("Entire lifetime of the fresh generator process (including imports, all rejected candidates, "
                           "grading, independent checks, hashing, serialization, fsync and exit), plus supervisor CPU "
                           "from interpreter startup to writing this timing receipt. No learner was run.")
    _exclusive_data(receipt, _encoded(row))
    print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()
