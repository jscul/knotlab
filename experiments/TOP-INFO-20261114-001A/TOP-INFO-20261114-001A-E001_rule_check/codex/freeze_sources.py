"""Freeze executable code and small source metadata without copying inputs."""
from pathlib import Path
import sys
import top_data as d
import two_block
import two_block_brute


def main():
    deps=two_block.load_dependencies()
    brute=two_block_brute.load_brute()
    brute._language()
    files=set(d.HERE.glob('*.py'))
    for directory in (d.CARRY,d.inputs.FT,d.inputs.PATHS_DIR):
        files.update(directory.glob('*.py'))
    files.add(d.ROOT/'scripts/longrun.py')
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.is_relative_to(d.ROOT) and not path.is_relative_to(d.ROOT/'.venv') and path.suffix=='.py':files.add(path)
    files.update([d.HERE/'catalog.json',d.READ/'results.json',d.READ/'summary.json',d.READ/'source_index.json',d.READ/'coverage.py',d.CARRY/'paths_full/results.jsonl'])
    result=dict(schema_version=1,files=[dict(path=str(p.relative_to(d.ROOT)),sha256=d.inputs.digest(p)) for p in sorted(files)])
    d.dump('frozen_sources.json',result)
    print('frozen',len(files),'files; CARRY 3.5GB window source guarded by reused streamed digest/size/mtime receipt')


if __name__=='__main__':main()
