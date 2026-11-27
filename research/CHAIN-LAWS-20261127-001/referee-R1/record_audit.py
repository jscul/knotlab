"""Read the archived counts, freeze, comparison cases and indexed prior work."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, islice, product
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parent.parent
FOUR = STUDY.parent / "FOUR-CLAUSE-20261127-001"
ORDINARY = STUDY.parent / "CHAIN-STEP-20261127-001" / "referee-R1"
RING = STUDY.parent / "RING-BOND-20261127-001" / "referee-R1"
FREEZE = "fb0b54c376"
CLOSE = "3aeb9ca6ac"
QUERIES = (
    "eight-knot chain four clauses step one layer up census growth",
    "forbidding cuts one fewer fresh arity floor stalled funding census",
    "eight lower bonds disjoint agreements closed start grown ring",
    "four-clause alternating chain first-three readings upper bond",
)
DEFINING = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))


def run(*args, **env):
    return subprocess.check_output(args, cwd=ROOT, env={**os.environ, **env})


def recorded(law, pilot):
    totals = [Counter() for _ in range(7)]
    chunk_counts, ids, first = [], set(), Counter()
    maximum = 0
    for part in range(8):
        path = STUDY / "out" / f"{law}_{part}.jsonl"
        with path.open() as stream:
            n = 0
            for line in islice(stream, 12 if pilot else None):
                record = json.loads(line)
                ident = record["start"]
                assert ident == part + 8*n and ident not in ids
                ids.add(ident)
                n += 1
                positive = []
                for j, row in enumerate(record["rows"]):
                    if "round" not in row:
                        assert j == len(record["rows"])-1 and row["after round"] == j-1
                        totals[j-1][row["stopped"]] += 1
                        continue
                    assert j == row["round"]
                    count = row["chains"]
                    checks = min(count, 3)
                    maximum = max(count, maximum)
                    passes = row.get("carried steps", 0)
                    necessary = row.get("every law needed", 0)
                    assert 0 <= necessary <= passes <= checks
                    totals[j].update(dict(stages=1, knots=row["knots"], chains=count,
                                          chain_positive_stages=int(count > 0), checked=checks,
                                          unchecked=count-checks, frozen_passes=passes,
                                          frozen_and_every_law=necessary,
                                          frozen_positive_stages=int(passes > 0)))
                    if passes:
                        positive.append(j)
                if positive:
                    first[min(positive)] += 1
            chunk_counts.append(n)
    if not pilot:
        assert ids == set(range(7075))
    return dict(rows_by_chunk=chunk_counts, rounds=totals, first_frozen_pass=first,
                starts_with_frozen_pass=sum(first.values()), maximum_chain_count=maximum)


def hashes():
    saved = {}
    for line in (STUDY/"frozen.sha256").read_text().splitlines():
        expected, path = line.split()
        for rev in (FREEZE, CLOSE):
            assert sha256(run("git", "show", f"{rev}:{path}")).hexdigest() == expected
        assert sha256((ROOT/path).read_bytes()).hexdigest() == expected
        saved[path] = expected
    paths = [str(p.relative_to(ROOT)) for p in sorted((STUDY/"out").glob("*.jsonl"))]
    assert all(run("git","rev-parse",f"{CLOSE}:{p}").strip() ==
               run("git","hash-object",p).strip() for p in paths)
    def tree(rev):
        return len(run("git","ls-tree","-r","--name-only",rev,"--",str((STUDY/"out").relative_to(ROOT))).splitlines())
    return dict(freeze=FREEZE, close=CLOSE, manifest=saved, archived_chunk_counts=[tree(FREEZE),tree(CLOSE)],
                raw_chunks_match_close=len(paths), post_directory_in_study=(STUDY/"post").is_dir())


def prior(pilot):
    results = []
    for query in QUERIES[:1] if pilot else QUERIES:
        res = json.loads(run(sys.executable, "-B", "scripts/track.py", "objects", query,
                             "--until", "2026-11-27", "--exclude", STUDY.name, "--limit", "8", "--json"))
        results.append(dict(query=query, indexed_records=[(r["id"],r["object"]) for r in res["index"]],
                            unindexed_records=[(r["id"],r["title"]) for r in res["other_epics"]]))
    return results


def enumerate_states(supports, carriers, limit):
    """Count reading words on the actual allowed states by direct binary assignment."""
    def mask(names):
        return sum(1 << d for d in names)
    laws = [mask(names) for names in supports]
    reads = [mask(names) for names in carriers]
    width = max(laws).bit_length()
    counts = Counter()
    for s in range(min(limit or 1 << width, 1 << width)):
        if all((s & law) not in (0,law) for law in laws):
            counts[tuple(int(s & m in (0,m)) for m in reads)] += 1
    return counts


def post_and_logic(pilot):
    original = json.loads((FOUR/"post/chain_replay.json").read_text())
    earlier = json.loads((ORDINARY/"converse_chain_replay.json").read_text())
    post = {}
    for key, row in original.items():
        counts = {name: row[name] for name in ("bonds","patterns","steps","every law needed")}
        assert all(earlier["stage_summary"][key][name] == n for name,n in counts.items())
        post[key] = counts

    bare = tuple(tuple(range(2*i,2*i+3)) for i in range(8))
    chosen = [g for g, forbidden in original["chain of 8"]["example"] if forbidden == 1]
    limit = 4096 if pilot else None
    words = enumerate_states(bare, chosen, limit)
    allowed = set(words)
    def upper(w, both):
        return tuple((all if j == both else any)(w[j*2:j*2+2]) for j in range(3))
    eight = set(product((0,1),repeat=3))
    image = [set(upper(w,b) for w in words) for b in range(3)]
    masks = [tuple(int(v) for v in vals) for vals in product((0,1),repeat=6)]
    permitted = {w for w in masks if all(not all(w[j] for j in t) for t in DEFINING)}
    seven = eight-{(1,1,1)}
    assert all({upper(w,b) for w in permitted} == seven for b in range(3))
    # Any seven binary triples already give four values on every two places.
    pair_failures = sum(len({(w[a],w[b]) for w in eight-{omit}}) != 4
                        for omit in eight for a,b in combinations(range(3),2))
    assert pair_failures == 0
    if not pilot:
        assert all(v == seven for v in image) and allowed < permitted
        assert all({tuple(w[j] for j in t) for w in allowed} == seven for t in DEFINING)
    earlier_witness = json.loads((RING/"layer_witness.json").read_text())
    witness = enumerate_states(earlier_witness["source_knots_not_all_equal"],
                               earlier_witness["lower_carriers_in_A0_A1_B0_B1_C0_C1_order"], limit)
    if not pilot:
        assert {"".join(map(str,w)): n for w,n in witness.items()} == earlier_witness["source_state_counts_by_lower_word"]
    canonical = json.loads(run(sys.executable,"-B","-m","knotlab","check","--cnf","~A ~B ~C",
                               "--loops","A","B","--contact","C","--json",PYTHONPATH=str(ROOT/"tools")))
    return dict(earlier_chain_post=post, bare_chain_source_states=sum(words.values()),
                bare_chain_distinct_lower_words=len(words), four_clauses_only_lower_words=len(permitted),
                upper_images=[[list(map(int,w)) for w in sorted(s)] for s in image],
                seven_word_sets_times_three_pair_projections=24, pair_failures=pair_failures,
                canonical_missing_111=canonical, earlier_closed_witness_states=sum(witness.values()),
                earlier_closed_witness_lower_words=len(witness))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    begin = perf_counter()
    data = dict(archive={law: recorded(law,args.pilot) for law in ("one_fewer","arity_floor")},
                history=hashes(), earlier_and_controls=post_and_logic(args.pilot),
                prior_searches=prior(args.pilot))
    data.update(pilot=args.pilot, elapsed_seconds=round(perf_counter()-begin,3))
    (HERE/("record_pilot.json" if args.pilot else "record_counts.json")).write_text(json.dumps(data,indent=2)+"\n")
    print(f"{data['elapsed_seconds']:.3f} seconds")

if __name__ == "__main__":
    main()
