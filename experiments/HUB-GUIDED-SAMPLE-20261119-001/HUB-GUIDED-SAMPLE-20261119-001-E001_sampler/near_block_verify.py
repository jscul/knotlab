"""Verify the reduced count and the two literal roster renamings independently."""

import argparse
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
import subprocess
import tempfile

from near_block import NearBlock, mask_of, indices


HERE = Path(__file__).resolve().parent


def solve(binary, n, edges):
    data = f"{n} {len(edges)}\n" + "".join(f"{u} {v}\n" for u,v in edges)
    output = subprocess.run([str(binary)],input=data,text=True,capture_output=True,check=True).stdout.split()
    return list(map(int,output))


def brute(n, edges):
    conflicts = [0]*n
    for u,v in edges:
        conflicts[u] |= 1 << v
        conflicts[v] |= 1 << u
    full = (1 << n)-1
    return sum(all(not conflicts[v] & x for v in indices(x)) and
               all(conflicts[v] & x for v in indices(full ^ x)) for x in range(1,full+1))


def check_cpp(rows):
    small = [(1, []), (6, []), (8, list(combinations(range(8),2))),
             (7, [(i,i+1) for i in range(6)]), (6, [(0,5),(1,3),(2,4)])]
    rng = Random(202611199091)
    for n in range(2,10):
        for bound in (1,2,4,7):
            small.append((n, [pair for pair in combinations(range(n),2) if rng.randrange(8)<bound]))
    n = len(rows)
    edges = [(u,v) for u,a in enumerate(rows) for v in indices(a & ~((1 << (u+1))-1))]
    source = HERE / "near_block_count.cpp"
    with tempfile.TemporaryDirectory(prefix="hub-near-verify-") as tmp:
        binary = Path(tmp)/"check"
        subprocess.run(["c++","-O3","-std=c++20","-Wall","-Wextra",str(source),"-o",str(binary)],check=True)
        for size, links in small:
            assert solve(binary,size,links)[1] == brute(size,links)
        reduced, total, calls = solve(binary,n,edges)
    return {"raw_maximal_cliques":total, "full_quotient_vertices":reduced,
            "independent_small_graph_checks":len(small), "calls":calls,
            "source_sha256":sha256(source.read_bytes()).hexdigest()}


def read_json_gzip(path):
    with gzip.open(path,"rt") as handle:
        return json.load(handle)


def check_maps(base, folder):
    archive = json.loads((folder/"index.json").read_text())
    results = []
    parent_sets = read_json_gzip(base.path.with_suffix(".parents.json.gz"))
    assert len(parent_sets) == base.n
    reference = base.corrections()
    for spec in archive["exact_isomorphisms"]:
        assert spec["source"] == "start-02"
        tag = spec["image"]
        cohort = NearBlock(folder/f"{tag}-age09.txt")
        assert base.n == cohort.n
        supplied = folder / spec["age9_live_map"]["name"]
        assert sha256(supplied.read_bytes()).hexdigest() == spec["age9_live_map"]["sha256"]
        named = read_json_gzip(supplied)
        assert sorted(named) == list(range(base.n))
        transformation = {mask_of((named[v] for v in indices(row)),base.n) for row in base.blocks}
        assert transformation == set(cohort.blocks)
        before = spec["age8_live_map"]
        old = read_json_gzip(cohort.path.with_suffix(".parents.json.gz"))
        assert len(old) == len(named)
        assert all(sorted(before[p] for p in parents) == sorted(old[named[u]])
                   for u,parents in enumerate(parent_sets))
        correction = cohort.corrections()
        assert len(correction["held_maximal_cliques"]) == len(reference["held_maximal_cliques"]) == 1
        assert all(v == reference[k] for k,v in correction.items() if k != "held_maximal_cliques")
        results.append({"image":tag, "blocks_sha256":cohort.digest,
                        "named_map_sha256":spec["age9_live_map"]["sha256"],
                        "checked_point_count":base.n,"checked_parent_sets":len(old),
                        "checked_block_count":len(transformation),"birth_correction":correction})
    assert {row["image"] for row in results} == {"start-05","start-08"}
    return results


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("stage_directory",type=Path)
    cli.add_argument("primary",type=Path)
    cli.add_argument("output",type=Path)
    args = cli.parse_args()
    count = json.loads(args.primary.read_text())
    stage = NearBlock(args.stage_directory/"start-02-age09.txt")
    assert stage.digest == count["input_sha256"]
    rows, literal_names_per_node, n_inside = stage.quotient()
    assert [hex(r) for r in rows] == count["literal_conflict_rows_on_quotient"]
    assert n_inside == count["inside_types"] and sum(literal_names_per_node) == stage.n
    check = check_cpp(rows)
    assert check["raw_maximal_cliques"] == count["exact_count"]["raw_maximal_cliques"]
    carried = check_maps(stage,args.stage_directory)
    record = {"independent_full_quotient_counter":check, "renamings":carried,
              "exact_next_births_each":count["exact_count"]["next_births"]}
    args.output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
