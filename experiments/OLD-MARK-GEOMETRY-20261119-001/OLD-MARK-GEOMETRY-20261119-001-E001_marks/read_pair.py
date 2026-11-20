"""Read one old pair and its entire midpoint ball profile from the measured stages."""
import argparse
from itertools import accumulate
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",help="e.g. J1, T4, T8 or J1x2")
    parser.add_argument("first",type=int,choices=range(16))
    parser.add_argument("second",type=int,choices=range(16))
    parser.add_argument("--loads",nargs="+",default=["0","1"],help="0 and 1, or w00 ... w63 on the doubled ring")
    parser.add_argument("--age",type=int,help="one materialized layer; omit to view all")
    args=parser.parse_args()
    if args.first == args.second:
        parser.error("select two distinct original marks")
    i,j=sorted((args.first,args.second))
    with gzip.open(DATA/"routes.json.gz","rt") as stream:
        cases=json.load(stream)["cases"]
    if args.source not in cases:
        parser.error("unknown source")
    source=cases[args.source]
    for load in args.loads:
        if load not in source["assignments"]:
            parser.error(f"load {load} is unavailable on this source")
        mask=source["assignments"][load]["activity_mask"]
        trace=source["activity_geometries"][mask]
        for age,frame in trace["stages"].items():
            if args.age is not None and int(age)!=args.age:
                continue
            pair=next(pair for pair in frame["pairs"] if (pair["i"],pair["j"])==(i,j))
            profiles={}
            for label,field in (("midpoint_union","union_profile"),("fixed_source","fixed_profile")):
                profile=frame["profiles"][pair[field]]
                counts=list(accumulate(shell[0] for shell in profile["shells"]))
                assert counts[-1]==frame["knots"]
                profiles[label]={"centers": profile["centers"],"knots_by_radius_from_zero":counts}
            print(json.dumps({"source":args.source,"load":load,"pair":[i,j],"age":int(age),
                              "knots":frame["knots"],"distinctions":frame["distinctions"],
                              "ordinary_mark_steps":pair["steps"],"shortest_routes":pair["routes"],
                              "routes_visiting":dict(zip(frame["tags"],pair["routes_visiting_tag"],strict=True)),
                              "profiles":profiles},separators=(",",":")))
        print(json.dumps({"load":load,"materialization_stop":trace["termination"]},separators=(",",":")))


if __name__=="__main__":
    main()
