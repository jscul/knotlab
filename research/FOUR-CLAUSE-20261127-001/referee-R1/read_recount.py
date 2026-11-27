"""Recompute every archived stage up to 19 distinctions and the earlier positive control."""
import argparse
import gzip
import json
import resource
import subprocess
import sys
import time
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001/referee-R1"))
import growth_rule

PROGRAM = HERE / "read_engine"
STUDY = HERE.parent
SUM_FIELDS = ("bonds", "patterns", "relations read", "seven upper words",
              "proper and pairs free and not read at one lower bond", "a birth needed",
              "a birth needed, proper, free, not read at one lower bond")


def mask(support):
    return sum(1 << x for x in support)


def stage_source(starts, index):
    supports = growth_rule.supports_of(starts[index])
    yield 0, supports
    for t in (1, 2):
        result = growth_rule.advance(supports)
        if result.status != "funded":
            break
        supports = result.supports
        yield t, supports


def archived():
    records = {}
    for path in sorted((STUDY / "out").glob("four_*.jsonl")):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            index = int(record["start"].split()[1])
            if index in records:
                raise ValueError(f"duplicate start {index}")
            records[index] = record["rounds"]
    return records


def projected_image(codes):
    return np.flatnonzero(np.bincount(codes, minlength=8)).tolist()


def read_relations(supports, patterns, starting_laws):
    if not patterns:
        return []
    masks = [mask(s) for s in supports]
    names = set().union(*map(set, supports))
    states = np.arange(1 << len(names), dtype=np.uint32)
    violations = np.zeros(len(states), dtype=np.uint8)
    last = np.zeros(len(states), dtype=np.uint8)
    for q, raw in enumerate(masks):
        projection = states & raw
        failed = (projection == 0) | (projection == raw)
        violations += failed
        last[failed] = q
    allowed = violations == 0
    one_failed = violations == 1
    readings = {}
    result = []
    for pattern in patterns:
        for pair in pattern["pairs"]:
            for lit in pair:
                if lit not in readings:
                    raw = lit >> 1
                    on = states & raw
                    readings[lit] = ((on == 0) | (on == raw)) == bool(lit & 1)
        lower_codes = []
        for triple in pattern["clauses"]:
            parts = [readings[v][allowed].astype(np.uint8) for v in triple]
            lower_codes.append(4*parts[0] + 2*parts[1] + parts[2])
        for both in range(3):
            upper = []
            for i,(left,right) in enumerate(pattern["pairs"]):
                a, b = readings[left], readings[right]
                upper.append(a & b if i == both else a | b)
            upper_codes = 4*upper[0].astype(np.uint8) + 2*upper[1].astype(np.uint8) + upper[2]
            words = projected_image(upper_codes[allowed])
            pairwise = all(len(set((w & ~(1 << j)) for w in words)) == 4 for j in range(3))
            fixed_by = []
            for j, u in enumerate(upper):
                ua = u[allowed].astype(np.uint8)
                for k, lower in enumerate(lower_codes):
                    table = np.bincount(2*lower+ua,minlength=16).reshape((8,2))
                    if not ((table[:,0] > 0) & (table[:,1] > 0)).any():
                        fixed_by.append([j,k])
            by_deletion = np.bincount(last[one_failed & (upper_codes == 7)],minlength=len(masks)).tolist()
            needed = [q for q, count in enumerate(by_deletion) if count]
            result.append({
                "both": both, "pairs": pattern["pairs"], "clauses": pattern["clauses"], "words": words,
                "pairs_free":pairwise, "upper_reading_determined_by_selected_lower_bond": fixed_by,
                "restored_111_assignments_by_individual_law_deletion": by_deletion, "laws_needed": needed,
                "birth_needed": any(q >= starting_laws for q in needed)})
    return result


def calculate(supports, n_start, export):
    run = subprocess.run([str(PROGRAM),str(export),*map(str,map(mask,supports))],
                         capture_output=True, check=True)
    result = json.loads(run.stdout)
    families = result.pop("patterns")
    roles = read_relations(supports, families, n_start)
    groups = {tuple(tuple(p) for p in f["pairs"]) for f in families}
    steps = [r for r in roles if len(r["words"]) < 8 and r["pairs_free"]
             and not r["upper_reading_determined_by_selected_lower_bond"]]
    result.update({"patterns": len(families), "signed_pairings": len(groups), "relations read": len(roles),
                   "seven upper words": sum(len(r["words"]) == 7 for r in roles),
                   "proper and pairs free and not read at one lower bond": len(steps),
                   "a birth needed": sum(r["birth_needed"] for r in roles),
                   "a birth needed, proper, free, not read at one lower bond": sum(r["birth_needed"] for r in steps)})
    if roles:
        result["relations"] = roles
    return result


def check(row, reference):
    return {k:[reference.get(k),row.get(k)] for k in set(reference) | {"distinctions","knots","round"}
            if reference.get(k) != row.get(k)}


def pilot(starts, raw, cases, output, export_cases=False):
    rows = []
    for name in cases.split(","):
        start, round_number = map(int,name.split("/"))
        sup = dict(stage_source(starts,start))[round_number]
        t0 = time.perf_counter()
        result = calculate(sup,len(starts[start][2]),2)
        diff = check({"round":round_number,"distinctions":len(set().union(*map(set,sup))),
                      "knots":len(sup),**result},raw[start][round_number]) if start in raw else {}
        clauses = result.pop("clauses")
        bonds = result.pop("all_bonds")
        # Two positives are also data for checking determination by single bonds.
        if export_cases or (start,round_number) in {(420,2),(5260,2)}:
            target = HERE / f"read_all_bonds_{start}_{round_number}.json.gz"
            with TemporaryDirectory(prefix="read_export_",dir=HERE) as scratch:
                staged = Path(scratch) / target.name
                with gzip.open(staged,"wt",encoding="utf-8",compresslevel=2) as f:
                    json.dump({"census_entry":start,"start":start,"round":round_number,"supports":sup,
                               "literal":"(raw carrier mask << 1) | forbidden agreement value",
                               "bond":"[first raw mask, second raw mask, third raw mask, eight-bit set of missing words; first reading is high bit]",
                               "all_bonds":bonds,"clauses":clauses,"relations":result.get("relations",[])},
                              f,separators=(",",":"))
                staged.replace(target)
        rows.append({"census_entry":start,"round":round_number,"distinctions":len(set().union(*map(set,sup))),
                     "seconds":round(time.perf_counter()-t0,4),"archive_differences":diff,**result})
    data={"rows":rows,"max_child_rss_KiB":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
    (HERE / output).write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps([{k:r[k] for k in ("census_entry","round","distinctions","bonds","patterns","seconds","archive_differences")} for r in rows]))


def recount(starts, raw, part, parts, signed_spool, timing=False):
    rows=[]
    t0=time.perf_counter()
    roster=sorted(raw)[part::parts]
    signed_path=HERE/("read_timing_signed.jsonl.gz" if timing else f"read_signed_{part}.jsonl.gz")
    with TemporaryDirectory(prefix="read_stage_",dir=HERE) as directory:
        private=Path(directory)
        spool_path=private/"read_signed.jsonl.gz"
        spool_context=gzip.open(spool_path,"wt",encoding="utf-8",compresslevel=1) if signed_spool else nullcontext()
        with spool_context as spool:
            for index in roster:
                stages=list(stage_source(starts,index))
                if len(stages)!=len(raw[index]):
                    raise ValueError(f"funding differs at census entry {index}")
                for t,sup in stages:
                    n=len(set().union(*map(set,sup)))
                    row={"start":index,"round":t,"distinctions":n,"knots":len(sup)}
                    if n>19:
                        row["not read"]=True
                    else:
                        row.update(calculate(sup,starts[index][0],int(signed_spool)))
                        if signed_spool:
                            clauses=row.pop("clauses")
                            print(json.dumps({"start":index,"round":t,"clauses":clauses},separators=(",",":")),file=spool)
                    row["archive_differences"]=check(row,raw[index][t])
                    rows.append(row)
        data={"part":part,"parts":parts,"census_entries":len(roster),"seconds":round(time.perf_counter()-t0,3),
              "max_child_rss_KiB":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,"rows":rows}
        outfile=HERE/("read_stage_timing.json" if timing else f"read_stages_{part}.json")
        stage_path=private/"read_rows.json"
        stage_path.write_text(json.dumps(data,separators=(",",":"))+"\n")
        if signed_spool and not timing:
            spool_path.replace(signed_path)
        stage_path.replace(outfile)
    print(json.dumps({**{k:v for k,v in data.items() if k!="rows"},"stages":len(rows),
                      "mismatches":sum(bool(r["archive_differences"]) for r in rows)}))


def summarize(parts):
    captures=[json.loads((HERE/f"read_stages_{i}.json").read_text()) for i in range(parts)]
    if any(c["part"]!=p or c["parts"]!=parts for p,c in enumerate(captures)):
        raise ValueError("incompatible parts")
    rows=[r for c in captures for r in c["rows"]]
    all_keys={(r["start"],r["round"]) for r in rows}
    if len(all_keys)!=len(rows):
        raise ValueError("repeated stage")
    raw=archived()
    assert all_keys=={(a,r["round"]) for a,rs in raw.items() for r in rs}
    stats={}
    for t in (0,1,2):
        run=[r for r in rows if r["round"]==t and not r.get("not read")]
        stats[t]={"read":len(run),"omitted":sum(r["round"]==t and bool(r.get("not read")) for r in rows),
                  **{f:sum(r[f] for r in run) for f in (*SUM_FIELDS,"single_word_bonds","single_word_bonds_on_pairs","signed_pairings")},
                  "max_patterns":max(r["patterns"] for r in run),
                  "stages_at_least_12_raw":sum(r["distinctions"]>=12 for r in run),
                  "stages_at_least_12_raw_and_four_single_word_bonds":sum(r["distinctions"]>=12 and r["single_word_bonds"]>=4 for r in run),
                  "stages_at_least_12_raw_and_four_single_word_bonds_using_only_pairs":sum(r["distinctions"]>=12 and r["single_word_bonds_on_pairs"]>=4 for r in run),
                  "stages_with_a_pattern":sum(r["patterns"]>0 for r in run),
                  "maximum_raw_distinctions":max(r["distinctions"] for r in run),
                  "single_word_bits_by_order":list(map(sum,zip(*(r["single_word_bits_in_carrier_order"] for r in run))))}
    data={"archived_census_entries":len(raw),"funded_stages_by_stage_and_start":len(all_keys),
          "all_snapshot_starts_match_funding":True,
          "archive_field_mismatches":[r for r in rows if r['archive_differences']],
          "counts_by_round":stats,
          "census_entries_with_a_grown_stage_read":len({r["start"] for r in rows if r["round"] and not r.get("not read")}),
          "positive_rows":[r for r in rows if r.get("patterns",0)],
          "elapsed_seconds_by_chunk":[c["seconds"] for c in captures],
          "max_child_rss_KiB":max(c["max_child_rss_KiB"] for c in captures)}
    (HERE/"read_counts.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({k:v for k,v in data.items() if k!="positive_rows"}))


def main():
    args=argparse.ArgumentParser()
    mode=args.add_mutually_exclusive_group(required=True)
    mode.add_argument("--pilot",help="comma-separated census entry/round pairs")
    mode.add_argument("--chunk",help="index/number of chunks")
    mode.add_argument("--summarize",type=int,metavar="CHUNKS")
    args.add_argument("--out",default="read_pilot.json")
    args.add_argument("--export-pilot-bonds",action="store_true",help="save all lower bonds for each specified pilot stage")
    args.add_argument("--signed-spool",action="store_true",help="write signed single-word bonds for a second search")
    args.add_argument("--timing",action="store_true",help="keep the small timing slice under its own filenames")
    opt=args.parse_args()
    if opt.summarize:
        summarize(opt.summarize)
        return
    starts=json.loads((RESEARCH/"FORBID-EDITS-20261126-001/starts.json").read_text())
    raw=archived()
    if opt.pilot:
        pilot(starts,raw,opt.pilot,opt.out,opt.export_pilot_bonds)
    else:
        part,parts=map(int,opt.chunk.split("/"))
        if not 0<=part<parts: raise ValueError("invalid chunk")
        recount(starts,raw,part,parts,opt.signed_spool,opt.timing)


if __name__=="__main__":
    main()
