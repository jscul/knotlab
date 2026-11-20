"""Check the disputed source-side condition and published numeric examples from separate records."""
from collections import Counter
from itertools import accumulate
from pathlib import Path
import gzip
import json
from hashlib import sha256

from side_sources import cases
from far_bond_ball import literal_control

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def read(name):
    return json.loads((DATA / (name+".json")).read_text())


def read_routes():
    with gzip.open(DATA/"side_routes.json.gz","rt") as fd:
        return json.load(fd)


def ordinary():
    result=read_routes()
    assert result["source_sha256"] == sha256((HERE/"side_routes.py").read_bytes()).hexdigest()
    conditions=0
    for tag in ("J1","P4","P8","P16","J1x2","PX4"):
        case=result["cases"][tag]
        seam=str(cases()[tag]["roles"]["seams"][0])
        quiet=case["geometries"][""]["stages"]
        for age,frame in quiet.items():
            for q,query in enumerate(case["queries"]):
                h=query["offsets"][seam]
                first=2*max((h+1)//2,h-int(age))+1
                assert frame["first_non_side_ancestry_hops"][q][seam]==first
                conditions+=1
    move=read("moving_count")
    generous=0
    for tag,case in move["cases"].items():
        for row in case["comparisons"]:
            k=row["k"];m=len(row["marks"]);target=k+1
            if not row["generous"]:
                continue
            for age,comp in row["comparisons"].items():
                assert comp["delta_by_radius_odd"][:-1]==[0]*(k+1), (tag,k,m,age)
                assert comp["delta"] == (-2 if int(age)>=target else 0)
                if int(age)==target:
                    expected=(k+2)*(m+2*k+3)+6
                    assert comp["quiet"]["knots"]==expected and comp["loaded"]["knots"]==expected-2
                    assert comp["quiet"]["with_ancestry_outside_side"] and comp["loaded"]["with_ancestry_outside_side"]
                    generous+=1
    assert generous==57
    assert all(v[0]==v[1] for v in move["renaming_old_holders_and_distinctions"].values())
    loads=read("moving_loads")
    for rows in loads["dose"].values():
        for row in rows:
            assert sum(sum(c.values()) for c in row["by_hot"].values())==64
            assert all(set(delta)==({"-2"} if hot[0]=="1" else {"0"})
                       for hot,delta in row["by_hot"].items())
    double_rows=[r for rows in loads["two_rings"].values() for r in rows]
    assert all(row["interaction"]==0 for row in double_rows)
    return {"quiet_ancestry_thresholds":conditions,"preregistered_margin_checks":generous,
            "two_donor_moving_checks":len(double_rows),"dose_readings":sum(len(rows) for rows in loads["dose"].values())}


def anchored():
    d=read("far_bond_ball")
    assert d["literal_control"] == literal_control()
    expect={"0":[4,4,4,16,16,30,30,45],"1":[4,4,4,16,16,30,30,46]}
    for arm,row in d["arms"].items():
        assert row["complete"] and row["knots_by_bond_radius"]==expect[arm]
        for name,bank in row["roots"].items():
            bonds=[frozenset(b) for b in bank["bonds"]]
            assert all(int(name) in b and len(b)<=8 for b in bonds)
            assert not any(x<y for x in bonds for y in bonds)


if __name__=="__main__":
    result=ordinary()
    anchored()
    print(json.dumps(result))

