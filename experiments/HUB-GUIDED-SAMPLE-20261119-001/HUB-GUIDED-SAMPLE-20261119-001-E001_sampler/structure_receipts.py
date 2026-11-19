"""Bind the two exact counting implementations and both physical rankers to one reached stage."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from structure_export import check_groups
from structure_rank import load_bundled, unrank
from structure_union import read_blocks


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(folder, name, cnf, tool):
    log=(folder / name).read_text()
    expression=r"^s (\d+)\s*$" if tool=="d4" else r"^c s exact arb int (\d+)\s*$"
    matches=re.findall(expression,log,re.M)
    assert len(matches)==1
    if tool=="ganak":
        assert "pac guarantees epsilon: 0 delta: 0" in log
    lines=(folder/cnf).read_text().splitlines()
    _,_,variables,clauses=lines[0].split()
    assert len(lines)==int(clauses)+1
    return dict(solver=tool,count=int(matches[0]),variables=int(variables),clauses=int(clauses),
                input_sha256=digest(folder/cnf),result_line=matches[0],
                log_sha256=digest(folder/name))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("folder",type=Path)
    ap.add_argument("artifacts",type=Path)
    args=ap.parse_args()
    d=args.folder;art=args.artifacts
    _,blocks=read_blocks(d/'start-03-age08.txt')
    cases={"structure_full35_0":[("structure_ganak_350raw.log","structure_350raw.cnf","ganak")],
           "structure_sector13_4":[("structure_ganak_sector.log","structure_sector.cnf","ganak"),
                                  ("structure_d4_sector.log","structure_sector.cnf","d4"),
                                  ("structure_ganak_sector_raw.log","structure_sector_raw.cnf","ganak")]}
    output={}
    for name,streams in cases.items():
        data=load_bundled(art/'structure_rankers.json',name)
        bound=json.loads((art/(name+'.json')).read_text())
        rows=[receipt(d,*s) for s in streams]
        assert all(r["count"]==data["count"]==bound["count"] for r in rows)
        audits=bound["direct_maximality_checks"]
        assert check_groups(blocks,data,[r["rank"] for r in audits],decode=unrank)==audits
        output[name]=dict(rank_table_count=data["count"],physical_rank_replays=len(audits),solvers=rows)
    tools={
      "ganak":{"source":"https://github.com/meelgroup/ganak/releases/tag/release%2Fv2.9.0",
               "release":"v2.9.0","release_archive_sha256":digest(d/'structure_ganak.tar.gz'),
               "executable_sha256":digest(d/'structure_ganak'),
               "arguments":["--prob","0","--mode","0","--verb","0","input.cnf"]},
      "d4":{"source":"https://github.com/practical-kc/d4v2/releases/tag/2.3.2",
            "release":"2.3.2","release_archive_sha256":digest(d/'structure_d4.zip'),
            "executable_sha256":digest(d/'structure_d4_runtime/bin/d4'),
            "arguments":["-i","input.cnf","-m","counting"]}}
    assert tools["ganak"]["release_archive_sha256"]=="a303febfa889d887771d9c97680ca83475987d39166c524f50e8d9d344655183"
    assert tools["d4"]["release_archive_sha256"]=="a70fddf2bd369bbee169851912f44469e64072223b64c5f7c1a65ed4679f4df2"
    final=dict(stage_sha256=digest(d/'start-03-age08.txt'),tools=tools,cases=output)
    (art/'structure_solver_checks.json').write_text(json.dumps(final,indent=2)+'\n')

if __name__=="__main__":
    main()
