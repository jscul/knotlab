"""Independently recount every finite stage and its surviving old states in the two small-source receipts."""
from functools import cache
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


@cache
def recount(law, rows):
    n = max(map(max,rows)) + 1
    if law == "parity":
        # Eliminate each distinction in order by XORing the first row that contains it.
        equations = [set(row) for row in rows]
        rank = 0
        for bit in range(n):
            pivot = next((i for i in range(rank,len(rows)) if bit in equations[i]), None)
            if pivot is None:
                continue
            equations[rank],equations[pivot] = equations[pivot],equations[rank]
            for i in range(rank+1,len(rows)):
                if bit in equations[i]:
                    equations[i] ^= equations[rank]
            rank += 1
        return 1 << (n-rank)

    # Inclusion-exclusion of the monochromatic events. Selecting a row joins
    # its bits into one equality class. Each remaining class has two choices.
    def terms(i, classes):
        if i == len(rows):
            return 1 << len(classes)
        merged = set(rows[i])
        keep = []
        for group in classes:
            if merged.isdisjoint(group):
                keep.append(group)
            else:
                merged.update(group)
        return terms(i+1,classes) - terms(i+1,(*keep,merged))
    return terms(0,tuple({bit} for bit in range(n)))


def run():
    stages = individual = rounds = 0
    for filename in ("growth_checks.json","supplement_split_spares.json"):
        data = json.loads((OUT / filename).read_text())
        for source, laws in data["arms"].items():
            for law,arms in laws.items():
                for rival,record in arms.items():
                    for stage in record["stages"]:
                        rows = tuple(map(tuple,stage["supports"]))
                        assert recount(law,rows) == stage["states"], (source,law,rival)
                        stages += 1
                    for old,receipt in zip(record["stages"],record["rounds"]):
                        if receipt["verdict"] != "extend":
                            continue
                        rows = tuple(map(tuple,old["supports"]))
                        retired = tuple(tuple(b["spent"]) for b in receipt["births"] if b["f"]==0)
                        assert recount(law,rows+retired) == receipt["surviving_old"]
                        for b in receipt["births"]:
                            extra = (tuple(b["spent"]),) if b["f"]==0 else ()
                            assert recount(law,rows+extra) == b["solo_survivors"]
                            individual += 1
                        rounds += 1
    counts = dict(stages=stages, funded_transitions=rounds, individual_survivor_counts=individual,
                  distinct_recounts=recount.cache_info().currsize, passed=True)
    (OUT / "count_verification.json").write_text(json.dumps(counts,indent=2)+"\n")
    print(counts)


if __name__ == "__main__":
    run()
