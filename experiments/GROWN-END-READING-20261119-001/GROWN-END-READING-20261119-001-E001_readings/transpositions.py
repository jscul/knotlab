"""Exhaust transpositions on small reached starts with repeated meetings."""
import argparse
from collections import Counter
from pathlib import Path
import json
import subprocess
import tempfile

import networkx as nx


HERE = Path(__file__).resolve().parent
FIELDS = ("start_junctions", "start_distinctions", "allocations", "open_stages",
          "largest_age", "non_span_swaps_tested", "pair_table", "pair_and_flip",
          "pair_and_triples", "pair_triples_flip")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-junctions", type=int, default=6, choices=range(2, 8))
    parser.add_argument("--width", type=int, default=12, choices=range(5, 17))
    parser.add_argument("--current", type=int, default=13, choices=range(6, 18))
    parser.add_argument("--current-width", type=int, default=48, choices=range(8,63))
    parser.add_argument("--engine", type=Path)
    args = parser.parse_args()
    graphs = []
    for graph in nx.graph_atlas_g():
        n, e = len(graph), graph.number_of_edges()
        if 2 <= n <= args.start_junctions and e < args.width and nx.is_connected(graph):
            row = [n, e, *(end for edge in sorted(graph.edges()) for end in edge)]
            graphs.append(" ".join(map(str,row)))
    with tempfile.TemporaryDirectory() as directory:
        exe = args.engine or Path(directory) / "scan"
        if not args.engine:
            subprocess.run(["c++","-std=c++20","-O3","-Wno-return-type",str(HERE/"transpositions.cpp"),"-o",str(exe)],check=True)
        run = subprocess.run([str(exe),str(args.width),str(args.current),str(args.current_width)],text=True,
                             input="\n".join(graphs)+"\n",capture_output=True)
        if run.returncode:
            raise RuntimeError(f"reached-stage scan exited {run.returncode}: {run.stderr}")
    tiers, hits = [], []
    for line in run.stdout.splitlines():
        tag, *values = line.split()
        if tag == "H":
            hits.append(list(map(int,values)))
        else:
            assert tag == "S" and len(values) == len(FIELDS)
            tiers.append(dict(zip(FIELDS,map(int,values))))
    totals = Counter()
    for row in tiers:
        totals.update({k:row[k] for k in FIELDS[2:] if k != "largest_age"})
    print(json.dumps({"bounds":{"starting_junctions":args.start_junctions,
                                "starting_distinctions":args.width,"current_junctions":args.current,
                                "current_distinctions":args.current_width},
                      "meeting_multiplicities":"one or two, at least one repeated ordinary meeting",
                      "starting_representatives":"one connected simple graph per isomorphism class, all labeled multiplicity and loose allocations",
                      "scope":"single transpositions of old distinctions outside every live support, positive ages with a lawful next round",
                      "measurement":"number of non-equation symmetries in the indicated reading; nonpreservation of the equation span by itself does not imply failure of extension",
                      "largest_age":max(row["largest_age"] for row in tiers),"tiers":tiers,
                      "totals":totals,"non_span_triple_preservers":hits},indent=2))


if __name__ == "__main__":
    main()
