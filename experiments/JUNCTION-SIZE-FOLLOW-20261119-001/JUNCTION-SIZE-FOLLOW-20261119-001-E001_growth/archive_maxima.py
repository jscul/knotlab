"""Read the original multiplicities of (parents, fresh) in the followed explosive starts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KEY = "JUNCTION-SIZE-FOLLOW-20261119-001"
FAMILY = ROOT / "artifacts" / KEY / (KEY + "-E001_growth")


def raw_records(directory):
    records = {}
    for line in (ROOT / "runs" / directory / "results.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row.get("status") == "ok":
            records[row["case"]] = row["result"]
    return records


def main():
    follows = raw_records("wall-read-b")
    starts = raw_records("merge-burst")
    samples = {}
    for i in range(16):
        name = f"start-{i:02d}"
        base = starts[name]["start"]
        raw = follows[f"follow-{i:02d}"]["records"]
        births = [dict(age=0, max_size=max(base["sizes"]))]
        for row in raw:
            if "keys" not in row:
                continue
            triples = [(p,f,mult) for (p,f),mult in row["keys"]]
            p,f,mult = max(triples,key=lambda x:x[0]+x[1])
            births.append(dict(age=row["t"], max_size=p+f, parents=p, fresh=f, multiplicity=mult))
        lower_bounds=[(row["t"],row["largest"]) for row in raw if "largest" in row]
        samples[name]={"source_sizes":base["sizes"],"observed_birth_maxima":births,
                       "parents_only_lower_bounds":lower_bounds,
                       "complete_prefix_max":max(r["max_size"] for r in births)}
    # A full binomial tail is determined at its first equal-count single block.
    for name,b,age in (("start-00",9,14),("start-04",781,8)):
        history=starts[name]["follow"]
        reading=history["reading"]
        assert (reading["t"],reading["live"],reading["maximal_blocks"],reading["largest_block"]) == (age,b,1,b)
        assert reading["predicted"][0] == b*(b-1)//2
        samples[name]["single_block_size"]=b
    # Verify the published partnered control by the actual projected growth rule.
    n=[6,8]
    for _ in range(3):
        n.append(2**(n[-1]//2)-n[-2])
    partnered=[2**(x//2-1) for x in n[1:]]
    assert n==[6,8,10,24,4086]
    assert samples["start-04"]["complete_prefix_max"]>=1754
    report={"partnered_round_counts":n,"partnered_birth_maxima_decimal":[str(v) for v in partnered],
            "explosive_starts_selected_by":"The sixteen EXPLOSIVE cases with the specified jump, conditional on its source weightings.",
            "explosive":samples}
    (FAMILY/"archive_maxima.json").write_text(json.dumps(report,indent=2)+"\n")
    print([(n, samples[n]["complete_prefix_max"]) for n in ("start-00","start-04")])


if __name__ == "__main__":
    main()
